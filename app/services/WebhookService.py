import mercadopago
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.Agendamento import Agendamento
from app.models.StatusPagamentos import StatusPagamento
# from mercadopago.exceptions import MPRestException

# Map de status MP -> ID do banco
STATUS_MAP = {
    "approved": 1,    # Pago
    "pending": 2,     # Pendente / Em Processamento
    "rejected": 3,    # Falha / Rejeitado
    "cancelled": 3,   # Falha
    "refunded": 3     # Falha
}

def consultar_pagamento(mp_sdk: mercadopago.SDK, payment_id: str):
    try:
        # SDK retorna o payload principal diretamente
        pagamento_info = mp_sdk.payment().get(payment_id)
        return pagamento_info  # sem .get("response")
    except Exception as e:
        print(f"[ERRO MP] Pagamento {payment_id}: {e}")
        return None

def processar_notificacao_mp(mp_sdk: mercadopago.SDK, topic: str, resource_url: str):
    if topic != "payment":
        return

    try:
        payment_id = resource_url.split("/")[-1]
    except IndexError:
        print("[ERRO] Não foi possível extrair ID do pagamento da URL.")
        return

    pagamento = consultar_pagamento(mp_sdk, payment_id)
    if not pagamento:
        print(f"[AVISO] Pagamento {payment_id} não encontrado no MP.")
        return

    status_mp = pagamento.get("status")
    agendamento_id_str = pagamento.get("external_reference")

    if not agendamento_id_str:
        print(f"[AVISO] Pagamento {payment_id} sem referência externa (agendamento_id).")
        return

    db: Session = SessionLocal()
    try:
        agendamento_id = int(agendamento_id_str)
        # Busca pelo campo correto
        ag = db.query(Agendamento).filter(Agendamento.idagendamento == agendamento_id).first()

        if not ag:
            print(f"[AVISO] Agendamento {agendamento_id} não encontrado no DB.")
            return

        novo_status_id = STATUS_MAP.get(status_mp)
        if not novo_status_id:
            print(f"[AVISO] Status MP '{status_mp}' não mapeado para ID de status.")
            return

        # Atualiza apenas se for diferente
        if ag.status_pagamento_id != novo_status_id:
            ag.status_pagamento_id = novo_status_id
            db.commit()
            print(f"[SUCESSO] Agendamento {agendamento_id} atualizado para status ID {novo_status_id}.")
        else:
            print(f"[INFO] Agendamento {agendamento_id} já está no status correto.")

    except Exception as e:
        db.rollback()
        print(f"[ERRO DB] Ao processar agendamento {agendamento_id_str}: {e}")
        raise
    finally:
        db.close()
