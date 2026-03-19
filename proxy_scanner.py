# bot criado por @Digital_Apps (FAVOR MANTER OS CREDITOS E PROIBIDO A VENDA DESTE CODIGO)
import os
import sys
import time
import random
import requests
import urllib3
import re
import concurrent.futures
import subprocess
import zipfile
from colorama import init, Fore, Style

# Desativa avisos de conexões inseguras que poluem o terminal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

# Configurações da Ferramenta
VERSION = "3.0 PRO"

CHANGELOG = """
- Letreiro Gigante (ASCII) atualizado para PROXY & IPTV SCANNER!
- Novo Módulo: Scanner IPTV integrado no painel principal.
- Gerenciador Automático para Bots de Telegram (Proxy e IPTV).
- Mantido 100% das funções originais de Proxy e Cloudflare.
"""

UPDATE_URL = "https://raw.githubusercontent.com/DigitalAppsofc/Proxy_scan1/refs/heads/main/proxy_scanner.py" 
UPDATE_AVAILABLE = False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_for_updates_silently():
    global UPDATE_AVAILABLE
    try:
        res = requests.get(UPDATE_URL, timeout=2)
        if f'VERSION = "{VERSION}"' not in res.text:
            UPDATE_AVAILABLE = True
    except:
        pass

def show_banner():
    clear_screen()
    banner = f"""{Fore.CYAN}{Style.BRIGHT}
  ___  ____  ____  _  _    ____  ___   __   __ _  __ _  ____  ____ 
 (  _ \(  _ \(_  _)/ )( \  / ___)/ __) / _\ (  ( \(  ( \(  __)(  _ \\
  )   / )   /  )(  \ \/ /  \___ \( (__ /    \/    //    / ) _)  )   /
 (_)\_)(__\_) (__)  \__/   (____/\___)\_/\_/\_)__)\_)__)(____)(__\_)
    
    {Fore.WHITE}Versão {VERSION} - By {Fore.GREEN}@Digital_Apps
    {Fore.YELLOW}A Ferramenta Definitiva: IPTV & Proxies
    """
    print(banner)
    
    if UPDATE_AVAILABLE:
        print(f"    {Fore.GREEN}🟢 NOVA ATUALIZAÇÃO DISPONÍVEL! Vá no menu 6.{Style.RESET_ALL}\n")

# ==========================================
# 1. MÓDULO: SCANNER IPTV (TERMINAL)
# ==========================================
def test_iptv_account(server_url, username, password):
    try:
        url = server_url.rstrip('/')
        if not url.startswith('http'): url = 'http://' + url
        api_url = f"{url}/player_api.php?username={username}&password={password}"
        
        headers = {"User-Agent": "IPTVSmartersPro", "Accept": "*/*", "Connection": "close"}
        res = requests.get(api_url, headers=headers, timeout=10, verify=False)
        
        if res.status_code == 200:
            data = res.json()
            user_info = data.get('user_info', {})
            status_conta = str(user_info.get('status', '')).strip().lower()
            auth = user_info.get('auth')
            
            if auth == 1 or auth == "1" or status_conta in ['active', 'active!', 'trial', 'ativo', 'ativa', 'enabled']:
                return True, user_info.get('status', 'Active')
        return False, "Failed"
    except:
        return False, "Error"

