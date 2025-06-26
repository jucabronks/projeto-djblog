"""
Utilitários para o projeto de agregação de notícias
"""
import logging
import os
import time
from typing import List, Dict, Any
from difflib import SequenceMatcher
import requests
from urllib.parse import urlparse
import hashlib
from datetime import datetime, timedelta, UTC

from config import get_config

# Configuração centralizada de logging


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configura logging centralizado com formato estruturado"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


logger = setup_logging()


def validar_variaveis_obrigatorias(nomes: List[str]) -> None:
    """Valida se variáveis de ambiente obrigatórias estão definidas"""
    faltando = []
    for nome in nomes:
        if not os.environ.get(nome):
            faltando.append(nome)

    if faltando:
        error_msg = f"Variáveis de ambiente obrigatórias não definidas: {', '.join(faltando)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def validar_url(url: str) -> bool:
    """
    Valida se uma URL é acessível

    Args:
        url: URL para validar

    Returns:
        True se a URL é válida e acessível
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code < 400

    except Exception as e:
        logger.debug(f"URL inválida ou inacessível: {url} - {e}")
        return False


def checar_plagio_local(title: str, resumo: str, table, threshold: float = 0.8) -> bool:
    """
    Verifica se uma notícia é plágio comparando com notícias existentes no DynamoDB

    Args:
        title: Título da notícia
        resumo: Resumo da notícia
        table: Tabela do DynamoDB
        threshold: Limiar de similaridade (0-1)

    Returns:
        True se for considerado plágio
    """
    try:
        from boto3.dynamodb.conditions import Attr

        # Normaliza o texto para comparação
        title_normalized = title.lower().strip()
        resumo_normalized = resumo.lower().strip()

        # Busca notícias recentes (últimos 7 dias)
        cutoff_date = datetime.now(UTC) - timedelta(days=7)
        cutoff_timestamp = int(cutoff_date.timestamp())

        response = table.scan(
            FilterExpression=Attr('data_insercao').gte(cutoff_timestamp),
            ProjectionExpression='titulo, resumo',
            Limit=100  # Limita para performance
        )

        for item in response.get('Items', []):
            titulo_existente = item.get("titulo", "").lower().strip()
            resumo_existente = item.get("resumo", "").lower().strip()

            # Calcula similaridade
            sim_titulo = SequenceMatcher(None, titulo_existente, title_normalized).ratio()
            sim_resumo = SequenceMatcher(None, resumo_existente, resumo_normalized).ratio()

            if sim_titulo > threshold or sim_resumo > threshold:
                logger.info(f"Plágio detectado - Título: {sim_titulo:.2f}, Resumo: {sim_resumo:.2f}")
                return True

        return False

    except Exception as e:
        logger.error(f"Erro ao checar plágio local: {e}")
        return False


def is_duplicate(noticia: Dict[str, Any], collection: Any, threshold: float = 0.8) -> bool:
    """
    Verifica se uma notícia é duplicada comparando com notícias publicadas

    Args:
        noticia: Notícia para verificar
        collection: Coleção/tabela do DynamoDB
        threshold: Limiar de similaridade (0-1)

    Returns:
        True se for duplicada
    """
    try:
        title_normalized = noticia["titulo"].lower().strip()
        resumo_normalized = noticia["resumo"].lower().strip()

        # Busca apenas notícias publicadas recentemente
        cutoff_date = datetime.now(UTC) - timedelta(days=30)  # 30 dias atrás

        for existente in collection.find(
            {
                "publicado": True,
                "data_insercao": {"$gte": cutoff_date}
            },
            {"titulo": 1, "resumo": 1}
        ).limit(50):  # Limita para performance

            titulo_existente = existente.get("titulo", "").lower().strip()
            resumo_existente = existente.get("resumo", "").lower().strip()

            sim_titulo = SequenceMatcher(None, titulo_existente, title_normalized).ratio()
            sim_resumo = SequenceMatcher(None, resumo_existente, resumo_normalized).ratio()

            if sim_titulo > threshold or sim_resumo > threshold:
                logger.info(f"Duplicata detectada - Título: {sim_titulo:.2f}, Resumo: {sim_resumo:.2f}")
                return True

        return False

    except Exception as e:
        logger.error(f"Erro ao verificar duplicidade: {e}")
        return False


def get_dynamodb_table(table_name: str = None):
    """
    Obtém uma tabela do DynamoDB

    Args:
        table_name: Nome da tabela (opcional, usa configuração padrão)

    Returns:
        Objeto tabela do DynamoDB
    """
    config = get_config()
    table_name = table_name or config.database.dynamodb_table_name

    dynamodb = config.get_dynamodb_resource()
    table = dynamodb.Table(table_name)

    return table


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitiza texto removendo caracteres especiais e limitando tamanho

    Args:
        text: Texto para sanitizar
        max_length: Comprimento máximo do texto

    Returns:
        Texto sanitizado
    """
    if not text:
        return ""

    # Remove caracteres especiais e normaliza espaços
    import re
    text = re.sub(r'\s+', ' ', text.strip())
    text = text[:max_length]

    return text


