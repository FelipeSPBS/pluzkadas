import requests
from utils.dataManage import storeValue, readValue
from constants import TOKEN_mercadopago
import uuid  # Importa a biblioteca de geração de UUIDs


def genPixLink(value, uid):
    # Gera um idempotency key único
    idempotency_key = str(uuid.uuid4())
    
    data = requests.post('https://api.mercadopago.com/v1/payments',
                         headers={
                             "Authorization": "Bearer " + TOKEN_mercadopago,
                             "Content-Type": "application/json",
                             "X-Idempotency-Key": idempotency_key  # Adicione o cabeçalho aqui
                         },
                         json={
                             "transaction_amount": value,
                             "payment_method_id": "pix",
                             "description": "Buy telegram group access",
                             "payer": {
                                 "email": readValue('email', str(uid))
                             }})
    data = data.json()
    
    # Logar a resposta da API
    print("Resposta da API:", data)
    
    if 'id' not in data:
        raise Exception("Erro ao gerar o código PIX, verifique a resposta da API.")

    storeValue(data['id'], 'txid', uid)
    return data['point_of_interaction']['transaction_data']['qr_code']



def checkTransaction(id):
    if id == None:
        return 'Not Found'
    data = requests.get(f'https://api.mercadopago.com/v1/payments/{id}',
                        headers={"Authorization": "Bearer "+TOKEN_mercadopago})
    return [data.json()['status'], int(data.json()['transaction_details']['total_paid_amount'])]
