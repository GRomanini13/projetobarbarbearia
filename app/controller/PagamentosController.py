from fastapi import APIRouter, HTTPException, Request, Depends, Query
from sqlalchemy.orm import Session
import traceback
import sys
import inspect # Importado para ajudar no diagnóstico de erros

# Imports conforme seu código
from app.services.MercadoPagoService import criar_preferencia
from app.schemas.PagamentosSchemas import PreferenciaRequest
from app.core.database import get_db 

router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"]
)

@router.post("/criar_preferencia")
async def criar_preferencia_route(
    request_data: PreferenciaRequest, 
    request: Request,
    db: Session = Depends(get_db)
):
    print(f"🔄 Recebendo pedido de preferência. Dados recebidos: {request_data}")
    
    try:
        # --- CORREÇÃO FINAL BASEADA NO DIAGNÓSTICO ---
        # A função 'criar_preferencia' do seu serviço aceita APENAS 3 argumentos:
        # (item_title, quantity, unit_price).
        # Removemos payer_email, payer_name e external_reference da chamada
        # pois o seu serviço atual não suporta esses campos.
        
        pref = criar_preferencia(
            request_data.item.title,            # item_title
            int(request_data.item.quantity),    # quantity
            float(request_data.item.unit_price) # unit_price
        ) 
        
        # Verifica se retornou um erro tratado
        if isinstance(pref, dict) and "error" in pref:
            print(f"⚠️ Erro retornado pelo Service: {pref['error']}")
            raise HTTPException(status_code=400, detail=pref["error"])

        # Verifica se a resposta tem o formato esperado
        if not pref or "init_point" not in pref:
            print(f"⚠️ Resposta inválida do Service: {pref}")
            raise HTTPException(status_code=500, detail="O serviço de pagamento não retornou um link válido.")

        print(f"✅ Preferência criada com sucesso! ID: {pref.get('id')}")

        return {
            "id": pref.get("id"),
            "init_point": pref.get("init_point"),
            "sandbox_init_point": pref.get("sandbox_init_point"),
        }

    except AttributeError as ae:
        print("❌ ERRO DE ATRIBUTO (Dados incompatíveis):")
        print(f"Tentativa de acessar um campo inexistente: {ae}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro de processamento de dados (AttributeError): {str(ae)}")

    except TypeError as te:
        print("❌ ERRO DE ASSINATURA DA FUNÇÃO (TypeError):")
        print(f"A função 'criar_preferencia' foi chamada com argumentos incorretos: {te}")
        
        # --- DIAGNÓSTICO AUTOMÁTICO ---
        try:
            sig = inspect.signature(criar_preferencia)
            print(f"\n💡 DICA DO SISTEMA: A sua função 'criar_preferencia' foi definida esperando estes parâmetros:")
            print(f"👉 {sig}")
            print("Compare a lista acima com o que estamos enviando.\n")
        except Exception:
            pass

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno de configuração: {str(te)}")

    except Exception as e:
        # --- BLOCO DE DEPURAÇÃO ---
        print("❌ ERRO CRÍTICO AO CRIAR PREFERÊNCIA:")
        traceback.print_exc() 
        # --------------------------
        
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno no servidor: {str(e)}"
        )

# --- Rotas de Retorno (Back URLs) ---

@router.get("/success")
def pagamento_sucesso(
    payment_id: str = Query(..., alias="payment_id"),
    status: str = Query(..., alias="status"),
    external_reference: str = Query(..., alias="external_reference"),
    merchant_order_id: str = Query(None, alias="merchant_order_id")
):
    print(f"✅ Pagamento APROVADO! ID MP: {payment_id}, Status: {status}, Ref: {external_reference}")
    return {
        "message": "Pagamento aprovado! Seu pedido será processado.",
        "detalhes_mp": { "payment_id": payment_id, "status": status, "referencia": external_reference }
    }

@router.get("/failure")
def pagamento_falha(
    payment_id: str = Query(..., alias="payment_id"),
    status: str = Query(..., alias="status"),
    external_reference: str = Query(..., alias="external_reference"),
    merchant_order_id: str = Query(None, alias="merchant_order_id")
):
    print(f"❌ Pagamento RECUSADO! ID MP: {payment_id}, Status: {status}, Ref: {external_reference}")
    return {
        "message": "Pagamento recusado. Tente novamente.",
        "detalhes_mp": { "payment_id": payment_id, "status": status, "referencia": external_reference }
    }

@router.get("/pending")
def pagamento_pendente(
    payment_id: str = Query(..., alias="payment_id"),
    status: str = Query(..., alias="status"),
    external_reference: str = Query(..., alias="external_reference"),
    merchant_order_id: str = Query(None, alias="merchant_order_id")
):
    print(f"⏳ Pagamento PENDENTE! ID MP: {payment_id}, Status: {status}, Ref: {external_reference}")
    return {
        "message": "Seu pagamento está pendente.",
        "detalhes_mp": { "payment_id": payment_id, "status": status, "referencia": external_reference }
    }