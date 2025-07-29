#!/usr/bin/env python3
"""
AIIA SDK v0.3.0 - 100% PLUG & PLAY
Auto-detección completa de empresa sin configuración manual
"""

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
import os
import time
import tldextract
from dotenv import load_dotenv

# === CONFIGURACIÓN DE ENDPOINT ===
DEFAULT_BACKEND_URL = os.getenv("AIIA_BACKEND_URL", "https://api.aiiatrace.com")

class AIIA:
    """
    AIIA SDK v0.3.0 - 100% PLUG & PLAY
    
    CARACTERÍSTICAS:
    - Solo requiere 3 variables: api_key, client_secret, ia_id
    - Auto-detección de empresa desde el contexto
    - No configuración manual de company_email
    - Adaptable a cualquier tipo de IA y contexto
    """
    
    def __init__(self, api_key: Optional[str] = None, client_secret: Optional[str] = None, 
                 ia_id: Optional[str] = None, backend_url: Optional[str] = None):
        """
        Inicializar AIIA SDK - 100% PLUG & PLAY
        
        Args:
            api_key: API key para autenticación
            client_secret: Client secret para encriptación  
            ia_id: Identificador de la IA
            backend_url: URL del backend AIIA
        """
        # Cargar desde variables de entorno si no se proporcionan
        self.api_key = api_key or os.getenv('AIIA_API_KEY')
        self.client_secret = client_secret or os.getenv('AIIA_CLIENT_SECRET')
        self.ia_id = ia_id or os.getenv('AIIA_IA_ID')
        self.backend_url = backend_url or DEFAULT_BACKEND_URL
        
        # Validar credenciales requeridas
        if not all([self.api_key, self.client_secret, self.ia_id]):
            missing = []
            if not self.api_key: missing.append("api_key/AIIA_API_KEY")
            if not self.client_secret: missing.append("client_secret/AIIA_CLIENT_SECRET") 
            if not self.ia_id: missing.append("ia_id/AIIA_IA_ID")
            raise ValueError(f"Credenciales faltantes: {', '.join(missing)}")
        
        print(f"🚀 AIIA SDK v0.3.0 inicializado - 100% Plug & Play")
        print(f"🔑 IA ID: {self.ia_id}")
        print(f"🌐 Backend: {self.backend_url}")
        
        # Inicializar caches internos
        self._recent_logs = set()
        self._workflow_cache = {}
        
    def log_action(self, *args, **kwargs) -> bool:
        """
        Registrar acción de IA - 100% PLUG & PLAY
        
        AUTO-DETECCIÓN:
        - Extrae automáticamente email del usuario desde el contexto
        - Identifica empresa por dominio del email
        - Asocia log a empresa sin configuración manual
        
        Ejemplos:
        - log_action("process_query", context={"user_email": "juan@empresa.com"})
        - log_action("analyze_document", user_email="maria@hospital.com")
        - log_action("generate_report", context={"client_email": "admin@startup.com"})
        """
        try:
            # Extraer parámetros básicos
            action_code = self._extract_action(args, kwargs)
            context = self._extract_context(args, kwargs)
            
            # AUTO-DETECCIÓN DE EMPRESA
            user_email, domain, company_info = self._auto_detect_company(context)
            
            if not user_email:
                print("⚠️  AIIA SDK: No se detectó email de usuario en el contexto")
                print("💡 Incluye user_email, client_email, o email en el contexto")
                return False
            
            # Construir payload con información auto-detectada
            log_payload = {
                "log_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": action_code,
                "ia_id": self.ia_id,
                "api_key": self.api_key,
                "context_public": context,
                "domain": domain,
                "user_email": user_email,  # Email auto-detectado
                "company_name": company_info.get("name"),
                "registered": True
            }
            
            # Agregar información de workflow si está disponible
            self._add_workflow_info(log_payload, kwargs)
            
            # Enviar al backend
            return self._send_log(log_payload)
            
        except Exception as e:
            print(f"❌ Error registrando acción '{action_code}': {str(e)}")
            return False
    
    def _extract_action(self, args, kwargs) -> str:
        """Extraer código de acción de argumentos"""
        if len(args) >= 1:
            return args[0]
        
        action = kwargs.get('action_code') or kwargs.get('action')
        if not action:
            raise ValueError("Acción requerida: log_action('action_name', ...) o log_action(action='action_name', ...)")
        
        return action
    
    def _extract_context(self, args, kwargs) -> dict:
        """Extraer contexto de argumentos"""
        context = {}
        
        # Contexto desde argumentos posicionales
        if len(args) >= 2 and isinstance(args[1], dict):
            context.update(args[1])
        
        # Contexto desde kwargs
        if 'context' in kwargs and isinstance(kwargs['context'], dict):
            context.update(kwargs['context'])
        
        # Parámetros especiales como contexto
        special_params = ['criticality', 'priority', 'severity', 'user_email', 'client_email', 'email']
        for param in special_params:
            if param in kwargs:
                context[param] = kwargs[param]
        
        return context
    
    def _auto_detect_company(self, context: dict) -> tuple:
        """
        AUTO-DETECCIÓN DE EMPRESA - Núcleo del sistema plug & play
        
        Busca emails en el contexto y extrae información de empresa:
        - user_email, client_email, email, admin_email, etc.
        - Extrae dominio usando tldextract
        - Genera nombre de empresa desde dominio
        
        Returns:
            tuple: (user_email, domain, company_info)
        """
        user_email = None
        domain = None
        
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
        
        # Extraer dominio si se encontró email
        if user_email:
            try:
                domain_candidate = user_email.split("@")[1]
                extracted = tldextract.extract(domain_candidate)
                if extracted.domain and extracted.suffix:
                    domain = f"{extracted.domain}.{extracted.suffix}"
                    
                    # Generar nombre de empresa desde dominio
                    company_name = extracted.domain.replace("-", " ").replace("_", " ").title()
                    
                    company_info = {
                        "name": company_name,
                        "domain": domain,
                        "subdomain": extracted.subdomain if extracted.subdomain else None
                    }
                    
                    return user_email, domain, company_info
            except Exception as e:
                print(f"⚠️  Error extrayendo dominio de {user_email}: {e}")
        
        return user_email, domain, {}
    
    def _add_workflow_info(self, log_payload: dict, kwargs: dict):
        """Agregar información de workflow si está disponible"""
        workflow_fields = ['workflow_id', 'workflow_step', 'workflow_step_number', 
                          'context_id', 'context_type', 'context_action']
        
        for field in workflow_fields:
            if field in kwargs:
                log_payload[field] = kwargs[field]
    
    def _send_log(self, log_payload: dict) -> bool:
        """Enviar log al backend"""
        try:
            url = f"{self.backend_url}/receive_log"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.post(url, json=log_payload, headers=headers, timeout=10)
            
            # Aceptar tanto 200 como 201 como éxito
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('success'):
                    print(f"✅ Log enviado: {log_payload['action']} -> {log_payload.get('company_name', 'N/A')}")
                    return True
                else:
                    print(f"❌ Backend rechazó log: {result.get('error', 'Error desconocido')}")
                    return False
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando log: {e}")
            return False

# Mantener compatibilidad con versiones anteriores
def create_aiia_client(api_key: str, client_secret: str, ia_id: str) -> AIIA:
    """Función helper para crear cliente AIIA"""
    return AIIA(api_key=api_key, client_secret=client_secret, ia_id=ia_id)

# Exportar clase principal
__all__ = ['AIIA', 'create_aiia_client']
