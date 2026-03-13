import os
import sys
import time
import random
import requests
import urllib3
import concurrent.futures
from colorama import init, Fore, Style

# Desativa avisos de conexões inseguras que poluem o terminal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

# Configurações da Ferramenta
VERSION = "1.5"
UPDATE_URL = "https://raw.githubusercontent.com/DigitalAppsofc/Proxy_scan1/refs/heads/main/proxy_scanner.py" 

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    banner = f"""{Fore.CYAN}{Style.BRIGHT}
  ____  _       _ _        _        _                 
 |  _ \(_)     (_) |      | |      | |                
 | | | |_  __ _ _| |_ __ _| |   /  \ |_ __  _ __  ___ 
 | | | | |/ _` | | __/ _` | |  / /\ \| '_ \| '_ \/ __|
 | |/ /| | (_| | | || (_| | | / ____ \ |_) | |_) \__ \\
 |___/ |_|\__, |_|\__\__,_|_|/_/    \_\ .__/| .__/|___/
           __/ |                      | |   | |       
          |___/                       |_|   |_|       
    {Fore.YELLOW}Proxy Scanner Avançado - Versão {VERSION}
    {Fore.GREEN}Criado por Digital Apps©
    """
    print(banner)

def get_country(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        if res['status'] == 'success':
            return res['country']
    except:
        pass
    return "Desconhecido"

def test_proxy(ip, port, proxy_type, timeout_val):
    start_time = time.time()
    
    protocols_to_test = []
    if proxy_type in ['1', '2']: 
        protocols_to_test.append(('HTTP', f"http://{ip}:{port}"))
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
        except:
            pass
            
        try:
            res2 = requests.get("http://example.com", proxies=proxies, timeout=timeout_val, verify=False)
            if res2.status_code == 200:
                ms = int((time.time() - start_time) * 1000)
                return True, proto_name, ms, get_country(ip)
        except:
            continue
            
    return False, None, 0, None

def generate_random_base():
    while True:
        oct1 = random.randint(1, 223)
        if oct1 in [10, 127, 169, 172, 192]: 
            continue
        oct2 = random.randint(0, 255)
        oct3 = random.randint(0, 255)
        return f"{oct1}.{oct2}.{oct3}"

def generate_ips(base_ip):
    parts = [p for p in base_ip.strip().split('.') if p] 
    ips = []
    
    if len(parts) >= 4:
        return ['.'.join(parts[:4])]
    elif len(parts) == 3:
        base = '.'.join(parts)
        for i in range(256):
            ips.append(f"{base}.{i}")
    elif len(parts) == 2:
        base = '.'.join(parts)
        for i in range(256):
            for j in range(256):
                ips.append(f"{base}.{i}.{j}")
    elif len(parts) == 1:
        base = f"{parts[0]}.0"
        for i in range(256):
            for j in range(256):
                ips.append(f"{base}.{i}.{j}")
    return ips

def update_system():
    print(f"\n{Fore.YELLOW}[*] Verificando atualizações online...")
    try:
        response = requests.get(UPDATE_URL, timeout=10)
        if response.status_code == 200:
            new_code = response.text
            if f'VERSION = "{VERSION}"' in new_code:
                print(f"{Fore.GREEN}[+] Você já está na versão mais recente!")
            else:
                print(f"{Fore.CYAN}[+] Nova versão encontrada! Baixando...")
                with open(__file__, 'w', encoding='utf-8') as f:
                    f.write(new_code)
                print(f"{Fore.GREEN}[+] Atualização concluída com sucesso! Reinicie o script.")
                sys.exit()
        else:
            print(f"{Fore.RED}[-] Erro ao acessar o servidor de atualização.")
    except Exception as e:
        print(f"{Fore.RED}[-] Falha na atualização: {e}")
    input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")

def main():
    while True:
        show_banner()
        print(f"{Fore.WHITE}[1] {Fore.CYAN}Iniciar Scanner (Gerar IPs e Testar)")
        print(f"{Fore.WHITE}[2] {Fore.CYAN}Informações da Ferramenta")
        print(f"{Fore.WHITE}[3] {Fore.CYAN}Atualizar Script Online")
        print(f"{Fore.WHITE}[4] {Fore.RED}Sair\n")
        
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
            print(f"Digite uma porta {Fore.WHITE}(ex: 8080){Fore.CYAN}, várias {Fore.WHITE}(80,8080,3128){Fore.CYAN}")
            print(f"Ou dê {Fore.YELLOW}ENTER (ALL){Fore.CYAN} para testar as portas proxy mais comuns.")
            
            porta_input = input("Portas: ").strip().lower()
            if porta_input == 'all' or porta_input == '':
                portas = ['80', '8080', '3128', '1080', '443', '8000', '9090']
                print(f"{Fore.GREEN}[+] Portas selecionadas: {', '.join(portas)}")
            else:
                portas = [p.strip() for p in porta_input.split(',')]
            
            print(f"\n{Fore.CYAN}--- Protocolos e Desempenho ---")
            proxy_type = input(f"Tipo (1=Todos, 2=HTTP, 3=SOCKS) {Fore.WHITE}[Padrão: 1]{Fore.CYAN}: ").strip()
            if not proxy_type: proxy_type = '1'
            
            # NOVAS OPÇÕES DE DESEMPENHO
            threads_input = input(f"Quantidade de Threads (Velocidade) {Fore.WHITE}[Padrão: 200]{Fore.CYAN}: ").strip()
            max_threads = int(threads_input) if threads_input.isdigit() else 200
            
            timeout_input = input(f"Timeout em segundos {Fore.WHITE}[Padrão: 5]{Fore.CYAN}: ").strip()
            timeout_val = int(timeout_input) if timeout_input.isdigit() else 5
            
            filename = input(f"\nNome do arquivo para salvar {Fore.WHITE}[Padrão: vivos.txt]{Fore.CYAN}: ").strip()
            if not filename: filename = "vivos.txt"
            
            ips_to_test = generate_ips(base_ip)
            testes_totais = []
            for ip in ips_to_test:
                for port in portas:
                    testes_totais.append((ip, port))
            
            total = len(testes_totais)
            print(f"\n{Fore.YELLOW}[*] Gerados {len(ips_to_test)} IPs válidos!")
            print(f"{Fore.YELLOW}[*] Iniciando {total} testes com {max_threads} Threads...\n")
            print(f"{Fore.RED}[!] DICA: Pressione CTRL+C a qualquer momento para cancelar e salvar os resultados.{Fore.WHITE}\n")
            
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
                        except Exception:
                            pass
                        
                        # ATUALIZA A TELA APENAS A CADA 20 TESTES (Evita o travamento do terminal)
                        if concluidos % 20 == 0 or concluidos == total:
                            progresso = f"\r{Fore.CYAN}[Progresso: {concluidos}/{total}] {Fore.WHITE}Testados... | {Fore.GREEN}Encontrados: {encontrados}\033[K"
                            sys.stdout.write(progresso)
                            sys.stdout.flush()
                        
            except KeyboardInterrupt:
                sys.stdout.write(f"\n\n{Fore.RED}[!] Scanner interrompido pelo usuário! Salvando os proxies encontrados...{Fore.WHITE}")
                executor.shutdown(wait=False, cancel_futures=True) if sys.version_info >= (3, 9) else executor.shutdown(wait=False)
            
            print("\n")
            if working_proxies:
                with open(filename, 'a', encoding='utf-8') as f:
                    for p in working_proxies:
                        f.write(p + "\n")
                print(f"{Fore.GREEN}[+] Busca concluída ou parada! {len(working_proxies)} proxies salvos em {filename}")
            else:
                print(f"{Fore.RED}[-] Nenhum proxy funcionando encontrado ou salvo.")
            
            input(f"\n{Fore.WHITE}Pressione ENTER para voltar ao menu...")
            
        elif choice == '2':
            show_banner()
            print(f"{Fore.CYAN}Sobre a ferramenta:")
            print(f"{Fore.WHITE}Proxy Scanner e Checker de alta velocidade usando Multi-Threading.")
            print(f"Funcionalidades: Gerador IP Random, Múltiplas Portas, GeoIP, Ping (ms), Auto-Update e Interrupção Segura.")
            print(f"\n{Fore.GREEN}Desenvolvido exclusivamente por Digital Apps©")
            input(f"\n{Fore.WHITE}Pressione ENTER para voltar...")
            
        elif choice == '3':
            update_system()
            
        elif choice == '4':
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
