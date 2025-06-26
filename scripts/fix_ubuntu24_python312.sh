#!/bin/bash

# 🔧 Script de Correção para Ubuntu 24.04 + Python 3.12

echo "🔧 Correção Específica - Ubuntu 24.04 + Python 3.12"
echo "===================================================="

# 1. Detectar sistema
echo "1. Detectando sistema..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
OS_VERSION=$(lsb_release -rs 2>/dev/null || echo "Unknown")
echo "📍 Python: $PYTHON_VERSION"
echo "📍 Ubuntu: $OS_VERSION"

# 2. Remover ambiente virtual problemático
if [ -d "venv" ]; then
    echo ""
    echo "2. Removendo ambiente virtual problemático..."
    rm -rf venv
    echo "✅ Ambiente virtual removido"
fi

# 3. Instalar dependências corretas para Python 3.12
echo ""
echo "3. Instalando dependências específicas do Python $PYTHON_VERSION..."

# Lista de pacotes a instalar
PACKAGES=(
    "python$PYTHON_VERSION-venv"
    "python$PYTHON_VERSION-full" 
    "python$PYTHON_VERSION-dev"
    "python3-virtualenv"
    "curl"
    "build-essential"
)

echo "📦 Atualizando lista de pacotes..."
sudo apt update

echo "📦 Instalando pacotes necessários..."
for package in "${PACKAGES[@]}"; do
    echo "   - Instalando $package..."
    if sudo apt install -y "$package"; then
        echo "     ✅ $package instalado"
    else
        echo "     ⚠️ $package não disponível, continuando..."
    fi
done

# 4. Verificar se venv funciona agora
echo ""
echo "4. Testando criação de ambiente virtual..."

if python3 -m venv test_venv; then
    echo "✅ python3 -m venv funciona"
    rm -rf test_venv
else
    echo "❌ python3 -m venv ainda não funciona"
    echo "🔧 Tentando com virtualenv..."
    
    if virtualenv test_venv; then
        echo "✅ virtualenv funciona"
        rm -rf test_venv
    else
        echo "❌ Nenhum método funciona"
        exit 1
    fi
fi

# 5. Criar ambiente virtual real
echo ""
echo "5. Criando ambiente virtual definitivo..."

# Tentar venv primeiro
if python3 -m venv venv; then
    echo "✅ Ambiente virtual criado com venv"
    VENV_METHOD="venv"
elif virtualenv venv; then
    echo "✅ Ambiente virtual criado com virtualenv"
    VENV_METHOD="virtualenv"
else
    echo "❌ Falha ao criar ambiente virtual"
    exit 1
fi

# 6. Verificar estrutura do ambiente virtual
echo ""
echo "6. Verificando estrutura do ambiente virtual..."

VENV_PYTHON="venv/bin/python"
if [ -f "$VENV_PYTHON" ]; then
    echo "✅ venv/bin/python existe"
    echo "📍 Versão: $($VENV_PYTHON --version)"
else
    echo "❌ venv/bin/python não existe"
    exit 1
fi

# 7. Configurar pip no ambiente virtual
echo ""
echo "7. Configurando pip..."

# Primeiro, verificar se pip já existe
if $VENV_PYTHON -m pip --version &> /dev/null; then
    echo "✅ pip já disponível no ambiente virtual"
else
    echo "📦 Instalando pip no ambiente virtual..."
    
    # Baixar get-pip.py
    if curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py; then
        echo "✅ get-pip.py baixado"
        
        # Instalar pip
        if $VENV_PYTHON get-pip.py; then
            echo "✅ pip instalado com sucesso"
        else
            echo "❌ Falha ao instalar pip"
            exit 1
        fi
        
        # Limpar arquivo temporário
        rm get-pip.py
    else
        echo "❌ Falha ao baixar get-pip.py"
        exit 1
    fi
fi

# 8. Atualizar pip
echo ""
echo "8. Atualizando pip..."
$VENV_PYTHON -m pip install --upgrade pip
echo "✅ pip atualizado: $($VENV_PYTHON -m pip --version)"

# 9. Instalar dependências
echo ""
echo "9. Instalando dependências do projeto..."
if $VENV_PYTHON -m pip install -r requirements.txt; then
    echo "✅ Todas as dependências instaladas"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# 10. Teste final
echo ""
echo "10. Teste final de importações..."
$VENV_PYTHON -c "
import sys
print('🐍 Python:', sys.version)
print('📍 Localização:', sys.executable)
print()

try:
    import boto3
    print('✅ boto3:', boto3.__version__)
except ImportError as e:
    print('❌ boto3:', e)
    exit(1)

try:
    import requests
    print('✅ requests:', requests.__version__)
except ImportError as e:
    print('❌ requests:', e)
    exit(1)

try:
    import pytest
    print('✅ pytest:', pytest.__version__)
except ImportError as e:
    print('❌ pytest:', e)
    exit(1)

print()
print('🎉 Todas as dependências funcionando!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!"
    echo "=================================="
    echo "✅ Ambiente virtual: venv/"
    echo "✅ Método usado: $VENV_METHOD"
    echo "✅ Python: $VENV_PYTHON"
    echo "✅ Dependências: Todas instaladas"
    echo ""
    echo "🚀 Agora você pode executar:"
    echo "   ./scripts/deploy_local.sh"
    echo "   $VENV_PYTHON test_runner.py"
else
    echo "❌ Erro no teste final"
    exit 1
fi
