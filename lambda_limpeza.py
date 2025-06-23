#!/usr/bin/env python3
"""
Lambda Function para Limpeza Automática de Notícias Antigas
Remove notícias com mais de 7 dias do MongoDB
"""

import json
from datetime import datetime, timedelta, UTC
from bson import ObjectId
from utils import setup_logging, get_collection

logger = setup_logging()

def lambda_handler(event, context):
    """
    Handler principal da Lambda de limpeza
    Remove notícias antigas (> 7 dias) do MongoDB
    """
    client = None
    try:
        # Conectar ao MongoDB
        client, db = get_collection("noticias_coletadas")
        collection = db["noticias_coletadas"]
        
        # Data limite (7 dias atrás)
        data_limite = datetime.now(UTC) - timedelta(days=7)
        
        logger.info(f"Iniciando limpeza de notícias anteriores a {data_limite}")
        
        # Contar notícias antes da limpeza
        total_antes = collection.count_documents({})
        logger.info(f"Total de notícias antes da limpeza: {total_antes}")
        
        # Remover notícias antigas
        resultado = collection.delete_many({
            "data_insercao": {"$lt": data_limite}
        })
        
        # Contar notícias após a limpeza
        total_depois = collection.count_documents({})
        
        # Logs do resultado
        logger.info(f"Notícias removidas: {resultado.deleted_count}")
        logger.info(f"Total de notícias após limpeza: {total_depois}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Limpeza concluída com sucesso',
                'noticias_removidas': resultado.deleted_count,
                'total_antes': total_antes,
                'total_depois': total_depois,
                'data_limite': data_limite.isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Erro na limpeza: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Erro na limpeza: {str(e)}'
            })
        }
    finally:
        if client:
            client.close() 