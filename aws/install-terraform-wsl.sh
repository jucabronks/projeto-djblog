#!/bin/bash

# =============================================================================
# INSTALAR TERRAFORM NO WSL/LINUX
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

print_header "Instalando Terraform no WSL/Linux..."

# Verificar se já está instalado
if command -v terraform &> /dev/null; then
    TERRAFORM_VERSION=$(terraform version -json | jq -r '.terraform_version')
    print_status "Terraform já está instalado: $TERRAFORM_VERSION"
    
    # Verificar se a versão é compatível
    REQUIRED_VERSION="1.12.0"
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$TERRAFORM_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        print_status "Versão compatível! ✅"
        exit 0
    else
        print_warning "Versão antiga detectada. Atualizando..."
    fi
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
    sudo apt-get install -y wget unzip jq
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Amazon Linux"* ]]; then
    sudo yum update -y
    sudo yum install -y wget unzip jq
elif [[ "$OS" == *"Fedora"* ]]; then
    sudo dnf update -y
    sudo dnf install -y wget unzip jq
else
    print_warning "Distribuição não reconhecida. Tentando instalar com apt-get..."
    sudo apt-get update
    sudo apt-get install -y wget unzip jq
fi

# Baixar Terraform
print_info "Baixando Terraform..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Obter a versão mais recente
LATEST_VERSION=$(curl -s https://checkpoint-api.hashicorp.com/v1/check/terraform | jq -r '.current_version')

print_info "Versão mais recente: $LATEST_VERSION"

# Baixar Terraform
curl -LO "https://releases.hashicorp.com/terraform/${LATEST_VERSION}/terraform_${LATEST_VERSION}_linux_amd64.zip"

# Verificar se o download foi bem-sucedido
if [ ! -f "terraform_${LATEST_VERSION}_linux_amd64.zip" ]; then
    print_error "Falha ao baixar Terraform"
    exit 1
fi

print_status "Download concluído"

# Extrair e instalar
print_info "Extraindo e instalando Terraform..."
unzip -q "terraform_${LATEST_VERSION}_linux_amd64.zip"

# Mover para /usr/local/bin
sudo mv terraform /usr/local/bin/

# Verificar instalação
if command -v terraform &> /dev/null; then
    INSTALLED_VERSION=$(terraform version -json | jq -r '.terraform_version')
    print_status "Terraform instalado com sucesso: $INSTALLED_VERSION"
else
    print_error "Falha na instalação do Terraform"
    exit 1
fi

# Limpar arquivos temporários
cd - > /dev/null
rm -rf "$TEMP_DIR"

echo ""
print_header "Instalação concluída!"
echo ""
print_info "Para testar o Terraform:"
echo "   terraform version"
echo "   terraform --help"
echo ""
print_info "Próximos passos:"
echo "   1. Configure AWS CLI: ./install-aws-cli-wsl.sh"
echo "   2. Configure permissões: ./setup-aws-permissions-wsl.sh"
echo "   3. Configure backend: ./configure-terraform-backend-wsl.sh" 