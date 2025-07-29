from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .aiia_sdk import AIIA

class AIIAMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, aiia_instance: AIIA):
        super().__init__(app)
        self.aiia = aiia_instance

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        try:
            # Only analyze JSON or text responses
            if response.media_type and (
                "json" in response.media_type or "text" in response.media_type
            ):
                # Get the response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                # Rebuild the response for the client
                response.body_iterator = iter([body])
                text = body.decode("utf-8", errors="ignore")
                self.aiia.analyze_output(text)
        except Exception as e:
            print(f"[AIIA SDK] Error analyzing FastAPI response: {e}")
        return response

# Ejemplo legacy/manual (solo si usas frameworks no estándar)
# ⚠️ Normalmente NO necesitas registrar el middleware manualmente: el SDK lo hace por ti.
# Solo usa esto si tienes un caso edge o disables la auto-inyección:
# from aiia_sdk import AIIA
# from aiia_sdk.middleware_fastapi import AIIAMiddleware
# aiia = AIIA(api_key="...", client_secret="...", ia_id="...")
# app.add_middleware(AIIAMiddleware, aiia_instance=aiia)
