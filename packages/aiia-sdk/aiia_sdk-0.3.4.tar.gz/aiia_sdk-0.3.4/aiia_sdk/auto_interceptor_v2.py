#!/usr/bin/env python3
"""
AIIA SDK Auto-Interceptor V2 - 100% PLUG AND PLAY
SOLUCIÓN ANTI-RECURSIÓN ROBUSTA
"""

import sys
import types
import inspect
import re
import threading
from typing import Dict, Any, Optional, Set, List
from datetime import datetime
import traceback

class AIIAAutoInterceptorV2:
    """
    Auto-interceptor con protección anti-recursión de 3 capas
    """
    
    def __init__(self, aiia_sdk):
        self.aiia_sdk = aiia_sdk
        self.intercepted = False
        self.business_keywords = self._load_business_keywords()
        
        # CAPA 1: Thread-local para evitar recursión por thread
        self._thread_local = threading.local()
        
        # CAPA 2: Set global de funciones en ejecución
        self._executing_functions = set()
        self._execution_lock = threading.Lock()
        
        # CAPA 3: Lista de funciones que NUNCA deben ser interceptadas
        self.never_intercept = {
            'log_action', 'analyze_output', '_auto_detect_company',
            '_detect_direct_context', '_detect_http_headers', 
            '_detect_thread_local', '_detect_stack_variables',
            '_detect_environment', '_detect_database_context',
            'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict',
            'isinstance', 'hasattr', 'getattr', 'setattr', '__init__',
            '__new__', '__call__', '__getattr__', '__setattr__',
            'signature', 'from_callable', 'getfullargspec', 'getargspec'
        }
        
        # Módulos que no deben ser interceptados
        self.excluded_modules = {
            'builtins', 'sys', 'os', 'threading', 'logging', 'json', 'datetime',
            'requests', 'urllib', 'http', 'socket', 'ssl', 'hashlib', 'hmac',
            'aiia_sdk', 'transformers', 'sentence_transformers', 'torch', 'numpy',
            'inspect', 'traceback', 're', 'types'
        }
        
        self.intercepted_functions: Set[str] = set()
        self.lock = threading.Lock()
        
    def _load_business_keywords(self) -> Dict[str, List[str]]:
        """Carga palabras clave para detectar acciones de negocio"""
        return {
            'ai_processing': [
                'generate', 'generar', 'process', 'procesar', 'analyze', 'analizar',
                'predict', 'predecir', 'classify', 'clasificar', 'extract', 'extraer',
                'summarize', 'resumir', 'translate', 'traducir', 'complete', 'completar',
                'approve', 'aprobar', 'review', 'revisar', 'decide', 'decidir'
            ],
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
            'content': [
                'write', 'escribir', 'create', 'crear', 'edit', 'editar', 'review', 'revisar',
                'publish', 'publicar', 'draft', 'borrador', 'content', 'contenido'
            ]
        }
    
    def _is_in_recursion(self, func_name: str) -> bool:
        """
        CAPA 1: Verificar recursión usando thread-local storage
        """
        if not hasattr(self._thread_local, 'call_stack'):
            self._thread_local.call_stack = set()
        
        if func_name in self._thread_local.call_stack:
            return True
        
        return False
    
    def _enter_function(self, func_name: str):
        """Marcar entrada a función"""
        if not hasattr(self._thread_local, 'call_stack'):
            self._thread_local.call_stack = set()
        
        self._thread_local.call_stack.add(func_name)
        
        with self._execution_lock:
            self._executing_functions.add(func_name)
    
    def _exit_function(self, func_name: str):
        """Marcar salida de función"""
        if hasattr(self._thread_local, 'call_stack'):
            self._thread_local.call_stack.discard(func_name)
        
        with self._execution_lock:
            self._executing_functions.discard(func_name)
    
    def is_business_function(self, func) -> tuple[bool, str]:
        """
        Determina si una función es una acción de negocio
        """
        if not hasattr(func, '__name__'):
            return False, ""
            
        func_name = func.__name__.lower()
        
        # CAPA 3: Nunca interceptar funciones críticas
        if func_name in self.never_intercept:
            return False, ""
        
        # Excluir funciones internas y de sistema
        if (func_name.startswith('_') or 
            func_name in ['main', 'init', 'setup', 'config', 'test']):
            return False, ""
        
        # Buscar palabras clave de negocio
        for category, keywords in self.business_keywords.items():
            for keyword in keywords:
                if keyword in func_name:
                    return True, category
        
        return False, ""
    
    def extract_company_context(self, args, kwargs) -> dict:
        """
        Extrae contexto de empresa usando el sistema multi-nivel completo del SDK
        """
        # Construir contexto desde argumentos y kwargs
        context = {}
        
        # Buscar valores relevantes en argumentos
        all_values = list(args) + list(kwargs.values())
        
        # Buscar emails
        for value in all_values:
            if isinstance(value, str) and '@' in value and '.' in value:
                if re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
                    context['user_email'] = value
                    break
        
        # Buscar en kwargs específicos
        email_fields = ['user_email', 'email', 'sender_email', 'recipient_email', 
                       'customer_email', 'admin_email', 'authenticated_user']
        
        for field in email_fields:
            if field in kwargs and kwargs[field]:
                context['user_email'] = str(kwargs[field])
                break
        
        # NOTA: NO buscamos company_id/user_id externos porque no tienen relación
        # con los IDs internos de AIIA. Solo los emails son universales.
        
        # SIEMPRE usar el sistema multi-nivel completo del SDK
        # No solo cuando hay contexto en argumentos - buscar en headers, stack, env, etc.
        try:
            user_email, domain, company_info = self.aiia_sdk._auto_detect_company(context)
            
            if user_email and domain:
                result = {
                    'user_email': user_email,
                    'domain': domain, 
                    'company_info': company_info,
                    'detection_success': True
                }
                return result
        except Exception as e:
            # Silenciar errores para no afectar la función original
            pass
        
        # Si no se detectó nada con el sistema multi-nivel
        return {'detection_success': False}
    
    def _is_builtin_or_system_func(self, func) -> bool:
        """
        Determina si una función es del sistema y no debe ser interceptada
        """
        try:
            if not hasattr(func, '__module__'):
                return True
            
            module_name = getattr(func, '__module__', '')
            if not module_name or module_name in self.excluded_modules:
                return True
            
            # Funciones builtin
            if hasattr(func, '__qualname__') and 'builtin' in str(type(func)):
                return True
            
            return False
        except:
            return True
    
    def intercept_function_call(self, original_func, *args, **kwargs):
        """
        Intercepta llamada a función con protección anti-recursión de 3 capas
        """
        func_name = getattr(original_func, '__name__', 'unknown')
        
        try:
            # CAPA 1: Verificar recursión thread-local
            if self._is_in_recursion(func_name):
                return original_func(*args, **kwargs)
            
            # CAPA 2: Verificar si ya está ejecutándose globalmente
            with self._execution_lock:
                if func_name in self._executing_functions:
                    return original_func(*args, **kwargs)
            
            # CAPA 3: Verificar lista de funciones prohibidas
            if func_name in self.never_intercept:
                return original_func(*args, **kwargs)
            
            # Marcar entrada a función
            self._enter_function(func_name)
            
            try:
                # Verificar si es función de negocio
                is_business, category = self.is_business_function(original_func)
                
                if is_business:
                    # Extraer contexto de empresa
                    company_context = self.extract_company_context(args, kwargs)
                    
                    # Ejecutar función original primero
                    result = original_func(*args, **kwargs)
                    
                    # Log DIRECTO al backend (sin usar log_action para evitar recursión)
                    try:
                        self._direct_log_to_backend(
                            func_name, category, company_context, args, kwargs, result
                        )
                    except Exception as log_error:
                        # Silenciar errores de logging para no afectar la función original
                        pass
                    
                    return result
                else:
                    # Función normal, ejecutar sin logging
                    return original_func(*args, **kwargs)
                    
            finally:
                # Siempre marcar salida de función
                self._exit_function(func_name)
                
        except Exception as e:
            # En caso de error, ejecutar función original
            self._exit_function(func_name)
            return original_func(*args, **kwargs)
    
    def _direct_log_to_backend(self, func_name, category, company_context, args, kwargs, result):
        """
        Log DIRECTO al backend sin usar log_action (evita recursión)
        """
        try:
            # Verificar si se detectó contexto exitosamente
            if company_context.get('detection_success', False):
                user_email = company_context.get('user_email')
                domain = company_context.get('domain')
                company_info = company_context.get('company_info', {})
                
                print(f"✅ [AIIA AUTO] Detectada: {func_name} ({category}) - {user_email} @ {domain}")
                print(f"   🎯 Método: {company_info.get('detection_method', 'unknown')}")
                print(f"   📊 Confianza: {company_info.get('confidence', 'unknown')}")
                print(f"   🔢 Nivel: {company_info.get('level', 'unknown')}")
                
                # Crear payload directo para el backend
                payload = {
                    "ia_id": self.aiia_sdk.ia_id,
                    "action_name": func_name,
                    "user_email": user_email,
                    "company_domain": domain,
                    "company_name": company_info.get('name', domain),
                    "context": {
                        "function_name": func_name,
                        "category": category,
                        "auto_detected": True,
                        "timestamp": datetime.now().isoformat(),
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                        "result_type": type(result).__name__ if result is not None else "None"
                    },
                    "detection_metadata": company_info,
                    "timestamp": datetime.now().isoformat(),
                    "auto_intercepted": True
                }
                
                # Aquí iría la llamada HTTP directa al backend
                # self._send_to_backend(payload)
                
            else:
                # No se detectó contexto - log para debug
                print(f"⚠️ [AIIA AUTO] Sin contexto: {func_name} ({category})")
                if company_context:
                    print(f"   📝 Contexto parcial: {company_context}")
                
        except Exception as e:
            # Silenciar errores para no afectar la función original
            print(f"❌ [AIIA AUTO] Error en log: {e}")
    
    def should_intercept_module(self, module_name: str) -> bool:
        """
        Determina si un módulo debe ser interceptado
        """
        if not module_name or module_name in self.excluded_modules:
            return False
        
        # Solo interceptar módulos de aplicación (no librerías)
        if any(excluded in module_name.lower() for excluded in self.excluded_modules):
            return False
        
        return True
    
    def monkey_patch_functions(self):
        """
        Inicia interceptación usando sys.settrace() como APM tools reales (OpenTelemetry, New Relic, DataDog)
        Intercepta TODAS las funciones: nested, dinámicas, en clases, etc.
        """
        if self.intercepted:
            return
            
        try:
            print("🔧 [AIIA TRACE] Activando interceptación global con sys.settrace()...")
            
            # Configurar trace function global para interceptar TODAS las llamadas
            sys.settrace(self._trace_function)
            
            # También configurar para threads nuevos
            import threading
            threading.settrace(self._trace_function)
            
            self.intercepted = True
            print("🔍 [AIIA TRACE] Interceptación global activada - Captura funciones nested/dinámicas")
            print("✅ [AIIA AUTO] Interceptación automática activada")
            
        except Exception as e:
            print(f"❌ [AIIA TRACE] Error activando interceptación: {e}")
        
    def _trace_function(self, frame, event, arg):
        """
        Función de trace que intercepta TODAS las llamadas a funciones
        Usado por APM tools como OpenTelemetry, New Relic, DataDog
        """
        # Solo procesar eventos de llamada a función
        if event != 'call':
            return
            
        try:
            # Obtener información de la función
            func_name = frame.f_code.co_name
            filename = frame.f_code.co_filename
            
            # Protección anti-recursión
            if self._is_in_recursion(func_name):
                return
            
            # Filtrar funciones del sistema/internas
            if self._should_skip_function(func_name, filename):
                return
                
            # Extraer argumentos de TODAS las funciones
            args, kwargs = self._extract_function_args(frame)
            
            # Verificar si la función tiene contexto de usuario/empresa
            context = self.extract_company_context(args, kwargs)
            
            if context.get('user_email'):
                # Esta función SÍ tiene contexto relevante - interceptar
                is_business, category = self._is_business_function_by_name(func_name)
                
                print(f"✅ [AIIA TRACE] Interceptada función con contexto: {func_name}")
                print(f"🎯 [AIIA TRACE] Contexto detectado: {context['user_email']} -> {context.get('company_domain', 'N/A')}")
                
                # Procesar la función interceptada
                self._process_intercepted_function(func_name, args, kwargs, category or 'unknown', context)
                
        except Exception as e:
            # Silenciar errores para no romper la aplicación
            pass
            
        return
    
    def _should_skip_function(self, func_name, filename):
        """Determina si debe saltar una función (sistema, interna, etc.)"""
        # Saltar funciones del SDK
        if 'aiia_sdk' in filename:
            return True
            
        # Saltar funciones del sistema
        if func_name.startswith('_') or func_name in ['<module>', '<lambda>']:
            return True
            
        # Saltar librerías estándar
        if any(path in filename for path in ['/lib/python', 'site-packages', '<frozen']):
            return True
            
        return False
    
    def _is_business_function_by_name(self, func_name):
        """Determina si una función es de negocio basado en su nombre"""
        func_name_lower = func_name.lower()
        
        if func_name_lower in self.never_intercept:
            return False, ""
            
        for category, keywords in self.business_keywords.items():
            for keyword in keywords:
                if keyword in func_name_lower:
                    return True, category
                    
        return False, ""
    
    def _extract_function_args(self, frame):
        """Extrae argumentos y kwargs de un frame de función"""
        try:
            # Obtener variables locales del frame
            local_vars = frame.f_locals
            
            # Obtener nombres de argumentos del código
            code = frame.f_code
            arg_names = code.co_varnames[:code.co_argcount]
            
            # Construir args y kwargs
            args = []
            kwargs = {}
            
            for arg_name in arg_names:
                if arg_name in local_vars:
                    value = local_vars[arg_name]
                    if arg_name == 'self':  # Saltar 'self' en métodos
                        continue
                    args.append(value)
                    kwargs[arg_name] = value
                    
            return tuple(args), kwargs
            
        except Exception:
            return (), {}
    
    def _process_intercepted_function(self, func_name, args, kwargs, category, context):
        """Procesa una función interceptada que ya tiene contexto válido"""
        try:
            # Generar IDs únicos para contexto y workflow
            import uuid
            context_id = str(uuid.uuid4())[:8]  # ID corto para contexto
            workflow_id = f"wf_{str(uuid.uuid4())[:8]}"  # ID de workflow
            
            # Crear log de acción completo
            action_data = {
                'function_name': func_name,
                'category': category,
                'user_email': context['user_email'],
                'company_domain': context.get('company_domain'),
                'args_preview': str(args)[:100] if args else '',
                'intercepted_via': 'sys.settrace',
                'detection_method': 'context_based',
                # CAMPOS REQUERIDOS PARA LOGS COMPLETOS
                'context_id': context_id,
                'workflow_id': workflow_id,
                'workflow_step': 1,  # Paso 1 para acciones individuales
                'context_type': 'business_function'  # Tipo de contexto
            }
            
            # Enviar al SDK para logging
            if hasattr(self.aiia_sdk, 'log_action'):
                self.aiia_sdk.log_action(
                    action=f"{category}_{func_name}",
                    details=action_data,
                    user_email=context['user_email'],
                    context_id=context_id,
                    workflow_id=workflow_id,
                    workflow_step=1
                )
                print(f"📤 [AIIA TRACE] Log enviado para {func_name}")
                    
        except Exception as e:
            # Silenciar errores para no romper la aplicación
            pass
    
    def _patch_module_functions(self, module, module_name: str):
        """
        Parchea funciones en un módulo específico
        """
        if not hasattr(module, '__dict__'):
            return
        
        functions_found = 0
        functions_patched = 0
        
        for attr_name in list(dir(module)):
            try:
                attr = getattr(module, attr_name)
                if callable(attr) and hasattr(attr, '__name__'):
                    functions_found += 1
                        
                    # Filtrar funciones de sistema
                    if self._is_builtin_or_system_func(attr):
                        continue
                        
                    # Verificar si es función de negocio
                    is_business, category = self.is_business_function(attr)
                        
                    if is_business:
                        # Parchear la función
                        original_func = attr
                        wrapped_func = self._create_interceptor_wrapper(original_func, category)
                        setattr(module, attr_name, wrapped_func)
                        functions_patched += 1
                    else:
                        # Parchear todas las funciones para detectar contexto
                        original_func = attr
                        wrapped_func = self._create_interceptor_wrapper(original_func, "unknown")
                        setattr(module, attr_name, wrapped_func)
                        functions_patched += 1
                            
            except (AttributeError, TypeError, RuntimeError) as e:
                continue
    
    def _create_interceptor_wrapper(self, original_func, category):
        """Crea wrapper para interceptar función"""
        def wrapper(*args, **kwargs):
            return self.intercept_function_call(original_func, *args, **kwargs)
        
        # Preservar metadatos
        try:
            wrapper.__name__ = original_func.__name__
            wrapper.__doc__ = original_func.__doc__
            wrapper.__module__ = original_func.__module__
        except (AttributeError, TypeError):
            pass
        
        return wrapper
    
    def start_auto_detection(self):
        """
        Inicia la detección automática 100% plug-and-play
        """
        print("🚀 [AIIA AUTO V2] Iniciando detección automática con protección anti-recursión")
        self.monkey_patch_functions()
        print("✅ [AIIA AUTO V2] SDK configurado para detectar automáticamente TODAS las acciones")
        print("🛡️ [AIIA AUTO V2] Protección anti-recursión de 3 capas activada")
