#!/bin/bash

# 🛡️ Script de Configuração Segura do Ambiente Virtual
# Resolve problemas de "externally-managed-environment" em Ubuntu 22.04+/Python 3.12

set -e  # Para na primeira falha

echo "🛡️ Configuração Segura do Ambiente Virtual"
echo "=========================================="

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

log_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

# 1. Detectar sistema e Python
log_info "Detectando ambiente..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "unknown")
OS_INFO=$(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo "Unknown OS")

echo "📍 Sistema: $OS_INFO"
echo "📍 Python: $PYTHON_VERSION"

# Verificar se é Ubuntu 22.04+ ou Python 3.12+
IS_MODERN_UBUNTU=false
if [[ "$OS_INFO" == *"Ubuntu"* ]]; then
    VERSION=$(echo "$OS_INFO" | grep -o '[0-9][0-9]\.[0-9][0-9]' | head -1)
    if [[ "$VERSION" =~ ^2[2-9]\. ]] || [[ "$VERSION" =~ ^[3-9][0-9]\. ]]; then
        IS_MODERN_UBUNTU=true
        log_warning "Detectado Ubuntu $VERSION - pode ter restrições de pip"
    fi
fi

IS_PYTHON_312_PLUS=false
if [[ "$PYTHON_VERSION" =~ ^3\.1[2-9]$ ]] || [[ "$PYTHON_VERSION" =~ ^3\.[2-9][0-9]$ ]] || [[ "$PYTHON_VERSION" =~ ^[4-9]\. ]]; then
    IS_PYTHON_312_PLUS=true
    log_warning "Detectado Python $PYTHON_VERSION - pode ter restrições de pip"
fi

# 2. Remover ambiente virtual problemático se existir
if [ -d "venv" ]; then
    log_warning "Removendo ambiente virtual existente para recriação segura..."
    rm -rf venv
fi

# 3. Verificar e instalar dependências do sistema necessárias
log_info "Verificando dependências do sistema..."

if [[ "$IS_MODERN_UBUNTU" == true ]] || [[ "$IS_PYTHON_312_PLUS" == true ]]; then
    log_info "Instalando dependências específicas para Ubuntu moderno/Python 3.12+..."
    
    # Lista de pacotes críticos
    PACKAGES=(
        "python$PYTHON_VERSION-venv"
        "python$PYTHON_VERSION-full"
        "python$PYTHON_VERSION-dev"
        "python3-venv"
        "python3-virtualenv"
        "python3-pip"
        "curl"
        "build-essential"
    )
    
    log_info "Atualizando lista de pacotes..."
    sudo apt update
    
    for package in "${PACKAGES[@]}"; do
        if dpkg -s "$package" >/dev/null 2>&1; then
            log_success "$package já instalado"
        else
            log_info "Instalando $package..."
            if sudo apt install -y "$package" 2>/dev/null; then
                log_success "$package instalado"
            else
                log_warning "$package não disponível, continuando..."
            fi
        fi
    done
fi

# 4. Criar ambiente virtual com método mais robusto
log_info "Criando ambiente virtual robusto..."

# Método 1: python3 -m venv (preferido)
if python3 -m venv venv 2>/dev/null; then
    log_success "Ambiente virtual criado com 'python3 -m venv'"
    VENV_METHOD="venv"
# Método 2: virtualenv (fallback)
elif command -v virtualenv >/dev/null && virtualenv venv 2>/dev/null; then
    log_success "Ambiente virtual criado com 'virtualenv'"
    VENV_METHOD="virtualenv"
# Método 3: python -m virtualenv
elif python3 -m virtualenv venv 2>/dev/null; then
    log_success "Ambiente virtual criado com 'python3 -m virtualenv'"
    VENV_METHOD="python-virtualenv"
else
    log_error "Falha ao criar ambiente virtual com todos os métodos"
    log_error "Execute: sudo apt install python3-venv python3-virtualenv"
    exit 1
fi

# 5. Verificar estrutura do ambiente virtual
VENV_PYTHON="venv/bin/python"
VENV_PIP="venv/bin/pip"

if [ ! -f "$VENV_PYTHON" ]; then
    log_error "Ambiente virtual criado mas python não encontrado em venv/bin/"
    exit 1
fi

log_success "Ambiente virtual estrutura verificada"
echo "📍 Python do venv: $($VENV_PYTHON --version)"

# 6. Configurar pip no ambiente virtual (método robusto)
log_info "Configurando pip no ambiente virtual..."

# Primeiro, tentar usar pip interno
if $VENV_PYTHON -m pip --version >/dev/null 2>&1; then
    log_success "pip já funcional no ambiente virtual"
else
    log_warning "pip não encontrado, instalando manualmente..."
    
    # Baixar e instalar get-pip.py
    if curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py; then
        log_info "get-pip.py baixado, instalando..."
        if $VENV_PYTHON get-pip.py; then
            log_success "pip instalado via get-pip.py"
        else
            log_error "Falha ao instalar pip via get-pip.py"
            exit 1
        fi
        rm -f get-pip.py
    else
        log_error "Falha ao baixar get-pip.py"
        exit 1
    fi
fi

# 7. Atualizar pip para versão mais recente
log_info "Atualizando pip..."
$VENV_PYTHON -m pip install --upgrade pip >/dev/null 2>&1
log_success "pip atualizado: $($VENV_PYTHON -m pip --version)"

# 8. Instalar dependências usando método seguro
log_info "Instalando dependências do projeto de forma segura..."

if [ ! -f "requirements.txt" ]; then
    log_error "requirements.txt não encontrado"
    exit 1
fi

# Usar python -m pip para evitar problemas de PATH
if $VENV_PYTHON -m pip install -r requirements.txt; then
    log_success "Todas as dependências instaladas com sucesso"
else
    log_error "Falha ao instalar dependências"
    exit 1
fi

# 9. Teste de verificação final
log_info "Executando teste de verificação final..."

$VENV_PYTHON -c "
import sys
import os
print('🐍 Verificação do Ambiente Virtual')
print('=' * 40)
print(f'📍 Python: {sys.version}')
print(f'📍 Executável: {sys.executable}')
print(f'📍 Prefixo: {sys.prefix}')
print()

# Verificar se está realmente no venv
expected_prefix = os.path.abspath('venv')
if expected_prefix in sys.prefix:
    print('✅ Executando dentro do ambiente virtual')
else:
    print('❌ NÃO está executando dentro do ambiente virtual')
    print(f'   Esperado: {expected_prefix}')
    print(f'   Atual: {sys.prefix}')
    exit(1)

# Testar importações críticas
critical_modules = ['boto3', 'requests', 'pytest', 'flake8']
for module in critical_modules:
    try:
        __import__(module)
        print(f'✅ {module}: importado com sucesso')
    except ImportError:
        print(f'❌ {module}: falha na importação')
        exit(1)

print()
print('🎉 Ambiente virtual configurado e funcionando perfeitamente!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 CONFIGURAÇÃO SEGURA CONCLUÍDA!"
    echo "================================="
    echo "✅ Método usado: $VENV_METHOD"
    echo "✅ Python do venv: $VENV_PYTHON"
    echo "✅ pip do venv: $($VENV_PYTHON -m pip --version)"
    echo "✅ Dependências: Todas instaladas e testadas"
    echo ""
    echo "🚀 Comandos recomendados:"
    echo "   $VENV_PYTHON test_runner.py --quick"
    echo "   ./scripts/deploy_local.sh"
    echo ""
    echo "💡 Para ativar manualmente o ambiente:"
    echo "   source venv/bin/activate"
else
    log_error "Erro na verificação final"
    exit 1
fi
