#!/bin/bash

# ==========================================
# Cores para o Terminal
# ==========================================
CYAN='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
WHITE='\033[1;37m'
NC='\033[0m' # Sem cor

# Limpa a tela
clear

# ==========================================
# Banner e Informações Iniciais
# ==========================================
echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${GREEN}       INSTALADOR DO PROXY SCANNER AVANÇADO         ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo -e "                ${YELLOW}Criado por: ${WHITE}@Digital_Apps${NC}\n"

echo -e "${CYAN}[ INFORMAÇÕES DA FERRAMENTA ]${NC}"
echo -e "${WHITE}Este instalador irá preparar o seu sistema (Termux/VPS)${NC}"
echo -e "${WHITE}para executar o Proxy Scanner sem erros. Ele realiza:${NC}"
echo -e " ${GREEN}1.${WHITE} Atualização dos repositórios do sistema."
echo -e " ${GREEN}2.${WHITE} Instalação do Python 3 e gerenciador PIP."
echo -e " ${GREEN}3.${WHITE} Download e instalação das bibliotecas base."
echo -e " ${GREEN}4.${WHITE} Download do código-fonte do Scanner."

echo -e "\n${CYAN}[ DEPENDÊNCIAS QUE SERÃO INSTALADAS ]${NC}"
echo -e " ${YELLOW}• requests${NC}        -> Para testar as conexões e API GeoIP"
echo -e " ${YELLOW}• requests[socks]${NC} -> Para testar proxies SOCKS4 e SOCKS5"
echo -e " ${YELLOW}• colorama${NC}        -> Para a interface colorida do painel"
echo -e " ${YELLOW}• curl & wget${NC}     -> Para o sistema de atualizações online"
echo -e ""

# Aguarda o usuário confirmar
read -p "$(echo -e ${GREEN}Pressione ENTER para iniciar a instalação... ${NC})"

# ==========================================
# Detector de Sistema (Termux vs Linux/VPS)
# ==========================================
if command -v pkg &> /dev/null; then
    # É Termux
    UPDATE_CMD="pkg update -y"
    INSTALL_CMD="pkg install -y"
elif command -v apt &> /dev/null; then
    # É Debian/Ubuntu/VPS
    UPDATE_CMD="apt-get update -y"
    INSTALL_CMD="apt-get install -y"
else
    echo -e "\n${RED}[-] Sistema não reconhecido ou incompatível.${NC}"
    exit 1
fi

# ==========================================
# Função de Animação de Carregamento (Spinner)
# ==========================================
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " ${YELLOW}[%c]${NC} " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

echo -e "\n${CYAN}Iniciando o processo... por favor, aguarde.${NC}"

# ==========================================
# Etapa 1: Atualizar pacotes
# ==========================================
echo -ne "${WHITE}[1/4] Atualizando repositórios do sistema...${NC}"
$UPDATE_CMD > /dev/null 2>&1 &
spinner $!
echo -e "\r${GREEN}[1/4] Repositórios atualizados com sucesso!      ${NC}"

# ==========================================
# Etapa 2: Instalar pacotes de sistema
# ==========================================
echo -ne "${WHITE}[2/4] Instalando Python3, PIP, cURL e Wget...${NC}"
$INSTALL_CMD python3 python3-pip curl wget > /dev/null 2>&1 &
spinner $!
echo -e "\r${GREEN}[2/4] Pacotes de sistema instalados com sucesso! ${NC}"

# ==========================================
# Etapa 3: Instalar dependências Python
# ==========================================
echo -ne "${WHITE}[3/4] Instalando bibliotecas do Python...    ${NC}"
pip install requests "requests[socks]" colorama --break-system-packages > /dev/null 2>&1 || pip install requests "requests[socks]" colorama > /dev/null 2>&1 &
spinner $!
echo -e "\r${GREEN}[3/4] Bibliotecas do Python instaladas!          ${NC}"

# ==========================================
# Etapa 4: Baixar o Proxy Scanner via Vercel
# ==========================================
echo -ne "${WHITE}[4/4] Baixando o código fonte do Scanner...  ${NC}"
# Usa o curl para baixar do seu link do Vercel silenciosamente e salva como proxy_scanner.py
curl -sL https://proxy-scan.vercel.app/ -o proxy_scanner.py &
spinner $!
echo -e "\r${GREEN}[4/4] Código fonte baixado com sucesso!          ${NC}"

# ==========================================
# Finalização
# ==========================================
echo -e "\n${CYAN}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}      INSTALAÇÃO CONCLUÍDA COM SUCESSO!             ${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}O seu ambiente está pronto para rodar a ferramenta!${NC}"
echo -e "\nPara iniciar o scanner, digite:"
echo -e "${YELLOW}python3 proxy_scanner.py${NC}"
echo -e "\n${GREEN}Obrigado por usar os sistemas da @Digital_Apps!${NC}\n"

# Remove o arquivo de instalador para deixar a pasta limpa (opcional)
rm install.sh
