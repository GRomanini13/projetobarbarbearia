from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.AgendamentoSchema import AgendamentoCreate, AgendamentoResponse
from app.services.AgendamentoService import criar_agendamento

router = APIRouter(
    prefix="/agendamento",
    tags=["Agendamento"]
)

@router.post("/", response_model=AgendamentoResponse)
def post_agendamento(agendamento: AgendamentoCreate, db: Session = Depends(get_db)):
    return criar_agendamento(db, agendamento)
