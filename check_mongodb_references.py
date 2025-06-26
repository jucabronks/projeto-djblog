#!/usr/bin/env python3
"""
Script para verificar se ainda existem referências ao MongoDB no projeto
"""

import os
import re
import sys
from pathlib import Path


def check_mongodb_references():
    """Verifica referências ao MongoDB no projeto"""
    
    # Padrões a buscar
    patterns = [
        r'mongodb',
        r'pymongo',
        r'mongo_uri',
        r'MONGO_URI',
        r'MongoClient',
        r'seed_mongodb',
        r'conectar_mongodb'
    ]
    
    # Arquivos a ignorar
    ignore_files = {
        'check_mongodb_references.py',
        '.git',
        '__pycache__',
        'venv',
        '.pytest_cache',
        'node_modules',
        '.terraform',
        'terraform.tfstate',
        'terraform.tfstate.backup'
    }
    
    # Extensões a verificar
    check_extensions = {'.py', '.md', '.tf', '.sh', '.ps1', '.yml', '.yaml', '.json'}
    
    project_root = Path('.')
    found_references = []
    
    for file_path in project_root.rglob('*'):
        # Pular diretórios e arquivos ignorados
        if any(ignore in str(file_path) for ignore in ignore_files):
            continue
        
        # Pular links simbólicos (problemas no Windows)
        if file_path.is_symlink():
            continue
            
        # Verificar apenas arquivos (não diretórios)
        if not file_path.is_file():
            continue
            
        # Verificar apenas arquivos com extensões relevantes
        if file_path.suffix not in check_extensions:
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                
                for pattern in patterns:
                    if re.search(pattern.lower(), content):
                        found_references.append({
                            'file': str(file_path),
                            'pattern': pattern
                        })
                        break
                        
        except Exception as e:
            print(f"Erro ao ler {file_path}: {e}")
            continue
    
    return found_references


def main():
    """Função principal"""
    print("🔍 Verificando referências ao MongoDB no projeto...")
    print("=" * 60)
    
    references = check_mongodb_references()
    
    if not references:
        print("✅ SUCESSO: Nenhuma referência ao MongoDB encontrada!")
        print("🎉 O projeto está 100% migrado para DynamoDB!")
        return 0
    else:
        print(f"⚠️  Encontradas {len(references)} referências ao MongoDB:")
        print()
        
        for ref in references:
            print(f"  📄 {ref['file']}")
            print(f"     → Padrão: {ref['pattern']}")
            print()
        
        print("❌ Ainda existem referências ao MongoDB que precisam ser removidas.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
