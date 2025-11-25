from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Agenda(Base):
    __tablename__ = "agenda"
    
    idagenda = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    