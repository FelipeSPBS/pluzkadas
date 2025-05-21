import psycopg2
import time
import telebot
from telebot import types
import threading
import uuid
import requests
from constants import APIkey, groupId, plano1, plano2, plano3, PUSHINPAY_TOKEN, plano1DESC, plano2DESC, plano3DESC, pack1, pack2, pack3, Orderbump1, Orderbump2, Orderbump3

# Inicializa o bot
bot = telebot.TeleBot(APIkey)

# Função para conexão com o PostgreSQL
def db_connection():
    return psycopg2.connect(
        dbname="PH",  # Substitua pelo nome do seu banco de dados
        user="postgres",   # Substitua pelo seu usuário
        password="hd1450", # Substitua pela sua senha
        host="localhost",  # Ou o endereço do seu servidor
        port="5432"        # Porta padrão do PostgreSQL
    )

# Criação da tabela de usuários e de vendas
def create_table():
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                chat_id INTEGER,
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
                status TEXT DEFAULT 'Não Pago',
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
    return "https://typebot.co/vipnayvip"  # Altere pelo seu link real

# Método para lidar com o comando Start
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = str(msg.from_user.id)
    first_name = str(msg.from_user.first_name)
    chat_id = msg.chat.id

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
                    "Oiê, amor! Olha o que aguarda você ⤵️💖\n\n"
                    "🫦 Tudo aquilo que não posso compartilhar em nenhum outro lugar!\n"
                    "🎬 Tenha acesso aos meus vídeos mais safados... 😏🔥\n\n"
                    "💎 (+500 MÍDIAS DO MEU ONLYFANS)\n"
                    "💎 (VÍDEOS COM AMIGUINHAS)\n"
                    "💎 (INCESTO COM PRIMO E TIO)\n"
                    "🚨 SORTEIOS DIÁRIOS PARA GRAVAR COMIGO!\n\n"
                    "O que você precisa para se divertir do jeito que quer é um clique e uma única atitude... \n"
                    "Te espero no meu privado! 🙈👇🏻",
                     reply_markup=showPlansButton()
                    )

# Função para mostrar planos promocionais
def showPromotionPlansButton():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
       
        types.InlineKeyboardButton(f"{plano1DESC['name']} - R$ {plano1DESC['price'] / 100:.2f}", callback_data=f"{plano1DESC['price']}-promo"),
        types.InlineKeyboardButton(f"{plano2DESC['name']} - R$ {plano2DESC['price'] / 100:.2f}", callback_data=f"{plano2DESC['price']}-promo"),
        types.InlineKeyboardButton(f"{plano3DESC['name']} - R$ {plano3DESC['price'] / 100:.2f}", callback_data=f"{plano3DESC['price']}-promo"),

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
# Escolha de planos
def choosePlan():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1

    # Adicionando os planos na nova ordem, do maior para o menor
    markup.add(
        
        types.InlineKeyboardButton(f"    {plano1['name']} - R$ {plano1['price'] / 100:.2f}    ", callback_data=f"{plano1['price']}-plan"),
        types.InlineKeyboardButton(f"    {plano2['name']} - R$ {plano2['price'] / 100:.2f}    ", callback_data=f"{plano2['price']}-plan"),
        types.InlineKeyboardButton(f"    {plano3['name']} - R$ {plano3['price'] / 100:.2f}    ", callback_data=f"{plano3['price']}-plan"),

    )
    return markup

# Gera o botão "Checkar Pagamento"
@bot.callback_query_handler(func=lambda cb: cb.data == "checkMyPayment")
def checkPayment(cb):
    chat_id = cb.message.chat.id
    user_id = str(cb.from_user.id)

    # Responder imediatamente ao callback
    bot.answer_callback_query(cb.id, text="Verificando pagamento...")

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
            # proposta depois do envio do link de convite
            send_proposal(chat_id, first_name)
        else:
            # Se não pago, informa o usuário e avisa para aguardar
            bot.send_message(chat_id, "A transação ainda não foi paga. Confira o app do banco ou continue aguardando...")
            # Inicia a contagem regressiva de 10 minutos para enviar uma mensagem de follow-up
            

