import psycopg2
import time
import telebot
from telebot import types
import threading
import uuid
import requests
from constants import APIkey, groupId, plano1, plano2, plano3, plano4, PUSHINPAY_TOKEN, plano1DESC, plano2DESC, plano3DESC, plano4DESC, pack1,pack2,pack3, pack4,pack5 ,plano5, order1, order2, order3, order4
from flask import Flask, render_template

# Inicializa o bot
bot = telebot.TeleBot(APIkey)

# Função para conexão com o PostgreSQL
def db_connection():
    return psycopg2.connect(
        dbname="pluzk2",  # Substitua pelo nome do seu banco de dados
        user="postgres",   # Substitua pelo seu usuário
        password="hd1450", # Substitua pela sua senha
        host="localhost",  # Ou o endereço do seu servidor
        port="5432"        # Porta padrão do PostgreSQL
    )

# Criação da tabela de usuários
# Criação da tabela de vendas
def create_table():
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                chat_id BIGINT,
                nome TEXT,
                txid TEXT,
                expires INTEGER,
                plano TEXT,
                status TEXT DEFAULT 'Não assinante'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id SERIAL PRIMARY KEY,
                txid TEXT,
                user_id TEXT,
                plano TEXT,
                valor FLOAT,
                status TEXT DEFAULT 'Não Pago',  -- Adicionando a nova coluna "Status"
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()


create_table()



# Função para gerar link Pix
def genPixLinkNormal(value, uid):
    print(f"Tentando gerar código Pix normal para o usuário {uid} no valor de {value}.")
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

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"Erro ao chamar a API: {response.status_code} - {response.text}")
            raise Exception(f"Erro ao chamar a API: {response.status_code} - {response.text}")

        data = response.json()
        print("Dados recebidos da PushinPay:", data)

        if 'id' not in data or 'qr_code' not in data:
            raise Exception("Erro ao gerar o código PIX, verifique a resposta da Pushin Pay API.")
        
        return data['qr_code'], data['id']

    except Exception as e:
        print(f"Erro ao gerar o link Pix: {e}")
        return None, None

# Gera o link de convite
def generate_invite_link():
    return "https://typebot.co/nayara-vip-1-mp6t2rw"  # Altere pelo seu link real



