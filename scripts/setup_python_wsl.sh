#!/bin/bash
# Script para configurar Python no WSL/Linux

echo "🐍 Configuração Python para WSL/Linux"
echo "======================================"

# Detectar distribuição
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    echo "Sistema detectado: $OS"
else
    echo "Sistema não detectado"
    exit 1
fi

# Função para logs coloridos
log_info() {
    echo -e "\033[36m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

log_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

# Verificar se Python já está instalado
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    log_success "Python já instalado: $PYTHON_VERSION"
    
    # Verificar pip
    if command -v pip3 &> /dev/null; then
        log_success "pip3 já instalado"
    else
        log_info "Instalando pip3..."
        case "$OS" in
            *Ubuntu*|*Debian*)
                sudo apt update
                sudo apt install -y python3-pip
                ;;
            *CentOS*|*Red Hat*|*Amazon Linux*)
                sudo yum install -y python3-pip
                ;;
            *)
                log_error "Distribuição não suportada para instalação automática do pip"
                exit 1
                ;;
        esac
    fi
else
    log_info "Python3 não encontrado. Instalando..."
    
    case "$OS" in
        *Ubuntu*|*Debian*)
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
            ;;
        *CentOS*|*Red Hat*|*Amazon Linux*)
            sudo yum install -y python3 python3-pip
            ;;
        *)
            log_error "Distribuição não suportada para instalação automática"
            log_info "Instale Python 3.8+ manualmente:"
            log_info "  Ubuntu/Debian: sudo apt install python3 python3-pip"
            log_info "  CentOS/RHEL: sudo yum install python3 python3-pip"
            exit 1
            ;;
    esac
fi

# Verificar versão mínima
PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    log_success "✅ Python $PYTHON_VERSION é compatível (>= $REQUIRED_VERSION)"
else
    log_error "❌ Python $PYTHON_VERSION é muito antigo. Requer >= $REQUIRED_VERSION"
    exit 1
fi

# Criar alias se necessário
if ! command -v python &> /dev/null; then
    log_info "Criando alias 'python' para 'python3'..."
    echo "alias python=python3" >> ~/.bashrc
    echo "alias pip=pip3" >> ~/.bashrc
    log_info "Alias criado! Execute: source ~/.bashrc"
fi

# Instalar dependências do projeto
if [ -f "requirements.txt" ]; then
    log_info "Instalando dependências do projeto..."
    python3 -m pip install --user -r requirements.txt
    log_success "Dependências instaladas!"
else
    log_warning "Arquivo requirements.txt não encontrado"
fi

echo ""
log_success "🎉 Configuração do Python concluída!"
echo "Para usar o deploy local, execute:"
echo "  ./scripts/deploy_local.sh"
echo ""
echo "Se houver problemas com o alias, execute primeiro:"
echo "  source ~/.bashrc"
