from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, date, time


class AgendamentoCreate(BaseModel):
    cliente_id: int
    barbeiro_id: int
    servico_id: int
    data: date
    hora_inicio: time
    hora_fim: time
    observacao: Optional[str] = None

    # REMOVE timezone automaticamente (caso venha com "Z" no JSON)
    @field_validator("hora_inicio", "hora_fim", mode="before")
    def remover_timezone(cls, v):
        if hasattr(v, "tzinfo") and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class AgendamentoResponse(BaseModel):
    idagendamento: int
    cliente_id: int
    barbeiro_id: int
    servico_id: int
    data_hora_inicio: datetime
    data_hora_fim: datetime
    observacao: Optional[str] = None
    status_id: int
    preco: float

    class Config:
        from_attributes = True


class HorarioDisponivel(BaseModel):
    hora_inicio: time
    hora_fim: time


class DisponibilidadeResponse(BaseModel):
    barbeiro_id: int
    barbeiro_nome: str
    servico_id: int
    servico_nome: str
    duracao_minutos: int
    data: date
    horarios_disponiveis: List[HorarioDisponivel]