# Método para lidar com o comando Start
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = str(msg.from_user.id)
    first_name = str(msg.from_user.first_name)
    chat_id = msg.chat.id
    planoBarato = plano1['price'] / 100
    print(f"User ID: {user_id}, Chat ID: {chat_id}, First Name: {first_name}")

    

    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            data = cursor.fetchone()

            if data is None:
                cursor.execute("INSERT INTO users (user_id, chat_id, nome) VALUES (%s, %s, %s)", (user_id, chat_id, first_name))
                conn.commit()
                print("Usuário inserido com sucesso.")
            else:
                print("Usuário já existente.")

    except Exception as e:
        print(f"Ocorreu um erro ao inserir no banco de dados: {e}")

    welcome_user(chat_id)

    bot.send_message(chat_id, 
                            "🇧🇷 𝗔𝗖𝗘𝗦𝗦𝗘 𝗢 𝗖𝗟𝗨𝗕𝗘 BRASIL FAMOSAS 🇧🇷\n\n"
                            "𝗧𝗲𝗺𝗼𝘀 𝗰𝗼𝗻𝘁𝗲𝘂𝗱𝗼𝘀 𝗱𝗲 𝗺𝗮𝗶𝘀 𝗱𝗲 𝟮𝟱 𝗽𝗹𝗮𝘁𝗮𝗳𝗼𝗿𝗺𝗮𝘀 𝗮𝗱𝘂𝗹𝘁𝗮𝘀 ⤵️\n\n"
                            "⭐️ 𝙊𝙣𝙡𝙮𝙁𝙖𝙣𝙨 / 𝙋𝙧𝙞𝙫𝙖𝙘𝙮 / 𝘾𝙡𝙤𝙨𝙚 𝙁𝙖𝙣𝙨 / 𝙋𝙖𝙩𝙧𝙚𝙤𝙣 / 𝙓𝙫𝙞𝙙𝙚𝙤𝙨 𝙍𝙚𝙙\n"
                            "⭐️ 𝙁𝙖𝙢𝙤𝙨𝙖𝙨 𝙚 𝙈𝙤𝙙𝙚𝙡𝙤𝙨 𝘽𝙧𝙖𝙨𝙞𝙡𝙚𝙞𝙧𝙖𝙨 𝙑𝙖𝙯𝙖𝙙𝙖𝙨\n"
                            "⭐️ 𝙄𝙣𝙨𝙩𝙖𝙜𝙧4𝙢 𝙚 𝙏𝙞𝙠𝙩𝙤𝙠𝙚𝙧𝙨 +18\n\n"
                            "🤩 𝘿𝙚𝙨𝙛𝙧𝙪𝙩𝙚 𝙙𝙚 𝙩𝙤𝙙𝙤 𝙘𝙤𝙣𝙩𝙚𝙪𝙙𝙤 𝙙𝙖 𝙨𝙪𝙖 𝙢𝙤𝙙𝙚𝙡𝙤 𝙥𝙧𝙚𝙛𝙚𝙧𝙞𝙙𝙖 🤩\n\n"
                            "⭐️ 𝘿𝙖𝙣ç𝙖𝙧𝙞𝙣𝙖 𝙙𝙤 𝙁𝙖𝙪𝙨𝙩ã𝙤 / 𝙋𝙖𝙣𝙞𝙘𝙖𝙩 𝙙𝙤 𝙋𝙖𝙣𝙞𝙘𝙤 𝙣𝙖 𝘽𝙖𝙣𝙙\n"
                            "⭐️ 𝘽𝙧𝙖𝙨𝙞𝙡𝙚𝙞𝙧𝙞𝙣𝙝𝙖𝙨 / 𝙈𝙖𝙣𝙨ã𝙤 𝙈𝙖𝙧𝙤𝙢𝙗𝙖\n"
                            "⭐️ 𝘾𝙡𝙤𝙨𝙚 𝙁𝙧𝙞𝙚𝙣𝙙𝙨 100% 𝙇𝙞𝙗𝙚𝙧𝙖𝙙𝙤\n\n"
                            "✅ 𝙊𝙧𝙜𝙖𝙣𝙞𝙯𝙖𝙙𝙤 𝙥𝙤𝙧 𝙣𝙤𝙢𝙚𝙨 𝙘𝙤𝙢 𝙡𝙞𝙨𝙩𝙖\n"
                            "✅ 𝙀𝙘𝙤𝙣𝙤𝙢𝙞𝙯𝙚 𝙩𝙚𝙢𝙥𝙤 𝙚 𝙙𝙞𝙣𝙝𝙚𝙞𝙧𝙤\n\n"
                            "❌𝙋𝙖𝙧𝙚 𝙙𝙚 𝙥𝙚𝙧𝙙𝙚𝙧 𝙙𝙞𝙣𝙝𝙚𝙞𝙧𝙤 𝙘𝙤𝙢 𝙫𝙞𝙥𝙨 𝙧𝙪𝙞𝙣𝙨❌\n\n"
                            "🥇 𝗘𝗡𝗧𝗥𝗘 𝗡𝗢 𝗠𝗘𝗟𝗛𝗢𝗥 𝗗𝗢 𝗕𝗥𝗔𝗦𝗜𝗟 ⤵️",
                    reply_markup=choosePlan()  # Alterado para enviar diretamente os planos
                            )


def ShowOrder():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        types.InlineKeyboardButton(f"{order1['name']} - R$ {order1['price'] / 100:.2f}", callback_data=f"{order1['price']}-promo"),
        types.InlineKeyboardButton(f"{order2['name']} - R$ {order2['price'] / 100:.2f}", callback_data=f"{order2['price']}-promo"),
        types.InlineKeyboardButton(f"{order3['name']} - R$ {order3['price'] / 100:.2f}", callback_data=f"{order3['price']}-promo"),
        types.InlineKeyboardButton(f"{order4['name']} - R$ {order4['price'] / 100:.2f}", callback_data=f"{order4['price']}-promo"),
    )
    return markup

