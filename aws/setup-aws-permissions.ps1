# =============================================================================
# SCRIPT DE CONFIGURAÇÃO DE PERMISSÕES AWS PARA PROJETO VM (POWERSHELL)
# =============================================================================

param(
    [string]$Region = "us-east-1"
)

# Configurar para parar em caso de erro
$ErrorActionPreference = "Stop"

Write-Host "🚀 Configurando permissões AWS para o projeto..." -ForegroundColor Green

# Verificar se AWS CLI está instalado
try {
    $null = Get-Command aws -ErrorAction Stop
    Write-Host "✅ AWS CLI encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI não está instalado. Instale primeiro:" -ForegroundColor Red
    Write-Host "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html" -ForegroundColor Yellow
    exit 1
}

# Verificar se está logado na AWS
try {
    $callerIdentity = aws sts get-caller-identity | ConvertFrom-Json
    Write-Host "✅ Logado na AWS" -ForegroundColor Green
} catch {
    Write-Host "❌ Não está logado na AWS. Execute:" -ForegroundColor Red
    Write-Host "   aws configure" -ForegroundColor Yellow
    exit 1
}

# Obter informações da conta
$ACCOUNT_ID = $callerIdentity.Account
$USER_ARN = $callerIdentity.Arn
$USER_NAME = $USER_ARN.Split('/')[1]

Write-Host "✅ Logado como: $USER_NAME" -ForegroundColor Green
Write-Host "✅ Account ID: $ACCOUNT_ID" -ForegroundColor Green

# Nome da política
$POLICY_NAME = "ProjetoVMPermissions"
$POLICY_DESCRIPTION = "Permissões necessárias para o projeto VM serverless"

Write-Host "📋 Criando política IAM: $POLICY_NAME" -ForegroundColor Cyan

# Criar política IAM
try {
    $policyResult = aws iam create-policy `
        --policy-name $POLICY_NAME `
        --policy-document file://iam-policy.json `
        --description $POLICY_DESCRIPTION | ConvertFrom-Json
    $POLICY_ARN = $policyResult.Policy.Arn
    Write-Host "✅ Política criada: $POLICY_ARN" -ForegroundColor Green
} catch {
    try {
        $POLICY_ARN = "arn:aws:iam::$ACCOUNT_ID`:policy/$POLICY_NAME"
        $null = aws iam get-policy --policy-arn $POLICY_ARN
        Write-Host "✅ Política já existe: $POLICY_ARN" -ForegroundColor Green
    } catch {
        Write-Host "❌ Erro ao criar/obter política" -ForegroundColor Red
        exit 1
    }
}

# Verificar se o usuário já existe
try {
    $null = aws iam get-user --user-name $USER_NAME
    Write-Host "✅ Usuário IAM encontrado: $USER_NAME" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Usuário IAM não encontrado. Criando..." -ForegroundColor Yellow
    aws iam create-user --user-name $USER_NAME
    Write-Host "✅ Usuário criado: $USER_NAME" -ForegroundColor Green
}

# Anexar política ao usuário
Write-Host "🔗 Anexando política ao usuário..." -ForegroundColor Cyan

try {
    aws iam attach-user-policy `
        --user-name $USER_NAME `
        --policy-arn $POLICY_ARN
    Write-Host "✅ Política anexada com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Política já estava anexada ou erro ao anexar" -ForegroundColor Yellow
}

# Criar grupo (opcional)
$GROUP_NAME = "ProjetoVMGroup"
Write-Host "👥 Criando grupo: $GROUP_NAME" -ForegroundColor Cyan

try {
    aws iam create-group --group-name $GROUP_NAME
    Write-Host "✅ Grupo criado" -ForegroundColor Green
} catch {
    Write-Host "✅ Grupo já existe" -ForegroundColor Green
}

