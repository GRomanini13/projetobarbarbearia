import mercadopago
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time, date
from fastapi import HTTPException
from app.models.Agendamento import Agendamento
from app.models.Usuario import Usuario
from app.models.Servico import Servico
from dotenv import load_dotenv
import os

load_dotenv()

# Token do MP
MP_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
if not MP_ACCESS_TOKEN:
    raise ValueError("Token do Mercado Pago não encontrado no .env")

# Inicializa SDK
mp_sdk = mercadopago.SDK(str(MP_ACCESS_TOKEN))

# Map de status MP -> ID do banco
STATUS_MAP = {
    "approved": 1,
    "pending": 2,
    "rejected": 3,
    "cancelled": 3,
    "refunded": 3
}

def criar_agendamento(db: Session, agendamento_data):
    """
    Cria o agendamento no DB com validações e status inicial.
    """
    # --- Validacoes existentes ---
    cliente = db.query(Usuario).filter(Usuario.idusuario == agendamento_data.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    barbeiro = db.query(Usuario).filter(Usuario.idusuario == agendamento_data.barbeiro_id).first()
    if not barbeiro:
        raise HTTPException(status_code=404, detail="Barbeiro não encontrado")
    if not barbeiro.is_barbeiro:
        raise HTTPException(status_code=400, detail="Usuário selecionado não é um barbeiro")
    
    servico = db.query(Servico).filter(Servico.idservicos == agendamento_data.servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    data_hora_inicio = datetime.combine(agendamento_data.data, agendamento_data.hora_inicio)
    data_hora_fim = datetime.combine(agendamento_data.data, agendamento_data.hora_fim)
    
    if data_hora_fim <= data_hora_inicio:
        raise HTTPException(400, "Horário de término deve ser maior que horário de início")
    
    # Valida expediente, almoço e conflitos (mantém seu código atual)
    # ... (copiar suas validações existentes aqui) ...
    
    # Cria agendamento com status inicial
    novo_agendamento = Agendamento(
        cliente_id=agendamento_data.cliente_id,
        barbeiro_id=agendamento_data.barbeiro_id,
        servico_id=agendamento_data.servico_id,
        data_hora_inicio=data_hora_inicio,
        data_hora_fim=data_hora_fim,
        observacao=agendamento_data.observacao,
        status_id=1,            # 1 = agendado/pendente
        status_pagamento_id=4   # 4 = aguardando pagamento
    )
    
    db.add(novo_agendamento)
    db.commit()
    db.refresh(novo_agendamento)
    
    return novo_agendamento


def criar_preferencia_mp(agendamento: Agendamento, valor_servico: float):
    """
    Cria a preferência de pagamento no Mercado Pago e retorna preference_id.
    """
    try:
        preference_data = {
            "items": [
                {
                    "title": f"Agendamento de Serviço ID {agendamento.idagendamento}",
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": valor_servico
                }
            ],
            "external_reference": str(agendamento.idagendamento),
            "notification_url": os.getenv("MP_WEBHOOK_URL"),
            "auto_return": "approved",
            "back_urls": {
                "success": os.getenv("MP_SUCCESS_URL"),
                "pending": os.getenv("MP_PENDING_URL"),
                "failure": os.getenv("MP_FAILURE_URL")
            }
        }
        preference = mp_sdk.preference().create(preference_data)
        # SDK atual retorna payload direto
        preference_id = preference["id"] if "id" in preference else preference["response"]["id"]
        return preference_id

    except Exception as e:
        print(f"[ERRO MP] Ao criar preferência: {e}")
        raise HTTPException(500, f"Erro ao criar pagamento: {e}")