# Função para mostrar planos promocionais
def showPromotionPlansButton():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        
        types.InlineKeyboardButton(f"{plano1DESC['name']} - R$ {plano1DESC['price'] / 100:.2f}", callback_data=f"{plano1DESC['price']}-promo"),
        types.InlineKeyboardButton(f"{plano2DESC['name']} - R$ {plano2DESC['price'] / 100:.2f}", callback_data=f"{plano2DESC['price']}-promo"),
        types.InlineKeyboardButton(f"{plano3DESC['name']} - R$ {plano3DESC['price'] / 100:.2f}", callback_data=f"{plano3DESC['price']}-promo"),
        types.InlineKeyboardButton(f"{plano4DESC['name']} - R$ {plano4DESC['price'] / 100:.2f}", callback_data=f"{plano4DESC['price']}-promo"),
        
        
    )
    return markup




# Envia as opções de promoção para usuários expirados
def sendPromotionOptions(chat_id):
    print(f"Enviando promoções para {chat_id}...")
    promotion_markup = showPromotionPlansButton()  # Chame a função para obter os botões promocionais
    
    try:
        bot.send_message(chat_id, "💥 Seu acesso expirou. 💥\n\nEscolha um dos planos promocionais abaixo para reativar seu acesso às minhas ofertas especiais:", reply_markup=promotion_markup)
    except Exception as e:
        print(f"Erro ao enviar promoções para {chat_id}: {e}")




# Callback para lidar com promoções
@bot.callback_query_handler(func=lambda cb: 'promo' in cb.data)
def handlePromotion(cb):
    user_id = str(cb.from_user.id)
    value = cb.data.split('-')[0]  # Obtém o valor do plano promocional em centavos
    value_cents = int(value)

    # Enviar uma resposta imediata ao callback
    bot.answer_callback_query(cb.id, text="Gerando código PIX...")

    print(f"Usuário {user_id} tentou acessar o plano promocional de {value_cents} centavos.")
    
    # Tente gerar o Pix
    success = generate_pix_and_notify(value_cents, user_id, cb.message.chat.id)
    if success:
        print("Pix gerado e enviado com sucesso para o plano promocional.")
    else:
        print("Falha ao gerar o Pix para o plano promocional.")

# Botão para mostrar planos disponíveis
def showPlansButton():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("OBTER OFERTA", callback_data="view_plans"))
    return markup


# Visualiza planos
@bot.callback_query_handler(func=lambda cb: cb.data == "view_plans")
def viewPlans(cb):
    print("Visualizando planos...")
    bot.send_message(cb.message.chat.id, 'Quase lá vida, agora é só escolher o plano pra ver TUDO 🫦\n' 'Selecione um Plano', reply_markup=choosePlan())

# Escolha de planos
def choosePlan():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    
    markup.add(
        types.InlineKeyboardButton(f"    {plano1['name']} - R$ {plano1['price'] / 100:.2f}    ", callback_data=f"{plano1['price']}-plan"),
        types.InlineKeyboardButton(f"    {plano2['name']} - R$ {plano2['price'] / 100:.2f}    ", callback_data=f"{plano2['price']}-plan"),
        types.InlineKeyboardButton(f"    {plano3['name']} - R$ {plano3['price'] / 100:.2f}    ", callback_data=f"{plano3['price']}-plan"),
        types.InlineKeyboardButton(f"    {plano4['name']} - R$ {plano4['price'] / 100:.2f}    ", callback_data=f"{plano4['price']}-plan"),
       
    )
    return markup


# Gera o botão "Checkar Pagamento"
@bot.callback_query_handler(func=lambda cb: cb.data == "checkMyPayment")
def checkPayment(cb):
    chat_id = cb.message.chat.id
    user_id = str(cb.from_user.id)

    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT txid FROM users WHERE user_id = %s", (user_id,))
        txid = cursor.fetchone()

        if txid is None:
            bot.send_message(chat_id, "Nenhuma transação encontrada.")
            return

        txid = txid[0]
        status = checkTransaction(txid)

        # Verifica o status da transação
        if status[0] == "paid":
            # Se pago, envia o link de convite para o grupo
            invite_link = generate_invite_link()
            bot.send_message(chat_id, f"🎉 Parabéns! Seu pagamento foi confirmado!\n\n👉 Acesse o grupo com o link: {invite_link}")
            checkSpecificTransaction(chat_id, txid)
            # Obtendo o primeiro nome do usuário pra enviar na proposta
            first_name = cb.from_user.first_name
            # proposta dps do envio do link de convite
            send_proposal(chat_id, first_name)
        else:
            
            # Se não pago, informa o usuário e avisa para aguardar
            bot.send_message(chat_id, "A transação ainda não foi paga. Confira o app do banco ou continue aguardando...")
            # Inicia a contagem regressiva de 10 minutos para enviar uma mensagem de follow-up
            threading.Thread(target=follow_up_payment_check, args=(chat_id, txid)).start()


