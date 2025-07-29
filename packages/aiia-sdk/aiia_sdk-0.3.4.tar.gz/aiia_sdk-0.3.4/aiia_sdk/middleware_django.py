from django.utils.deprecation import MiddlewareMixin
from .aiia_sdk import AIIA

class AIIAMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None, aiia_instance: AIIA=None):
        super().__init__(get_response)
        self.aiia = aiia_instance

    def process_response(self, request, response):
        try:
            content_type = getattr(response, 'content_type', None)
            if content_type and ("json" in content_type or "text" in content_type):
                text = response.content.decode("utf-8", errors="ignore")
                if self.aiia:
                    self.aiia.analyze_output(text)
        except Exception as e:
            print(f"[AIIA SDK] Error analyzing Django response: {e}")
        return response

# ⚠️ Django requiere pasos manuales por limitaciones del framework.
# Añade 'aiia_sdk.middleware_django.AIIAMiddleware' en settings.py y asigna la instancia globalmente en tu AppConfig o arranque.
# from aiia_sdk import AIIA
# from aiia_sdk.middleware_django import AIIAMiddleware
# aiia = AIIA(api_key="...", client_secret="...", ia_id="...")
# AIIAMiddleware.aiia = aiia
