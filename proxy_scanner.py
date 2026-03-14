import os
import sys
import time
import random
import requests
import urllib3
import re
import concurrent.futures
from colorama import init, Fore, Style

# Desativa avisos de conexões inseguras que poluem o terminal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

# Configurações da Ferramenta
VERSION = "2.0"

CHANGELOG = """
- Letreiro Gigante (ASCII) atualizado para PROXY SCANNER!
- Novo Módulo: Cloudflare Checker integrado ao painel principal.
- Teste de Bypass automático ou por colagem manual.
- Notificação inteligente de atualização na tela inicial (Bolinha Verde).
"""

UPDATE_URL = "https://raw.githubusercontent.com/DigitalAppsofc/Proxy_scan1/refs/heads/main/proxy_scanner.py" 
UPDATE_AVAILABLE = False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_for_updates_silently():
    """Verifica rapidamente em segundo plano se há atualizações"""
    global UPDATE_AVAILABLE
    try:
        res = requests.get(UPDATE_URL, timeout=2)
        if f'VERSION = "{VERSION}"' not in res.text:
            UPDATE_AVAILABLE = True
    except:
        pass

def show_banner():
    clear_screen()
    # Novo Letreiro desenhado especialmente para caber na tela do celular!
    banner = f"""{Fore.CYAN}{Style.BRIGHT}
   ____  ____  __  _  _  _  _ 
  (  _ \\(  _ \\/  \\( \\/ )( \\/ )
   ) __/ )   (  O ))  (  \\  / 
  (__)  (_)\\_)\\__/(_/\\_) (__) 
    ___  ___  __  __ _  __ _  ____  ____ 
   / __)/ __)/  \\(  ( \\(  ( \\(  __)(  _ \\
   \\__ \\\\__ (  O )    /    / ) _)  )   /
   (___/(__/ \\__/\\_)__)\\_)__)(____)(__\\_)
    
    {Fore.WHITE}Versão {VERSION} - By {Fore.GREEN}@Digital_Apps
    """
    print(banner)
    
    if UPDATE_AVAILABLE:
        print(f"    {Fore.GREEN}🟢 NOVA ATUALIZAÇÃO DISPONÍVEL! Vá no menu 4.{Style.RESET_ALL}\n")

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