def generate_content_hash(title: str, resumo: str) -> str:
    """
    Gera hash único para o conteúdo da notícia

    Args:
        title: Título da notícia
        resumo: Resumo da notícia

    Returns:
        Hash SHA-256 do conteúdo
    """
    content = f"{title}:{resumo}".lower().strip()
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def rate_limit_delay(seconds: float = 1.0) -> None:
    """
    Adiciona delay para respeitar rate limits

    Args:
        seconds: Tempo de delay em segundos
    """
    time.sleep(seconds)


def retry_on_failure(func=None, *, max_retries: int = 3, delay: float = 1.0):
    """
    Decorator para retry em caso de falha
    Pode ser usado com ou sem parâmetros.
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                    if attempt == max_retries - 1:
                        logger.error(f"Função falhou após {max_retries} tentativas")
                        raise
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    if func is None:
        return decorator
    else:
        return decorator(func)


def inserir_noticia_coletada_legacy(item):
    """Função legacy - usar inserir_noticia_coletada() ao invés desta"""
    table = get_dynamodb_table()
    table.put_item(Item=item)


def buscar_noticias_coletadas():
    """Busca todas as notícias coletadas"""
    table = get_dynamodb_table()
    response = table.scan()
    return response.get('Items', [])


def inserir_noticia_resumida(item):
    """Insere notícia resumida"""
    config = get_config()
    dynamodb = config.get_dynamodb_resource()
    table = dynamodb.Table(f"{config.database.dynamodb_table_name}-resumidas")
    table.put_item(Item=item)


def buscar_noticias_resumidas():
    """Busca todas as notícias resumidas"""
    config = get_config()
    dynamodb = config.get_dynamodb_resource()
    table = dynamodb.Table(f"{config.database.dynamodb_table_name}-resumidas")
    response = table.scan()
    return response.get('Items', [])


def buscar_fontes(nicho: str = None, pais: str = "Brasil") -> List[Dict[str, str]]:
    """
    Busca fontes de notícias por nicho e país

    Args:
        nicho: Nicho das notícias (tecnologia, esportes, etc.)
        pais: País das fontes

    Returns:
        Lista de fontes de notícias
    """
    # Fontes exemplo - em produção viriam do DynamoDB
    fontes_exemplo = {
        "tecnologia": [
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "type": "RSS"},
            {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "type": "RSS"},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "type": "RSS"}
        ],
        "esportes": [
            {"name": "ESPN", "url": "https://www.espn.com/espn/rss/news", "type": "RSS"},
            {"name": "Sports Illustrated", "url": "https://www.si.com/rss/si_topstories.rss", "type": "RSS"}
        ]
    }

    if nicho and nicho in fontes_exemplo:
        return fontes_exemplo[nicho]

    # Retorna todas as fontes se nicho não especificado
    todas_fontes = []
    for lista_fontes in fontes_exemplo.values():
        todas_fontes.extend(lista_fontes)

    return todas_fontes


def inserir_noticia_coletada(noticia: Dict[str, Any]) -> bool:
    """
    Insere uma notícia coletada no DynamoDB

    Args:
        noticia: Dados da notícia

    Returns:
        True se inserção foi bem-sucedida
    """
    try:
        table = get_dynamodb_table()

        # Gera ID único baseado no link
        noticia_id = generate_content_hash(noticia.get('link', ''))
        noticia['id'] = noticia_id
        noticia['data_insercao'] = int(datetime.now(UTC).timestamp())

        table.put_item(Item=noticia)
        logger.info(f"Notícia inserida com sucesso: {noticia.get('titulo', '')}")
        return True

    except Exception as e:
        logger.error(f"Erro ao inserir notícia: {e}")
        return False


# Exemplos de uso:
if __name__ == "__main__":
    print("Fontes de tecnologia do Brasil:")
    for f in buscar_fontes(nicho="tecnologia"):
        print(f"- {f['name']} ({f.get('type', '')})")

    print("\nFontes de redes sociais internacionais:")
    for f in buscar_fontes(nicho="redes_sociais"):
        print(f"- {f['name']} ({f.get('type', '')})")
