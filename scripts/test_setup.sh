#!/bin/bash

# 🧪 Script de Teste Rápido - Verificação de Dependências

echo "🔍 Testando Dependências Python"
echo "================================"

# 1. Verificar Python
echo "1. Verificando Python..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3 encontrado: $(python3 --version)"
else
    echo "❌ Python3 não encontrado"
    exit 1
fi

# 2. Verificar pip
echo ""
echo "2. Verificando pip..."
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 encontrado: $(pip3 --version)"
else
    echo "❌ pip3 não encontrado"
    # Tentar instalar
    echo "📦 Instalando pip3..."
    sudo apt update && sudo apt install -y python3-pip
fi

# 3. Criar ambiente virtual
echo ""
echo "3. Criando ambiente virtual..."

# Detectar versão do Python para instalar pacote correto
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "📍 Versão Python detectada: $PYTHON_VERSION"

if [ ! -d "venv" ]; then
    # Verificar se python3-venv está instalado para a versão específica
    if ! python3 -m venv --help &> /dev/null; then
        echo "📦 Instalando python$PYTHON_VERSION-venv..."
        
        # Tentar instalar pacote específico da versão primeiro
        if sudo apt update && sudo apt install -y python$PYTHON_VERSION-venv python$PYTHON_VERSION-full python$PYTHON_VERSION-dev; then
            echo "✅ python$PYTHON_VERSION-venv instalado"
        else
            echo "⚠️ Tentando instalar pacotes genéricos..."
            sudo apt install -y python3-venv python3-full python3-dev
        fi
    fi
    
    # Criar ambiente virtual
    python3 -m venv venv --clear
    
    if [ $? -eq 0 ] && [ -f "venv/bin/python" ]; then
        echo "✅ Ambiente virtual criado"
    else
        echo "❌ Falha ao criar ambiente virtual"
        echo "🔧 Tentando método alternativo..."
        
        # Método alternativo: virtualenv
        if command -v virtualenv &> /dev/null; then
            virtualenv venv
        else
            echo "📦 Instalando virtualenv..."
            sudo apt install -y python3-virtualenv
            virtualenv venv
        fi
        
        if [ ! -f "venv/bin/python" ]; then
            echo "❌ Não foi possível criar ambiente virtual"
            exit 1
        fi
    fi
else
    echo "✅ Ambiente virtual já existe"
fi

# 4. Instalar dependências no ambiente virtual
echo ""
echo "4. Instalando dependências no ambiente virtual..."

# Usar caminho direto para o Python do ambiente virtual
VENV_PYTHON="venv/bin/python"

# Verificar se o ambiente virtual foi criado corretamente
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Ambiente virtual não foi criado corretamente"
    exit 1
fi

# Atualizar pip no ambiente virtual usando python -m pip
echo "📦 Atualizando pip..."
$VENV_PYTHON -m pip install --upgrade pip

# Verificar se pip está funcionando
if ! $VENV_PYTHON -m pip --version &> /dev/null; then
    echo "❌ pip não está funcionando no ambiente virtual"
    echo "🔧 Tentando reinstalar pip..."
    
    # Tentar baixar e instalar pip manualmente
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $VENV_PYTHON get-pip.py
    rm get-pip.py
    
    if ! $VENV_PYTHON -m pip --version &> /dev/null; then
        echo "❌ Falha ao instalar pip"
        exit 1
    fi
fi

# Instalar dependências usando python -m pip
echo "📦 Instalando dependências do requirements.txt..."
$VENV_PYTHON -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso no ambiente virtual"
else
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# 5. Testar importação
echo ""
echo "5. Testando importações no ambiente virtual..."
$VENV_PYTHON -c "
import boto3
import pytest  
import requests
print('✅ Todas as dependências importadas com sucesso!')
print('✅ boto3 versão:', boto3.__version__)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup completo! Agora execute:"
    echo "   ./scripts/deploy_local.sh"
    echo ""
    echo "💡 O ambiente virtual foi criado em 'venv/'"
    echo "💡 Para ativar manualmente: source venv/bin/activate"
    echo "💡 Para usar Python do venv: venv/bin/python"
else
    echo "❌ Erro ao importar dependências"
    exit 1
fi