# Função para verificar o pagamento após um tempo
def follow_up_payment_check(chat_id, txid):
    time.sleep(600)  # Aguardar 10 minutos (600 segundos)
    status = checkTransaction(txid)
    promotion_markup = showPromotionPlansButton()

    try:
        if status[0] == "paid":
            invite_link = generate_invite_link()
            bot.send_message(chat_id, f"🎉 Seu pagamento foi confirmado após verificação adicional!\n\n👉 Acesse o grupo com o link: {invite_link}")


        else:
            bot.send_message(
                chat_id,
                " 👀 Curioso pra ver tudo que eu posso te mostar?😈 \n\n"
                "Então vem... porque com só R$ 7,98 você entra no meu mundo sem limites.💸 Pagamento único — sem mensalidades, sem enrolação.\n\n"

                "E olha o que te espera lá dentro... 👇\n\n"

                "✅ Novinhas 18+\n"
                "✅ Corninhos safados\n"
                "✅ Virgens bem comportadas (ou nem tanto...)\n"
                "✅ Novinhas 18+\n"
                "✅ Lésbicas apaixonadas\n"
                "✅ Gordinhas gostosas\n"
                

                "✅ Vazadas reais\n"
                "✅ Flagras & Câmeras Escondidas\n"
                "✅ Trans maravilhosas\n"
                "✅ Orgias\n"
                "✅ GangBang pesado\n"
                "✅ Coroas experientes\n"
                "✅ Famosas deliciosas\n"

                "✅ Squirts 💦 (Bônus)\n"
                "✅ Caiu na Net 👀 (Bônus)s\n"
                "✅ Público sem pudor (Bônus)\n"
                "✅ Sexo em Público (Bônus)\n"
                "✅ +8 Canais Bônus só pra você\n\n"


                "🔁 Atualizações todos os dias\n"
                "🛡️ Compra 100% Segura\n"
                "👨‍💻 Suporte 24H\n"
                "⚡ Acesso Instantâneo\n", 
                parse_mode="Markdown", 
                reply_markup=promotion_markup  # Mantendo o teclado promocional, se necessário
            )
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Erro ao enviar mensagem para o chat {chat_id}: {e}")
        # Você pode adicionar lógica adicional aqui se necessário, como registrar em um log ou enviar uma notificação.




# Converte dias para segundos
def daysToSeconds(days):
    return days * 24 * 60 * 60

def welcome_user(chat_id):

    # Enviando a imagem
    with open("pluzkada.mp4", "rb") as video:
        bot.send_video(chat_id, video)

def videozin(chat_id):
    with open("Donwsell-Cliente01.mp4", "rb") as video:
        bot.send_video(chat_id, video)


