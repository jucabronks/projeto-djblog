"""
Configuração de testes para o projeto
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Configura variáveis de ambiente para testes
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Configura ambiente de teste automaticamente"""
    # Salva variáveis originais
    original_env = os.environ.copy()
    
    # Define variáveis de teste
    test_env = {
        "MONGO_URI": "mongodb://test:27017/test",
        "OPENAI_API_KEY": "sk-test-key",
        "DD_API_KEY": "test-dd-key",
        "DD_SITE": "datadoghq.com",
        "DD_ENV": "test",
        "NICHOS": "tecnologia,esportes",
        "PAIS": "Brasil",
        "MAX_NEWS_PER_SOURCE": "3",
        "THRESHOLD_CARACTERES": "250",
        "COPYS_API_USER": "test-user",
        "COPYS_API_KEY": "test-key",
        "WP_URL": "https://test.com/wp-json/wp/v2",
        "WP_USER": "admin",
        "WP_APP_PASSWORD": "test-password",
        "ALARM_EMAIL": "test@example.com"
    }
    
    # Aplica variáveis de teste
    for key, value in test_env.items():
        os.environ[key] = value
    
    yield
    
    # Restaura variáveis originais
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def mock_mongodb():
    """Mock para conexão MongoDB"""
    with patch('utils.MongoClient') as mock_client:
        mock_instance = Mock()
        mock_instance.admin.command.return_value = True
        mock_instance.get_default_database.return_value = Mock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_requests():
    """Mock para requests"""
    with patch('utils.requests') as mock_req:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "OK"
        mock_req.head.return_value = mock_response
        mock_req.post.return_value = mock_response
        yield mock_req

@pytest.fixture
def mock_openai():
    """Mock para OpenAI"""
    with patch('summarize_ai.openai') as mock_ai:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Resumo de teste"
        mock_client.chat.completions.create.return_value = mock_response
        mock_ai.OpenAI.return_value = mock_client
        yield mock_ai 