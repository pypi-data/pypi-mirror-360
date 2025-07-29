# AIIA SDK - AI Action Intelligence & Analytics
# Version: 0.3.0 - 100% Plug & Play Compatible

# Exportar la clase AIIA directamente en el nivel superior
# Esto permite importarla como 'from aiia_sdk import AIIA'
from .aiia_sdk import AIIA, WorkflowTracker
from .utils import generate_signature

# Crear alias en el nivel superior para compatibilidad con código existente
AIIA = AIIA

# Import middleware components
try:
    from .middleware_flask import AIIAFlaskMiddleware
except ImportError:
    AIIAFlaskMiddleware = None

try:
    from .middleware_django import AIIADjangoMiddleware
except ImportError:
    AIIADjangoMiddleware = None

try:
    from .middleware_fastapi import AIIAFastAPIMiddleware
except ImportError:
    AIIAFastAPIMiddleware = None

# Define what's available when using 'from aiia_sdk import *'
__all__ = [
    'AIIA',
    'WorkflowTracker',
    'generate_signature',
    'AIIAFlaskMiddleware',
    'AIIADjangoMiddleware',
    'AIIAFastAPIMiddleware'
]

# Package metadata
__version__ = '0.3.4'
__author__ = 'AIIA'
__email__ = 'javier.sanchez@aiiatrace.com'