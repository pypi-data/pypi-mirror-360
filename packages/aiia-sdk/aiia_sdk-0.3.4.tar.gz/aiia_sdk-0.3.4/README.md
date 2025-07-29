# AIIA SDK

The official SDK for integrating the AIIA protocol (Artificial Intelligence Interaction Agreement) into your AI systems.  
This library allows AI applications to log actions in a secure, auditable, and legally traceable way.

## ⚡️ Quickstart (Resumen Rápido)

1. **Instala el SDK:**
   ```bash
   pip install AIIA_TEST
   ```
2. **Configura tus credenciales en `.env`:**
   ```env
   AIIA_API_KEY=tu_api_key
   AIIA_CLIENT_SECRET=tu_client_secret
   AIIA_IA_ID=tu_ia_id
   ```
3. **Integra según tu framework:**

   - **FastAPI y Flask:**
     ```python
     from aiia_sdk import AIIA
     aiia = AIIA()
     # ¡NO necesitas registrar el middleware manualmente! El SDK lo hace por ti si detecta el framework.
     # Solo en casos edge o si disables la auto-inyección, consulta la documentación avanzada.
     ```
   - **Django:**
     ```python
     # settings.py
     MIDDLEWARE = [
         ...
         'aiia_sdk.middleware_django.AIIAMiddleware',
         ...
     ]
     # apps.py o arranque
     from aiia_sdk import AIIA
     from aiia_sdk.middleware_django import AIIAMiddleware
     aiia = AIIA()
     AIIAMiddleware.aiia = aiia
     ```
     ⚠️ Django requiere pasos manuales por limitaciones del framework.
   - **Universal:**
     ```python
     from aiia_sdk import AIIA
     aiia = AIIA()
     output = "respuesta de tu IA"
     aiia.analyze_output(output)
     ```

## What this SDK does

The AIIA SDK enables developers to integrate plug & play action logging and auditing into any AI-based system. It offers a dual-layer logging mechanism:

### Layer 1: Automatic action detection

- The SDK analyzes all outputs from the AI system.
- It detects and logs actions using a pretrained semantic model.
- Logs are cryptographically signed, verified against the official dictionary, and marked as `registered` or `non_registered`.

### Layer 2: Universal integration

- Developers can integrate the SDK into any AI system, regardless of the framework or stack used.
- The SDK provides a universal API for analyzing any relevant output from the AI system.

## Plug-and-play integration

### 1. Integración automática con FastAPI

```python
from aiia_sdk import AIIA
from aiia_sdk.middleware_fastapi import AIIAMiddleware
from fastapi import FastAPI

aiia = AIIA(api_key="...", client_secret="...", ia_id="...")
app = FastAPI()
app.add_middleware(AIIAMiddleware, aiia_instance=aiia)
```
Con esto, **todas las respuestas de tu API serán analizadas automáticamente** y registradas en AIIA sin modificar tus endpoints.

### 2. Integración automática con Flask

```python
from aiia_sdk import AIIA
from aiia_sdk.middleware_flask import AIIAMiddleware
from flask import Flask

aiia = AIIA(api_key="...", client_secret="...", ia_id="...")
app = Flask(__name__)
AIIAMiddleware(app, aiia)
```
Esto intercepta todas las respuestas y las analiza automáticamente.

### 3. Integración automática con Django

```python
from aiia_sdk import AIIA
aiia = AIIA(api_key="...", client_secret="...", ia_id="...")

# En tu settings.py añade:
MIDDLEWARE = [
    ...
    'aiia_sdk.middleware_django.AIIAMiddleware',
    ...
]

# En tu AppConfig o arranque, asegúrate de pasar la instancia de AIIA:
from aiia_sdk.middleware_django import AIIAMiddleware
AIIAMiddleware.aiia = aiia  # (alternativamente, puedes modificar el middleware para soportar inyección directa)
```
Esto intercepta todas las respuestas HTTP y las analiza automáticamente.

### 4. Integración universal para cualquier stack