# Função para gerar o Pix e notificar o usuário
def generate_pix_and_notify(value_cents, user_id, chat_id):
    print("Tentando gerar o código Pix...")
    qr_code, txid = genPixLinkNormal(value_cents, user_id)
    if qr_code is None or txid is None:
        print("Erro: não foi possível gerar o QR code ou txid.")
        bot.send_message(chat_id, "❌ Erro ao gerar o link Pix, tente novamente mais tarde.")
        return False

    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET txid = %s WHERE user_id = %s", (txid, user_id))
            conn.commit()
            print("TXID armazenado com sucesso no banco de dados.")

            # Inserir venda na tabela vendas
            plano = "plano_exemplo"  # Defina como você deseja obter o nome do plano
            valor = value_cents / 100  # Converte centavos para valor em reais
            cursor.execute("INSERT INTO vendas (txid, user_id, plano, valor, status) VALUES (%s, %s, %s, %s, %s)",
                           (txid, user_id, plano, valor, 'Não Pago'))  # Status inicial como "Não Pago"
            conn.commit()
            print("Venda registrada com sucesso na tabela 'Vendas'.")
    except Exception as e:
        print(f"Erro ao armazenar txid no banco de dados: {e}")

    # O restante do código pode seguir igual


    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Encaminhar Código Pix", switch_inline_query=f"{qr_code}"))

    bot.send_message(
        chat_id,
        "✅ <b>Prontinho</b>\n\n"
        "Para pagar, clique na chave Pix abaixo ⬇️ para copiar e pague no app do seu banco\n\n"
        "‼ <b>Utilize a opção PIX Copia e Cola</b> no seu aplicativo bancário "
        "(ou pagamento via QR CODE em alguns bancos)",
        parse_mode="HTML"
    )

    bot.send_message(
        chat_id,
        f"<code>{qr_code}</code>",
        parse_mode="HTML",
        reply_markup=markup
    )

    # Gera o botão "Checkar Pagamento"
    check_payment_markup = types.InlineKeyboardMarkup()
    check_payment_markup.add(types.InlineKeyboardButton("Receber Link", callback_data="checkMyPayment"))

    bot.send_message(
        chat_id,
        "⚠ <b>Importante!</b> Após o pagamento, volte nesta tela para receber o link de acesso.\n\n"
        "⏰ Aguarde alguns instantes para que nosso sistema receba a confirmação do seu pagamento pelo banco.\n\n"
        "Após concluir o pagamento, clique no botão \"<b>Receber Link</b>\" abaixo ⬇️.",
        parse_mode="HTML",
        reply_markup=check_payment_markup
    )

    # Iniciar a verificação de pagamento após 10 segundos
    threading.Thread(target=follow_up_payment_check, args=(chat_id, txid)).start()
    return True




# Função para verificar o pagamento em uma thread
# Função para verificar o pagamento em uma thread
def verificar_pagamento(user_id, chat_id, txid):
    time.sleep(60)  # Aguarda 60 segundos antes de verificar o pagamento
    checkSpecificTransaction(chat_id, txid)


# Checar status da transação
def checkTransaction(txid):
    if txid is None:
        return ['not_found', 0]

    url = f'https://api.pushinpay.com.br/api/transactions/{txid}'
    headers = {
        "Authorization": f"Bearer {PUSHINPAY_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erro ao checar transação: {response.status_code} - {response.text}")
        return ['not_found', 0]

    try:
        data = response.json()
        print("Dados da transação:", data)
    except ValueError:
        print("Resposta não está em formato JSON: " + response.text)
        return ['not_found', 0]

    if 'status' not in data:
        return ['not_found', 0]

    return [data['status'], float(data.get('value', 0))]

# Checar status da transação específica
# Checar status da transação específica
def checkSpecificTransaction(chat_id, txid):
    try:
        print(f"Verificando status da transação para txid: {txid}")
        status = checkTransaction(txid)

        if status[0] != "paid":
            with db_connection() as conn:
                cursor = conn.cursor()
                # Defina a expiração para 30 dias a partir de agora
                expires = int(time.time()) + daysToSeconds(30)
                
                cursor.execute("UPDATE users SET status = 'Assinante', expires = %s WHERE txid = %s", (expires, txid))
                print(f"Usuário {chat_id} atualizado para Assinante com expires = {expires}")

                # Atualize também o plano
                plan_name = "nome_do_plano"  # Aqui você deve obter o nome real do plano, talvez de um parâmetro
                cursor.execute("UPDATE users SET plano = %s WHERE txid = %s", (plan_name, txid))

                cursor.execute("UPDATE vendas SET status = 'Pago' WHERE txid = %s", (txid,))
                conn.commit()
                print(f"Venda atualizada para pago para txid: {txid}")

            invite_link = generate_invite_link()
            bot.send_message(chat_id, f"🎉 Parabéns! Você agora é um Assinante!\n👉 Acesse o grupo com o link de convite: {invite_link}")
            print("Usuário promovido a Assinante:", chat_id)

        else:
            print(f"Transação não paga ou com status: {status[0]}")

    except Exception as e:
        bot.send_message(chat_id, f"Erro ao verificar a transação: {e}")
        print(f"Erro ao verificar a transação para {chat_id}: {e}")

