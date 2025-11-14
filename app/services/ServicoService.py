from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.Servico import Servico

# Listar todos os serviços
def listar_servicos(db: Session):
    return db.query(Servico).all()

# Regra de negócio para obter o serviço por ID 
def obter_servico(db: Session, servico_id: int):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()

    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )

    return servico

# Regra de negócio para criar o serviço
def criar_servico(db: Session, nome: str, duracao_min: str, preco: float):
    novo_servico = Servico(
        nome=nome,
        duracao=duracao_min,
        preco=preco
    )

    db.add(novo_servico)
    db.commit()
    db.refresh(novo_servico)

    return novo_servico

# Regra de negócio para deletar o serviço
def deletar_servico(db: Session, servico_id: int):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()

    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )

    db.delete(servico)
    db.commit()
    return {"detail": "Serviço deletado com sucesso"}

# Regra de negócio para atualizar o serviço
def atualizar_servico(db: Session, servico_id: int, nome: str, duracao: str, preco: float):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()

    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )

    servico.nome = nome
    servico.duracao = duracao
    servico.preco = preco

    db.commit()
    db.refresh(servico)
    return servico

