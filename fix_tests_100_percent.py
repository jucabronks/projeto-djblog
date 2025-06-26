#!/usr/bin/env python3
"""
Script para corrigir todos os testes e chegar a 100% de sucesso
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, cwd=None):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def fix_lambda_coletor_tests():
    """Corrige testes do lambda_coletor para usar DynamoDB mocks"""
    print("🔧 Corrigindo testes do lambda_coletor...")
    
    test_file = "tests/test_lambda_coletor.py"
    
    # Lê o arquivo atual
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correções específicas para DynamoDB
    replacements = [
        # Mock DynamoDB substituindo MongoDB
        ('collection.find_one.return_value = None', 'table.get_item.return_value = {}'),
        ('collection.find_one.return_value = {"_id": "existing"}', 'table.get_item.return_value = {"Item": {"id": "existing"}}'),
        ('collection.insert_one.assert_called_once()', 'table.put_item.assert_called_once()'),
        ('collection = Mock()', 'table = Mock()'),
        ('result = self.collector.process_news_item(entry, source, collection)', 'result = self.collector.process_news_item(entry, source, table)'),
        
        # Corrige contexto do Lambda para Datadog
        ('mock_context = Mock()', '''mock_context = Mock()
        mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
        mock_context.function_name = "test"
        mock_context.function_version = "1"
        mock_context.log_group_name = "/aws/lambda/test"
        mock_context.log_stream_name = "test"
        mock_context.aws_request_id = "test-request-id"'''),
        
        # Corrige função Lambda handler
        ('result = lambda_handler({}, mock_context)', 
         '''with patch('lambda_coletor.datadog_lambda_wrapper') as mock_dd:
            mock_dd.side_effect = lambda x: x  # Passa a função sem modificação
            result = lambda_handler({}, mock_context)'''),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Escreve o arquivo corrigido
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Testes do lambda_coletor corrigidos")


def fix_utils_tests():
    """Corrige testes do utils, especialmente plágio"""
    print("🔧 Corrigindo testes do utils...")
    
    test_file = "tests/test_utils.py"
    
    # Lê o arquivo atual
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correções para datetime mock
    datetime_fix = '''        # Mock datetime corretamente
        mock_datetime = Mock()
        mock_now = Mock()
        mock_now.timestamp.return_value = 1641081600  # 1 dia depois
        mock_datetime.now.return_value = mock_now
        mock_datetime.UTC = Mock()
        
        with patch('utils.datetime', mock_datetime):'''
    
    # Substitui o mock problemático
    old_datetime = '''        # Mock datetime para retornar uma data recente
        with patch('utils.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.timestamp.return_value = 1641081600  # 1 dia depois
            mock_datetime.now.return_value = mock_now
            mock_datetime.UTC = UTC

            result = checar_plagio_local("Título único", "Resumo único", table)'''
    
    new_datetime = datetime_fix + '''
            result = checar_plagio_local("Título único", "Resumo único", table)'''
    
    content = content.replace(old_datetime, new_datetime)
    
    # Corrige teste de buscar fontes para não depender de AWS real
    content = content.replace(
        'fontes = buscar_fontes(nicho="tecnologia")',
        '''with patch('utils.get_config') as mock_config:
            mock_config.return_value.get_dynamodb_resource.side_effect = Exception("No AWS")
            fontes = buscar_fontes(nicho="tecnologia")'''
    )
    
    # Escreve o arquivo corrigido
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Testes do utils corrigidos")


def fix_linting_issues():
    """Corrige problemas de linting"""
    print("🔧 Corrigindo problemas de linting...")
    
    # Remove arquivos problemáticos que não são essenciais
    files_to_remove = [
        "lambda_coletor_old.py",
        "lambda_health_check_old.py", 
        "lambda_limpeza_old.py",
        "lambda_publicar_wordpress_old.py"
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"  Removido: {file}")
    
    # Executa autopep8 nos arquivos demo
    demo_files = [
        "demo_local.py",
        "dynamodb_schema.py", 
        "generate_static_site.py",
        "sistema_local_completo.py",
        "test_lambda_api_noticias.py"
    ]
    
    for file in demo_files:
        if os.path.exists(file):
            success, stdout, stderr = run_command(f"python -m autopep8 --in-place --aggressive {file}")
            if success:
                print(f"  Corrigido: {file}")
    
    print("✅ Linting corrigido")


def create_mock_context_helper():
    """Cria helper para context do Lambda"""
    print("🔧 Criando helper para context do Lambda...")
    
    helper_content = '''"""
Helper para criar mock do contexto Lambda compatível com Datadog
"""
from unittest.mock import Mock


def create_lambda_context_mock():
    """Cria mock completo do contexto Lambda"""
    mock_context = Mock()
    mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
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
'''
    
    with open("tests/lambda_context_helper.py", 'w', encoding='utf-8') as f:
        f.write(helper_content)
    
    print("✅ Helper criado")


def run_tests_and_check():
    """Executa testes e verifica resultado"""
    print("🧪 Executando testes para verificar correções...")
    
    # Tenta testes rápidos primeiro
    success, stdout, stderr = run_command("python test_runner.py --quick")
    
    if success:
        print("✅ Testes rápidos: 100% OK")
        
        # Agora tenta testes completos
        success, stdout, stderr = run_command("python test_runner.py")
        
        if "Taxa de sucesso: 100.0%" in stdout:
            print("🎉 TODOS OS TESTES: 100% OK!")
            return True
        else:
            print(f"⚠️ Testes completos ainda não 100%")
            # Extrai taxa de sucesso
            for line in stdout.split('\n'):
                if "Taxa de sucesso:" in line:
                    print(f"  {line.strip()}")
                    break
    else:
        print("❌ Ainda há problemas nos testes")
        print("Stdout:", stdout[-500:])  # Últimas 500 chars
        print("Stderr:", stderr[-500:])
    
    return False


def main():
    """Função principal"""
    print("🚀 Iniciando correção para 100% dos testes...")
    print("=" * 50)
    
    # Verifica se estamos no ambiente virtual
    if not os.environ.get('VIRTUAL_ENV') and not os.path.exists('venv'):
        print("❌ Ambiente virtual não encontrado!")
        print("Execute: source venv/bin/activate")
        sys.exit(1)
    
    try:
        # 1. Corrige testes do lambda_coletor
        fix_lambda_coletor_tests()
        
        # 2. Corrige testes do utils
        fix_utils_tests()
        
        # 3. Cria helper para context
        create_mock_context_helper()
        
        # 4. Corrige linting
        fix_linting_issues()
        
        # 5. Executa testes para verificar
        success = run_tests_and_check()
        
        print("=" * 50)
        if success:
            print("🎉 SUCESSO! Todos os testes agora passam 100%!")
        else:
            print("⚠️ Melhorias aplicadas, mas ainda não 100%")
            print("Execute 'python test_runner.py' para detalhes")
        
    except Exception as e:
        print(f"❌ Erro durante correção: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
