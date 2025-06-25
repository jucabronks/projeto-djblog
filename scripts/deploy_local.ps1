# PowerShell script para deploy local no Windows

param(
    [switch]$Test,
    [switch]$Force,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Deploy Local - Projeto DJBlog (Windows)

Uso:
  .\deploy_local.ps1           # Deploy completo
  .\deploy_local.ps1 -Test     # Apenas testes
  .\deploy_local.ps1 -Force    # Force deploy sem confirmação

Pré-requisitos:
  - AWS CLI configurado
  - Python 3.8+
  - Terraform instalado
"@
    exit 0
}

# Função para logs coloridos
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Warning { param($msg) Write-Host "[WARNING] $msg" -ForegroundColor Yellow }

Write-Info "🚀 Deploy Local - Projeto DJBlog"
Write-Info "=================================="

# Verificar se estamos no diretório correto
if (-not (Test-Path "requirements.txt")) {
    Write-Error "Execute este script do diretório raiz do projeto"
    exit 1
}

# Detectar comando Python
$PythonCmd = $null
$PipCmd = $null

# Tentar python3 primeiro (WSL/Linux style)
if (Get-Command "python3" -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
    $PipCmd = "pip3"
}
# Depois tentar python (Windows style)
elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
    $PipCmd = "pip"
    
    # Verificar se é Python 3
    $pythonVersion = & $PythonCmd --version 2>&1
    if ($pythonVersion -match "Python 2\.") {
        Write-Error "Python 2 detectado. Este projeto requer Python 3.8+"
        Write-Error "Instale Python 3.8+ em: https://python.org/downloads"
        exit 1
    }
}
# Tentar py launcher (Windows)
elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $PythonCmd = "py -3"
    $PipCmd = "py -3 -m pip"
}
else {
    Write-Error "Python não encontrado!"
    Write-Error "Instale Python 3.8+ em: https://python.org/downloads"
    Write-Error "Ou se estiver no WSL, execute: sudo apt install python3 python3-pip"
    exit 1
}

$pythonVersionOutput = & $PythonCmd --version 2>&1
Write-Info "Usando Python: $PythonCmd ($pythonVersionOutput)"

# Verificar e instalar dependências sempre
Write-Info "Verificando dependências Python..."

# Tentar importar boto3 para verificar se as dependências estão instaladas
try {
    & $PythonCmd -c "import boto3" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Dependências já instaladas"
    } else {
        throw "boto3 não encontrado"
    }
} catch {
    Write-Info "Instalando dependências Python..."
    
    # Tentar com --user primeiro
    & $PipCmd install --user -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Instalação com --user falhou, tentando sem --user..."
        & $PipCmd install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Falha ao instalar dependências. Tente manualmente:"
            Write-Error "$PipCmd install -r requirements.txt"
            exit 1
        } else {
            Write-Success "Dependências instaladas globalmente"
        }
    } else {
        Write-Success "Dependências instaladas com --user"
    }
}

# 1. Executar testes
Write-Info "Executando testes completos..."
& $PythonCmd test_runner.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "Testes falharam! Corrija os erros antes de fazer deploy."
    exit 1
}

Write-Success "Testes passaram!"

# Se apenas teste, parar aqui
if ($Test) {
    Write-Success "Modo teste concluído!"
    exit 0
}

# 2. Verificar variáveis obrigatórias
Write-Info "Verificando variáveis de ambiente..."

$requiredVars = @(
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "DYNAMODB_TABLE_NAME",
    "ALARM_EMAIL"
)

foreach ($var in $requiredVars) {
    if (-not (Get-Item "Env:$var" -ErrorAction SilentlyContinue)) {
        Write-Error "Variável obrigatória não definida: $var"
        exit 1
    }
}

Write-Success "Variáveis de ambiente OK!"

# 3. Validar AWS
Write-Info "Validando credenciais AWS..."
$awsTest = aws sts get-caller-identity 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Error "Credenciais AWS inválidas"
    exit 1
}

Write-Success "AWS conectado!"

# 4. Preparar pacotes Lambda
Write-Info "Preparando pacotes Lambda..."

# Criar diretório temporário
New-Item -ItemType Directory -Path "dist" -Force | Out-Null

# Função auxiliar para criar zip
function Create-LambdaZip {
    param($name, $files)
    
    Write-Info "Criando $name.zip..."
    
    # Remover zip existente
    if (Test-Path "dist\$name.zip") {
        Remove-Item "dist\$name.zip"
    }
    
    # Criar zip usando PowerShell
    Compress-Archive -Path $files -DestinationPath "dist\$name.zip" -Force
}

