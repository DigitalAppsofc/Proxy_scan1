# bot criado por @Digital_Apps
import sys
import os
import time
import random
import requests
import urllib3
import concurrent.futures
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if len(sys.argv) > 1: TOKEN = sys.argv[1]
else: sys.exit("Erro: Token não fornecido. Inicie pelo painel_digital.py")

bot = telebot.TeleBot(TOKEN)
user_data = {}

# --- Lógica de Proxy Reutilizada ---
def get_country(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        if res['status'] == 'success': return res['country']
    except: pass
    return "Desconhecido"

def test_proxy(ip, port, timeout_val=5):
    start_time = time.time()
    proxies = {"http": f"http://{ip}:{port}", "https": f"http://{ip}:{port}"}
    try:
        res = requests.get("http://gstatic.com/generate_204", proxies=proxies, timeout=timeout_val, verify=False)
        if res.status_code in [204, 200]:
            return True, "HTTP", int((time.time() - start_time) * 1000), get_country(ip)
    except: pass
    return False, None, 0, None

def generate_ips(base_ip):
    parts = [p for p in base_ip.strip().split('.') if p] 
    ips = []
    if len(parts) == 2:
        for i in range(256):
            for j in range(256): ips.append(f"{parts[0]}.{parts[1]}.{i}.{j}")
    elif len(parts) == 3:
        for i in range(256): ips.append(f"{parts[0]}.{parts[1]}.{parts[2]}.{i}")
    return ips

# --- Comandos do Bot ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🔍 Escanear Proxies (Gerar IPs)", callback_data="gen_proxy"),
        InlineKeyboardButton("👨‍💻 Suporte / Dev", url="https://t.me/Digital_Apps")
    )
    texto = (
        "👋 *Bem-vindo ao Proxy Scanner Oficial!*\n\n"
        "🛡️ *By: @Digital_Apps*\n\n"
        "Gere e teste proxies de elite diretamente aqui pelo Telegram."
    )
    bot.send_message(message.chat.id, texto, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "gen_proxy":
        msg = bot.send_message(chat_id, "🔢 *Gerador de IPs*\nEnvie a Base de IP que deseja escanear.\nExemplo: `192.168` ou `200.15`", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_base_ip)

def process_base_ip(message):
    chat_id = message.chat.id
    base_ip = message.text.strip()
    user_data[chat_id] = {'base': base_ip}
    
    msg = bot.send_message(chat_id, "🔌 *Portas*\nEnvie a porta que deseja testar.\nExemplo: `8080` ou `80`", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_porta)

def process_porta(message):
    chat_id = message.chat.id
    porta = message.text.strip()
    user_data[chat_id]['porta'] = porta
    
    msg = bot.send_message(chat_id, "🚀 *Iniciando Teste...*\nGerando lista de IPs e verificando conexão. Isso pode levar alguns minutos.")
    
    # Inicia o scanner de forma real
    base_ip = user_data[chat_id]['base']
    ips_to_test = generate_ips(base_ip)
    
    if not ips_to_test:
        bot.send_message(chat_id, "❌ Base de IP inválida. Tente novamente enviando /start")
        return

    bot.edit_message_text(f"⏳ Testando {len(ips_to_test)} IPs na porta {porta}...\nAguarde o arquivo final.", chat_id=chat_id, message_id=msg.message_id)
    
    working_proxies = []
    # Usando 50 threads no bot para não travar o Telegram
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(test_proxy, ip, porta, 5): ip for ip in ips_to_test}
        for future in concurrent.futures.as_completed(futures):
            ip = futures[future]
            try:
                success, proto, ms, country = future.result()
                if success:
                    working_proxies.append(f"{ip}:{porta} | {proto} | {ms}ms | {country}")
            except: pass

    if working_proxies:
        filename = f"vivos_{chat_id}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for p in working_proxies: f.write(p + "\n")
        
        bot.send_message(chat_id, f"✅ *Scan Concluído!*\nEncontrados: `{len(working_proxies)}` proxies vivos.", parse_mode="Markdown")
        with open(filename, "rb") as doc:
            bot.send_document(chat_id, doc)
        os.remove(filename)
    else:
        bot.send_message(chat_id, "❌ Nenhum proxy vivo encontrado nessa base/porta.")

if __name__ == "__main__":
    print("Iniciando Bot Proxy Telegram...")
    bot.infinity_polling()
