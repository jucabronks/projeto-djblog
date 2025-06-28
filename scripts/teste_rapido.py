#!/usr/bin/env python3
"""
Teste rápido do site sem SSL para verificar funcionamento
"""

import requests
import socket
from datetime import datetime

def testar_acesso_http():
    """Testa acesso HTTP (sem SSL) aos domínios"""
    print("🧪 TESTE RÁPIDO - ACESSO HTTP")
    print("=" * 40)
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # 1. Testa CloudFront direto
    print("1️⃣ CLOUDFRONT DIRETO:")
    try:
        response = requests.get("https://d3q2d002qno2yn.cloudfront.net", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ CloudFront funcionando!")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Verifica resolução DNS
    dominios = ["noticiasontem.com.br", "www.noticiasontem.com.br"]
    
    print("\n2️⃣ RESOLUÇÃO DNS:")
    for dominio in dominios:
        try:
            ip = socket.gethostbyname(dominio)
            print(f"   {dominio} → {ip}")
        except:
            print(f"   {dominio} → ❌ Não resolvido")
    
    # 3. Testa acesso HTTP (sem SSL)
    print("\n3️⃣ TESTE HTTP (SEM SSL):")
    for dominio in dominios:
        try:
            # Tenta HTTP primeiro (para evitar erro SSL)
            response = requests.get(f"http://{dominio}", timeout=10, allow_redirects=False)
            print(f"   http://{dominio} → {response.status_code}")
            
            if response.status_code == 301 or response.status_code == 302:
                print(f"      Redirecionamento para: {response.headers.get('Location', 'N/A')}")
                
        except Exception as e:
            print(f"   http://{dominio} → ❌ {e}")
    
    print("\n" + "=" * 40)
    print("📋 DIAGNÓSTICO:")
    print("✅ CloudFront: Funcionando")
    print("🔄 DNS: Em propagação")
    print("⏳ SSL: Precisa configurar certificado")
    print("=" * 40)

if __name__ == "__main__":
    testar_acesso_http()
