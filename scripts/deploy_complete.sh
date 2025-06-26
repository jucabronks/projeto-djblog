#!/bin/bash

# =============================================================================
# SCRIPT DE DEPLOY COMPLETO - PROJETO VM SERVERLESS
# =============================================================================

set -e  # Para em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ️  $1${NC}"
}

# Banner
echo "=================================================================="
echo "🚀 DEPLOY COMPLETO - PROJETO VM SERVERLESS"
echo "=================================================================="
echo "Este script irá:"
echo "1. Verificar pré-requisitos"
echo "2. Empacotar Lambda Functions"
echo "3. Fazer deploy via Terraform"
echo "4. Verificar se tudo está funcionando"
echo "=================================================================="
echo

# Verificar pré-requisitos
log "Verificando pré-requisitos..."

# Verificar se AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    error "AWS CLI não está instalado. Instale em: https://aws.amazon.com/cli/"
    exit 1
fi

# Verificar se Terraform está instalado
if ! command -v terraform &> /dev/null; then
    error "Terraform não está instalado. Instale em: https://terraform.io/"
    exit 1
fi

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    error "Python 3 não está instalado"
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    error "pip3 não está instalado"
    exit 1
fi

# Verificar se zip está instalado
if ! command -v zip &> /dev/null; then
    error "zip não está instalado"
    exit 1
fi

log "✅ Todos os pré-requisitos estão instalados"

# Verificar variáveis de ambiente
log "Verificando variáveis de ambiente..."

required_vars=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_REGION" "ALARM_EMAIL")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    error "Variáveis de ambiente obrigatórias não configuradas:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    echo
    echo "Configure as variáveis de ambiente ou exporte-as:"
    echo "export AWS_ACCESS_KEY_ID=sua_access_key"
    echo "export AWS_SECRET_ACCESS_KEY=sua_secret_key"
    echo "export AWS_REGION=us-east-1"
    echo "export ALARM_EMAIL=seu@email.com"
    exit 1
fi

log "✅ Variáveis de ambiente configuradas"

# Instalar dependências Python
log "Instalando dependências Python..."
pip3 install -r requirements.txt
log "✅ Dependências instaladas"

# Executar testes
log "Executando testes..."
if python3 -m pytest tests/ -v; then
    log "✅ Todos os testes passaram"
else
    error "❌ Alguns testes falharam"
    exit 1
fi

# Empacotar Lambda Functions
log "Empacotando Lambda Functions..."

# Limpar arquivos zip antigos
rm -f *.zip

# Empacotar cada Lambda
log "📦 Empacotando coletor..."
zip -j lambda_coletor.zip lambda_coletor.py utils.py summarize_ai.py

log "📦 Empacotando publicador..."
zip -j lambda_publicar_wordpress.zip lambda_publicar_wordpress.py utils.py

log "📦 Empacotando limpeza..."
zip -j lambda_limpeza.zip lambda_limpeza.py utils.py

log "📦 Empacotando health check..."
zip -j lambda_health_check.zip lambda_health_check.py utils.py

log "✅ Lambda Functions empacotadas"

# Verificar se os arquivos zip foram criados
for zip_file in lambda_coletor.zip lambda_publicar_wordpress.zip lambda_limpeza.zip lambda_health_check.zip; do
    if [ ! -f "$zip_file" ]; then
        error "Arquivo $zip_file não foi criado"
        exit 1
    fi
    log "✅ $zip_file criado ($(du -h $zip_file | cut -f1))"
done

# Criar arquivo terraform.tfvars
log "Criando arquivo terraform.tfvars..."

cat > terraform/aws/terraform.tfvars << EOF
# Configurações básicas
aws_region = "us-east-1"
project_name = "projeto-vm"
environment = "dev"

# DynamoDB
dynamodb_table_name = "djblog-noticias"

# OpenAI (opcional)
openai_api_key = "${OPENAI_API_KEY:-}"

# Datadog (opcional)
dd_api_key = "${DD_API_KEY:-}"
dd_site = "datadoghq.com"
dd_env = "prod"

# Configurações de coleta
nicho = "ciencia"
pais = "Brasil"
max_news_per_source = 3

# Copyscape (opcional)
copys_api_user = "${COPYS_API_USER:-}"
copys_api_key = "${COPYS_API_KEY:-}"

# Nichos a coletar
nicho_lista = ["saude", "esportes", "tecnologia", "economia"]

# Mapeamento WordPress
categorias_wp = {
  saude      = 2
  esportes   = 3
  tecnologia = 4
  economia   = 5
}

# WordPress
wp_url = "${WP_URL:-https://placeholder.com}"
wp_user = "${WP_USER:-admin}"
wp_app_password = "${WP_APP_PASSWORD:-placeholder}"

# Email para alertas
alarm_email = "$ALARM_EMAIL"

# Tags
tags = {
  Owner       = "DevOps Team"
  Environment = "dev"
  Project     = "projeto-vm"
  ManagedBy   = "Terraform"
}
EOF

log "✅ arquivo terraform.tfvars criado"

# Fazer deploy via Terraform
log "Iniciando deploy via Terraform..."

cd terraform/aws

# Inicializar Terraform
log "🔧 Inicializando Terraform..."
terraform init
log "✅ Terraform inicializado"

# Verificar plano
log "📋 Verificando plano de execução..."
terraform plan -out=tfplan
log "✅ Plano verificado"

# Aplicar infraestrutura
log "🚀 Aplicando infraestrutura..."
terraform apply tfplan
log "✅ Infraestrutura aplicada"

# Mostrar outputs
log "📊 Informações da infraestrutura:"
terraform output

cd ../..

# Aguardar um pouco para as Lambdas ficarem disponíveis
log "⏳ Aguardando Lambdas ficarem disponíveis..."
sleep 30

# Executar script de monitoramento
log "🔍 Executando verificação pós-deploy..."
python3 scripts/monitor_deployment.py

# Resumo final
echo
echo "=================================================================="
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "=================================================================="
echo "✅ Infraestrutura serverless criada"
echo "✅ Lambda Functions configuradas"
echo "✅ EventBridge Rules agendadas"
echo "✅ SNS Topic para alertas criado"
echo "✅ CloudWatch Alarms configurados"
echo
echo "📅 Próximas execuções automáticas:"
echo "   - Coleta: 20:00, 20:10, 20:20, 20:30 (BRT)"
echo "   - Resumo: 20:35 (BRT)"
echo "   - Publicação: 6:40 (BRT) - Seg, Ter, Qua, Sex"
echo "   - Limpeza: Domingo 3:00 (BRT)"
echo "   - Health Check: Diário"
echo
echo "📧 Verifique seu email para confirmar alertas SNS"
echo "🔍 Monitore no CloudWatch: https://console.aws.amazon.com/cloudwatch"
echo "💰 Custo estimado: $5-8/mês"
echo "==================================================================" 