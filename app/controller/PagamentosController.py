from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import traceback, json, os
from app.services.MercadoPagoService import criar_preferencia, consultar_pagamento
from app.schemas.PagamentosSchemas import PreferenciaRequest
from app.core.database import get_db

# Tenta importar o modelo, evita quebrar se o caminho estiver diferente
try:
    from app.models.Agendamento import Agendamento
except ImportError:
    print("ERRO CRÍTICO: Model 'Agendamento' não encontrado. Verifique o caminho.")

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])


# =================================================================
#  ROTA 1: CRIAR PREFERÊNCIA (Checkout)
# =================================================================
@router.post("/criar_preferencia")
async def criar_preferencia_route(request_data: PreferenciaRequest, db: Session = Depends(get_db)):
    print(f"\n--- INICIANDO CRIAÇÃO DE PAGAMENTO ---")
    print(f"Agendamento ID: {request_data.agendamento_id}")

    # Verifica a URL base (Ngrok) para o Webhook e Retorno
    base_url_ngrok = os.getenv("BASE_URL")
    if not base_url_ngrok or "localhost" in base_url_ngrok:
        print(f"[ERRO] BASE_URL inválida ({base_url_ngrok}). Use o link do Ngrok no .env")
    else:
        print(f"[INFO] Webhook configurado: {base_url_ngrok}/pagamentos/webhook")

    try:
        email = getattr(request_data, "payer_email", "cliente@email.com")
        
        # --- CONFIGURAÇÃO DA PONTE ---
        # Apontamos para as rotas "ponte" deste Controller (que são HTTPS/Ngrok)
        # O Mercado Pago aceita HTTPS, e a ponte redireciona para localhost:5500
        back_urls = {
            "success": f"{base_url_ngrok}/pagamentos/retorno/sucesso",
            "failure": f"{base_url_ngrok}/pagamentos/retorno/falha",
            "pending": f"{base_url_ngrok}/pagamentos/retorno/pendente"
        }

        pref = criar_preferencia(
            item_title=request_data.item.title,
            quantity=request_data.item.quantity,
            unit_price=request_data.item.unit_price,
            payer_email=email,
            external_reference=str(request_data.agendamento_id),
            back_urls=back_urls,      # Envia URLs do Ngrok
            auto_return="approved"    # Ativa retorno automático
        )

        if "error" in pref:
            raise HTTPException(status_code=400, detail=pref["error"])

        return {
            "id": pref.get("id"),
            "init_point": pref.get("init_point"),
            "sandbox_init_point": pref.get("sandbox_init_point"),
        }

    except Exception as e:
        print("[ERRO] Criar preferência:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# =================================================================
#  FUNÇÃO AUXILIAR: ATUALIZAR STATUS NO BANCO
# =================================================================
def atualizar_agendamento(db: Session, external_reference: str, status_mp: str):
    if not external_reference or external_reference == "null":
        print("[AVISO] Pagamento sem referência externa.")
        return

    try:
        agendamento_id = int(external_reference)
        
        # --- CORREÇÃO APLICADA: .idagendamento ---
        agendamento = db.query(Agendamento).filter(Agendamento.idagendamento == agendamento_id).first()
        
        if not agendamento:
            print(f"[AVISO] Agendamento {agendamento_id} não encontrado no banco.")
            return

        status_map = {
            "approved": 2,  # Pago
            "pending": 1,   # Pendente
            "rejected": 3,  # Falha
            "cancelled": 3,
            "refunded": 3
        }

        novo_status = status_map.get(status_mp)
        if novo_status is None:
            print(f"[AVISO] Status MP '{status_mp}' não mapeado.")
            return

        # Verifica qual o nome correto do campo de status no seu modelo
        campo_status = 'status_id' if hasattr(agendamento, 'status_id') else 'status_pagamento'
        status_atual = getattr(agendamento, campo_status)

        if status_atual != novo_status:
            setattr(agendamento, campo_status, novo_status)
            db.commit()
            print(f"[SUCESSO] Agendamento {agendamento_id} atualizado para status {novo_status}.")
        else:
            print(f"[INFO] Agendamento {agendamento_id} já estava no status correto ({novo_status}).")

    except ValueError:
        print(f"[ERRO] external_reference '{external_reference}' não é um número válido.")


# =================================================================
#  ROTA 2: WEBHOOK (Recebe notificação do MP)
# =================================================================
@router.post("/webhook")
async def receber_notificacao_mp(request: Request, db: Session = Depends(get_db)):
    try:
        query_params = dict(request.query_params)
        try:
            body = await request.json()
        except:
            body = {}

        print("\n" + "="*50)
        print("[WEBHOOK RECEBIDO]")
        print(f"Query: {query_params}")
        # print(f"Body: {json.dumps(body, indent=2)}") 
        print("="*50 + "\n")

        op_id = query_params.get("id") or body.get("data", {}).get("id")
        topic = query_params.get("topic") or body.get("type")

        if not op_id:
            print("[AVISO] Webhook sem ID. Ignorando.")
            return {"status": "ignored"}

        # --- PAYMENT ---
        if topic == "payment":
            print(f"[INFO] Consultando pagamento {op_id}...")
            pagamento = consultar_pagamento(op_id)
            if not pagamento:
                print("[ERRO] Consulta ao MP falhou.")
                return {"status": "error"}

            status_mp = pagamento.get("status")
            ref = pagamento.get("external_reference")
            
            # Chama a função auxiliar corrigida
            atualizar_agendamento(db, ref, status_mp)

        # --- MERCHANT ORDER ---
        elif topic == "merchant_order":
            print(f"[INFO] Webhook merchant_order recebido: {op_id} - Ignorado.")
        
        else:
            print(f"[INFO] Notificação ignorada: topic='{topic}'")

        return {"status": "ok"}

    except Exception as e:
        print("[ERRO WEBHOOK]:", e)
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


# =================================================================
#  ROTA 3: POLLING DE STATUS (Front-end pergunta aqui)
# =================================================================
@router.get("/status/{agendamento_id}")
def consultar_status_pagamento(agendamento_id: int, db: Session = Depends(get_db)):
    # --- CORREÇÃO APLICADA: .idagendamento ---
    agendamento = db.query(Agendamento).filter(Agendamento.idagendamento == agendamento_id).first()
    
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    # Detecção automática do campo de status
    status_valor = getattr(agendamento, 'status_pagamento', getattr(agendamento, 'status_id', 1))

    status_map = {1: "pendente", 2: "pago", 3: "falha"}
    status_desc = "approved" if status_valor == 2 else "pending"
    if status_valor == 3: status_desc = "failure"

    return {
        "agendamento_id": agendamento.idagendamento, # Retorna o ID correto
        "status": status_valor,
        "status_descricao": status_desc
    }


# =================================================================
#  ROTA 4: PONTE (Ngrok -> Localhost)
# =================================================================
@router.get("/retorno/sucesso")
def ponte_sucesso():
    # Redireciona para o Live Server local
    return RedirectResponse("http://127.0.0.1:5500/horasmarcadasclientes.html")

@router.get("/retorno/falha")
def ponte_falha():
    return RedirectResponse("http://127.0.0.1:5500/pagamento_falhou.html")

@router.get("/retorno/pendente")
def ponte_pendente():
    return RedirectResponse("http://127.0.0.1:5500/pagamento_pendente.html")

# Rotas simples apenas para teste direto (opcional)
@router.get("/success")
def s(): return {"msg": "Sucesso"}
@router.get("/failure")
def f(): return {"msg": "Falha"}
@router.get("/pending")
def p(): return {"msg": "Pendente"}