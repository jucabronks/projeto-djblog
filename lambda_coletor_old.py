"""
Função AWS Lambda para coleta de notícias automatizada, com integração Datadog, resumo automático com IA, revisão ortográfica e persistência no MongoDB.

Como usar:
1. Instale o layer/pacote Datadog na Lambda (veja README)
2. Configure as variáveis de ambiente na Lambda:
   - MONGO_URI: string de conexão do MongoDB (produção ou teste)
   - OPENAI_API_KEY: chave da OpenAI (opcional)
   - DD_API_KEY: chave do Datadog
   - DD_SITE: datadoghq.com ou datadoghq.eu
   - DD_ENV: prod ou test
3. Faça upload deste arquivo como função Lambda (Python 3.8+)
4. Agende via EventBridge (CloudWatch Events) para rodar periodicamente
"""

import os
import feedparser
from datetime import datetime, UTC
import requests
import boto3
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import uuid
import logging

# Imports locais
from utils import (
    setup_logging, 
    validar_variaveis_obrigatorias, 
    buscar_fontes, 
    checar_plagio_local,
    get_dynamodb_table,
    validar_url,
    sanitize_text,
    generate_content_hash,
    rate_limit_delay,
    retry_on_failure,
    inserir_noticia_coletada
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

try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    from summarize_ai import resumir_com_ia
    SUMMARIZE_AI_AVAILABLE = True
except ImportError:
    SUMMARIZE_AI_AVAILABLE = False

logger = setup_logging()

@dataclass
class NewsItem:
    """Estrutura de dados para uma notícia"""
    title: str
    link: str
    description: str
    source: str
    niche: str
    published_date: Optional[datetime] = None
    content_hash: Optional[str] = None

class NewsCollector:
    """Classe para coleta e processamento de notícias"""
    
    def __init__(self):
        self.total_saved = 0
        self.total_existing = 0
        self.total_errors = 0
        self.start_time = time.time()
    
    def validate_rss_feed(self, feed_url: str, source_name: str) -> bool:
        """
        Valida se um feed RSS é acessível e válido
        
        Args:
            feed_url: URL do feed RSS
            source_name: Nome da fonte
            
        Returns:
            True se o feed é válido
        """
        try:
            if not validar_url(feed_url):
                logger.warning(f"URL inválida para {source_name}: {feed_url}")
                return False
            
            feed = feedparser.parse(feed_url)
            if not feed.entries:
                logger.warning(f"Feed sem dados para {source_name}: {feed_url}")
                return False
            
            if hasattr(feed, 'bozo') and feed.bozo:
                logger.warning(f"Feed malformado para {source_name}: {feed_url}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar feed de {source_name}: {e}")
            return False
    
    def process_news_item(self, entry: Dict[str, Any], source: Dict[str, Any], table) -> bool:
        """
        Processa um item de notícia individual
        
        Args:
            entry: Item do feed RSS
            source: Informações da fonte
            table: Tabela DynamoDB
            
        Returns:
            True se a notícia foi salva com sucesso
        """
        try:
            # Extrai dados básicos
            title = sanitize_text(entry.get("title", "(Sem título)"))
            link = entry.get("link", "")
            description = sanitize_text(entry.get("summary", ""))
            
            # Valida dados obrigatórios
            if not title or not link:
                logger.warning(f"Dados insuficientes: título='{title}', link='{link}'")
                return False
            
            # Gera resumo se necessário
            if len(description) > get_config().content.threshold_caracteres:
                resumo = " ".join(description.split()[:60]) + "..."
            else:
                resumo = description
            
            # Gera ID único baseado no link
            noticia_id = generate_content_hash(link)
            
            # Verifica se já existe no DynamoDB
            try:
                response = table.get_item(Key={'id': noticia_id})
                if 'Item' in response:
                    self.total_existing += 1
                    return False
            except Exception as e:
                logger.debug(f"Erro ao verificar existência: {e}")
            
            # Verifica plágio local
            is_plagio_local = checar_plagio_local(title, resumo, table)
            
            # Verifica plágio Copyscape se configurado
            plagio_copyscape = False
            if (not is_plagio_local and 
                get_config().is_copyscape_configured() and 
                len(resumo) > get_config().content.threshold_caracteres):
                try:
                    plagio_copyscape = self.check_copyscape_plagiarism(resumo)
                except Exception as e:
                    logger.error(f"Erro ao verificar plágio Copyscape: {e}")
                    plagio_copyscape = False
            
            # Determina se está aprovado
            aprovado = not (is_plagio_local or plagio_copyscape)
            
            # Detecta idioma se disponível
            language = "pt-BR"  # Default
            if LANGDETECT_AVAILABLE and description:
                try:
                    language = detect(description)
                except Exception as e:
                    logger.debug(f"Erro ao detectar idioma: {e}")
            
            # Cria documento da notícia
            noticia = {
                "id": noticia_id,
                "titulo": title,
                "link": link,
                "resumo": resumo,
                "descricao_completa": description,
                "fonte": source["name"],
                "nicho": source.get("nicho", "geral"),
                "data_insercao": int(datetime.now(UTC).timestamp()),
                "data_publicacao": entry.get("published_parsed"),
                "aprovado": aprovado,
                "plagio_local": is_plagio_local,
                "plagio_copyscape": plagio_copyscape,
                "idioma": language,
                "publicado": False,
                "duplicada": False,
                "metadata": {
                    "source_type": source.get("type", "rss"),
                    "source_url": source.get("url", ""),
                    "processing_time": time.time() - self.start_time
                }
            }
            
            # Salva no DynamoDB
            if aprovado:
                table.put_item(Item=noticia)
                self.total_saved += 1
                logger.info(f"Notícia salva: {title[:50]}...")
                return True
            else:
                self.total_existing += 1
                return False
                
        except Exception as e:
            logger.error(f"Erro ao processar notícia: {e}")
            self.total_errors += 1
            return False
    
    @retry_on_failure
    def check_copyscape_plagiarism(self, text: str) -> bool:
        """
        Verifica plágio usando Copyscape API
        
        Args:
            text: Texto para verificar
            
        Returns:
            True se for considerado plágio
        """
    url = "https://www.copyscape.com/api/"
    params = {
            "u": get_config().api.copys_api_user,
            "k": get_config().api.copys_api_key,
        "o": "csearch",
            "t": text[:10000]  # Limite da API
    }
        
        response = requests.post(url, data=params, timeout=10)
        
        if "<result>" in response.text and "<count>0</count>" in response.text:
            return False  # Não é plágio
        return True  # Possível plágio
    
    def collect_from_source(self, source: Dict[str, Any], table) -> None:
        """
        Coleta notícias de uma fonte específica
        
        Args:
            source: Informações da fonte
            table: Tabela DynamoDB
        """
        try:
            if not source.get("url"):
                logger.warning(f"Fonte sem URL RSS: {source['name']}")
                return
            
            # Valida feed RSS
            if not self.validate_rss_feed(source["url"], source["name"]):
                return
            
            # Parse do feed
            feed = feedparser.parse(source["url"])
            
            # Processa itens do feed
            processed_count = 0
            for entry in feed.entries[:get_config().content.max_news_per_source]:
                if self.process_news_item(entry, source, table):
                    processed_count += 1
                
                # Rate limiting
                rate_limit_delay(0.5)
            
            logger.info(f"Processadas {processed_count} notícias de {source['name']}")
            
        except Exception as e:
            logger.error(f"Erro ao coletar de {source['name']}: {e}")
            self.total_errors += 1
    
    def collect_all_news(self) -> Dict[str, Any]:
        """
        Coleta notícias de todas as fontes configuradas
        
        Returns:
            Dicionário com estatísticas da coleta
        """
        logger.info("Iniciando coleta de notícias")
        
        try:
            table = get_dynamodb_table()
            
            # Coleta por nicho
            for nicho in get_config().content.nichos:
                logger.info(f"Coletando notícias do nicho: {nicho}")
                
                fontes = buscar_fontes(nicho=nicho)
                if not fontes:
                    logger.warning(f"Nenhuma fonte encontrada para nicho: {nicho}")
                    continue
                
                for fonte in fontes:
                    self.collect_from_source(fonte, table)
            
            # Estatísticas finais
            execution_time = time.time() - self.start_time
            stats = {
                "salvas": self.total_saved,
                "existentes": self.total_existing,
                "erros": self.total_errors,
                "tempo_execucao": execution_time,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            logger.info(f"Coleta concluída: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Erro crítico na coleta: {e}")
            raise

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Função principal do Lambda
@datadog_lambda_wrapper
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal da função Lambda
    
    Args:
        event: Evento do Lambda
        context: Contexto do Lambda
        
    Returns:
        Dicionário com estatísticas da execução
    """
    logger.info("Iniciando execução da Lambda de coleta")
    
    try:
        # Valida variáveis obrigatórias
        validar_variaveis_obrigatorias(["MONGO_URI"])
        
        # Inicializa coletor
        collector = NewsCollector()
        
        # Executa coleta
        stats = collector.collect_all_news()
        
        logger.info("Execução da Lambda concluída com sucesso")
        return stats
        
    except Exception as e:
        logger.error(f"Erro na execução da Lambda: {e}")
        raise

if __name__ == "__main__":
    # Teste local
    lambda_handler({}, {})