def ShowPacksPlans():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        types.InlineKeyboardButton(f"{pack1['name']} - R$ {pack1['price'] / 100:.2f}", callback_data=f"{pack1['price']}-promo"),
        types.InlineKeyboardButton(f"{pack2['name']} - R$ {pack2['price'] / 100:.2f}", callback_data=f"{pack2['price']}-promo"),
        types.InlineKeyboardButton(f"{pack3['name']} - R$ {pack3['price'] / 100:.2f}", callback_data=f"{pack3['price']}-promo"),
        types.InlineKeyboardButton(f"{pack4['name']} - R$ {pack4['price'] / 100:.2f}", callback_data=f"{pack4['price']}-promo"),
        types.InlineKeyboardButton(f"{pack5['name']} - R$ {pack5['price'] / 100:.2f}", callback_data=f"{pack5['price']}-promo"),
      
    )
    return markup

@bot.message_handler(commands=['proposta'])  # Comando para enviar a proposta
def handle_proposal(msg):
    chat_id = msg.chat.id
    first_name = msg.from_user.first_name  # Obtendo o primeiro nome do usuário
    send_proposal(chat_id, first_name)  # Passa o nome para a função send_proposal

def send_proposal(chat_id, first_name):
    message = (

"💌 ACESSO VIP LIBERADO (por tempo limitado)\n\n"

"Existe um pacote especial com conteúdos que não estão disponíveis no grupo aberto.\n"
"É exclusivo pra quem quer ver o que realmente vale a pena.\n\n"

"🔓 O que tá incluso:\n\n"

"✅ Vazados nunca postados no grupo\n"
"✅ Conteúdos organizados e atualizados direto no privado\n"
"✅ Canal secreto com acesso instantâneo\n"
"✅ Extras exclusivos só pra quem tem o VIP 😈\n\n"

"💸 Planos a partir de R$ 7,99\n"
"⏳ Disponível por tempo limitado. Depois, o acesso é fechado sem aviso.\n\n"

"Escolha seu nível de acesso e desbloqueie tudo agora.\n"
    )

    bot.send_message(chat_id, message, reply_markup=ShowPacksPlans())
    print(f'Upsell enviado corretamente')




        



def unban_after_delay(user_id, delay=60):  # Define o delay em segundos
    time.sleep(delay)
    try:
        bot.unban_chat_member(groupId, user_id)
        print(f'Usuário {user_id} desbanido.')
    except Exception as e:
        print(f'Erro ao desbanir o usuário {user_id}: {e}')

@bot.callback_query_handler(func=lambda cb: 'plan' in cb.data)
def handlePlanSelection(cb):
    user_id = str(cb.from_user.id)
    value = cb.data.split('-')[0]  # Obtém o valor do plano em centavos
    value_cents = int(value)

    # Responder imediatamente saindo do callback
    bot.answer_callback_query(cb.id, text="Gerando código PIX...")
    print(f"Usuário {user_id} selecionou o plano de {value_cents} centavos.")

    # Chamada da função para gerar o Pix
    success = generate_pix_and_notify(value_cents, user_id, cb.message.chat.id)
    if success:
        print("Pix gerado e enviado com sucesso.")
    else:
        print("Falha ao gerar o Pix.")

# # Função para verificar se um membro é autorizado ao entrar no grupo
# # @bot.my_chat_member_handler(func=lambda update: update.new_chat_member.status in ['member', 'administrator', 'creator'])
# # def check_member_access(update):
#     # user_id = str(update.from_user.id)
#     # chat_id = update.chat.id

#     print(f'Checando acesso para o usuário: {user_id}')

#     try:
#         with db_connection() as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT status, expires FROM users WHERE user_id = %s", (user_id,))
#             data = cursor.fetchone()

#             if not data:
#                 print(f'Usuário {user_id} não encontrado na base, banindo.')
#                 bot.ban_chat_member(chat_id, user_id)
#                 return

#             status, expires = data
#             current_time = int(time.time())

#             print(f'STATUS: {status}, EXPIRES: {expires}, CURRENT TIME: {current_time}')

#             if status == "Assinante" and (expires is None or expires >= current_time):
#                 print(f'Usuário {user_id} permitido no grupo.')
#                 bot.send_message(chat_id, f"Bem-vindo de volta, {update.from_user.first_name}! Você possui acesso ao grupo.")
#             else:
#                 print(f'Usuário {user_id} banido. Motivo: Status = {status}, Expires = {expires}.')
#                 bot.ban_chat_member(chat_id, user_id)

#     except Exception as e:
#         print(f'Erro ao verificar acesso do membro {user_id}: {e}')

