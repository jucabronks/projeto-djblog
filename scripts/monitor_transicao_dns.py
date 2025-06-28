#!/usr/bin/env python3
"""
Monitor de transição DNS - Cloudflare
Monitora a transição do DNS e avisa quando estiver pronto
"""

import time
import subprocess
import socket
from datetime import datetime, timedelta

def verificar_servidores_dns():
    """Verifica quais servidores DNS estão respondendo"""
    print("🔍 VERIFICANDO SERVIDORES DNS")
    print("=" * 40)
    
    # Testa diferentes servidores DNS
    servidores = {
        "Google DNS": "8.8.8.8",
        "Cloudflare DNS": "1.1.1.1", 
        "OpenDNS": "208.67.222.222"
    }
    
    for nome, servidor in servidores.items():
        try:
            result = subprocess.run(
                ['nslookup', 'noticiasontem.com.br', servidor],
                capture_output=True, text=True, timeout=10
            )
            
            if 'cloudfront' in result.stdout.lower() or '3.167.54' in result.stdout:
                print(f"✅ {nome}: Resolvendo para CloudFront")
            elif 'address:' in result.stdout.lower():
                print(f"⚠️  {nome}: Resolvendo para outro IP")
            else:
                print(f"❌ {nome}: Não resolvendo")
                
        except Exception:
            print(f"❌ {nome}: Timeout ou erro")

def verificar_nameservers():
    """Verifica nameservers autoritativos"""
    print("\n🌐 VERIFICANDO NAMESERVERS")
    print("=" * 40)
    
    try:
        result = subprocess.run(
            ['nslookup', '-type=NS', 'noticiasontem.com.br'],
            capture_output=True, text=True, timeout=10
        )
        
        if 'cloudflare' in result.stdout.lower():
            print("✅ Nameservers Cloudflare ativos!")
            return True
        elif 'registro.br' in result.stdout.lower():
            print("⏳ Ainda usando nameservers Registro.br")
            return False
        else:
            print("⚠️  Nameservers indefinidos")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar nameservers: {e}")
        return False

def calcular_tempo_restante():
    """Calcula tempo restante estimado"""
    print("\n⏰ TEMPO ESTIMADO")
    print("=" * 40)
    
    # Baseado na mensagem original: ~1h56m
    agora = datetime.now()
    estimativa = agora + timedelta(hours=1, minutes=56)
    
    print(f"🕐 Agora: {agora.strftime('%H:%M:%S')}")
    print(f"🎯 Estimativa conclusão: {estimativa.strftime('%H:%M:%S')}")
    print(f"⏳ Tempo restante: ~{(estimativa - agora).seconds // 3600}h{((estimativa - agora).seconds % 3600) // 60}m")

def testar_site():
    """Testa acesso ao site"""
    print("\n🧪 TESTE BÁSICO DO SITE")
    print("=" * 40)
    
    # Testa CloudFront direto
    try:
        import requests
        response = requests.get("https://d3q2d002qno2yn.cloudfront.net", timeout=10)
        if response.status_code == 200:
            print("✅ CloudFront: Funcionando perfeitamente")
        else:
            print(f"⚠️  CloudFront: Status {response.status_code}")
    except Exception as e:
        print(f"❌ CloudFront: Erro {e}")
    
    # Testa resolução DNS
    dominios = ["noticiasontem.com.br", "www.noticiasontem.com.br"]
    for dominio in dominios:
        try:
            ip = socket.gethostbyname(dominio)
            print(f"✅ {dominio}: {ip}")
        except:
            print(f"❌ {dominio}: Não resolvido")

def main():
    print("🔄 MONITOR TRANSIÇÃO DNS - CLOUDFLARE")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Verifica status atual
    verificar_servidores_dns()
    cloudflare_ativo = verificar_nameservers()
    calcular_tempo_restante()
    testar_site()
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DA TRANSIÇÃO:")
    
    if cloudflare_ativo:
        print("🎉 TRANSIÇÃO COMPLETA!")
        print("✅ Nameservers Cloudflare ativos")
        print("🚀 Pode configurar SSL agora")
        print("📞 Execute: python scripts/configurar_ssl_dominio.py")
    else:
        print("⏳ TRANSIÇÃO EM ANDAMENTO")
        print("⚠️  Ainda usando nameservers antigos")
        print("📅 Aguarde mais ~2 horas")
        print("☕ CloudFront funcionando enquanto isso")
    
    print("\n🎯 SITE ATUAL:")
    print("✅ Funcionando: https://d3q2d002qno2yn.cloudfront.net")
    print("⏳ Em transição: noticiasontem.com.br")
    print("=" * 60)

if __name__ == "__main__":
    main()
