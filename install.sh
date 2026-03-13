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

clear

echo -e "${CYAN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${GREEN}       INSTALADOR DO PROXY SCANNER AVANÇADO         ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════╝${NC}"
echo -e "                ${YELLOW}Criado por: ${WHITE}@Digital_Apps${NC}\n"

echo -e "${CYAN}[ INFORMAÇÕES DA FERRAMENTA ]${NC}"
echo -e "${WHITE}Este instalador irá preparar o seu sistema (Termux/VPS)${NC}"
echo -e " ${GREEN}1.${WHITE} Atualização dos repositórios do sistema."
echo -e " ${GREEN}2.${WHITE} Instalação do Python 3 e gerenciador PIP."
echo -e " ${GREEN}3.${WHITE} Download e instalação das bibliotecas base."
echo -e " ${GREEN}4.${WHITE} Download do código-fonte do Scanner."
echo -e " ${GREEN}5.${WHITE} Criação do comando de sistema 'px'."

read -p "$(echo -e "\n${GREEN}Pressione ENTER para iniciar a instalação... ${NC}")"

if command -v pkg &> /dev/null; then
    # É Termux
    UPDATE_CMD="pkg update -y"
    INSTALL_CMD="pkg install -y"
    BIN_DIR="$PREFIX/bin"
elif command -v apt &> /dev/null; then
    # É Debian/Ubuntu/VPS
    UPDATE_CMD="apt-get update -y"
    INSTALL_CMD="apt-get install -y"
    BIN_DIR="/usr/local/bin"
else
    echo -e "\n${RED}[-] Sistema não reconhecido ou incompatível.${NC}"
    exit 1
fi

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

echo -ne "${WHITE}[1/5] Atualizando repositórios do sistema...${NC}"
$UPDATE_CMD > /dev/null 2>&1 &
spinner $!
echo -e "\r${GREEN}[1/5] Repositórios atualizados com sucesso!      ${NC}"

echo -ne "${WHITE}[2/5] Instalando Python3, PIP, cURL e Wget...${NC}"
$INSTALL_CMD python3 python3-pip curl wget > /dev/null 2>&1 &
spinner $!
echo -e "\r${GREEN}[2/5] Pacotes de sistema instalados com sucesso! ${NC}"

echo -ne "${WHITE}[3/5] Instalando bibliotecas do Python...    ${NC}"
pip install requests "requests[socks]" colorama --break-system-packages > /dev/null 2>&1 || pip install requests "requests[socks]" colorama > /dev/null 2>&1 &
spinner $!
echo -e "\r${GREEN}[3/5] Bibliotecas do Python instaladas!          ${NC}"

echo -ne "${WHITE}[4/5] Baixando o código fonte do Scanner...  ${NC}"
cd ~ 
curl -sL https://raw.githubusercontent.com/DigitalAppsofc/Proxy_scan1/refs/heads/main/proxy_scanner.py -o proxy_scanner.py &
spinner $!
echo -e "\r${GREEN}[4/5] Código fonte baixado com sucesso!          ${NC}"

echo -ne "${WHITE}[5/5] Configurando comando global 'px'...    ${NC}"
# Cria um script executável nativo direto na pasta raiz do sistema (bin)
echo '#!/bin/bash' > $BIN_DIR/px
echo 'cd ~ && python3 proxy_scanner.py' >> $BIN_DIR/px
chmod +x $BIN_DIR/px
echo -e "\r${GREEN}[5/5] Comando global configurado com sucesso!    ${NC}"

echo -e "\n${CYAN}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}      INSTALAÇÃO CONCLUÍDA COM SUCESSO!             ${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}O seu ambiente está pronto para rodar a ferramenta!${NC}"
echo -e "\nPara abrir a ferramenta agora e das próximas vezes, digite apenas:"
echo -e "${YELLOW}px${NC}"
echo -e "\n${GREEN}Obrigado por usar os sistemas da @Digital_Apps!${NC}\n"

rm install.sh 2>/dev/null
