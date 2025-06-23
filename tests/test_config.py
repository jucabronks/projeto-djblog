"""
Testes para o módulo de configuração
"""
import pytest
import os
import importlib

class TestConfig:
    """Testes para a classe Config"""
    
    def test_default_values(self, monkeypatch):
        """Testa valores padrão das configurações"""
        monkeypatch.setenv("MONGO_URI", "mongodb://test")
        monkeypatch.setenv("DD_ENV", "test")
        importlib.reload(importlib.import_module("config"))
        from config import get_config
        config = get_config()
        
        assert config.monitoring.dd_site == "datadoghq.com"
        assert config.monitoring.dd_env == "test"
        assert config.content.pais == "Brasil"
        assert config.content.max_news_per_source == 3
        assert config.content.threshold_caracteres == 250
    
    def test_nichos_default(self, monkeypatch):
        """Testa nichos padrão"""
        monkeypatch.setenv("MONGO_URI", "mongodb://test")
        monkeypatch.setenv("NICHOS", "tecnologia,esportes")
        importlib.reload(importlib.import_module("config"))
        from config import get_config
        config = get_config()
        
        expected_nichos = ["tecnologia", "esportes"]
        assert config.content.nichos == expected_nichos
    
    def test_categorias_wp(self, monkeypatch):
        """Testa mapeamento de categorias WordPress"""
        monkeypatch.setenv("MONGO_URI", "mongodb://test")
        
        importlib.reload(importlib.import_module("config"))
        from config import get_config
        config = get_config()
        
        assert config.get_categoria_wp("tecnologia") == 2
        assert config.get_categoria_wp("esportes") == 3
        assert config.get_categoria_wp("saude") == 4
        assert config.get_categoria_wp("economia") == 5
        assert config.get_categoria_wp("nichos_inexistente") == 1  # Uncategorized
    
    def test_validate_required_vars(self, monkeypatch):
        """Testa validação de variáveis obrigatórias"""
        monkeypatch.delenv("MONGO_URI", raising=False)
        
        importlib.reload(importlib.import_module("config"))
        from config import validate_required_vars
        with pytest.raises(Exception):
            validate_required_vars()
        
        monkeypatch.setenv("MONGO_URI", "mongodb://test")
        importlib.reload(importlib.import_module("config"))
        missing = validate_required_vars()
        assert len(missing) == 0
    
    def test_environment_variables(self, monkeypatch):
        """Testa leitura de variáveis de ambiente"""
        monkeypatch.setenv("MONGO_URI", "mongodb://test")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("NICHOS", "tecnologia,esportes")
        monkeypatch.setenv("MAX_NEWS_PER_SOURCE", "5")
        
        # Recarregar configurações
        importlib.reload(importlib.import_module("config"))
        from config import get_config
        config = get_config()
        
        assert config.database.mongo_uri == "mongodb://test"
        assert config.api.openai_api_key == "sk-test"
        assert config.content.nichos == ["tecnologia", "esportes"]
        assert config.content.max_news_per_source == 5
    
    def test_wordpress_configuration(self, monkeypatch):
        """Testa configuração do WordPress"""
        monkeypatch.setenv("MONGO_URI", "mongodb://test")
        monkeypatch.setenv("WP_URL", "https://test.com/wp-json/wp/v2")
        monkeypatch.setenv("WP_USER", "admin")
        monkeypatch.setenv("WP_APP_PASSWORD", "password")
        
        importlib.reload(importlib.import_module("config"))
        from config import get_config
        config = get_config()
        
        assert config.is_wordpress_configured() is True
        assert config.wordpress.wp_url == "https://test.com/wp-json/wp/v2"
        assert config.wordpress.wp_user == "admin"
        assert config.wordpress.wp_app_password == "password"
    
    def test_openai_configuration(self, monkeypatch):
        """Testa configuração da OpenAI"""
        monkeypatch.setenv("MONGO_URI", "mongodb://test")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        
        importlib.reload(importlib.import_module("config"))
        from config import get_config
        config = get_config()
        
        assert config.is_openai_configured() is True
        assert config.api.openai_api_key == "sk-test"
    
    def test_copyscape_configuration(self, monkeypatch):
        """Testa configuração do Copyscape"""
        monkeypatch.setenv("MONGO_URI", "mongodb://test")
        monkeypatch.setenv("COPYS_API_USER", "user")
        monkeypatch.setenv("COPYS_API_KEY", "key")
        
        importlib.reload(importlib.import_module("config"))
        from config import get_config
        config = get_config()
        
        assert config.is_copyscape_configured() is True
        assert config.api.copys_api_user == "user"
        assert config.api.copys_api_key == "key"
    
    def test_mongo_connection_string(self, monkeypatch):
        """Testa geração da string de conexão do MongoDB"""
        monkeypatch.setenv("MONGO_URI", "mongodb://test")
        
        importlib.reload(importlib.import_module("config"))
        from config import get_config
        config = get_config()
        
        connection_string = config.get_mongo_connection_string()
        assert "mongodb://test?" in connection_string
        assert "maxPoolSize=100" in connection_string
        assert "retryWrites=true" in connection_string 