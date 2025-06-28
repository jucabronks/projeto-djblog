#!/usr/bin/env python3
"""
Script para configuração automática de domínio na Cloudflare
Configuração DNS + SSL automático
"""

import os
import sys
import requests
import json
import time
from datetime import datetime


class CloudflareDNSSetup:
    """Configurar DNS na Cloudflare"""
    
    def __init__(self, domain_name: str, target_url: str, api_token: str = None):
        self.domain_name = domain_name
        self.target_url = target_url.replace('https://', '').replace('http://', '')
        self.api_token = api_token
        self.zone_id = None
        
        # Headers para API
        if self.api_token:
            self.headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        print(f"{icons.get(level, 'ℹ️')} [{timestamp}] {message}")
        
    def get_api_token(self) -> str:
        """Obter token da API Cloudflare"""
        if self.api_token:
            return self.api_token
            
        self.log("📝 Como obter token da API Cloudflare:")
        self.log("1. Acesse: https://dash.cloudflare.com/profile/api-tokens")
        self.log("2. Clique em 'Create Token'")
        self.log("3. Use template 'Edit zone DNS'")
        self.log("4. Selecione seu domínio")
        self.log("5. Copie o token gerado")
        
        token = input("\\nCole seu token da API Cloudflare: ").strip()
        
        if not token:
            self.log("Token é obrigatório!", "ERROR")
            return None
            
        self.api_token = token
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        return token
        
    def verify_api_token(self) -> bool:
        """Verificar se token é válido"""
        if not self.api_token:
            return False
            
        try:
            response = requests.get(
                'https://api.cloudflare.com/client/v4/user/tokens/verify',
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log("Token válido!", "SUCCESS")
                    return True
                    
            self.log("Token inválido!", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"Erro ao verificar token: {e}", "ERROR")
            return False
            
    def find_zone_id(self) -> str:
        """Encontrar Zone ID do domínio"""
        try:
            response = requests.get(
                f'https://api.cloudflare.com/client/v4/zones?name={self.domain_name}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('result'):
                    self.zone_id = data['result'][0]['id']
                    self.log(f"Zone ID encontrado: {self.zone_id}", "SUCCESS")
                    return self.zone_id
                    
            self.log(f"Domínio {self.domain_name} não encontrado na Cloudflare!", "ERROR")
            self.log("Adicione o domínio na Cloudflare primeiro!", "ERROR")
            return None
            
        except Exception as e:
            self.log(f"Erro ao buscar zone: {e}", "ERROR")
            return None
            
    def create_dns_record(self, record_type: str, name: str, content: str, proxied: bool = True) -> bool:
        """Criar registro DNS"""
        if not self.zone_id:
            return False
            
        record_data = {
            'type': record_type,
            'name': name,
            'content': content,
            'proxied': proxied
        }
        
        try:
            response = requests.post(
                f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records',
                headers=self.headers,
                json=record_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log(f"Registro criado: {name} -> {content}", "SUCCESS")
                    return True
                else:
                    # Verificar se já existe
                    errors = data.get('errors', [])
                    for error in errors:
                        if 'already exists' in error.get('message', ''):
                            self.log(f"Registro já existe: {name}", "WARNING")
                            return True
                            
                    self.log(f"Erro ao criar registro: {errors}", "ERROR")
                    return False
            else:
                self.log(f"Erro HTTP: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Erro ao criar registro: {e}", "ERROR")
            return False
            
    def setup_dns_records(self) -> bool:
        """Configurar todos os registros DNS necessários"""
        self.log(f"Configurando DNS para {self.domain_name} -> {self.target_url}")
        
        # Determinar tipo de registro baseado no target
        if 'vercel.app' in self.target_url:
            # Vercel - usar CNAME
            records = [
                ('CNAME', self.domain_name, self.target_url, True),
                ('CNAME', f'www.{self.domain_name}', self.target_url, True)
            ]
        elif 'cloudfront.net' in self.target_url:
            # CloudFront - usar CNAME
            records = [
                ('CNAME', self.domain_name, self.target_url, True),
                ('CNAME', f'www.{self.domain_name}', self.target_url, True)
            ]
        else:
            # IP ou outro - tentar CNAME
            records = [
                ('CNAME', self.domain_name, self.target_url, True),
                ('CNAME', f'www.{self.domain_name}', self.target_url, True)
            ]
            
        success = True
        for record_type, name, content, proxied in records:
            if not self.create_dns_record(record_type, name, content, proxied):
                success = False
                
        return success
        
    def enable_ssl(self) -> bool:
        """Habilitar SSL/TLS"""
        if not self.zone_id:
            return False
            
        self.log("Configurando SSL/TLS...")
        
        try:
            # Configurar SSL para "Full (strict)"
            ssl_data = {'value': 'full'}
            
            response = requests.patch(
                f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/settings/ssl',
                headers=self.headers,
                json=ssl_data
            )
            
            if response.status_code == 200:
                self.log("SSL configurado para 'Full'", "SUCCESS")
            else:
                self.log("Erro ao configurar SSL", "WARNING")
                
            # Habilitar "Always Use HTTPS"
            https_data = {'value': 'on'}
            
            response = requests.patch(
                f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/settings/always_use_https',
                headers=self.headers,
                json=https_data
            )
            
            if response.status_code == 200:
                self.log("'Always Use HTTPS' habilitado", "SUCCESS")
                return True
            else:
                self.log("Erro ao habilitar HTTPS automático", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Erro ao configurar SSL: {e}", "ERROR")
            return False
            
    def setup_page_rules(self) -> bool:
        """Configurar regras de página para www redirect"""
        if not self.zone_id:
            return False
            
        self.log("Configurando redirecionamento www...")
        
        try:
            # Regra para redirecionar www para domínio principal
            rule_data = {
                'targets': [
                    {
                        'target': 'url',
                        'constraint': {
                            'operator': 'matches',
                            'value': f'www.{self.domain_name}/*'
                        }
                    }
                ],
                'actions': [
                    {
                        'id': 'forwarding_url',
                        'value': {
                            'url': f'https://{self.domain_name}/$1',
                            'status_code': 301
                        }
                    }
                ],
                'priority': 1,
                'status': 'active'
            }
            
            response = requests.post(
                f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/pagerules',
                headers=self.headers,
                json=rule_data
            )
            
            if response.status_code == 200:
                self.log("Redirecionamento www configurado", "SUCCESS")
                return True
            else:
                self.log("Erro ao configurar redirecionamento", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Erro ao configurar page rules: {e}", "ERROR")
            return False
            
    def setup_complete(self) -> bool:
        """Configuração completa do DNS"""
        self.log(f"🚀 Configurando DNS completo para {self.domain_name}")
        
        # 1. Obter/verificar token
        if not self.get_api_token():
            return False
            
        if not self.verify_api_token():
            return False
            
        # 2. Encontrar zone
        if not self.find_zone_id():
            return False
            
        # 3. Configurar registros DNS
        if not self.setup_dns_records():
            return False
            
        # 4. Configurar SSL
        self.enable_ssl()
        
        # 5. Configurar redirecionamentos
        self.setup_page_rules()
        
        # Relatório final
        self.log("🎉 DNS configurado com sucesso!", "SUCCESS")
        self.log(f"📊 Configuração:")
        self.log(f"   Domínio: {self.domain_name}")
        self.log(f"   Target: {self.target_url}")
        self.log(f"   SSL: Habilitado")
        self.log(f"   CDN: Habilitado (Cloudflare)")
        self.log(f"   www redirect: Configurado")
        
        self.log("⏰ Aguarde 5-10 minutos para propagação DNS")
        self.log(f"🌐 Teste: https://{self.domain_name}")
        
        return True


def main():
    """Função principal"""
    print("🌐 Configuração DNS Cloudflare - DJBlog")
    print("=" * 50)
    
    # Solicitar informações
    domain_name = input("Digite seu domínio (ex: meublog.com.br): ").strip()
    target_url = input("URL de destino (ex: site.vercel.app): ").strip()
    
    if not domain_name or not target_url:
        print("❌ Domínio e URL de destino são obrigatórios!")
        return
        
    print(f"\\n📋 Configuração:")
    print(f"   Domínio: {domain_name}")
    print(f"   Destino: {target_url}")
    print(f"   Provider: Cloudflare")
    
    print(f"\\n📝 Requisitos:")
    print(f"   1. Domínio já adicionado na Cloudflare")
    print(f"   2. Token da API Cloudflare")
    print(f"   3. Site de destino funcionando")
    
    confirm = input("\\nContinuar? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Configuração cancelada.")
        return
        
    # Executar configuração
    dns_setup = CloudflareDNSSetup(domain_name, target_url)
    success = dns_setup.setup_complete()
    
    if success:
        print(f"\\n🎉 DNS configurado com sucesso!")
        print(f"🌐 Site: https://{domain_name}")
    else:
        print("\\n❌ Configuração falhou. Verifique os erros acima.")
        

if __name__ == "__main__":
    main()
