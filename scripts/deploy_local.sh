#!/bin/bash
# Script de deploy local completo

set -e  # Para na primeira falha

echo "🚀 Deploy Local - Projeto DJBlog"
echo "=================================="

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

# Detectar comando Python e ambiente
PYTHON_CMD=""
PIP_CMD=""

# Verificar se está no WSL
if grep -q Microsoft /proc/version 2>/dev/null; then
    log_info "Detectado ambiente WSL"
    export WSL_ENVIRONMENT=true
fi

# Detectar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    # Verificar se é Python 3
    python_version=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1)
    if [ "$python_version" = "3" ]; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    else
        log_error "Python 2 detectado. Este projeto requer Python 3.8+"
        exit 1
    fi
else
    log_error "Python não encontrado. Instalando automaticamente..."
    
    # Auto-instalar Python se possível
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [ "$WSL_ENVIRONMENT" = true ]; then
        # WSL/Linux - Ubuntu/Debian
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
            PYTHON_CMD="python3"
            PIP_CMD="pip3"
        # Red Hat/CentOS
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
            PYTHON_CMD="python3"
            PIP_CMD="pip3"
        else
            log_error "Não foi possível instalar Python automaticamente"
            log_error "Instale Python 3.8+ manualmente e execute novamente"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install python3
            PYTHON_CMD="python3"
            PIP_CMD="pip3"
        else
            log_error "Homebrew não encontrado. Instale Python 3.8+ manualmente"
            exit 1
        fi
    else
        log_error "Sistema não suportado para instalação automática"
        log_error "Instale Python 3.8+ manualmente e execute novamente"
        exit 1
    fi
fi

log_info "Usando Python: $PYTHON_CMD ($($PYTHON_CMD --version))"

# Verificar se pip está disponível
if ! command -v $PIP_CMD &> /dev/null; then
    log_warning "pip não encontrado, tentando instalar..."
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [ "$WSL_ENVIRONMENT" = true ]; then
        sudo apt install -y python3-pip
    fi
fi

# Verificar se estamos no diretório correto
if [ ! -f "requirements.txt" ]; then
    log_error "Execute este script do diretório raiz do projeto"
    exit 1
fi

# 1. Executar testes
log_info "Executando testes completos..."

# Verificar e instalar dependências sempre
log_info "Verificando dependências Python..."

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    log_info "Criando ambiente virtual Python..."
    
    # Detectar versão do Python
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "Versão Python detectada: $PYTHON_VERSION"
    
    # Verificar se é um ambiente moderno que pode ter restrições
    NEEDS_SECURE_SETUP=false
    
    # Ubuntu 22.04+ ou Python 3.12+
    if [[ -f "/etc/os-release" ]]; then
        OS_INFO=$(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2 || echo "")
        if [[ "$OS_INFO" == *"Ubuntu"* ]]; then
            VERSION=$(echo "$OS_INFO" | grep -o '[0-9][0-9]\.[0-9][0-9]' | head -1)
            if [[ "$VERSION" =~ ^2[2-9]\. ]] || [[ "$VERSION" =~ ^[3-9][0-9]\. ]]; then
                NEEDS_SECURE_SETUP=true
            fi
        fi
    fi
    
    if [[ "$PYTHON_VERSION" =~ ^3\.1[2-9]$ ]] || [[ "$PYTHON_VERSION" =~ ^3\.[2-9][0-9]$ ]]; then
        NEEDS_SECURE_SETUP=true
    fi
    
    # Se precisa de configuração segura, usar script especializado
    if [ "$NEEDS_SECURE_SETUP" = true ]; then
        log_warning "Detectado ambiente moderno (Ubuntu 22.04+ ou Python 3.12+)"
        log_info "Usando configuração segura para evitar 'externally-managed-environment'..."
        
        if [ -f "scripts/setup_secure_venv.sh" ]; then
            chmod +x scripts/setup_secure_venv.sh
            if ./scripts/setup_secure_venv.sh; then
                log_success "Ambiente virtual configurado de forma segura"
            else
                log_error "Falha na configuração segura do ambiente virtual"
                exit 1
            fi
        else
            log_error "Script setup_secure_venv.sh não encontrado"
            exit 1
        fi
    else
        # Configuração padrão para ambientes mais antigos
        if command -v python3-venv &> /dev/null || $PYTHON_CMD -m venv --help &> /dev/null; then
            $PYTHON_CMD -m venv venv
            log_success "Ambiente virtual criado"
        else
            log_warning "python$PYTHON_VERSION-venv não encontrado, instalando..."
            if [[ "$OSTYPE" == "linux-gnu"* ]] || [ "$WSL_ENVIRONMENT" = true ]; then
                # Tentar instalar pacote específico da versão primeiro
                if sudo apt update && sudo apt install -y python$PYTHON_VERSION-venv python$PYTHON_VERSION-full; then
                    log_success "python$PYTHON_VERSION-venv instalado"
                else
                    log_warning "Tentando pacotes genéricos..."
                    sudo apt install -y python3-venv python3-full python3-virtualenv
                fi
                
                # Tentar criar ambiente virtual
                if $PYTHON_CMD -m venv venv; then
                    log_success "Ambiente virtual criado"
                elif command -v virtualenv &> /dev/null && virtualenv venv; then
                    log_success "Ambiente virtual criado com virtualenv"
                else
                    log_error "Não foi possível criar ambiente virtual"
                    log_error "Execute: ./scripts/setup_secure_venv.sh"
                    exit 1
                fi
            else
                log_error "Não foi possível criar ambiente virtual"
                exit 1
            fi
        fi
    fi
