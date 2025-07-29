"""
Persistent Queue Module for AIIA SDK

This module provides a persistent queue implementation for the AIIA SDK
to ensure logs are not lost even in case of application crashes or network failures.
"""

import os
import json
import time
import sqlite3
import threading
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import gzip
import base64

class PersistentQueue:
    """
    A thread-safe persistent queue implementation using SQLite.
    Provides durability for logs that haven't been sent to the backend.
    """
    _instance = None
    _lock = threading.RLock()  # Use RLock instead of Lock to allow reentrant locking
    
    @classmethod
    def get_instance(cls, storage_dir: Optional[str] = None) -> 'PersistentQueue':
        """Get singleton instance of the persistent queue."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(storage_dir)
        return cls._instance
    
    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize the persistent queue with the given storage directory."""
        self.storage_dir = Path(storage_dir) if storage_dir else Path(__file__).parent / "queue_storage"
        self.storage_dir.mkdir(exist_ok=True, parents=True)
        
        self.db_path = self.storage_dir / "queue.db"
        self.conn = None
        self.cursor = None
        self._init_db()
        
        # Configuration
        self.max_retries = 5
        self.max_age_days = 7  # Auto-purge logs older than this
        self.compression_threshold = 1024  # Bytes, compress if larger
        
        # Stats
        self.stats = {
            "enqueued": 0,
            "dequeued": 0,
            "failed": 0,
            "retried": 0,
            "purged": 0
        }
        
        # Perform maintenance on startup
        self._maintenance()
    
    def _init_db(self):
        """Initialize the SQLite database."""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Create logs table if it doesn't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id TEXT PRIMARY KEY,
                    data BLOB,
                    compressed INTEGER,
                    created_at INTEGER,
                    last_attempt INTEGER,
                    retries INTEGER,
                    priority INTEGER
                )
            ''')
            
            # Create index on priority and created_at for efficient querying
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_logs_priority_created 
                ON logs (priority, created_at)
            ''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"[AIIA SDK] Error initializing persistent queue database: {e}")
            # Fallback to in-memory if file access fails
            self.conn = sqlite3.connect(":memory:")
            self.cursor = self.conn.cursor()
            self._init_db()
    
    def enqueue(self, log_data: Dict[str, Any], priority: int = 1) -> str:
        """
        Add a log to the persistent queue.
        
        Args:
            log_data: The log data to enqueue
            priority: Priority level (1=normal, 2=high, 3=critical)
            
        Returns:
            The ID of the enqueued log
        """
        log_id = str(uuid.uuid4())
        now = int(time.time())
        
        # Serialize and potentially compress the data
        serialized = json.dumps(log_data).encode('utf-8')
        compressed = 0
        
        # Compress if larger than threshold
        if len(serialized) > self.compression_threshold:
            serialized = gzip.compress(serialized)
            compressed = 1
        
        with self._lock:
            try:
                self.cursor.execute(
                    "INSERT INTO logs VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (log_id, serialized, compressed, now, 0, 0, priority)
                )
                self.conn.commit()
                self.stats["enqueued"] += 1
                return log_id
            except sqlite3.Error as e:
                print(f"[AIIA SDK] Error enqueueing log: {e}")
                return None
    
    def dequeue(self, limit: int = 10) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get logs from the queue, ordered by priority and creation time.
        
        Args:
            limit: Maximum number of logs to retrieve
            
        Returns:
            List of (log_id, log_data) tuples
        """
        with self._lock:
            try:
                self.cursor.execute(
                    """
                    SELECT id, data, compressed FROM logs 
                    ORDER BY priority DESC, created_at ASC
                    LIMIT ?
                    """, 
                    (limit,)
                )
                results = []
                
                for row in self.cursor.fetchall():
                    log_id, data, compressed = row
                    
                    # Decompress if needed
                    if compressed:
                        data = gzip.decompress(data)
                    
                    # Deserialize
                    log_data = json.loads(data.decode('utf-8'))
                    results.append((log_id, log_data))
                
                return results
            except sqlite3.Error as e:
                print(f"[AIIA SDK] Error dequeuing logs: {e}")
                return []
    
    def mark_processed(self, log_id: str) -> bool:
        """
        Remove a log from the queue after successful processing.
        
        Args:
            log_id: ID of the log to remove
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            try:
                self.cursor.execute("DELETE FROM logs WHERE id = ?", (log_id,))
                self.conn.commit()
                self.stats["dequeued"] += 1
                return True
            except sqlite3.Error as e:
                print(f"[AIIA SDK] Error marking log as processed: {e}")
                return False
    
    def mark_failed(self, log_id: str) -> bool:
        """
        Mark a log as failed, incrementing retry counter.
        
        Args:
            log_id: ID of the log that failed processing
            
        Returns:
            True if the log will be retried, False if max retries reached
        """
        now = int(time.time())
        
        with self._lock:
            try:
                # Get current retry count
                self.cursor.execute(
                    "SELECT retries FROM logs WHERE id = ?", 
                    (log_id,)
                )
                result = self.cursor.fetchone()
                
                if not result:
                    return False
                
                retries = result[0]
                
                if retries >= self.max_retries:
                    # Max retries reached, remove the log
                    self.cursor.execute("DELETE FROM logs WHERE id = ?", (log_id,))
                    self.conn.commit()
                    self.stats["failed"] += 1
                    return False
                else:
                    # Update retry counter and last attempt time
                    self.cursor.execute(
                        "UPDATE logs SET retries = ?, last_attempt = ? WHERE id = ?",
                        (retries + 1, now, log_id)
                    )
                    self.conn.commit()
                    self.stats["retried"] += 1
                    return True
            except sqlite3.Error as e:
                print(f"[AIIA SDK] Error marking log as failed: {e}")
                return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get queue statistics."""
        with self._lock:
            try:
                # Get current queue size
                self.cursor.execute("SELECT COUNT(*) FROM logs")
                queue_size = self.cursor.fetchone()[0]
                
                # Get priority distribution
                self.cursor.execute(
                    "SELECT priority, COUNT(*) FROM logs GROUP BY priority"
                )
                priority_counts = {f"priority_{p}": c for p, c in self.cursor.fetchall()}
                
                # Combine stats
                stats = {
                    "queue_size": queue_size,
                    **priority_counts,
                    **self.stats
                }
                
                return stats
            except sqlite3.Error as e:
                print(f"[AIIA SDK] Error getting queue stats: {e}")
                return {"error": str(e), **self.stats}
    
    def _maintenance(self):
        """Perform maintenance tasks like purging old logs."""
        now = int(time.time())
        max_age_seconds = self.max_age_days * 24 * 60 * 60
        cutoff = now - max_age_seconds
        
        # Use a timeout to avoid deadlocks
        lock_acquired = self._lock.acquire(timeout=5.0)
        if not lock_acquired:
            print("[AIIA SDK] Warning: Could not acquire lock for maintenance, skipping")
            return
            
        try:
            # Delete logs older than max age
            self.cursor.execute(
                "DELETE FROM logs WHERE created_at < ?",
                (cutoff,)
            )
            purged = self.cursor.rowcount
            self.conn.commit()
            
            if purged > 0:
                self.stats["purged"] += purged
                print(f"[AIIA SDK] Purged {purged} logs older than {self.max_age_days} days")
        except sqlite3.Error as e:
            print(f"[AIIA SDK] Error during queue maintenance: {e}")
        finally:
            self._lock.release()
    
    def close(self):
        """Close the database connection."""
        # Use a timeout to avoid deadlocks
        lock_acquired = self._lock.acquire(timeout=5.0)
        if not lock_acquired:
            print("[AIIA SDK] Warning: Could not acquire lock for closing, forcing close")
        
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
                self.cursor = None
        finally:
            if lock_acquired:
                self._lock.release()
    
    def __del__(self):
        """Ensure connection is closed when object is garbage collected."""
        try:
            self.close()
        except:
            pass


# Helper functions for compression and serialization
def compress_data(data: Dict[str, Any]) -> bytes:
    """Compress data using gzip."""
    serialized = json.dumps(data).encode('utf-8')
    return gzip.compress(serialized)

def decompress_data(compressed_data: bytes) -> Dict[str, Any]:
    """Decompress data compressed with compress_data."""
    decompressed = gzip.decompress(compressed_data)
    return json.loads(decompressed.decode('utf-8'))
