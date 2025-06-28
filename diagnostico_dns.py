#!/usr/bin/env python3
"""
Diagnóstico DNS Avançado - 40 minutos sem propagação
"""

import subprocess
import time
from datetime import datetime

def diagnosticar_dns():
    print("🚨 DIAGNÓSTICO DNS - 40 MINUTOS SEM PROPAGAÇÃO")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    print("🔍 TESTANDO DNS EM SERVIDORES EXTERNOS:")
    print("-" * 40)
    
    # Teste com DNS do Google
    print("📡 Testando com DNS Google (8.8.8.8)...")
    try:
        result = subprocess.run(["nslookup", "noticiasontem.com.br", "8.8.8.8"], 
                              capture_output=True, text=True, timeout=15)
        if "cloudfront" in result.stdout.lower():
            print("✅ Google DNS: FUNCIONANDO!")
        else:
            print("❌ Google DNS: Não encontrou CloudFront")
            print(f"Resposta: {result.stdout[:200]}")
    except Exception as e:
        print(f"❌ Google DNS: Erro - {e}")
    
    print()
    
    # Teste com DNS Cloudflare
    print("📡 Testando com DNS Cloudflare (1.1.1.1)...")
    try:
        result = subprocess.run(["nslookup", "www.noticiasontem.com.br", "1.1.1.1"], 
                              capture_output=True, text=True, timeout=15)
        if "cloudfront" in result.stdout.lower():
            print("✅ Cloudflare DNS: FUNCIONANDO!")
        else:
            print("❌ Cloudflare DNS: Não encontrou CloudFront")
            print(f"Resposta: {result.stdout[:200]}")
    except Exception as e:
        print(f"❌ Cloudflare DNS: Erro - {e}")
    
    print()
    print("🔧 ANÁLISE APÓS 40 MINUTOS:")
    print("=" * 30)
    print("⚠️  40 minutos é tempo suficiente para propagação")
    print("🔍 Possíveis problemas:")
    print("   1. Configuração incorreta no Registro.br")
    print("   2. Cache DNS muito agressivo")
    print("   3. Problema com CNAME para CloudFront")
    print()
    print("🛠️  RECOMENDAÇÕES:")
    print("   1. Verificar registros no painel Registro.br")
    print("   2. Testar com navegador em modo anônimo")
    print("   3. Limpar cache DNS: ipconfig /flushdns")

if __name__ == "__main__":
    diagnosticar_dns()
