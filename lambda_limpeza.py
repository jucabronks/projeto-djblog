"""
Função AWS Lambda para limpeza automática de notícias antigas
Remove notícias com mais de 7 dias do DynamoDB
"""

from datetime import datetime, timedelta, UTC
from utils import setup_logging, get_dynamodb_table

logger = setup_logging()


def lambda_handler(event, context):
    """Remove notícias antigas do DynamoDB"""
    try:
        logger.info("Iniciando limpeza de notícias antigas")

        table = get_dynamodb_table()

        # Data limite (7 dias atrás)
        cutoff_date = datetime.now(UTC) - timedelta(days=7)
        cutoff_timestamp = int(cutoff_date.timestamp())

        # Busca notícias antigas
        from boto3.dynamodb.conditions import Attr

        response = table.scan(
            FilterExpression=Attr('data_insercao').lt(cutoff_timestamp),
            ProjectionExpression='id'
        )

        items_to_delete = response.get('Items', [])
        deleted_count = 0

        # Remove em lotes
        for item in items_to_delete:
            try:
                table.delete_item(Key={'id': item['id']})
                deleted_count += 1
            except Exception as e:
                logger.error(f"Erro ao deletar item {item['id']}: {e}")

        logger.info(f"Limpeza concluída: {deleted_count} notícias removidas")

        return {
            'statusCode': 200,
            'body': {
                'message': f'Limpeza executada com sucesso',
                'deleted_count': deleted_count
            }
        }

    except Exception as e:
        logger.error(f"Erro na limpeza: {e}")
        return {
            'statusCode': 500,
            'body': {'message': f'Erro na limpeza: {str(e)}'}
        }
