from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.models.Usuario import Usuario
from app.schemas.UsuarioSchema import UsuarioCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# LISTAR TODOS OS USUÁRIOS
def listar_usuarios(db: Session):
    return db.query(Usuario).all()


# OBTER USUÁRIO POR ID
def obter_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.idusuario == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return usuario


# CRIAR USUÁRIO (REGRA PRINCIPAL)
def criar_usuario(db: Session, usuario: UsuarioCreate):

    # EMAIL duplicado
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado."
        )

    # TELEFONE duplicado
    if db.query(Usuario).filter(Usuario.telefone == usuario.telefone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telefone já cadastrado."
        )

    # BARBEIRO → horários obrigatórios
    if usuario.is_barbeiro:

        if not usuario.inicio_expediente or not usuario.fim_expediente:
            raise HTTPException(
                status_code=400,
                detail="Barbeiro deve preencher início e fim de expediente."
            )

        if not usuario.inicio_almoco or not usuario.fim_almoco:
            raise HTTPException(
                status_code=400,
                detail="Barbeiro deve preencher horário de almoço."
            )

    # CLIENTE → limpar horários
    else:
        usuario.inicio_expediente = None
        usuario.fim_expediente = None
        usuario.inicio_almoco = None
        usuario.fim_almoco = None

    # HASH DA SENHA
    senha_hash = pwd_context.hash(usuario.senha)

    novo_usuario = Usuario(
        nome=usuario.nome,
        telefone=usuario.telefone,
        email=usuario.email,
        senha=senha_hash,
        is_barbeiro=usuario.is_barbeiro,
        inicio_expediente=usuario.inicio_expediente,
        fim_expediente=usuario.fim_expediente,
        inicio_almoco=usuario.inicio_almoco,
        fim_almoco=usuario.fim_almoco
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


# DELETAR USUÁRIO
def deletar_usuario(db: Session, usuario_id: int):
    usuario = db.query(Usuario).filter(Usuario.idusuario == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    db.delete(usuario)
    db.commit()

    return {"msg": "Usuário deletado com sucesso"}


# RESETAR SENHA PELO EMAIL
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


# RESETAR EMAIL PELO TELEFONE
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

    return {"msg": "Email atualizado com sucesso."}



# LOGIN / AUTENTICAR
def autenticar_usuario(db: Session, email: str, senha: str):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado."
        )

    if not pwd_context.verify(senha, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta."
        )

    return usuario
