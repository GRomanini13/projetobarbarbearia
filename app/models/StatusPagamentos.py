from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

# Assumindo que a Base é definida aqui ou importada de core.database
Base = declarative_base() 

class StatusPagamento(Base):
    """Representa a tabela public.status_pagamento no banco de dados."""
    __tablename__ = 'status_pagamento'

    id = Column(Integer, primary_key=True, index=True)
    nome_status = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<StatusPagamento(id={self.id}, nome='{self.nome_status}')>"