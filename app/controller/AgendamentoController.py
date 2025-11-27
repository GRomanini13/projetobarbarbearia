from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.AgendamentoSchema import AgendamentoCreate, AgendamentoResponse
from app.services.AgendamentoService import criar_agendamento, criar_preferencia_mp
from app.core.database import get_db

router = APIRouter(
    prefix="/agendamento",
    tags=["Agendamentos"]
)


@router.post("/", response_model=AgendamentoResponse)
def post_agendamento(
    agendamento: AgendamentoCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um agendamento e retorna a preferência de pagamento do Mercado Pago.
    """
    try:
        novo_agendamento = criar_agendamento(db, agendamento)
    except Exception as e:
        raise HTTPException(500, "Erro ao criar agendamento")
    
    try:
        preference_id = criar_preferencia_mp(novo_agendamento, agendamento.valor_servico)
    except Exception as e:
        raise HTTPException(500, "Erro ao criar pagamento no Mercado Pago")
    
    return {
        **novo_agendamento.__dict__,
        "preferenceId": preference_id
    }
