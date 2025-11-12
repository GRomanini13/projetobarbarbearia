from fastapi import FastAPI
from app.core.database import Base, engine
import app.models  # importa todos os models para registrar as tabelas

# ✅ Cria as tabelas e mostra no console
print("🔄 Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas (ou já existentes):")
for table in Base.metadata.tables.keys():
    print(f" - {table}")

# ✅ Importa os routers
from app.controller.UsuarioController import router as usuario_router

# Inicializa o FastAPI
app = FastAPI(title="API Barbearia")

# Inclui as rotas
app.include_router(usuario_router)

@app.get("/")
def read_root():
    return {"msg": "API da Barbearia rodando 🚀"}
