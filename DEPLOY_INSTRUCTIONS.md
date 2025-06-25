# 🚀 Guia Completo de Deploy - Projeto VM Serverless

## 📋 **Resumo do Projeto**

Sistema automatizado de agregação de notícias usando AWS Lambda, DynamoDB e EventBridge. **Custo: $3-5/mês** com **zero manutenção**.

## 🎯 **Próximos Passos (1-2-3-4-5)**

### **Passo 1: Configurar DynamoDB (Automático)**

**As tabelas DynamoDB são criadas automaticamente via Terraform!**
- ✅ **Zero configuração manual**
- ✅ **100% serverless** 
- ✅ **Auto-scaling automático**
- ✅ **Pay-per-request** - você só paga pelo que usar

### **Passo 2: Configurar Variáveis de Ambiente**

#### **Obrigatórias:**
```bash
export AWS_ACCESS_KEY_ID=sua_access_key
export AWS_SECRET_ACCESS_KEY=sua_secret_key
export AWS_REGION=us-east-1
export DYNAMODB_TABLE_NAME=djblog-noticias
export ALARM_EMAIL=seu@email.com
```

#### **Opcionais:**
```bash
export OPENAI_API_KEY=sk-...  # Para resumos com IA
export WP_URL=https://seu-site.com  # Para publicação
export WP_USER=admin
export WP_APP_PASSWORD=senha-app
```

### **Passo 3: Deploy via GitHub Actions (Recomendado)**

1. **Configurar Secrets no GitHub**:
   - Vá para Settings → Secrets and variables → Actions
   - Adicione todos os secrets listados em `scripts/setup_github_secrets.md`

2. **Fazer Push para main**:
   ```bash
   git add .
   git commit -m "Deploy serverless otimizado"
   git push origin main
   ```

3. **Monitorar o Deploy**:
   - Vá para Actions no GitHub
   - Acompanhe a execução do workflow "Deploy to AWS"

### **Passo 4: Deploy Local (Alternativo)**

Se preferir fazer deploy local, os scripts detectam automaticamente o ambiente e instalam dependências:

#### **Windows (PowerShell)**:
```powershell
# Execute no PowerShell (não precisa ser Administrador)
.\scripts\deploy_local.ps1

# Apenas testes
.\scripts\deploy_local.ps1 -Test

# Ver ajuda
.\scripts\deploy_local.ps1 -Help
```

#### **WSL/Linux/MacOS**:
```bash
# Torna o script executável e executa
chmod +x scripts/deploy_local.sh
./scripts/deploy_local.sh

# O script detecta automaticamente:
# - Se está no WSL, Linux ou macOS
# - Qual comando Python usar (python3/python)
# - Instala dependências automaticamente se necessário
```

**🔧 Os scripts fazem automaticamente:**
- ✅ Detectam Python 3.8+ disponível  
- ✅ Instalam dependências se necessário
- ✅ Executam testes completos
- ✅ Validam credenciais AWS
- ✅ Fazem deploy via Terraform

### **Passo 5: Verificar e Monitorar**

1. **Executar testes completos**:
   ```bash
   # Windows
   python test_runner.py
   
   # Ou usar script completo
   .\scripts\deploy_local.ps1 -Test
   ```

2. **Confirmar email SNS**:
   - Verifique seu email
   - Clique no link de confirmação

3. **Monitorar no CloudWatch**:
   - https://console.aws.amazon.com/cloudwatch
   - Verificar logs das Lambdas

4. **Testar execução manual**:
   ```bash
   # Testar coletor
   aws lambda invoke \
     --function-name djblog-coletor \
     --payload '{}' \
     --region us-east-1 \
     response.json
   
   # Ver resultado
   cat response.json
   ```

## 🧪 **Guia Completo de Testes**

**📖 Para testes detalhados, veja: [`TESTING_GUIDE.md`](TESTING_GUIDE.md)**

### **Testes Locais Rápidos:**
```bash
# Teste completo automatizado
python test_runner.py

# Apenas validação rápida
python test_runner.py --quick

# Pular testes AWS (desenvolvimento)
python test_runner.py --no-aws
```

### **CI/CD GitHub Actions:**
- ✅ **Automático**: Push para `main` executa testes + deploy
- ✅ **Manual**: Vá para Actions → Run workflow
- ✅ **Monitoramento**: Acompanhe logs em tempo real

## 📊 **O que será criado**

### **Lambda Functions:**
- `coletor-noticias` - Coleta RSS 4x/dia
- `publicador-noticias` - Publica no WordPress
- `limpeza-noticias` - Limpa dados antigos
- `health-check-fontes` - Verifica fontes RSS

### **EventBridge Rules:**
- **Coleta**: 20:00, 20:10, 20:20, 20:30 (BRT)
- **Resumo**: 20:35 (BRT)
- **Publicação**: 6:40 (BRT) - Seg, Ter, Qua, Sex
- **Limpeza**: Domingo 3:00 (BRT)
- **Health Check**: Diário

