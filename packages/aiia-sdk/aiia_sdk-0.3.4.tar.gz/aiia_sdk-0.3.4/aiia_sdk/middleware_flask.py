from flask import Response, request
from functools import wraps
from .aiia_sdk import AIIA

class AIIAMiddleware:
    def __init__(self, app, aiia_instance: AIIA):
        self.app = app
        self.aiia = aiia_instance
        self.app.after_request(self.after_request)

    def after_request(self, response: Response):
        try:
            if response.content_type and ("json" in response.content_type or "text" in response.content_type):
                text = response.get_data(as_text=True)
                self.aiia.analyze_output(text)
        except Exception as e:
            print(f"[AIIA SDK] Error analyzing Flask response: {e}")
        return response

# Ejemplo legacy/manual (solo si usas frameworks no estándar)
# ⚠️ Normalmente NO necesitas registrar el middleware manualmente: el SDK lo hace por ti.
# Solo usa esto si tienes un caso edge o disables la auto-inyección:
# from aiia_sdk import AIIA
# from aiia_sdk.middleware_flask import AIIAMiddleware
# aiia = AIIA(api_key="...", client_secret="...", ia_id="...")
# app = Flask(__name__)
# AIIAMiddleware(app, aiia)
