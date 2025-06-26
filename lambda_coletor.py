"""
Função AWS Lambda para coleta de notícias automatizada, com integração Datadog, resumo automático com IA, revisão ortográfica e persistência no DynamoDB.

Como usar:
1. Instale o layer/pacote Datadog na Lambda (veja README)
2. Configure as variáveis de ambiente na Lambda:
   - DYNAMODB_TABLE_NAME: nome da tabela DynamoDB
   - AWS_REGION: região da AWS
   - OPENAI_API_KEY: chave da OpenAI (opcional)
   - DD_API_KEY: chave do Datadog
   - DD_SITE: datadoghq.com ou datadoghq.eu
   - DD_ENV: prod ou test
3. Faça upload deste arquivo como função Lambda (Python 3.8+)
4. Agende via EventBridge (CloudWatch Events) para rodar periodicamente
"""

import feedparser
from datetime import datetime, UTC
import requests
import time
from typing import Dict, Any
from dataclasses import dataclass

# Imports locais
from utils import (
    setup_logging,
    buscar_fontes,
    checar_plagio_local,
    get_dynamodb_table,
    validar_url,
    sanitize_text,
    generate_content_hash,
    rate_limit_delay,
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

try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

logger = setup_logging()


@dataclass
class CollectionStats:
    """Estatísticas da coleta"""
    total_saved: int = 0
    total_existing: int = 0
    total_errors: int = 0


class NewsCollector:
    """Coletor de notícias otimizado para Lambda"""

    def __init__(self):
        self.start_time = time.time()
        self.total_saved = 0
        self.total_existing = 0
        self.total_errors = 0

    def validate_rss_feed(self, rss_url: str, source_name: str) -> bool:
        """
        Valida se o feed RSS está acessível

        Args:
            rss_url: URL do feed RSS
            source_name: Nome da fonte

        Returns:
            True se o feed está válido
        """
        try:
            # Valida URL
            if not validar_url(rss_url):
                logger.warning(f"URL inválida para {source_name}: {rss_url}")
                return False

            # Testa parse do feed
            feed = feedparser.parse(rss_url)
            if hasattr(feed, 'bozo') and feed.bozo:
                logger.warning(f"Feed RSS com problemas para {source_name}: {feed.bozo_exception}")
                return False

            if not feed.entries:
                logger.warning(f"Feed RSS vazio para {source_name}")
                return False

            return True

        except Exception as e:
            logger.error(f"Erro ao validar RSS de {source_name}: {e}")
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
            noticia_id = generate_content_hash(title, resumo)

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

        if "<r>" in response.text and "<count>0</count>" in response.text:
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
        logger.info("Iniciando execução da Lambda de coleta")

        # Validação de configuração
        config = get_config()
        logger.info(f"Configuração carregada - Nichos: {config.content.nichos}")

        # Executa coleta
        collector = NewsCollector()
        stats = collector.collect_all_news()

        return {
            'statusCode': 200,
            'body': {
                'message': 'Coleta executada com sucesso',
                'statistics': stats
            }
        }

    except Exception as e:
        logger.error(f"Erro na execução da Lambda: {e}")
        return {
            'statusCode': 500,
            'body': {
                'message': f'Erro na coleta: {str(e)}'
            }
        }


# Wrapper Datadog se disponível
if DATADOG_AVAILABLE:
    lambda_handler = datadog_lambda_wrapper(lambda_handler)
