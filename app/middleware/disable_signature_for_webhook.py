from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import hmac
import hashlib
import os

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

def verify_signature(signature_header: str, body: bytes) -> bool:
    # Função provisória só para não travar seu backend
    print("-> verify_signature CHAMADO")
    return True

class SignatureMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Só valida se a rota for /webhook
        if request.url.path == "/webhook":
            raw_body = await request.body()

            signature = request.headers.get("x-signature")
            if not signature:
                print("Sem assinatura. Cancelando.")
                return JSONResponse({"status": "invalid signature"}, status_code=400)

            if not verify_signature(signature, raw_body):
                print("Assinatura inválida")
                return JSONResponse({"status": "invalid signature"}, status_code=400)

            print("Assinatura válida, continuando...")

            # DEVOLVE O BODY PARA A ROTA PODER USAR
            request._body = raw_body

        return await call_next(request)