"""
Utilitários para o projeto de agregação de notícias
"""
import logging
import os
import time
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError
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

def conectar_mongodb(uri: Optional[str] = None, max_retries: int = 3) -> Tuple[MongoClient, Any]:
    """
    Conecta ao MongoDB com retry e configurações otimizadas
    
    Args:
        uri: String de conexão do MongoDB (opcional)
        max_retries: Número máximo de tentativas de conexão
    
    Returns:
        Tuple com client e database
        
    Raises:
        ConnectionFailure: Se não conseguir conectar após todas as tentativas
    """
    mongo_uri = uri or get_config().get_mongo_connection_string()
    
    if not mongo_uri:
        raise ValueError("MONGO_URI não configurada")
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de conexão com MongoDB")
            client = MongoClient(mongo_uri)
            
            # Testa a conexão
            client.admin.command('ping')
            db = client.get_default_database()
            
            logger.info("Conexão com MongoDB estabelecida com sucesso")
            return client, db
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Falha ao conectar no MongoDB após {max_retries} tentativas")
                raise ConnectionFailure(f"Não foi possível conectar ao MongoDB: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logger.error(f"Erro inesperado ao conectar no MongoDB: {e}")
            raise

def buscar_fontes(nicho: Optional[str] = None, ativo: bool = True) -> List[Dict[str, Any]]:
    """
    Busca fontes de notícias no MongoDB com cache e validação
    
    Args:
        nicho: Nicho específico para filtrar
        ativo: Se deve buscar apenas fontes ativas
    
    Returns:
        Lista de fontes de notícias
    """
    try:
        client, db = conectar_mongodb()
        query = {"ativo": ativo}
        
        if nicho:
            query["nicho"] = nicho
        
        # Adiciona índices para melhor performance
        db["fontes_noticias"].create_index([("nicho", 1), ("ativo", 1)])
        
        fontes = list(db["fontes_noticias"].find(query))
        client.close()
        
        logger.info(f"Encontradas {len(fontes)} fontes para nicho: {nicho or 'todos'}")
        return fontes
        
    except Exception as e:
        logger.error(f"Erro ao buscar fontes no MongoDB: {e}")
        return []

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

def checar_plagio_local(title: str, resumo: str, collection: Any, threshold: float = 0.8) -> bool:
    """
    Verifica se uma notícia é plágio comparando com notícias existentes
    
    Args:
        title: Título da notícia
        resumo: Resumo da notícia
        collection: Coleção do MongoDB
        threshold: Limiar de similaridade (0-1)
    
    Returns:
        True se for considerado plágio
    """
    try:
        # Normaliza o texto para comparação
        title_normalized = title.lower().strip()
        resumo_normalized = resumo.lower().strip()
        
        # Busca apenas notícias recentes para melhor performance
        cutoff_date = datetime.now(UTC) - timedelta(days=7)  # 7 dias atrás
        
        for noticia_existente in collection.find(
            {"data_insercao": {"$gte": cutoff_date}},
            {"titulo": 1, "resumo": 1}
        ).limit(100):  # Limita para performance
            
            titulo_existente = noticia_existente.get("titulo", "").lower().strip()
            resumo_existente = noticia_existente.get("resumo", "").lower().strip()
            
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
        collection: Coleção do MongoDB
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

def get_collection(collection_name: str = "noticias_coletadas") -> Tuple[MongoClient, Any]:
    """
    Obtém uma coleção específica do MongoDB com configurações otimizadas
    
    Args:
        collection_name: Nome da coleção
    
    Returns:
        Tuple com client e collection
    """
    client, db = conectar_mongodb()
    collection = db[collection_name]
    
    # Cria índices para melhor performance
    collection.create_index([("link", 1)], unique=True)
    collection.create_index([("nicho", 1), ("aprovado", 1), ("publicado", 1)])
    collection.create_index([("data_insercao", -1)])
    collection.create_index([("fonte", 1)])
    
    return client, collection

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

# Exemplos de uso:
if __name__ == "__main__":
    print("Fontes de tecnologia do Brasil:")
    for f in buscar_fontes(nicho="tecnologia"):
        print(f"- {f['name']} ({f.get('type', '')})")

    print("\nFontes de redes sociais internacionais:")
    for f in buscar_fontes(nicho="redes_sociais"):
        print(f"- {f['name']} ({f.get('type', '')})") 