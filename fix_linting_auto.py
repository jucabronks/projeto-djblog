#!/usr/bin/env python3
"""
Script automático para corrigir problemas de linting detectados pelo flake8
"""

import os
import re
import subprocess
from pathlib import Path


def run_command(cmd):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def fix_line_length(content, max_length=79):
    """Corrige linhas muito longas"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) <= max_length:
            fixed_lines.append(line)
            continue
            
        # Se for uma string longa, tenta quebrar
        if '"' in line or "'" in line:
            # Tenta quebrar strings longas
            if '=' in line and ('"' in line or "'" in line):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    indent = len(parts[0]) - len(parts[0].lstrip())
                    fixed_lines.append(parts[0] + '= (')
                    fixed_lines.append(' ' * (indent + 4) + parts[1].strip())
                    fixed_lines.append(' ' * indent + ')')
                    continue
        
        # Se for uma linha de comentário longa
        if line.strip().startswith('#'):
            indent = len(line) - len(line.lstrip())
            words = line.strip().split()
            current_line = ' ' * indent + words[0]
            
            for word in words[1:]:
                if len(current_line + ' ' + word) <= max_length:
                    current_line += ' ' + word
                else:
                    fixed_lines.append(current_line)
                    current_line = ' ' * indent + '# ' + word
            
            if current_line.strip():
                fixed_lines.append(current_line)
            continue
        
        # Para outras linhas, mantém como está (pode precisar de correção manual)
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_whitespace_issues(content):
    """Corrige problemas de espaços em branco"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Remove trailing whitespace (W291)
        line = line.rstrip()
        
        # Corrige blank line contains whitespace (W293)
        if line.strip() == '':
            line = ''
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_imports(content):
    """Corrige imports não utilizados"""
    lines = content.split('\n')
    fixed_lines = []
    
    # Lista de imports a remover se não usados
    unused_imports = [
        "import os",
        "import json", 
        "import sys",
        "import time",
        "import shutil",
        "from pathlib import Path",
        "from datetime import timezone",
        "import requests"
    ]
    
    for line in lines:
        # Se for um import não usado, pula (simplificado)
        skip_line = False
        for unused in unused_imports:
            if line.strip() == unused:
                # Verifica se está sendo usado no código
                import_name = unused.split()[-1]
                if import_name not in content:
                    skip_line = True
                    break
        
        if not skip_line:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_fstring_issues(content):
    """Corrige f-strings sem placeholders"""
    # F541: f-string is missing placeholders
    content = re.sub(r'f"([^{]*)"', r'"\1"', content)
    content = re.sub(r"f'([^{]*)'", r"'\1'", content)
    return content


def fix_bare_except(content):
    """Corrige bare except (E722)"""
    # Substitui 'except:' por 'except Exception:'
    content = re.sub(r'except\s*:', 'except Exception:', content)
    return content


def fix_syntax_errors(content):
    """Corrige erros de sintaxe básicos"""
    # Fix unterminated string literals
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Verifica se há string não terminada
        if line.count('"') % 2 != 0 and not line.strip().startswith('#'):
            # Adiciona aspas no final se necessário
            line = line + '"'
        
        if line.count("'") % 2 != 0 and not line.strip().startswith('#'):
            # Adiciona aspas simples no final se necessário  
            line = line + "'"
            
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_file(file_path):
    """Corrige um arquivo específico"""
    print(f"🔧 Corrigindo: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Aplica correções
        content = fix_whitespace_issues(content)
        content = fix_fstring_issues(content)
        content = fix_bare_except(content)
        content = fix_syntax_errors(content)
        content = fix_line_length(content)
        
        # Salva arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {file_path} corrigido!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir {file_path}: {e}")
        return False


def main():
    """Função principal"""
    print("🚀 Iniciando correção automática de linting...")
    
    # Lista de arquivos Python para corrigir
    python_files = [
        "check_mongodb_references.py",
        "config.py",
        "configurar_blog.py", 
        "demo_local.py",
        "deploy_oneclick.py",
        "fix_linting.py",
        "fix_tests_100_percent.py",
        "generate_static_site.py",
        "improve_tests.py",
        "lambda_coletor.py",
        "lambda_health_check.py",
        "lambda_limpeza.py", 
        "lambda_publicar_wordpress.py",
        "monitor_sistema.py",
        "relatorio_remocao_mongodb.py",
        "setup.py",
        "setup_github_pages.py",
        "sistema_local_completo.py",
        "summarize_ai.py",
        "test_runner.py",
        "utils.py",
        "verificar_site.py"
    ]
    
    # Corrige arquivos de teste
    test_files = [
        "tests/lambda_context_helper.py",
        "tests/test_config.py", 
        "tests/test_lambda_coletor.py",
        "tests/test_utils.py"
    ]
    
    all_files = python_files + test_files
    
    fixed_count = 0
    error_count = 0
    
    for file_path in all_files:
        if os.path.exists(file_path):
            if fix_file(file_path):
                fixed_count += 1
            else:
                error_count += 1
        else:
            print(f"⚠️  Arquivo não encontrado: {file_path}")
    
    print(f"\n📊 Resumo:")
    print(f"✅ Arquivos corrigidos: {fixed_count}")
    print(f"❌ Arquivos com erro: {error_count}")
    
    # Executa flake8 novamente para ver melhorias
    print("\n🔍 Executando flake8 novamente...")
    success, stdout, stderr = run_command("flake8 --max-line-length=88 .")
    
    if success:
        print("🎉 Nenhum problema de linting encontrado!")
    else:
        print("⚠️  Ainda há alguns problemas:")
        print(stdout)
    
    print("\n💡 Dica: Alguns problemas podem precisar de correção manual.")


if __name__ == "__main__":
    main()
