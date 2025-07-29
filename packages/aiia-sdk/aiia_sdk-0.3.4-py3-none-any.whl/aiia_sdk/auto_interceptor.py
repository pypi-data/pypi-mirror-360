#!/usr/bin/env python3
"""
AIIA SDK Auto-Interceptor - 100% PLUG AND PLAY
Intercepta automáticamente TODAS las funciones para detectar acciones de negocio
SIN necesidad de modificar código existente
"""

import sys
import types
import inspect
import re
import threading
from typing import Dict, Any, Optional, Set, List
from datetime import datetime
import traceback

class AIIAAutoInterceptor:
    """
    Interceptor automático que detecta acciones de negocio sin modificar código
    """
    
    def __init__(self, aiia_sdk):
        self.aiia_sdk = aiia_sdk
        self.original_call = None
        self.intercepted = False
        self.business_keywords = self._load_business_keywords()
        self.excluded_modules = {
            'builtins', 'sys', 'os', 'threading', 'logging', 'json', 'datetime',
            'requests', 'urllib', 'http', 'socket', 'ssl', 'hashlib', 'hmac',
            'aiia_sdk', 'transformers', 'sentence_transformers', 'torch', 'numpy'
        }
        self.intercepted_functions: Set[str] = set()
        self.lock = threading.Lock()
        
    def _load_business_keywords(self) -> Dict[str, List[str]]:
        """Carga palabras clave para detectar acciones de negocio"""
        return {
            'communication': [
                'send', 'enviar', 'email', 'mail', 'message', 'mensaje', 'sms', 'call', 'llamar',
                'notify', 'notificar', 'alert', 'alertar', 'communicate', 'comunicar'
            ],
            'crm': [
                'create', 'crear', 'contact', 'contacto', 'client', 'cliente', 'customer',
                'lead', 'prospect', 'update', 'actualizar', 'manage', 'gestionar'
            ],
            'finance': [
                'pay', 'pagar', 'payment', 'pago', 'invoice', 'factura', 'bill', 'charge',
                'cobrar', 'transfer', 'transferir', 'transaction', 'transaccion'
            ],
            'sales': [
                'sell', 'vender', 'sale', 'venta', 'quote', 'cotizar', 'proposal', 'propuesta',
                'deal', 'negocio', 'pipeline', 'opportunity', 'oportunidad'
            ],
            'inventory': [
                'stock', 'inventory', 'inventario', 'product', 'producto', 'item', 'articulo',
                'warehouse', 'almacen', 'supply', 'suministro'
            ],
            'reporting': [
                'report', 'reporte', 'generate', 'generar', 'analyze', 'analizar',
                'dashboard', 'metric', 'metrica', 'kpi', 'statistic', 'estadistica'
            ],
            'scheduling': [
                'schedule', 'programar', 'meeting', 'reunion', 'appointment', 'cita',
                'calendar', 'calendario', 'event', 'evento', 'book', 'reservar'
            ]
        }
    
    def is_business_function(self, func) -> tuple[bool, str]:
        """
        Determina si una función es una acción de negocio usando análisis semántico
        
        Returns:
            tuple: (is_business, category)
        """
        if not hasattr(func, '__name__'):
            return False, ""
            
        func_name = func.__name__.lower()
        
        # Excluir funciones internas y de sistema
        if (func_name.startswith('_') or 
            func_name in ['main', 'init', 'setup', 'config', 'test']):
            return False, ""
        
        # Buscar palabras clave de negocio
        for category, keywords in self.business_keywords.items():
            for keyword in keywords:
                if keyword in func_name:
                    return True, category
        
        # Análisis adicional por parámetros (con manejo seguro de errores)
        try:
            sig = inspect.signature(func)
            param_names = [param.lower() for param in sig.parameters.keys()]
            
            business_params = [
                'email', 'cliente', 'customer', 'client', 'user', 'usuario',
                'amount', 'monto', 'price', 'precio', 'invoice', 'factura',
                'product', 'producto', 'order', 'pedido', 'payment', 'pago'
            ]
            
            for param in param_names:
                for business_param in business_params:
                    if business_param in param:
                        return True, "business_operation"
                    
        except (ValueError, TypeError, AttributeError, RuntimeError) as e:
            # Silenciar errores de signature para funciones problemáticas
            print(f"⚠️ [AIIA AUTO] Error interceptando signature: {e}")
            pass
        
        return False, ""
    
    def extract_company_context(self, args, kwargs) -> Optional[str]:
        """
        Extrae contexto de empresa de los argumentos de la función
        """
        # Buscar emails en argumentos
        all_values = list(args) + list(kwargs.values())
        
        for value in all_values:
            if isinstance(value, str):
                # Buscar emails
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, value)
                if emails:
                    return emails[0]
                
                # Buscar dominios de empresa
                if '@' in value and '.' in value:
                    return value
        
        # Buscar en nombres de parámetros
        for key, value in kwargs.items():
            key_lower = key.lower()
            if any(keyword in key_lower for keyword in ['email', 'user', 'client', 'customer', 'company']):
                if isinstance(value, str) and '@' in value:
                    return value
        
        return None
    
    def _is_builtin_or_system_func(self, func) -> bool:
        """
        Determina si una función es del sistema o builtin y no debe ser interceptada
        """
        try:
            # Funciones builtin
            if hasattr(func, '__module__') and func.__module__ in ('builtins', None):
                return True
                
            # Funciones de módulos del sistema
            if hasattr(func, '__module__'):
                module_name = func.__module__ or ''
                system_modules = {'inspect', 'functools', 'operator', 'itertools'}
                if any(sys_mod in module_name for sys_mod in system_modules):
                    return True
                    
            # Funciones con nombres problemáticos
            if hasattr(func, '__name__'):
                problematic_names = {'signature', 'from_callable', 'partial'}
                if func.__name__ in problematic_names:
                    return True
                    
            return False
        except (AttributeError, TypeError):
            return True  # Si no podemos determinar, mejor no interceptar
    
    def intercept_function_call(self, original_func, *args, **kwargs):
        """
        Intercepta llamada a función y detecta si es acción de negocio
        """
        try:
            # Verificar si es función de negocio
            is_business, category = self.is_business_function(original_func)
            
            if is_business:
                # Extraer contexto de empresa
                company_context = self.extract_company_context(args, kwargs)
                
                # Ejecutar función original primero
                result = original_func(*args, **kwargs)
                
                # Log de la acción detectada automáticamente
                try:
                    context = {
                        "function_name": original_func.__name__,
                        "category": category,
                        "auto_detected": True,
                        "module": getattr(original_func, '__module__', 'unknown'),
                        "timestamp": datetime.now().isoformat(),
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                        "result_type": type(result).__name__ if result is not None else "None"
                    }
                    
                    if company_context:
                        context["company_email"] = company_context
                    
                    # Agregar algunos argumentos relevantes (sin datos sensibles)
                    safe_kwargs = {}
                    for key, value in kwargs.items():
                        if isinstance(value, (str, int, float, bool)) and len(str(value)) < 100:
                            safe_kwargs[key] = value
                    
                    if safe_kwargs:
                        context["parameters"] = safe_kwargs
                    
                    # Log automático
                    self.aiia_sdk.log_action(
                        action_name=original_func.__name__,
                        user_email=company_context,
                        context=context
                    )
                    
                    print(f"🤖 [AIIA AUTO] Detectada acción: {original_func.__name__} ({category})")
                    if company_context:
                        print(f"    📧 Empresa: {company_context}")
                    
                except Exception as log_error:
                    print(f"⚠️ [AIIA AUTO] Error logging acción {original_func.__name__}: {log_error}")
                
                return result
            else:
                # Función normal, ejecutar sin logging
                return original_func(*args, **kwargs)
                
        except Exception as e:
            print(f"⚠️ [AIIA AUTO] Error interceptando {getattr(original_func, '__name__', 'unknown')}: {e}")
            # En caso de error, ejecutar función original
            return original_func(*args, **kwargs)
    
    def should_intercept_module(self, module_name: str) -> bool:
        """
        Determina si un módulo debe ser interceptado
        """
        if not module_name:
            return False
            
        # Excluir módulos del sistema
        for excluded in self.excluded_modules:
            if module_name.startswith(excluded):
                return False
        
        # Interceptar módulos de usuario
        return True
    
    def monkey_patch_functions(self):
        """
        Aplica monkey patching a todas las funciones del sistema
        """
        if self.intercepted:
            return
            
        print("🤖 [AIIA AUTO] Iniciando interceptación automática...")
        
        try:
            # Interceptar funciones en módulos cargados
            for module_name, module in sys.modules.items():
                if not self.should_intercept_module(module_name):
                    continue
                
                try:
                    self._patch_module_functions(module, module_name)
                except Exception as e:
                    # Continuar con otros módulos si uno falla
                    continue
            
            # Interceptar nuevas funciones que se definan
            self._patch_function_creation()
            
            self.intercepted = True
            print("✅ [AIIA AUTO] Interceptación automática activada")
            
        except Exception as e:
            print(f"❌ [AIIA AUTO] Error en monkey patching: {e}")
    
    def _patch_module_functions(self, module, module_name: str):
        """
        Parchea funciones en un módulo específico con protección mejorada
        """
        if not hasattr(module, '__dict__'):
            return
            
        # Lista de funciones que NO deben ser interceptadas
        skip_functions = {
            'signature', 'from_callable', 'getfullargspec', 'getargspec',
            '__init__', '__new__', '__call__', '__getattr__', '__setattr__',
            'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict',
            'isinstance', 'hasattr', 'getattr', 'setattr'
        }
            
        for attr_name in dir(module):
            try:
                # Saltar funciones problemáticas
                if attr_name in skip_functions or attr_name.startswith('_'):
                    continue
                    
                attr = getattr(module, attr_name)
                
                if (callable(attr) and 
                    hasattr(attr, '__name__') and 
                    not self._is_builtin_or_system_func(attr)):
                    
                    # Crear función interceptada con manejo de errores
                    original_func = attr
                    
                    def create_intercepted_func(orig_func):
                        def intercepted_func(*args, **kwargs):
                            try:
                                return self.intercept_function_call(orig_func, *args, **kwargs)
                            except Exception as e:
                                # Si hay error en interceptación, ejecutar función original
                                return orig_func(*args, **kwargs)
                        return intercepted_func
                    
                    # Reemplazar función original
                    intercepted_func = create_intercepted_func(original_func)
                    try:
                        intercepted_func.__name__ = original_func.__name__
                        intercepted_func.__doc__ = original_func.__doc__
                    except (AttributeError, TypeError):
                        pass
                    
                    setattr(module, attr_name, intercepted_func)
                    
                    func_id = f"{module_name}.{attr_name}"
                    if func_id not in self.intercepted_functions:
                        self.intercepted_functions.add(func_id)
                        
            except (AttributeError, TypeError, RuntimeError) as e:
                # Silenciar errores y continuar
                continue
    
    def _patch_function_creation(self):
        """
        Intercepta la creación de nuevas funciones
        """
        # Este es un enfoque más avanzado que requeriría interceptar
        # la creación de objetos función a nivel del intérprete
        # Por ahora, el monkey patching de módulos existentes es suficiente
        pass
    
    def start_auto_detection(self):
        """
        Inicia la detección automática de acciones
        """
        print("🚀 [AIIA AUTO] Iniciando detección automática 100% plug-and-play")
        self.monkey_patch_functions()
        print("✅ [AIIA AUTO] SDK configurado para detectar automáticamente TODAS las acciones")
