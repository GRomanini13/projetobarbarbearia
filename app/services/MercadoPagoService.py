import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
BASE_URL = os.getenv("BASE_URL")  # Ngrok ou URL pública
URL_DO_FRONTEND = f"{BASE_URL}/site" if BASE_URL else "http://localhost:8000/site"

if not ACCESS_TOKEN:
    raise ValueError("MERCADOPAGO_ACCESS_TOKEN não encontrado no .env!")

def criar_preferencia(item_title, quantity, unit_price, payer_email="cliente@test.com", external_reference=None):
    if not external_reference:
        raise ValueError("O external_reference não pode ser vazio ou None!")

    url = "https://api.mercadopago.com/checkout/preferences"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    preference_data = {
        "items": [
            {
                "title": item_title,
                "quantity": int(quantity),
                "unit_price": float(unit_price),
                "currency_id": "BRL",
            }
        ],
        "payer": {"email": payer_email},
        "notification_url": f"{BASE_URL}/pagamentos/webhook" if BASE_URL else None,
        "back_urls": {
            "success": f"{URL_DO_FRONTEND}/sucesso.html",
            "failure": f"{URL_DO_FRONTEND}/agendamento.html",
            "pending": f"{URL_DO_FRONTEND}/sucesso.html",
        },
        "external_reference": str(external_reference),
        "auto_return": "approved",
    }

    print(f"[DEBUG] Criando preferência no MP com external_reference: '{external_reference}'")
    print(f"[DEBUG] Webhook: {preference_data['notification_url']} | Front-end: {URL_DO_FRONTEND}")

    try:
        response = requests.post(url, json=preference_data, headers=headers)
        if response.status_code not in (200, 201):
            print(f"[ERRO MP] Código {response.status_code}: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_detail = response.text if 'response' in locals() else "Sem detalhes"
        return {"error": f"Erro Mercado Pago ({response.status_code}): {error_detail}"}
    except requests.exceptions.RequestException as e:
        print("[ERRO Request]:", e)
        return {"error": str(e)}


def consultar_pagamento(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Erro ao consultar pagamento:", e)
        return None
