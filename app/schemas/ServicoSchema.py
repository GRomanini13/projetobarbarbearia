from pydantic import BaseModel

class ServicoBase(BaseModel):
    nome: str
    preco: float
    duracao_min: int


class ServicoCreate(ServicoBase):
    nome: str
    preco: float 
    duracao_min: int 
    
class ServicoResponse(ServicoBase):
    idservicos: int

    class Config:
        orm_mode = True
