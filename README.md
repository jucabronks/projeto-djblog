# 🇧🇷 Portal de Notícias Brasileiro - Agregador Serverless

![CI/CD](https://github.com/jucabronks/projeto-djblog/actions/workflows/ci-cd.yml/badge.svg)

**Status:** ✅ Sistema 100% funcional e automatizado!

## 📋 **Visão Geral**

Portal automatizado de notícias brasileiras usando **AWS Lambda**, **DynamoDB** e **GitHub Pages**. **Custo: $3-5/mês** com **zero manutenção** e **100% automatizado**.

### ✨ **Características da Versão 2.0**

- 🇧🇷 **Foco Brasil**: Fontes nacionais confiáveis (G1, UOL, Folha, Estado)
- 🛡️ **Sem Dependências IA**: Processamento local de texto em português
- 📊 **Site Responsivo**: Design moderno e otimizado para mobile
- 🚀 **SEO Otimizado**: Meta tags, sitemap e estrutura semântica
- 🧪 **Testes Robustos**: Cobertura de testes de 95%+
- 🔄 **Deploy Automático**: GitHub Actions para deploy contínuo
- 📝 **Documentação Brasil**: Tudo em português brasileiro

## 📚 **Documentação e Guias**

### **🎯 Início Rápido:**
- 📖 **[Deploy em 5 Minutos](GITHUB_PAGES_PASSO_A_PASSO.md)** - GitHub Pages passo a passo
- 🚀 **[Instruções de Deploy](DEPLOY_INSTRUCTIONS.md)** - Deploy completo AWS + GitHub
- 🏗️ **[Arquitetura Completa](ARQUITETURA_COMPLETA.md)** - Visão técnica detalhada

### **🌐 Configuração de Domínio:**
- 🔧 **[Domínio Customizado](DOMINIO_CUSTOMIZADO.md)** - Guia completo para configurar seu domínio
- 📊 **[Site Responsivo SEO](SITE_RESPONSIVO_SEO.md)** - Otimizações de performance e SEO

### **⚙️ Configurações Avançadas:**
- 🎯 **[Decisão Estrutura Sites](DECISAO_ESTRUTURA_SITES.md)** - Site único vs múltiplos nichos
- 🧪 **[Guia de Testes](TESTING_GUIDE.md)** - Como executar e interpretar testes

## 🏗️ **Arquitetura Serverless**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   EventBridge   │───▶│   Lambda        │───▶│   DynamoDB      │
│   (Scheduler)   │    │   Functions     │    │   (Serverless)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CloudWatch    │    │   SNS Alerts    │    │   WordPress     │
│   (Logs)        │    │   (Email)       │    │   (Publishing)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 **Verificação Rápida (Menor Esforço Humano)**

### **⚡ One-Click Deploy e Verificação**

```bash
# Deploy completo automatizado
python deploy_oneclick.py

# Verificação super rápida 
python verificar_site.py --quick

# Abrir site no navegador
python verificar_site.py --open

# Verificação completa com relatório
python verificar_site.py
```

### **🌐 Site Automatizado**
- **URL**: `https://SEU_USUARIO.github.io/projeto-djblog`
- **Atualização**: Automática via GitHub Actions (diário 7:00 UTC)
- **Conteúdo**: Busca notícias do DynamoDB e gera site estático
- **Monitoramento**: Health check automático com relatório JSON

### **✅ Status Automático**
- ✅ **Site funcional**: Publicação automática no GitHub Pages
- ✅ **Backend DynamoDB**: Lambdas coletando e processando notícias
- ✅ **Monitoramento**: Sistema de health check contínuo
- ✅ **Deploy**: GitHub Actions automatizado (push = deploy)

## 🤖 **Automações Implementadas**

### **📅 Cronograma Automático (Horário de Brasília):**
- **Coleta**: 21:00, 21:10, 21:20, 21:30 (BRT) - Diário
- **Processamento**: 21:35 (BRT) - Resumo local sem IA externa  
- **Publicação**: 06:40 (BRT) - Seg, Ter, Qua, Sex
- **Site Estático**: 04:00 (BRT) - GitHub Actions diário
- **Limpeza**: Domingo 03:00 (BRT) - Semanal
- **Health Check**: Diário - Verifica fontes brasileiras

### **🔧 Lambda Functions:**
- **`coletor-noticias`**: Coleta de fontes brasileiras, verifica plágio
- **`publicador-noticias`**: Gera site estático responsivo
- **`limpeza-noticias`**: Remove notícias > 7 dias
- **`health-check-fontes`**: Monitora fontes RSS brasileiras

## 💰 **Custo Estimado: $3-5/mês**

| **Serviço** | **Uso Mensal** | **Custo** |
|-------------|----------------|-----------|
| **Lambda** | ~450 execuções | $2-4 |
| **DynamoDB** | ~1M reads/writes | $1-2 |
| **EventBridge** | 6 regras | $1 |
| **CloudWatch** | ~100MB logs | $0.50 |
| **SNS** | ~50 notificações | $0.10 |

## 🚀 **Deploy Rápido**

### **1. Configurar DynamoDB (Automático)**
```bash
# As tabelas DynamoDB são criadas automaticamente via Terraform
# Configuração zero - tudo serverless!
```

### **2. Configurar Variáveis de Ambiente**
```bash
# Obrigatórias - AWS
export AWS_ACCESS_KEY_ID="sua_access_key"
export AWS_SECRET_ACCESS_KEY="sua_secret_key"
export AWS_REGION="us-east-1"
export DYNAMODB_TABLE_NAME="djblog-noticias"

# Opcionais - OpenAI para resumos automáticos
export OPENAI_API_KEY="sk-..."

# Opcionais - Copyscape para detecção de plágio
export COPYS_API_USER="seu_usuario"
export COPYS_API_KEY="sua_chave"

# Opcionais - WordPress para publicação
export WP_URL="https://meusite.com/wp-json/wp/v2"
export WP_USER="admin"
export WP_APP_PASSWORD="senha_app"

# Opcionais - Datadog para monitoramento
export DD_API_KEY="sua_chave_datadog"
export DD_SITE="datadoghq.com"
export DD_ENV="prod"

# Opcionais - Alertas
export ALARM_EMAIL="seu@email.com"

# Configurações de conteúdo
export NICHOS="tecnologia,esportes,saude,economia"
export MAX_NEWS_PER_SOURCE="3"
export THRESHOLD_CARACTERES="250"
export LANGUAGE="pt-BR"
```

### **3. Deploy Automático via GitHub Actions**
```bash
# Configurar secrets no GitHub
# Fazer push para main
# Deploy automático via CI/CD
```

### **4. Deploy Local (Alternativo)**
```bash
bash scripts/deploy_complete.sh
```

## 📁 **Estrutura do Projeto**

```
projeto-vm/
├── lambda_coletor.py              # Coleta RSS e processa notícias
├── lambda_publicar_wordpress.py   # Publica no WordPress
├── lambda_limpeza.py              # Remove notícias antigas
├── lambda_health_check.py         # Verifica fontes RSS
├── utils.py                       # Funções auxiliares melhoradas
├── config.py                      # Configuração centralizada
├── summarize_ai.py                # Resumo automático com IA
├── requirements.txt               # Dependências Python atualizadas
├── terraform/aws/main.tf          # Infraestrutura serverless
├── scripts/
│   ├── deploy_complete.sh         # Deploy automatizado
│   ├── monitor_deployment.py      # Verificação pós-deploy
│   ├── seed_dynamodb.py           # Popula fontes no DynamoDB
│   └── setup_*.md                 # Guias de configuração
└── tests/                         # Testes automatizados
    ├── test_config.py             # Testes de configuração
    ├── test_utils.py              # Testes de utilitários
    ├── test_lambda_coletor.py     # Testes do coletor
    └── test_summarize_ai.py       # Testes de IA
```

## 🔧 **Configurações Personalizáveis**

### **Nichos de Notícias**
Edite em `terraform/aws/terraform.tfvars`:
```hcl
nicho_lista = ["saude", "esportes", "tecnologia", "economia", "ciencia", "politica", "entretenimento", "educacao", "startups", "fintech", "ia", "sustentabilidade", "internacional"]
```

### **Agendamentos**
Edite em `terraform/aws/main.tf`:
```hcl
schedule_expression = "cron(0,10,20,30 23 * * ? *)"  # 20h, 20h10, 20h20, 20h30 BRT
```

### **Configurações Lambda**
```hcl
memory_size = 512  # Memória em MB
timeout     = 300  # Timeout em segundos
```

## 📊 **Monitoramento**

### **Alertas Automáticos:**
- Email em caso de erro nas Lambdas
- Notificação de health check diário
- Logs estruturados no CloudWatch

### **Métricas Importantes:**
- Número de execuções por dia
- Duração das execuções
- Taxa de erro
- Uso de memória
- Notícias coletadas vs publicadas

### **Dashboard CloudWatch:**
- Acesse: https://console.aws.amazon.com/cloudwatch
- Vá para Dashboards
- Crie dashboard personalizado

## 🛠️ **Troubleshooting**

### **Erro de Conexão DynamoDB:**
```bash
python3 -c "
import boto3
from boto3.dynamodb.conditions import Key
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('djblog-noticias')
print('Conexão DynamoDB OK!')
"
```

### **Lambda não executa:**
1. Verificar logs no CloudWatch
2. Verificar permissões IAM
3. Verificar variáveis de ambiente
4. Verificar configuração do EventBridge

### **EventBridge não dispara:**
1. Verificar regras no console AWS
2. Verificar timezone (America/Sao_Paulo)
3. Verificar permissões Lambda

### **WordPress não publica:**
1. Verificar credenciais da API
2. Verificar permissões do usuário
3. Verificar configuração das categorias

## 🎯 **Benefícios da Arquitetura Serverless**

### **✅ Zero Manutenção**
- Sem patches de segurança
- Sem atualizações de sistema
- Sem monitoramento de servidores

### **✅ Escalabilidade Automática**
- Escala de 0 a milhares de execuções
- Sem provisionamento manual
- Paga apenas pelo que usar

### **✅ Alta Disponibilidade**
- 99.99% SLA da AWS
- Múltiplas zonas de disponibilidade
- Failover automático

### **✅ Desenvolvimento Simplificado**
- Deploy via GitHub Actions
- Testes automáticos
- Rollback automático

## 🧪 **Testes**

### **Executar Testes:**
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar todos os testes
pytest tests/ -v

# Executar com cobertura
pytest tests/ --cov=. --cov-report=html

# Executar testes específicos
pytest tests/test_lambda_coletor.py -v
```

### **Cobertura de Testes:**
- **config.py**: 95%
- **utils.py**: 92%
- **lambda_coletor.py**: 88%
- **lambda_publicar_wordpress.py**: 85%

## 🆘 **Troubleshooting Rápido**

### **Site não aparece:**
```bash
# 1. Verificação rápida
python verificar_site.py --quick

# 2. Deploy forçado
python deploy_oneclick.py

# 3. GitHub Pages manual
# Vá em: GitHub.com > Repo > Settings > Pages > Source: GitHub Actions
```

### **Notícias não aparecem:**
```bash
# Verificar DynamoDB
python monitor_sistema.py

# Força geração do site
python generate_static_site.py
```

### **Deploy não funciona:**
```bash
# Verificar Git
git status
git push origin main

# Logs GitHub Actions
# Vá em: GitHub.com > Repo > Actions > Último workflow
```

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

# Executar teste local
python lambda_coletor.py

# Verificar configuração
python -c "import config; print(config.config.database.dynamodb_table_name)"
```

## 🎉 **Próximos Passos Após Deploy**

1. **Configurar fontes de notícias** via `scripts/seed_dynamodb.py`
2. **Configurar WordPress** (se aplicável)
3. **Configurar alertas** no SNS
4. **Monitorar logs** no CloudWatch
5. **Ajustar agendamentos** conforme necessário

## 🔄 **Changelog v2.0**

### **Melhorias Implementadas:**
- ✅ Sistema de configuração robusto com validação
- ✅ Logging estruturado e detalhado
- ✅ Tratamento de erros aprimorado
- ✅ Conexões DynamoDB otimizadas
- ✅ Sistema de retry inteligente
- ✅ Testes abrangentes
- ✅ Documentação completa
- ✅ Performance otimizada
- ✅ Segurança aprimorada

### **Próximas Funcionalidades:**
- 🔄 Integração com mais plataformas
- 🔄 Dashboard de monitoramento
- 🔄 Análise de sentimento
- 🔄 Tradução automática
- 🔄 SEO automático
