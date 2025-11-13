from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from app.schemas.UsuarioSchema import UsuarioCreate, UsuarioResetEmail, UsuarioResetSenha, UsuarioResponse
from app.services.UsuarioService import autenticar_usuario, criar_usuario, listar_usuarios, obter_usuario, deletar_usuario, resetar_email_por_telefone, resetar_senha_por_email
from app.core.database import get_db


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)

# GET todos os usuários
@router.get("/", response_model=list[UsuarioResponse])
def get_usuarios(db: Session = Depends(get_db)):
    return listar_usuarios(db)

# GET usuário por ID
@router.get("/{usuario_id}", response_model=UsuarioResponse)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = obter_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

# POST criar usuário
@router.post("/", response_model=UsuarioResponse)
def post_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return criar_usuario(db, usuario)

# DELETE usuário
@router.delete("/{usuario_id}")
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return deletar_usuario(db, usuario_id)

#Alterar senha passando de parâmetro o email
@router.put("/reset-senha")
def reset_senha(dados: UsuarioResetSenha, db: Session = Depends(get_db)):
    return resetar_senha_por_email(db, dados.email, dados.nova_senha)

#Alterar email passando de parâmetro o telefone
@router.put("/reset-email")
def reset_email(dados: UsuarioResetEmail, db: Session = Depends(get_db)):
    return resetar_email_por_telefone(db, dados.telefone, dados.novo_email)


@router.post("/login", response_model=UsuarioResponse)
def login(
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = autenticar_usuario(db, email, senha)
    return usuario