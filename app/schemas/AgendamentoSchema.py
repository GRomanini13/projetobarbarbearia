from pydantic import BaseModel

class AgendamentoBase(BaseModel):
    usuario_id: int
    barbeiro_id: int
    servico_id: int
    agenda_id: int

class AgendamentoCreate(AgendamentoBase):
    pass

class AgendamentoResponse(AgendamentoBase):
    id: int

    class Config:
        orm_mode = True
