import requests
from utils.dataManage import storeValue, readValue
from constants import PUSHINPAY_TOKEN  # Adicione seu token da Pushin Pay
import uuid  # Importa a biblioteca de geração de UUIDs

def genPixLink(value, uid):
    # Gera um idempotency key único
    idempotency_key = str(uuid.uuid4())

    url = 'https://api.pushinpay.com.br/api/pix/cashIn'
    headers = {
        "Authorization": f"Bearer {PUSHINPAY_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "value": value,
        "webhook_url": "http://seuservico.com/webhook",  # Atualize para o seu webhook
        "idempotency_key": idempotency_key
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Erro ao chamar a API: {response.status_code} - {response.text}")

    try:
        data = response.json()
    except ValueError:
        raise Exception("Resposta não está em formato JSON: " + response.text)

    # Garantindo que o txid está presente na resposta
    if 'id' not in data or 'qr_code' not in data:
        raise Exception("Erro ao gerar o código PIX, verifique a resposta da Pushin Pay API.")

    return data['qr_code'], data['id']  # Retorne o QR code e o txid

def checkTransaction(txid):
    # Verificação se txid é None
    if txid is None:
        return ['not_found', 0]

    # URL para checar o status da transação
    url = f'https://api.pushinpay.com.br/api/transactions/{txid}'  # Usando a URL que você mostrou com cURL
    headers = {
        "Authorization": f"Bearer {PUSHINPAY_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Realizando a requisição GET
    response = requests.get(url, headers=headers)

    # Verificando o status da resposta
    if response.status_code != 200:
        print(f"Erro ao checar transação: {response.status_code} - {response.text}")  # Log detalhado
        return ['not_found', 0]

    try:
        data = response.json()  # Tente converter a resposta para JSON
    except ValueError:
        print("Resposta não está em formato JSON: " + response.text)
        return ['not_found', 0]

    # Verifica se 'status' está presente na resposta
    if 'status' not in data:
        return ['not_found', 0]

    # Retorna o status e o valor
    return [data['status'], float(data.get('value', 0))]  # Modifique 'amount' para 'value'
