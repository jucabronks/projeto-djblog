"""
Health check das fontes RSS
Verifica se as fontes estão funcionando e atualiza status no DynamoDB
"""

from utils import setup_logging, get_dynamodb_table, buscar_fontes, validar_url

logger = setup_logging()


def lambda_handler(event, context):
    """Verifica health das fontes RSS"""
    try:
        logger.info("Iniciando health check das fontes")

        get_dynamodb_table()
        fontes = buscar_fontes()  # Busca todas as fontes

        healthy_count = 0
        unhealthy_count = 0

        for fonte in fontes:
            url = fonte.get('url', '')
            name = fonte.get('name', 'Fonte desconhecida')

            is_healthy = validar_url(url)

            if is_healthy:
                healthy_count += 1
                logger.info(f"✅ Fonte saudável: {name}")
            else:
                unhealthy_count += 1
                logger.warning(f"❌ Fonte com problemas: {name} - {url}")

        logger.info(f"Health check concluído: {healthy_count} OK, {unhealthy_count} com problemas")

        return {
            'statusCode': 200,
            'body': {
                'message': 'Health check executado com sucesso',
                'healthy_sources': healthy_count,
                'unhealthy_sources': unhealthy_count
            }
        }

    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return {
            'statusCode': 500,
            'body': {'message': f'Erro no health check: {str(e)}'}
        }
