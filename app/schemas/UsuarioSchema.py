from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import time

class UsuarioCreate(BaseModel):
    nome: str
    telefone: str
    email: EmailStr
    senha: str
    is_barbeiro: bool = False

    # Horários opcionais
    inicio_expediente: Optional[time] = None
    fim_expediente: Optional[time] = None
    inicio_almoco: Optional[time] = None
    fim_almoco: Optional[time] = None


class UsuarioResponse(BaseModel):
    idusuario: int
    nome: str
    telefone: str
    email: str
    is_barbeiro: bool
    inicio_expediente: Optional[time]
    fim_expediente: Optional[time]
    inicio_almoco: Optional[time]
    fim_almoco: Optional[time]

    class Config:
        orm_mode = True


class UsuarioResetSenha(BaseModel):
    email: EmailStr
    nova_senha: str


class UsuarioResetEmail(BaseModel):
    telefone: str
    novo_email: EmailStr
