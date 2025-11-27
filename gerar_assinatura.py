import hmac
import hashlib
import json
import time

WEBHOOK_KEY = "f7f6ee9ca3474b230201de31c1b83dd93f329e04ce2cea13f9b062503ebaef3f"

body = {"test": 123}
body_str = json.dumps(body)
timestamp = int(time.time())

# O Mercado Pago assina: "{timestamp}.{body}"
message = f"{timestamp}.{body_str}".encode()

signature = hmac.new(
    WEBHOOK_KEY.encode(),
    message,
    hashlib.sha256
).hexdigest()

print(f"x-signature: t={timestamp},v1={signature}")
print("Body JSON:", body_str)
