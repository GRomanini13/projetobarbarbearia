from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 🔹 URL de conexão com o banco Neon (PostgreSQL)
DATABASE_URL = (
    "postgresql+psycopg2://neondb_owner:npg_qR24dDyMvEeT@"
    "ep-super-bread-a4vjvdo3-pooler.us-east-1.aws.neon.tech/sis_barber"
    "?sslmode=require"
)

# 🔹 Cria o engine para conectar ao banco
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # evita desconexões automáticas
)

# 🔹 Configuração da sessão
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 🔹 Base para os models herdarem
Base = declarative_base()

# 🔹 Dependência para injeção no FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
