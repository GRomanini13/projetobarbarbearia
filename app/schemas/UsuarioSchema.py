# app/schemas/UsuarioSchema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import time


class UsuarioCreate(BaseModel):
    nome: str
    telefone: str
    email: str
    senha: str
    is_barbeiro: bool
    inicio_expediente: Optional[time] = None
    fim_expediente: Optional[time] = None
    inicio_almoco: Optional[time] = None
    fim_almoco: Optional[time] = None


class UsuarioResponse(BaseModel):
    id: int = Field(..., alias="idusuario")
    nome: str
    telefone: str
    email: str
    is_barbeiro: bool

    # Aqui é Pydantic → então só tipos Python
    inicio_expediente: Optional[time] = None
    fim_expediente: Optional[time] = None
    inicio_almoco: Optional[time] = None
    fim_almoco: Optional[time] = None

    model_config = {
        "from_attributes": True
    }


class UsuarioResetSenha(BaseModel):
    email: EmailStr
    nova_senha: str


class UsuarioResetEmail(BaseModel):
    telefone: str
    novo_email: EmailStr
