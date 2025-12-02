import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
BASE_URL = os.getenv("BASE_URL") # Link do NGROK (Porta 8000)

# AGORA TUDO VEM DO MESMO LUGAR (Python/Ngrok)
if BASE_URL:
    URL_DO_FRONTEND = f"{BASE_URL}/site"
else:
    URL_DO_FRONTEND = "http://localhost:8000/site"

if not ACCESS_TOKEN:
    raise ValueError("MERCADOPAGO_ACCESS_TOKEN não encontrado no .env!")


def criar_preferencia(item_title, quantity, unit_price, payer_email="cliente@test.com", external_reference=""):
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
        "payer": {
            "email": payer_email
        },
        # Webhook: Vai para o Python (API)
        "notification_url": f"{BASE_URL}/webhooks/mp" if BASE_URL else None,
        
        # Redirecionamento: Vai para o Python (Pasta Static)
        "back_urls": {
            "success": f"{URL_DO_FRONTEND}/sucesso.html",
            "failure": f"{URL_DO_FRONTEND}/agendamento.html", 
            "pending": f"{URL_DO_FRONTEND}/sucesso.html"
        },
        "external_reference": external_reference,
        
        # Agora podemos ativar o auto_return pois o BASE_URL é HTTPS (Ngrok)
        "auto_return": "approved", 
    }

    try:
        print(f"Configuração: Webhook em {preference_data['notification_url']} | Retorno em {URL_DO_FRONTEND}")
        response = requests.post(url, json=preference_data, headers=headers)
        
        if response.status_code != 200 and response.status_code != 201:
            print(f"Erro MP ({response.status_code}):", response.text)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        error_detail = response.text if 'response' in locals() else "Sem detalhes"
        return {"error": f"Erro Mercado Pago ({response.status_code}): {error_detail}"}

    except requests.exceptions.RequestException as e:
        print("Erro Request:", e)
        return {"error": str(e)}

def consultar_pagamento(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Erro ao consultar:", e)
        return None