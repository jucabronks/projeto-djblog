"""
Função AWS Lambda para publicação automática de notícias no WordPress

Como usar:
1. Configure as variáveis de ambiente:
   - DYNAMODB_TABLE_NAME: nome da tabela DynamoDB
   - AWS_REGION: região da AWS
   - WP_URL: URL do WordPress (ex: https://meusite.com/wp-json/wp/v2)
   - WP_USER: usuário do WordPress
   - WP_APP_PASSWORD: senha de aplicação do WordPress
2. Agende via EventBridge para rodar periodicamente
"""

import os
import json
import requests
import time
from datetime import datetime, UTC, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import boto3

from utils import (
    setup_logging, 
    validar_variaveis_obrigatorias, 
    get_dynamodb_table,
    sanitize_text,
    retry_on_failure
)
from config import get_config

# Imports opcionais
try:
    from datadog_lambda.wrapper import datadog_lambda_wrapper
    DATADOG_AVAILABLE = True
except ImportError:
    DATADOG_AVAILABLE = False
    def datadog_lambda_wrapper(func):
        return func

logger = setup_logging()

class WordPressPublisher:
    """Publicador de notícias no WordPress"""
    
    def __init__(self):
        self.start_time = time.time()
        self.published_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.duplicate_count = 0
        
    def get_unpublished_news(self, table, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Busca notícias aprovadas que ainda não foram publicadas
        
        Args:
            table: Tabela DynamoDB
            limit: Número máximo de notícias
            
        Returns:
            Lista de notícias para publicar
        """
        try:
            from boto3.dynamodb.conditions import Attr
            
            # Busca notícias aprovadas e não publicadas
            response = table.scan(
                FilterExpression=Attr('aprovado').eq(True) & Attr('publicado').eq(False),
                Limit=limit
            )
            
            noticias = response.get('Items', [])
            logger.info(f"Encontradas {len(noticias)} notícias para publicar")
            
            # Ordena por data de inserção (mais recentes primeiro)
            noticias.sort(key=lambda x: x.get('data_insercao', 0), reverse=True)
            
            return noticias
            
        except Exception as e:
            logger.error(f"Erro ao buscar notícias: {e}")
            return []

    def is_duplicate_content(self, noticia: Dict[str, Any], table) -> bool:
        """
        Verifica se a notícia é duplicada com base no título
        
        Args:
            noticia: Dados da notícia
            table: Tabela DynamoDB
            
        Returns:
            True se for duplicada
        """
        try:
            from boto3.dynamodb.conditions import Attr
            from difflib import SequenceMatcher
            
            titulo_normalizado = noticia['titulo'].lower().strip()
            
            # Busca notícias publicadas com títulos similares
            response = table.scan(
                FilterExpression=Attr('publicado').eq(True),
                ProjectionExpression='titulo'
            )
            
            for item in response.get('Items', []):
                titulo_existente = item.get('titulo', '').lower().strip()
                similarity = SequenceMatcher(None, titulo_normalizado, titulo_existente).ratio()
                
                if similarity > 0.8:  # 80% de similaridade
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar duplicidade: {e}")
            return False

    def prepare_post_content(self, noticia: Dict[str, Any]) -> str:
        """
        Prepara o conteúdo do post para WordPress
        
        Args:
            noticia: Dados da notícia
            
        Returns:
            Conteúdo HTML formatado
        """
        content = f"""
        <div class="noticia-content">
            <h2>{noticia['titulo']}</h2>
            
            <div class="resumo">
                <p>{noticia['resumo']}</p>
            </div>
            
            <div class="conteudo">
                <p>{noticia.get('descricao_completa', noticia['resumo'])}</p>
            </div>
            
            <div class="fonte">
                <p><strong>Fonte:</strong> <a href="{noticia['link']}" target="_blank" rel="noopener">{noticia['fonte']}</a></p>
            </div>
            
            <div class="metadata">
                <p><small>Nicho: {noticia['nicho']} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}</small></p>
            </div>
        </div>
        """
        
        return content.strip()

    @retry_on_failure
    def publish_to_wordpress(self, noticia: Dict[str, Any], table) -> bool:
        """
        Publica uma notícia no WordPress
        
        Args:
            noticia: Dados da notícia
            table: Tabela DynamoDB
            
        Returns:
            True se publicação foi bem-sucedida
        """
        try:
            # Verifica se já foi publicada
            if noticia.get("publicado"):
                logger.info(f"Notícia já publicada: {noticia['titulo'][:50]}...")
                return False
                
            # Verifica duplicidade
            if self.is_duplicate_content(noticia, table):
                logger.info(f"Notícia duplicada detectada: {noticia['titulo'][:50]}...")
                
                # Marca como duplicada
                table.update_item(
                    Key={'id': noticia['id']},
                    UpdateExpression='SET duplicada = :val',
                    ExpressionAttributeValues={':val': True}
                )
                
                self.duplicate_count += 1
                return False
            
            # Prepara dados do post
            post_data = {
                "title": sanitize_text(noticia['titulo'], 100),
                "content": self.prepare_post_content(noticia),
                "status": "publish",
                "categories": [get_config().get_categoria_wp(noticia['nicho'])],
                "excerpt": sanitize_text(noticia['resumo'], 200),
                "meta": {
                    "fonte_original": noticia['fonte'],
                    "link_original": noticia['link'],
                    "nicho": noticia['nicho'],
                    "data_coleta": noticia.get('data_insercao')
                }
            }
            
            # Faz requisição para WordPress
            wp_config = get_config().wordpress
            response = requests.post(
                f"{wp_config.wp_url}/posts",
                json=post_data,
                auth=(wp_config.wp_user, wp_config.wp_app_password),
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 201:
                post_id = response.json().get("id")
                post_url = response.json().get("link")
                
                # Atualiza notícia como publicada
                table.update_item(
                    Key={'id': noticia['id']},
                    UpdateExpression='SET publicado = :pub, wp_post_id = :pid, wp_post_url = :url, data_publicacao = :data',
                    ExpressionAttributeValues={
                        ':pub': True,
                        ':pid': post_id,
                        ':url': post_url,
                        ':data': int(datetime.now(UTC).timestamp())
                    }
                )
                
                logger.info(f"Notícia publicada com sucesso: {noticia['titulo'][:50]}... (ID: {post_id})")
                self.published_count += 1
                return True
                
            else:
                logger.error(f"Erro ao publicar notícia: {response.status_code} - {response.text}")
                self.error_count += 1
                return False
                
        except Exception as e:
            logger.error(f"Erro ao publicar notícia '{noticia.get('titulo', 'Sem título')}': {e}")
            self.error_count += 1
            return False

    def publish_all_pending(self) -> Dict[str, Any]:
        """
        Publica todas as notícias pendentes
        
        Returns:
            Dicionário com estatísticas da publicação
        """
        logger.info("Iniciando publicação de notícias no WordPress")
        
        try:
            table = get_dynamodb_table()
            
            # Busca notícias para publicar
            noticias = self.get_unpublished_news(table)
            
            if not noticias:
                logger.info("Nenhuma notícia encontrada para publicação")
                return {
                    "publicadas": 0,
                    "ignoradas": 0,
                    "erros": 0,
                    "duplicadas": 0,
                    "tempo_execucao": time.time() - self.start_time,
                    "timestamp": datetime.now(UTC).isoformat()
                }
            
            # Publica cada notícia
            for noticia in noticias:
                try:
                    success = self.publish_to_wordpress(noticia, table)
                    if not success:
                        self.skipped_count += 1
                        
                    # Rate limiting para evitar sobrecarga
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar notícia: {e}")
                    self.error_count += 1
            
            # Estatísticas finais
            execution_time = time.time() - self.start_time
            stats = {
                "publicadas": self.published_count,
                "ignoradas": self.skipped_count,
                "erros": self.error_count,
                "duplicadas": self.duplicate_count,
                "tempo_execucao": execution_time,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            logger.info(f"Publicação concluída: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Erro crítico na publicação: {e}")
            raise

def lambda_handler(event, context):
    """
    Handler principal da função Lambda
    
    Args:
        event: Evento do EventBridge
        context: Contexto da Lambda
    
    Returns:
        Dicionário com resultado da execução
    """
    try:
        logger.info("Iniciando execução da Lambda de publicação")
        
        # Validação de configuração
        config = get_config()
        if not config.is_wordpress_configured():
            logger.warning("WordPress não configurado - publicação desabilitada")
            return {
                'statusCode': 200,
                'body': {
                    'message': 'WordPress não configurado',
                    'statistics': {}
                }
            }
        
        # Executa publicação
        publisher = WordPressPublisher()
        stats = publisher.publish_all_pending()
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Publicação executada com sucesso',
                'statistics': stats
            }
        }
        
    except Exception as e:
        logger.error(f"Erro na execução da Lambda: {e}")
        return {
            'statusCode': 500,
            'body': {
                'message': f'Erro na publicação: {str(e)}'
            }
        }

# Wrapper Datadog se disponível
if DATADOG_AVAILABLE:
    lambda_handler = datadog_lambda_wrapper(lambda_handler)
