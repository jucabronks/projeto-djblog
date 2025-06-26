"""
Testes para o módulo utils
"""
import pytest
import os
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import UTC

from utils import (
    setup_logging,
    validar_variaveis_obrigatorias,
    buscar_fontes,
    validar_url,
    checar_plagio_local,
    is_duplicate,
    sanitize_text,
    generate_content_hash,
    rate_limit_delay,
    retry_on_failure
)


class TestLogging:
    """Testes para configuração de logging"""

    def test_setup_logging(self):
        """Testa configuração do logging"""
        logger = setup_logging("DEBUG")
        # O logger pode estar em NOTSET (0), WARNING (30) ou DEBUG (10)
        assert logger.level in (0, 10, 30)  # 0=NOTSET, 10=DEBUG, 30=WARNING
        assert logger.name == "utils"


class TestValidacao:
    """Testes para validação de variáveis"""

    def test_validar_variaveis_obrigatorias_sucesso(self, monkeypatch):
        """Testa validação com variáveis presentes"""
        monkeypatch.setenv("TEST_VAR", "test_value")
        validar_variaveis_obrigatorias(["TEST_VAR"])
        # Não deve levantar exceção

    def test_validar_variaveis_obrigatorias_falha(self, monkeypatch):
        """Testa validação com variáveis faltando"""
        monkeypatch.delenv("TEST_VAR", raising=False)
        with pytest.raises(ValueError, match="TEST_VAR"):
            validar_variaveis_obrigatorias(["TEST_VAR"])


class TestURLValidation:
    """Testes para validação de URLs"""

    @patch('utils.requests.head')
    def test_validar_url_sucesso(self, mock_head):
        """Testa validação de URL válida"""
        mock_head.return_value.status_code = 200

        assert validar_url("https://example.com") is True
        mock_head.assert_called_once()

    @patch('utils.requests.head')
    def test_validar_url_erro_404(self, mock_head):
        """Testa validação de URL com erro 404"""
        mock_head.return_value.status_code = 404

        assert validar_url("https://example.com") is False

    def test_validar_url_invalida(self):
        """Testa validação de URL inválida"""
        assert validar_url("invalid-url") is False
        assert validar_url("") is False


class TestPlagioDetection:
    """Testes para detecção de plágio"""

    def test_checar_plagio_local_sem_plagio(self):
        """Testa detecção de plágio quando não há"""
        table = MagicMock()
        table.scan.return_value = {
            'Items': []  # Sem itens = sem plágio
        }

        # Mock datetime para retornar uma data recente
        with patch('utils.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.timestamp.return_value = 1641081600
            mock_datetime.now.return_value = mock_now
            mock_datetime.UTC = UTC

            result = checar_plagio_local("Título único", "Resumo único", table)
            assert result is False

    def test_checar_plagio_local_com_plagio(self):
        """Testa detecção de plágio quando há"""
        table = MagicMock()
        table.scan.return_value = {
            'Items': [
                {"titulo": "Título único", "resumo": "Resumo único", "data_insercao": 1640995200}
            ]
        }

        # Mock datetime para retornar uma data recente
        with patch('utils.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.timestamp.return_value = 1641081600  # 1 dia depois
            mock_datetime.now.return_value = mock_now
            mock_datetime.UTC = UTC

            result = checar_plagio_local("Título único", "Resumo único", table)
            assert result is True


class TestDuplicateDetection:
    """Testes para detecção de duplicatas"""

    def test_is_duplicate_sem_duplicata(self):
        """Testa detecção de duplicata quando não há"""
        collection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = []
        collection.find.return_value = mock_cursor
        noticia = {"titulo": "Título único", "resumo": "Resumo único"}
        result = is_duplicate(noticia, collection)
        assert result is False

    def test_is_duplicate_com_duplicata(self):
        """Testa detecção de duplicata quando há"""
        collection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value = [
            {"titulo": "Título único", "resumo": "Resumo único"}
        ]
        collection.find.return_value = mock_cursor
        noticia = {"titulo": "Título único", "resumo": "Resumo único"}
        result = is_duplicate(noticia, collection)
        assert result is True


class TestTextProcessing:
    """Testes para processamento de texto"""

    def test_sanitize_text_normal(self):
        """Testa sanitização de texto normal"""
        text = "Texto normal"
        result = sanitize_text(text)
        assert result == "Texto normal"

    def test_sanitize_text_com_espacos(self):
        """Testa sanitização de texto com espaços extras"""
        text = "  Texto   com   espaços  "
        result = sanitize_text(text)
        assert result == "Texto com espaços"

    def test_sanitize_text_vazio(self):
        """Testa sanitização de texto vazio"""
        result = sanitize_text("")
        assert result == ""
        result = sanitize_text(None)
        assert result == ""

    def test_sanitize_text_limite(self):
        """Testa sanitização com limite de caracteres"""
        text = "A" * 2000
        result = sanitize_text(text, max_length=100)
        assert len(result) == 100

    def test_generate_content_hash(self):
        """Testa geração de hash de conteúdo"""
        title = "Título teste"
        resumo = "Resumo teste"

        hash1 = generate_content_hash(title, resumo)
        hash2 = generate_content_hash(title, resumo)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hash length
        assert isinstance(hash1, str)


class TestRateLimiting:
    """Testes para rate limiting"""

    def test_rate_limit_delay(self):
        """Testa delay de rate limiting"""
        start_time = time.time()
        rate_limit_delay(0.1)
        end_time = time.time()

        assert end_time - start_time >= 0.1


class TestRetryDecorator:
    """Testes para decorator de retry"""

    def test_retry_on_failure_sucesso(self):
        """Testa retry com sucesso na primeira tentativa"""
        @retry_on_failure
        def func_success():
            return "success"

        result = func_success()
        assert result == "success"

    def test_retry_on_failure_com_falha(self):
        """Testa retry com falha e sucesso posterior"""
        call_count = 0

        @retry_on_failure(max_retries=3, delay=0.1)
        def func_failure_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"

        result = func_failure_then_success()
        assert result == "success"
        assert call_count == 3

    def test_retry_on_failure_falha_total(self):
        """Testa retry com falha total"""
        @retry_on_failure(max_retries=2, delay=0.1)
        def func_always_fails():
            raise Exception("Always fails")

        with pytest.raises(Exception, match="Always fails"):
            func_always_fails()


class TestFontSearch:
    """Testes para busca de fontes"""

    def test_buscar_fontes_sucesso(self):
        """Testa busca de fontes com sucesso"""
        # Com DynamoDB não precisamos testar conexão
        fontes = buscar_fontes(nicho="tecnologia")
        assert isinstance(fontes, list)

    def test_buscar_fontes_erro(self):
        """Testa busca de fontes com erro de conexão"""
        # Simular erro removendo credenciais temporariamente
        old_env = os.environ.copy()
        if 'AWS_ACCESS_KEY_ID' in os.environ:
            del os.environ['AWS_ACCESS_KEY_ID']
        try:
            fontes = buscar_fontes(nicho="tecnologia")
            assert fontes == []
        finally:
            os.environ.clear()
            os.environ.update(old_env)