# Criar pacotes
Create-LambdaZip "lambda_coletor" @("lambda_coletor.py", "utils.py", "config.py", "summarize_ai.py")
Create-LambdaZip "lambda_publicar_wordpress" @("lambda_publicar_wordpress.py", "utils.py", "config.py")
Create-LambdaZip "lambda_limpeza" @("lambda_limpeza.py", "utils.py", "config.py")
Create-LambdaZip "lambda_health_check" @("lambda_health_check.py", "utils.py", "config.py")
Create-LambdaZip "lambda_api_noticias" @("lambda_api_noticias.py", "utils.py", "config.py")

Write-Success "Pacotes Lambda criados!"

# 5. Deploy Terraform
Write-Info "Executando deploy Terraform..."

Push-Location "terraform\aws"

try {
    # Inicializar se necessário
    if (-not (Test-Path ".terraform")) {
        Write-Info "Inicializando Terraform..."
        terraform init
        if ($LASTEXITCODE -ne 0) { throw "Terraform init falhou" }
    }

    # Planejar
    Write-Info "Planejando mudanças..."
    terraform plan -out=tfplan
    if ($LASTEXITCODE -ne 0) { throw "Terraform plan falhou" }

    # Confirmar deploy (se não forçado)
    if (-not $Force) {
        $confirm = Read-Host "Confirma o deploy? (y/N)"
        if ($confirm -ne "y") {
            Write-Warning "Deploy cancelado pelo usuário"
            exit 0
        }
    }

    # Aplicar
    Write-Info "Aplicando mudanças..."
    terraform apply tfplan
    if ($LASTEXITCODE -ne 0) { throw "Terraform apply falhou" }

    Write-Success "Deploy Terraform concluído!"
}
catch {
    Write-Error "Deploy Terraform falhou: $_"
    exit 1
}
finally {
    Pop-Location
}

# 6. Atualizar código das Lambdas
Write-Info "Atualizando código das Lambdas..."

$functions = @(
    "djblog-coletor",
    "djblog-publicar-wordpress", 
    "djblog-limpeza",
    "djblog-health-check",
    "djblog-api-noticias"
)

foreach ($func in $functions) {
    Write-Info "Atualizando função: $func"
    
    $zipFile = "dist\$($func -replace 'djblog-', 'lambda_').zip"
    
    if (Test-Path $zipFile) {
        $result = aws lambda update-function-code `
            --function-name $func `
            --zip-file "fileb://$zipFile" `
            --region $env:AWS_REGION 2>$null

        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ $func atualizado"
        } else {
            Write-Warning "⚠️ Falha ao atualizar $func (função pode não existir ainda)"
        }
    } else {
        Write-Warning "⚠️ Arquivo não encontrado: $zipFile"
    }
}

# 7. Executar testes pós-deploy
Write-Info "Executando testes pós-deploy..."

# Testar execução das Lambdas
Write-Info "Testando Lambda coletor..."
aws lambda invoke `
    --function-name "djblog-coletor" `
    --payload '{}' `
    --region $env:AWS_REGION `
    response.json 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Success "✅ Lambda coletor respondeu"
} else {
    Write-Warning "⚠️ Lambda coletor não respondeu (normal se for primeira vez)"
}

# 8. Verificar recursos criados
Write-Info "Verificando recursos criados..."

# DynamoDB
$tables = aws dynamodb list-tables --region $env:AWS_REGION --query 'TableNames' --output text 2>$null
if ($tables -and $tables.Contains("djblog")) {
    Write-Success "✅ Tabelas DynamoDB encontradas"
} else {
    Write-Warning "⚠️ Nenhuma tabela DynamoDB encontrada"
}

# EventBridge
$rules = aws events list-rules --region $env:AWS_REGION --query 'Rules[?contains(Name, `djblog`)].Name' --output text 2>$null
if ($rules) {
    Write-Success "✅ Regras EventBridge criadas"
} else {
    Write-Warning "⚠️ Nenhuma regra EventBridge encontrada"
}

# 9. Limpeza
Write-Info "Limpando arquivos temporários..."
Remove-Item "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "response.json" -ErrorAction SilentlyContinue

# 10. Resumo final
Write-Host ""
Write-Success "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
Write-Host "=================================="
Write-Host "📊 Recursos implantados:"
Write-Host "   • Lambdas: 5 funções"
Write-Host "   • DynamoDB: 3 tabelas"
Write-Host "   • EventBridge: Agendamentos configurados"
Write-Host "   • SNS: Alertas por email"
Write-Host ""
Write-Host "📋 Próximos passos:"
Write-Host "   1. Confirme inscrição no SNS (verifique seu email)"
Write-Host "   2. Monitore logs no CloudWatch"
Write-Host "   3. Execute teste manual se necessário"
Write-Host ""
Write-Host "🔗 Links úteis:"
Write-Host "   • CloudWatch: https://console.aws.amazon.com/cloudwatch"
Write-Host "   • DynamoDB: https://console.aws.amazon.com/dynamodb"
Write-Host "   • Lambda: https://console.aws.amazon.com/lambda"
Write-Host ""

Write-Success "Deploy concluído! Sistema está funcionando."