# Função para banir usuários expirados
# def kickExpiredMembers():
#     try:
#         with db_connection() as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT user_id, expires FROM users WHERE status = 'Assinante' AND expires IS NOT NULL AND expires < %s", (int(time.time()),))
#             expired_users = cursor.fetchall()

#             for user_id, expires in expired_users:
#                 print(f'Alterando status do usuário {user_id}, acesso expirado.')

#                 chat_id = None
#                 try:
#                     cursor.execute("SELECT chat_id FROM users WHERE user_id = %s", (user_id,))
#                     chat_id = cursor.fetchone()[0]
#                 except Exception as e:
#                     print(f'Erro ao obter chat_id para o usuário {user_id}: {e}')

#                 if chat_id is not None:
#                     sendPromotionOptions(chat_id)

#                 try:
#                     bot.ban_chat_member(groupId, user_id)
#                     print(f'Usuário {user_id} banido com sucesso.')
                    
#                     # Chamando a função para desbanir após um atraso
#                     threading.Thread(target=unban_after_delay, args=(user_id, 10)).start()  # Desbanir após 3600 segundos (1 hora)

#                 except telebot.apihelper.ApiException as e:
#                     print(f'Erro ao banir o usuário {user_id}: {e}')

#                 cursor.execute("UPDATE users SET status = 'Não assinante', expires = NULL WHERE user_id = %s", (user_id,))

#             conn.commit()

#     except Exception as e:
#         print(f'Erro ao verificar e banir membros expirados: {e}')

# def kickUnauthorizedMembers():
    # try:
    #     admins = bot.get_chat_administrators(groupId)
    #     admin_ids = {str(admin.user.id) for admin in admins}
    #     bot_id = str(bot.get_me().id)

    #     with db_connection() as conn:
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT user_id, status, expires FROM users")
    #         users = cursor.fetchall()

    #         for user_id, status, expires in users:
    #             if user_id == bot_id or user_id in admin_ids:
    #                 continue

    #             if status == "Assinante" and (expires is None or expires >= int(time.time())):
    #                 print(f'Usuário {user_id} é um assinante válido. Não será banido.')
    #                 continue

    #             # Se o usuário não for um assinante válido, banir
    #             print(f'Banindo {user_id} - Usuário não autorizado.')
    #             try:
    #                 bot.ban_chat_member(groupId, user_id)
    #             except Exception as e:
    #                 print(f'Erro ao banir o usuário {user_id}: {e}')
                    
    # except Exception as e:
    #     print(f'Erro ao verificar membros do grupo: {e}')

# Atualizando o loop principal
def kickPeople():
    while True:
        try:
            # kickUnauthorizedMembers()  # Verifica usuários não autorizados
            # kickExpiredMembers()        # Verifica e atualiza usuários expirados
            time.sleep(6600)       # Checa a cada 3 horas
        except Exception as e:
            print(f'Erro no kickPeople: {e}')
            time.sleep(60)

def is_user_interacted(chat_id):
    # Implementar lógica para verificar se o usuário interagiu, por exemplo, conferindo se o chat_id está na tabela de usuários
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE chat_id = %s)", (chat_id,))
        return cursor.fetchone()[0]
    
def has_interacted(chat_id):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE chat_id = %s)", (chat_id,))
        return cursor.fetchone()[0]



@bot.message_handler(commands=['order'])  # Comando para enviar a proposta
def handle_order(msg):
    chat_id = msg.chat.id
    sendPromo(chat_id)


def sendPromo(chat_id):
    print(f"Enviando promoções para {chat_id}...")
    promotion_markup = ShowOrder()

    try:
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 1
        bot.send_message(
            chat_id,
            "🔥😈 ACESSO VIP AO MELHOR CONTEÚDO +18! 🔥\n"
            "Desbloqueie milhares de vídeos vazados, completos e atualizados todos os dias!\n\n"

            "💸 Planos a partir de R$ 7,98 – pagamento único, sem mensalidades!\n\n"

            "Você encontra:"
            "✅ Novinhas, lésbicas, trans, cornos, gordinhas, virgens\n"
            "✅ Vazadas, flagras reais, celebridades, maduras, orgias e mais\n"
            "🎁 Bônus: Caiu na net, público, squirts e +8 canais secretos\n\n"

            "⚡️ Acesso instantâneo\n"
            "📅 Atualizações diárias\n"
            "🔒 100% seguro e discreto\n"
            "👨‍💻 Suporte 24h\n\n"

            "📌 Pague uma vez e tenha acesso vitalício!\n"
            "🤤😈 Você irá pagar apenas uma vez para ter acesso ao VIP para sempre com atualizações diárias.\n",
            reply_markup=promotion_markup
        )
        print(f"Promoção enviada para {chat_id}.")  # Log de sucesso
    except telebot.apihelper.ApiTelegramException as e:
        if "blocked" in str(e):  # Checa se o motivo do erro é bloqueado
            print(f"Usuário {chat_id} bloqueou o bot. Pulando...")
        else:
            print(f"Erro ao enviar promoções para {chat_id}: {e}")



