from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from app.core.database import get_db
from app.services.AgendaBarbeiroService import gerar_horarios_disponiveis
from app.models.Servico import Servico
from app.models.Usuario import Usuario

router = APIRouter(
    prefix="/agenda",
    tags=["AgendaBarbeiro"]
)

@router.get("/disponibilidade/{barbeiro_id}", response_model=List[str])
def disponibilidade_barbeiro(
    barbeiro_id: int,
    data: date = Query(..., description="Data do agendamento YYYY-MM-DD"),
    servico_id: int = Query(..., description="ID do serviço"),
    db: Session = Depends(get_db)
):
    # Verifica se o barbeiro existe
    barbeiro = db.query(Usuario).filter(Usuario.idusuario == barbeiro_id).first()
    if not barbeiro:
        raise HTTPException(status_code=404, detail="Barbeiro não encontrado")
    
    # Verifica se o serviço existe
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    # Gera horários disponíveis
    try:
        horarios = gerar_horarios_disponiveis(
            db=db,
            barbeiro_id=barbeiro_id,
            data=data,
            duracao_minutos=servico.duracao
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return horarios
