import os
import threading
import time
from pathlib import Path
from typing import List, Optional, Union, Dict, Any

class SemanticModelSingleton:
    _instance = None
    _model = None
    _lock = threading.Lock()
    _load_attempted = False
    _load_error = None
    _model_info = {
        "name": "all-MiniLM-L6-v2",  # Modelo más ligero pero efectivo
        "size_mb": 80,  # Tamaño aproximado en MB
        "dimensions": 384,  # Dimensiones del embedding
        "languages": ["multilingual"],  # Soporta múltiples idiomas
    }
    
    @classmethod
    def get_model(cls):
        """Get the singleton model instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._model
    
    @classmethod
    def get_model_info(cls) -> Dict[str, Any]:
        """Get information about the semantic model."""
        info = cls._model_info.copy()
        info["loaded"] = cls._model is not None
        info["load_attempted"] = cls._load_attempted
        if cls._load_error:
            info["error"] = str(cls._load_error)
        return info
    
    @classmethod
    def get_embeddings(cls, texts: List[str]):
        """Get embeddings for multiple texts."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        
        if cls._model is None:
            if cls._load_error:
                print(f"[AIIA SDK] ⚠️ Semantic model not available: {cls._load_error}")
            return None
            
        try:
            # Convertir a lista si es necesario
            if not isinstance(texts, list):
                texts = [texts]
                
            # Limitar longitud para evitar problemas de memoria
            max_length = 512
            truncated_texts = [t[:max_length] if len(t) > max_length else t for t in texts]
            
            embeddings = cls._model.encode(
                truncated_texts, 
                convert_to_tensor=True,
                device="cpu",
                normalize_embeddings=True
            )
            # Convertir a numpy para evitar problemas con tensores
            if hasattr(embeddings, 'cpu') and hasattr(embeddings, 'numpy'):
                return embeddings.cpu().numpy()
            return embeddings
        except Exception as e:
            print(f"[AIIA SDK] ⚠️ Error encoding texts: {e}")
            return None
    
    @classmethod
    def get_embedding(cls, text: str):
        """Get embedding for a single text."""
        if not text or not isinstance(text, str):
            return None
            
        return cls.get_embeddings([text])
    
    def __init__(self):
        """Private constructor."""
        if SemanticModelSingleton._model is not None:
            return
            
        # Marcar que se intentó cargar el modelo
        SemanticModelSingleton._load_attempted = True
        
        try:
            # Configuración para evitar problemas con tensores meta
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            
            # Intentar importar las dependencias
            try:
                import torch
                from sentence_transformers import SentenceTransformer
            except ImportError as e:
                SemanticModelSingleton._load_error = f"Missing dependencies: {e}. Install with 'pip install AIIA_TEST[semantic]'"
                print(f"[AIIA SDK] ⚠️ {SemanticModelSingleton._load_error}")
                return
                
            # Desactivar gradientes para ahorrar memoria
            torch.set_grad_enabled(False)
            
            # Forzar CPU para evitar problemas de concurrencia
            device = "cpu"
            
            # Asegurarse de que el directorio de caché existe
            cache_folder = Path(__file__).parent / "model_cache"
            cache_folder.mkdir(exist_ok=True)
            
            print(f"[AIIA SDK] Loading semantic model {self._model_info['name']} (~{self._model_info['size_mb']}MB)...")
            start_time = time.time()
            
            # Cargar el modelo con configuración explícita
            SemanticModelSingleton._model = SentenceTransformer(
                self._model_info['name'],
                device=device,
                cache_folder=str(cache_folder)
            )
            
            load_time = time.time() - start_time
            print(f"[AIIA SDK] ✅ Model loaded successfully in {load_time:.2f}s on {device}")
            
        except Exception as e:
            SemanticModelSingleton._load_error = str(e)
            print(f"[AIIA SDK] ⚠️ Error loading semantic model: {e}")
            print("[AIIA SDK] ⚠️ The SDK will continue to function without semantic detection")
            SemanticModelSingleton._model = None
