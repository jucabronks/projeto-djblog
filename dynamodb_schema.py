"""
Estrutura das tabelas DynamoDB para o projeto DJBlog
"""

# Tabela principal: djblog-noticias
NOTICIAS_TABLE_SCHEMA = {
    "TableName": "djblog-noticias",
    "KeySchema": [
        {
            "AttributeName": "id",
            "KeyType": "HASH"  # Partition key
        }
    ],
    "AttributeDefinitions": [
        {
            "AttributeName": "id",
            "AttributeType": "S"
        },
        {
            "AttributeName": "nicho",
            "AttributeType": "S"
        },
        {
            "AttributeName": "data_insercao",
            "AttributeType": "N"
        },
        {
            "AttributeName": "fonte",
            "AttributeType": "S"
        }
    ],
    "GlobalSecondaryIndexes": [
        {
            "IndexName": "nicho-data-index",
            "KeySchema": [
                {
                    "AttributeName": "nicho",
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "data_insercao",
                    "KeyType": "RANGE"
                }
            ],
            "Projection": {
                "ProjectionType": "ALL"
            },
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        },
        {
            "IndexName": "fonte-data-index",
            "KeySchema": [
                {
                    "AttributeName": "fonte",
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "data_insercao",
                    "KeyType": "RANGE"
                }
            ],
            "Projection": {
                "ProjectionType": "ALL"
            },
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        }
    ],
    "BillingMode": "PAY_PER_REQUEST"  # On-demand pricing
}

# Tabela para notícias resumidas
NOTICIAS_RESUMIDAS_TABLE_SCHEMA = {
    "TableName": "djblog-noticias-resumidas",
    "KeySchema": [
        {
            "AttributeName": "id",
            "KeyType": "HASH"
        }
    ],
    "AttributeDefinitions": [
        {
            "AttributeName": "id",
            "AttributeType": "S"
        },
        {
            "AttributeName": "data_resumo",
            "AttributeType": "N"
        }
    ],
    "GlobalSecondaryIndexes": [
        {
            "IndexName": "data-resumo-index",
            "KeySchema": [
                {
                    "AttributeName": "data_resumo",
                    "KeyType": "HASH"
                }
            ],
            "Projection": {
                "ProjectionType": "ALL"
            },
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        }
    ],
    "BillingMode": "PAY_PER_REQUEST"
}

# Tabela para fontes de notícias
FONTES_TABLE_SCHEMA = {
    "TableName": "djblog-fontes",
    "KeySchema": [
        {
            "AttributeName": "id",
            "KeyType": "HASH"
        }
    ],
    "AttributeDefinitions": [
        {
            "AttributeName": "id",
            "AttributeType": "S"
        },
        {
            "AttributeName": "nicho",
            "AttributeType": "S"
        },
        {
            "AttributeName": "ativo",
            "AttributeType": "S"
        }
    ],
    "GlobalSecondaryIndexes": [
        {
            "IndexName": "nicho-ativo-index",
            "KeySchema": [
                {
                    "AttributeName": "nicho",
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "ativo",
                    "KeyType": "RANGE"
                }
            ],
            "Projection": {
                "ProjectionType": "ALL"
            },
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        }
    ],
    "BillingMode": "PAY_PER_REQUEST"
}


def create_tables_if_not_exist():
    """Cria as tabelas DynamoDB se elas não existirem"""
    import boto3
    from botocore.exceptions import ResourceExistsError

    dynamodb = boto3.client('dynamodb')

    tables_to_create = [
        NOTICIAS_TABLE_SCHEMA,
        NOTICIAS_RESUMIDAS_TABLE_SCHEMA,
        FONTES_TABLE_SCHEMA
    ]

    for table_schema in tables_to_create:
        try:
            dynamodb.create_table(**table_schema)
            print(f"Tabela {table_schema['TableName']} criada com sucesso!")

            # Aguarda a tabela ficar ativa
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_schema['TableName'])

        except ResourceExistsError:
            print(f"Tabela {table_schema['TableName']} já existe.")
        except Exception as e:
            print(f"Erro ao criar tabela {table_schema['TableName']}: {e}")


if __name__ == "__main__":
    create_tables_if_not_exist()