# Função para verificar o pagamento após um tempo
# Dicionário para rastrear o status de envio de mensagens
user_status = {}
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
                " *Poxa gatinho, você me deixou esperando... Mas vamos fazer assim, eu vou te dar um descontinho em qualquer plano que você quiser!* \n\n"
                "🔥 [PAGUE COM PIX E RECEBA O CONTÉUDO NA HORA] 🔥\n\n"
                "🎁 *10 grupos exclusivos!*\n"
                "👩‍❤️‍💋‍👩 *Millfs*\n"
                "👙 *Peitudas*\n"
                "🍑 *Gordinhas*\n"
                "...e muito mais!\n\n"
                "🔥 *Garanta agora seu acesso e aproveite TUDO!* 🔥\n\n"
                "💎 *+500 MÍDIAS DO MEU ONLYFANS*\n", 
                parse_mode="Markdown", 
                reply_markup=showPromotionPlansButton()  # Mantendo o teclado promocional, se necessário
            )
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Erro ao enviar mensagem para o chat {chat_id}: {e}")
        # Você pode adicionar lógica adicional aqui se necessário, como registrar em um log ou enviar uma notificação.



def sendOrderBumpPlans(chat_id):
    orderbump_plans = [Orderbump1, Orderbump2, Orderbump3]

    # Função interna para enviar cada plano com um atraso
    def send_plan(plan):
        message = orderbump_messages.get(plan['name'], "Confira nosso plano especial.")
        try:
            if 'video' in plan:  # Verifica se o plano tem vídeo
                with open(plan['video'], 'rb') as video_file:
                    video_message = bot.send_video(chat_id, video_file, caption=f"{message}")

                # Cria o botão com o nome e valor do plano
                button_text = f"{plan['name']} - R$ {plan['price'] / 100:.2f}"
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(button_text, callback_data=f"{plan['price']}-orderbump"))

                # Envia o botão na mesma mensagem do vídeo
                bot.edit_message_reply_markup(chat_id=chat_id, message_id=video_message.message_id, reply_markup=markup)

            elif 'media' in plan:  # Verifica se tem uma imagem
                with open(plan['media'], 'rb') as media_file:
                    media_message = bot.send_photo(chat_id, media_file, caption=f"{message}")

                # Cria o botão com o nome e valor do plano
                button_text = f"{plan['name']} - R$ {plan['price'] / 100:.2f}"
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(button_text, callback_data=f"{plan['price']}-orderbump"))

                # Envia o botão na mesma mensagem da imagem
                bot.edit_message_reply_markup(chat_id=chat_id, message_id=media_message.message_id, reply_markup=markup)

        except Exception as e:
            print(f"Erro ao enviar o plano {plan['name']}: {e}")

    # Envia cada plano com intervalo de 5 minutos
    for plan in orderbump_plans:
        send_plan(plan)  # Envia o plano atual
        time.sleep(600)  # Aguardar 5 minutos (300 segundos) entre os envios


# Também é uma boa prática limpar o dicionário após um certo período ou uma ação

# Converte dias para segundos
def daysToSeconds(days):
    return days * 24 * 60 * 60

def welcome_user(chat_id):
    # Enviando a imagem
    with open("Apresenta-Cliente02.jpg", "rb") as image:
        bot.send_photo(chat_id, image)

def upsell(chat_id):
    with open("Donwsell-Cliente01.mp4") as video:
        bot.send_video(chat_id, video)



def videozin(chat_id):
    with open("Donwsell-Cliente02.mp4", "rb") as video:
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

    # Enviar message com instruções sobre como usar o Pix
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
def checkSpecificTransaction(chat_id, txid):
    try:
        print(f"Verificando status da transação para txid: {txid}")
        status = checkTransaction(txid)

        if status[0] == "paid":  # Verifica se a transação foi paga
            with db_connection() as conn:
                cursor = conn.cursor()
                # Define a expiração para 30 dias
                expires = int(time.time()) + daysToSeconds(30)
                
                # Atualize o status do usuário e a expiração
                cursor.execute("UPDATE users SET status = 'Assinante', expires = %s WHERE txid = %s", (expires, txid))
                print(f"Usuário {chat_id} atualizado para Assinante com expires = {expires}")

                # Atualize também o plano, se necessário
                plan_name = "nome_do_plano"  # Aqui você deve obter o nome real do plano, talvez de um parâmetro
                cursor.execute("UPDATE users SET plano = %s WHERE txid = %s", (plan_name, txid))

                # Atualiza a situação da venda
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

