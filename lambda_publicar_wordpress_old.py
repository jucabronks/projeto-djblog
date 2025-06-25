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
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from utils import (
    setup_logging, 
    validar_variaveis_obrigatorias, 
    get_dynamodb_table,
    sanitize_text,
    retry_on_failure
)
from config import get_config

logger = setup_logging()

@dataclass
class WordPressPost:
    """Estrutura de dados para um post do WordPress"""
    title: str
    content: str
    excerpt: str
    category_id: int
    status: str = "publish"
    tags: List[str] = None
    featured_media: Optional[int] = None

class WordPressPublisher:
    """Classe para publicação no WordPress"""
    
    def __init__(self):
        self.published_count = 0
        self.duplicate_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
        # Valida configuração do WordPress
        if not get_config().is_wordpress_configured():
            raise ValueError("WordPress não está configurado. Configure WP_URL, WP_USER e WP_APP_PASSWORD")
    
    def create_wordpress_post(self, post: WordPressPost) -> Optional[int]:
        """
        Cria um post no WordPress via API REST
        
        Args:
            post: Dados do post
            
        Returns:
            ID do post criado ou None se falhar
        """
        try:
            url = f"{get_config().wordpress.wp_url}/posts"
            
            # Prepara dados do post
            post_data = {
                "title": post.title,
                "content": post.content,
                "excerpt": post.excerpt,
                "status": post.status,
                "categories": [post.category_id]
            }
            
            if post.tags:
                post_data["tags"] = post.tags
            
            if post.featured_media:
                post_data["featured_media"] = post.featured_media
            
            # Headers de autenticação
            auth = (get_config().wordpress.wp_user, get_config().wordpress.wp_app_password)
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "NewsAggregator/1.0"
            }
            
            # Faz requisição
            response = requests.post(
                url,
                json=post_data,
                auth=auth,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                post_id = response.json().get("id")
                logger.info(f"Post criado com sucesso: ID {post_id}")
                return post_id
            else:
                logger.error(f"Erro ao criar post: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao criar post no WordPress: {e}")
            return None
    
    def prepare_post_content(self, noticia: Dict[str, Any]) -> str:
        """
        Prepara o conteúdo do post com formatação adequada
        
        Args:
            noticia: Dados da notícia
            
        Returns:
            Conteúdo formatado para o WordPress
        """
        content = f"""
<p><strong>{noticia['titulo']}</strong></p>

<p>{noticia['resumo']}</p>

<p><em>Fonte: <a href="{noticia['link']}" target="_blank" rel="noopener noreferrer">{noticia['fonte']}</a></em></p>

<p><small>Publicado em: {noticia['data_insercao'].strftime('%d/%m/%Y às %H:%M')}</small></p>
"""
        
        # Adiciona descrição completa se disponível
        if noticia.get('descricao_completa') and len(noticia['descricao_completa']) > len(noticia['resumo']):
            content += f"\n<p>{noticia['descricao_completa']}</p>\n"
        
        return content.strip()
    
    def prepare_post_excerpt(self, noticia: Dict[str, Any]) -> str:
        """
        Prepara o excerpt (resumo) do post
        
        Args:
            noticia: Dados da notícia
            
        Returns:
            Excerpt formatado
        """
        excerpt = noticia['resumo']
        
        # Limita o tamanho
        if len(excerpt) > 160:
            excerpt = excerpt[:157] + "..."
        
        return excerpt
    
    def get_post_tags(self, noticia: Dict[str, Any]) -> List[str]:
        """
        Gera tags para o post baseado no nicho e conteúdo
        
        Args:
            noticia: Dados da notícia
            
        Returns:
            Lista de tags
        """
        tags = [noticia['nicho']]
        
        # Adiciona tags baseadas no nicho
        nicho_tags = {
            "tecnologia": ["tech", "inovação", "digital"],
            "esportes": ["esporte", "atletismo", "competição"],
            "saude": ["saúde", "medicina", "bem-estar"],
            "economia": ["economia", "finanças", "mercado"],
            "ciencia": ["ciência", "pesquisa", "descoberta"],
            "politica": ["política", "governo", "sociedade"],
            "entretenimento": ["entretenimento", "cultura", "arte"],
            "educacao": ["educação", "ensino", "aprendizado"],
            "startups": ["startup", "empreendedorismo", "inovação"],
            "fintech": ["fintech", "tecnologia financeira", "pagamentos"],
            "ia": ["inteligência artificial", "IA", "machine learning"],
            "sustentabilidade": ["sustentabilidade", "meio ambiente", "ecologia"],
            "internacional": ["internacional", "global", "mundo"]
        }
        
        if noticia['nicho'] in nicho_tags:
            tags.extend(nicho_tags[noticia['nicho']])
        
        return tags
    
    def publish_news_item(self, noticia: Dict[str, Any], collection: Any) -> bool:
    """
        Publica uma notícia no WordPress
        
        Args:
            noticia: Dados da notícia
            collection: Coleção do MongoDB
            
        Returns:
            True se publicado com sucesso
        """
        try:
            # Verifica se já foi publicada
            if noticia.get("publicado"):
                logger.info(f"Notícia já publicada: {noticia['titulo'][:50]}...")
                return False
            
            # Verifica duplicidade
            if is_duplicate(noticia, collection):
                logger.info(f"Notícia duplicada detectada: {noticia['titulo'][:50]}...")
                collection.update_one(
                    {"_id": noticia["_id"]}, 
                    {"$set": {"duplicada": True}}
                )
                self.duplicate_count += 1
                return False
            
            # Prepara dados do post
            post = WordPressPost(
                title=sanitize_text(noticia['titulo'], 100),
                content=self.prepare_post_content(noticia),
                excerpt=self.prepare_post_excerpt(noticia),
                category_id=get_config().get_categoria_wp(noticia['nicho']),
                tags=self.get_post_tags(noticia)
            )
            
            # Cria post no WordPress
            post_id = self.create_wordpress_post(post)
            
            if post_id:
                # Atualiza notícia no MongoDB
                collection.update_one(
                    {"_id": noticia["_id"]},
                    {
                        "$set": {
                            "publicado": True,
                            "wp_post_id": post_id,
                            "data_publicacao": datetime.now(UTC),
                            "status_publicacao": "sucesso"
                        }
                    }
                )
                
                self.published_count += 1
                logger.info(f"Notícia publicada com sucesso: {noticia['titulo'][:50]}...")
                return True
            else:
                # Marca como erro
                collection.update_one(
                    {"_id": noticia["_id"]},
                    {
                        "$set": {
                            "status_publicacao": "erro",
                            "data_tentativa": datetime.now(UTC)
                        }
                    }
                )
                
                self.error_count += 1
                return False
                
        except Exception as e:
            logger.error(f"Erro ao publicar notícia: {e}")
            self.error_count += 1
            return False
    
    def publish_all_news(self) -> Dict[str, Any]:
        """
        Publica notícias aprovadas de todos os nichos
        
        Returns:
            Dicionário com estatísticas da publicação
        """
        logger.info("Iniciando publicação de notícias")
        
    try:
        client, collection = get_collection("noticias_coletadas")
            
            # Publica por nicho
            for nicho in get_config().content.nichos:
                logger.info(f"Publicando notícias do nicho: {nicho}")
                
                # Busca notícias aprovadas não publicadas
                noticias = collection.find({
                "nicho": nicho,
                "aprovado": True,
                "publicado": {"$ne": True},
                "duplicada": {"$ne": True}
                }).sort("data_insercao", -1).limit(1)  # 1 por nicho por execução
                
                for noticia in noticias:
                    self.publish_news_item(noticia, collection)
                    time.sleep(2)  # Rate limiting
            
            # Estatísticas finais
            execution_time = time.time() - self.start_time
            stats = {
                "publicadas": self.published_count,
                "duplicadas": self.duplicate_count,
                "erros": self.error_count,
                "tempo_execucao": execution_time,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            logger.info(f"Publicação concluída: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Erro crítico na publicação: {e}")
            raise
        finally:
            if 'client' in locals():
                client.close()

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal da função Lambda
    
    Args:
        event: Evento do Lambda
        context: Contexto do Lambda
        
    Returns:
        Dicionário com estatísticas da execução
    """
    logger.info("Iniciando execução da Lambda de publicação")
    
    try:
        # Valida variáveis obrigatórias
        required_vars = ["MONGO_URI"]
        if get_config().is_wordpress_configured():
            required_vars.extend(["WP_URL", "WP_USER", "WP_APP_PASSWORD"])
        
        validar_variaveis_obrigatorias(required_vars)
        
        # Inicializa publisher
        publisher = WordPressPublisher()
        
        # Executa publicação
        stats = publisher.publish_all_news()
        
        logger.info("Execução da Lambda concluída com sucesso")
        return stats
        
    except Exception as e:
        logger.error(f"Erro na execução da Lambda: {e}")
        raise

if __name__ == "__main__":
    # Teste local
    lambda_handler({}, {}) 