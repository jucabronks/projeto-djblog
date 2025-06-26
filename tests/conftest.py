"""
Configuração simplificada dos testes
"""
import os
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_dynamodb_table():
    """Mock para tabela DynamoDB"""
    table = Mock()
    table.get_item.return_value = {}
    table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    table.scan.return_value = {"Items": []}
    return table


@pytest.fixture
def mock_lambda_context():
    """Mock simplificado do contexto Lambda"""
    context = Mock()
    context.function_name = "test-function"
    context.aws_request_id = "test-request-id"
    context.get_remaining_time_in_millis.return_value = 30000
    return context


@pytest.fixture(autouse=True)
def disable_datadog():
    """Desabilita decorador Datadog Lambda para testes"""
    with patch('lambda_coletor.datadog_lambda_wrapper') as mock_dd:
        mock_dd.side_effect = lambda f: f  # Retorna função sem modificação
        yield


@pytest.fixture(autouse=True)
def mock_aws_credentials():
    """Mock de credenciais AWS para testes"""
    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing',
        'AWS_DEFAULT_REGION': 'us-east-1'
    }):
        yield
