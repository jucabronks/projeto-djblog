"""
Testes para o módulo de configuração
"""
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
        # Remove uma variável obrigatória para testar a validação
        monkeypatch.delenv("AWS_REGION", raising=False)

        importlib.reload(importlib.import_module("config"))
        from config import validate_required_vars
        # Com DynamoDB, a função não levanta mais exceção, apenas retorna variáveis faltando
        missing = validate_required_vars()
        # Se não há variáveis obrigatórias configuradas como essenciais, retorna lista vazia
        assert isinstance(missing, list)

        monkeypatch.setenv("AWS_REGION", "us-east-1")
        importlib.reload(importlib.import_module("config"))
        missing = validate_required_vars()
        assert len(missing) == 0

    def test_environment_variables(self, monkeypatch):
        """Testa leitura de variáveis de ambiente"""
        monkeypatch.setenv("AWS_REGION", "us-east-1")
        monkeypatch.setenv("DYNAMODB_TABLE_NAME", "test-table")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("NICHOS", "tecnologia,esportes")
        monkeypatch.setenv("MAX_NEWS_PER_SOURCE", "5")

        # Recarregar configurações
        importlib.reload(importlib.import_module("config"))
        from config import get_config
        config = get_config()

        assert config.database.dynamodb_table_name == "test-table"
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

    def test_dynamodb_configuration(self, monkeypatch):
        """Testa configuração do DynamoDB"""
        monkeypatch.setenv("AWS_REGION", "us-east-1")
        monkeypatch.setenv("DYNAMODB_TABLE_NAME", "test-table")

        importlib.reload(importlib.import_module("config"))
        from config import get_config
        config = get_config()

        assert config.database.dynamodb_table_name == "test-table"
        # Test que o recurso DynamoDB pode ser obtido
        dynamodb = config.get_dynamodb_resource()
        assert dynamodb is not None
