"""
Performance Optimizations Module for AIIA SDK

This module provides optimizations for the AIIA SDK to improve performance:
1. Data compression for reducing bandwidth usage
2. Efficient serialization using MessagePack
3. Connection pooling for HTTP requests
4. Batching optimizations
"""

import gzip
import json
import time
import zlib
from typing import Dict, Any, List, Union, Optional
import base64

# Try to import optional dependencies
try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class CompressionManager:
    """
    Handles compression and decompression of data to reduce bandwidth usage.
    Supports multiple compression algorithms and automatically selects the best one.
    """
    
    # Compression level constants
    NONE = 0
    FAST = 1
    BALANCED = 5
    MAX = 9
    
    # Compression algorithms
    GZIP = "gzip"
    ZLIB = "zlib"
    
    def __init__(self, default_algorithm: str = GZIP, default_level: int = BALANCED,
                 min_size_for_compression: int = 1024):
        """
        Initialize the compression manager.
        
        Args:
            default_algorithm: Default compression algorithm (gzip or zlib)
            default_level: Default compression level (0-9)
            min_size_for_compression: Minimum data size in bytes to apply compression
        """
        self.default_algorithm = default_algorithm
        self.default_level = default_level
        self.min_size_for_compression = min_size_for_compression
    
    def compress(self, data: Union[Dict[str, Any], List[Any], str, bytes], 
                 algorithm: Optional[str] = None, level: Optional[int] = None) -> Dict[str, Any]:
        """
        Compress data if it exceeds the minimum size threshold.
        
        Args:
            data: Data to compress (dict, list, string, or bytes)
            algorithm: Compression algorithm to use (defaults to self.default_algorithm)
            level: Compression level (defaults to self.default_level)
            
        Returns:
            Dict with compressed data and metadata
        """
        algorithm = algorithm or self.default_algorithm
        level = level if level is not None else self.default_level
        
        # Convert to bytes if not already
        if isinstance(data, (dict, list)):
            data_bytes = json.dumps(data).encode('utf-8')
        elif isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        
        # Check if data is large enough to benefit from compression
        if len(data_bytes) < self.min_size_for_compression:
            # Return uncompressed with metadata
            return {
                "data": base64.b64encode(data_bytes).decode('utf-8'),
                "compressed": False,
                "algorithm": "none",
                "original_size": len(data_bytes)
            }
        
        # Compress based on algorithm
        if algorithm == self.GZIP:
            compressed = gzip.compress(data_bytes, compresslevel=level)
        elif algorithm == self.ZLIB:
            compressed = zlib.compress(data_bytes, level=level)
        else:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")
        
        # Return compressed data with metadata
        return {
            "data": base64.b64encode(compressed).decode('utf-8'),
            "compressed": True,
            "algorithm": algorithm,
            "original_size": len(data_bytes),
            "compressed_size": len(compressed),
            "compression_ratio": len(data_bytes) / len(compressed) if len(compressed) > 0 else 0
        }
    
    def decompress(self, compressed_data: Dict[str, Any]) -> Union[Dict[str, Any], List[Any], str, bytes]:
        """
        Decompress data based on metadata.
        
        Args:
            compressed_data: Dict with compressed data and metadata from compress()
            
        Returns:
            Original data (dict, list, string, or bytes)
        """
        # Extract data and metadata
        data = base64.b64decode(compressed_data["data"])
        is_compressed = compressed_data.get("compressed", False)
        algorithm = compressed_data.get("algorithm", "none")
        
        if not is_compressed or algorithm == "none":
            # Data is not compressed
            try:
                # Try to parse as JSON
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Return as bytes if not valid JSON
                return data
        
        # Decompress based on algorithm
        if algorithm == self.GZIP:
            decompressed = gzip.decompress(data)
        elif algorithm == self.ZLIB:
            decompressed = zlib.decompress(data)
        else:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")
        
        # Try to parse as JSON
        try:
            return json.loads(decompressed.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Return as bytes if not valid JSON
            return decompressed


class SerializationManager:
    """
    Handles efficient serialization and deserialization of data.
    Uses MessagePack if available, otherwise falls back to JSON.
    """
    
    def __init__(self, use_msgpack: bool = True):
        """
        Initialize the serialization manager.
        
        Args:
            use_msgpack: Whether to use MessagePack if available
        """
        self.use_msgpack = use_msgpack and MSGPACK_AVAILABLE
    
    def serialize(self, data: Union[Dict[str, Any], List[Any]]) -> bytes:
        """
        Serialize data to bytes using the most efficient available method.
        
        Args:
            data: Data to serialize
            
        Returns:
            Serialized data as bytes
        """
        if self.use_msgpack:
            return msgpack.packb(data, use_bin_type=True)
        else:
            return json.dumps(data).encode('utf-8')
    
    def deserialize(self, data: bytes) -> Union[Dict[str, Any], List[Any]]:
        """
        Deserialize data from bytes.
        
        Args:
            data: Serialized data
            
        Returns:
            Deserialized data
        """
        if self.use_msgpack and data[0:1] != b'{' and data[0:1] != b'[':
            # Looks like MessagePack data
            return msgpack.unpackb(data, raw=False)
        else:
            # Assume JSON
            return json.loads(data.decode('utf-8'))


class HTTPManager:
    """
    Manages HTTP connections with connection pooling, retries, and timeouts.
    """
    
    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 10,
                 max_retries: int = 3, backoff_factor: float = 0.3,
                 status_forcelist: List[int] = [500, 502, 503, 504],
                 timeout: float = 5.0):
        """
        Initialize the HTTP manager.
        
        Args:
            pool_connections: Number of connection pools to cache
            pool_maxsize: Maximum number of connections to save in the pool
            max_retries: Maximum number of retries for failed requests
            backoff_factor: Backoff factor for retries
            status_forcelist: HTTP status codes that should trigger a retry
            timeout: Default timeout for requests
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests package is required for HTTPManager")
        
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=["HEAD", "GET", "PUT", "POST", "OPTIONS"]
        )
        
        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy
        )
        
        # Mount adapter for both HTTP and HTTPS
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make an HTTP request with connection pooling and retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response object
        """
        # Set default timeout if not provided
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        
        return self.session.request(method, url, **kwargs)
    
    def close(self):
        """Close the session and release resources."""
        if hasattr(self, 'session'):
            self.session.close()


