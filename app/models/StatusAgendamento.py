from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base 
class StatusAgendamento(Base):
    __tablename__ = "status_agendamento"

    idstatus_agendamento = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(200), nullable=True)
    ativo = Column(Boolean, default=True)


