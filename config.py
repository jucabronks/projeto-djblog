"""
Configurações centralizadas do projeto
"""
import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Configurações do banco de dados"""
    dynamodb_table_name: str = "djblog-noticias"
    aws_region: str = "us-east-1"

@dataclass
class APIConfig:
    """Configurações de APIs externas"""
    openai_api_key: Optional[str] = None
    copys_api_user: Optional[str] = None
    copys_api_key: Optional[str] = None

@dataclass
class MonitoringConfig:
    """Configurações de monitoramento"""
    dd_api_key: Optional[str] = None
    dd_site: str = "datadoghq.com"
    dd_env: str = "prod"
    alarm_email: Optional[str] = None

@dataclass
class ContentConfig:
    """Configurações de conteúdo"""
    nichos: List[str]
    pais: str = "Brasil"
    max_news_per_source: int = 3
    threshold_caracteres: int = 250
    language: str = "pt-BR"

@dataclass
class WordPressConfig:
    """Configurações do WordPress"""
    wp_url: Optional[str] = None
    wp_user: Optional[str] = None
    wp_app_password: Optional[str] = None
    categorias_wp: Dict[str, int] = None

class Config:
    """Configurações do projeto com validação robusta"""
    
    def __init__(self):
        self._load_configurations()
        self._validate_configurations()
    
    def _load_configurations(self):
        """Carrega todas as configurações do ambiente"""
        # Database
        self.database = DatabaseConfig(
            dynamodb_table_name=os.environ.get("DYNAMODB_TABLE_NAME", "djblog-noticias"),
            aws_region=os.environ.get("AWS_REGION", "us-east-1")
        )
        
        # APIs
        self.api = APIConfig(
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            copys_api_user=os.environ.get("COPYS_API_USER"),
            copys_api_key=os.environ.get("COPYS_API_KEY")
        )
        
        # Monitoring
        self.monitoring = MonitoringConfig(
            dd_api_key=os.environ.get("DD_API_KEY"),
            dd_site=os.environ.get("DD_SITE", "datadoghq.com"),
            dd_env=os.environ.get("DD_ENV", "prod"),
            alarm_email=os.environ.get("ALARM_EMAIL")
        )
        
        # Content
        nichos_str = os.environ.get("NICHOS", "saude,esportes,tecnologia,economia")
        self.content = ContentConfig(
            nichos=[n.strip() for n in nichos_str.split(",") if n.strip()],
            pais=os.environ.get("PAIS", "Brasil"),
            max_news_per_source=int(os.environ.get("MAX_NEWS_PER_SOURCE", 3)),
            threshold_caracteres=int(os.environ.get("THRESHOLD_CARACTERES", 250)),
            language=os.environ.get("LANGUAGE", "pt-BR")
        )
        
        # WordPress
        self.wordpress = WordPressConfig(
            wp_url=os.environ.get("WP_URL"),
            wp_user=os.environ.get("WP_USER"),
            wp_app_password=os.environ.get("WP_APP_PASSWORD"),
            categorias_wp={
                "tecnologia": 2,
                "esportes": 3,
                "saude": 4,
                "economia": 5,
                "ciencia": 6,
                "politica": 7,
                "entretenimento": 8,
                "educacao": 9,
                "startups": 10,
                "fintech": 11,
                "ia": 12,
                "sustentabilidade": 13,
                "internacional": 14
            }
        )
    
    def _validate_configurations(self):
        """Valida todas as configurações obrigatórias"""
        errors = []
        
        # Validações obrigatórias
        if not self.database.dynamodb_table_name:
            errors.append("DYNAMODB_TABLE_NAME é obrigatória")
        
        if not self.database.aws_region:
            errors.append("AWS_REGION é obrigatória")
        
        # Validações de formato
        if self.content.max_news_per_source <= 0:
            errors.append("MAX_NEWS_PER_SOURCE deve ser maior que 0")
        
        if self.content.threshold_caracteres <= 0:
            errors.append("THRESHOLD_CARACTERES deve ser maior que 0")
        
        if errors:
            error_msg = "Erros de configuração:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configurações validadas com sucesso")
    
    def get_categoria_wp(self, nicho: str) -> int:
        """Retorna ID da categoria WordPress para um nicho"""
        return self.wordpress.categorias_wp.get(nicho.lower(), 1)  # 1 = Uncategorized
    
    def is_wordpress_configured(self) -> bool:
        """Verifica se o WordPress está configurado"""
        return all([
            self.wordpress.wp_url,
            self.wordpress.wp_user,
            self.wordpress.wp_app_password
        ])
    
    def is_openai_configured(self) -> bool:
        """Verifica se a OpenAI está configurada"""
        return bool(self.api.openai_api_key)
    
    def is_copyscape_configured(self) -> bool:
        """Verifica se o Copyscape está configurado"""
        return bool(self.api.copys_api_user and self.api.copys_api_key)
    
    def is_datadog_configured(self) -> bool:
        """Verifica se o Datadog está configurado"""
        return bool(self.monitoring.dd_api_key)
    
    def get_dynamodb_resource(self):
        """Retorna recurso DynamoDB configurado"""
        import boto3
        return boto3.resource('dynamodb', region_name=self.database.aws_region)

_config_instance = None

def get_config():
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

def validate_required_vars() -> List[str]:
    """Valida variáveis obrigatórias e retorna lista de faltantes"""
    config = get_config()
    required_vars = ["DYNAMODB_TABLE_NAME", "AWS_REGION"]
    missing = []
    
    for var in required_vars:
        if var == "DYNAMODB_TABLE_NAME" and not config.database.dynamodb_table_name:
            missing.append(var)
        elif var == "AWS_REGION" and not config.database.aws_region:
            missing.append(var)
    
    return missing

def get_categoria_wp(nicho: str) -> int:
    """Retorna ID da categoria WordPress para um nicho"""
    return get_config().get_categoria_wp(nicho) 