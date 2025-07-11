"""
Testes para o lambda_coletor
"""
import pytest
from unittest.mock import Mock, patch

from lambda_coletor import (
    NewsCollector,
    lambda_handler
)


class TestNewsCollector:
    """Testes para a classe NewsCollector"""

    def setup_method(self):
        """Setup para cada teste"""
        self.collector = NewsCollector()

    def test_collector_initialization(self):
        """Testa inicialização do coletor"""
        assert self.collector.total_saved == 0
        assert self.collector.total_existing == 0
        assert self.collector.total_errors == 0
        assert self.collector.start_time > 0

    @patch('lambda_coletor.validar_url')
    @patch('lambda_coletor.feedparser.parse')
    def test_validate_rss_feed_success(self, mock_parse, mock_validate_url):
        """Testa validação de feed RSS bem-sucedida"""
        mock_validate_url.return_value = True

        mock_feed = Mock()
        mock_feed.entries = ["entry1", "entry2"]
        mock_feed.bozo = False
        mock_parse.return_value = mock_feed

        result = (
            self.collector.validate_rss_feed("https://example.com/rss", "Test Source")
        )
        assert result is True

    @patch('lambda_coletor.validar_url')
    def test_validate_rss_feed_invalid_url(self, mock_validate_url):
        """Testa validação de feed RSS com URL inválida"""
        mock_validate_url.return_value = False

        result = self.collector.validate_rss_feed("invalid-url", "Test Source")
        assert result is False

    @patch('lambda_coletor.validar_url')
    @patch('lambda_coletor.feedparser.parse')
    def test_validate_rss_feed_no_entries(self, mock_parse, mock_validate_url):
        """Testa validação de feed RSS sem entradas"""
        mock_validate_url.return_value = True

        mock_feed = Mock()
        mock_feed.entries = []
        mock_parse.return_value = mock_feed

        result = (
            self.collector.validate_rss_feed("https://example.com/rss", "Test Source")
        )
        assert result is False

    @patch('lambda_coletor.validar_url')
    @patch('lambda_coletor.feedparser.parse')
    def test_validate_rss_feed_bozo(self, mock_parse, mock_validate_url):
        """Testa validação de feed RSS malformado"""
        mock_validate_url.return_value = True

        mock_feed = Mock()
        mock_feed.entries = ["entry1"]
        mock_feed.bozo = True
        mock_parse.return_value = mock_feed

        result = (
            self.collector.validate_rss_feed("https://example.com/rss", "Test Source")
        )
        assert result is False

    def test_process_news_item_success(self):
        """Testa processamento bem-sucedido de item de notícia"""
        entry = {
            "title": "Test Title",
            "link": "https://example.com",
            "summary": "Test summary with enough content to process"
        }

        source = {
            "name": "Test Source",
            "nicho": "tecnologia",
            "type": "rss"
        }

        collection = Mock()
        collection.find_one.return_value = None  # Não existe ainda

        with patch('lambda_coletor.checar_plagio_local') as mock_plagio:
            mock_plagio.return_value = False

            result = self.collector.process_news_item(entry, source, collection)

            assert result is True
            assert self.collector.total_saved == 1
            collection.insert_one.assert_called_once()

    def test_process_news_item_missing_data(self):
        """Testa processamento de item com dados insuficientes"""
        entry = {
            "title": "",  # Título vazio
            "link": "https://example.com",
            "summary": "Test summary"
        }

        source = {
            "name": "Test Source",
            "nicho": "tecnologia"
        }

        collection = Mock()

        result = self.collector.process_news_item(entry, source, collection)

        assert result is False
        assert self.collector.total_saved == 0

    def test_process_news_item_already_exists(self):
        """Testa processamento de item que já existe"""
        entry = {
            "title": "Test Title",
            "link": "https://example.com",
            "summary": "Test summary"
        }

        source = {
            "name": "Test Source",
            "nicho": "tecnologia"
        }

        collection = Mock()
        collection.find_one.return_value = {"_id": "existing"}  # Já existe

        result = self.collector.process_news_item(entry, source, collection)

        assert result is False
        assert self.collector.total_existing == 1

    def test_process_news_item_plagio_detected(self):
        """Testa processamento de item com plágio detectado"""
        entry = {
            "title": "Test Title",
            "link": "https://example.com",
            "summary": "Test summary"
        }

        source = {
            "name": "Test Source",
            "nicho": "tecnologia"
        }

        collection = Mock()
        collection.find_one.return_value = None

        with patch('lambda_coletor.checar_plagio_local') as mock_plagio:
            mock_plagio.return_value = True  # Plágio detectado

            result = self.collector.process_news_item(entry, source, collection)

            assert result is False
            assert self.collector.total_existing == 1

    @patch('lambda_coletor.requests.post')
    @patch('lambda_coletor.get_config')
    def test_check_copyscape_plagiarism_no_plagio(self, mock_get_config, mock_post):
        """Testa verificação de plágio Copyscape sem plágio"""
        mock_response = Mock()
        mock_response.text = "<result><count>0</count></result>"
        mock_post.return_value = mock_response
        mock_config = Mock()
        mock_config.api.copys_api_user = "user"
        mock_config.api.copys_api_key = "key"
        mock_get_config.return_value = mock_config
        collector = NewsCollector()
        result = collector.check_copyscape_plagiarism("texto teste")
        assert result is False

    @patch('lambda_coletor.requests.post')
    @patch('lambda_coletor.get_config')
    def test_check_copyscape_plagiarism_with_plagio(self, mock_get_config, mock_post):
        """Testa verificação de plágio Copyscape com plágio"""
        mock_response = Mock()
        mock_response.text = "<result><count>1</count></result>"
        mock_post.return_value = mock_response
        mock_config = Mock()
        mock_config.api.copys_api_user = "user"
        mock_config.api.copys_api_key = "key"
        mock_get_config.return_value = mock_config
        collector = NewsCollector()
        result = collector.check_copyscape_plagiarism("texto teste")
        assert result is True

    @patch('lambda_coletor.buscar_fontes')
    @patch('lambda_coletor.get_config')
    def test_collect_from_source_success(self, mock_get_config, mock_buscar_fontes):
        """Testa coleta de fonte com sucesso"""
        source = {
            "name": "Test Source",
            "rss": "https://example.com/rss",
            "nicho": "tecnologia"
        }

        # Mock DynamoDB table
        mock_table = Mock()
        mock_config = Mock()
        mock_config.get_dynamodb_resource.return_value.Table.return_value = mock_table
        mock_get_config.return_value = mock_config

        with patch.object(self.collector, 'validate_rss_feed') as mock_validate:
            mock_validate.return_value = True

            with patch('lambda_coletor.feedparser.parse') as mock_parse:
                mock_feed = Mock()
                mock_feed.entries = [
                    {
                        "title": "Test Title",
                        "link": "https://example.com",
                        "summary": "Test summary"
                    }
                ]
                mock_parse.return_value = mock_feed

                with patch.object(self.collector, 'process_news_item') as mock_process:
                    mock_process.return_value = True

                    self.collector.collect_from_source(source, mock_table)

                    mock_process.assert_called_once()

    @patch('lambda_coletor.buscar_fontes')
    @patch('lambda_coletor.get_config')
    def test_collect_all_news_success(self, mock_get_config, mock_buscar_fontes):
        """Testa coleta completa de notícias"""
        mock_table = Mock()
        mock_config = Mock()
        mock_config.get_dynamodb_resource.return_value.Table.return_value = mock_table
        mock_config.content.nichos = ["tecnologia"]
        mock_get_config.return_value = mock_config
        mock_buscar_fontes.return_value = [
            {"name": "Test Source", "rss": "https://example.com/rss", "nicho": "tecnologia"}
        ]
        collector = NewsCollector()
        collector.collect_all_news()
        assert collector.total_errors == 0


