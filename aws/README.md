# AWS CLI v2

This bundle contains a built executable of the AWS CLI v2.

## Installation

To install the AWS CLI v2, run the `install` script:
```
$ sudo ./install 
You can now run: /usr/local/bin/aws --version
```
This will install the AWS CLI v2 at `/usr/local/bin/aws`.  Assuming
`/usr/local/bin` is on your `PATH`, you can now run:
```
$ aws --version
```


### Installing without sudo

If you don't have ``sudo`` permissions or want to install the AWS
CLI v2 only for the current user, run the `install` script with the `-b`
and `-i` options:
```
$ ./install -i ~/.local/aws-cli -b ~/.local/bin
``` 
This will install the AWS CLI v2 in `~/.local/aws-cli` and create
symlinks for `aws` and `aws_completer` in `~/.local/bin`. For more
information about these options, run the `install` script with `-h`:
```
$ ./install -h
```

### Updating

If you run the `install` script and there is a previously installed version
of the AWS CLI v2, the script will error out. To update to the version included
in this bundle, run the `install` script with `--update`:
```
$ sudo ./install --update
```


### Removing the installation

To remove the AWS CLI v2, delete the its installation and symlinks:
```
$ sudo rm -rf /usr/local/aws-cli
$ sudo rm /usr/local/bin/aws
$ sudo rm /usr/local/bin/aws_completer
```
Note if you installed the AWS CLI v2 using the `-b` or `-i` options, you will
need to remove the installation and the symlinks in the directories you
specified.

# Configuração de Permissões AWS

Este diretório contém scripts e configurações para configurar as permissões AWS necessárias para o projeto VM serverless.

## 📋 Pré-requisitos

1. **AWS CLI instalado**
   - **Windows**: Execute `.\install-aws-cli-windows.ps1`
   - **WSL/Linux**: Execute `./install-aws-cli-wsl.sh`
   - **Manual**: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

2. **Terraform instalado (versão >= 1.12.0)**
   - **Windows**: Execute `.\install-terraform-windows.ps1`
   - **WSL/Linux**: Execute `./install-terraform-wsl.sh`
   - **Manual**: https://www.terraform.io/downloads.html

3. **Configurar credenciais AWS**
   ```bash
   aws configure
   ```
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region: `us-east-1`
   - Default output format: `json`

## 🚀 Configuração Automática

### Windows (PowerShell)

1. **Instalar AWS CLI (se necessário):**
   ```powershell
   cd aws
   .\install-aws-cli-windows.ps1
   ```

2. **Instalar Terraform (se necessário):**
   ```powershell
   .\install-terraform-windows.ps1
   ```

3. **Configurar permissões AWS:**
   ```powershell
   .\setup-aws-permissions.ps1
   ```

4. **Configurar backend S3 do Terraform:**
   ```powershell
   .\configure-terraform-backend.ps1
   ```

### WSL/Linux (Bash)

1. **Instalar AWS CLI (se necessário):**
   ```bash
   cd aws
   chmod +x install-aws-cli-wsl.sh
   ./install-aws-cli-wsl.sh
   ```

2. **Instalar Terraform (se necessário):**
   ```bash
   chmod +x install-terraform-wsl.sh
   ./install-terraform-wsl.sh
   ```

3. **Configurar permissões AWS:**
   ```bash
   chmod +x setup-aws-permissions-wsl.sh
   ./setup-aws-permissions-wsl.sh
   ```

4. **Configurar backend S3 do Terraform:**
   ```bash
   chmod +x configure-terraform-backend-wsl.sh
   ./configure-terraform-backend-wsl.sh
   ```

## 📋 O que os scripts fazem

### 1. Política IAM (`iam-policy.json`)
Cria uma política com permissões para:
- **Lambda**: Criar, atualizar, invocar funções
- **IAM**: Criar roles e policies
- **EventBridge**: Criar rules e targets
- **SNS**: Criar topics e subscriptions
- **CloudWatch**: Criar alarms e logs
- **S3**: Gerenciar bucket do Terraform state
- **DynamoDB**: Gerenciar tabela de locks

