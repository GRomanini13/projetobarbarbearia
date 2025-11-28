import os
from dotenv import load_dotenv
import requests

# Carrega variáveis de ambiente
load_dotenv()

ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
BASE_URL = os.getenv("BASE_URL")  # <-- agora o ngrok vem daqui!

if not ACCESS_TOKEN:
    raise ValueError("MERCADOPAGO_ACCESS_TOKEN não encontrado no .env!")

if not BASE_URL:
    raise ValueError("BASE_URL não encontrada no .env!")

print("TOKEN EM USO:", ACCESS_TOKEN)  # apenas para debug

# -----------------------------------------------------------
# Criar preferência de pagamento
# -----------------------------------------------------------
def criar_preferencia(item_title, quantity, unit_price):
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
        "back_urls": {
            "success": f"{BASE_URL}/success",
            "failure": f"{BASE_URL}/failure",
            "pending": f"{BASE_URL}/pending",
        },
        "auto_return": "approved",
    }

    try:
        response = requests.post(url, json=preference_data, headers=headers)
        print("Status code:", response.status_code)
        print("Response body:", response.text)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        print("Erro HTTP:", e)
        return {"error": str(e), "details": response.text}

    except requests.exceptions.RequestException as e:
        print("Erro Request:", e)
        return {"error": str(e)}


# -----------------------------------------------------------
# Consultar pagamento
# -----------------------------------------------------------
def consultar_pagamento(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    try:
        response = requests.get(url, headers=headers)
        print("Consulta pagamento - status code:", response.status_code)
        print("Consulta pagamento - body:", response.text)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        print("Erro HTTP ao consultar pagamento:", e)
        return {"error": str(e), "details": response.text}

    except requests.exceptions.RequestException as e:
        print("Erro Request ao consultar pagamento:", e)
        return {"error": str(e)}
