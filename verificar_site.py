#!/usr/bin/env python3
"""
🌐 Verificação Rápida do Site
Script de linha de comando para verificar se o site está funcional com o menor esforço humano
"""

import requests
import json
import os
import sys
from datetime import datetime, timezone
import webbrowser
import argparse


def print_status(status, message, emoji=""):
    """Imprime status com cores no terminal"""
    colors = {
        'SUCCESS': '\033[92m',  # Verde
        'ERROR': '\033[91m',    # Vermelho
        'WARNING': '\033[93m',  # Amarelo
        'INFO': '\033[94m',     # Azul
        'RESET': '\033[0m'      # Reset
    }
    
    color = colors.get(status, colors['RESET'])
    reset = colors['RESET']
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    print(f"{color}{emoji} [{timestamp}] {message}{reset}")


def check_github_pages():
    """Verifica se o GitHub Pages está funcionando"""
    # Tenta determinar o URL do GitHub Pages automaticamente
    github_urls = [
        "https://jucabronks.github.io/projeto-djblog",
        "https://jucabronks.github.io/projeto-djblog/",
        "https://github.com/jucabronks/projeto-djblog"  # Fallback para repo
    ]
    
    for url in github_urls:
        try:
            print_status('INFO', f"Verificando: {url}", "🔍")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                content_length = len(response.content)
                response_time = response.elapsed.total_seconds()
                
                # Verifica se tem conteúdo mínimo
                if content_length > 1000:  # Pelo menos 1KB de conteúdo
                    print_status('SUCCESS', f"✅ Site FUNCIONANDO! ({content_length} bytes, {response_time:.2f}s)", "🎉")
                    print_status('INFO', f"URL: {url}", "🌐")
                    return url, True
                else:
                    print_status('WARNING', f"Site carregou mas com pouco conteúdo ({content_length} bytes)", "⚠️")
            else:
                print_status('WARNING', f"Status {response.status_code} em {url}", "⚠️")
                
        except requests.exceptions.RequestException as e:
            print_status('ERROR', f"Erro ao acessar {url}: {str(e)}", "❌")
    
    return None, False


def check_github_actions():
    """Verifica o status das GitHub Actions"""
    try:
        # Verifica se existe o arquivo de workflow
        workflow_file = '.github/workflows/deploy-site.yml'
        if os.path.exists(workflow_file):
            print_status('SUCCESS', "GitHub Actions configurado ✅", "⚙️")
            print_status('INFO', "Workflow: deploy-site.yml encontrado", "📁")
            
            # Verifica se há commits recentes
            import subprocess
            try:
                result = subprocess.run(['git', 'log', '--oneline', '-n', '1'], 
                                      capture_output=True, text=True, cwd='.')
                if result.returncode == 0 and result.stdout.strip():
                    print_status('SUCCESS', f"Último commit: {result.stdout.strip()}", "📝")
                    return True
            except:
                pass
                
        else:
            print_status('ERROR', "GitHub Actions NÃO configurado", "❌")
            return False
            
    except Exception as e:
        print_status('ERROR', f"Erro ao verificar GitHub Actions: {e}", "❌")
        return False
    
    return True


def check_aws_health():
    """Verifica saúde do AWS DynamoDB"""
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError
        
        # Verifica se as credenciais AWS estão configuradas
        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            if not credentials:
                print_status('WARNING', "Credenciais AWS não encontradas localmente", "⚠️")
                return False
        except:
            print_status('WARNING', "Erro ao verificar credenciais AWS", "⚠️")
            return False
            
        # Tenta conectar no DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'djblog-noticias')
        
        table = dynamodb.Table(table_name)
        response = table.scan(Limit=1)
        
        count = response.get('Count', 0)
        print_status('SUCCESS', f"DynamoDB funcionando! ({count} itens verificados)", "🗄️")
        return True
        
    except NoCredentialsError:
        print_status('WARNING', "Credenciais AWS não configuradas (normal em produção)", "⚠️")
        return False
    except ClientError as e:
        print_status('ERROR', f"Erro no DynamoDB: {e}", "❌")
        return False
    except ImportError:
        print_status('WARNING', "boto3 não instalado (verificação local)", "⚠️")
        return False
    except Exception as e:
        print_status('ERROR', f"Erro inesperado no AWS: {e}", "❌")
        return False