# Funções para gerenciamento de promoções
def ShowPacksPlans():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        types.InlineKeyboardButton(f"{pack1['name']} - R$ {pack1['price'] / 100:.2f}", callback_data=f"{pack1['price']}-promo"),
        types.InlineKeyboardButton(f"{pack2['name']} - R$ {pack2['price'] / 100:.2f}", callback_data=f"{pack2['price']}-promo"),
        types.InlineKeyboardButton(f"{pack3['name']} - R$ {pack3['price'] / 100:.2f}", callback_data=f"{pack3['price']}-promo"),
    )
    return markup

@bot.message_handler(commands=['proposta'])  # Comando para enviar a proposta
def handle_proposal(msg):
    chat_id = msg.chat.id
    first_name = msg.from_user.first_name  # Obtendo o primeiro nome do usuário
    send_proposal(chat_id, first_name)  # Passa o nome para a função send_proposal

def send_proposal(chat_id, first_name):
    message = (
        f"Oiee, {first_name}! Tudo bem? 😘\n\n"  
        "Que bom ter você no meu GRUPINHO DE PRÉVIAS 🔞! Te trouxe aqui para te fazer uma oferta especial ☺️ "
        "Tenho um conteúdo único que não envio no VIP, mas posso liberar pra você... 😈🔥\n\n"
        "Você terá acesso a:\n"
        "💎 VÍDEOS INÉDITOS 💎\n"
        "💎 SURPRESA NO PRIVADO 💎\n"
        "🔥 MEU WHATSAPP EXCLUSIVO 🔥\n\n"
        "TUDO POR R$ 14,99\n\n"
        "Ou será que vai me deixar esperando? Te aguardo ☺️👇"
    )

    bot.send_message(chat_id, message, reply_markup=ShowPacksPlans())
    print(f'Upsell enviado corretamente')

# def unban_after_delay(user_id, delay=60):  # Define o delay em segundos
#     time.sleep(delay)
#     try:
#         bot.unban_chat_member(groupId, user_id)
#         print(f'Usuário {user_id} desbanido.')
#     except Exception as e:
#         print(f'Erro ao desbanir o usuário {user_id}: {e}')

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

# Função para verificar se um membro é autorizado ao entrar no grupo
# TODO: Implementar função se necessário

# Atualizando o loop principal


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

def OrderBump():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        types.InlineKeyboardButton(f"{Orderbump3['name']} - R$ {plano3DESC['price'] / 100:.2f}", callback_data=f"{plano3DESC['price']}-promo"),
        types.InlineKeyboardButton(f"{Orderbump2['name']} - R$ {plano2DESC['price'] / 100:.2f}", callback_data=f"{plano2DESC['price']}-promo"),
        types.InlineKeyboardButton(f"{Orderbump1['name']} - R$ {plano1DESC['price'] / 100:.2f}", callback_data=f"{plano1DESC['price']}-promo"),

    )
    return markup


Orderbump3 = {"name": "VIP - 15 DIAS 😈", "length": 10, "price": 1090, "video": "video1.mp4"}
Orderbump2 = {"name": "3 MESES ❤‍🔥", "length": 60, "price": 1990, "video": "video2.mp4"}
Orderbump1 = {"name": "VITALÍCIO 🔥", "length": 90, "price": 2490, "media": "Peito.jpg"}  # Mantenha 'media' para a imagem