Si tu IA no usa ninguno de los frameworks anteriores, puedes analizar cualquier salida relevante de la IA con:

```python
from aiia_sdk import AIIA
aiia = AIIA(api_key="...", client_secret="...", ia_id="...")

output = "texto de salida de tu IA o respuesta de API"
aiia.analyze_output(output)
```

Esto funciona en cualquier framework, script o entorno.

## 🔒 Seguridad y buenas prácticas

- **Nunca compartas tu API Key ni tu Client Secret.**
- El SDK nunca imprime ni almacena secretos.
- Si pierdes tu Client Secret, regenera uno desde el dashboard (el anterior deja de funcionar).
- No subas tu archivo `.env` a repositorios públicos.

## Installation

Install the SDK and its dependencies using pip:

```bash
pip install aiia-sdk
```

If you are developing locally, you may also want to install:
```bash
pip install python-dotenv sentence-transformers cryptography tldextract
```

## Credentials management (.env recommended)

For maximum security, store your credentials in a `.env` file at the root of your project:

```env
AIIA_API_KEY=your_api_key_here
AIIA_CLIENT_SECRET=your_client_secret_here
AIIA_IA_ID=your_ia_id_here
```

**Never commit your `.env` file to version control.**

The SDK will automatically load these variables when you initialize the `AIIA` class. This keeps your secrets out of the codebase and version control.

You can also override these values by passing them directly as arguments when creating the `AIIA` instance, but using a `.env` file is the recommended and most secure approach.

## Security Best Practices

- **Never store your API key or client secret in your database in plain text.**
- The secret should only be visible once in the dashboard at creation or when regenerated. If lost, regenerate it (the IA ID remains the same, but the secret changes).
- Store only a hash or encrypted version of the secret in your backend, if required for validation.
- The SDK will never log, print, or store the secret value.
- Always add your credentials to a `.env` file or as environment variables, never commit them to version control.
- If you lose your secret, you must regenerate it from the dashboard.

> **Warning:**
> When you create or regenerate your API key or client secret in the dashboard, you will only see it ONCE. Copy and store it securely. If you lose it, you must regenerate it.

## Error handling and troubleshooting

- The SDK will print clear error messages to the console if there are issues loading the model, credentials, or making API requests.
- If credentials are missing, you will see an error about missing environment variables.
- If the semantic model cannot be loaded (e.g., missing `sentence-transformers`), you will see a warning and semantic detection will be disabled.
- If the API endpoint is unreachable or returns an error, the SDK will print a message but your app will not crash.
- All logs and error messages are in English for universal developer support.

**Tip:** For production, you may want to redirect or capture these logs to your own logging system.

## Security best practices

- **Never share your API key, client secret, or IA ID in public code, documentation, or screenshots.**
- Do not include `.env` or any credentials in your version control or public repositories.
- Only authorized personnel should have access to the credentials.

## What not to share

- Do not share your `.env` file, API keys, client secrets, or IA IDs with anyone outside your organization.
- Do not post logs or error messages that contain sensitive payloads or credentials.
- The README and SDK do not expose or log any secret values by default.

## Uninstallation

To remove the SDK:
```bash
pip uninstall aiia-sdk
```

## Compatibilidad

- FastAPI: integración automática plug-and-play (middleware incluido)
- Flask: integración automática plug-and-play (middleware incluido)
- Django: integración automática plug-and-play (middleware incluido)
- Otros frameworks (scripts, etc.): integración universal llamando a `analyze_output`

## ¿Qué hace este SDK?

- Detecta y registra automáticamente las acciones de la IA a partir de las respuestas API o cualquier texto de salida relevante.
- No requiere modificar endpoints ni lógica de negocio.
- Cumple con requisitos de privacidad y seguridad.

## Ejemplo completo FastAPI

```python
from aiia_sdk import AIIA
from aiia_sdk.middleware_fastapi import AIIAMiddleware
from fastapi import FastAPI

aiia = AIIA(api_key="...", client_secret="...", ia_id="...")
app = FastAPI()
app.add_middleware(AIIAMiddleware, aiia_instance=aiia)

@app.get("/demo")
def demo():
    return {"result": "La IA ha enviado un email"}
```

