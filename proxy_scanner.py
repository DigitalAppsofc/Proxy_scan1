import os
import sys
import time
import random
import requests
import socket
import concurrent.futures
from colorama import init, Fore, Style

# Inicializa as cores para funcionar em qualquer terminal
init(autoreset=True)

# Configurações da Ferramenta
VERSION = "1.1"
# URL RAW do seu GitHub onde o código atualizado ficará hospedado
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
    """Busca o país do IP usando uma API gratuita"""
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        if res['status'] == 'success':
            return res['country']
    except:
        pass
    return "Desconhecido"

def test_proxy(ip, port, proxy_type, timeout=5):
    """Testa se o proxy está funcionando, retorna MS e protocolo exato"""
    start_time = time.time()
    
    protocols_to_test = []
    if proxy_type in ['1', '2']: # All ou HTTP
        protocols_to_test.append(('HTTP', f"http://{ip}:{port}"))
    if proxy_type in ['1', '3']: # All ou SOCKS
        protocols_to_test.append(('SOCKS5', f"socks5://{ip}:{port}"))
        protocols_to_test.append(('SOCKS4', f"socks4://{ip}:{port}"))

    for proto_name, proxy_url in protocols_to_test:
        proxies = {"http": proxy_url, "https": proxy_url}
        try:
            res = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
            if res.status_code == 200:
                ms = int((time.time() - start_time) * 1000)
                country = get_country(ip)
                return True, proto_name, ms, country
        except:
            continue
            
    return False, None, 0, None

def generate_random_base():
    """Gera uma base de IP aleatória e válida na internet"""
    while True:
        oct1 = random.randint(1, 223)
        # Pula IPs de rede local/privada e loopback
        if oct1 in [10, 127, 169, 172, 192]: 
            continue
        oct2 = random.randint(0, 255)
        oct3 = random.randint(0, 255)
        return f"{oct1}.{oct2}.{oct3}"

def generate_ips(base_ip):
    """Gera uma lista de 256 IPs baseada nos primeiros octetos"""
    parts = base_ip.strip().split('.')
    if len(parts) >= 4:
        return [base_ip]
    
    base = '.'.join(parts[:3])
    ips = []
    for i in range(256):
        ips.append(f"{base}.{i}")
    return ips

def update_system():
    """Baixa a nova versão do script e substitui a atual"""
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
            print(f"Exemplo de base: {Fore.GREEN}190.32.15 {Fore.WHITE}(Gera de .0 até .255)")
            print(f"Digite {Fore.YELLOW}R{Fore.WHITE} para gerar uma base aleatória válida.")
            
            base_input = input("Digite a base do IP ou R: ").strip()
            if base_input.upper() == 'R':
                base_ip = generate_random_base()
                print(f"{Fore.GREEN}[+] Base gerada automaticamente: {base_ip}")
            else:
                base_ip = base_input

            print(f"\n{Fore.CYAN}--- Portas para Teste ---")
            print(f"Digite uma porta {Fore.WHITE}(ex: 8080){Fore.CYAN}, várias {Fore.WHITE}(80,8080,3128){Fore.CYAN}")
            print(f"Ou digite {Fore.YELLOW}ALL{Fore.CYAN} para testar as portas proxy mais comuns.")
            
            porta_input = input("Portas: ").strip().lower()
            if porta_input == 'all':
                portas = ['80', '8080', '3128', '1080', '443', '8000', '9090']
                print(f"{Fore.GREEN}[+] Portas selecionadas: {', '.join(portas)}")
            else:
                portas = [p.strip() for p in porta_input.split(',')]
            
            print(f"\n{Fore.CYAN}--- Tipo de Proxy ---")
            print("1 - Todos (HTTP, SOCKS4, SOCKS5)")
            print("2 - Apenas HTTP/HTTPS")
            print("3 - Apenas SOCKS")
            proxy_type = input("Escolha o que deseja salvar (1/2/3): ")
            
            filename = input("\nNome do arquivo para salvar (ex: vivos.txt): ")
            if not filename:
                filename = "vivos.txt"
            
            # Gera a lista de todas as combinações de IP e Porta
            ips_to_test = generate_ips(base_ip)
            testes_totais = []
            for ip in ips_to_test:
                for port in portas:
                    testes_totais.append((ip, port))
            
            total = len(testes_totais)
            print(f"\n{Fore.YELLOW}[*] Iniciando {total} testes com Threads...\n")
            
            working_proxies = []
            concluidos = 0
            encontrados = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                futures = {executor.submit(test_proxy, ip, port, proxy_type): (ip, port) for ip, port in testes_totais}
                
                for future in concurrent.futures.as_completed(futures):
                    ip, port = futures[future]
                    concluidos += 1
                    
                    # Atualiza a linha de progresso dinamicamente (usa \033[K para limpar o resto da linha)
                    progresso = f"\r{Fore.CYAN}[Progresso: {concluidos}/{total}] {Fore.WHITE}Testando: {ip}:{port} | {Fore.GREEN}Encontrados: {encontrados}\033[K"
                    print(progresso, end="", flush=True)
                    
                    try:
                        success, proto, ms, country = future.result()
                        if success:
                            encontrados += 1
                            proxy_str = f"{ip}:{port} | {proto} | {ms}ms | {country}"
                            # Apaga a linha de progresso, imprime o LIVE e volta com a linha de progresso
                            print(f"\r\033[K{Fore.GREEN}[+] LIVE: {proxy_str}")
                            working_proxies.append(proxy_str)
                    except Exception:
                        pass
            
            print("\n") # Quebra de linha final após o loop
            if working_proxies:
                with open(filename, 'a', encoding='utf-8') as f:
                    for p in working_proxies:
                        f.write(p + "\n")
                print(f"{Fore.GREEN}[+] Busca concluída! {len(working_proxies)} proxies salvos em {filename}")
            else:
                print(f"{Fore.RED}[-] Nenhum proxy funcionando encontrado nessa rodada.")
            
            input(f"\n{Fore.WHITE}Pressione ENTER para voltar ao menu...")
            
        elif choice == '2':
            show_banner()
            print(f"{Fore.CYAN}Sobre a ferramenta:")
            print(f"{Fore.WHITE}Proxy Scanner e Checker de alta velocidade usando Multi-Threading.")
            print(f"Funcionalidades: Gerador IP Random, Múltiplas Portas, GeoIP, Ping (ms), Auto-Update.")
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
        print(f"\n{Fore.RED}Script interrompido pelo usuário.")
        sys.exit()
