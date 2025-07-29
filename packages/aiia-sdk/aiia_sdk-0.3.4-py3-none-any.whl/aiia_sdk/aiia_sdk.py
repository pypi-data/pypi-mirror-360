import json
import hmac
import hashlib
import requests
import uuid
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import time
import tldextract
from dotenv import load_dotenv
from .utils import generate_signature
from .persistent_queue import PersistentQueue
from .performance_optimizations import CompressionManager, SerializationManager, HTTPManager, BatchOptimizer
from .auto_interceptor import AIIAAutoInterceptor

# Check for optional dependencies
_HAS_SEMANTIC_DEPS = False
_SEMANTIC_IMPORT_ERROR = None

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from sentence_transformers import SentenceTransformer
    _HAS_SEMANTIC_DEPS = True
except ImportError as e:
    _SEMANTIC_IMPORT_ERROR = str(e)
    
    # Create dummy classes/functions that provide helpful error messages
    class DummySentenceTransformer:
        def __init__(self, *args, **kwargs):
            print("⚠️ AIIA SDK: Semantic features are disabled. To enable them, install the semantic extras:")
            print("   pip install 'AIIA_TEST[semantic]'")
            print(f"Error details: {_SEMANTIC_IMPORT_ERROR}")
            self.encode = self._not_available
        
        def _not_available(self, *args, **kwargs):
            print("⚠️ AIIA SDK: Semantic model not available. Actions will be logged without semantic detection.")
            return None
    
    class DummyUtil:
        @staticmethod
        def cos_sim(*args, **kwargs):
            return None
    
    # Create dummy versions that don't raise exceptions but provide warnings
    SentenceTransformer = DummySentenceTransformer
    util = DummyUtil

# === CONFIGURACIÓN DE ENDPOINT ===
DEFAULT_BACKEND_URL = os.getenv("AIIA_BACKEND_URL", "https://api.aiiatrace.com")

