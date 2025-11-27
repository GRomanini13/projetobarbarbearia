# app/processors/webhook_processor.py
from app.services.MercadoPagoService import consultar_pagamento

def process_payment_event(event):
    print("Webhook recebido:", event)

    payment_id = None

    # Tipo padrão (mais usado hoje)
    if "data" in event and "id" in event["data"]:
        payment_id = event["data"]["id"]

    # Tipo antigo / fallback (muito usado em PIX)
    elif "resource" in event and "/v1/payments/" in event["resource"]:
        payment_id = event["resource"].split("/")[-1]

    # Tipo simplificado
    elif "id" in event and event.get("type") == "payment":
        payment_id = event["id"]

    if not payment_id:
        print("Nenhum ID de pagamento encontrado no webhook!")
        return

    print("Pagamento ID extraído:", payment_id)

    pagamento = consultar_pagamento(payment_id)

    if "error" in pagamento:
        print("Erro ao consultar pagamento:", pagamento)
        return

    status = pagamento.get("status")
    status_detail = pagamento.get("status_detail")
    payer = pagamento.get("payer", {}).get("email", "desconhecido")
    valor = pagamento.get("transaction_amount", 0)

    print(f"\n=== Atualização de Pagamento ===")
    print(f"ID: {payment_id}")
    print(f"Status: {status}")
    print(f"Motivo (detail): {status_detail}")
    print(f"Comprador: {payer}")
    print(f"Valor: {valor}\n")

  
    # TRATAMENTO POR STATUS
    if status == "approved":
        print("[OK] Pagamento aprovado! Liberar produto/serviço.")

    elif status == "pending":
        print("[PENDENTE] Aguardando PIX ou cartão.")

    elif status == "in_process":
        print("[ANÁLISE] Pagamento em análise.")

    elif status == "rejected":
        print(f"[RECUSADO] {status_detail}")

    elif status == "cancelled":
        print("[CANCELADO] Usuário cancelou.")

    elif status == "refunded":
        print("[REEMBOLSADO] Dinheiro devolvido.")

    elif status == "charged_back":
        print("[CHARGEBACK] Cliente abriu disputa.")

    else:
        print(f"[OUTRO] Status desconhecido: {status}")
