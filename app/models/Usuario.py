from sqlalchemy import Column, Integer, String, Boolean, Time
from sqlalchemy.orm import relationship
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    idusuario = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    is_barbeiro = Column(Boolean, default=False)
    
    # Horários de expediente
    inicio_expediente = Column(Time, default="09:00")
    fim_expediente = Column(Time, default="18:00")
    inicio_almoco = Column(Time, default="12:00")
    fim_almoco = Column(Time, default="13:00")
    
    # Relacionamento com agendamentos como CLIENTE (corrigido)
    agendamentos_como_cliente = relationship(
        "Agendamento",
        back_populates="cliente",
        foreign_keys="[Agendamento.cliente_id]"
    )
    
    # Relacionamento com agendamentos como BARBEIRO (corrigido)
    agendamentos_como_barbeiro = relationship(
        "Agendamento",
        back_populates="barbeiro",
        foreign_keys="[Agendamento.barbeiro_id]"
    )