class TestLambdaHandler:
    """Testes para o handler principal do Lambda"""

    @patch('lambda_coletor.validar_variaveis_obrigatorias')
    @patch('lambda_coletor.NewsCollector')
    def test_lambda_handler_success(self, mock_collector_class, mock_validate):
        """Testa execução bem-sucedida do handler"""
        mock_collector = Mock()
        mock_collector.collect_all_news.return_value = {
            "salvas": 5,
            "existentes": 2,
            "erros": 0
        }
        mock_collector_class.return_value = mock_collector

        # Criar mock adequado para o context do Lambda
        mock_context = Mock()
        mock_context.get_remaining_time_in_millis.return_value = 30000

        result = lambda_handler({}, mock_context)

        assert result["salvas"] == 5
        assert result["existentes"] == 2
        assert result["erros"] == 0

        mock_validate.assert_called_once_with(["AWS_REGION", "DYNAMODB_TABLE_NAME"])
        mock_collector.collect_all_news.assert_called_once()

    @patch('lambda_coletor.validar_variaveis_obrigatorias')
    def test_lambda_handler_validation_error(self, mock_validate):
        """Testa handler com erro de validação"""
        mock_validate.side_effect = ValueError("Missing required variables")

        # Criar mock adequado para o context do Lambda
        mock_context = Mock()
        mock_context.get_remaining_time_in_millis.return_value = 30000

        with pytest.raises(ValueError):
            lambda_handler({}, mock_context)

    @patch('lambda_coletor.validar_variaveis_obrigatorias')
    @patch('lambda_coletor.NewsCollector')
    def test_lambda_handler_collector_error(self, mock_collector_class, mock_validate):
        """Testa handler com erro no coletor"""
        mock_collector = Mock()
        mock_collector.collect_all_news.side_effect = (
            Exception("Collection failed")
        )
        mock_collector_class.return_value = mock_collector

        # Criar mock adequado para o context do Lambda
        mock_context = Mock()
        mock_context.get_remaining_time_in_millis.return_value = 30000

        with pytest.raises(Exception):
            lambda_handler({}, mock_context)