# Anexar política ao grupo
try {
    aws iam attach-group-policy `
        --group-name $GROUP_NAME `
        --policy-arn $POLICY_ARN
    Write-Host "✅ Política anexada ao grupo" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Política já estava anexada ao grupo" -ForegroundColor Yellow
}

# Adicionar usuário ao grupo
try {
    aws iam add-user-to-group `
        --group-name $GROUP_NAME `
        --user-name $USER_NAME
    Write-Host "✅ Usuário adicionado ao grupo!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Usuário já estava no grupo" -ForegroundColor Yellow
}

# Criar bucket S3 para Terraform state (se não existir)
$BUCKET_NAME = "projeto-vm-terraform-state-$ACCOUNT_ID"
Write-Host "🪣 Verificando bucket S3: $BUCKET_NAME" -ForegroundColor Cyan

try {
    $null = aws s3 ls "s3://$BUCKET_NAME"
    Write-Host "✅ Bucket S3 já existe!" -ForegroundColor Green
} catch {
    Write-Host "📦 Criando bucket S3 para Terraform state..." -ForegroundColor Cyan
    aws s3 mb "s3://$BUCKET_NAME" --region $Region
    
    # Habilitar versionamento
    aws s3api put-bucket-versioning `
        --bucket $BUCKET_NAME `
        --versioning-configuration Status=Enabled
    
    # Habilitar criptografia
    $encryptionConfig = @{
        Rules = @(
            @{
                ApplyServerSideEncryptionByDefault = @{
                    SSEAlgorithm = "AES256"
                }
            }
        )
    } | ConvertTo-Json -Depth 10

    aws s3api put-bucket-encryption `
        --bucket $BUCKET_NAME `
        --server-side-encryption-configuration $encryptionConfig
    
    Write-Host "✅ Bucket S3 criado e configurado!" -ForegroundColor Green
}

# Criar tabela DynamoDB para locks do Terraform
$TABLE_NAME = "terraform-locks"
Write-Host "🗄️  Verificando tabela DynamoDB: $TABLE_NAME" -ForegroundColor Cyan

try {
    $null = aws dynamodb describe-table --table-name $TABLE_NAME
    Write-Host "✅ Tabela DynamoDB já existe!" -ForegroundColor Green
} catch {
    Write-Host "📊 Criando tabela DynamoDB para locks..." -ForegroundColor Cyan
    aws dynamodb create-table `
        --table-name $TABLE_NAME `
        --attribute-definitions AttributeName=LockID,AttributeType=S `
        --key-schema AttributeName=LockID,KeyType=HASH `
        --billing-mode PAY_PER_REQUEST `
        --region $Region
    
    Write-Host "⏳ Aguardando tabela ficar ativa..." -ForegroundColor Yellow
    aws dynamodb wait table-exists --table-name $TABLE_NAME
    Write-Host "✅ Tabela DynamoDB criada!" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Configuração AWS concluída com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Resumo:" -ForegroundColor Cyan
Write-Host "   ✅ Política IAM: $POLICY_ARN" -ForegroundColor White
Write-Host "   ✅ Usuário: $USER_NAME" -ForegroundColor White
Write-Host "   ✅ Grupo: $GROUP_NAME" -ForegroundColor White
Write-Host "   ✅ Bucket S3: $BUCKET_NAME" -ForegroundColor White
Write-Host "   ✅ Tabela DynamoDB: $TABLE_NAME" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Atualize o arquivo terraform/aws/main.tf para usar o bucket correto" -ForegroundColor White
Write-Host "   2. Execute o workflow CI/CD no GitHub" -ForegroundColor White
Write-Host "   3. Verifique se o deploy funciona corretamente" -ForegroundColor White
Write-Host ""
Write-Host "💡 Para testar as permissões:" -ForegroundColor Cyan
Write-Host "   aws lambda list-functions" -ForegroundColor White
Write-Host "   aws iam list-attached-user-policies --user-name $USER_NAME" -ForegroundColor White 