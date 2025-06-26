#!/bin/bash

# 🔧 Script de Diagnóstico e Correção do Erro "externally-managed-environment"
# Para Ubuntu 22.04+ e Python 3.12+

echo "🔧 Diagnóstico: externally-managed-environment"
echo "=============================================="

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

# 1. Diagnóstico do problema
log_info "Diagnosticando o problema..."

# Verificar Python e sistema
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "unknown")
OS_INFO=$(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo "Unknown")

echo "📍 Sistema: $OS_INFO"
echo "📍 Python: $PYTHON_VERSION"

# Verificar se arquivo EXTERNALLY-MANAGED existe
EXTERNAL_MANAGED_FILE=""
for path in "/usr/lib/python3/dist-packages" "/usr/lib/python$PYTHON_VERSION/site-packages" "/usr/local/lib/python$PYTHON_VERSION/dist-packages"; do
    if [ -f "$path/EXTERNALLY-MANAGED" ]; then
        EXTERNAL_MANAGED_FILE="$path/EXTERNALLY-MANAGED"
        break
    fi
done

if [ -n "$EXTERNAL_MANAGED_FILE" ]; then
    log_warning "Arquivo EXTERNALLY-MANAGED encontrado: $EXTERNAL_MANAGED_FILE"
    echo "📄 Conteúdo:"
    cat "$EXTERNAL_MANAGED_FILE" | head -10
    echo ""
else
    log_info "Arquivo EXTERNALLY-MANAGED não encontrado (normal em sistemas mais antigos)"
fi

# Verificar pip
if python3 -m pip --version >/dev/null 2>&1; then
    log_success "pip funcional: $(python3 -m pip --version)"
else
    log_error "pip não funcional no Python do sistema"
fi

# Testar criação de venv
log_info "Testando criação de ambiente virtual..."
if python3 -m venv test_diagnose_venv >/dev/null 2>&1; then
    log_success "python3 -m venv funciona"
    rm -rf test_diagnose_venv
    VENV_WORKS=true
else
    log_error "python3 -m venv não funciona"
    VENV_WORKS=false
fi

# 2. Oferecer soluções baseadas no diagnóstico
echo ""
echo "🔧 SOLUÇÕES RECOMENDADAS"
echo "======================="

if [ "$VENV_WORKS" = true ]; then
    log_success "Ambiente virtual funciona, problema pode ser de dependências"
    echo ""
    echo "✅ Soluções rápidas:"
    echo "   1. ./scripts/setup_secure_venv.sh"
    echo "   2. python3 -m venv venv && source venv/bin/activate"
    echo "   3. venv/bin/pip install -r requirements.txt"
else
    log_warning "Ambiente virtual não funciona, precisa de correção do sistema"
    echo ""
    echo "🔧 Soluções por ordem de preferência:"
    echo ""
    echo "1️⃣ SOLUÇÃO RECOMENDADA (automática):"
    echo "   ./scripts/setup_secure_venv.sh"
    echo ""
    echo "2️⃣ SOLUÇÃO MANUAL (instalar dependências):"
    echo "   sudo apt update"
    echo "   sudo apt install -y python$PYTHON_VERSION-venv python$PYTHON_VERSION-full"
    echo "   python3 -m venv venv"
    echo ""
    echo "3️⃣ SOLUÇÃO ALTERNATIVA (virtualenv):"
    echo "   sudo apt install -y python3-virtualenv"
    echo "   virtualenv venv"
    echo ""
    echo "4️⃣ SOLUÇÃO EXTREMA (não recomendada):"
    echo "   # Remove a proteção do sistema (PERIGOSO)"
    echo "   # sudo rm $EXTERNAL_MANAGED_FILE"
fi

# 3. Verificar se já existe venv no projeto
echo ""
if [ -d "venv" ]; then
    log_info "Ambiente virtual 'venv' já existe"
    
    if [ -f "venv/bin/python" ]; then
        log_success "venv/bin/python existe"
        echo "📍 Versão: $(venv/bin/python --version 2>/dev/null || echo 'Erro ao verificar versão')"
        
        if venv/bin/python -m pip --version >/dev/null 2>&1; then
            log_success "pip funcionando no venv"
            echo "📍 pip: $(venv/bin/python -m pip --version)"
        else
            log_error "pip não funciona no venv"
        fi
    else
        log_error "venv/bin/python não existe - venv corrompido"
        echo "🔧 Solução: rm -rf venv && ./scripts/setup_secure_venv.sh"
    fi
else
    log_info "Ambiente virtual não existe - precisa ser criado"
fi

# 4. Auto-execução se solicitado
echo ""
read -p "🤖 Executar correção automática agora? (y/N): " auto_fix
if [[ $auto_fix == [yY] ]]; then
    log_info "Executando correção automática..."
    
    if [ -f "scripts/setup_secure_venv.sh" ]; then
        ./scripts/setup_secure_venv.sh
    else
        log_error "Script setup_secure_venv.sh não encontrado"
        echo "Execute os comandos manuais listados acima"
    fi
else
    echo ""
    echo "📝 RESUMO DOS PRÓXIMOS PASSOS:"
    echo "============================="
    echo "1. Execute: ./scripts/setup_secure_venv.sh"
    echo "2. Ou siga as soluções manuais listadas acima"
    echo "3. Teste com: python3 test_runner.py --quick"
    echo "4. Deploy com: ./scripts/deploy_local.sh"
fi

echo ""
echo "💡 Para mais informações, consulte:"
echo "   - DEPLOY_INSTRUCTIONS.md"
echo "   - https://peps.python.org/pep-0668/"
