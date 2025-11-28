from fastapi import APIRouter, HTTPException, Request, Depends, Query
from sqlalchemy.orm import Session

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

    try:
        # ❗️ NÃO PASSAR mp_sdk – seu service não usa isso
        pref = criar_preferencia(
            item=request_data.item,
            quantity=request_data.quantity,
            unit_price=request_data.unit_price
        )

        if "error" in pref:
            raise HTTPException(status_code=400, detail=pref["error"])

        return {
            "id": pref.get("id"),
            "init_point": pref.get("init_point"),
            "sandbox_init_point": pref.get("sandbox_init_point"),
        }

    except Exception as e:
        print(f"Erro no Controller: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------
# ROTAS BACK_URLS
# ------------------------

@router.get("/success")
def pagamento_sucesso(
    payment_id: str = Query(...),
    status: str = Query(...),
    external_reference: str = Query(...),
    merchant_order_id: str = Query(None)
):
    print(f"Pagamento APROVADO -> payment_id={payment_id}, referencia={external_reference}")
    return {"status": "approved"}


@router.get("/failure")
def pagamento_falha(
    payment_id: str = Query(...),
    status: str = Query(...),
    external_reference: str = Query(...),
    merchant_order_id: str = Query(None)
):
    print(f"Pagamento FALHOU -> {payment_id}")
    return {"status": "failure"}


@router.get("/pending")
def pagamento_pendente(
    payment_id: str = Query(...),
    status: str = Query(...),
    external_reference: str = Query(...),
    merchant_order_id: str = Query(None)
):
    print(f"Pagamento PENDENTE -> {payment_id}")
    return {"status": "pending"}
