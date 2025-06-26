# =============================================================================
# AWS INFRASTRUCTURE - PROJETO VM
# =============================================================================

terraform {
  required_version = ">= 1.12.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "projeto-vm-terraform-state-317304475005"  # Será substituído pelo script
    key            = "aws/dev/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# =============================================================================
# PROVIDERS
# =============================================================================

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "DevOps Team"
    }
  }
}

# =============================================================================
# VARIABLES
# =============================================================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "projeto-vm"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "openai_api_key" {
  description = "Chave da OpenAI (opcional)"
  type        = string
  default     = ""
}

variable "dd_api_key" {
  description = "Chave do Datadog"
  type        = string
  default     = ""
}

variable "dd_site" {
  description = "Site do Datadog"
  type        = string
  default     = "datadoghq.com"
}

variable "dd_env" {
  description = "Ambiente do Datadog"
  type        = string
  default     = "prod"
}

variable "nicho" {
  description = "Nicho de notícias"
  type        = string
  default     = "ciencia"
}

variable "pais" {
  description = "País de coleta"
  type        = string
  default     = "Brasil"
}

variable "max_news_per_source" {
  description = "Máximo de notícias por fonte"
  type        = number
  default     = 3
}

variable "copys_api_user" {
  description = "Usuário da API Copyscape"
  type        = string
  default     = ""
}

variable "copys_api_key" {
  description = "Chave da API Copyscape"
  type        = string
  default     = ""
}

variable "coletas" {
  description = "Configuração das coletas por país"
  type = list(object({
    pais             = string
    cron             = string
    timezone         = string
    nicho            = string
    mongo_uri        = string
    openai_api_key   = string
    dd_api_key       = string
    dd_site          = string
    dd_env           = string
    max_news         = number
    copys_api_user   = string
    copys_api_key    = string
  }))
  default = []
}

variable "nicho_lista" {
  description = "Lista de nichos a coletar/publicar"
  type        = list(string)
  default     = ["tecnologia", "esportes", "saude", "economia", "ciencia", "politica", "entretenimento", "educacao", "startups", "fintech", "ia", "sustentabilidade", "internacional"]
}

variable "categorias_wp" {
  description = "Mapeamento de nichos para IDs de categoria do WordPress"
  type        = map(number)
  default     = {
    tecnologia      = 2
    esportes        = 3
    saude           = 4
    economia        = 5
    ciencia         = 6
    politica        = 7
    entretenimento  = 8
    educacao        = 9
    startups        = 10
    fintech         = 11
    ia              = 12
    sustentabilidade = 13
    internacional   = 14
  }
}

variable "wp_url" { 
  type = string
  default = ""
}
variable "wp_user" { 
  type = string
  default = ""
}
variable "wp_app_password" { 
  type = string
  default = ""
}

