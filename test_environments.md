# 🧪 Teste dos Scripts em Diferentes Ambientes

## Como Testar Ambos os Ambientes

### 1. **No WSL/Linux** (dentro do Windows):
```bash
# Entrar no WSL
wsl

# Navegar para o projeto
cd /mnt/c/Users/dgajr/OneDrive/Área\ de\ Trabalho/projeto-djblog

# Tornar executável e executar
chmod +x scripts/deploy_local.sh
./scripts/deploy_local.sh
```

### 2. **No PowerShell** (Windows nativo):
```powershell
# No PowerShell (já deve estar na pasta)
.\scripts\deploy_local.ps1 -Test
```

## ✅ Scripts Agora Suportam

### **Deploy Local Bash (`scripts/deploy_local.sh`)**:
- ✅ **Auto-detecta**: `python3`, `python`, ou instala automaticamente
- ✅ **Ambientes**: WSL, Ubuntu, Debian, Red Hat, CentOS, macOS
- ✅ **Auto-instala**: Python 3.8+ se não estiver disponível
- ✅ **Dependências**: Instala pip packages automaticamente

### **Deploy Local PowerShell (`scripts/deploy_local.ps1`)**:
- ✅ **Auto-detecta**: `python3`, `python`, `py -3` (py launcher)
- ✅ **Ambientes**: Windows 10/11, PowerShell 5.1+
- ✅ **Compatível**: WSL dentro do Windows
- ✅ **Dependências**: Instala pip packages automaticamente

## 🎯 Comandos de Teste Rápido

```bash
# WSL - Apenas teste
./scripts/deploy_local.sh

# PowerShell - Apenas teste  
.\scripts\deploy_local.ps1 -Test

# PowerShell - Deploy completo
.\scripts\deploy_local.ps1

# Ver ajuda
.\scripts\deploy_local.ps1 -Help
```

## 🔧 O que os Scripts Fazem Automaticamente

1. **Detectam Python** disponível no sistema
2. **Instalam Python** se necessário (apenas Linux/WSL)
3. **Instalam dependências** via pip
4. **Executam testes** completos
5. **Validam AWS** credentials  
6. **Fazem deploy** via Terraform

## 💡 Próximos Passos

Agora você pode executar o deploy/testes em **qualquer ambiente**:
- ✅ **WSL** no Windows
- ✅ **PowerShell** no Windows  
- ✅ **Linux** nativo
- ✅ **macOS** com Homebrew

Sem necessidade de configuração manual de Python!
