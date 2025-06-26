# 🧪 **Guia Completo de Testes - Projeto DJBlog**

## 🎯 **Estratégia de Testes**

### **1. Testes Locais (Desenvolvimento)**
### **2. Testes no GitHub (CI/CD)**
### **3. Testes de Deploy (Staging)**
### **4. Testes de Produção (Monitoramento)**

---

## 🏠 **1. Testes Locais**

### **Pré-requisitos:**
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente locais
export AWS_REGION=us-east-1
export DYNAMODB_TABLE_NAME=djblog-noticias-test
export OPENAI_API_KEY=sk-test-key
```

### **Executar Testes:**
```bash
# Todos os testes
pytest tests/ -v

# Testes específicos
pytest tests/test_config.py -v
pytest tests/test_utils.py -v
pytest tests/test_lambda_coletor.py -v

# Com cobertura
pytest tests/ --cov=. --cov-report=html
```

### **Testes Unitários Individuais:**
```bash
# Testar configuração
python -c "from config import get_config; print('Config OK!')"

# Testar utils
python -c "from utils import setup_logging; print('Utils OK!')"

# Testar lambda (mock)
python tests/test_lambda_coletor.py
```

---

## 🚀 **2. CI/CD via GitHub Actions**

### **🔧 Setup Inicial:**

#### **Passo 1: Configurar Secrets no GitHub**
Vá para: `Settings → Secrets and variables → Actions`

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

# Projeto
DYNAMODB_TABLE_NAME=djblog-noticias
ALARM_EMAIL=seu@email.com

# Opcionais
OPENAI_API_KEY=sk-...
WP_URL=https://seu-site.com
WP_USER=admin
WP_APP_PASSWORD=senha-app

# Terraform (se usar S3 backend)
TF_VAR_aws_access_key_id=AKIA...
TF_VAR_aws_secret_access_key=...
```

#### **Passo 2: Verificar Workflow**
O arquivo `.github/workflows/ci-cd.yml` já está configurado para:
- ✅ Executar testes automaticamente
- ✅ Fazer deploy no push para `main`
- ✅ Validar código com lint
- ✅ Gerar artefatos

### **🔄 Processo Automático:**

```bash
# 1. Fazer mudanças no código
git add .
git commit -m "feat: nova funcionalidade"

# 2. Push para triggerar CI/CD
git push origin main
```

### **📊 Monitorar Execução:**
1. Vá para GitHub → Actions
2. Veja o workflow em execução
3. Acompanhe logs em tempo real
4. Verifique se todos os jobs passaram

---

## 🧪 **3. Testes de Deploy (Staging)**

### **Ambiente de Teste:**
```bash
# Criar ambiente staging
export TF_VAR_environment=staging
export TF_VAR_project_name=djblog-staging

# Deploy terraform staging
cd terraform/aws
terraform workspace new staging
terraform plan -var-file=terraform.tfvars.staging
terraform apply
```

### **Testes Pós-Deploy:**
```bash
# Testar Lambdas criadas
aws lambda list-functions --region us-east-1 | grep djblog-staging

# Testar execução manual
aws lambda invoke \
  --function-name djblog-staging-coletor \
  --payload '{}' \
  --region us-east-1 \
  response.json

# Verificar logs
aws logs describe-log-groups --region us-east-1 | grep djblog-staging
```

### **Validação de Infraestrutura:**
```bash
# Verificar DynamoDB
aws dynamodb list-tables --region us-east-1 | grep djblog-staging

# Verificar EventBridge
aws events list-rules --region us-east-1 | grep djblog-staging

# Verificar SNS
aws sns list-topics --region us-east-1 | grep djblog-staging
```

---

## 🎛️ **4. Script de Teste Automatizado**

Vou criar um script completo para você:

```bash
#!/bin/bash

# 1. Testes de Unidade
echo "Executando testes de unidade..."
pytest tests/ -v --disable-warnings

# 2. Testes de Integração
echo "Executando testes de integração..."
pytest tests/integration/ -v --disable-warnings

# 3. Testes de Aceitação
echo "Executando testes de aceitação..."
pytest tests/acceptance/ -v --disable-warnings

# 4. Verificando cobertura de código
echo "Verificando cobertura de código..."
pytest --cov=app --cov-report=html

# 5. Validando estilo de código
echo "Validando estilo de código com flake8..."
flake8 app/ tests/

# 6. Checando segurança com bandit
echo "Checando segurança do código com bandit..."
bandit -r app/

echo "Todos os testes concluídos!"
```

---

## 🔄 **5. Teste Manual de Execução**

### **Testar Lambda Individual:**
```bash
# Coletor
aws lambda invoke \
  --function-name djblog-coletor \
  --payload '{}' \
  --region us-east-1 \
  response.json

# Ver resultado
cat response.json | jq '.'
```

