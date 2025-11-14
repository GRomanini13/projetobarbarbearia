from pydantic import BaseModel
from datetime import date, time

class AgendaBase(BaseModel):
    data: date
    horario_inicio: time
    horario_fim: time

class AgendaCreate(AgendaBase):
    pass

class AgendaResponse(AgendaBase):
    id: int

    class Config:
        orm_mode = True
