from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
import traceback
import json
import os # Importado para verificar variáveis de ambiente

# Importações dos seus serviços e schemas
from app.services.MercadoPagoService import criar_preferencia, consultar_pagamento
from app.schemas.PagamentosSchemas import PreferenciaRequest
from app.core.database import get_db 

# Tenta importar o Model Agendamento
try:
    from app.models.AgendamentoModel import Agendamento
except ImportError:
    try:
        from app.models.Agendamento import Agendamento
    except ImportError:
        print("❌ ERRO CRÍTICO: Model 'Agendamento' não encontrado.")

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

# -------------------------------------------------------------------------
# ROTA 1: CRIAR A PREFERÊNCIA
# -------------------------------------------------------------------------
@router.post("/criar_preferencia")
async def criar_preferencia_route(request_data: PreferenciaRequest, db: Session = Depends(get_db)):
    print(f"\n🔄 --- INICIANDO CRIAÇÃO DE PAGAMENTO ---")
    print(f"🆔 Agendamento ID: {request_data.agendamento_id}")

    # --- DIAGNÓSTICO DO NGROK (Para saber por que o webhook não chega) ---
    base_url = os.getenv("BASE_URL")
    if not base_url:
        print("⚠️  ERRO GRAVE: A variável 'BASE_URL' não existe no .env!")
        print("    -> O Webhook NÃO será enviado e o status não atualizará.")
    elif "localhost" in base_url or "127.0.0.1" in base_url:
        print(f"⚠️  ERRO GRAVE: Sua BASE_URL é local ({base_url}).")
        print("    -> O Mercado Pago NÃO consegue enviar notificações para localhost.")
        print("    -> SOLUÇÃO: Use o link do Ngrok no arquivo .env (ex: BASE_URL=https://xxxx.ngrok-free.app)")
    else:
        print(f"✅ Configuração de Webhook parece correta.")
        print(f"   -> O Mercado Pago deve notificar em: {base_url}/pagamentos/webhook")
    # ---------------------------------------------------------------------

    try:
        email = getattr(request_data, "payer_email", "cliente@email.com")
        
        # Tenta enviar com todos os dados
        try:
            pref = criar_preferencia(
                item_title=request_data.item.title,
                quantity=request_data.item.quantity,
                unit_price=request_data.item.unit_price,
                payer_email=email,
                external_reference=str(request_data.agendamento_id) 
            )
        except TypeError:
            print("⚠️ Aviso: Usando versão antiga do Service (sem external_reference).")
            pref = criar_preferencia(
                item_title=request_data.item.title,
                quantity=request_data.item.quantity,
                unit_price=request_data.item.unit_price
            )
        
        if "error" in pref:
            raise HTTPException(status_code=400, detail=pref["error"])

        return {
            "id": pref.get("id"),
            "init_point": pref.get("init_point"),
            "sandbox_init_point": pref.get("sandbox_init_point"),
        }
    except Exception as e:
        print("❌ Erro ao criar:", e)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------------
# ROTA 2: WEBHOOK - MODO ESPIÃO (DEBUG)
# -------------------------------------------------------------------------
@router.post("/webhook")
async def receber_notificacao_mp(request: Request, db: Session = Depends(get_db)):
    """
    Recebe notificação do Mercado Pago e imprime TUDO no terminal.
    """
    try:
        # 1. PEGAR OS DADOS BRUTOS (Para você ver o que está chegando)
        query_params = dict(request.query_params)
        try:
            body = await request.json()
        except:
            body = {}

        print("\n" + "="*50)
        print("🔔 WEBHOOK CHEGOU! DADOS RECEBIDOS:")
        print(f"📍 Via URL (Query): {query_params}")
        print(f"📦 Via Corpo (JSON): {json.dumps(body, indent=2)}")
        print("="*50 + "\n")

        # 2. DESCOBRIR O ID DO PAGAMENTO
        # O MP pode mandar de dois jeitos: na URL (?id=123&topic=payment) ou no JSON ({data: {id: 123}})
        op_id = query_params.get("id") or query_params.get("data.id")
        topic = query_params.get("topic") or query_params.get("type")

        if not op_id and body:
            op_id = body.get("data", {}).get("id")
            topic = body.get("type") or body.get("action")

        if not op_id:
            print("⚠️ Webhook recebido sem ID de operação. Ignorando.")
            return {"status": "ignored"}

        # 3. CONSULTAR O STATUS REAL NA API DO MERCADO PAGO
        if topic == "payment" or "payment" in str(topic):
            print(f"🔎 Consultando Pagamento ID {op_id}...")
            
            pagamento = consultar_pagamento(op_id)
            
            if not pagamento:
                print("❌ Erro ao consultar API do Mercado Pago.")
                return {"status": "error"}

            status = pagamento.get("status")
            ref_agendamento = pagamento.get("external_reference") # AQUI ESTÁ O SEGREDO!

            print(f"📊 STATUS ATUAL: {status}")
            print(f"🔗 REF AGENDAMENTO (ID): {ref_agendamento}")

            # 4. ATUALIZAR O BANCO DE DADOS
            if status == "approved":
                if ref_agendamento and ref_agendamento != "null":
                    try:
                        id_busca = int(ref_agendamento)
                        agendamento = db.query(Agendamento).filter(Agendamento.idagendamento == id_busca).first()
                        
                        if agendamento:
                            print(f"✅ Encontrei o agendamento {id_busca}! Status atual: {agendamento.status_id}")
                            
                            # MUDANDO STATUS PARA 'PAGO' (Ex: 2)
                            agendamento.status_id = 2 
                            db.commit()
                            
                            print(f"🎉 SUCESSO: Agendamento {id_busca} atualizado para PAGO no banco!")
                        else:
                            print(f"⚠️ Agendamento ID {id_busca} não existe no banco.")
                    except ValueError:
                        print(f"⚠️ A referência '{ref_agendamento}' não é um número válido.")
                else:
                    print("⚠️ Pagamento aprovado, mas sem ID de agendamento vinculado.")
            else:
                print("ℹ️ Pagamento ainda não foi aprovado.")

        return {"status": "ok"}

    except Exception as e:
        print("❌ ERRO NO WEBHOOK:", e)
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

# Rotas auxiliares para o front-end
@router.get("/success")
def s(): return {"msg": "Sucesso"}
@router.get("/failure")
def f(): return {"msg": "Falha"}
@router.get("/pending")
def p(): return {"msg": "Pendente"}