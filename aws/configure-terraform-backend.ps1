# =============================================================================
# CONFIGURAR BACKEND S3 DO TERRAFORM
# =============================================================================

param(
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "🔧 Configurando backend S3 do Terraform..." -ForegroundColor Green

# Obter Account ID
try {
    $callerIdentity = aws sts get-caller-identity | ConvertFrom-Json
    $ACCOUNT_ID = $callerIdentity.Account
    Write-Host "✅ Account ID: $ACCOUNT_ID" -ForegroundColor Green
} catch {
    Write-Host "❌ Erro ao obter Account ID" -ForegroundColor Red
    exit 1
}

# Nome do bucket
$BUCKET_NAME = "projeto-vm-terraform-state-$ACCOUNT_ID"

# Verificar se o bucket existe
try {
    $null = aws s3 ls "s3://$BUCKET_NAME"
    Write-Host "✅ Bucket S3 encontrado: $BUCKET_NAME" -ForegroundColor Green
} catch {
    Write-Host "❌ Bucket S3 não encontrado: $BUCKET_NAME" -ForegroundColor Red
    Write-Host "Execute primeiro: .\setup-aws-permissions.ps1" -ForegroundColor Yellow
    exit 1
}

# Atualizar o arquivo main.tf
$terraformFile = "..\terraform\aws\main.tf"
$content = Get-Content $terraformFile -Raw

# Substituir ACCOUNT_ID pelo valor real
$updatedContent = $content -replace "projeto-vm-terraform-state-ACCOUNT_ID", $BUCKET_NAME

# Salvar o arquivo atualizado
Set-Content -Path $terraformFile -Value $updatedContent -Encoding UTF8

Write-Host "✅ Arquivo Terraform atualizado com bucket: $BUCKET_NAME" -ForegroundColor Green

# Verificar se a tabela DynamoDB existe
$TABLE_NAME = "terraform-locks"
try {
    $null = aws dynamodb describe-table --table-name $TABLE_NAME
    Write-Host "✅ Tabela DynamoDB encontrada: $TABLE_NAME" -ForegroundColor Green
} catch {
    Write-Host "❌ Tabela DynamoDB não encontrada: $TABLE_NAME" -ForegroundColor Red
    Write-Host "Execute primeiro: .\setup-aws-permissions.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🎉 Backend S3 configurado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Configuração:" -ForegroundColor Cyan
Write-Host "   ✅ Bucket S3: $BUCKET_NAME" -ForegroundColor White
Write-Host "   ✅ Tabela DynamoDB: $TABLE_NAME" -ForegroundColor White
Write-Host "   ✅ Arquivo: $terraformFile" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Agora você pode executar o workflow CI/CD!" -ForegroundColor Green 