# 🚀 Guia Completo de Deploy - Projeto VM Serverless

## 📋 **Resumo do Projeto**

Sistema automatizado de agregação de notícias usando AWS Lambda, MongoDB Atlas e EventBridge. **Custo: $5-8/mês** com **zero manutenção**.

## 🎯 **Próximos Passos (1-2-3-4-5)**

### **Passo 1: Configurar MongoDB Atlas (Gratuito)**

1. **Criar conta**: https://www.mongodb.com/atlas
2. **Criar cluster M0** (gratuito) na região us-east-1
3. **Configurar usuário**: `projeto-vm-user` com senha forte
4. **Network Access**: `0.0.0.0/0` (permite acesso de qualquer lugar)
5. **Obter connection string** e guardar

**Guia detalhado**: `scripts/setup_mongodb_atlas.md`

### **Passo 2: Configurar Variáveis de Ambiente**

#### **Obrigatórias:**
```bash
export AWS_ACCESS_KEY_ID=sua_access_key
export AWS_SECRET_ACCESS_KEY=sua_secret_key
export MONGO_URI=mongodb+srv://projeto-vm-user:senha@cluster.mongodb.net/?retryWrites=true&w=majority
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

Se preferir fazer deploy local:

```bash
# Linux/Mac
./scripts/deploy_complete.sh

# Windows (PowerShell)
bash scripts/deploy_complete.sh
```

### **Passo 5: Verificar e Monitorar**

1. **Executar verificação**:
   ```bash
   python3 scripts/monitor_deployment.py
   ```

2. **Confirmar email SNS**:
   - Verifique seu email
   - Clique no link de confirmação

3. **Monitorar no CloudWatch**:
   - https://console.aws.amazon.com/cloudwatch
   - Verificar logs das Lambdas

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

### **Monitoramento:**
- **SNS Topic** para alertas por email
- **CloudWatch Alarms** para erros
- **Logs estruturados** para debugging

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

### **Erro de Conexão MongoDB:**
```bash
# Testar conexão
python3 -c "
from pymongo import MongoClient
client = MongoClient('sua_connection_string')
print('Conexão OK!')
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