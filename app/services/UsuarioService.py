from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.models.Usuario import Usuario  
from app.schemas.UsuarioSchema import UsuarioCreate, UsuarioResponse
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def listar_usuarios(db: Session):
    return db.query(Usuario).all()

from fastapi import HTTPException, status

#usuario ID
def obter_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    # mostrar senha antes de truncar
    print("Senha original:", usuario.senha)
    senha_truncada = usuario.senha[:72] if usuario.senha else None

    return usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Regra de negócio para criar o usuário
def criar_usuario(db: Session, usuario: UsuarioCreate):
    senha_bytes = usuario.senha.encode('utf-8')

    print("Senha original bytes:", senha_bytes)
    print("Tamanho em bytes:", len(senha_bytes))

    if len(senha_bytes) > 72:
        senha_bytes = senha_bytes[:72]

    hashed_password = pwd_context.hash(senha_bytes.decode('utf-8', 'ignore'))

    novo_usuario = Usuario(
        nome=usuario.nome,
        telefone=usuario.telefone, 
        email=usuario.email,
        senha=hashed_password,
        is_barbeiro=usuario.is_barbeiro
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario

# Regra de negócio para deletar o usuário
def deletar_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise Exception("Usuário não encontrado")
    db.delete(usuario)
    db.commit()
    return {"msg": "Usuário deletado com sucesso"}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Regra de negócio para resetar a senha por email
def resetar_senha_por_email(db: Session, email: str, nova_senha: str):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado com este e-mail."
        )

    usuario.senha = pwd_context.hash(nova_senha)
    db.commit()
    db.refresh(usuario)
    return {"msg": "Senha atualizada com sucesso."}

# Regra de negócio para resetar o email por telefone
def resetar_email_por_telefone(db: Session, telefone: str, novo_email: str):
    usuario = db.query(Usuario).filter(Usuario.telefone == telefone).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado com este telefone."
        )

    usuario.email = novo_email
    db.commit()
    db.refresh(usuario)