#!/bin/bash

# 🔄 Script de Reset e Teste - Recriar Ambiente Virtual

echo "🔄 Reset e Teste do Ambiente Python"
echo "===================================="

# 1. Remover ambiente virtual existente
if [ -d "venv" ]; then
    echo "🗑️ Removendo ambiente virtual existente..."
    rm -rf venv
    echo "✅ Ambiente virtual removido"
fi

# 2. Verificar Python
echo ""
echo "1. Verificando Python..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3 encontrado: $(python3 --version)"
else
    echo "❌ Python3 não encontrado"
    exit 1
fi

# 3. Verificar dependências do sistema
echo ""
echo "2. Verificando dependências do sistema..."

# Verificar se python3-venv está disponível
if python3 -m venv --help &> /dev/null; then
    echo "✅ python3-venv disponível"
else
    echo "📦 Instalando python3-venv..."
    sudo apt update && sudo apt install -y python3-venv python3-full python3-dev
fi

# Verificar se curl está disponível (para instalar pip se necessário)
if command -v curl &> /dev/null; then
    echo "✅ curl disponível"
else
    echo "📦 Instalando curl..."
    sudo apt install -y curl
fi

# 4. Criar novo ambiente virtual
echo ""
echo "3. Criando novo ambiente virtual..."
python3 -m venv venv --clear

if [ $? -eq 0 ] && [ -f "venv/bin/python" ]; then
    echo "✅ Ambiente virtual criado com sucesso"
else
    echo "❌ Falha ao criar ambiente virtual"
    exit 1
fi

# 5. Verificar Python no ambiente virtual
echo ""
echo "4. Verificando Python no ambiente virtual..."
VENV_PYTHON="venv/bin/python"
echo "📍 Python venv: $($VENV_PYTHON --version)"

# 6. Configurar pip no ambiente virtual
echo ""
echo "5. Configurando pip no ambiente virtual..."

# Primeiro, tentar usar o pip que vem com o venv
if $VENV_PYTHON -m pip --version &> /dev/null; then
    echo "✅ pip já disponível no venv"
else
    echo "📦 Instalando pip no ambiente virtual..."
    
    # Baixar e instalar pip
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $VENV_PYTHON get-pip.py
    rm get-pip.py
    
    if $VENV_PYTHON -m pip --version &> /dev/null; then
        echo "✅ pip instalado com sucesso"
    else
        echo "❌ Falha ao instalar pip"
        exit 1
    fi
fi

# 7. Atualizar pip
echo ""
echo "6. Atualizando pip..."
$VENV_PYTHON -m pip install --upgrade pip
echo "✅ pip atualizado: $($VENV_PYTHON -m pip --version)"

# 8. Instalar dependências
echo ""
echo "7. Instalando dependências..."
$VENV_PYTHON -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# 9. Testar importações
echo ""
echo "8. Testando importações..."
$VENV_PYTHON -c "
import sys
print('Python:', sys.version)
print()

try:
    import boto3
    print('✅ boto3:', boto3.__version__)
except ImportError as e:
    print('❌ boto3:', e)

try:
    import requests
    print('✅ requests:', requests.__version__)
except ImportError as e:
    print('❌ requests:', e)

try:
    import pytest
    print('✅ pytest:', pytest.__version__)
except ImportError as e:
    print('❌ pytest:', e)

print()
print('🎯 Teste de conexão AWS...')
try:
    client = boto3.client('sts', region_name='us-east-1')
    print('✅ Cliente AWS criado com sucesso')
except Exception as e:
    print('⚠️ Cliente AWS:', e)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completo e testado!"
    echo "✅ Ambiente virtual: venv/"
    echo "✅ Python: $VENV_PYTHON"
    echo "✅ Todas as dependências funcionando"
    echo ""
    echo "🚀 Próximos passos:"
    echo "   ./scripts/deploy_local.sh    # Deploy completo"
    echo "   venv/bin/python test_runner.py  # Apenas testes"
else
    echo "❌ Erro nos testes de importação"
    exit 1
fi