def run_iptv_scanner():
    print(f"\n{Fore.CYAN}--- Módulo: Scanner IPTV ---")
    server_url = input(f"{Fore.YELLOW}Digite a URL do painel (ex: http://site.com): {Fore.WHITE}").strip()
    
    print(f"\n{Fore.CYAN}Qual Combo (Lista) deseja usar?")
    print(f"{Fore.WHITE}[1] combo.txt (Padrão do Bot)")
    print(f"{Fore.WHITE}[2] Outro arquivo (.txt na pasta Download)")
    
    op = input(f"Escolha (1/2): ").strip()
    file_path = "combo.txt"
    
    if op == '2':
        filename = input(f"Nome do arquivo {Fore.WHITE}(ex: vivos.txt){Fore.CYAN}: ").strip()
        file_path = f"/sdcard/Download/{filename}" if os.path.exists('/data/data/com.termux') else filename

    if not os.path.exists(file_path):
        print(f"{Fore.RED}[-] Arquivo {file_path} não encontrado!")
        input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")
        return

    threads_input = input(f"\nQuantidade de Threads {Fore.WHITE}[ENTER p/ 50]{Fore.CYAN}: ").strip()
    max_threads = int(threads_input) if threads_input.isdigit() else 50
    
    with open(file_path, 'r', encoding='utf-8') as f:
        linhas = [l.strip() for l in f if ':' in l]

    if not linhas:
        print(f"{Fore.RED}[-] Nenhuma conta válida (user:pass) encontrada no arquivo.")
        return

    print(f"\n{Fore.YELLOW}[*] Iniciando teste de {len(linhas)} contas no painel {server_url}...")
    print(f"{Fore.RED}[!] Pressione CTRL+C a qualquer momento para parar.\n")
    
    hits = []
    concluidos = 0
    total = len(linhas)
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {}
            for linha in linhas:
                usr, pwd = linha.split(':', 1)
                futures[executor.submit(test_iptv_account, server_url, usr, pwd)] = (usr, pwd)
                
            for future in concurrent.futures.as_completed(futures):
                concluidos += 1
                usr, pwd = futures[future]
                try:
                    is_hit, status = future.result()
                    if is_hit:
                        msg_hit = f"{usr}:{pwd} | Status: {status}"
                        sys.stdout.write(f"\r\033[K{Fore.GREEN}[+] HIT: {msg_hit}\n")
                        hits.append(msg_hit)
                except: pass
                
                if concluidos % 10 == 0 or concluidos == total:
                    progresso = f"\r{Fore.CYAN}[Progresso: {concluidos}/{total}] {Fore.WHITE}Hits: {Fore.GREEN}{len(hits)}\033[K"
                    sys.stdout.write(progresso)
                    sys.stdout.flush()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Teste interrompido pelo usuário.")

    print(f"\n\n{Fore.GREEN}[+] Scan Finalizado! {len(hits)} Hits encontrados.")
    if hits:
        nome_arquivo = f"hits_{random.randint(1000,9999)}.txt"
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            for h in hits: f.write(h + "\n")
        print(f"{Fore.YELLOW}[*] As contas válidas foram salvas em: {Fore.WHITE}{nome_arquivo}")
    
    input(f"\n{Fore.WHITE}Pressione ENTER para voltar ao menu...")

# ==========================================
# 2. MÓDULOS DE GERENCIAMENTO DE BOTS TELEGRAM
# ==========================================
def config_and_run_iptv_bot():
    print(f"\n{Fore.CYAN}--- Instalar e Ligar Bot IPTV ---")
    
    # 1. Extração do ZIP
    if not os.path.exists("main.py"):
        zip_name = "bot_scan_iptv.zip"
        if os.path.exists(zip_name):
            print(f"{Fore.YELLOW}[*] Arquivo {zip_name} encontrado! Extraindo...")
            try:
                with zipfile.ZipFile(zip_name, 'r') as zip_ref:
                    zip_ref.extractall(".")
                print(f"{Fore.GREEN}[+] Extração concluída!")
            except Exception as e:
                print(f"{Fore.RED}[-] Erro ao extrair: {e}")
                input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")
                return
        else:
            print(f"{Fore.RED}[-] O arquivo main.py ou {zip_name} não foi encontrado!")
            print(f"{Fore.WHITE}Certifique-se de que estão na mesma pasta.")
            input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")
            return

    # 2. Configuração do main.py
    print(f"\n{Fore.WHITE}Vamos configurar o seu Bot IPTV.")
    token = input(f"{Fore.YELLOW}Digite o Token do Bot do BotFather: {Fore.WHITE}").strip()
    admin_id = input(f"{Fore.YELLOW}Digite o seu ID do Telegram (Admin): {Fore.WHITE}").strip()

    if token and admin_id:
        try:
            with open("main.py", "r", encoding="utf-8") as f:
                conteudo = f.read()
            
            conteudo = re.sub(r'API_TOKEN\s*=\s*["\'].*?["\']', f'API_TOKEN = "{token}"', conteudo)
            conteudo = re.sub(r'ADMIN_ID\s*=\s*["\'].*?["\']', f'ADMIN_ID = "{admin_id}"', conteudo)
            
            with open("main.py", "w", encoding="utf-8") as f:
                f.write(conteudo)
            print(f"{Fore.GREEN}[+] Credenciais salvas com sucesso no main.py!")
        except Exception as e:
            print(f"{Fore.RED}[-] Erro ao salvar credenciais: {e}")

    # 3. Execução
    print(f"\n{Fore.YELLOW}[*] Iniciando o Bot IPTV...")
    time.sleep(1)
    print(f"{Fore.GREEN}[+] O BOT ESTÁ ON! Vá no Telegram e mande /admin no seu bot.")
    
    try: subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt: print(f"\n{Fore.RED}[!] Bot IPTV desligado.")
    input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")

