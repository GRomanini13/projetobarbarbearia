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
    
    # Horários opcionais
    inicio_expediente = Column(Time, nullable=True)
    fim_expediente = Column(Time, nullable=True)
    inicio_almoco = Column(Time, nullable=True)
    fim_almoco = Column(Time, nullable=True)

    agendamentos_como_cliente = relationship(
        "Agendamento",
        back_populates="cliente",
        foreign_keys="[Agendamento.cliente_id]"
    )

    agendamentos_como_barbeiro = relationship(
        "Agendamento",
        back_populates="barbeiro",
        foreign_keys="[Agendamento.barbeiro_id]"
    )
