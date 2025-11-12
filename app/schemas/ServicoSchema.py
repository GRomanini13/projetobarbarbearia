from pydantic import BaseModel

class ServicoBase(BaseModel):
    nome: str
    duracao_min: int
    preco: float

class ServicoCreate(ServicoBase):
    pass

class ServicoResponse(ServicoBase):
    id: int

    class Config:
        orm_mode = True