# --- MÓDULO: CLOUDFLARE CHECKER ---
def check_cloudflare_proxy(proxy_str, url, timeout_val):
    proxy_clean = proxy_str.split('|')[0].strip()
    
    proxy_dict = {
        "http": f"http://{proxy_clean}",
        "https": f"http://{proxy_clean}"
    }

    try:
        r = requests.get(url, proxies=proxy_dict, timeout=timeout_val, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
        text = r.text.lower()

        if r.status_code == 200 and "attention required" not in text and "cloudflare" not in text:
            return "OK", proxy_clean
        elif r.status_code in [403, 1020, 429] or "cloudflare" in text:
            return "BLOCK", proxy_clean
        else:
            return "FAIL", proxy_clean
    except:
        return "DEAD", proxy_clean

def run_cf_checker():
    print(f"\n{Fore.CYAN}--- Cloudflare Proxy Checker ---")
    print(f"{Fore.WHITE}Este módulo testa se os seus proxies vivos conseguem burlar")
    print(f"{Fore.WHITE}a proteção de um site específico (ex: um site de IPTV ou API).")
    
    url = input(f"\n{Fore.YELLOW}Digite o site alvo (ex: https://site.com): {Fore.WHITE}").strip()
    if not url.startswith("http"):
        url = "https://" + url
        
    print(f"\n{Fore.CYAN}Como deseja inserir os Proxies?")
    print(f"{Fore.WHITE}[1] Ler automaticamente do arquivo local (ex: vivos.txt)")
    print(f"{Fore.WHITE}[2] Colar manualmente no terminal")
    
    op_cf = input(f"Escolha (1/2): ").strip()
    proxies_list = []
    
    if op_cf == '1':
        file_read = input(f"Nome do arquivo para ler {Fore.WHITE}[ENTER p/ vivos.txt]{Fore.CYAN}: ").strip()
        if not file_read: file_read = "vivos.txt"
        
        paths_to_check = [file_read, f"/sdcard/Download/{file_read}"]
        file_found = False
        
        for path in paths_to_check:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    proxies_list = [line.strip() for line in f if line.strip()]
                file_found = True
                print(f"{Fore.GREEN}[+] {len(proxies_list)} proxies carregados de {path}")
                break
                
        if not file_found:
            print(f"{Fore.RED}[-] Arquivo não encontrado. Faça um Scan primeiro!")
            input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")
            return
            
    else:
        # AQUI ESTÁ A OPÇÃO DE COLAR OS PRÓPRIOS PROXIES!
        print(f"\n{Fore.YELLOW}Cole sua lista de proxies (IP:PORTA).")
        print(f"{Fore.WHITE}Quando terminar de colar, digite a palavra {Fore.RED}FIM{Fore.WHITE} e dê Enter.\n")
        while True:
            linha = input()
            if linha.strip().upper() == "FIM": break
            if linha.strip(): proxies_list.append(linha.strip())

    if not proxies_list:
        print(f"{Fore.RED}[-] Nenhuma proxy fornecida.")
        return

    threads_input = input(f"\nQuantidade de Threads {Fore.WHITE}[ENTER p/ 50]{Fore.CYAN}: ").strip()
    max_threads = int(threads_input) if threads_input.isdigit() else 50
    
    filename_cf = input(f"Salvar os aprovados como {Fore.WHITE}[ENTER p/ cf_ok.txt]{Fore.CYAN}: ").strip()
    if not filename_cf: filename_cf = "cf_ok.txt"
    
    filepath = filename_cf
    if os.path.exists('/data/data/com.termux') and os.path.exists('/sdcard/Download') and os.access('/sdcard/Download', os.W_OK):
        filepath = os.path.join('/sdcard/Download', filename_cf)
        
    print(f"\n{Fore.YELLOW}[*] Testando {len(proxies_list)} proxies contra {url}...\n")
    
    ok_count = 0
    total = len(proxies_list)
    concluidos = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(check_cloudflare_proxy, p, url, 10): p for p in proxies_list}
        
        for future in concurrent.futures.as_completed(futures):
            concluidos += 1
            status, proxy_clean = future.result()
            
            if status == "OK":
                ok_count += 1
                sys.stdout.write(f"\r\033[K{Fore.GREEN}[OK - PASSED] {proxy_clean}\n")
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(proxy_clean + "\n")
                
            progresso = f"\r{Fore.CYAN}[Progresso: {concluidos}/{total}] {Fore.WHITE}Aprovados no CF: {Fore.GREEN}{ok_count}\033[K"
            sys.stdout.write(progresso)
            sys.stdout.flush()

    print(f"\n\n{Fore.GREEN}[+] Verificação Cloudflare finalizada!")
    if ok_count > 0:
        print(f"{Fore.YELLOW}[*] {ok_count} Proxies aprovados salvos em: {Fore.WHITE}{filepath}")
    else:
        print(f"{Fore.RED}[-] Nenhum proxy conseguiu passar pela proteção deste site.")
        
    input(f"\n{Fore.WHITE}Pressione ENTER para voltar ao menu...")
# -----------------------------------------------

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
                    print(f"{Fore.CYAN}[+] Nova versão encontrada: {Fore.GREEN}v{new_version}")
                    changelog_match = re.search(r'CHANGELOG\s*=\s*\"\"\"(.*?)\"\"\"', new_code, re.DOTALL)
                    if changelog_match:
                        print(f"\n{Fore.YELLOW}=== O que há de novo ===")
                        print(f"{Fore.WHITE}{changelog_match.group(1).strip()}")
                        print(f"{Fore.YELLOW}========================")
                    confirm = input(f"\n{Fore.YELLOW}Deseja instalar a atualização agora? (S/N): {Fore.WHITE}").strip().upper()
                    if confirm == 'S':
                        with open(__file__, 'w', encoding='utf-8') as f: f.write(new_code)
                        print(f"\n{Fore.GREEN}[+] Atualização concluída com sucesso!")
                        print(f"{Fore.WHITE}Por favor, abra a ferramenta novamente digitando: {Fore.CYAN}px")
                        sys.exit()
                    else:
                        print(f"{Fore.RED}[-] Atualização cancelada pelo usuário.")
            else: print(f"{Fore.RED}[-] Não foi possível ler a versão no servidor.")
        else: print(f"{Fore.RED}[-] Erro ao acessar o servidor de atualização.")
    except Exception as e: print(f"{Fore.RED}[-] Falha na atualização: {e}")
    input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")

