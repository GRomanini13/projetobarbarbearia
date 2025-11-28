from sqlalchemy import Column, Float, Integer, ForeignKey, DateTime, Numeric, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Agendamento(Base):
    __tablename__ = "agendamentos"
    
    idagendamento = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.idusuario"), nullable=False)
    barbeiro_id = Column(Integer, ForeignKey("usuarios.idusuario"), nullable=False)
    servico_id = Column(Integer, ForeignKey("servicos.idservicos"), nullable=False)
    data_hora_inicio = Column(DateTime, nullable=False)
    data_hora_fim = Column(DateTime, nullable=False)
    observacao = Column(String, nullable=True)
    status_id = Column(Integer, default=1)
    preco = Column(Numeric(10,2), nullable=False, default=0)
    
    # Relacionamentos
    cliente = relationship(
        "Usuario", 
        foreign_keys=[cliente_id],
        back_populates="agendamentos_como_cliente"
    )
    
    barbeiro = relationship(
        "Usuario", 
        foreign_keys=[barbeiro_id],
        back_populates="agendamentos_como_barbeiro"
    )
    
    servico = relationship("Servico", foreign_keys=[servico_id])