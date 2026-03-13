import os
import sys
import time
import requests
import socket
import concurrent.futures
from colorama import init, Fore, Style

# Inicializa as cores para funcionar em qualquer terminal
init(autoreset=True)

# Configurações da Ferramenta
VERSION = "1.0"
# URL RAW do seu GitHub onde o código atualizado ficará hospedado
UPDATE_URL = "https://proxy-scan.vercel.app/proxy_scanner.py" 

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
    
    # Monta os dicionários de teste
    protocols_to_test = []
    if proxy_type in ['1', '2']: # All ou HTTP
        protocols_to_test.append(('HTTP', f"http://{ip}:{port}"))
    if proxy_type in ['1', '3']: # All ou SOCKS
        protocols_to_test.append(('SOCKS5', f"socks5://{ip}:{port}"))
        protocols_to_test.append(('SOCKS4', f"socks4://{ip}:{port}"))

    for proto_name, proxy_url in protocols_to_test:
        proxies = {"http": proxy_url, "https": proxy_url}
        try:
            # Testa a conexão
            res = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=timeout)
            if res.status_code == 200:
                ms = int((time.time() - start_time) * 1000)
                country = get_country(ip)
                return True, proto_name, ms, country
        except:
            continue
            
    return False, None, 0, None

def generate_ips(base_ip):
    """Gera uma lista de 256 IPs baseada nos primeiros octetos"""
    # Exemplo: se base_ip for '190.150.32', gera de .0 a .255
    parts = base_ip.strip().split('.')
    if len(parts) >= 4:
        return [base_ip] # É um IP único
    
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
            print(f"Exemplo de base: {Fore.GREEN}190.32.15 {Fore.WHITE}(Irá gerar do 190.32.15.0 até 190.32.15.255)")
            base_ip = input("Digite a base do IP ou um IP completo: ")
            porta = input("Digite a porta (Ex: 80, 8080, 3128, 1080): ")
            
            print(f"\n{Fore.CYAN}--- Tipo de Proxy ---")
            print("1 - Todos (HTTP, SOCKS4, SOCKS5)")
            print("2 - Apenas HTTP/HTTPS")
            print("3 - Apenas SOCKS")
            proxy_type = input("Escolha o que deseja salvar (1/2/3): ")
            
            filename = input("\nNome do arquivo para salvar (ex: vivos.txt): ")
            
            ips_to_test = generate_ips(base_ip)
            print(f"\n{Fore.YELLOW}[*] Foram gerados {len(ips_to_test)} IPs para teste na porta {porta}.")
            print(f"{Fore.YELLOW}[*] Iniciando testes com Threads (isso pode levar alguns minutos)...\n")
            
            working_proxies = []
            
            # Usando ThreadPoolExecutor para testar dezenas de proxies ao mesmo tempo
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
                futures = {executor.submit(test_proxy, ip, porta, proxy_type): ip for ip in ips_to_test}
                
                for future in concurrent.futures.as_completed(futures):
                    ip = futures[future]
                    try:
                        success, proto, ms, country = future.result()
                        if success:
                            proxy_str = f"{ip}:{porta} | {proto} | {ms}ms | {country}"
                            print(f"{Fore.GREEN}[+] LIVE: {proxy_str}")
                            working_proxies.append(proxy_str)
                        else:
                            # Remova o comentário da linha abaixo se quiser ver os erros na tela
                            # print(f"{Fore.RED}[-] DEAD: {ip}:{porta}")
                            pass
                    except Exception as e:
                        pass
            
            if working_proxies:
                with open(filename, 'w', encoding='utf-8') as f:
                    for p in working_proxies:
                        f.write(p + "\n")
                print(f"\n{Fore.GREEN}[+] Busca concluída! {len(working_proxies)} proxies salvos em {filename}")
            else:
                print(f"\n{Fore.RED}[-] Nenhum proxy funcionando encontrado nessa range.")
            
            input(f"\n{Fore.WHITE}Pressione ENTER para voltar ao menu...")
            
        elif choice == '2':
            show_banner()
            print(f"{Fore.CYAN}Sobre a ferramenta:")
            print(f"{Fore.WHITE}Este é um Proxy Scanner e Checker de alta velocidade usando Multi-Threading.")
            print(f"Ele verifica a validade do proxy resolvendo conexões HTTP e SOCKS.")
            print(f"Funcionalidades: GeoIP, Medidor de Ping (ms), Auto-Update e Exportação.")
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
