#!/usr/bin/env python3
"""
Script para corrigir docstrings malformadas
"""

import os
import re


def fix_docstrings_in_file(filepath):
    """Corrige docstrings malformadas em um arquivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Corrigir """ para """
        fixed_content = re.sub(r'"""', '"""', content)
        
        if content != fixed_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Corrigido: {filepath}")
            return True
        else:
            print(f"✅ OK: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Erro em {filepath}: {e}")
        return False


def main():
    """Função principal"""
    print("🔧 Corrigindo docstrings malformadas...")
    
    total_fixed = 0
    
    # Corrigir arquivos na raiz
    for file in os.listdir('.'):
        if file.endswith('.py'):
            if fix_docstrings_in_file(file):
                total_fixed += 1
    
    # Corrigir arquivos na pasta tests
    if os.path.exists('tests'):
        for file in os.listdir('tests'):
            if file.endswith('.py'):
                filepath = os.path.join('tests', file)
                if fix_docstrings_in_file(filepath):
                    total_fixed += 1
    
    print(f"\n🎉 Corrigidos {total_fixed} arquivos!")


if __name__ == "__main__":
    main()
