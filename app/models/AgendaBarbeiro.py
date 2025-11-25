from sqlalchemy import Column, Integer, Date, Time, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base  

class AgendaBarbeiro(Base):
    __tablename__ = "agenda_barbeiro"

    idagenda_barbeiro = Column(Integer, primary_key=True, index=True)
    id_barbeiro = Column(Integer, ForeignKey("usuarios.idusuario"), nullable=False)
    id_cliente = Column(Integer, ForeignKey("usuarios.idusuario"), nullable=False)
    servico_id = Column(Integer, ForeignKey("servicos.idservicos"), nullable=False)
    data = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    status_id = Column(Integer, ForeignKey("status_agendamento.idstatus_agendamento"), nullable=False)
    observacao = Column(Text, nullable=True)

    # RELACIONAMENTOS
    barbeiro = relationship("Usuario", foreign_keys=[id_barbeiro])
    cliente = relationship("Usuario", foreign_keys=[id_cliente])
    servico = relationship("Servico")
    status = relationship("StatusAgendamento")
