from flask import Flask, render_template
import psycopg2
import requests
from constants import PUSHINPAY_TOKEN  # Importar PUSHINPAY_TOKEN de constants.py

app = Flask(__name__)

# Função de conexão com o PostgreSQL
def db_connection():
    return psycopg2.connect(
        dbname="pluzk2",
        user="postgres",
        password="hd1450",
        host="localhost",
        port="5432"
    )

# Função para verificar a transação pelo txid
def checkTransaction(txid):
    url = f'https://api.pushinpay.com.br/api/transactions/{txid}'
    headers = {
        "Authorization": f"Bearer {PUSHINPAY_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erro ao checar transação: {response.status_code} - {response.text}")
        return {'status': 'not_found'}

    return response.json()

# Função para atualizar o status no banco de dados
def updateTransactionStatus(txid, new_status):
    print(f"Atualizando transação {txid} para o status '{new_status}'")
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE vendas SET status = %s WHERE txid = %s", (new_status, txid))
        conn.commit()

# Rota para a página de vendas
@app.route('/vendas', methods=['GET'])
def vendas():
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.id, v.txid, v.user_id, u.nome, v.plano, v.valor, v.status, v.created_at 
            FROM vendas v
            JOIN users u ON v.user_id = u.user_id
        ''')
        vendas_data = cursor.fetchall()

    # Verificar o status de cada transação ao carregar a página
    for venda in vendas_data:
        txid = venda[1]  # txid é o segundo item na tupla de vendas
        print(f"Verificando transação: {txid}")  # Log de verificação
        transaction_data = checkTransaction(txid)

        # Log da resposta da transação
        print(f"Dados da transação: {transaction_data}")  # Log da resposta da API

        # Se a transação foi paga, atualiza o status no banco
        if transaction_data.get('status') == 'paid':
            updateTransactionStatus(txid, 'Pago')
        elif transaction_data.get('status') == 'not_found':
            print(f"Transação {txid} não encontrada.")  # Log se a transação não foi encontrada.
        else:
            print(f"Transação {txid} ainda está com status: {transaction_data.get('status')}")  # Log do status div

    return render_template('vendas.html', vendas=vendas_data)

if __name__ == '__main__':
    app.run(debug=True, port="5033")
