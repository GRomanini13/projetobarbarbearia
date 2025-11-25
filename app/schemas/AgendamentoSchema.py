from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class AgendamentoCreate(BaseModel):
    cliente_id: int
    barbeiro_id: int
    servico_id: int
    data: date
    hora_inicio: time
    hora_fim: time
    observacao: Optional[str] = None

class AgendamentoResponse(AgendamentoCreate):
    idagendamento: int
    status_id: int

    class Config:
        from_attributes = True
