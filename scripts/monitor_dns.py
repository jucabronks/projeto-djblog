#!/usr/bin/env python3
"""
Monitor de DNS - Verifica se DNS foi configurado
"""

import subprocess
import time
import sys


def test_dns(domain):
    """Testa se DNS foi configurado"""
    try:
        result = subprocess.run(['nslookup', domain], 
                              capture_output=True, text=True, timeout=5)
        
        if 'cloudfront' in result.stdout.lower():
            return True, "DNS configurado corretamente!"
        elif 'timeout' in result.stderr.lower() or 'não foi possível' in result.stdout.lower():
            return False, "Domínio ainda não configurado"
        else:
            return False, f"DNS configurado, mas não aponta para CloudFront"
            
    except subprocess.TimeoutExpired:
        return False, "Timeout - DNS pode não estar configurado"
    except Exception as e:
        return False, f"Erro: {e}"


def main():
    """Monitor contínuo"""
    domain = "noticiasontem.com.br"
    
    print(f"🔄 Monitor DNS para {domain}")
    print("=" * 50)
    print("Pressione Ctrl+C para parar")
    print()
    
    attempt = 1
    
    while True:
        try:
            print(f"🔍 Teste #{attempt} - {time.strftime('%H:%M:%S')}")
            
            success, message = test_dns(domain)
            
            if success:
                print(f"✅ {message}")
                print(f"🎉 SUCESSO! DNS configurado!")
                print(f"🌐 Teste: http://{domain}")
                print(f"🌐 Teste: http://www.{domain}")
                break
            else:
                print(f"⏳ {message}")
                
            print("Aguardando 30 segundos...")
            print("-" * 30)
            
            time.sleep(30)
            attempt += 1
            
        except KeyboardInterrupt:
            print("\n🛑 Monitor interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro no monitor: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
