#!/bin/bash

# =============================================================================
# CONFIGURAR BACKEND S3 DO TERRAFORM (WSL/LINUX)
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}📋 $1${NC}"
}

print_header() {
    echo -e "${WHITE}🚀 $1${NC}"
}

print_header "Configurando backend S3 do Terraform..."

# Obter Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ -z "$ACCOUNT_ID" ]; then
    print_error "Erro ao obter Account ID"
    exit 1
fi

print_status "Account ID: $ACCOUNT_ID"

# Nome do bucket
BUCKET_NAME="projeto-vm-terraform-state-$ACCOUNT_ID"

# Verificar se o bucket existe
if aws s3 ls "s3://$BUCKET_NAME" &> /dev/null; then
    print_status "Bucket S3 encontrado: $BUCKET_NAME"
else
    print_error "Bucket S3 não encontrado: $BUCKET_NAME"
    print_warning "Execute primeiro: ./setup-aws-permissions-wsl.sh"
    exit 1
fi

# Atualizar o arquivo main.tf
TERRAFORM_FILE="../terraform/aws/main.tf"

if [ ! -f "$TERRAFORM_FILE" ]; then
    print_error "Arquivo Terraform não encontrado: $TERRAFORM_FILE"
    exit 1
fi

# Fazer backup do arquivo original
cp "$TERRAFORM_FILE" "${TERRAFORM_FILE}.backup"
print_status "Backup criado: ${TERRAFORM_FILE}.backup"

# Substituir ACCOUNT_ID pelo valor real
sed -i "s/projeto-vm-terraform-state-ACCOUNT_ID/$BUCKET_NAME/g" "$TERRAFORM_FILE"

print_status "Arquivo Terraform atualizado com bucket: $BUCKET_NAME"

# Verificar se a tabela DynamoDB existe
TABLE_NAME="terraform-locks"
if aws dynamodb describe-table --table-name "$TABLE_NAME" &> /dev/null; then
    print_status "Tabela DynamoDB encontrada: $TABLE_NAME"
else
    print_error "Tabela DynamoDB não encontrada: $TABLE_NAME"
    print_warning "Execute primeiro: ./setup-aws-permissions-wsl.sh"
    exit 1
fi

echo ""
print_header "Backend S3 configurado com sucesso!"
echo ""
print_info "Configuração:"
echo "   ✅ Bucket S3: $BUCKET_NAME"
echo "   ✅ Tabela DynamoDB: $TABLE_NAME"
echo "   ✅ Arquivo: $TERRAFORM_FILE"
echo ""
print_header "Agora você pode executar o workflow CI/CD!"
echo ""
print_info "Para testar o Terraform:"
echo "   cd ../terraform/aws"
echo "   terraform init"
echo "   terraform plan" 