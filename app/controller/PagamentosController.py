from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
import traceback, json, os
from app.services.MercadoPagoService import criar_preferencia, consultar_pagamento
from app.schemas.PagamentosSchemas import PreferenciaRequest
from app.core.database import get_db

try:
    from app.models.Agendamento import Agendamento
except ImportError:
    print("ERRO CRÍTICO: Model 'Agendamento' não encontrado.")

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])


# --- CRIAR PREFERÊNCIA ---
@router.post("/criar_preferencia")
async def criar_preferencia_route(request_data: PreferenciaRequest, db: Session = Depends(get_db)):
    print(f"\n--- INICIANDO CRIAÇÃO DE PAGAMENTO ---")
    print(f"Agendamento ID: {request_data.agendamento_id}")

    base_url = os.getenv("BASE_URL")
    if not base_url or "localhost" in base_url:
        print(f"[ERRO] BASE_URL inválida ({base_url}). Use o link do Ngrok.")
    else:
        print(f"[INFO] Webhook configurado corretamente: {base_url}/pagamentos/webhook")

    try:
        email = getattr(request_data, "payer_email", "cliente@email.com")
        pref = criar_preferencia(
            item_title=request_data.item.title,
            quantity=request_data.item.quantity,
            unit_price=request_data.item.unit_price,
            payer_email=email,
            external_reference=str(request_data.agendamento_id)
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
        raise HTTPException(status_code=500, detail=str(e))


# --- FUNÇÃO AUXILIAR PARA ATUALIZAR AGENDAMENTO ---
def atualizar_agendamento(db: Session, external_reference: str, status_mp: str):
    if not external_reference or external_reference == "null":
        print("[AVISO] Pagamento sem referência externa.")
        return

    try:
        agendamento_id = int(external_reference)
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

        if agendamento.status_id != novo_status:
            agendamento.status_id = novo_status
            db.commit()
            print(f"[SUCESSO] Agendamento {agendamento_id} atualizado para status {novo_status}.")
        else:
            print(f"[INFO] Agendamento {agendamento_id} já estava no status correto ({novo_status}).")

    except ValueError:
        print(f"[ERRO] external_reference '{external_reference}' não é um número válido.")


# --- WEBHOOK ---
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
        print(f"Body: {json.dumps(body, indent=2)}")
        print("="*50 + "\n")

        op_id = query_params.get("id") or body.get("data", {}).get("id")
        topic = query_params.get("topic") or body.get("type")

        if not op_id:
            print("[AVISO] Webhook sem ID. Ignorando.")
            return {"status": "ignored"}

        # --- PAYMENT ---
        if "payment" in str(topic):
            print(f"[INFO] Consultando pagamento {op_id}...")
            pagamento = consultar_pagamento(op_id)
            if not pagamento:
                print("[ERRO] Consulta ao MP falhou.")
                return {"status": "error"}

            status_mp = pagamento.get("status")
            ref = pagamento.get("external_reference")
            atualizar_agendamento(db, ref, status_mp)

        # --- MERCHANT ORDER ---
        elif "merchant_order" in str(topic):
            print(f"[INFO] Webhook merchant_order recebido: {op_id}")
            # Para cada pagamento, chamar atualizar_agendamento se necessário
            print("Merchant order ainda não processado individualmente.")

        else:
            print(f"[INFO] Notificação ignorada, topic='{topic}' não é payment nem merchant_order.")

        return {"status": "ok"}

    except Exception as e:
        print("[ERRO WEBHOOK]:", e)
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


# --- ROTAS AUXILIARES ---
@router.get("/success")
def s(): return {"msg": "Sucesso"}

@router.get("/failure")
def f(): return {"msg": "Falha"}

@router.get("/pending")
def p(): return {"msg": "Pendente"}


@router.get("/status/{agendamento_id}")
def consultar_status_pagamento(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = db.query(Agendamento).filter(Agendamento.idagendamento == agendamento_id).first()
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    status_map = {
        1: "pendente",
        2: "pago",
        3: "falha"
    }

    return {
        "agendamento_id": agendamento.idagendamento,
        "status_id": agendamento.status_id,
        "status": status_map.get(agendamento.status_id, "desconhecido")
    }