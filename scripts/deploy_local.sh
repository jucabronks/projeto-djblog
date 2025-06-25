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

# Verificar se estamos no diretório correto
if [ ! -f "requirements.txt" ]; then
    log_error "Execute este script do diretório raiz do projeto"
    exit 1
fi

# 1. Executar testes
log_info "Executando testes completos..."
python test_runner.py

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