class BatchOptimizer:
    """
    Optimizes batch processing for improved throughput.
    """
    
    def __init__(self, min_batch_size: int = 5, max_batch_size: int = 100,
                 min_batch_interval: float = 1.0, max_batch_interval: float = 30.0,
                 adaptive: bool = True):
        """
        Initialize the batch optimizer.
        
        Args:
            min_batch_size: Minimum batch size
            max_batch_size: Maximum batch size
            min_batch_interval: Minimum interval between batches (seconds)
            max_batch_interval: Maximum interval between batches (seconds)
            adaptive: Whether to use adaptive batching based on queue size
        """
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size
        self.min_batch_interval = min_batch_interval
        self.max_batch_interval = max_batch_interval
        self.adaptive = adaptive
        
        # Metrics for adaptive batching
        self.last_batch_time = time.time()
        self.last_batch_size = 0
        self.last_processing_time = 0
        self.average_processing_time = 0.1  # Initial guess
        self.batch_count = 0
    
    def get_optimal_batch_size(self, queue_size: int) -> int:
        """
        Get the optimal batch size based on current conditions.
        
        Args:
            queue_size: Current size of the queue
            
        Returns:
            Optimal batch size
        """
        if not self.adaptive:
            return min(self.max_batch_size, max(self.min_batch_size, queue_size))
        
        # Adaptive logic based on processing history
        if self.batch_count < 5:
            # Not enough history, use conservative batch size
            return min(self.min_batch_size * 2, queue_size, self.max_batch_size)
        
        # Calculate optimal batch size based on processing time
        if self.average_processing_time < 0.1:
            # Very fast processing, use larger batches
            optimal_size = min(self.max_batch_size, queue_size)
        elif self.average_processing_time > 1.0:
            # Slow processing, use smaller batches
            optimal_size = min(self.min_batch_size * 2, queue_size)
        else:
            # Balanced approach
            factor = 0.5 / self.average_processing_time  # Higher factor for faster processing
            optimal_size = min(int(self.min_batch_size * factor), queue_size, self.max_batch_size)
        
        return max(self.min_batch_size, optimal_size)
    
    def get_next_batch_interval(self, queue_size: int) -> float:
        """
        Get the optimal interval before processing the next batch.
        
        Args:
            queue_size: Current size of the queue
            
        Returns:
            Interval in seconds
        """
        if not self.adaptive:
            return self.min_batch_interval
        
        # Adaptive logic based on queue size
        if queue_size == 0:
            # Empty queue, longer interval
            return self.max_batch_interval
        elif queue_size < self.min_batch_size:
            # Small queue, medium interval
            return min(self.max_batch_interval, 
                       self.min_batch_interval + (self.max_batch_interval - self.min_batch_interval) * 
                       (1 - queue_size / self.min_batch_size))
        else:
            # Queue has enough items for a batch, shorter interval
            return self.min_batch_interval
    
    def update_metrics(self, batch_size: int, processing_time: float):
        """
        Update metrics after processing a batch.
        
        Args:
            batch_size: Size of the batch that was processed
            processing_time: Time taken to process the batch in seconds
        """
        self.last_batch_time = time.time()
        self.last_batch_size = batch_size
        self.last_processing_time = processing_time
        
        # Update moving average of processing time per item
        if batch_size > 0:
            time_per_item = processing_time / batch_size
            if self.batch_count == 0:
                self.average_processing_time = time_per_item
            else:
                # Exponential moving average with more weight on recent batches
                self.average_processing_time = 0.7 * time_per_item + 0.3 * self.average_processing_time
        
        self.batch_count += 1
