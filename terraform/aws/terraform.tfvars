# =============================================================================
# CONFIGURAÇÃO DO PROJETO VM - SERVERLESS
# =============================================================================

# Configurações básicas
aws_region = "us-east-1"
project_name = "projeto-vm"
environment = "dev"

# OpenAI (OPCIONAL - para resumos com IA)
openai_api_key = "sk-..."  # Deixe vazio se não usar OpenAI

# Datadog (OPCIONAL - para monitoramento avançado)
dd_api_key = ""  # Deixe vazio se não usar Datadog
dd_site = "datadoghq.com"
dd_env = "prod"

# Configurações de coleta
nicho = "ciencia"
pais = "Brasil"
max_news_per_source = 3

# Copyscape (OPCIONAL - para verificação de plágio)
copys_api_user = ""  # Deixe vazio se não usar Copyscape
copys_api_key = ""

# Nichos a coletar
nicho_lista = [
  "saude",
  "esportes", 
  "tecnologia",
  "economia"
]

# Mapeamento de nichos para categorias WordPress
categorias_wp = {
  saude      = 2
  esportes   = 3
  tecnologia = 4
  economia   = 5
}

# WordPress (OBRIGATÓRIO - para publicação)
wp_url = "https://seu-site.com"
wp_user = "admin"
wp_app_password = "senha-app-wordpress"

# Email para alertas (OBRIGATÓRIO)
alarm_email = "seu@email.com"

# Tags adicionais
tags = {
  Owner       = "DevOps Team"
  Environment = "dev"
  Project     = "projeto-vm"
}

coletas = [
  {
    pais                = "brasil"
    cron                = "cron(0,10,20,30 23 * * ? *)"
    timezone            = "America/Sao_Paulo"
    nicho               = "tecnologia"
    dynamodb_table_name = "projeto-vm-noticias"
    aws_region          = "us-east-1"
    openai_api_key      = ""
    dd_api_key          = ""
    dd_site             = ""
    dd_env              = ""
    max_news            = 3
    copys_api_user      = ""
    copys_api_key       = ""
  }
] 