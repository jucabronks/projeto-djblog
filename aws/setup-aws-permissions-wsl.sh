#!/bin/bash

# =============================================================================
# SCRIPT DE CONFIGURAÇÃO DE PERMISSÕES AWS PARA PROJETO VM (WSL/LINUX)
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

print_header "Configurando permissões AWS para o projeto..."

# Verificar se AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI não está instalado. Instale primeiro:"
    echo "   curl \"https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip\" -o \"awscliv2.zip\""
    echo "   unzip awscliv2.zip"
    echo "   sudo ./aws/install"
    exit 1
fi

# Verificar se está logado na AWS
if ! aws sts get-caller-identity &> /dev/null; then
    print_error "Não está logado na AWS. Execute:"
    echo "   aws configure"
    exit 1
fi

# Obter informações da conta
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
USER_NAME=$(echo $USER_ARN | cut -d'/' -f2)

print_status "Logado como: $USER_NAME"
print_status "Account ID: $ACCOUNT_ID"

# Nome da política
POLICY_NAME="ProjetoVMPermissions"
POLICY_DESCRIPTION="Permissões necessárias para o projeto VM serverless"

print_info "Criando política IAM: $POLICY_NAME"

# Criar política IAM
POLICY_ARN=$(aws iam create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document file://iam-policy.json \
    --description "$POLICY_DESCRIPTION" \
    --query 'Policy.Arn' \
    --output text 2>/dev/null || \
    aws iam get-policy \
    --policy-arn "arn:aws:iam::$ACCOUNT_ID:policy/$POLICY_NAME" \
    --query 'Policy.Arn' \
    --output text)

print_status "Política criada: $POLICY_ARN"

# Verificar se o usuário já existe
if aws iam get-user --user-name "$USER_NAME" &> /dev/null; then
    print_status "Usuário IAM encontrado: $USER_NAME"
else
    print_warning "Usuário IAM não encontrado. Criando..."
    aws iam create-user --user-name "$USER_NAME"
    print_status "Usuário criado: $USER_NAME"
fi

# Anexar política ao usuário
print_info "Anexando política ao usuário..."

aws iam attach-user-policy \
    --user-name "$USER_NAME" \
    --policy-arn "$POLICY_ARN"

print_status "Política anexada com sucesso!"

# Criar grupo (opcional)
GROUP_NAME="ProjetoVMGroup"
print_info "Criando grupo: $GROUP_NAME"

aws iam create-group --group-name "$GROUP_NAME" 2>/dev/null || print_status "Grupo já existe"

# Anexar política ao grupo
aws iam attach-group-policy \
    --group-name "$GROUP_NAME" \
    --policy-arn "$POLICY_ARN"

# Adicionar usuário ao grupo
aws iam add-user-to-group \
    --group-name "$GROUP_NAME" \
    --user-name "$USER_NAME"

print_status "Usuário adicionado ao grupo!"

# Criar bucket S3 para Terraform state (se não existir)
BUCKET_NAME="projeto-vm-terraform-state-$ACCOUNT_ID"
print_info "Verificando bucket S3: $BUCKET_NAME"

if ! aws s3 ls "s3://$BUCKET_NAME" &> /dev/null; then
    print_info "Criando bucket S3 para Terraform state..."
    aws s3 mb "s3://$BUCKET_NAME" --region us-east-1
    
    # Habilitar versionamento
    aws s3api put-bucket-versioning \
        --bucket "$BUCKET_NAME" \
        --versioning-configuration Status=Enabled
    
    # Habilitar criptografia
    aws s3api put-bucket-encryption \
        --bucket "$BUCKET_NAME" \
        --server-side-encryption-configuration '{
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }
            ]
        }'
    
    print_status "Bucket S3 criado e configurado!"
else
    print_status "Bucket S3 já existe!"
fi

# Criar tabela DynamoDB para locks do Terraform
TABLE_NAME="terraform-locks"
print_info "Verificando tabela DynamoDB: $TABLE_NAME"

if ! aws dynamodb describe-table --table-name "$TABLE_NAME" &> /dev/null; then
    print_info "Criando tabela DynamoDB para locks..."
    aws dynamodb create-table \
        --table-name "$TABLE_NAME" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region us-east-1
    
    print_warning "Aguardando tabela ficar ativa..."
    aws dynamodb wait table-exists --table-name "$TABLE_NAME"
    print_status "Tabela DynamoDB criada!"
else
    print_status "Tabela DynamoDB já existe!"
fi

echo ""
print_header "Configuração AWS concluída com sucesso!"
echo ""
print_info "Resumo:"
echo "   ✅ Política IAM: $POLICY_ARN"
echo "   ✅ Usuário: $USER_NAME"
echo "   ✅ Grupo: $GROUP_NAME"
echo "   ✅ Bucket S3: $BUCKET_NAME"
echo "   ✅ Tabela DynamoDB: $TABLE_NAME"
echo ""
print_info "Próximos passos:"
echo "   1. Execute: ./configure-terraform-backend-wsl.sh"
echo "   2. Execute o workflow CI/CD no GitHub"
echo "   3. Verifique se o deploy funciona corretamente"
echo ""
print_info "Para testar as permissões:"
echo "   aws lambda list-functions"
echo "   aws iam list-attached-user-policies --user-name $USER_NAME" 