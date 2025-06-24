#!/bin/bash

# =============================================================================
# SCRIPT DE CONFIGURAÇÃO DE PERMISSÕES AWS PARA PROJETO VM
# =============================================================================

set -e

echo "🚀 Configurando permissões AWS para o projeto..."

# Verificar se AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI não está instalado. Instale primeiro:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Verificar se está logado na AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Não está logado na AWS. Execute:"
    echo "   aws configure"
    exit 1
fi

# Obter informações da conta
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
USER_NAME=$(echo $USER_ARN | cut -d'/' -f2)

echo "✅ Logado como: $USER_NAME"
echo "✅ Account ID: $ACCOUNT_ID"

# Nome da política
POLICY_NAME="ProjetoVMPermissions"
POLICY_DESCRIPTION="Permissões necessárias para o projeto VM serverless"

echo "📋 Criando política IAM: $POLICY_NAME"

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

echo "✅ Política criada: $POLICY_ARN"

# Verificar se o usuário já existe
if aws iam get-user --user-name "$USER_NAME" &> /dev/null; then
    echo "✅ Usuário IAM encontrado: $USER_NAME"
else
    echo "⚠️  Usuário IAM não encontrado. Criando..."
    aws iam create-user --user-name "$USER_NAME"
    echo "✅ Usuário criado: $USER_NAME"
fi

# Anexar política ao usuário
echo "🔗 Anexando política ao usuário..."

aws iam attach-user-policy \
    --user-name "$USER_NAME" \
    --policy-arn "$POLICY_ARN"

echo "✅ Política anexada com sucesso!"

# Criar grupo (opcional)
GROUP_NAME="ProjetoVMGroup"
echo "👥 Criando grupo: $GROUP_NAME"

aws iam create-group --group-name "$GROUP_NAME" 2>/dev/null || echo "✅ Grupo já existe"

# Anexar política ao grupo
aws iam attach-group-policy \
    --group-name "$GROUP_NAME" \
    --policy-arn "$POLICY_ARN"

# Adicionar usuário ao grupo
aws iam add-user-to-group \
    --group-name "$GROUP_NAME" \
    --user-name "$USER_NAME"

echo "✅ Usuário adicionado ao grupo!"

# Criar bucket S3 para Terraform state (se não existir)
BUCKET_NAME="projeto-vm-terraform-state-$ACCOUNT_ID"
echo "🪣 Verificando bucket S3: $BUCKET_NAME"

if ! aws s3 ls "s3://$BUCKET_NAME" &> /dev/null; then
    echo "📦 Criando bucket S3 para Terraform state..."
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
    
    echo "✅ Bucket S3 criado e configurado!"
else
    echo "✅ Bucket S3 já existe!"
fi

# Criar tabela DynamoDB para locks do Terraform
TABLE_NAME="terraform-locks"
echo "🗄️  Verificando tabela DynamoDB: $TABLE_NAME"

if ! aws dynamodb describe-table --table-name "$TABLE_NAME" &> /dev/null; then
    echo "📊 Criando tabela DynamoDB para locks..."
    aws dynamodb create-table \
        --table-name "$TABLE_NAME" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region us-east-1
    
    echo "⏳ Aguardando tabela ficar ativa..."
    aws dynamodb wait table-exists --table-name "$TABLE_NAME"
    echo "✅ Tabela DynamoDB criada!"
else
    echo "✅ Tabela DynamoDB já existe!"
fi

echo ""
echo "🎉 Configuração AWS concluída com sucesso!"
echo ""
echo "📋 Resumo:"
echo "   ✅ Política IAM: $POLICY_ARN"
echo "   ✅ Usuário: $USER_NAME"
echo "   ✅ Grupo: $GROUP_NAME"
echo "   ✅ Bucket S3: $BUCKET_NAME"
echo "   ✅ Tabela DynamoDB: $TABLE_NAME"
echo ""
echo "🔧 Próximos passos:"
echo "   1. Atualize o arquivo terraform/aws/main.tf para usar o bucket correto"
echo "   2. Execute o workflow CI/CD no GitHub"
echo "   3. Verifique se o deploy funciona corretamente"
echo ""
echo "💡 Para testar as permissões:"
echo "   aws lambda list-functions"
echo "   aws iam list-attached-user-policies --user-name $USER_NAME" 