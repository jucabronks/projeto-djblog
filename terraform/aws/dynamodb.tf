# =============================================================================
# DYNAMODB TABLES
# =============================================================================

# Tabela principal de notícias
resource "aws_dynamodb_table" "djblog_noticias" {
  name           = "${var.project_name}-noticias"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "nicho"
    type = "S"
  }

  attribute {
    name = "data_insercao"
    type = "N"
  }

  attribute {
    name = "fonte"
    type = "S"
  }

  global_secondary_index {
    name     = "nicho-data-index"
    hash_key = "nicho"
    range_key = "data_insercao"
    projection_type = "ALL"
  }

  global_secondary_index {
    name     = "fonte-data-index"
    hash_key = "fonte"
    range_key = "data_insercao"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name = "${var.project_name}-noticias"
    Description = "Tabela principal de notícias coletadas"
  }
}

# Tabela de notícias resumidas
resource "aws_dynamodb_table" "djblog_noticias_resumidas" {
  name           = "${var.project_name}-noticias-resumidas"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "data_resumo"
    type = "N"
  }

  global_secondary_index {
    name     = "data-resumo-index"
    hash_key = "data_resumo"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name = "${var.project_name}-noticias-resumidas"
    Description = "Tabela de notícias resumidas pela IA"
  }
}

# Tabela de fontes de notícias
resource "aws_dynamodb_table" "djblog_fontes" {
  name           = "${var.project_name}-fontes"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "nicho"
    type = "S"
  }

  attribute {
    name = "ativo"
    type = "S"
  }

  global_secondary_index {
    name     = "nicho-ativo-index"
    hash_key = "nicho"
    range_key = "ativo"
    projection_type = "ALL"
  }

  tags = {
    Name = "${var.project_name}-fontes"
    Description = "Tabela de fontes RSS de notícias"
  }
}

# Outputs
output "dynamodb_table_noticias_name" {
  description = "Nome da tabela principal de notícias"
  value       = aws_dynamodb_table.djblog_noticias.name
}

output "dynamodb_table_noticias_arn" {
  description = "ARN da tabela principal de notícias"
  value       = aws_dynamodb_table.djblog_noticias.arn
}

output "dynamodb_table_resumidas_name" {
  description = "Nome da tabela de notícias resumidas"
  value       = aws_dynamodb_table.djblog_noticias_resumidas.name
}

output "dynamodb_table_fontes_name" {
  description = "Nome da tabela de fontes"
  value       = aws_dynamodb_table.djblog_fontes.name
} 