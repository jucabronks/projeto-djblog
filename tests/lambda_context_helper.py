"""
Helper para criar mock do contexto Lambda compatível com Datadog
"""
from unittest.mock import Mock


def create_lambda_context_mock():
    """Cria mock completo do contexto Lambda"""
    mock_context = Mock()
    mock_context.invoked_function_arn = (
        "arn:aws:lambda:us-east-1:123456789012:function:test"
    )
    mock_context.function_name = "test-function"
    mock_context.function_version = "$LATEST"
    mock_context.log_group_name = "/aws/lambda/test-function"
    mock_context.log_stream_name = "2025/06/25/[$LATEST]test"
    mock_context.aws_request_id = "test-request-id-123"
    mock_context.get_remaining_time_in_millis.return_value = 30000
    mock_context.memory_limit_in_mb = 512
    return mock_context


def patch_datadog_lambda():
    """Patch para remover decorador datadog lambda"""
    def decorator_bypass(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator_bypass
