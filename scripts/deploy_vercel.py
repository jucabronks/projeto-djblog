#!/usr/bin/env python3
"""
Script para deploy automatizado no Vercel
Opção mais simples para produção
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime


class VercelDeploy:
    """Deploy simplificado no Vercel"""
    
    def __init__(self, domain_name: str = None):
        self.domain_name = domain_name
        self.project_name = "djblog-noticias"
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        print(f"{icons.get(level, 'ℹ️')} [{timestamp}] {message}")
        
    def check_vercel_cli(self) -> bool:
        """Verificar se Vercel CLI está instalado"""
        try:
            result = subprocess.run(['vercel', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"Vercel CLI: {result.stdout.strip()}", "SUCCESS")
                return True
            else:
                return False
        except FileNotFoundError:
            return False
            
    def install_vercel_cli(self) -> bool:
        """Instalar Vercel CLI"""
        self.log("Instalando Vercel CLI...")
        
        try:
            subprocess.run(['npm', 'install', '-g', 'vercel'], check=True)
            self.log("Vercel CLI instalado com sucesso!", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Erro ao instalar Vercel CLI: {e}", "ERROR")
            return False
        except FileNotFoundError:
            self.log("Node.js/npm não encontrado! Instale primeiro:", "ERROR")
            self.log("https://nodejs.org/", "ERROR")
            return False
            
    def create_vercel_config(self):
        """Criar arquivo de configuração do Vercel"""
        self.log("Criando configuração do Vercel...")
        
        config = {
            "name": self.project_name,
            "version": 2,
            "builds": [
                {
                    "src": "generate_static_site.py",
                    "use": "@vercel/python"
                }
            ],
            "routes": [
                {
                    "src": "/",
                    "dest": "/generate_static_site.py"
                },
                {
                    "src": "/(.*)",
                    "dest": "/generate_static_site.py"
                }
            ],
            "env": {
                "PYTHON_VERSION": "3.11"
            }
        }
        
        with open('vercel.json', 'w') as f:
            json.dump(config, f, indent=2)
            
        self.log("Configuração criada: vercel.json", "SUCCESS")
        
    def create_requirements_vercel(self):
        """Criar requirements.txt específico para Vercel"""
        self.log("Criando requirements para Vercel...")
        
        # Requirements mínimos para Vercel
        vercel_requirements = [
            "boto3>=1.34.0",
            "requests>=2.31.0",
            "python-dateutil>=2.8.2"
        ]
        
        with open('requirements-vercel.txt', 'w') as f:
            f.write('\n'.join(vercel_requirements))
            
        self.log("Requirements criado: requirements-vercel.txt", "SUCCESS")
        
    def create_api_handler(self):
        """Criar handler para API do Vercel"""
        self.log("Criando API handler...")
        
        # Criar diretório api se não existir
        os.makedirs('api', exist_ok=True)
        
        handler_code = '''#!/usr/bin/env python3
"""
Handler do Vercel para servir o site estático
"""

import os
import sys
from http.server import BaseHTTPRequestHandler
import json

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Importar gerador do site
try:
    from generate_static_site import gerar_site_estatico
except ImportError:
    def gerar_site_estatico():
        return "<html><body><h1>DJBlog - Site em manutenção</h1></body></html>"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Servir site estático"""
        try:
            # Gerar HTML do site
            html_content = gerar_site_estatico()
            
            # Headers
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'public, max-age=300')
            self.end_headers()
            
            # Enviar conteúdo
            self.wfile.write(html_content.encode('utf-8'))
            
        except Exception as e:
            # Error fallback
            self.send_response(500)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            
            error_html = f"""
            <html>
            <head><title>DJBlog - Erro</title></head>
            <body>
                <h1>DJBlog - Temporariamente Indisponível</h1>
                <p>Erro: {str(e)}</p>
                <p>Tente novamente em alguns minutos.</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode('utf-8'))
'''
        
        with open('api/index.py', 'w', encoding='utf-8') as f:
            f.write(handler_code)
            
        self.log("API handler criado: api/index.py", "SUCCESS")
        
    def login_vercel(self) -> bool:
        """Login no Vercel"""
        self.log("Fazendo login no Vercel...")
        
        try:
            # Verificar se já está logado
            result = subprocess.run(['vercel', 'whoami'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log(f"Já logado como: {result.stdout.strip()}", "SUCCESS")
                return True
            else:
                # Fazer login
                self.log("Abrindo navegador para login...")
                subprocess.run(['vercel', 'login'], check=True)
                return True
                
        except subprocess.CalledProcessError as e:
            self.log(f"Erro no login: {e}", "ERROR")
            return False
            
    def deploy_to_vercel(self) -> str:
        """Deploy para Vercel"""
        self.log("Fazendo deploy para Vercel...")
        
        try:
            # Deploy para produção
            result = subprocess.run(['vercel', '--prod', '--yes'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Extrair URL do deploy
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'https://' in line and 'vercel.app' in line:
                        vercel_url = line.strip()
                        self.log(f"Deploy concluído: {vercel_url}", "SUCCESS")
                        return vercel_url
                        
                self.log("Deploy realizado, mas URL não encontrada", "WARNING")
                return "https://djblog-noticias.vercel.app"
                
            else:
                self.log(f"Erro no deploy: {result.stderr}", "ERROR")
                return None
                
        except subprocess.TimeoutExpired:
            self.log("Deploy demorou mais que 5 minutos - verifique manualmente", "WARNING")
            return None
        except Exception as e:
            self.log(f"Erro no deploy: {e}", "ERROR")
            return None
            
    def setup_custom_domain(self, vercel_url: str) -> bool:
        """Configurar domínio customizado"""
        if not self.domain_name:
            return True
            
        self.log(f"Configurando domínio: {self.domain_name}")
        
        try:
            # Adicionar domínio
            subprocess.run(['vercel', 'domains', 'add', self.domain_name], 
                         check=True)
            
            # Fazer alias
            subprocess.run(['vercel', 'alias', 'set', vercel_url, self.domain_name], 
                         check=True)
            
            self.log(f"Domínio configurado: https://{self.domain_name}", "SUCCESS")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Erro ao configurar domínio: {e}", "ERROR")
            self.log("Configure manualmente no painel Vercel", "WARNING")
            return False
            
    def deploy_complete(self) -> bool:
        """Deploy completo no Vercel"""
        self.log(f"🚀 Iniciando deploy no Vercel...")
        
        # 1. Verificar/instalar CLI
        if not self.check_vercel_cli():
            if not self.install_vercel_cli():
                return False
                
        # 2. Configurar projeto
        self.create_vercel_config()
        self.create_requirements_vercel()
        self.create_api_handler()
        
        # 3. Login
        if not self.login_vercel():
            return False
            
        # 4. Deploy
        vercel_url = self.deploy_to_vercel()
        if not vercel_url:
            return False
            
        # 5. Domínio customizado (opcional)
        self.setup_custom_domain(vercel_url)
        
        # Relatório final
        self.log("🎉 Deploy no Vercel concluído!", "SUCCESS")
        self.log(f"📊 Relatório do Deploy:")
        self.log(f"   URL Vercel: {vercel_url}")
        if self.domain_name:
            self.log(f"   Domínio: https://{self.domain_name}")
        self.log(f"   Configuração: vercel.json")
        self.log(f"   API: api/index.py")
        
        return True


def main():
    """Função principal"""
    print("🚀 Deploy Simplificado Vercel - DJBlog")
    print("=" * 50)
    
    # Solicitar informações
    domain_name = input("Domínio customizado (opcional): ").strip()
    if not domain_name:
        domain_name = None
        
    print("\\n📋 Próximos passos:")
    print("1. Instalar Node.js (se não tiver): https://nodejs.org/")
    print("2. O script instalará Vercel CLI automaticamente")
    print("3. Login no Vercel será solicitado")
    print("4. Deploy automático para produção")
    
    if domain_name:
        print(f"5. Configurar DNS para: {domain_name}")
        
    confirm = input("\\nContinuar? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Deploy cancelado.")
        return
        
    # Executar deploy
    deployer = VercelDeploy(domain_name)
    success = deployer.deploy_complete()
    
    if success:
        print("\\n🎉 Site disponível em produção!")
        if domain_name:
            print(f"🌐 URL: https://{domain_name}")
        print("📊 Painel: https://vercel.com/dashboard")
    else:
        print("\\n❌ Deploy falhou. Verifique os erros acima.")
        

if __name__ == "__main__":
    main()
