# =============================================================================
# INSTALAR TERRAFORM NO WINDOWS
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

Write-Header "Instalando Terraform no Windows..."

# Verificar se já está instalado
try {
    $terraformVersion = terraform version -json 2>$null | ConvertFrom-Json
    if ($terraformVersion -and -not $Force) {
        $version = $terraformVersion.terraform_version
        Write-Status "Terraform já está instalado: $version"
        
        # Verificar se a versão é compatível
        $requiredVersion = "1.12.0"
        if ([System.Version]$version -ge [System.Version]$requiredVersion) {
            Write-Status "Versão compatível! ✅"
            exit 0
        } else {
            Write-Warning "Versão antiga detectada. Atualizando..."
        }
    }
} catch {
    # Terraform não está instalado, continuar
}

# Verificar se winget está disponível
try {
    $null = Get-Command winget -ErrorAction Stop
    Write-Info "Winget encontrado, usando para instalação..."
    
    if ($Force) {
        Write-Info "Removendo instalação existente..."
        winget uninstall -e --id HashiCorp.Terraform 2>$null
    }
    
    Write-Info "Instalando Terraform via winget..."
    winget install -e --id HashiCorp.Terraform
    
    Write-Status "Terraform instalado via winget"
    
} catch {
    Write-Warning "Winget não disponível, tentando download manual..."
    
    # Download manual
    $tempDir = [System.IO.Path]::GetTempPath()
    $zipFile = Join-Path $tempDir "terraform.zip"
    $extractDir = Join-Path $tempDir "terraform"
    
    Write-Info "Baixando Terraform..."
    
    try {
        # Obter versão mais recente
        $checkpointResponse = Invoke-RestMethod -Uri "https://checkpoint-api.hashicorp.com/v1/check/terraform"
        $latestVersion = $checkpointResponse.current_version
        
        Write-Info "Versão mais recente: $latestVersion"
        
        # Baixar Terraform
        $downloadUrl = "https://releases.hashicorp.com/terraform/${latestVersion}/terraform_${latestVersion}_windows_amd64.zip"
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile
        
        Write-Info "Extraindo Terraform..."
        
        # Criar diretório de extração
        if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
        New-Item -ItemType Directory -Path $extractDir -Force | Out-Null
        
        # Extrair arquivo
        Expand-Archive -Path $zipFile -DestinationPath $extractDir -Force
        
        # Mover para diretório no PATH
        $terraformExe = Join-Path $extractDir "terraform.exe"
        $targetDir = "$env:USERPROFILE\terraform"
        
        if (Test-Path $targetDir) { Remove-Item $targetDir -Recurse -Force }
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        
        Copy-Item $terraformExe $targetDir -Force
        
        # Adicionar ao PATH do usuário
        $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($userPath -notlike "*$targetDir*") {
            [Environment]::SetEnvironmentVariable("PATH", "$userPath;$targetDir", "User")
            $env:PATH = "$env:PATH;$targetDir"
        }
        
        Write-Status "Terraform instalado manualmente"
        
    } catch {
        Write-Error "Falha na instalação manual"
        Write-Info "Tente instalar manualmente:"
        Write-Info "1. Baixe de: https://www.terraform.io/downloads.html"
        Write-Info "2. Extraia e adicione ao PATH"
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
    
    $terraformVersion = terraform version -json | ConvertFrom-Json
    $version = $terraformVersion.terraform_version
    Write-Status "Terraform instalado com sucesso: $version"
} catch {
    Write-Warning "Terraform instalado, mas pode precisar reiniciar o terminal"
    Write-Info "Reinicie o PowerShell ou abra um novo terminal"
}

echo ""
Write-Header "Instalação concluída!"
echo ""
Write-Info "Para testar o Terraform:"
echo "   terraform version"
echo "   terraform --help"
echo ""
Write-Info "Próximos passos:"
echo "   1. Configure AWS CLI: .\install-aws-cli-windows.ps1"
echo "   2. Configure permissões: .\setup-aws-permissions.ps1"
echo "   3. Configure backend: .\configure-terraform-backend.ps1" 