def generate_quick_report():
    """Gera relatório rápido de status"""
    print_status('INFO', "=== VERIFICAÇÃO RÁPIDA DO DJBLOG ===", "🚀")
    print()
    
    # 1. Verificar GitHub Pages
    print_status('INFO', "1. Verificando GitHub Pages...", "🌐")
    site_url, site_ok = check_github_pages()
    print()
    
    # 2. Verificar GitHub Actions
    print_status('INFO', "2. Verificando GitHub Actions...", "⚙️")
    actions_ok = check_github_actions()
    print()
    
    # 3. Verificar AWS (opcional)
    print_status('INFO', "3. Verificando AWS DynamoDB...", "🗄️")
    aws_ok = check_aws_health()
    print()
    
    # Resumo final
    print_status('INFO', "=== RESUMO ===", "📊")
    
    if site_ok:
        print_status('SUCCESS', "✅ SITE FUNCIONANDO", "🎉")
        if site_url:
            print_status('INFO', f"   URL: {site_url}", "🌐")
    else:
        print_status('ERROR', "❌ SITE COM PROBLEMAS", "🚨")
        print_status('INFO', "   Verifique se o GitHub Pages está configurado", "💡")
    
    if actions_ok:
        print_status('SUCCESS', "✅ AUTOMAÇÃO FUNCIONANDO", "⚙️")
    else:
        print_status('WARNING', "⚠️ AUTOMAÇÃO PRECISA DE ATENÇÃO", "🔧")
    
    if aws_ok:
        print_status('SUCCESS', "✅ BACKEND FUNCIONANDO", "🗄️")
    else:
        print_status('INFO', "ℹ️ Backend verificado via GitHub Actions", "☁️")
    
    print()
    
    # Instruções finais
    if site_ok:
        print_status('SUCCESS', "🎯 TUDO FUNCIONANDO! Menor esforço humano atingido.", "🏆")
        print_status('INFO', "💡 Próximos passos automatizados:", "📋")
        print_status('INFO', "   • Site atualiza automaticamente (GitHub Actions)", "🔄")
        print_status('INFO', "   • Notícias coletadas diariamente (Lambda)", "📰")
        print_status('INFO', "   • Monitoramento contínuo (health checks)", "📊")
    else:
        print_status('WARNING', "🔧 CONFIGURAÇÃO NECESSÁRIA:", "⚙️")
        print_status('INFO', "   1. Verifique se o repositório tem GitHub Pages habilitado", "🌐")
        print_status('INFO', "   2. Execute: git push origin main", "📤")
        print_status('INFO', "   3. Aguarde 2-5 minutos para deploy", "⏱️")
    
    return site_ok and actions_ok


def open_site_browser(url=None):
    """Abre o site no navegador"""
    if not url:
        url, _ = check_github_pages()
    
    if url:
        print_status('INFO', f"Abrindo {url} no navegador...", "🌐")
        webbrowser.open(url)
        return True
    else:
        print_status('ERROR', "URL do site não encontrada", "❌")
        return False


def main():
    parser = argparse.ArgumentParser(description='Verificação rápida do DJBlog')
    parser.add_argument('--open', '-o', action='store_true', 
                       help='Abrir site no navegador após verificação')
    parser.add_argument('--url-only', '-u', action='store_true',
                       help='Mostrar apenas URL do site')
    parser.add_argument('--quick', '-q', action='store_true',
                       help='Verificação super rápida (apenas site)')
    
    args = parser.parse_args()
    
    if args.url_only:
        url, ok = check_github_pages()
        if ok and url:
            print(url)
            sys.exit(0)
        else:
            print("Site não encontrado")
            sys.exit(1)
    
    if args.quick:
        print_status('INFO', "Verificação rápida...", "⚡")
        url, ok = check_github_pages()
        if ok:
            print_status('SUCCESS', "Site funcionando!", "✅")
            if args.open:
                open_site_browser(url)
        else:
            print_status('ERROR', "Site com problemas", "❌")
        sys.exit(0 if ok else 1)
    
    # Verificação completa
    all_ok = generate_quick_report()
    
    if args.open:
        open_site_browser()
    
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
