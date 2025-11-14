from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    barbeiro_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    agenda_id = Column(Integer, ForeignKey("agenda.id"), nullable=False)
    servico_id = Column(Integer, ForeignKey("servicos.id"), nullable=False)  # <--- FK adicionada
    data_hora = Column(DateTime, nullable=False)

    usuario = relationship(
        "Usuario",
        back_populates="agendamentos",
        foreign_keys=[usuario_id]
    )

    barbeiro = relationship(
        "Usuario",
        back_populates="agendamentos_como_barbeiro",
        foreign_keys=[barbeiro_id]
    )

    agenda = relationship(
        "Agenda",
        back_populates="agendamentos"
    )

    servico = relationship(
        "Servico",
        back_populates="agendamentos"
    )
