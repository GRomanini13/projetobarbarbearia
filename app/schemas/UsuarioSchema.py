# app/schemas/UsuarioSchema.py
from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    nome: str
    telefone: str
    email: str
    senha: str
    is_barbeiro: bool

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    is_barbeiro: bool

    class Config:
        from_attributes = True

class UsuarioResetSenha(BaseModel):
    email: EmailStr
    nova_senha: str

class UsuarioResetEmail(BaseModel):
    telefone: str
    novo_email: EmailStr