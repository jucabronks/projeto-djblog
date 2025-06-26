#!/usr/bin/env python3
"""
🌐 Monitor de Site Automatizado
Verifica se o site está funcional e gera relatórios automáticos
"""

import requests
import json
import boto3
from datetime import datetime, timezone
import os
import time


def check_website_health(url, timeout=10):
    """Verifica se o website está funcionando"""
    try:
        response = requests.get(url, timeout=timeout)
        return {
            'status': 'UP' if response.status_code == 200 else 'DOWN',
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'content_length': len(response.content),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            'status': 'DOWN',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


def check_dynamodb_health():
    """Verifica se DynamoDB está respondendo"""
    try:
        dynamodb = (
            boto3.resource('dynamodb', region_name= (
                os.environ.get('AWS_REGION', 'us-east-1'))
            )
        )
        table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'djblog-noticias')
        table = dynamodb.Table(table_name)

        # Faz um scan limitado para testar conectividade
        response = table.scan(Limit=1)

        return {
            'status': 'UP',
            'table_name': table_name,
            'items_count': response.get('Count', 0),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            'status': 'DOWN',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


def check_lambda_functions():
    """Verifica se as Lambda functions estão ativas"""
    try:
        lambda_client = (
            boto3.client('lambda', region_name= (
                os.environ.get('AWS_REGION', 'us-east-1'))
            )
        )

        functions = [
            'djblog-coletor',
            'djblog-publicar-wordpress',
            'djblog-limpeza',
            'djblog-health-check',
            'djblog-api-noticias'
        ]

        results = {}
        for func_name in functions:
            try:
                response = lambda_client.get_function(FunctionName=func_name)
                results[func_name] = {
                    'status': 'UP',
                    'state': response['Configuration']['State'],
                    'last_modified': response['Configuration']['LastModified']
                }
            except lambda_client.exceptions.ResourceNotFoundException:
                results[func_name] = {
                    'status': 'NOT_FOUND',
                    'error': 'Function not found'
                }
            except Exception as e:
                results[func_name] = {
                    'status': 'ERROR',
                    'error': str(e)
                }

        return results
    except Exception as e:
        return {'error': str(e)}


def generate_health_report():
    """Gera relatório completo de saúde do sistema"""
    print("🔍 Verificando saúde do sistema...")

    # URLs para testar
    urls_to_check = [
        'https://seu-usuario.github.io/projeto-djblog',  # GitHub Pages
        'https://projeto-djblog.vercel.app',  # Vercel (se configurado)
    ]

    report = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'websites': {},
        'dynamodb': check_dynamodb_health(),
        'lambda_functions': check_lambda_functions()
    }

    # Verifica websites
    for url in urls_to_check:
        print(f"🌐 Testando: {url}")
        report['websites'][url] = check_website_health(url)

    return report


def save_report_to_file(report, filename='health_report.json'):
    """Salva relatório em arquivo"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"📄 Relatório salvo em: {filename}")


def print_health_summary(report):
    """Exibe resumo do relatório"""
    print("\n" + "="*60)
    print("📊 RESUMO DE SAÚDE DO SISTEMA")
    print("="*60)

    # Status dos websites
    print("\n🌐 WEBSITES:")
    for url, status in report['websites'].items():
        emoji = "✅" if status['status'] == 'UP' else "❌"
        print(f"  {emoji} {url}: {status['status']}")
        if 'response_time' in status:
            print(f"      ⏱️ Tempo de resposta: {status['response_time']:.2f}s")

    # Status do DynamoDB
    print("\n📊 DYNAMODB:")
    db_status = report['dynamodb']
    emoji = "✅" if db_status['status'] == 'UP' else "❌"
    print(f"  {emoji} DynamoDB: {db_status['status']}")
    if 'table_name' in db_status:
        print(f"      📋 Tabela: {db_status['table_name']}")

    # Status das Lambda functions
    print("\n⚡ LAMBDA FUNCTIONS:")
    if 'error' not in report['lambda_functions']:
        for func_name, status in report['lambda_functions'].items():
            emoji = "✅" if status['status'] == 'UP' else "❌"
            print(f"  {emoji} {func_name}: {status['status']}")
    else:
        print(f"  ❌ Erro ao verificar functions: {report['lambda_functions']['error']}")

    # Status geral
    print("\n🎯 STATUS GERAL:")
    all_websites_up = (
        all(status['status'] == 'UP' for status in report['websites'].values())
    )
    db_up = report['dynamodb']['status'] == 'UP'

    if all_websites_up and db_up:
        print("  🎉 SISTEMA 100% OPERACIONAL!")
    else:
        print("  ⚠️ SISTEMA COM PROBLEMAS - Verifique detalhes acima")


def main():
    """Função principal"""
    print("🚀 MONITOR DE SISTEMA AUTOMATIZADO")
    print("="*50)

    try:
        # Gera relatório
        report = generate_health_report()

        # Salva em arquivo
        save_report_to_file(report)

        # Exibe resumo
        print_health_summary(report)

        # Determina código de saída
        all_up = (
            all(status['status'] = (
                = 'UP' for status in report['websites'].values()) and
            )
            report['dynamodb']['status'] == 'UP'
        )

        if all_up:
            print("\n✅ TODOS OS SISTEMAS FUNCIONAIS!")
            return 0
        else:
            print("\n❌ ALGUNS SISTEMAS COM PROBLEMAS!")
            return 1

    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