class TestIntegration:
    """Testes de integração"""

    @patch('lambda_coletor.os.environ')
    def test_full_integration_flow(self, mock_environ):
        """Testa fluxo completo de integração"""
        # Mock environment variables
        mock_environ.get.side_effect = lambda key, default=None: {
            "AWS_REGION": "us-east-1",
            "DYNAMODB_TABLE_NAME": "djblog-noticias",
            "NICHOS": "tecnologia,esportes"
        }.get(key, default)

        # Mock all external dependencies
        with patch('lambda_coletor.get_config') as mock_get_config:
            with patch('lambda_coletor.buscar_fontes') as mock_buscar_fontes:
                with patch('lambda_coletor.feedparser.parse') as mock_parse:

                    # Setup mocks
                    mock_table = Mock()
                    mock_config = Mock()
                    mock_config.get_dynamodb_resource.return_value.Table.return_value = mock_table
                    mock_get_config.return_value = mock_config

                    mock_buscar_fontes.return_value = [
                        {
                            "name": "Test Source",
                            "rss": "https://example.com/rss",
                            "nicho": "tecnologia",
                            "ativo": True
                        }
                    ]

                    mock_feed = Mock()
                    mock_feed.entries = [
                        {
                            "title": "Test News",
                            "link": "https://example.com/news",
                            "summary": "This is a test news article"
                        }
                    ]
                    mock_parse.return_value = mock_feed

                    # Mock DynamoDB operations
                    mock_table.get_item.return_value = {}  # Item not found
                    mock_table.put_item.return_value = True

                    # Criar mock adequado para o context do Lambda
                    mock_context = Mock()
                    mock_context.get_remaining_time_in_millis.return_value = 30000

                    # Execute
                    result = lambda_handler({}, mock_context)

                    # Assertions
                    assert "salvas" in result
                    assert "existentes" in result
                    assert "erros" in result
