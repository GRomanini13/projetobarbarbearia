from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
import app.models
import os # <-- 1. Importação necessária para usar os.getenv()

from app.controller.ServicoController import router as servico_router
from app.controller.AgendamentoController import router as agendamento_router
from app.controller.PagamentosController import router as pagamentos_router
from app.routes.MercadoPagoRoutes import router as mp_router
from app.controller.WebhookController import router as webhook_router
from app.controller.UsuarioController import router as usuario_router

from app.middleware.disable_signature_for_webhook import SignatureMiddleware
import mercadopago
from dotenv import load_dotenv

app = FastAPI(title="API Barbearia")

# --- Configuração do Mercado Pago ---
load_dotenv()  # Carrega variáveis de ambiente do arquivo .env
mp_access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

if not mp_access_token:
    print("ERRO: MERCADOPAGO_ACCESS_TOKEN não encontrado nas variáveis de ambiente.")
    # Aqui você pode optar por levantar uma exceção ou usar um token de teste
    # Mas para produção, isso é crítico.
    
# 2. Inicialização CORRETA: Passando a variável carregada
sdk = mercadopago.SDK(mp_access_token)

# 3. Anexar o SDK ao estado da aplicação para que possa ser injetado nas rotas
app.state.mp_sdk = sdk
# ------------------------------------

#  CORS primeiro (não afeta o webhook)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  SignatureMiddleware (antes de chamar as rotas)
app.add_middleware(SignatureMiddleware)

# Debug (pode ser antes das rotas também)
@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    print(">>> Passou no debug_middleware:", request.url.path)
    return await call_next(request)

#  Banco
print("Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)

#  Rotas
app.include_router(usuario_router)
app.include_router(servico_router)
app.include_router(agendamento_router)
app.include_router(pagamentos_router)
app.include_router(mp_router)
app.include_router(webhook_router)


@app.get("/")
def read_root():
    return {"msg": "API da Barbearia rodando"}