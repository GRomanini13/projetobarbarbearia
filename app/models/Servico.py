from sqlalchemy import Column, Integer, String, Numeric # Importe Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class Servico(Base):
    __tablename__ = "servicos"

    idservicos = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    duracao = Column(Integer, nullable=False)
    
    # MUDANÇA AQUI: De Float para Numeric(10, 2)
    # Isso garante que o Python trate o valor com a mesma precisão do banco
    preco = Column(Numeric(10, 2), nullable=False)

    agendamentos = relationship(
        "Agendamento",
        back_populates="servico"
    )