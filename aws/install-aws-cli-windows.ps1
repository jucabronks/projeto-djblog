# =============================================================================
# INSTALAR AWS CLI NO WINDOWS
# =============================================================================

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Função para imprimir com cores
function Write-Status {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "📋 $Message" -ForegroundColor Cyan
}

function Write-Header {
    param([string]$Message)
    Write-Host "🚀 $Message" -ForegroundColor White
}

Write-Header "Instalando AWS CLI no Windows..."

# Verificar se já está instalado
try {
    $awsVersion = aws --version 2>$null
    if ($awsVersion -and -not $Force) {
        Write-Status "AWS CLI já está instalado: $awsVersion"
        Write-Info "Para forçar reinstalação, use: .\install-aws-cli-windows.ps1 -Force"
        exit 0
    }
} catch {
    # AWS CLI não está instalado, continuar
}

# Verificar se winget está disponível
try {
    $null = Get-Command winget -ErrorAction Stop
    Write-Info "Winget encontrado, usando para instalação..."
    
    if ($Force) {
        Write-Info "Removendo instalação existente..."
        winget uninstall -e --id Amazon.AWSCLI 2>$null
    }
    
    Write-Info "Instalando AWS CLI via winget..."
    winget install -e --id Amazon.AWSCLI
    
    Write-Status "AWS CLI instalado via winget"
    
} catch {
    Write-Warning "Winget não disponível, tentando download manual..."
    
    # Download manual
    $tempDir = [System.IO.Path]::GetTempPath()
    $zipFile = Join-Path $tempDir "awscliv2.zip"
    $extractDir = Join-Path $tempDir "awscliv2"
    
    Write-Info "Baixando AWS CLI..."
    
    try {
        Invoke-WebRequest -Uri "https://awscli.amazonaws.com/AWSCLIV2.msi" -OutFile $zipFile
        
        Write-Info "Instalando AWS CLI..."
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i $zipFile /quiet /norestart" -Wait
        
        Write-Status "AWS CLI instalado via MSI"
        
    } catch {
        Write-Error "Falha na instalação manual"
        Write-Info "Tente instalar manualmente:"
        Write-Info "1. Baixe de: https://awscli.amazonaws.com/AWSCLIV2.msi"
        Write-Info "2. Execute o instalador"
        exit 1
    } finally {
        # Limpar arquivos temporários
        if (Test-Path $zipFile) { Remove-Item $zipFile -Force }
        if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
    }
}

# Verificar instalação
try {
    # Atualizar PATH temporariamente
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
    
    $awsVersion = aws --version
    Write-Status "AWS CLI instalado com sucesso: $awsVersion"
} catch {
    Write-Warning "AWS CLI instalado, mas pode precisar reiniciar o terminal"
    Write-Info "Reinicie o PowerShell ou abra um novo terminal"
}

echo ""
Write-Header "Instalação concluída!"
echo ""
Write-Info "Próximos passos:"
echo "   1. Configure suas credenciais: aws configure"
echo "   2. Execute: .\setup-aws-permissions.ps1"
echo "   3. Execute: .\configure-terraform-backend.ps1"
echo ""
Write-Info "Para configurar credenciais AWS:"
echo "   aws configure"
echo "   # AWS Access Key ID: [sua-access-key]"
echo "   # AWS Secret Access Key: [sua-secret-key]"
echo "   # Default region name: us-east-1"
echo "   # Default output format: json" 