variable "alarm_email" {
  description = "E-mail para receber alertas de erro das Lambdas"
  type        = string
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

# =============================================================================
# DATA SOURCES
# =============================================================================

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# =============================================================================
# NETWORK MODULE (COMENTADO - NÃO NECESSÁRIO PARA SERVERLESS)
# =============================================================================

# module "network" {
#   source = "../modules/network"
# 
#   cloud_provider = "aws"
#   project_name   = var.project_name
#   environment    = var.environment
#   vpc_cidr       = var.vpc_cidr
# 
#   subnets = {
#     public-1 = {
#       cidr_block = "10.0.1.0/24"
#       az         = data.aws_availability_zones.available.names[0]
#       public     = true
#     }
#     private-1 = {
#       cidr_block = "10.0.2.0/24"
#       az         = data.aws_availability_zones.available.names[0]
#       public     = false
#     }
#     public-2 = {
#       cidr_block = "10.0.3.0/24"
#       az         = data.aws_availability_zones.available.names[1]
#       public     = true
#     }
#     private-2 = {
#       cidr_block = "10.0.4.0/24"
#       az         = data.aws_availability_zones.available.names[1]
#       public     = false
#     }
#   }
# 
#   tags = var.tags
# }

# =============================================================================
# COMPUTE MODULE (COMENTADO - NÃO NECESSÁRIO PARA SERVERLESS)
# =============================================================================

# module "compute" {
#   source = "../modules/compute"
# 
#   cloud_provider = "aws"
#   project_name   = var.project_name
#   environment    = var.environment
#   vpc_id         = module.network.vpc_id
#   subnet_ids     = module.network.subnet_ids
# 
#   instance_type  = var.instance_type
#   instance_count = var.instance_count
# 
#   user_data = templatefile("${path.module}/user_data.sh", {
#     project_name = var.project_name
#     environment  = var.environment
#   })
# 
#   tags = var.tags
# }

# =============================================================================
# DATABASE MODULE (COMENTADO - USAR MONGODB ATLAS GRATUITO)
# =============================================================================

# module "database" {
#   source = "../modules/database"
# 
#   cloud_provider = "aws"
#   project_name   = var.project_name
#   environment    = var.environment
#   vpc_id         = module.network.vpc_id
#   subnet_ids     = module.network.private_subnet_ids
# 
#   engine         = "postgres"
#   engine_version = "14.10"
#   instance_class = "db.t3.micro"
#   allocated_storage = 20
# 
#   database_name = "projetovm"
#   username      = "admin"
#   password      = var.db_password
# 
#   backup_retention_period = 7
#   backup_window          = "03:00-04:00"
#   maintenance_window     = "sun:04:00-sun:05:00"
# 
#   tags = var.tags
# }

# =============================================================================
# LOAD BALANCER MODULE (COMENTADO - NÃO NECESSÁRIO PARA SERVERLESS)
# =============================================================================

# module "load_balancer" {
#   source = "../modules/load_balancer"
# 
#   cloud_provider = "aws"
#   project_name   = var.project_name
#   environment    = var.environment
#   vpc_id         = module.network.vpc_id
#   subnet_ids     = module.network.public_subnet_ids
# 
#   target_instance_ids = module.compute.instance_ids
#   target_instance_ips = module.compute.instance_private_ips
# 
#   health_check_path = "/health"
#   health_check_port = 80
# 
#   tags = var.tags
# }

# =============================================================================
# MONITORING MODULE (COMENTADO - USAR CLOUDWATCH NATIVO)
# =============================================================================

# module "monitoring" {
#   source = "../modules/monitoring"
# 
#   cloud_provider = "aws"
#   project_name   = var.project_name
#   environment    = var.environment
# 
#   log_group_name = "/aws/ec2/${var.project_name}-${var.environment}"
#   retention_days = 30
# 
#   alarm_email = var.alarm_email
# 
#   tags = var.tags
# }

# =============================================================================
# LAMBDA DE COLETA DE NOTÍCIAS
# =============================================================================
resource "aws_lambda_function" "coletor" {
  function_name    = "coletor-noticias"
  filename         = "../../lambda_coletor.zip"
  source_code_hash = filebase64sha256("../../lambda_coletor.zip")
  handler          = "lambda_coletor.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512
  role          = aws_iam_role.lambda_coletor_role.arn
  environment {
    variables = {
      NICHOS            = join(",", var.nicho_lista)
      OPENAI_API_KEY    = var.openai_api_key
      DD_API_KEY        = var.dd_api_key
      DD_SITE           = var.dd_site
      DD_ENV            = var.dd_env
      PAIS              = var.pais
      MAX_NEWS_PER_SOURCE = var.max_news_per_source
      COPYS_API_USER    = var.copys_api_user
      COPYS_API_KEY     = var.copys_api_key
    }
  }
}

resource "aws_lambda_function" "publicador" {
  function_name = "publicador-noticias"
  filename      = "../../lambda_publicar_wordpress.zip"
  handler       = "lambda_publicar_wordpress.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512
  role          = aws_iam_role.lambda_coletor_role.arn
  environment {
    variables = {
      WP_URL         = var.wp_url
      WP_USER        = var.wp_user
      WP_APP_PASSWORD= var.wp_app_password
      CATEGORIAS_WP  = jsonencode(var.categorias_wp)
    }
  }
  source_code_hash = filebase64sha256("../../lambda_publicar_wordpress.zip")
}

resource "aws_lambda_function" "limpeza" {
  function_name = "limpeza-noticias"
  filename      = "../../lambda_limpeza.zip"
  handler       = "lambda_limpeza.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512
  role          = aws_iam_role.lambda_coletor_role.arn
  environment {
    variables = {
    }
  }
  source_code_hash = filebase64sha256("../../lambda_limpeza.zip")
}

resource "aws_lambda_function" "health_check" {
  function_name = "health-check"
  filename      = "../../lambda_health_check.zip"
  handler       = "lambda_health_check.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60
  memory_size   = 256
  role          = aws_iam_role.lambda_coletor_role.arn
  environment {
    variables = {
    }
  }
  source_code_hash = filebase64sha256("../../lambda_health_check.zip")
}

resource "aws_lambda_function" "api_noticias" {
  function_name = "api-noticias"
  handler       = "lambda_api_noticias.lambda_handler"
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_coletor_role.arn
  filename      = "../../lambda_api_noticias.zip"
  source_code_hash = filebase64sha256("../../lambda_api_noticias.zip")
  timeout       = 10
  environment {
    variables = {
      # Adicione variáveis se necessário
    }
  }
}

resource "aws_apigatewayv2_api" "noticias_api" {
  name          = "noticias-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "noticias_lambda_integration" {
  api_id                 = aws_apigatewayv2_api.noticias_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api_noticias.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "noticias_route" {
  api_id    = aws_apigatewayv2_api.noticias_api.id
  route_key = "GET /noticias"
  target    = "integrations/${aws_apigatewayv2_integration.noticias_lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "noticias_stage" {
  api_id      = aws_apigatewayv2_api.noticias_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "allow_apigw_invoke_api_noticias" {
  statement_id  = "AllowAPIGatewayInvokeApiNoticias"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_noticias.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.noticias_api.execution_arn}/*/*"
}

resource "aws_iam_role" "lambda_coletor_role" {
  name = "lambda_coletor_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_coletor_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# =============================================================================
# EVENTBRIDGE RULES POR PAÍS
# =============================================================================
resource "aws_cloudwatch_event_rule" "coleta" {
  name                = "coleta-diaria"
  schedule_expression = "cron(0 21 * * ? *)"
  description         = "Coleta diária de notícias"
}

resource "aws_cloudwatch_event_rule" "publicacao" {
  name                = "publicacao-diaria"
  schedule_expression = "cron(40 6 * * ? *)"
  description         = "Publicação diária de notícias"
}

resource "aws_cloudwatch_event_rule" "limpeza" {
  name                = "limpeza-semanal"
  schedule_expression = "cron(0 3 ? * SUN *)"
  description         = "Limpeza semanal do banco"
}

resource "aws_cloudwatch_event_target" "coleta_target" {
  rule      = aws_cloudwatch_event_rule.coleta.name
  target_id = "lambda-coleta"
  arn       = aws_lambda_function.coletor.arn
}

resource "aws_cloudwatch_event_target" "publicacao_target" {
  rule      = aws_cloudwatch_event_rule.publicacao.name
  target_id = "lambda-publicacao"
  arn       = aws_lambda_function.publicador.arn
}

resource "aws_cloudwatch_event_target" "limpeza_target" {
  rule      = aws_cloudwatch_event_rule.limpeza.name
  target_id = "lambda-limpeza"
  arn       = aws_lambda_function.limpeza.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge-coleta"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.coletor.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.coleta.arn
}

resource "aws_lambda_permission" "allow_eventbridge_publicacao" {
  statement_id  = "AllowExecutionFromEventBridge-publicacao"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.publicador.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.publicacao.arn
}

resource "aws_lambda_permission" "allow_eventbridge_limpeza" {
  statement_id  = "AllowExecutionFromEventBridge-limpeza"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.limpeza.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.limpeza.arn
}

# =============================================================================
# EVENTBRIDGE RULES PARA FLUXO AUTOMATIZADO
# =============================================================================

# Coletor: 20:00, 20:10, 20:20, 20:30 (horário de Brasília)
resource "aws_cloudwatch_event_rule" "coletor_batch" {
  name                = "coletor-batch"
  schedule_expression = "cron(0,10,20,30 23 * * ? *)" # 23h UTC = 20h BRT
  description         = "Coleta de notícias em lote às 20h, 20h10, 20h20, 20h30 BRT"
}

resource "aws_cloudwatch_event_target" "coletor_batch_target" {
  rule      = aws_cloudwatch_event_rule.coletor_batch.name
  target_id = "lambda-coletor-batch"
  arn       = aws_lambda_function.coletor.arn
}

resource "aws_lambda_permission" "allow_eventbridge_coletor_batch" {
  statement_id  = "AllowExecutionFromEventBridge-coletor-batch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.coletor.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.coletor_batch.arn
}

# Publicador: Segunda, Terça, Quarta e Sexta às 6:40 (horário de Brasília)
resource "aws_cloudwatch_event_rule" "publicador_manha" {
  name                = "publicador-manha"
  schedule_expression = "cron(40 9 ? * MON,TUE,WED,FRI *)" # 9:40 UTC = 6:40 BRT
  description         = "Publicação automática das notícias às 6h40 BRT, seg, ter, qua, sex"
}

resource "aws_cloudwatch_event_target" "publicador_manha_target" {
  rule      = aws_cloudwatch_event_rule.publicador_manha.name
  target_id = "lambda-publicador-manha"
  arn       = aws_lambda_function.publicador.arn
}

resource "aws_lambda_permission" "allow_eventbridge_publicador_manha" {
  statement_id  = "AllowExecutionFromEventBridge-publicador-manha"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.publicador.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.publicador_manha.arn
}

# =============================================================================
# EVENTBRIDGE RULES PARA HEALTH CHECK
# =============================================================================

resource "aws_cloudwatch_event_rule" "health_check_schedule" {
  name                = "health-check-schedule"
  schedule_expression = "rate(1 day)"
  description         = "Verificação diária da saúde das fontes RSS"
}

resource "aws_cloudwatch_event_target" "health_check_target" {
  rule      = aws_cloudwatch_event_rule.health_check_schedule.name
  target_id = "lambda-health-check"
  arn       = aws_lambda_function.health_check.arn
}

resource "aws_lambda_permission" "allow_eventbridge_health_check" {
  statement_id  = "AllowExecutionFromEventBridge-health-check"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health_check.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.health_check_schedule.arn
}

# =============================================================================
# SNS TOPIC PARA ALERTAS DE ERRO
# =============================================================================

resource "aws_sns_topic" "lambda_errors" {
  name = "lambda-error-notifications"
}

resource "aws_sns_topic_subscription" "email_alerts" {
  topic_arn = aws_sns_topic.lambda_errors.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

resource "aws_cloudwatch_metric_alarm" "coletor_error_alarm" {
  alarm_name          = "lambda-coletor-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Alarme para erros na Lambda de coleta"
  dimensions = {
    FunctionName = aws_lambda_function.coletor.function_name
  }
  alarm_actions = [aws_sns_topic.lambda_errors.arn]
}

# =============================================================================
# EVENTBRIDGE RULES PARA LIMPEZA DE LOGS
# =============================================================================

resource "aws_cloudwatch_event_rule" "limpeza_logs" {
  name                = "limpeza-logs-semanal"
  description         = "Executa a função de limpeza de logs semanalmente"
  schedule_expression = "cron(0 3 ? * MON *)" # toda segunda-feira às 03:00 UTC
}

resource "aws_cloudwatch_event_target" "limpeza_logs_target" {
  rule      = aws_cloudwatch_event_rule.limpeza_logs.name
  target_id = "lambda-limpeza-logs"
  arn       = aws_lambda_function.limpeza.arn
}

resource "aws_lambda_permission" "allow_eventbridge_limpeza_logs" {
  statement_id  = "AllowExecutionFromEventBridgeLimpezaLogs"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.limpeza.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.limpeza_logs.arn
}

# =============================================================================
# OUTPUTS
# =============================================================================

output "lambda_functions" {
  description = "Lambda function ARNs"
  value = {
    coletor     = aws_lambda_function.coletor.arn
    publicador  = aws_lambda_function.publicador.arn
    limpeza     = aws_lambda_function.limpeza.arn
    health_check = aws_lambda_function.health_check.arn
  }
}

output "eventbridge_rules" {
  description = "EventBridge rule ARNs"
  value = {
    coleta           = aws_cloudwatch_event_rule.coleta.arn
    publicacao       = aws_cloudwatch_event_rule.publicacao.arn
    limpeza          = aws_cloudwatch_event_rule.limpeza.arn
    coletor_batch    = aws_cloudwatch_event_rule.coletor_batch.arn
    publicador_manha = aws_cloudwatch_event_rule.publicador_manha.arn
    health_check     = aws_cloudwatch_event_rule.health_check_schedule.arn
  }
}

output "sns_topic" {
  description = "SNS topic for error notifications"
  value       = aws_sns_topic.lambda_errors.arn
}

output "cloudwatch_alarm" {
  description = "CloudWatch alarm for Lambda errors"
  value       = aws_cloudwatch_metric_alarm.coletor_error_alarm.arn
}

output "project_info" {
  description = "Project information"
  value = {
    project_name = var.project_name
    environment  = var.environment
    region       = var.aws_region
  }
} 