# Mensagens específicas para cada plano de OrderBump
orderbump_messages = {
    Orderbump3['name']: (
        "Você merece o melhor! 😏\n"
        "De R$34,90 por apenas R$24,90, tenha acesso vitalício ao conteúdo exclusivo.\n"
        "WhatsApp direto e sorteios constantes para tornar sua experiência ainda mais especial! 🍀\n\n"
        "⏰ Essa oferta é por tempo limitado! Não deixe passar! 👇🏼"
       
    ),
    Orderbump2['name']: (
        "Já decidiu? 😏\n\n"
        "O PLANO 3 MESES está com desconto imperdível!\n"
        "De R$24,90 por apenas R$19,90!\n\n"
        "Inclui WhatsApp pessoal e sorteios exclusivos para aproveitar o mês de uma forma única!\n\n"
        "💥 Essa oportunidade não se repete! Aproveite agora e tenha tudo para sempre! 👇🏼"
    ),
    Orderbump1['name']: (
        "Indeciso? 😏\n\n"
        "PLANO VITALÍCIO\n\n"
        "De R$19,90 por apenas R$10,90! 🔥\n"
        "Com WhatsApp pessoal para atendimento exclusivo e sorteios semanais para te deixar ainda mais animado! 🍀\n\n"
        "⏳ Essa chance não vai durar! Aproveite agora antes que o tempo acabe! 👇🏼"
    )
}



def schedule_promotions():
    while True:
        try:
            users = get_all_users()  # Implementar esta função conforme necessário

            for user in users:
                chat_id = user['chat_id']
                sendPromo(chat_id)  # Envia a promoção para o usuário

            time.sleep(7200)  # Aguardar 2 horas (7200 segundos) antes de enviar novamente as promoções

        except Exception as e:
            print(f"Erro ao enviar promoções: {e}")
            time.sleep(60)  # Aguardar por 1 minuto antes de tentar novamente


def sendPromo(chat_id):
    print(f"Enviando promoções para {chat_id}...")
    
    # Envia a mensagem da promoção
    promotion_markup = showPromotionPlansButton()
    
    try:
        
        print(f"Promoção enviada para {chat_id}.")

        # Iniciar o envio dos Planos de OrderBump
        threading.Thread(target=sendOrderBumpPlans, args=(chat_id,)).start()

    except Exception as e:
        print(f"Erro ao enviar promoções para {chat_id}: {e}")



@bot.callback_query_handler(func=lambda cb: 'orderbump' in cb.data)
def handleOrderBump(cb):
    user_id = str(cb.from_user.id)
    value = cb.data.split('-')[0]  # Obtém o valor do plano de OrderBump em centavos
    value_cents = int(value)

    bot.answer_callback_query(cb.id, text="Gerando código PIX...")
    
    # Tente gerar o Pix relacionado a este OrderBump.
    success = generate_pix_and_notify(value_cents, user_id, cb.message.chat.id)
    if success:
        print("Pix gerado e enviado com sucesso para o plano OrderBump.")
    else:
        print("Falha ao gerar o Pix para o plano OrderBump.")


# Função para obter todos os usuários
def get_all_users():
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM users")
        return [{'chat_id': row[0]} for row in cursor.fetchall()]


def sendPromo(chat_id):
    print(f"Enviando promoções para {chat_id}...")
    promotion_markup = showPromotionPlansButton()

    try:
        videozin(chat_id)
        bot.send_message(
            chat_id,
            "🎉 Oferta Imperdível! 🎉\n\n"
            "Quer conhecer ou voltar a aproveitar nossas ofertas especiais? 🔥\n"
            "Escolha um dos planos promocionais abaixo e desbloqueie o seu acesso! ⬇️",
            reply_markup=showPromotionPlansButton()
        )
        print(f"Promoção enviada para {chat_id}.")  # Log de sucesso
    except Exception as e:
        print(f"Erro ao enviar promoções para {chat_id}: {e}")

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
                        sendPromo(chat_id)  # Chama a função para enviar a promoção
                    else:
                        print(f"Usuário {chat_id} não interagiu com o bot, pulando...")
                    time.sleep(2)  # Tempo de espera entre envios

            time.sleep(3600)  # Espera 10 minutos (600 segundos) antes de começar de novo

        except Exception as e:
            print(f'Erro ao enviar promoções: {e}')
            time.sleep(2000)  # Espera 1 minuto antes de tentar novamente



# Seção principal do programa
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
