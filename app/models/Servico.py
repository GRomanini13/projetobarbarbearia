from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Servico(Base):
    __tablename__ = "servicos"

    idservicos = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    duracao = Column(Integer, nullable=False)  # duração em minutos
    preco = Column(Integer, nullable=False)

    # Relacionamento com Agendamento
    agendamentos = relationship(
        "Agendamento",
        back_populates="servico"
    )