### **Testar DynamoDB:**
```bash
# Listar tabelas
aws dynamodb list-tables --region us-east-1

# Ver itens na tabela principal
aws dynamodb scan \
  --table-name djblog-noticias \
  --region us-east-1 \
  --limit 5
```

### **Monitorar Logs:**
```bash
# Ver logs recentes
aws logs describe-log-groups --region us-east-1 | grep djblog

# Seguir logs em tempo real
aws logs tail /aws/lambda/djblog-coletor --follow --region us-east-1
```

---

## 📱 **6. GitHub Actions - Setup Completo**

### **Secrets Obrigatórios:**
No GitHub, vá para: `Settings → Secrets and variables → Actions`

#### **AWS (Obrigatórios):**
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
ALARM_EMAIL=seu@email.com
```

#### **Projeto (Obrigatórios):**
```
DYNAMODB_TABLE_NAME=djblog-noticias
```

#### **Opcionais (Funcionalidades extras):**
```
OPENAI_API_KEY=sk-...
WP_URL=https://seu-site.com
WP_USER=admin
WP_APP_PASSWORD=senha-app
DD_API_KEY=datadog-key
```

### **Workflow Automático:**
```yaml
# .github/workflows/ci-cd.yml já configurado para:
# ✅ Executar testes em cada push
# ✅ Deploy automático no push para main
# ✅ Validar sintaxe e linting
# ✅ Criar pacotes Lambda
# ✅ Deploy via Terraform
```

### **Monitorar CI/CD:**
1. **Push para main**:
   ```bash
   git add .
   git commit -m "feat: nova funcionalidade"
   git push origin main
   ```

2. **Acompanhar no GitHub**:
   - Vá para `Actions`
   - Veja workflow em execução
   - Monitore logs de cada step

---

## 🚨 **7. Troubleshooting Comum**

### **Erro: "Testes falharam"**
```bash
# Executar testes com mais detalhes
python test_runner.py

# Testar apenas configuração
python -c "from config import get_config; print('OK')"

# Verificar imports
python -c "import boto3, feedparser, requests; print('Deps OK')"
```

### **Erro: "AWS Credentials"**
```bash
# Verificar credenciais
aws sts get-caller-identity

# Configurar se necessário
aws configure

# Testar permissões DynamoDB
aws dynamodb list-tables --region us-east-1
```

### **Erro: "Terraform failed"**
```bash
# Ver logs detalhados
cd terraform/aws
terraform plan -detailed-exitcode

# Resetar estado se necessário
terraform refresh
```

### **Erro: "Lambda timeout"**
```bash
# Ver logs da Lambda
aws logs tail /aws/lambda/djblog-coletor --follow

# Aumentar timeout no Terraform
# resource "aws_lambda_function" {
#   timeout = 300  # 5 minutos
# }
```

---

## 📊 **8. Monitoramento Contínuo**

### **Métricas Importantes:**
- **Execuções por dia**: Deve ser ~4-6 execuções
- **Duração**: < 30 segundos normalmente
- **Taxa de erro**: < 5%
- **Itens DynamoDB**: Crescimento constante

### **Alertas Configurados:**
- ✅ Email quando Lambda falha
- ✅ Notificação de health check
- ✅ Logs no CloudWatch

### **Dashboard Recomendado:**
```bash
# Criar dashboard personalizado no CloudWatch
aws cloudwatch put-dashboard --dashboard-name "DJBlog" --dashboard-body file://dashboard.json
```

---

## 🎯 **9. Comandos de Uso Diário**

### **Execução Rápida de Testes:**
```bash
# Windows
.\scripts\deploy_local.ps1 -Test

# Linux/Mac
python test_runner.py --quick
```

### **Deploy Rápido:**
```bash
# Windows
.\scripts\deploy_local.ps1 -Force

# Linux/Mac  
./scripts/deploy_local.sh
```

### **Monitoramento:**
```bash
# Ver execuções recentes
aws lambda get-function --function-name djblog-coletor

# Contar itens no DynamoDB
aws dynamodb describe-table --table-name djblog-noticias
```

---

## ✨ **10. Resultado Final**

Após configurar tudo, você terá:

### **✅ Sistema 100% Automatizado:**
- Coleta notícias 4x por dia
- Publica automaticamente 
- Limpa dados antigos
- Monitora fontes RSS
- Envia alertas por email

### **✅ Custo Ultra-Baixo ($3-5/mês):**
- DynamoDB pay-per-request
- Lambda apenas quando executa
- Sem custos fixos de servidor

### **✅ CI/CD Profissional:**
- Testes automáticos
- Deploy sem intervenção
- Rollback automático
- Monitoramento integrado

### **✅ Zero Manutenção:**
- Auto-scaling automático
- Backup e recovery automático
- Health checks automáticos
- Logs estruturados

🎉 **Parabéns! Você tem um sistema de notícias totalmente profissional e serverless!**