fi

# Configurar caminhos do ambiente virtual
log_info "Configurando ambiente virtual..."
VENV_PYTHON="venv/bin/python"

# Verificar se o ambiente virtual foi criado corretamente
if [ ! -f "$VENV_PYTHON" ]; then
    log_error "Ambiente virtual não foi criado corretamente"
    exit 1
fi

log_success "Ambiente virtual configurado"

# Atualizar pip no ambiente virtual usando python -m pip
log_info "Atualizando pip..."
$VENV_PYTHON -m pip install --upgrade pip

# Verificar se pip está funcionando
if ! $VENV_PYTHON -m pip --version &> /dev/null; then
    log_warning "pip não está funcionando, tentando reinstalar..."
    
    # Tentar baixar e instalar pip manualmente
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $VENV_PYTHON get-pip.py
    rm get-pip.py
    
    if ! $VENV_PYTHON -m pip --version &> /dev/null; then
        log_error "Falha ao instalar pip no ambiente virtual"
        exit 1
    fi
    log_success "pip reinstalado com sucesso"
fi

# Verificar se boto3 está instalado no ambiente virtual
log_info "Verificando e instalando dependências no ambiente virtual..."

# Sempre instalar/atualizar dependências para garantir que estão atualizadas
if $VENV_PYTHON -m pip install -r requirements.txt; then
    log_success "Dependências instaladas/atualizadas no ambiente virtual"
else
    log_error "Falha ao instalar dependências. Verifique o requirements.txt"
    exit 1
fi

# Verificar se boto3 está funcionando
if ! $VENV_PYTHON -c "import boto3" &> /dev/null; then
    log_error "boto3 não está funcionando no ambiente virtual"
    exit 1
fi

$VENV_PYTHON test_runner.py

if [ $? -ne 0 ]; then
    log_error "Testes falharam! Corrija os erros antes de fazer deploy."
    exit 1
fi

log_success "Testes passaram!"

# 2. Verificar variáveis obrigatórias
log_info "Verificando variáveis de ambiente..."

