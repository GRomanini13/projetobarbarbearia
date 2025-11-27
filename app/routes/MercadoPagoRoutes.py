from fastapi import APIRouter, Request, HTTPException
from app.services.MercadoPagoService import criar_preferencia
from app.processors.webhook_processor import process_payment_event
import os, hmac, hashlib

router = APIRouter()
WEBHOOK_KEY = os.getenv("WEBHOOK_KEY")

@router.get("/criar_preferencia")
def criar_preferencia_route():
    try:
        pref = criar_preferencia("Produto Teste", 1, 10.0)
        return {
            "id": pref.get("id"),
            "init_point": pref.get("init_point"),
            "sandbox_init_point": pref.get("sandbox_init_point")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/success")
def pagamento_sucesso():
    return {"message": "Pagamento aprovado com sucesso!"}

@router.get("/failure")
def pagamento_falha():
    return {"message": "Pagamento recusado!"}

@router.get("/pending")
def pagamento_pendente():
    return {"message": "Pagamento pendente!"}

@router.post("/webhook")
async def mercadopago_webhook(request: Request):
    body = await request.body()
    mp_signature = request.headers.get("x-meli-signature")

    # valida assinatura
    computed_signature = hmac.new(
        key=WEBHOOK_KEY.encode("utf-8"),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()

    if mp_signature != computed_signature:
        return {"status": "invalid signature"}

    event = await request.json()
    
    # processa evento
    process_payment_event(event)
    
    return {"status": "ok"}
