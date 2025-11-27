import os
from dotenv import load_dotenv
import requests

load_dotenv()

ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")  # deve ser APP_USR-xxxxxx

print("TOKEN EM USO:", ACCESS_TOKEN)  # <-- COLOQUE AQUI

def criar_preferencia(item_title, quantity, unit_price):
    url = "https://api.mercadopago.com/checkout/preferences"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    preference_data = {
        "items": [
            {
                "title": item_title,
                "quantity": int(quantity),
                "unit_price": float(unit_price),
                "currency_id": "BRL"
            }
        ],
        "back_urls": {
            "success": "https://495df6870dfb.ngrok-free.app/success",
            "failure": "https://495df6870dfb.ngrok-free.app/failure",
            "pending": "https://495df6870dfb.ngrok-free.app/pending"
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

def consultar_pagamento(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
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
