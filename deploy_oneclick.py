#!/usr/bin/env python3
"""
🚀 Deploy One-Click do DJBlog
Script que configura e deploya tudo automaticamente com o menor esforço humano
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime


def print_step(step, message, emoji=""):
    """Imprime passos do deploy com formatação"""
    print(f"\n{emoji} {step}. {message}")
    print("=" * 50)


def run_command(command, description="", show_output=True):
    """Executa comando com tratamento de erro"""
    if description:
        print(f"🔧 {description}")
    
    try:
        if show_output:
            result = subprocess.run(command, shell=True, check=True, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True, 
                                   text=True, capture_output=True)
        return True, result
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"Saída: {e.stdout}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Erro: {e.stderr}")
        return False, e


def check_git_status():
    """Verifica status do git"""
    try:
        # Verifica se está em um repositório git
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, "Não é um repositório Git"
    except:
        return False, "Git não instalado"


def configure_github_pages():
    """Configura GitHub Pages automaticamente"""
    print("🌐 Configurando GitHub Pages...")
    
    # Verifica se já está configurado
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            repo_url = result.stdout.strip()
            print(f"📍 Repositório: {repo_url}")
            
            # Extrai owner/repo do URL
            if 'github.com' in repo_url:
                if repo_url.endswith('.git'):
                    repo_url = repo_url[:-4]
                parts = repo_url.split('/')
                if len(parts) >= 2:
                    owner = parts[-2]
                    repo = parts[-1]
                    
                    site_url = f"https://{owner}.github.io/{repo}"
                    print(f"🌐 URL do site será: {site_url}")
                    return site_url
    except:
        pass
    
    print("⚠️ Configure manualmente no GitHub: Settings > Pages > Source: GitHub Actions")
    return None


def deploy_complete():
    """Deploy completo automatizado"""
    print("🚀 INICIANDO DEPLOY AUTOMATIZADO DO DJBLOG")
    print("=" * 60)
    
    # Passo 1: Verificar ambiente
    print_step(1, "Verificando ambiente", "🔍")
    
    git_ok, git_status = check_git_status()
    if not git_ok:
        print(f"❌ Problema com Git: {git_status}")
        return False
    
    print("✅ Git configurado")
    
    # Passo 2: Instalar dependências mínimas
    print_step(2, "Instalando dependências", "📦")
    
    success, _ = run_command("pip install requests boto3", "Instalando requests e boto3")
    if not success:
        print("⚠️ Erro ao instalar dependências, continuando...")
    
    # Passo 3: Verificar arquivos essenciais
    print_step(3, "Verificando arquivos essenciais", "📁")
    
    arquivos_essenciais = [
        '.github/workflows/deploy-site.yml',
        'generate_static_site.py',
        'monitor_sistema.py'
    ]
    
    for arquivo in arquivos_essenciais:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} não encontrado")
            return False
    
    # Passo 4: Commit e push
    print_step(4, "Fazendo commit e push", "📤")
    
    # Adiciona todos os arquivos
    run_command("git add .", "Adicionando arquivos")
    
    # Faz commit
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    commit_msg = f"🚀 Deploy automatizado {timestamp}"
    
    success, _ = run_command(f'git commit -m "{commit_msg}"', "Fazendo commit", show_output=False)
    if not success:
        print("ℹ️ Nenhuma mudança para commit (normal)")
    
    # Push para main
    success, _ = run_command("git push origin main", "Enviando para GitHub")
    if not success:
        print("❌ Erro no push - verifique suas credenciais Git")
        return False
    
    # Passo 5: Configurar GitHub Pages
    print_step(5, "Configurando GitHub Pages", "🌐")
    site_url = configure_github_pages()
    
    # Passo 6: Aguardar deploy
    print_step(6, "Aguardando deploy do GitHub Actions", "⏱️")
    
    print("🔄 GitHub Actions está processando...")
    print("   Tempo estimado: 2-5 minutos")
    print("   Aguardando deploy...")
    
    # Aguarda um pouco para o GitHub processar
    for i in range(30, 0, -1):
        print(f"\r⏳ Aguardando {i}s... ", end='', flush=True)
        time.sleep(1)
    print("\n")
    
    # Passo 7: Verificar resultado
    print_step(7, "Verificando resultado", "🎯")
    
    # Executa verificação do site
    try:
        exec(open('verificar_site.py').read())
    except:
        print("⚠️ Não foi possível executar verificação automática")
    
    # Resultado final
    print("\n🎉 DEPLOY CONCLUÍDO!")
    print("=" * 40)
    
    if site_url:
        print(f"🌐 Site: {site_url}")
        print("📊 Status: Verifique em alguns minutos")
    
    print("\n💡 PRÓXIMOS PASSOS AUTOMÁTICOS:")
    print("✅ GitHub Actions irá:")
    print("   • Gerar o site estático")
    print("   • Buscar notícias do DynamoDB") 
    print("   • Publicar no GitHub Pages")
    print("   • Monitorar automaticamente")
    
    print("\n🏆 MENOR ESFORÇO HUMANO ATINGIDO!")
    print("   O sistema agora funciona 100% automaticamente")
    
    return True


def quick_check():
    """Verificação rápida sem deploy"""
    print("⚡ VERIFICAÇÃO RÁPIDA")
    print("=" * 30)
    
    try:
        exec(open('verificar_site.py').read())
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        
        # Fallback: verificação manual básica
        print("\n🔍 Verificação manual:")
        git_ok, _ = check_git_status()
        if git_ok:
            print("✅ Git OK")
        else:
            print("❌ Git com problemas")
        
        if os.path.exists('.github/workflows/deploy-site.yml'):
            print("✅ GitHub Actions configurado")
        else:
            print("❌ GitHub Actions não configurado")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--check' or sys.argv[1] == '-c':
            quick_check()
            return
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("🚀 Deploy One-Click do DJBlog")
            print("\nUso:")
            print("  python deploy_oneclick.py         # Deploy completo")
            print("  python deploy_oneclick.py --check # Verificação rápida")
            print("  python deploy_oneclick.py --help  # Esta ajuda")
            return
    
    # Deploy completo
    success = deploy_complete()
    
    if success:
        print("\n🎯 Para verificar o site a qualquer momento:")
        print("   python verificar_site.py")
        print("   python verificar_site.py --open  # Abre no navegador")
        print("   python deploy_oneclick.py --check  # Verificação rápida")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
