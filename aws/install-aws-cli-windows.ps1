# =============================================================================
# INSTALAR AWS CLI NO WINDOWS
# =============================================================================

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-WarningMsg {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Header {
    param([string]$Message)
    Write-Host "==== $Message ====" -ForegroundColor White
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
$wingetOk = $false
try {
    $null = Get-Command winget -ErrorAction Stop
    $wingetOk = $true
} catch {}

if ($wingetOk) {
    Write-Info "Winget encontrado, usando para instalação..."
    if ($Force) {
        Write-Info "Removendo instalação existente..."
        winget uninstall -e --id Amazon.AWSCLI 2>$null
    }
    Write-Info "Instalando AWS CLI via winget..."
    winget install -e --id Amazon.AWSCLI
    Write-Status "AWS CLI instalado via winget"
} else {
    Write-WarningMsg "Winget não disponível, tentando download manual..."
    $tempDir = [System.IO.Path]::GetTempPath()
    $msiFile = Join-Path $tempDir "awscliv2.msi"
    Write-Info "Baixando AWS CLI..."
    try {
        Invoke-WebRequest -Uri "https://awscli.amazonaws.com/AWSCLIV2.msi" -OutFile $msiFile
        Write-Info "Instalando AWS CLI..."
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i $msiFile /quiet /norestart" -Wait
        Write-Status "AWS CLI instalado via MSI"
    } catch {
        Write-ErrorMsg "Falha na instalação manual"
        Write-Info "Tente instalar manualmente:"
        Write-Info "1. Baixe de: https://awscli.amazonaws.com/AWSCLIV2.msi"
        Write-Info "2. Execute o instalador"
        exit 1
    } finally {
        if (Test-Path $msiFile) { Remove-Item $msiFile -Force }
    }
}

# Verificar instalação
try {
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
    $awsVersion = aws --version
    Write-Status "AWS CLI instalado com sucesso: $awsVersion"
} catch {
    Write-WarningMsg "AWS CLI instalado, mas pode precisar reiniciar o terminal"
    Write-Info "Reinicie o PowerShell ou abra um novo terminal"
}

Write-Host ""
Write-Header "Instalação concluída!"
Write-Host ""
Write-Info "Próximos passos:"
Write-Host "   1. Configure suas credenciais: aws configure"
Write-Host "   2. Execute: .\setup-aws-permissions.ps1"
Write-Host "   3. Execute: .\configure-terraform-backend.ps1"
Write-Host ""
Write-Info "Para configurar credenciais AWS:"
Write-Host "   aws configure"
Write-Host "   # AWS Access Key ID: [sua-access-key]"
Write-Host "   # AWS Secret Access Key: [sua-secret-key]"
Write-Host "   # Default region name: us-east-1"
Write-Host "   # Default output format: json" 