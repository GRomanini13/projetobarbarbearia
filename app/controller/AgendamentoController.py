from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from app.schemas.AgendamentoSchema import AgendamentoCreate, AgendamentoResponse, DisponibilidadeResponse
from app.services.AgendamentoService import criar_agendamento, obter_horarios_disponiveis
from app.core.database import get_db

router = APIRouter(
    prefix="/agendamento",
    tags=["Agendamentos"]
)

@router.post("/agendamento/", response_model=AgendamentoResponse)
def post_agendamento(
    agendamento: AgendamentoCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo agendamento.
    """
    return criar_agendamento(db, agendamento)

@router.get("/agendamento/disponibilidade/", response_model=DisponibilidadeResponse)
def get_horarios_disponiveis(
    barbeiro_id: int = Query(..., description="ID do barbeiro"),
    servico_id: int = Query(..., description="ID do serviço"),
    data: date = Query(..., description="Data desejada (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Retorna todos os horários disponíveis para um barbeiro e serviço em uma data específica.
    
    Considera:
    - Horário de expediente do barbeiro
    - Horário de almoço
    - Agendamentos já existentes
    - Duração do serviço
    
    Exemplo de uso:
    GET /agendamento/disponibilidade/?barbeiro_id=6&servico_id=8&data=2025-11-26
    """
    return obter_horarios_disponiveis(db, barbeiro_id, servico_id, data)