## Ejemplo completo Flask

```python
from aiia_sdk import AIIA
from aiia_sdk.middleware_flask import AIIAMiddleware
from flask import Flask

aiia = AIIA(api_key="...", client_secret="...", ia_id="...")
app = Flask(__name__)
AIIAMiddleware(app, aiia)

@app.route("/demo")
def demo():
    return "La IA ha enviado un email"
```

## Ejemplo completo Django

```python
# settings.py
MIDDLEWARE = [
    ...
    'aiia_sdk.middleware_django.AIIAMiddleware',
    ...
]

# apps.py o arranque
from aiia_sdk import AIIA
from aiia_sdk.middleware_django import AIIAMiddleware
aiia = AIIA(api_key="...", client_secret="...", ia_id="...")
AIIAMiddleware.aiia = aiia  # (alternativamente, puedes modificar el middleware para soportar inyección directa)
```

## Ejemplo universal

```python
from aiia_sdk import AIIA
aiia = AIIA(api_key="...", client_secret="...", ia_id="...")

output = "La IA ha accedido a un documento confidencial"
aiia.analyze_output(output)
```

## Seguridad y privacidad

- Los logs se firman y cifran automáticamente.
- No se requiere modificar el código fuente de la IA ni de la API.

## Developer Responsibility and Certification

By installing the AIIA SDK, developers agree to act responsibly in the registration of their AI's actions.

- Every action performed by the AI must be registered using the `analyze_output` method.
- If a specific action is not available in the official dictionary (`aiia_actions_v1.0.json`), developers must contact javier.sanchez@aiiatrace.com to request its inclusion.
- The `non_registered` column exists as a transparency mechanism so that companies can monitor undeclared activity.
- If a developer accumulates more than 10 logs marked as `non_registered`, a notification will be sent requiring them to review and properly register those actions.
- If the developer does not update their configuration within 1 month, the IA will receive an internal warning tag and may appear as "non-compliant" on the AIIA Trust Portal.
- The semantic detection model included in the SDK may occasionally result in imprecise matches. AIIA reserves the right to improve this model dynamically based on evolving trends in AI system development. Therefore, some actions may not be accurately traced. It remains the developer's responsibility to use the `analyze_output` method to ensure every action is properly logged. If a particular action does not yet exist in the official dictionary, this will not result in warnings provided the developer notifies AIIA via email at javier.sanchez@aiiatrace.com.

### AIIA Trust Portal

Within the AIIA portal, companies will be able to:

- View all AIs that have downloaded and installed the AIIA certificate
- Verify the transparency level of each AI (clean / warning)
- See how many warnings are registered for each implementation
- Make informed decisions about integrating external AI systems

This structure ensures that both developers and companies uphold the standards of safe, auditable AI.

## License

This SDK is released under the MIT License. See `LICENSE` for more information.

## ⚠️ Advertencias y limitaciones
- El SDK **no genera warnings** ni advertencias automáticas en el dashboard.
- El dashboard solo muestra logs y acciones registradas.
- Si necesitas soporte para nuevas acciones, contacta a javier.sanchez@aiiatrace.com.

## 🧑‍💻 Buenas prácticas para desarrolladores
- Usa siempre el decorador o la integración automática para registrar acciones.
- Si tu IA realiza acciones no contempladas, notifícalo para su inclusión.
- Revisa periódicamente tus logs desde el dashboard.

## ✅ Certificación y transparencia
- Las IAs que usen el SDK y registren correctamente sus acciones pueden obtener el certificado AIIA.
- El estado de cumplimiento es visible en el Trust Portal para empresas.

## 📞 Soporte
- Email: javier.sanchez@aiiatrace.com
- Documentación actualizada: [https://aiiatrace.com/docs](https://aiiatrace.com/docs)

## 📝 Licencia
MIT License. Consulta el archivo LICENSE para más información.