def send_proposal(chat_id, first_name):
    message = (

        "💌 Ei... posso te contar um segredo? "
        "Você tá aqui no grupinho, mas nem imagina o que eu guardei só pra quem realmente merece 😈\n\n"
        "📦 Preparei um pacote VIP EXCLUSIVO, que não vai pra ninguém do grupo… só pra quem fechar comigo agora.\n\n"
        "Olha o que você recebe:\n\n"

        "✅ Conteúdos secretos (nunca postados antes)\n"
        "✅ Presente íntimo direto no privado\n"
        "✅ Meu WhatsApp pessoal – só os especiais têm 💋\n\n"

        "💸 Por tão pouco assim? A partir de R$ 7,99... e o prazer é todo seu.(É sério. Depois não diz que eu não avisei…)\n\n"
        "⏳ Válido só pra hoje. Me chama antes que eu feche essa porta."
    )

    bot.send_message(chat_id, message, reply_markup=ShowPacksPlans())
    print(f'Upsell enviado corretamente')

def PROMO():
    while True:
        try:
            with db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT chat_id FROM users")
                users = cursor.fetchall()

                for user in users:
                    chat_id = user[0]
                    if has_interacted(chat_id):
                        sendPromo(chat_id)
                    else:
                        print(f"Usuário {chat_id} não interagiu com o bot, pulando...")
                    time.sleep(2)  # Tempo de espera entre envios

            time.sleep(43200)  # Espera antes de começar de novo

        except Exception as e:
            print(f'Erro ao enviar promoções: {e}')







if __name__ == '__main__':
    print("Iniciando o bot...")

    # Inicia a thread para programar as promoções, se necessário
    promo_scheduler = threading.Thread(target=PROMO)
    promo_scheduler.start()

    # Inicia o polling do bot para receber mensagens e interações
    while True:
        try:
            print("Bot em execução...")
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Erro ao executar o bot: {e}. Reiniciando...")
            time.sleep(5)  # Espera um pouco antes de reiniciar



# Função para desbanir um usuário
def unbanUser(user_id):
    try:
        bot.unban_chat_member(groupId, user_id)
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET status = 'Assinante' WHERE user_id = %s", (user_id,))
            conn.commit()
            print(f'Usuário {user_id} desbanido e promovido a Assinante.')
    except Exception as e:
        print(f'Erro ao desbanir o usuário {user_id}: {e}')

try:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, expires FROM users WHERE expires IS NOT NULL OR status = 'Não assinante'")
        expired_users = cursor.fetchall()

        for user in expired_users:
            user_id, expires = user
            if expires is None or expires < int(time.time()):
                print(f'Alterando status do usuário {user_id}, acesso expirado.')

                # Tente obter o chat_id para enviar mensagem
                chat_id = None
                try:
                    cursor.execute("SELECT chat_id FROM users WHERE user_id = %s", (user_id,))
                    chat_id = cursor.fetchone()[0]
                except Exception as e:
                    print(f'Erro ao obter chat_id para o usuário {user_id}: {e}')

                if chat_id is not None:
                    # Mensagem de expiração com planos promocionais
                    sendPromotionOptions(chat_id)

                    # Banir o usuário
                    bot.ban_chat_member(groupId, user_id)
                    print(f'Usuário {user_id} banido com sucesso.')

                # Atualiza para não assinante
                cursor.execute("UPDATE users SET status = 'Não assinante', expires = NULL WHERE user_id = %s", (user_id,))

        conn.commit()

except Exception as e:
    print(f'Erro ao verificar membros expirados: {e}')