def config_and_run_proxy_bot():
    print(f"\n{Fore.CYAN}--- Ligar Bot de Proxy ---")
    if not os.path.exists("bot_proxy.py"):
        print(f"{Fore.RED}[-] O arquivo bot_proxy.py não foi encontrado!")
        input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")
        return

    token = ""
    if os.path.exists("token_proxy.txt"):
        with open("token_proxy.txt", "r") as f: token = f.read().strip()
    
    if token:
        print(f"{Fore.GREEN}[+] Token salvo encontrado: {token[:10]}...")
        op = input(f"{Fore.YELLOW}Deseja usar este token? (S/N): {Fore.WHITE}").strip().upper()
        if op != 'S': token = ""

    if not token:
        token = input(f"{Fore.YELLOW}Digite o Token do Bot de Proxy: {Fore.WHITE}").strip()
        with open("token_proxy.txt", "w") as f: f.write(token)
        print(f"{Fore.GREEN}[+] Token salvo para as próximas vezes!")

    print(f"\n{Fore.YELLOW}[*] Iniciando o Bot de Proxy...")
    time.sleep(1)
    print(f"{Fore.GREEN}[+] O BOT ESTÁ ON! Vá no Telegram e mande /start")
    
    try: subprocess.run([sys.executable, "bot_proxy.py", token])
    except KeyboardInterrupt: print(f"\n{Fore.RED}[!] Bot Proxy desligado.")
    input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")


