#!/usr/bin/env python3
"""
Teste contínuo de DNS - noticiasontem.com.br
Monitora até o DNS estar funcionando
"""

import subprocess
import time
from datetime import datetime

def test_dns(domain):
    """Testa se o DNS está funcionando"""
    try:
        result = subprocess.run(['nslookup', domain], 
                              capture_output=True, text=True, timeout=10)
        if 'cloudfront' in result.stdout.lower():
            return True, result.stdout
        else:
            return False, result.stdout
    except:
        return False, "Timeout ou erro"

def main():
    print("🔄 MONITOR DNS CONTÍNUO - NOTICIASONTEM.COM.BR")
    print("=" * 50)
    print()
    
    domains = ['noticiasontem.com.br', 'www.noticiasontem.com.br']
    test_count = 0
    
    while True:
        test_count += 1
        current_time = datetime.now().strftime('%H:%M:%S')
        
        print(f"🕐 TESTE #{test_count} - {current_time}")
        print("-" * 30)
        
        all_working = True
        
        for domain in domains:
            working, output = test_dns(domain)
            
            if working:
                print(f"✅ {domain}: FUNCIONANDO!")
            else:
                print(f"⏳ {domain}: Ainda propagando...")
                all_working = False
        
        if all_working:
            print("\n🎉 SUCESSO! TODOS OS DOMÍNIOS FUNCIONANDO!")
            print("🌐 Teste agora no navegador:")
            print("- http://noticiasontem.com.br")
            print("- http://www.noticiasontem.com.br")
            break
        
        print("\n⏰ Próximo teste em 2 minutos...")
        print("=" * 50)
        
        # Aguardar 2 minutos
        time.sleep(120)

if __name__ == "__main__":
    main()
