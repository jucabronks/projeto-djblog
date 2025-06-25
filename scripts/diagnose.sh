#!/bin/bash

# 🔧 Script de Diagnóstico - Ambiente Python

echo "🔧 Diagnóstico do Ambiente Python"
echo "=================================="

# 1. Sistema
echo "1. Sistema:"
echo "   OS: $(uname -s)"
echo "   Distribuição: $(lsb_release -d 2>/dev/null | cut -f2 || echo 'N/A')"
echo "   WSL: $(grep -i microsoft /proc/version 2>/dev/null && echo 'Sim' || echo 'Não')"

# 2. Python
echo ""
echo "2. Python disponível:"
if command -v python3 &> /dev/null; then
    echo "   ✅ python3: $(python3 --version)"
    echo "   📍 Localização: $(which python3)"
else
    echo "   ❌ python3: Não encontrado"
fi

if command -v python &> /dev/null; then
    echo "   ✅ python: $(python --version 2>&1)"
    echo "   📍 Localização: $(which python)"
else
    echo "   ❌ python: Não encontrado"
fi

# 3. pip
echo ""
echo "3. pip disponível:"
if command -v pip3 &> /dev/null; then
    echo "   ✅ pip3: $(pip3 --version)"
else
    echo "   ❌ pip3: Não encontrado"
fi

if command -v pip &> /dev/null; then
    echo "   ✅ pip: $(pip --version)"
else
    echo "   ❌ pip: Não encontrado"
fi

# 4. Ambiente virtual
echo ""
echo "4. Ambiente virtual:"
if [ -d "venv" ]; then
    echo "   ✅ Diretório venv/ existe"
    
    if [ -f "venv/bin/python" ]; then
        echo "   ✅ venv/bin/python existe"
        echo "   📍 Versão: $(venv/bin/python --version)"
        
        # Testar importações básicas
        echo ""
        echo "5. Testando importações no venv:"
        
        # boto3
        if venv/bin/python -c "import boto3" 2>/dev/null; then
            BOTO3_VERSION=$(venv/bin/python -c "import boto3; print(boto3.__version__)" 2>/dev/null)
            echo "   ✅ boto3: $BOTO3_VERSION"
        else
            echo "   ❌ boto3: Não encontrado"
        fi
        
        # requests
        if venv/bin/python -c "import requests" 2>/dev/null; then
            REQUESTS_VERSION=$(venv/bin/python -c "import requests; print(requests.__version__)" 2>/dev/null)
            echo "   ✅ requests: $REQUESTS_VERSION"
        else
            echo "   ❌ requests: Não encontrado"
        fi
        
        # pytest
        if venv/bin/python -c "import pytest" 2>/dev/null; then
            PYTEST_VERSION=$(venv/bin/python -c "import pytest; print(pytest.__version__)" 2>/dev/null)
            echo "   ✅ pytest: $PYTEST_VERSION"
        else
            echo "   ❌ pytest: Não encontrado"
        fi
        
    else
        echo "   ❌ venv/bin/python não existe"
    fi
    
    if [ -f "venv/bin/pip" ]; then
        echo "   ✅ venv/bin/pip existe"
    else
        echo "   ❌ venv/bin/pip não existe"
    fi
else
    echo "   ❌ Diretório venv/ não existe"
fi

# 6. Permissões
echo ""
echo "6. Permissões dos scripts:"
for script in scripts/test_setup.sh scripts/deploy_local.sh; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo "   ✅ $script: Executável"
        else
            echo "   ⚠️ $script: Não executável (execute: chmod +x $script)"
        fi
    else
        echo "   ❌ $script: Não encontrado"
    fi
done

# 7. Recomendações
echo ""
echo "7. Próximos passos recomendados:"

if [ ! -d "venv" ]; then
    echo "   🔄 Criar ambiente virtual: python3 -m venv venv"
fi

if [ -d "venv" ] && [ ! -f "venv/bin/python" ]; then
    echo "   🔄 Recriar ambiente virtual: rm -rf venv && python3 -m venv venv"
fi

if [ -f "venv/bin/python" ]; then
    if ! venv/bin/python -c "import boto3" 2>/dev/null; then
        echo "   📦 Instalar dependências: venv/bin/pip install -r requirements.txt"
    fi
fi

if [ ! -x "scripts/test_setup.sh" ]; then
    echo "   🔧 Tornar scripts executáveis: chmod +x scripts/*.sh"
fi

echo ""
echo "🎯 Para testar após correções:"
echo "   ./scripts/test_setup.sh"
echo "   ./scripts/deploy_local.sh"
