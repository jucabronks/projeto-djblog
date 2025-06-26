#!/usr/bin/env python3
"""
Script para corrigir automaticamente problemas de linting
"""
import subprocess
import sys
import os

def run_autopep8():
    """Executa autopep8 para corrigir problemas de formatação"""
    print("🔧 Executando autopep8 para corrigir formatação...")
    
    # Usar o ambiente virtual se disponível
    if os.path.exists("venv/Scripts/python.exe"):
        python_cmd = "venv/Scripts/python.exe"
        pip_cmd = "venv/Scripts/pip.exe"
    elif os.path.exists("venv/bin/python"):
        python_cmd = "venv/bin/python"
        pip_cmd = "venv/bin/pip"
    else:
        python_cmd = "python"
        pip_cmd = "pip"
    
    # Instalar autopep8 se necessário
    try:
        subprocess.run([pip_cmd, "install", "autopep8"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️ Erro ao instalar autopep8")
        return False
    
    # Arquivos para corrigir (excluindo os antigos e de teste)
    files_to_fix = [
        "config.py",
        "utils.py",
        "lambda_coletor.py",
        "lambda_publicar_wordpress.py",
        "lambda_limpeza.py",
        "lambda_health_check.py",
        "lambda_api_noticias.py",
        "test_runner.py",
        "summarize_ai.py",
        "setup.py",
        "tests/conftest.py",
        "tests/test_config.py",
        "tests/test_lambda_coletor.py",
        "tests/test_utils.py",
        "tests/test_summarize_ai.py"
    ]
    
    # Corrigir cada arquivo
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"  Corrigindo {file_path}...")
            try:
                subprocess.run([
                    python_cmd, "-m", "autopep8",
                    "--in-place",
                    "--aggressive",
                    "--aggressive",
                    "--max-line-length=120",
                    file_path
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"    ⚠️ Erro ao corrigir {file_path}: {e}")
    
    print("✅ Correção de formatação concluída!")
    return True

def remove_unused_imports():
    """Remove imports não utilizados usando autoflake"""
    print("🔧 Removendo imports não utilizados...")
    
    # Usar o ambiente virtual se disponível
    if os.path.exists("venv/Scripts/python.exe"):
        python_cmd = "venv/Scripts/python.exe"
        pip_cmd = "venv/Scripts/pip.exe"
    elif os.path.exists("venv/bin/python"):
        python_cmd = "venv/bin/python"
        pip_cmd = "venv/bin/pip"
    else:
        python_cmd = "python"
        pip_cmd = "pip"
    
    # Instalar autoflake se necessário
    try:
        subprocess.run([pip_cmd, "install", "autoflake"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️ Erro ao instalar autoflake")
        return False
    
    # Corrigir imports em arquivos principais
    files_to_fix = [
        "config.py",
        "utils.py", 
        "lambda_coletor.py",
        "lambda_publicar_wordpress.py",
        "lambda_limpeza.py",
        "lambda_health_check.py",
        "lambda_api_noticias.py",
        "test_runner.py",
        "summarize_ai.py",
        "tests/conftest.py",
        "tests/test_config.py",
        "tests/test_lambda_coletor.py",
        "tests/test_utils.py",
        "tests/test_summarize_ai.py"
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"  Removendo imports não utilizados em {file_path}...")
            try:
                subprocess.run([
                    python_cmd, "-m", "autoflake",
                    "--in-place",
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    file_path
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"    ⚠️ Erro ao processar {file_path}: {e}")
    
    print("✅ Remoção de imports concluída!")
    return True

def main():
    """Função principal"""
    print("🚀 Iniciando correção automática de linting...")
    
    # Remover imports não utilizados primeiro
    if not remove_unused_imports():
        print("❌ Falha ao remover imports não utilizados")
        return 1
    
    # Corrigir formatação
    if not run_autopep8():
        print("❌ Falha ao corrigir formatação")
        return 1
    
    print("🎉 Correção de linting concluída com sucesso!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