def main():
    check_for_updates_silently()
    
    while True:
        show_banner()
        print(f"{Fore.WHITE}[1] {Fore.CYAN}Proxy Scanner (Gerar IPs e Buscar Vivos)")
        print(f"{Fore.WHITE}[2] {Fore.CYAN}Cloudflare Checker (Testar bypass em sites)")
        print(f"{Fore.WHITE}[3] {Fore.CYAN}Informações e Como Usar")
        
        upd_text = f"{Fore.GREEN}🟢 Atualizar Script Online" if UPDATE_AVAILABLE else f"{Fore.CYAN}Atualizar Script Online"
        print(f"{Fore.WHITE}[4] {upd_text}")
        print(f"{Fore.WHITE}[5] {Fore.RED}Sair\n")
        
        choice = input(f"{Fore.YELLOW}Escolha uma opção: {Fore.WHITE}")
        
        if choice == '1':
            print(f"\n{Fore.CYAN}--- Geração de IPs ---")
            print(f"{Fore.GREEN}Exemplos:")
            print(f"{Fore.WHITE}12.50.107     {Fore.YELLOW}-> (Gera 256 IPs)")
            print(f"{Fore.WHITE}209.197       {Fore.YELLOW}-> (Gera 65.536 IPs)")
            print(f"{Fore.WHITE}Digite {Fore.YELLOW}R{Fore.WHITE} para gerar uma base aleatória válida.")
            
            base_input = input("\nBase do IP ou R: ").strip()
            if base_input.upper() == 'R':
                base_ip = generate_random_base()
                print(f"{Fore.GREEN}[+] Base gerada automaticamente: {base_ip}")
            else:
                base_ip = base_input

            print(f"\n{Fore.CYAN}--- Portas para Teste ---")
            print(f"Digite uma porta {Fore.WHITE}(ex: 8080){Fore.CYAN}, várias {Fore.WHITE}(80,8080){Fore.CYAN}")
            print(f"Ou dê {Fore.YELLOW}ENTER (ALL){Fore.CYAN} para testar as portas proxy mais comuns.")
            
            porta_input = input("Portas: ").strip().lower()
            if porta_input == 'all' or porta_input == '':
                portas = ['80', '8080', '3128', '1080', '443', '8000', '9090']
                print(f"{Fore.GREEN}[+] Portas selecionadas: {', '.join(portas)}")
            else:
                portas = [p.strip() for p in porta_input.split(',')]
            
            print(f"\n{Fore.CYAN}--- Protocolos e Desempenho ---")
            proxy_type = input(f"Tipo (1=Todos, 2=HTTP, 3=SOCKS) {Fore.WHITE}[ENTER p/ Padrão: 1]{Fore.CYAN}: ").strip()
            if not proxy_type: proxy_type = '1'
            
            threads_input = input(f"Quantidade de Threads (Velocidade) {Fore.WHITE}[ENTER p/ Padrão: 200]{Fore.CYAN}: ").strip()
            max_threads = int(threads_input) if threads_input.isdigit() else 200
            
            timeout_input = input(f"Timeout em segundos {Fore.WHITE}[ENTER p/ Padrão: 5]{Fore.CYAN}: ").strip()
            timeout_val = int(timeout_input) if timeout_input.isdigit() else 5
            
            filename_input = input(f"\nNome do arquivo para salvar {Fore.WHITE}[ENTER p/ Padrão: vivos.txt]{Fore.CYAN}: ").strip()
            filename = filename_input if filename_input else "vivos.txt"
            
            filepath = filename
            print(f"\n{Fore.CYAN}--- Local de Salvamento ---")
            if os.path.exists('/data/data/com.termux'):
                download_dir = '/sdcard/Download'
                if os.path.exists(download_dir) and os.access(download_dir, os.W_OK):
                    filepath = os.path.join(download_dir, filename)
                    print(f"{Fore.GREEN}[+] Sucesso: {Fore.WHITE}Será salvo na pasta de Downloads!")
                else:
                    print(f"{Fore.YELLOW}[!] Aviso: {Fore.WHITE}Salvando na pasta interna do sistema.")
            else:
                print(f"{Fore.GREEN}[+] Sucesso: {Fore.WHITE}Salvando na pasta atual (VPS/Linux).")
            
            ips_to_test = generate_ips(base_ip)
            testes_totais = []
            for ip in ips_to_test:
                for port in portas: testes_totais.append((ip, port))
            
            total = len(testes_totais)
            print(f"\n{Fore.YELLOW}[*] Gerados {len(ips_to_test)} IPs válidos!")
            print(f"{Fore.YELLOW}[*] Iniciando {total} testes com {max_threads} Threads...\n")
            print(f"{Fore.RED}[!] DICA: Pressione CTRL+C a qualquer momento para cancelar e salvar.{Fore.WHITE}\n")
            
            working_proxies = []
            concluidos = 0
            encontrados = 0
            
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
                        
                        if concluidos % 15 == 0 or concluidos == total:
                            progresso = f"\r{Fore.CYAN}[Progresso: {concluidos}/{total}] {Fore.WHITE}Testando: {ip}:{port} | {Fore.GREEN}Encontrados: {encontrados}\033[K"
                            sys.stdout.write(progresso)
                            sys.stdout.flush()
            except KeyboardInterrupt:
                sys.stdout.write(f"\n\n{Fore.RED}[!] Scanner interrompido! Salvando encontrados...{Fore.WHITE}")
                executor.shutdown(wait=False, cancel_futures=True) if sys.version_info >= (3, 9) else executor.shutdown(wait=False)
            
            print("\n")
            if working_proxies:
                with open(filepath, 'a', encoding='utf-8') as f:
                    for p in working_proxies: f.write(p + "\n")
                print(f"{Fore.GREEN}[+] Busca concluída! {len(working_proxies)} proxies salvos com sucesso.")
                print(f"{Fore.YELLOW}[*] Arquivo: {Fore.WHITE}{filepath}")
            else:
                print(f"{Fore.RED}[-] Nenhum proxy funcionando encontrado.")
            
            input(f"\n{Fore.WHITE}Pressione ENTER para voltar ao menu...")
            
        elif choice == '2':
            run_cf_checker()
            
        elif choice == '3':
            show_banner()
            print(f"{Fore.CYAN}--- Como funciona a ferramenta ---")
            print(f"\n{Fore.YELLOW}1. Proxy Scanner:")
            print(f"{Fore.WHITE}Ele varre blocos inteiros da internet procurando por 'portas abertas'.")
            print(f"Quando acha uma, ele testa a conexão no Google. Se passar direto,")
            print(f"significa que é um proxy público e anônimo. Ele mede o ping e a localização.")
            
            print(f"\n{Fore.YELLOW}2. Cloudflare Checker:")
            print(f"{Fore.WHITE}Ter um proxy 'vivo' não garante que ele acesse sites protegidos.")
            print(f"O Cloudflare (e outros firewalls) barram IPs com reputação ruim.")
            print(f"Esta opção pega os seus proxies vivos e testa um por um contra o site")
            print(f"que você quer acessar, filtrando apenas a 'Elite' que burla o bloqueio.")
            print(f"\n{Fore.GREEN}Desenvolvido exclusivamente por Digital Apps©")
            input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")
            
        elif choice == '4':
            update_system()
            
        elif choice == '5':
            print(f"\n{Fore.RED}Saindo... Até logo!")
            sys.exit()
        else:
            print(f"{Fore.RED}Opção inválida.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Script fechado pelo usuário.")
        sys.exit()