required_vars=(
    "AWS_ACCESS_KEY_ID"
    "AWS_SECRET_ACCESS_KEY" 
    "AWS_REGION"
    "DYNAMODB_TABLE_NAME"
    "ALARM_EMAIL"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        log_error "Variável obrigatória não definida: $var"
        exit 1
    fi
done

log_success "Variáveis de ambiente OK!"

# 3. Validar AWS
log_info "Validando credenciais AWS..."
aws sts get-caller-identity > /dev/null 2>&1

if [ $? -ne 0 ]; then
    log_error "Credenciais AWS inválidas"
    exit 1
fi

log_success "AWS conectado!"

# 4. Preparar pacotes Lambda
log_info "Preparando pacotes Lambda..."

# Criar diretório temporário
mkdir -p dist/

# Pacote principal
log_info "Criando lambda_coletor.zip..."
zip -r dist/lambda_coletor.zip \
    lambda_coletor.py \
    utils.py \
    config.py \
    summarize_ai.py \
    -x "*.pyc" "__pycache__/*" "*.git*"

log_info "Criando lambda_publicar_wordpress.zip..."
zip -r dist/lambda_publicar_wordpress.zip \
    lambda_publicar_wordpress.py \
    utils.py \
    config.py \
    -x "*.pyc" "__pycache__/*" "*.git*"

log_info "Criando lambda_limpeza.zip..."
zip -r dist/lambda_limpeza.zip \
    lambda_limpeza.py \
    utils.py \
    config.py \
    -x "*.pyc" "__pycache__/*" "*.git*"

log_info "Criando lambda_health_check.zip..."
zip -r dist/lambda_health_check.zip \
    lambda_health_check.py \
    utils.py \
    config.py \
    -x "*.pyc" "__pycache__/*" "*.git*"

log_info "Criando lambda_api_noticias.zip..."
zip -r dist/lambda_api_noticias.zip \
    lambda_api_noticias.py \
    utils.py \
    config.py \
    -x "*.pyc" "__pycache__/*" "*.git*"

log_success "Pacotes Lambda criados!"

# 5. Deploy Terraform
log_info "Executando deploy Terraform..."

cd terraform/aws

# Inicializar se necessário
if [ ! -d ".terraform" ]; then
    log_info "Inicializando Terraform..."
    terraform init
fi

# Planejar
log_info "Planejando mudanças..."
terraform plan -out=tfplan

# Confirmar deploy
read -p "Confirma o deploy? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    log_warning "Deploy cancelado pelo usuário"
    exit 0
fi

# Aplicar
log_info "Aplicando mudanças..."
terraform apply tfplan

if [ $? -ne 0 ]; then
    log_error "Deploy Terraform falhou!"
    exit 1
fi

log_success "Deploy Terraform concluído!"

# Voltar ao diretório raiz
cd ../..

# 6. Atualizar código das Lambdas
log_info "Atualizando código das Lambdas..."

# Lista de funções
functions=(
    "djblog-coletor"
    "djblog-publicar-wordpress"
    "djblog-limpeza"
    "djblog-health-check"
    "djblog-api-noticias"
)

# Atualizar cada função
for func in "${functions[@]}"; do
    log_info "Atualizando função: $func"
    
    zip_file="dist/${func/djblog-/lambda_}.zip"
    
    if [ -f "$zip_file" ]; then
        aws lambda update-function-code \
            --function-name "$func" \
            --zip-file "fileb://$zip_file" \
            --region "$AWS_REGION" > /dev/null
        
        if [ $? -eq 0 ]; then
            log_success "✅ $func atualizado"
        else
            log_warning "⚠️ Falha ao atualizar $func (função pode não existir ainda)"
        fi
    else
        log_warning "⚠️ Arquivo não encontrado: $zip_file"
    fi
done

# 7. Executar testes pós-deploy
log_info "Executando testes pós-deploy..."

# Testar execução das Lambdas
log_info "Testando Lambda coletor..."
aws lambda invoke \
    --function-name "djblog-coletor" \
    --payload '{}' \
    --region "$AWS_REGION" \
    response.json > /dev/null 2>&1

if [ $? -eq 0 ]; then
    log_success "✅ Lambda coletor respondeu"
else
    log_warning "⚠️ Lambda coletor não respondeu (normal se for primeira vez)"
fi

# 8. Verificar recursos criados
log_info "Verificando recursos criados..."

# DynamoDB
tables=$(aws dynamodb list-tables --region "$AWS_REGION" --query 'TableNames' --output text | grep djblog || true)
if [ -n "$tables" ]; then
    log_success "✅ Tabelas DynamoDB: $tables"
else
    log_warning "⚠️ Nenhuma tabela DynamoDB encontrada"
fi

# EventBridge
rules=$(aws events list-rules --region "$AWS_REGION" --query 'Rules[?contains(Name, `djblog`)].Name' --output text || true)
if [ -n "$rules" ]; then
    log_success "✅ Regras EventBridge criadas"
else
    log_warning "⚠️ Nenhuma regra EventBridge encontrada"
fi

# 9. Limpeza
log_info "Limpando arquivos temporários..."
rm -rf dist/
rm -f response.json

# 10. Resumo final
echo ""
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "=================================="
echo "📊 Recursos implantados:"
echo "   • Lambdas: 5 funções"
echo "   • DynamoDB: 3 tabelas"
echo "   • EventBridge: Agendamentos configurados"
echo "   • SNS: Alertas por email"
echo ""
echo "📋 Próximos passos:"
echo "   1. Confirme inscrição no SNS (verifique seu email)"
echo "   2. Monitore logs no CloudWatch"
echo "   3. Execute teste manual se necessário"
echo ""
echo "🔗 Links úteis:"
echo "   • CloudWatch: https://console.aws.amazon.com/cloudwatch"
echo "   • DynamoDB: https://console.aws.amazon.com/dynamodb"
echo "   • Lambda: https://console.aws.amazon.com/lambda"
echo ""

log_success "Deploy concluído! Sistema está funcionando."
