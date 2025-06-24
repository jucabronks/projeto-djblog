#!/bin/bash

# =============================================================================
# INSTALAR AWS CLI NO WSL/LINUX
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}📋 $1${NC}"
}

print_header() {
    echo -e "${WHITE}🚀 $1${NC}"
}

print_header "Instalando AWS CLI no WSL/Linux..."

# Verificar se já está instalado
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version)
    print_status "AWS CLI já está instalado: $AWS_VERSION"
    print_info "Para atualizar, remova a versão atual primeiro"
    exit 0
fi

# Detectar distribuição Linux
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    print_error "Não foi possível detectar a distribuição Linux"
    exit 1
fi

print_info "Distribuição detectada: $OS $VER"

# Instalar dependências
print_info "Instalando dependências..."

if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    sudo apt-get update
    sudo apt-get install -y unzip curl
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Amazon Linux"* ]]; then
    sudo yum update -y
    sudo yum install -y unzip curl
elif [[ "$OS" == *"Fedora"* ]]; then
    sudo dnf update -y
    sudo dnf install -y unzip curl
else
    print_warning "Distribuição não reconhecida. Tentando instalar com apt-get..."
    sudo apt-get update
    sudo apt-get install -y unzip curl
fi

# Baixar AWS CLI
print_info "Baixando AWS CLI..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Verificar se o download foi bem-sucedido
if [ ! -f "awscliv2.zip" ]; then
    print_error "Falha ao baixar AWS CLI"
    exit 1
fi

print_status "Download concluído"

# Extrair e instalar
print_info "Extraindo e instalando AWS CLI..."
unzip -q awscliv2.zip

# Verificar se há uma instalação existente
if command -v aws &> /dev/null; then
    print_warning "Removendo instalação existente..."
    sudo ./aws/install --update
else
    sudo ./aws/install
fi

# Limpar arquivos temporários
cd - > /dev/null
rm -rf "$TEMP_DIR"

# Verificar instalação
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version)
    print_status "AWS CLI instalado com sucesso: $AWS_VERSION"
else
    print_error "Falha na instalação do AWS CLI"
    exit 1
fi

echo ""
print_header "Instalação concluída!"
echo ""
print_info "Próximos passos:"
echo "   1. Configure suas credenciais: aws configure"
echo "   2. Execute: ./setup-aws-permissions-wsl.sh"
echo "   3. Execute: ./configure-terraform-backend-wsl.sh"
echo ""
print_info "Para configurar credenciais AWS:"
echo "   aws configure"
echo "   # AWS Access Key ID: [sua-access-key]"
echo "   # AWS Secret Access Key: [sua-secret-key]"
echo "   # Default region name: us-east-1"
echo "   # Default output format: json" 