import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
BASE_URL = os.getenv("BASE_URL")  # Ngrok

# Fallback se não for passado nada
URL_PADRAO_FRONT = f"{BASE_URL}/site" if BASE_URL else "http://localhost:5500"

if not ACCESS_TOKEN:
    raise ValueError("MERCADOPAGO_ACCESS_TOKEN não encontrado no .env!")

def criar_preferencia(item_title, quantity, unit_price, payer_email="cliente@test.com", external_reference=None, back_urls=None, auto_return=None):
    if not external_reference:
        raise ValueError("O external_reference não pode ser vazio ou None!")

    url = "https://api.mercadopago.com/checkout/preferences"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    # Se o Controller não mandou URLs, usamos um padrão de emergência
    if not back_urls:
        back_urls = {
            "success": f"{URL_PADRAO_FRONT}/sucesso.html",
            "failure": f"{URL_PADRAO_FRONT}/falha.html",
            "pending": f"{URL_PADRAO_FRONT}/pendente.html",
        }

    # Se auto_return for ativado, garantimos que seja "approved" ou "all"
    if auto_return and auto_return not in ["approved", "all"]:
        auto_return = "approved"

    # --- MONTAGEM DO PACOTE JSON (IMPORTANTE: back_urls DEVE ESTAR AQUI) ---
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
        
        # AQUI ESTÃO OS CAMPOS QUE ESTAVAM DANDO ERRO
        "back_urls": back_urls,
        "auto_return": auto_return, # Se for None, o MP ignora. Se for "approved", ele exige back_urls.
        
        "external_reference": str(external_reference),
        "binary_mode": True # Opcional: força o pagamento a ser aprovado ou rejeitado na hora (sem pendente)
    }

    # DEBUG PARA GARANTIR QUE ESTÁ NO PACOTE
    print(f"[DEBUG] Enviando Preferência. Auto Return: {preference_data.get('auto_return')}")
    print(f"[DEBUG] Back URLs no pacote: {preference_data.get('back_urls')}")

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