class AIIA:
    """
    AIIA SDK principal (plug-and-play).
    - Allows registering AI actions automatically and securely.
    - Detects actions semantically using language models.
    - No decorators or manual registration required: just initialize and use.
    - Supports universal context identifiers and workflow correlation.
    """
    def __init__(self, api_key: Optional[str] = None, client_secret: Optional[str] = None, 
                 ia_id: Optional[str] = None, backend_url: Optional[str] = None, 
                 rules: Optional[dict] = None, batch_size: int = 10, batch_interval: int = 5,
                 storage_dir: Optional[str] = None, use_persistent_queue: bool = True,
                 use_compression: bool = True, use_connection_pooling: bool = True,
                 adaptive_batching: bool = True, min_size_for_compression: int = 1024,
                 auto_integrate: bool = False, encrypt_sensitive_data: bool = False,
                 auto_detect_actions: bool = True):
        """
        Initialize AIIA SDK with 100% plug & play functionality.
        
        Args:
            api_key: API key for authentication (auto-loaded from .env if not provided)
            client_secret: Client secret for authentication (auto-loaded from .env if not provided)
            ia_id: IA identifier (auto-loaded from .env if not provided)
            backend_url: Backend URL (defaults to production)
            rules: Custom detection rules
            batch_size: Number of logs to batch together
            batch_interval: Interval in seconds between batch sends
            storage_dir: Directory for persistent storage
            use_persistent_queue: Enable persistent queue for reliability
            use_compression: Enable compression for large payloads
            use_connection_pooling: Enable HTTP connection pooling
            adaptive_batching: Enable adaptive batch sizing
            min_size_for_compression: Minimum payload size for compression
            auto_integrate: Enable automatic framework integration
            encrypt_sensitive_data: Enable automatic data encryption
            auto_detect_actions: Enable automatic action detection
        """
        # 🔥 AUTO-LOAD ENVIRONMENT VARIABLES FOR 100% PLUG & PLAY
        load_dotenv()
        
        # Initialize credentials with auto-fallback to environment variables
        self.api_key = api_key or os.getenv("AIIA_API_KEY")
        client_secret_raw = client_secret or os.getenv("AIIA_CLIENT_SECRET")
        self.ia_id = ia_id or os.getenv("AIIA_IA_ID") or os.getenv("AIIA_DEVELOPER_ID")
        self.backend_url = backend_url or os.getenv("AIIA_BACKEND_URL", DEFAULT_BACKEND_URL)
        
        # Store additional parameters for compatibility with tests
        self.auto_integrate = auto_integrate
        self.encrypt_sensitive_data = encrypt_sensitive_data
        
        # Handle client_secret encoding properly
        if client_secret_raw is not None:
            if isinstance(client_secret_raw, str):
                self.client_secret = client_secret_raw.encode()
            elif isinstance(client_secret_raw, bytes):
                self.client_secret = client_secret_raw
            else:
                self.client_secret = str(client_secret_raw).encode()
        else:
            self.client_secret = None
        
        # Guardar el directorio de almacenamiento para acceso en pruebas
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "storage")
        
        # Configurar la ruta de caché
        cache_dir = os.path.join(self.storage_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = Path(cache_dir) / "actions_cache.json"
        self._init_cache()
        self._load_semantic_model()
        self.rules = rules or {}
        
        # Configuración de procesamiento por lotes
        self._batch_size = batch_size
        self._batch_interval = batch_interval
        self._batch_worker_started = False
        
        # Inicializar optimizaciones de rendimiento
        self.use_compression = use_compression
        if use_compression:
            self.compression_manager = CompressionManager(
                default_algorithm=CompressionManager.GZIP,
                default_level=CompressionManager.BALANCED,
                min_size_for_compression=min_size_for_compression
            )
            print(f"[AIIA SDK] Compression enabled for payloads > {min_size_for_compression} bytes")
        
        # Inicializar serialización eficiente
        self.serialization_manager = SerializationManager(use_msgpack=True)
        
        # Inicializar connection pooling
        if use_connection_pooling:
            self.http_manager = HTTPManager(
                pool_connections=10,
                pool_maxsize=20,
                max_retries=3,
                timeout=10.0
            )
            print("[AIIA SDK] HTTP connection pooling enabled")
        else:
            self.http_manager = None
        
        # Inicializar optimizador de batches
        if adaptive_batching:
            self.batch_optimizer = BatchOptimizer(
                min_batch_size=batch_size // 2,
                max_batch_size=batch_size * 2,
                min_batch_interval=batch_interval / 2,
                max_batch_interval=batch_interval * 2,
                adaptive=True
            )
            print("[AIIA SDK] Adaptive batch processing enabled")
        else:
            self.batch_optimizer = BatchOptimizer(
                min_batch_size=batch_size,
                max_batch_size=batch_size,
                min_batch_interval=batch_interval,
                max_batch_interval=batch_interval,
                adaptive=False
            )
        
        # Inicializar cola persistente o en memoria
        self.use_persistent_queue = use_persistent_queue
        if use_persistent_queue:
            self.persistent_queue = PersistentQueue.get_instance(storage_dir)
            print(f"[AIIA SDK] Persistent queue initialized. Current size: {self.persistent_queue.get_stats()['queue_size']} logs")
        else:
            self._batch_queue = []
            print("[AIIA SDK] Using in-memory queue (non-persistent)")
        
        self._auto_inject_middleware()
        self._start_batch_worker()
        
        # Inicializar auto-interceptor para detección automática
        # Auto-interceptor TEMPORALMENTE DESHABILITADO por bug de recursión
        # TODO: Arreglar recursión infinita en inspect.signature()
        print("⚠️ [AIIA SDK] Auto-interceptor temporalmente deshabilitado por bug de recursión")
        self.auto_interceptor = None
        print("[AIIA SDK] Use log_action() manually.")
        
        if not (self.api_key and self.client_secret and self.ia_id):
            print("[AIIA SDK] ⚠️ Missing credentials. Check your .env or constructor args.")
        
        if auto_detect_actions:
            # Mostrar estado de credenciales
            if self.api_key and self.ia_id:
                print("[AIIA SDK] ✅ Initialized in 100% PLUG & PLAY mode with credentials from .env")
                print(f"[AIIA SDK] ✅ Ready to detect actions for IA: {self.ia_id[:8]}...")
            else:
                print("[AIIA SDK] ⚠️ Initialized but missing credentials. Check your .env file:")
                print("[AIIA SDK] ⚠️ Required: AIIA_API_KEY, AIIA_IA_ID (or AIIA_DEVELOPER_ID)")
            print("[AIIA SDK] 🌟 Use aiia.analyze_output(text) for universal AI detection")
        else:
            print("[AIIA SDK] Initialized in manual mode. Use log_action() to track actions.")

    def _load_semantic_model(self):
        """Cargar el modelo semántico y las definiciones de acciones."""
        # Inicializar valores por defecto
        self.semantic_model = None
        self.semantic_actions = []
        self.semantic_embeddings = []
        
        # Verificar si las dependencias semánticas están instaladas
        if not _HAS_SEMANTIC_DEPS:
            print("[AIIA SDK] ℹ️ Semantic detection disabled: dependencies not installed")
            print("[AIIA SDK] ℹ️ Install with: pip install 'AIIA_TEST[semantic]'")
            if _SEMANTIC_IMPORT_ERROR:
                print(f"[AIIA SDK] ℹ️ Error details: {_SEMANTIC_IMPORT_ERROR}")
            print("[AIIA SDK] ℹ️ The SDK will continue to function without semantic detection")
            return
            
        try:
            # Importar el singleton y cargar el modelo
            from .semantic_singleton import SemanticModelSingleton
            
            # Obtener información sobre el modelo antes de cargarlo
            model_info = SemanticModelSingleton.get_model_info()
            print(f"[AIIA SDK] ℹ️ Using semantic model: {model_info['name']} ({model_info['size_mb']}MB)")
            
            # Obtener el modelo del singleton (esto lo cargará si aún no está cargado)
            self.semantic_model = SemanticModelSingleton.get_model()
            
            # Si el modelo no se cargó correctamente, mostrar información y salir
            if not self.semantic_model:
                model_info = SemanticModelSingleton.get_model_info()
                if 'error' in model_info:
                    print(f"[AIIA SDK] ⚠️ Semantic model not available: {model_info['error']}")
                print("[AIIA SDK] ⚠️ The SDK will continue to function without semantic detection")
                return
            
            # Cargar o crear archivo de acciones
            data_dir = Path(__file__).parent / "data"
            data_dir.mkdir(exist_ok=True)
            actions_file = data_dir / "actions.json"
            
            # Si el archivo no existe, crear uno con acciones predefinidas
            if not actions_file.exists():
                print("[AIIA SDK] ℹ️ Creating default actions file")
                default_actions = [
                    {"code": "GENERATE", "description": "Generate or create content, code, text, or other information"},
                    {"code": "ANALYZE", "description": "Analyze, evaluate, assess or examine data, text, or content"},
                    {"code": "CLASSIFY", "description": "Categorize, label, or classify information into predefined groups"},
                    {"code": "TRANSFORM", "description": "Convert, translate, or transform data from one format to another"},
                    {"code": "SUMMARIZE", "description": "Condense, summarize, or create a brief version of content"},
                    {"code": "EXTRACT", "description": "Extract specific information, data, or insights from content"},
                    {"code": "SEARCH", "description": "Find, search for, or locate specific information or content"},
                    {"code": "PREDICT", "description": "Forecast, predict, or project future outcomes or trends"}
                ]
                with open(actions_file, "w", encoding="utf-8") as f:
                    json.dump(default_actions, f, indent=2)
            
            # Cargar el archivo de acciones
            try:
                with open(actions_file, "r", encoding="utf-8") as f:
                    actions_data = json.load(f)
                    
                # Preparar acciones y sus descripciones para embeddings
                self.semantic_actions = []
                action_texts = []
                
                for action in actions_data:
                    if "code" in action and "description" in action:
                        self.semantic_actions.append(action)
                        action_texts.append(action["description"])
                    
                # Generar embeddings para las acciones usando el singleton
                if self.semantic_model and action_texts:
                    self.semantic_embeddings = SemanticModelSingleton.get_embeddings(action_texts)
                    if self.semantic_embeddings is not None:
                        print(f"[AIIA SDK] ✅ Loaded {len(self.semantic_actions)} semantic action definitions")
                    else:
                        print("[AIIA SDK] ⚠️ Could not generate embeddings for actions")
                        self.semantic_model = None  # Desactivar modelo si no se pueden generar embeddings
                        
            except Exception as e:
                print(f"[AIIA SDK] ⚠️ Error loading action definitions: {e}")
                print("[AIIA SDK] ⚠️ The SDK will continue to function without semantic detection")
                self.semantic_model = None
                
        except Exception as e:
            print(f"[AIIA SDK] ⚠️ Error in semantic model initialization: {e}")
            print("[AIIA SDK] ⚠️ The SDK will continue to function without semantic detection")
            self.semantic_model = None

    def analyze_output(self, output_text: str) -> Optional[str]:
        """🌟 UNIVERSAL METHOD - Analyze any AI output and detect actions automatically.
        
        This is the core universal interface that works with ANY AI model or framework:
        - OpenAI GPT
        - Anthropic Claude  
        - Ollama
        - Custom AI implementations
        - LangChain agents
        - Any text output from any AI system
        
        Args:
            output_text: The text output from any AI system
            
        Returns:
            str: Detected action code or None if no action detected
            
        Example:
            ```python
            from aiia_sdk import AIIA
            aiia = AIIA()  # Auto-loads from .env
            
            # Works with any AI output
            ai_response = "I created a new file called report.pdf"
            aiia.analyze_output(ai_response)
            ```
        """
        return self.semantic_detect_action(output_text)

    def semantic_detect_action(self, output_text: str) -> Optional[str]:
        """Detect action type from AI output using semantic similarity or keyword fallback."""
        if not output_text or not isinstance(output_text, str):
            return None
            
        try:
            # 1. Check for manual override rules first
            override_code = self._apply_override_rules(output_text)
            if override_code is not None:  # Explicit None check
                self.log_action(
                    override_code, 
                    context={
                        "output": output_text[:200],
                        "detection_method": "override_rule"
                    }, 
                    registered=True
                )
                return override_code

            # 2. Check if semantic detection is available
            if not bool(_HAS_SEMANTIC_DEPS):  # Explicit boolean conversion
                return self._fallback_to_keyword_detection(output_text, 
                                                         reason="Semantic dependencies not available")
            
            if self.semantic_model is None:
                return self._fallback_to_keyword_detection(output_text, 
                                                         reason="Semantic model not loaded")
            
            if len(self.semantic_embeddings) == 0:  # Explicit length check instead of truthiness
                return self._fallback_to_keyword_detection(output_text, 
                                                         reason="No semantic action embeddings")
                
            # 3. Try semantic detection
            try:
                from .semantic_singleton import SemanticModelSingleton
                import numpy as np
                
                # Get embedding for output text
                output_embedding = SemanticModelSingleton.get_embedding(output_text)
                
                # Check if embedding is None explicitly
                if output_embedding is None:
                    return self._fallback_to_keyword_detection(output_text, 
                                                             reason="Could not generate text embedding")
                
                # Ensure output_embedding is a NumPy array and 1D
                if hasattr(output_embedding, 'cpu') and hasattr(output_embedding, 'numpy'):
                    # Convert PyTorch tensor to NumPy
                    output_embedding = output_embedding.cpu().numpy()
                
                # Ensure it's a NumPy array
                if not isinstance(output_embedding, np.ndarray):
                    output_embedding = np.array(output_embedding)
                    
                # Ensure it's 1D
                output_embedding = np.squeeze(output_embedding)
                
                # Initialize variables for tracking best match
                best_score = -1.0  # Use float to avoid any array comparison issues
                best_index = -1
                
                # Calculate similarity with each action
                for i, action_embedding in enumerate(self.semantic_embeddings):
                    # Process action embedding
                    if hasattr(action_embedding, 'cpu') and hasattr(action_embedding, 'numpy'):
                        action_embedding = action_embedding.cpu().numpy()
                    
                    if not isinstance(action_embedding, np.ndarray):
                        action_embedding = np.array(action_embedding)
                        
                    action_embedding = np.squeeze(action_embedding)
                    
                    # Calculate cosine similarity manually and safely
                    # Convert all intermediate results to Python scalars to avoid array comparisons
                    dot_product = float(np.dot(output_embedding, action_embedding))
                    norm_output = float(np.linalg.norm(output_embedding))
                    norm_action = float(np.linalg.norm(action_embedding))
                    
                    # Avoid division by zero
                    if float(norm_output) > 0.0 and float(norm_action) > 0.0:  # Explicit float conversion
                        similarity = float(dot_product / (norm_output * norm_action))  # Explicit float conversion
                        
                        # Use explicit float comparison
                        if float(similarity) > float(best_score):  # Explicit float conversion
                            best_score = float(similarity)  # Explicit float conversion
                            best_index = int(i)  # Explicit int conversion
                
                # Apply confidence threshold with explicit float comparison
                threshold = 0.5
                if float(best_score) > float(threshold) and int(best_index) >= 0:  # Explicit conversions
                    action_code = self.semantic_actions[best_index]["code"]
                    
                    self.log_action(
                        action_code, 
                        context={
                            "output": output_text[:200],
                            "confidence": float(best_score),
                            "detection_method": "semantic"
                        },
                        registered=True
                    )
                    return action_code
                    
                # If confidence is below threshold, try keyword fallback
                fallback_code = self._keyword_based_detection(output_text)
                if fallback_code is not None:  # Explicit None check
                    self.log_action(
                        fallback_code,
                        context={
                            "output": output_text[:200],
                            "detection_method": "keyword_fallback",
                            "semantic_confidence": float(best_score),
                            "note": "Below confidence threshold"
                        },
                        registered=True
                    )
                    return fallback_code
                
                # If all else fails, return UNKNOWN
                self.log_action(
                    "UNKNOWN",
                    context={
                        "output": output_text[:200],
                        "semantic_confidence": float(best_score),
                        "note": "No semantic or keyword match found"
                    },
                    registered=True
                )
                return "UNKNOWN"
                
            except Exception as e:
                print(f"[AIIA SDK] ⚠️ Error in semantic detection: {e}")
                return self._fallback_to_keyword_detection(output_text, 
                                                          reason=f"Semantic error: {str(e)[:100]}")
                
        except Exception as e:
            print(f"[AIIA SDK] ⚠️ Error in action detection: {e}")
            try:
                fallback_code = self._keyword_based_detection(output_text)
                if fallback_code is None:  # Explicit None check
                    fallback_code = "UNKNOWN"
                    
                self.log_action(
                    fallback_code,
                    context={
                        "output": output_text[:200],
                        "detection_method": "emergency_fallback",
                        "error": str(e)[:100]
                    },
                    registered=True
                )
                return fallback_code
            except Exception:
                # Si todo falla, registrar como UNKNOWN
                self.log_action(
                    "UNKNOWN",
                    context={
                        "output": output_text[:200] if output_text else "None",
                        "note": "Critical error in action detection"
                    },
                    registered=True
                )
                return "UNKNOWN"

    def _fallback_to_keyword_detection(self, text: str, reason: str = "") -> str:
        """Método auxiliar para usar detección por palabras clave como fallback."""
        fallback_code = self._keyword_based_detection(text)
        if fallback_code:
            self.log_action(
                fallback_code,
                context={
                    "output": text[:200],
                    "detection_method": "keyword_fallback",
                    "reason": reason
                },
                registered=True
            )
            return fallback_code
            
        # Si no se encuentra ninguna coincidencia, registrar como UNKNOWN
        self.log_action(
            "UNKNOWN",
            context={
                "output": text[:200],
                "note": f"{reason}, no keyword match found"
            },
            registered=True
        )
        return "UNKNOWN"

    def _init_cache(self) -> None:
        """Initialize cache directory and file."""
        try:
            # Intentar crear el directorio de caché
            self.cache_file.parent.mkdir(exist_ok=True)
            if not self.cache_file.exists():
                self.cache_file.write_text("{}")
        except (OSError, PermissionError) as e:
            # En caso de error, usar un diccionario en memoria
            print(f"[AIIA SDK] No se pudo inicializar el caché en disco: {e}")
            print(f"[AIIA SDK] Usando caché en memoria")
            self._in_memory_cache = {}
            # Definir una propiedad para el archivo de caché que usa memoria
            self._use_memory_cache = True

    def _load_cache(self) -> Dict[str, Any]:
        """Load cached data."""
        # Si estamos usando caché en memoria, devolver eso
        if hasattr(self, '_use_memory_cache') and self._use_memory_cache:
            return self._in_memory_cache
            
        # De lo contrario, intentar cargar desde el archivo
        try:
            return json.loads(self.cache_file.read_text())
        except (json.JSONDecodeError, FileNotFoundError, OSError, PermissionError):
            return {}

    def _save_cache(self, data: Dict[str, Any]) -> None:
        """Save data to cache."""
        # Si estamos usando caché en memoria, actualizar el diccionario
        if hasattr(self, '_use_memory_cache') and self._use_memory_cache:
            self._in_memory_cache = data
            return
            
        # De lo contrario, intentar guardar en el archivo
        try:
            self.cache_file.write_text(json.dumps(data))
        except (OSError, PermissionError) as e:
            # Si falla, cambiar a modo memoria
            if not hasattr(self, '_use_memory_cache'):
                print(f"[AIIA SDK] No se pudo guardar el caché en disco: {e}")
                print(f"[AIIA SDK] Cambiando a caché en memoria")
                self._in_memory_cache = data
                self._use_memory_cache = True

    def _get_action_definition(self, action_code: str) -> Dict[str, Any]:
        """Retrieve action definition from cache or backend."""
        cache = self._load_cache()
        if action_code in cache:
            return cache[action_code]

        try:
            response = requests.get(
                f"{self.backend_url}/actions/{action_code}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            response.raise_for_status()
            action_data = response.json()
            cache[action_code] = action_data
            self._save_cache(cache)
            return action_data
        except requests.exceptions.RequestException:
            return {
                "code": action_code,
                "description": f"Action {action_code}",
                "category": "general",
                "sensitive": False
            }

    def log_action(self, *args, **kwargs) -> bool:
        """Log an AI action with context and workflow tracking.
        
        100% PLUG & PLAY - Accepts any parameter combination:
        
        Examples:
        - log_action("action_name", context={...})
        - log_action(action="action_name", context={...})  
        - log_action(action_code="action_name", context={...})
        - log_action("action_name", criticality="High", context={...})
        - log_action(action="action_name", criticality="Medium", **extra_params)
        - log_action("action_name", {"context": "data"}, criticality="Low")
        
        All parameters are automatically handled and converted to the correct format.
        """
        try:
            # Initialize variables
            action_code = None
            context = {}
            context_id = kwargs.get('context_id')
            context_type = kwargs.get('context_type')
            context_action = kwargs.get('context_action')
            workflow_id = kwargs.get('workflow_id')
            workflow_step = kwargs.get('workflow_step')
            workflow_step_number = kwargs.get('workflow_step_number')
            registered = kwargs.get('registered', True)
            
            # Handle positional arguments
            if len(args) >= 1:
                # First argument is always the action
                action_code = args[0]
                
            if len(args) >= 2:
                # Second argument could be context dict
                if isinstance(args[1], dict):
                    context.update(args[1])
                    
            # Handle keyword arguments for action
            if action_code is None:
                action_code = kwargs.get('action_code') or kwargs.get('action')
                
            if action_code is None:
                raise ValueError("Action is required. Use: log_action('action_name', ...) or log_action(action='action_name', ...)")
            
            # Handle context from kwargs
            if 'context' in kwargs and isinstance(kwargs['context'], dict):
                context.update(kwargs['context'])
            
            # Handle special parameters that should go into context
            special_params = ['criticality', 'priority', 'severity', 'importance', 'level', 'status', 'result']
            for param in special_params:
                if param in kwargs:
                    context[param] = kwargs[param]
            
            # Handle any other kwargs as context (except SDK internal parameters)
            sdk_internal_params = {
                'action_code', 'action', 'context', 'context_id', 'context_type', 
                'context_action', 'workflow_id', 'workflow_step', 'workflow_step_number', 
                'registered', 'self'
            }
            
            for key, value in kwargs.items():
                if key not in sdk_internal_params and not key.startswith('_'):
                    context[key] = value
            log_id = str(uuid.uuid4())
            
            if not hasattr(self, "_recent_logs"):
                self._recent_logs = set()

            log_fingerprint = hashlib.sha256(
                f"{action_code}|{json.dumps(context, sort_keys=True)}|{self.ia_id}|{context_id}|{context_type}|{context_action}".encode()
            ).hexdigest()

            if log_fingerprint in self._recent_logs:
                return False
            self._recent_logs.add(log_fingerprint)

            if len(self._recent_logs) > 10000:
                self._recent_logs = set(list(self._recent_logs)[-5000:])

            # === LÓGICA DE WORKFLOW COHERENTE ===
            if not workflow_id:
                # Generar workflow_id basado en empresa/dominio para mantener coherencia
                company_domain = None
                company_name = None
                
                # Extraer dominio de empresa del contexto
                if isinstance(context, dict):
                    # Buscar email en el contexto para extraer dominio
                    for key, value in context.items():
                        if isinstance(value, str) and '@' in value and '.' in value:
                            try:
                                domain_parts = tldextract.extract(value.split('@')[1])
                                if domain_parts.domain and domain_parts.suffix:
                                    company_domain = f"{domain_parts.domain}.{domain_parts.suffix}"
                                    break
                            except:
                                continue
                    
                    # Buscar company_name directamente
                    company_name = context.get('company_name') or context.get('company') or context.get('organization')
                
                # Si no hay dominio, usar context_id y context_type como fallback
                if not company_domain and context_id and context_type:
                    company_domain = f"{context_type}_{context_id}"
                
                # Generar workflow_key basado en empresa/dominio
                if company_domain:
                    workflow_key = f"company_{company_domain}"
                elif company_name:
                    workflow_key = f"org_{company_name.lower().replace(' ', '_')}"
                else:
                    # Fallback: usar IA ID para agrupar por desarrollador
                    workflow_key = f"ia_{self.ia_id}"
                
                # Inicializar cache si no existe
                if not hasattr(self, "_workflow_cache"):
                    self._workflow_cache = {}
                
                # Buscar o crear workflow para esta empresa/contexto
                if workflow_key in self._workflow_cache:
                    # Usar workflow existente para esta empresa
                    workflow_data = self._workflow_cache[workflow_key]
                    workflow_id = workflow_data["workflow_id"]
                    
                    # Incrementar step number
                    if workflow_step_number is None:
                        workflow_step_number = workflow_data.get("step", 0) + 1
                    
                    # Generar step name coherente
                    if not workflow_step:
                        if context_action:
                            workflow_step = f"step_{workflow_step_number}"
                        else:
                            workflow_step = f"step_{workflow_step_number}"
                            
                    # Actualizar cache con nuevo step
                    self._workflow_cache[workflow_key]["step"] = workflow_step_number
                    self._workflow_cache[workflow_key]["last_action"] = action_code
                    self._workflow_cache[workflow_key]["timestamp"] = datetime.now(timezone.utc).isoformat()
                    
                else:
                    # Crear nuevo workflow para esta empresa
                    workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
                    workflow_step_number = 1
                    workflow_step = "step_1"
                    
                    # Guardar en cache
                    self._workflow_cache[workflow_key] = {
                        "workflow_id": workflow_id,
                        "step": workflow_step_number,
                        "last_action": action_code,
                        "company_domain": company_domain,
                        "company_name": company_name,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                
                # Limpiar cache si crece demasiado
                if len(self._workflow_cache) > 1000:
                    sorted_cache = sorted(
                        self._workflow_cache.items(),
                        key=lambda x: x[1]["timestamp"]
                    )
                    self._workflow_cache = dict(sorted_cache[-500:])

            action_def = self._get_action_definition(action_code)
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Generar firma si tenemos client_secret
            signature = None
            if self.client_secret is not None:
                data_to_sign = action_code + timestamp + log_id
                signature = hmac.new(
                    self.client_secret,
                    data_to_sign.encode(),
                    hashlib.sha256
                ).hexdigest()

            encrypted_context = {}
            public_context = {}

            # Solo encriptar si tenemos client_secret y la acción lo requiere
            for key, value in context.items():
                if self.client_secret is not None and action_def.get("sensitive", False):
                    encrypted_context[key] = self._encrypt_value(value)
                else:
                    public_context[key] = value

            # AUTO-DETECCIÓN DE EMPRESA v0.3.0 - 100% PLUG & PLAY
            domain = None
            user_email = None
            company_name = None
            
            # Buscar email en cualquier campo del contexto
            email_fields = ['user_email', 'client_email', 'email', 'admin_email', 'contact_email']
            
            # Primero buscar en campos específicos
            for field in email_fields:
                if field in context and isinstance(context[field], str) and "@" in context[field]:
                    user_email = context[field].lower().strip()
                    break
            
            # Si no se encuentra, buscar en cualquier campo que contenga "email"
            if not user_email:
                for key, value in context.items():
                    if "email" in key.lower() and isinstance(value, str) and "@" in value:
                        user_email = value.lower().strip()
                        break
            
            # Extraer dominio y generar nombre de empresa si se encontró email
            if user_email:
                try:
                    domain_candidate = user_email.split("@")[1]
                    extracted = tldextract.extract(domain_candidate)
                    if extracted.domain and extracted.suffix:
                        domain = f"{extracted.domain}.{extracted.suffix}"
                        # Generar nombre de empresa desde dominio
                        company_name = extracted.domain.replace("-", " ").replace("_", " ").title()
                except Exception as e:
                    print(f"⚠️  Error extrayendo dominio de {user_email}: {e}")
            
            log_payload = {
                "log_id": log_id,
                "timestamp": timestamp,
                "action": action_code,
                "ia_id": self.ia_id,
                "context_encrypted": encrypted_context,
                "context_public": public_context,
                "domain": domain,
                "registered": registered
            }
            
            # Agregar información auto-detectada de empresa a context_public
            # para que el backend la encuentre correctamente
            if user_email:
                public_context["user_email"] = user_email
            if company_name:
                public_context["company_name"] = company_name
            if domain:
                public_context["domain"] = domain
            
            # Add company email for log association if available
            # Removed company_email parameter
            
            # Solo agregar campos de encriptación si tenemos client_secret
            if self.client_secret is not None:
                log_payload.update({
                    "signature": signature,
                    "encryption_metadata": {
                        "algorithm": "AES-256-GCM",
                        "key_derivation": "SHA-256",
                        "key_owner": "client"
                    }
                })
            
            if context_id:
                log_payload["context_id"] = context_id
            if context_type:
                log_payload["context_type"] = context_type
            if context_action:
                log_payload["context_action"] = context_action
                
            if workflow_id:
                log_payload["workflow_id"] = workflow_id
            if workflow_step:
                log_payload["workflow_step"] = workflow_step
            if workflow_step_number is not None:
                log_payload["workflow_step_number"] = workflow_step_number
                
            if self.use_persistent_queue:
                # Use persistent queue with priority based on workflow presence
                priority = 2 if workflow_id else 1  # Higher priority for workflow logs
                log_id = self.persistent_queue.enqueue(log_payload, priority=priority)
                if log_id:
                    # Check if we should trigger immediate flush based on queue size
                    stats = self.persistent_queue.get_stats()
                    if stats['queue_size'] >= self._batch_size:
                        self.flush_batch()
                else:
                    print(f"[AIIA SDK] Warning: Failed to enqueue log to persistent queue")
                    return False
            else:
                # Use in-memory queue
                self._batch_queue.append(log_payload)
                # If batch size reached, trigger immediate flush
                if len(self._batch_queue) >= self._batch_size:
                    self.flush_batch()
        
            return True
        except Exception as e:
            print(f"❌ Error logging action '{action_code}': {str(e)}")
            return False

    def _apply_override_rules(self, text: str) -> Optional[str]:
        """Apply manual override rules to detect action."""
        if not self.rules or not text:
            return None
            
        for rule_code, patterns in self.rules.items():
            if not isinstance(patterns, list):
                continue
                
            for pattern in patterns:
                if pattern.lower() in text.lower():
                    return rule_code
                    
        return None
        
    def _keyword_based_detection(self, text: str) -> Optional[str]:
        """Detect action type using keyword matching as fallback when semantic detection is unavailable."""
        if not text or not isinstance(text, str):
            return None
            
        # Convertir texto a minúsculas para comparación insensible a mayúsculas/minúsculas
        text_lower = text.lower()
        
        # Diccionario de palabras clave para cada tipo de acción
        # Estas palabras clave se usan cuando la detección semántica no está disponible
        keyword_patterns = {
            "GENERATE": [
                "generate", "generated", "generation", "creating", "created", "create",
                "produce", "produced", "producing", "build", "built", "building",
                "write", "written", "writing", "compose", "composed", "composing",
                "construct", "constructed", "constructing", "output", "response",
                "response generated", "text generated", "content generated", 
                "output generated", "result generated", "answer generated",
                "generar", "generado", "generación", "crear", "creado", "creación",
                "producir", "producido", "escribir", "escrito", "respuesta generada"
            ],
            "ANALYZE": [
                "analyze", "analyzed", "analyzing", "analysis", "examine", "examined",
                "examining", "examination", "evaluate", "evaluated", "evaluating",
                "evaluation", "review", "reviewed", "reviewing", "assess", "assessed",
                "assessing", "assessment", "study", "studied", "studying", "investigate",
                "investigated", "investigating", "investigation", "process", "processed",
                "processing", "analysis completed", "document analyzed", "analyzing document",
                "analysis complete", "processed document", "document processing",
                "analizar", "analizado", "análisis", "evaluar", "evaluado", "examinar",
                "análisis completado", "documento analizado", "analizando documento"
            ],
            "CLASSIFY": [
                "classify", "classified", "classifying", "classification", "categorize", 
                "categorized", "categorizing", "categorization", "label", "labeled", 
                "labeling", "tag", "tagged", "tagging", "sort", "sorted", "sorting",
                "group", "grouped", "grouping", "organize", "organized", "organizing",
                "clasificar", "clasificado", "clasificación", "categorizar", "categorizado",
                "etiquetar", "etiquetado"
            ],
            "TRANSFORM": [
                "transform", "transformed", "transforming", "transformation", "convert", 
                "converted", "converting", "conversion", "translate", "translated", 
                "translating", "translation", "change", "changed", "changing", "modify", 
                "modified", "modifying", "modification", "alter", "altered", "altering",
                "process", "processed", "processing", "processing completed", "records processed",
                "data processed", "transformation complete", "conversion complete",
                "transformar", "transformado", "convertir", "convertido", "traducir", "traducido",
                "procesar", "procesado", "procesamiento", "procesamiento completado", "registros procesados"
            ],
            "SUMMARIZE": [
                "summarize", "summarized", "summarizing", "summary", "synthesize", 
                "synthesized", "synthesizing", "synthesis", "condense", "condensed", 
                "condensing", "shorten", "shortened", "shortening", "brief", "briefed", 
                "briefing", "recap", "recapped", "recapping", "abstract", "abstracted",
                "summarization", "summary complete", "summary generated",
                "resumir", "resumido", "resumen", "sintetizar", "sintetizado", "síntesis"
            ],
            "EXTRACT": [
                "extract", "extracted", "extracting", "extraction", "obtain", "obtained", 
                "obtaining", "pull", "pulled", "pulling", "retrieve", "retrieved", 
                "retrieving", "retrieval", "get", "getting", "isolate", "isolated", 
                "isolating", "isolation", "fetch", "fetched", "fetching", "capture",
                "captured", "capturing", "extraction complete", "data extracted",
                "extraer", "extraído", "extracción", "obtener", "obtenido", "obtención"
            ],
            "SEARCH": [
                "search", "searched", "searching", "find", "found", "finding",
                "locate", "located", "locating", "discover", "discovered", "discovering",
                "seek", "seeking", "query", "queried", "querying", "lookup", "retrieve",
                "retrieved", "retrieving", "results", "results found", "search completed",
                "search complete", "found results", "searching in", "knowledge base",
                "database search", "index search", "search results", "query results",
                "buscar", "buscado", "encontrar", "encontrado", "búsqueda", 
                "búsqueda completada", "resultados encontrados", "buscando en", "base de conocimiento"
            ],
            "PREDICT": [
                "predict", "predicted", "predicting", "prediction", "forecast", "forecasted",
                "forecasting", "project", "projected", "projecting", "projection", "anticipate",
                "anticipated", "anticipating", "foresee", "foreseeing", "model", "modeling",
                "prediction completed", "prediction complete", "model prediction", "forecast complete",
                "making prediction", "prediction with model", "predicted value", "forecast result",
                "predecir", "predicho", "predicción", "pronosticar", "pronosticado", "modelo",
                "predicción completada", "realizando predicción", "predicción con modelo"
            ]
        }
        
        # Verificar coincidencias de palabras clave en el texto
        for action_code, keywords in keyword_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return action_code
        
        # Si no se encuentra ninguna coincidencia
        return None

    def flush_batch(self):
        """Manually send pending logs batch."""
        self._flush_batch()
        
        # Mostrar estadísticas de la cola si está usando cola persistente
        if self.use_persistent_queue:
            stats = self.persistent_queue.get_stats()
            print(f"[AIIA SDK] Queue stats: {stats['queue_size']} logs pending, {stats['enqueued']} total enqueued, {stats['dequeued']} processed successfully")
        return True

    def validate_credentials(self) -> bool:
        """Validate API credentials."""
        try:
            response = requests.get(
                f"{self.backend_url}/validate_ia",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=3
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
            
    def update_api_key(self, new_api_key: str) -> bool:
        """Update the API key used for authentication.
        
        Args:
            new_api_key: The new API key to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not new_api_key or not isinstance(new_api_key, str):
            print("[AIIA SDK] Invalid API key provided")
            return False
            
        self.api_key = new_api_key
        print("[AIIA SDK] API key updated successfully")
        return True
        
    def start_workflow(self, workflow_id: Optional[str] = None, workflow_type: Optional[str] = None,
                       context_id: Optional[str] = None, context_type: Optional[str] = None,
                       total_steps: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> 'WorkflowTracker':
        """Start a new workflow and return a WorkflowTracker instance.
        
        Args:
            workflow_id: Optional unique identifier for the workflow. If not provided, a UUID will be generated.
            workflow_type: Optional type/category of the workflow.
            context_id: Optional identifier for the context this workflow is associated with.
            context_type: Optional type of the context (e.g., 'document', 'conversation').
            total_steps: Optional total number of steps expected in this workflow.
            metadata: Optional additional metadata for the workflow.
            
        Returns:
            A WorkflowTracker instance to track this workflow.
        """
        # Create workflow metadata if not provided
        if metadata is None:
            metadata = {}
            
        # Add workflow type to metadata if provided
        if workflow_type:
            metadata['workflow_type'] = workflow_type
            
        # Create and return a workflow tracker
        tracker = WorkflowTracker(
            sdk=self,
            workflow_id=workflow_id,
            context_id=context_id,
            context_type=context_type,
            total_steps=total_steps,
            metadata=metadata
        )
        
        # Log the workflow start event
        self.log_action(
            action_code="WORKFLOW_START",
            context_id=context_id,
            context_type=context_type,
            context_action="start_workflow",
            context=metadata,
            workflow_id=tracker.workflow_id
        )
        
        return tracker
            
    def _auto_inject_middleware(self):
        """Auto-detect framework and inject appropriate middleware."""
        try:
            import sys
            if "fastapi.applications" in sys.modules:
                from fastapi import FastAPI
                from .middleware_fastapi import AIIAMiddleware as FastAPIMiddleware
                for obj in sys.modules["fastapi.applications"].__dict__.values():
                    if isinstance(obj, type) and issubclass(obj, FastAPI):
                        for inst in obj.__subclasses__():
                            if hasattr(inst, "add_middleware"):
                                inst.add_middleware(FastAPIMiddleware, aiia_instance=self)
                                print("[AIIA SDK] Auto-injected middleware in FastAPI")
                                return
            if "flask.app" in sys.modules:
                from flask import Flask
                from .middleware_flask import AIIAMiddleware as FlaskMiddleware
                for obj in sys.modules["flask.app"].__dict__.values():
                    if isinstance(obj, type) and issubclass(obj, Flask):
                        for inst in obj.__subclasses__():
                            if hasattr(inst, "after_request"):
                                FlaskMiddleware(inst, self)
                                print("[AIIA SDK] Auto-injected middleware in Flask")
                                return
            if "django.conf" in sys.modules:
                print("[AIIA SDK] Detected Django: add 'aiia_sdk.middleware_django.AIIAMiddleware' in settings.py")
        except Exception as e:
            print(f"[AIIA SDK] Error in middleware auto-injection: {e}")

    def _apply_override_rules(self, text: str) -> Optional[str]:
        """Apply manual override rules to detect action."""
        if not self.rules or not text:
            return None
            
        for rule_code, patterns in self.rules.items():
            if not isinstance(patterns, list):
                continue
                
            for pattern in patterns:
                if pattern.lower() in text.lower():
                    return rule_code
                    
        return None
        
    def _keyword_based_detection(self, text: str) -> Optional[str]:
        """Detect action type using keyword matching as fallback when semantic detection is unavailable."""
        if not text or not isinstance(text, str):
            return None
            
        # Convertir texto a minúsculas para comparación insensible a mayúsculas/minúsculas
        text_lower = text.lower()
        
        # Diccionario de palabras clave para cada tipo de acción
        # Estas palabras clave se usan cuando la detección semántica no está disponible
        keyword_patterns = {
            "GENERATE": [
                "generate", "generated", "generation", "creating", "created", "create",
                "produce", "produced", "producing", "build", "built", "building",
                "write", "written", "writing", "compose", "composed", "composing",
                "construct", "constructed", "constructing", "output", "response",
                "response generated", "text generated", "content generated", 
                "output generated", "result generated", "answer generated",
                "generar", "generado", "generación", "crear", "creado", "creación",
                "producir", "producido", "escribir", "escrito", "respuesta generada"
            ],
            "ANALYZE": [
                "analyze", "analyzed", "analyzing", "analysis", "examine", "examined",
                "examining", "examination", "evaluate", "evaluated", "evaluating",
                "evaluation", "review", "reviewed", "reviewing", "assess", "assessed",
                "assessing", "assessment", "study", "studied", "studying", "investigate",
                "investigated", "investigating", "investigation", "process", "processed",
                "processing", "analysis completed", "document analyzed", "analyzing document",
                "analysis complete", "processed document", "document processing",
                "analizar", "analizado", "análisis", "evaluar", "evaluado", "examinar",
                "análisis completado", "documento analizado", "analizando documento"
            ],
            "CLASSIFY": [
                "classify", "classified", "classifying", "classification", "categorize", 
                "categorized", "categorizing", "categorization", "label", "labeled", 
                "labeling", "tag", "tagged", "tagging", "sort", "sorted", "sorting",
                "group", "grouped", "grouping", "organize", "organized", "organizing",
                "clasificar", "clasificado", "clasificación", "categorizar", "categorizado",
                "etiquetar", "etiquetado"
            ],
            "TRANSFORM": [
                "transform", "transformed", "transforming", "transformation", "convert", 
                "converted", "converting", "conversion", "translate", "translated", 
                "translating", "translation", "change", "changed", "changing", "modify", 
                "modified", "modifying", "modification", "alter", "altered", "altering",
                "process", "processed", "processing", "processing completed", "records processed",
                "data processed", "transformation complete", "conversion complete",
                "transformar", "transformado", "convertir", "convertido", "traducir", "traducido",
                "procesar", "procesado", "procesamiento", "procesamiento completado", "registros procesados"
            ],
            "SUMMARIZE": [
                "summarize", "summarized", "summarizing", "summary", "synthesize", 
                "synthesized", "synthesizing", "synthesis", "condense", "condensed", 
                "condensing", "shorten", "shortened", "shortening", "brief", "briefed", 
                "briefing", "recap", "recapped", "recapping", "abstract", "abstracted",
                "summarization", "summary complete", "summary generated",
                "resumir", "resumido", "resumen", "sintetizar", "sintetizado", "síntesis"
            ],
            "EXTRACT": [
                "extract", "extracted", "extracting", "extraction", "obtain", "obtained", 
                "obtaining", "pull", "pulled", "pulling", "retrieve", "retrieved", 
                "retrieving", "retrieval", "get", "getting", "isolate", "isolated", 
                "isolating", "isolation", "fetch", "fetched", "fetching", "capture",
                "captured", "capturing", "extraction complete", "data extracted",
                "extraer", "extraído", "extracción", "obtener", "obtenido", "obtención"
            ],
            "SEARCH": [
                "search", "searched", "searching", "find", "found", "finding",
                "locate", "located", "locating", "discover", "discovered", "discovering",
                "seek", "seeking", "query", "queried", "querying", "lookup", "retrieve",
                "retrieved", "retrieving", "results", "results found", "search completed",
                "search complete", "found results", "searching in", "knowledge base",
                "database search", "index search", "search results", "query results",
                "buscar", "buscado", "encontrar", "encontrado", "búsqueda", 
                "búsqueda completada", "resultados encontrados", "buscando en", "base de conocimiento"
            ],
            "PREDICT": [
                "predict", "predicted", "predicting", "prediction", "forecast", "forecasted",
                "forecasting", "project", "projected", "projecting", "projection", "anticipate",
                "anticipated", "anticipating", "foresee", "foreseeing", "model", "modeling",
                "prediction completed", "prediction complete", "model prediction", "forecast complete",
                "making prediction", "prediction with model", "predicted value", "forecast result",
                "predecir", "predicho", "predicción", "pronosticar", "pronosticado", "modelo",
                "predicción completada", "realizando predicción", "predicción con modelo"
            ]
        }
        
        # Verificar coincidencias de palabras clave en el texto
        for action_code, keywords in keyword_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return action_code
        
        # Si no se encuentra ninguna coincidencia
        return None

    def flush_batch(self):
        """Manually send pending logs batch."""
        self._flush_batch()
        
        # Mostrar estadísticas de la cola si está usando cola persistente
        if self.use_persistent_queue:
            stats = self.persistent_queue.get_stats()
            print(f"[AIIA SDK] Queue stats: {stats['queue_size']} logs pending, {stats['enqueued']} total enqueued, {stats['dequeued']} processed successfully")
        return True

    def validate_credentials(self) -> bool:
        """Validate API credentials."""
        try:
            response = requests.get(
                f"{self.backend_url}/validate_ia",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=3
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
            
    def update_api_key(self, new_api_key: str) -> bool:
        """Update the API key used for authentication.
        
        Args:
            new_api_key: The new API key to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not new_api_key or not isinstance(new_api_key, str):
            print("[AIIA SDK] Invalid API key provided")
            return False
            
        self.api_key = new_api_key
        print("[AIIA SDK] API key updated successfully")
        return True
        
    def start_workflow(self, workflow_id: Optional[str] = None, workflow_type: Optional[str] = None,
                       context_id: Optional[str] = None, context_type: Optional[str] = None,
                       total_steps: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> 'WorkflowTracker':
        """Start a new workflow and return a WorkflowTracker instance.
        
        Args:
            workflow_id: Optional unique identifier for the workflow. If not provided, a UUID will be generated.
            workflow_type: Optional type/category of the workflow.
            context_id: Optional identifier for the context this workflow is associated with.
            context_type: Optional type of the context (e.g., 'document', 'conversation').
            total_steps: Optional total number of steps expected in this workflow.
            metadata: Optional additional metadata for the workflow.
            
        Returns:
            A WorkflowTracker instance to track this workflow.
        """
        # Create workflow metadata if not provided
        if metadata is None:
            metadata = {}
            
        # Add workflow type to metadata if provided
        if workflow_type:
            metadata['workflow_type'] = workflow_type
            
        # Create and return a workflow tracker
        tracker = WorkflowTracker(
            sdk=self,
            workflow_id=workflow_id,
            context_id=context_id,
            context_type=context_type,
            total_steps=total_steps,
            metadata=metadata
        )
        
        # Log the workflow start event
        self.log_action(
            action_code="WORKFLOW_START",
            context_id=context_id,
            context_type=context_type,
            context_action="start_workflow",
            context=metadata,
            workflow_id=tracker.workflow_id
        )
        
        return tracker
            
    def _auto_inject_middleware(self):
        """Auto-detect framework and inject appropriate middleware."""
        try:
            import sys
            if "fastapi.applications" in sys.modules:
                from fastapi import FastAPI
                from .middleware_fastapi import AIIAMiddleware as FastAPIMiddleware
                for obj in sys.modules["fastapi.applications"].__dict__.values():
                    if isinstance(obj, type) and issubclass(obj, FastAPI):
                        for inst in obj.__subclasses__():
                            if hasattr(inst, "add_middleware"):
                                inst.add_middleware(FastAPIMiddleware, aiia_instance=self)
                                print("[AIIA SDK] Auto-injected middleware in FastAPI")
                                return
            if "flask.app" in sys.modules:
                from flask import Flask
                from .middleware_flask import AIIAMiddleware as FlaskMiddleware
                for obj in sys.modules["flask.app"].__dict__.values():
                    if isinstance(obj, type) and issubclass(obj, Flask):
                        for inst in obj.__subclasses__():
                            if hasattr(inst, "after_request"):
                                FlaskMiddleware(inst, self)
                                print("[AIIA SDK] Auto-injected middleware in Flask")
                                return
            if "django.conf" in sys.modules:
                print("[AIIA SDK] Detected Django: add 'aiia_sdk.middleware_django.AIIAMiddleware' in settings.py")
        except Exception as e:
            print(f"[AIIA SDK] Error in middleware auto-injection: {e}")

    def _start_batch_worker(self):
        """Start a singleton worker thread for batch processing."""
        if not self._batch_worker_started:
            self._batch_worker_started = True
            self._stop_worker = False
            self._worker_thread = threading.Thread(target=self.worker, daemon=True)
            self._worker_thread.start()
            print("[AIIA SDK] Background batch worker started")
        else:
            self._batch_worker_started = True
            print("[AIIA SDK] Using existing batch worker thread.")
            
    def worker(self):
        """Worker thread function for batch processing with adaptive interval."""
        while not self._stop_worker:
            try:
                # Determine queue size
                queue_size = 0
                if self.use_persistent_queue:
                    stats = self.persistent_queue.get_stats()
                    queue_size = stats['queue_size']
                else:  # In-memory queue
                    queue_size = len(self._batch_queue)
                
                # Process logs if queue has items
                if queue_size > 0:
                    self._flush_batch()
                
                # Calculate next interval using batch optimizer if available
                if hasattr(self, 'batch_optimizer'):
                    next_interval = self.batch_optimizer.get_next_batch_interval(queue_size)
                    
                    # Log adaptive behavior if interval changes significantly
                    if abs(next_interval - self._batch_interval) > 0.5:
                        print(f"[AIIA SDK] Adaptive batch interval: {next_interval:.1f}s (queue size: {queue_size})")
                else:
                    next_interval = self._batch_interval
                
                # Sleep for the calculated interval, but check stop flag periodically
                for _ in range(int(next_interval * 2)):
                    if self._stop_worker:
                        break
                    time.sleep(0.5)
            except Exception as e:
                print(f"[AIIA SDK] Error in batch worker: {e}")
                # Sleep longer on error, but use batch optimizer if available
                error_sleep = self.batch_optimizer.max_batch_interval if hasattr(self, 'batch_optimizer') else self._batch_interval * 2
                for _ in range(int(error_sleep * 2)):
                    if self._stop_worker:
                        break
                    time.sleep(0.5)

    def shutdown(self):
        """Shutdown the SDK gracefully, stopping background threads and flushing queues."""
        print("[AIIA SDK] Shutting down...")
        
        # Stop the worker thread
        if self._batch_worker_started:
            self._stop_worker = True
            if hasattr(self, '_worker_thread') and self._worker_thread.is_alive():
                try:
                    self._worker_thread.join(timeout=5.0)  # Wait up to 5 seconds for worker to stop
                    if self._worker_thread.is_alive():
                        print("[AIIA SDK] Warning: Worker thread did not stop cleanly")
                except Exception as e:
                    print(f"[AIIA SDK] Error stopping worker thread: {e}")
            self._batch_worker_started = False
        
        # Final flush of any pending logs
        try:
            self._flush_batch()
        except Exception as e:
            print(f"[AIIA SDK] Error during final flush: {e}")
        
        # Close persistent queue if used
        if self.use_persistent_queue and hasattr(self, 'persistent_queue'):
            try:
                self.persistent_queue.close()
            except Exception as e:
                print(f"[AIIA SDK] Error closing persistent queue: {e}")
        
        print("[AIIA SDK] Shutdown complete")
    
    def _flush_batch(self):
        """Send accumulated logs batch with performance optimizations."""
        if not self.api_key or not self.backend_url:
            return
            
        url = f"{self.backend_url}/receive_log"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if self.ia_id:
            headers["X-IA-ID"] = self.ia_id
        
        # Add content-type header based on serialization method
        if hasattr(self, 'serialization_manager') and self.serialization_manager.use_msgpack:
            headers["Content-Type"] = "application/msgpack"
        else:
            headers["Content-Type"] = "application/json"
            
        # Add compression header if enabled
        if hasattr(self, 'use_compression') and self.use_compression:
            headers["Accept-Encoding"] = "gzip, deflate"
            
        start_time = time.time()
        
        # Configure retry settings
        max_retries = 3  # Maximum number of retries for HTTP requests
        
        # Initialize retry counter if not exists
        if not hasattr(self, '_retry_count'):
            self._retry_count = 0
            self._retry_timestamp = 0
        
        # Check if we're in a backoff period
        current_time = time.time()
        if self._retry_count > 0 and current_time < self._retry_timestamp:
            # Still in backoff period, skip this flush
            return
            
        # Use persistent queue if enabled
        if hasattr(self, 'use_persistent_queue') and self.use_persistent_queue and hasattr(self, 'persistent_queue'):
            # Process logs from persistent queue
            # Get optimal batch size using batch optimizer if available
            if hasattr(self, 'batch_optimizer'):
                stats = self.persistent_queue.get_stats()
                batch_size = self.batch_optimizer.get_optimal_batch_size(stats['queue_size'])
            else:
                batch_size = self._batch_size
                
            # Process logs from persistent queue
            batch = self.persistent_queue.dequeue(limit=batch_size)
            if not batch:
                return
                
            success_count = 0
            failure_count = 0
            
            for log_id, log_data in batch:
                try:
                    # Apply compression if enabled
                    if hasattr(self, 'use_compression') and self.use_compression:
                        compressed_data = self.compression_manager.compress(log_data)
                        # Add compression metadata to headers
                        if compressed_data["compressed"]:
                            headers["X-Compression"] = compressed_data["algorithm"]
                            headers["X-Original-Size"] = str(compressed_data["original_size"])
                            # Use the compressed data
                            payload = {"compressed_data": compressed_data}
                        else:
                            # Use original data if not compressed
                            payload = log_data
                    else:
                        payload = log_data
                    
                    # Use HTTP manager if available, otherwise use regular requests
                    if hasattr(self, 'http_manager') and self.http_manager:
                        response = self.http_manager.request("POST", url, json=payload, headers=headers)
                    else:
                        response = requests.post(url, json=payload, headers=headers, timeout=10)
                        
                    try:
                        response.raise_for_status()
                        # Mark as successfully processed
                        self.persistent_queue.mark_processed(log_id)
                        success_count += 1
                        # Reset retry counter on success
                        self._retry_count = 0
                    except requests.exceptions.HTTPError as err:
                        if response.status_code == 404:
                            print(f"[AIIA SDK] Endpoint not found (404). Removing log to prevent loops.")
                            self.persistent_queue.mark_processed(log_id)
                        elif response.status_code >= 500:  # Server errors
                            # Mark as failed, will be retried if under max_retries
                            retry_status = self.persistent_queue.mark_failed(log_id)
                            failure_count += 1
                            if retry_status:
                                print(f"[AIIA SDK] Server error sending log {log_id}: {err}. Will retry later.")
                            else:
                                print(f"[AIIA SDK] Server error sending log {log_id}: {err}. Max retries exceeded, dropping log.")
                        else:
                            # Client errors (4xx except 404) - don't retry indefinitely
                            print(f"[AIIA SDK] Client error sending log {log_id}: {err}. Removing log to prevent loops.")
                            self.persistent_queue.mark_processed(log_id)
                except requests.exceptions.RequestException as e:
                    # Network-related errors
                    retry_status = self.persistent_queue.mark_failed(log_id)
                    failure_count += 1
                    if retry_status:
                        print(f"[AIIA SDK] Network error sending log {log_id}: {e}. Will retry later.")
                    else:
                        print(f"[AIIA SDK] Network error sending log {log_id}: {e}. Max retries exceeded, dropping log.")
                except Exception as e:
                    # Other unexpected errors
                    retry_status = self.persistent_queue.mark_failed(log_id)
                    failure_count += 1
                    if retry_status:
                        print(f"[AIIA SDK] Error sending log {log_id}: {e}. Will retry later.")
                    else:
                        print(f"[AIIA SDK] Error sending log {log_id}: {e}. Max retries exceeded, dropping log.")
            
            # Calculate processing time for batch optimization
            processing_time = time.time() - start_time
            if hasattr(self, 'batch_optimizer'):
                self.batch_optimizer.update_metrics(len(batch), processing_time)
            
            if success_count > 0:
                print(f"[AIIA SDK] Sent {success_count} logs successfully, {failure_count} failed in {processing_time:.2f}s")
            
            # Check if there are more logs to process
            stats = self.persistent_queue.get_stats()
            if stats['queue_size'] > 0:
                print(f"[AIIA SDK] {stats['queue_size']} logs remaining in queue.")
        else:
            # Process logs from in-memory queue
            if not self._batch_queue:
                return
                
            batch = list(self._batch_queue)
            try:
                # Apply batch compression if enabled and batch is large enough
                if hasattr(self, 'use_compression') and self.use_compression and len(batch) > 1:
                    # Compress the entire batch as one unit for efficiency
                    compressed_batch = self.compression_manager.compress(batch)
                    if compressed_batch["compressed"]:
                        headers["X-Compression"] = compressed_batch["algorithm"]
                        headers["X-Original-Size"] = str(compressed_batch["original_size"])
                        headers["X-Compression-Ratio"] = str(round(compressed_batch["compression_ratio"], 2))
                        headers["X-Batch-Size"] = str(len(batch))
                        
                        # Send compressed batch in a single request
                        try:
                            if hasattr(self, 'http_manager') and self.http_manager:
                                response = self.http_manager.request("POST", 
                                                                   f"{self.backend_url}/receive_batch", 
                                                                   json={"compressed_batch": compressed_batch}, 
                                                                   headers=headers)
                            else:
                                response = requests.post(f"{self.backend_url}/receive_batch", 
                                                       json={"compressed_batch": compressed_batch}, 
                                                       headers=headers, 
                                                       timeout=10)
                            response.raise_for_status()
                            self._batch_queue.clear()
                            # Reset retry counter on success
                            self._retry_count = 0
                            print(f"[AIIA SDK] Batch of {len(batch)} logs sent successfully as compressed batch. " 
                                  f"Compression ratio: {compressed_batch['compression_ratio']:.2f}x")
                            return
                        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
                            # Handle errors with exponential backoff
                            self._retry_count += 1
                            if self._retry_count >= max_retries:
                                print(f"[AIIA SDK] Max retries ({max_retries}) exceeded for batch. Dropping logs.")
                                self._batch_queue.clear()
                                self._retry_count = 0
                                return
                            else:
                                # Calculate backoff time with exponential increase
                                backoff_time = min(2 ** (self._retry_count - 1), 30)  # Cap at 30 seconds
                                self._retry_timestamp = time.time() + backoff_time
                                print(f"[AIIA SDK] Error sending compressed batch: {e}. Retry {self._retry_count}/{max_retries} after {backoff_time}s backoff.")
                                return
                
                # If compression not enabled or failed, send logs individually
                success_count = 0
                for log in batch:
                    try:
                        if hasattr(self, 'http_manager') and self.http_manager:
                            response = self.http_manager.request("POST", url, json=log, headers=headers)
                        else:
                            response = requests.post(url, json=log, headers=headers, timeout=10)
                        response.raise_for_status()
                        success_count += 1
                    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
                        print(f"[AIIA SDK] Error sending log: {e}")
                
                # If all logs were sent successfully
                if success_count == len(batch):
                    self._batch_queue.clear()
                    # Reset retry counter on success
                    self._retry_count = 0
                    print(f"[AIIA SDK] Batch of {len(batch)} logs sent successfully.")
                else:
                    # Some logs failed, apply exponential backoff
                    self._retry_count += 1
                    if self._retry_count >= max_retries:
                        print(f"[AIIA SDK] Max retries ({max_retries}) exceeded for batch. Dropping logs.")
                        self._batch_queue.clear()
                        self._retry_count = 0
                    else:
                        # Calculate backoff time with exponential increase
                        backoff_time = min(2 ** (self._retry_count - 1), 30)  # Cap at 30 seconds
                        self._retry_timestamp = time.time() + backoff_time
                        print(f"[AIIA SDK] Sent {success_count}/{len(batch)} logs successfully. Retry {self._retry_count}/{max_retries} after {backoff_time}s backoff.")
            except Exception as e:
                # Handle unexpected errors with exponential backoff
                self._retry_count += 1
                if self._retry_count >= max_retries:
                    print(f"[AIIA SDK] Max retries ({max_retries}) exceeded for batch. Dropping logs.")
                    self._batch_queue.clear()
                    self._retry_count = 0
                else:
                    # Calculate backoff time with exponential increase
                    backoff_time = min(2 ** (self._retry_count - 1), 30)  # Cap at 30 seconds
                    self._retry_timestamp = time.time() + backoff_time
                    print(f"[AIIA SDK] Unexpected error in batch processing: {e}. Retry {self._retry_count}/{max_retries} after {backoff_time}s backoff.")
            
            # Calculate processing time for batch optimization
            processing_time = time.time() - start_time
            if hasattr(self, 'batch_optimizer'):
                self.batch_optimizer.update_metrics(len(batch), processing_time)

    def _encrypt_value(self, plaintext: str) -> str:
        """Encrypt a value using AES-256-GCM."""
        if self.client_secret is None:
            return str(plaintext)
            
        key = hashlib.sha256(self.client_secret).digest()
        nonce = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(str(plaintext).encode()) + encryptor.finalize()
        return "aes256:" + base64.b64encode(nonce + encryptor.tag + ciphertext).decode()
        
    def _decrypt_value(self, encrypted_text: str) -> str:
        """Decrypt a value encrypted with _encrypt_value."""
        if not encrypted_text.startswith("aes256:"):
            return encrypted_text
            
        if self.client_secret is None:
            raise ValueError("Cannot decrypt without client_secret")
            
        try:
            data = base64.b64decode(encrypted_text[7:])
            nonce = data[:12]
            tag = data[12:28]
            ciphertext = data[28:]
            
            key = hashlib.sha256(self.client_secret).digest()
            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext.decode()
        except Exception as e:
            raise ValueError(f"Decryption error: {str(e)}")


class WorkflowTracker:
    """
    Helper class to track multi-step AI workflows.
    """
    
    def __init__(self, sdk: AIIA, workflow_id: Optional[str] = None, 
                 context_id: Optional[str] = None, context_type: Optional[str] = None,
                 total_steps: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a workflow tracker.
        """
        self.sdk = sdk
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.context_id = context_id
        self.context_type = context_type
        self.total_steps = total_steps
        self.current_step = 0
        self.metadata = metadata or {}
        self.steps_history = []
    
    def log_step(self, action_code: str = "WORKFLOW_STEP", context_action: str = "workflow_step", 
                 step_name: Optional[str] = None, context: Optional[Dict[str, Any]] = None,
                 step_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log a workflow step.
        
        Args:
            action_code: The action code to log (default: WORKFLOW_STEP)
            context_action: The context action (default: workflow_step)
            step_name: Optional name for this step
            context: Optional context data for the action
            step_data: Optional step-specific data that will be merged with context
            
        Returns:
            bool: True if the step was logged successfully
        """
        self.current_step += 1
        step_name = step_name or context_action
        
        # Initialize context or use provided one
        context = context or {}
        
        # Merge step_data into context if provided
        if step_data:
            context.update(step_data)
        
        # Add workflow progress information
        if self.total_steps:
            context["workflow_total_steps"] = self.total_steps
            context["workflow_progress"] = f"{self.current_step}/{self.total_steps}"
        
        # Add workflow metadata to context
        for key, value in self.metadata.items():
            if key.startswith("workflow_") and key not in context:
                context[key] = value
        
        # Record step in history
        step_info = {
            "step_number": self.current_step,
            "step_name": step_name,
            "action_code": action_code,
            "context_action": context_action,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add step data to history if provided
        if step_data:
            step_info["data"] = step_data
            
        self.steps_history.append(step_info)
        
        return self.sdk.log_action(
            action_code=action_code,
            context_id=self.context_id,
            context_type=self.context_type,
            context_action=context_action,
            context=context,
            workflow_id=self.workflow_id,
            workflow_step=step_name,
            workflow_step_number=self.current_step
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get workflow summary including all logged steps.
        """
        return {
            "workflow_id": self.workflow_id,
            "context_id": self.context_id,
            "context_type": self.context_type,
            "total_steps": self.total_steps,
            "current_step": self.current_step,
            "metadata": self.metadata,
            "steps": self.steps_history,
            "started_at": self.steps_history[0]["timestamp"] if self.steps_history else None,
            "last_update": self.steps_history[-1]["timestamp"] if self.steps_history else None,
            "completed": hasattr(self, "completed_at")
        }
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        Alias for get_summary() for API compatibility.
        """
        return self.get_summary()
    
    def complete_workflow(self, status: str = "completed", final_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Mark the workflow as completed and log a final completion event.
        
        Args:
            status: Status of the workflow (default: "completed")
            final_data: Optional final data to include with the completion event
            
        Returns:
            bool: True if the completion was logged successfully
        """
        # Set completion timestamp
        self.completed_at = datetime.now(timezone.utc).isoformat()
        
        # Prepare context data
        context = final_data or {}
        context["workflow_status"] = status
        context["workflow_duration_seconds"] = self._calculate_duration()
        context["workflow_total_steps"] = self.current_step
        
        # Add workflow metadata
        for key, value in self.metadata.items():
            if key not in context:
                context[key] = value
        
        # Log the completion event
        return self.sdk.log_action(
            action_code="WORKFLOW_COMPLETE",
            context_id=self.context_id,
            context_type=self.context_type,
            context_action="complete_workflow",
            context=context,
            workflow_id=self.workflow_id
        )
    
    def _calculate_duration(self) -> float:
        """
        Calculate the workflow duration in seconds.
        """
        if not self.steps_history:
            return 0.0
            
        try:
            # Parse the ISO timestamp of the first step
            start_time = datetime.fromisoformat(self.steps_history[0]["timestamp"].replace('Z', '+00:00'))
            
            # Use current time if not completed
            end_time = datetime.now(timezone.utc)
            if hasattr(self, "completed_at"):
                end_time = datetime.fromisoformat(self.completed_at.replace('Z', '+00:00'))
                
            # Calculate duration in seconds
            return (end_time - start_time).total_seconds()
        except (ValueError, KeyError, IndexError):
            return 0.0