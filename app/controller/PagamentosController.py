from fastapi import APIRouter, HTTPException, Request, Depends, Query
from sqlalchemy.orm import Session
# Assumindo a importação correta dos seus módulos
from app.services.MercadoPagoService import criar_preferencia
from app.schemas.PagamentosSchemas import PreferenciaRequest
from app.core.database import get_db 

router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"]
)

@router.post("/criar_preferencia")
async def criar_preferencia_route(
    request_data: PreferenciaRequest, 
    request: Request,
    db: Session = Depends(get_db)
):
    # O objeto mp_sdk foi anexado ao estado da aplicação em main.py
    mp_sdk = request.app.state.mp_sdk
    
    # IMPORTANTE: Garanta que na função criar_preferencia (no MercadoPagoService.py) 
    # você inclua os atributos 'back_urls' e 'auto_return' no payload da preferência, 
    # apontando para os endpoints abaixo (/success, /failure, /pending).
    
    pref = criar_preferencia(
        mp_sdk=mp_sdk,
        item=request_data.item,
        agendamento_id=request_data.agendamento_id,
        db=db
    ) 
    
    if "error" in pref:
        # Se houver erro, retorna o status 400 com a mensagem detalhada do MP
        raise HTTPException(status_code=400, detail=pref["error"])

    # Retorna o ID e o link de inicialização (init_point)
    return {
        "id": pref.get("id"),
        "init_point": pref.get("init_point"),
        "sandbox_init_point": pref.get("sandbox_init_point"),
    }

# --- Rotas de Retorno (Back URLs) Ajustadas para receber parâmetros do MP ---

@router.get("/success")
def pagamento_sucesso(
    # Captura os parâmetros enviados pelo Mercado Pago na URL via GET
    payment_id: str = Query(..., alias="payment_id"),
    status: str = Query(..., alias="status"),
    external_reference: str = Query(..., alias="external_reference"),
    merchant_order_id: str = Query(None, alias="merchant_order_id") # Opcional
):
    # Lógica aqui para:
    # 1. Buscar o pedido no seu DB usando `external_reference` (ID do seu agendamento)
    # 2. Atualizar o status do pedido para 'Aprovado' no seu sistema
    
    print(f" Pagamento APROVADO! ID MP: {payment_id}, Status: {status}, Ref Externa: {external_reference}")
    
    return {
        "message": "Pagamento aprovado! Seu pedido será processado.",
        "detalhes_mp": {
            "payment_id": payment_id,
            "status": status,
            "referencia": external_reference
        }
    }

@router.get("/failure")
def pagamento_falha(
    payment_id: str = Query(..., alias="payment_id"),
    status: str = Query(..., alias="status"),
    external_reference: str = Query(..., alias="external_reference"),
    merchant_order_id: str = Query(None, alias="merchant_order_id")
):
    # Lógica aqui para:
    # 1. Buscar o pedido no seu DB usando `external_reference`
    # 2. Atualizar o status do pedido para 'Rejeitado/Falha'
    
    print(f" Pagamento RECUSADO! ID MP: {payment_id}, Status: {status}, Ref Externa: {external_reference}")
    
    return {
        "message": "Pagamento recusado. Tente novamente ou use outro método.",
        "detalhes_mp": {
            "payment_id": payment_id,
            "status": status,
            "referencia": external_reference
        }
    }

@router.get("/pending")
def pagamento_pendente(
    payment_id: str = Query(..., alias="payment_id"),
    status: str = Query(..., alias="status"),
    external_reference: str = Query(..., alias="external_reference"),
    merchant_order_id: str = Query(None, alias="merchant_order_id")
):
    # Lógica aqui para:
    # 1. Buscar o pedido no seu DB usando `external_reference`
    # 2. Atualizar o status do pedido para 'Pendente'
    # 3. Mostrar instruções de pagamento (ex: boleto ou código Pix) para o cliente.
    
    print(f" Pagamento PENDENTE! ID MP: {payment_id}, Status: {status}, Ref Externa: {external_reference}")
    
    return {
        "message": "Seu pagamento está pendente. Por favor, siga as instruções para finalizá-lo.",
        "detalhes_mp": {
            "payment_id": payment_id,
            "status": status,
            "referencia": external_reference
        }
    }