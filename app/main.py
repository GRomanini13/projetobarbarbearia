from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import mercadopago
import os

from app.core.database import Base, engine
import app.models  # registra os models

# Controllers / Routes
from app.controller.UsuarioController import router as usuario_router
from app.controller.ServicoController import router as servico_router
from app.controller.AgendamentoController import router as agendamento_router
from app.controller.PagamentosController import router as pagamentos_router
from app.routes.MercadoPagoRoutes import router as mp_router
from app.controller.WebhookController import router as webhook_router

# Middleware
from app.middleware.disable_signature_for_webhook import SignatureMiddleware


# APP
app = FastAPI(title="API Barbearia")


# MERCADO PAGO CONFIG
load_dotenv()
mp_access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

if not mp_access_token:
    print("ERRO: MERCADOPAGO_ACCESS_TOKEN não encontrado nas variáveis de ambiente!")

sdk = mercadopago.SDK(mp_access_token)
app.state.mp_sdk = sdk  # torna disponível para rotas


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajustar na produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Signature Middleware (Webhook)
app.add_middleware(SignatureMiddleware)


# Debug Middleware
@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    # print(f">>> DEBUG: {request.method} {request.url.path}") # Pode comentar se poluir muito
    response = await call_next(request)
    return response


# Banco de Dados
print("Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)

print("Tabelas criadas (ou já existentes):")
for table in Base.metadata.tables.keys():
    print(f" - {table}")


# Rotas
app.include_router(usuario_router)
app.include_router(servico_router)
app.include_router(agendamento_router)
app.include_router(pagamentos_router) # A rota de status correta está AQUI dentro agora
app.include_router(mp_router)
app.include_router(webhook_router)


# Rota raiz
@app.get("/")
def read_root():
    return {"msg": "API da Barbearia rodando"}