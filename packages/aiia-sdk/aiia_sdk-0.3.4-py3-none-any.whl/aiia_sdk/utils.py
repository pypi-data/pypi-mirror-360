import hmac
import hashlib

def generate_signature(secret, message):
    # Asegurar que secret sea bytes
    if isinstance(secret, str):
        secret_bytes = secret.encode()
    elif isinstance(secret, bytes):
        secret_bytes = secret
    else:
        secret_bytes = str(secret).encode()
    
    # Asegurar que message sea bytes
    if isinstance(message, str):
        message_bytes = message.encode()
    elif isinstance(message, bytes):
        message_bytes = message
    else:
        message_bytes = str(message).encode()
    
    return hmac.new(
        secret_bytes,
        message_bytes,
        hashlib.sha256
    ).hexdigest()