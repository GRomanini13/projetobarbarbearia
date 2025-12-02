from fastapi import APIRouter, Request, HTTPException
from app.services.WebhookService import processar_notificacao_mp # Importa a função de Service

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"]
)

@router.post("/mp")
async def receber_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Corpo da requisição inválido ou ausente.")

    print(f"--- WEBHOOK RECEBIDO: {data}")

    topic = data.get("topic")
    resource_url = data.get("resource")
    
    if not topic or not resource_url:
        print("Aviso: Notificação ignorada (sem topic/resource).")
        return {"status": "ok", "message": "Ignorado"}

    mp_sdk = request.app.state.mp_sdk

    try:
        # Passa também o payload completo 'data' para processar_payment_id corretamente
        processar_notificacao_mp(mp_sdk, topic, resource_url, data)
        return {"status": "ok"}
    
    except Exception as e:
        print(f"ERRO CRÍTICO ao processar webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    

@router.get("/mp")
async def testar():
    return {"status": "ok - GET funcionando"}