from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic import BaseModel, constr

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    is_barbeiro = Column(Boolean, default=False)

    # relacionamento com agendamentos como cliente
    agendamentos = relationship(
        "Agendamento",
        back_populates="usuario",
        foreign_keys="Agendamento.usuario_id"
    )

    # relacionamento com agendamentos como barbeiro
    agendamentos_como_barbeiro = relationship(
        "Agendamento",
        back_populates="barbeiro",
        foreign_keys="Agendamento.barbeiro_id"
    )