### 2. Recursos criados
- **Política IAM**: `ProjetoVMPermissions`
- **Grupo IAM**: `ProjetoVMGroup`
- **Bucket S3**: `projeto-vm-terraform-state-{ACCOUNT_ID}`
- **Tabela DynamoDB**: `terraform-locks`

## 🔧 Configuração Manual (Alternativa)

Se preferir configurar manualmente:

### 1. Criar Política IAM
```bash
aws iam create-policy \
    --policy-name ProjetoVMPermissions \
    --policy-document file://iam-policy.json \
    --description "Permissões para projeto VM serverless"
```

### 2. Anexar política ao usuário
```bash
aws iam attach-user-policy \
    --user-name SEU_USUARIO \
    --policy-arn arn:aws:iam::SEU_ACCOUNT_ID:policy/ProjetoVMPermissions
```

### 3. Criar bucket S3
```bash
aws s3 mb s3://projeto-vm-terraform-state-SEU_ACCOUNT_ID --region us-east-1
aws s3api put-bucket-versioning \
    --bucket projeto-vm-terraform-state-SEU_ACCOUNT_ID \
    --versioning-configuration Status=Enabled
```

### 4. Criar tabela DynamoDB
```bash
aws dynamodb create-table \
    --table-name terraform-locks \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

## ✅ Verificação

Após a configuração, teste as permissões:

```bash
# Verificar versões
terraform version
aws --version

# Listar funções Lambda
aws lambda list-functions

# Listar políticas do usuário
aws iam list-attached-user-policies --user-name SEU_USUARIO

# Verificar bucket S3
aws s3 ls s3://projeto-vm-terraform-state-SEU_ACCOUNT_ID

# Verificar tabela DynamoDB
aws dynamodb describe-table --table-name terraform-locks

# Testar Terraform
cd ../terraform/aws
terraform init
terraform plan
```

## 🚨 Troubleshooting

### Erro: Access Denied
- Verifique se as credenciais AWS estão corretas
- Confirme se o usuário tem permissões de administrador ou as permissões específicas

### Erro: Bucket já existe
- O script detecta automaticamente e continua
- Se houver conflito de nomes, use um nome único

### Erro: Tabela já existe
- O script detecta automaticamente e continua
- Se houver conflito, delete a tabela existente primeiro

### Erro: AWS CLI não encontrado
- Execute o script de instalação correspondente ao seu SO
- Reinicie o terminal após a instalação

### Erro: Terraform não encontrado
- Execute o script de instalação correspondente ao seu SO
- Verifique se a versão é >= 1.12.0

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do script
2. Confirme as permissões do usuário AWS
3. Teste comandos AWS individualmente
4. Consulte a documentação AWS IAM

## 🔒 Segurança

- As permissões são específicas para o projeto
- Use o princípio do menor privilégio
- Revise periodicamente as permissões
- Considere usar roles temporárias para produção

## 📁 Estrutura de Arquivos

```
aws/
├── README.md                           # Este arquivo
├── iam-policy.json                     # Política IAM
├── install-aws-cli-windows.ps1         # Instalar AWS CLI (Windows)
├── install-aws-cli-wsl.sh              # Instalar AWS CLI (WSL/Linux)
├── install-terraform-windows.ps1       # Instalar Terraform (Windows)
├── install-terraform-wsl.sh            # Instalar Terraform (WSL/Linux)
├── setup-aws-permissions.ps1           # Configurar permissões (Windows)
├── setup-aws-permissions-wsl.sh        # Configurar permissões (WSL/Linux)
├── configure-terraform-backend.ps1     # Configurar Terraform (Windows)
└── configure-terraform-backend-wsl.sh  # Configurar Terraform (WSL/Linux)
```