### **DynamoDB Tables:**
- `djblog-noticias` - Tabela principal de notícias
- `djblog-noticias-resumidas` - Notícias processadas pela IA
- `djblog-fontes` - Configuração de fontes RSS

### **Monitoramento:**
- **SNS Topic** para alertas por email  
- **CloudWatch Alarms** para erros
- **Logs estruturados** para debugging
- **Métricas DynamoDB** para performance

## 🔧 **Configurações Personalizáveis**

### **Agendamentos (EventBridge)**
Edite em `terraform/aws/main.tf`:
```hcl
schedule_expression = "cron(0,10,20,30 23 * * ? *)"  # 20h, 20h10, 20h20, 20h30 BRT
```

### **Nichos de Notícias**
Edite em `terraform/aws/terraform.tfvars`:
```hcl
nicho_lista = ["saude", "esportes", "tecnologia", "economia"]
```

### **Configurações Lambda**
Edite em `terraform/aws/main.tf`:
```hcl
memory_size = 512  # Memória em MB
timeout     = 300  # Timeout em segundos
```

## 📈 **Monitoramento Contínuo**

### **Alertas Automáticos:**
- Email em caso de erro nas Lambdas
- Notificação de health check diário
- Logs no CloudWatch

### **Métricas Importantes:**
- Número de execuções por dia
- Duração das execuções
- Taxa de erro
- Uso de memória

### **Dashboard CloudWatch:**
- Acesse: https://console.aws.amazon.com/cloudwatch
- Vá para Dashboards
- Crie dashboard personalizado

## 🛠️ **Troubleshooting**

### **Erro "python: command not found" no WSL/Linux:**

**✅ Solução Automática** - Os scripts agora detectam e instalam Python automaticamente!

1. **Execute o script novamente**:
   ```bash
   chmod +x scripts/deploy_local.sh
   ./scripts/deploy_local.sh
   ```

2. **Se ainda houver problemas, configure manualmente**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   
   # Criar alias (opcional)
   echo "alias python=python3" >> ~/.bashrc
   echo "alias pip=pip3" >> ~/.bashrc
   source ~/.bashrc
   ```

### **Erro "python: command not found" no Windows:**

1. **Execute no PowerShell**:
   ```powershell
   .\scripts\deploy_local.ps1
   ```

2. **Se Python não estiver instalado**:
   - Baixe em: https://python.org/downloads
   - Ou use Microsoft Store: `winget install Python.Python.3.11`
   - Ou use Chocolatey: `choco install python`

### **Testando em Ambos os Ambientes:**

```bash
# WSL/Linux
./scripts/deploy_local.sh

# PowerShell (na mesma máquina)
.\scripts\deploy_local.ps1 -Test
```

### **Erro de Conexão DynamoDB:**
```bash
# Testar conexão
python3 -c "
import boto3
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('djblog-noticias')
print('Conexão DynamoDB OK!')
"
```

### **Lambda não executa:**
1. Verificar logs no CloudWatch
2. Verificar permissões IAM
3. Verificar variáveis de ambiente

### **EventBridge não dispara:**
1. Verificar regras no console AWS
2. Verificar timezone (America/Sao_Paulo)
3. Verificar permissões Lambda

### **Erro de timeout:**
1. Aumentar timeout da Lambda
2. Aumentar memória
3. Otimizar código

## 💰 **Controle de Custos**

### **Monitoramento de Custos:**
- AWS Cost Explorer: https://console.aws.amazon.com/cost-management
- Configure alertas de billing
- Monitore uso mensal

### **Otimizações:**
- Reduzir timeout das Lambdas
- Otimizar uso de memória
- Configurar retenção de logs

### **Custo Esperado:**
- **Lambda**: $2-4/mês
- **EventBridge**: $1/mês
- **CloudWatch**: $0.50/mês
- **SNS**: $0.10/mês
- **S3/DynamoDB**: $0.30/mês
- **Total**: $5-8/mês

## 🎉 **Próximos Passos Após Deploy**

1. **Configurar fontes de notícias** via interface web
2. **Testar coleta manual** via console AWS
3. **Ajustar agendamentos** se necessário
4. **Configurar WordPress** para publicação
5. **Monitorar primeiras execuções**

## 📞 **Suporte**

### **Logs Úteis:**
- CloudWatch Logs: `/aws/lambda/coletor-noticias`
- GitHub Actions: Actions tab
- Terraform: `terraform/aws/terraform.tfstate`

### **Comandos Úteis:**
```bash
# Verificar status das Lambdas
aws lambda list-functions --region us-east-1

# Verificar regras EventBridge
aws events list-rules --region us-east-1

# Verificar logs recentes
aws logs describe-log-groups --region us-east-1
```

---

**🎯 Resultado Final: Sistema 100% automatizado com custo mínimo e zero manutenção!** 