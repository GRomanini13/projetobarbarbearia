from pydantic import BaseModel

class StatusAgendamentoBase(BaseModel):
    nome: str
    descricao: str | None = None
    cor_hex: str | None = None
    ativo: bool = True

class StatusAgendamentoResponse(StatusAgendamentoBase):
    id: int

    class Config:
        from_attributes = True
