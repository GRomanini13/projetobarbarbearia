from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Agenda(Base):
    __tablename__ = "agenda"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)

    # Relacionamento com Agendamento
    agendamentos = relationship(
        "Agendamento",
        back_populates="agenda"
    )