# ==========================================
# 3. MÓDULOS ORIGINAIS DE PROXY (MANTIDOS INTACTOS)
# ==========================================
def get_country(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        if res['status'] == 'success': return res['country']
    except: pass
    return "Desconhecido"

def test_proxy(ip, port, proxy_type, timeout_val):
    start_time = time.time()
    protocols_to_test = []
    if proxy_type in ['1', '2']: protocols_to_test.append(('HTTP', f"http://{ip}:{port}"))
    if proxy_type in ['1', '3']: 
        protocols_to_test.append(('SOCKS5', f"socks5://{ip}:{port}"))
        protocols_to_test.append(('SOCKS4', f"socks4://{ip}:{port}"))

    for proto_name, proxy_url in protocols_to_test:
        proxies = {"http": proxy_url, "https": proxy_url}
        try:
            res = requests.get("http://gstatic.com/generate_204", proxies=proxies, timeout=timeout_val, verify=False)
            if res.status_code in [204, 200]:
                ms = int((time.time() - start_time) * 1000)
                return True, proto_name, ms, get_country(ip)
        except: pass
        try:
            res2 = requests.get("http://example.com", proxies=proxies, timeout=timeout_val, verify=False)
            if res2.status_code == 200:
                ms = int((time.time() - start_time) * 1000)
                return True, proto_name, ms, get_country(ip)
        except: continue
    return False, None, 0, None

def generate_random_base():
    while True:
        oct1 = random.randint(1, 223)
        if oct1 in [10, 127, 169, 172, 192]: continue
        oct2 = random.randint(0, 255)
        oct3 = random.randint(0, 255)
        return f"{oct1}.{oct2}.{oct3}"

def generate_ips(base_ip):
    parts = [p for p in base_ip.strip().split('.') if p] 
    ips = []
    if len(parts) >= 4: return ['.'.join(parts[:4])]
    elif len(parts) == 3:
        base = '.'.join(parts)
        for i in range(256): ips.append(f"{base}.{i}")
    elif len(parts) == 2:
        base = '.'.join(parts)
        for i in range(256):
            for j in range(256): ips.append(f"{base}.{i}.{j}")
    elif len(parts) == 1:
        base = f"{parts[0]}.0"
        for i in range(256):
            for j in range(256): ips.append(f"{base}.{i}.{j}")
    return ips

def run_cf_checker():
    print(f"\n{Fore.CYAN}--- Cloudflare Proxy Checker ---")
    url = input(f"\n{Fore.YELLOW}Digite o site alvo (ex: https://site.com): {Fore.WHITE}").strip()
    if not url.startswith("http"): url = "https://" + url
        
    print(f"\n{Fore.CYAN}Como deseja inserir os Proxies?")
    print(f"{Fore.WHITE}[1] Ler de arquivo local (ex: vivos.txt)")
    print(f"{Fore.WHITE}[2] Colar no terminal")
    op_cf = input(f"Escolha (1/2): ").strip()
    proxies_list = []
    
    if op_cf == '1':
        file_read = input(f"Nome do arquivo {Fore.WHITE}[ENTER p/ vivos.txt]{Fore.CYAN}: ").strip() or "vivos.txt"
        paths_to_check = [file_read, f"/sdcard/Download/{file_read}"]
        file_found = False
        for path in paths_to_check:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    proxies_list = [line.strip() for line in f if line.strip()]
                file_found = True
                print(f"{Fore.GREEN}[+] Carregados de {path}")
                break
        if not file_found:
            print(f"{Fore.RED}[-] Arquivo não encontrado.")
            input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")
            return
    else:
        print(f"\n{Fore.YELLOW}Cole os proxies. Digite FIM para concluir:\n")
        while True:
            linha = input()
            if linha.strip().upper() == "FIM": break
            if linha.strip(): proxies_list.append(linha.strip())

    if not proxies_list: return

    threads_input = input(f"\nThreads {Fore.WHITE}[ENTER p/ 50]{Fore.CYAN}: ").strip()
    max_threads = int(threads_input) if threads_input.isdigit() else 50
    filename_cf = input(f"Salvar aprovados como {Fore.WHITE}[ENTER p/ cf_ok.txt]{Fore.CYAN}: ").strip() or "cf_ok.txt"
    filepath = f"/sdcard/Download/{filename_cf}" if os.path.exists('/data/data/com.termux') else filename_cf
        
    ok_count, concluidos, total = 0, 0, len(proxies_list)
    print(f"\n{Fore.YELLOW}[*] Testando {total} proxies contra {url}...")
    
    def check_cloudflare_proxy(proxy_str, url, timeout_val):
        proxy_clean = proxy_str.split('|')[0].strip()
        proxy_dict = {"http": f"http://{proxy_clean}", "https": f"http://{proxy_clean}"}
        try:
            r = requests.get(url, proxies=proxy_dict, timeout=timeout_val, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
            text = r.text.lower()
            if r.status_code == 200 and "attention required" not in text and "cloudflare" not in text:
                return "OK", proxy_clean
            return "BLOCK", proxy_clean
        except: return "DEAD", proxy_clean

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(check_cloudflare_proxy, p, url, 10): p for p in proxies_list}
        for future in concurrent.futures.as_completed(futures):
            concluidos += 1
            status, proxy_clean = future.result()
            if status == "OK":
                ok_count += 1
                sys.stdout.write(f"\r\033[K{Fore.GREEN}[OK - PASSED] {proxy_clean}\n")
                with open(filepath, 'a') as f: f.write(proxy_clean + "\n")
            progresso = f"\r{Fore.CYAN}[{concluidos}/{total}] {Fore.WHITE}Aprovados no CF: {Fore.GREEN}{ok_count}\033[K"
            sys.stdout.write(progresso)
            sys.stdout.flush()

    print(f"\n\n{Fore.GREEN}[+] Verificação Cloudflare finalizada! Salvo em: {filepath}")
    input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")

def update_system():
    print(f"\n{Fore.YELLOW}[*] Conectando ao servidor da Digital Apps...")
    try:
        response = requests.get(UPDATE_URL, timeout=10)
        if response.status_code == 200:
            new_code = response.text
            version_match = re.search(r'VERSION\s*=\s*"([^"]+)"', new_code)
            if version_match:
                new_version = version_match.group(1)
                if new_version == VERSION:
                    print(f"{Fore.GREEN}[+] Você já está na versão mais recente ({VERSION})!")
                else:
                    print(f"{Fore.CYAN}[+] Nova versão: {Fore.GREEN}v{new_version}")
                    confirm = input(f"\n{Fore.YELLOW}Instalar agora? (S/N): {Fore.WHITE}").strip().upper()
                    if confirm == 'S':
                        with open(__file__, 'w', encoding='utf-8') as f: f.write(new_code)
                        print(f"\n{Fore.GREEN}[+] Atualizado! Abra o script novamente.")
                        sys.exit()
    except Exception as e: print(f"{Fore.RED}[-] Falha: {e}")
    input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")

# ==========================================
# MENU PRINCIPAL
# ==========================================
def main():
    check_for_updates_silently()
    
    while True:
        show_banner()
        print(f"{Fore.WHITE}[1] {Fore.GREEN}Scanner IPTV (Testar lista no terminal)")
        print(f"{Fore.WHITE}[2] {Fore.CYAN}Proxy Scanner (Gerar e testar originais)")
        print(f"{Fore.WHITE}[3] {Fore.CYAN}Cloudflare Checker (Bypass em sites)")
        print(f"{Fore.WHITE}[4] {Fore.YELLOW}Instalar / Ligar Bot IPTV (Telegram)")
        print(f"{Fore.WHITE}[5] {Fore.YELLOW}Ligar Bot Proxy (Telegram)")
        
        upd_text = f"{Fore.GREEN}🟢 Atualizar Script Online" if UPDATE_AVAILABLE else f"{Fore.CYAN}Atualizar Script Online"
        print(f"{Fore.WHITE}[6] {upd_text}")
        print(f"{Fore.WHITE}[7] {Fore.RED}Sair\n")
        
        choice = input(f"{Fore.YELLOW}Escolha uma opção: {Fore.WHITE}").strip()
        
        if choice == '1':
            run_iptv_scanner()
            
        elif choice == '2':
            # === CÓDIGO ORIGINAL DO PROXY SCANNER (INTACTO) ===
            print(f"\n{Fore.CYAN}--- Geração de IPs ---")
            base_input = input("Base do IP (ex: 12.50) ou R para aleatório: ").strip()
            if base_input.upper() == 'R':
                base_ip = generate_random_base()
                print(f"{Fore.GREEN}[+] Base gerada: {base_ip}")
            else: base_ip = base_input

            porta_input = input("Portas [ENTER p/ ALL]: ").strip().lower()
            if porta_input == 'all' or porta_input == '': portas = ['80', '8080', '3128', '1080', '443', '8000', '9090']
            else: portas = [p.strip() for p in porta_input.split(',')]
            
            proxy_type = input(f"Tipo (1=Todos, 2=HTTP, 3=SOCKS) [ENTER p/ 1]: ").strip() or '1'
            threads_input = input(f"Threads [ENTER p/ 200]: ").strip()
            max_threads = int(threads_input) if threads_input.isdigit() else 200
            timeout_input = input(f"Timeout (segundos) [ENTER p/ 5]: ").strip()
            timeout_val = int(timeout_input) if timeout_input.isdigit() else 5
            
            filename = input(f"\nSalvar como [ENTER p/ vivos.txt]: ").strip() or "vivos.txt"
            filepath = f"/sdcard/Download/{filename}" if os.path.exists('/data/data/com.termux') else filename
            
            ips_to_test = generate_ips(base_ip)
            testes_totais = [(ip, port) for ip in ips_to_test for port in portas]
            
            print(f"\n{Fore.YELLOW}[*] Iniciando {len(testes_totais)} testes com {max_threads} Threads...\n")
            working_proxies, concluidos, encontrados = [], 0, 0
            
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                    futures = {executor.submit(test_proxy, ip, port, proxy_type, timeout_val): (ip, port) for ip, port in testes_totais}
                    for future in concurrent.futures.as_completed(futures):
                        ip, port = futures[future]
                        concluidos += 1
                        try:
                            success, proto, ms, country = future.result()
                            if success:
                                encontrados += 1
                                proxy_str = f"{ip}:{port} | {proto} | {ms}ms | {country}"
                                sys.stdout.write(f"\r\033[K{Fore.GREEN}[+] LIVE: {proxy_str}\n")
                                working_proxies.append(proxy_str)
                        except: pass
                        if concluidos % 15 == 0 or concluidos == len(testes_totais):
                            sys.stdout.write(f"\r{Fore.CYAN}[{concluidos}/{len(testes_totais)}] {Fore.WHITE}Encontrados: {Fore.GREEN}{encontrados}\033[K")
                            sys.stdout.flush()
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}[!] Interrompido. Salvando...")
            
            if working_proxies:
                with open(filepath, 'a', encoding='utf-8') as f:
                    for p in working_proxies: f.write(p + "\n")
                print(f"\n{Fore.GREEN}[+] Salvo em: {filepath}")
            input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")

        elif choice == '3':
            run_cf_checker()
        elif choice == '4':
            config_and_run_iptv_bot()
        elif choice == '5':
            config_and_run_proxy_bot()
        elif choice == '6':
            update_system()
        elif choice == '7':
            print(f"\n{Fore.RED}Saindo... Até logo!")
            sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Script fechado pelo usuário.")
        sys.exit()
