from fastapi import APIRouter, Request, HTTPException
from app.services.WebhookService import processar_notificacao_mp # Importa a função de Service

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"]
)

@router.post("/mp") # URL que deve ser configurada no Mercado Pago (ex: https://seudominio.com/webhooks/mp)
async def receber_webhook(request: Request):
    
    # O Mercado Pago recomenda o formato de JSON com 'topic' e 'resource'
    try:
        data = await request.json()
    except Exception:
        # Em caso de body vazio ou formato inválido
        raise HTTPException(status_code=400, detail="Corpo da requisição inválido ou ausente.")

    print(f"--- WEBHOOK RECEBIDO: {data}")

    topic = data.get("topic")
    resource_url = data.get("resource")
    
    # Verifica se a notificação está no formato esperado (tópico e URL de recurso)
    if not topic or not resource_url:
        print("Aviso: Notificação ignorada (sem topic/resource).")
        return {"status": "ok", "message": "Ignorado"}

    # O objeto mp_sdk foi anexado ao estado da aplicação em main.py
    mp_sdk = request.app.state.mp_sdk

    try:
        # Chama a camada de Service para executar a lógica de negócios e DB
        processar_notificacao_mp(mp_sdk, topic, resource_url)
        
        # O Mercado Pago espera um status 200 OK para confirmar o recebimento
        return {"status": "ok"}
    
    except Exception as e:
        # Se houver qualquer erro na camada de Service (ex: falha no DB), 
        # retornamos 500 para que o Mercado Pago tente reenviar a notificação.
        print(f"ERRO CRÍTICO ao processar webhook: {e}")
        # Aumentar a chance de reenvio
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")