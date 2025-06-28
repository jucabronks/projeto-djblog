#!/usr/bin/env python3
"""
Script para testar a funcionalidade completa do site
"""

import requests
import webbrowser
import time

def teste_completo_site():
    """Testa todas as funcionalidades do site"""
    print("🔍 TESTE COMPLETO DO SITE NOTÍCIAS ONTEM")
    print("="*50)
    
    # URLs para testar
    urls = [
        "https://noticiasontem.com.br",
        "https://www.noticiasontem.com.br"
    ]
    
    for url in urls:
        print(f"\n🌐 Testando: {url}")
        
        try:
            # Teste básico
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
            
            if response.status_code == 200:
                html = response.text
                
                # Testes específicos
                tests = {
                    "Título correto": "Notícias Ontem -" in html,
                    "CSS carregado": "style>" in html and ".news-card" in html,
                    "JavaScript presente": "<script>" in html and "function" in html,
                    "Modal implementado": 'id="newsModal"' in html,
                    "Cards clicáveis": 'onclick="openModal(' in html,
                    "Responsivo": "viewport" in html,
                    "HTTPS/SSL": url.startswith("https://"),
                    "Favicon": "favicon" in html or "icon" in html
                }
                
                for test_name, result in tests.items():
                    status = "✅" if result else "❌"
                    print(f"   {test_name}: {status}")
                
                # Teste de performance básico
                load_time = response.elapsed.total_seconds()
                speed_status = "✅" if load_time < 3 else "⚠️" if load_time < 5 else "❌"
                print(f"   Tempo de carregamento: {load_time:.2f}s {speed_status}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    print("\n" + "="*50)
    print("🎯 INSTRUÇÕES PARA TESTE MANUAL:")
    print("1. Abra o site em seu navegador")
    print("2. Clique em qualquer card de notícia")
    print("3. Verifique se o modal abre corretamente")
    print("4. Clique em itens individuais das notícias")
    print("5. Teste fechar o modal (X, ESC, clicar fora)")
    print("6. Teste em mobile (F12 > modo responsivo)")
    
    # Perguntar se quer abrir o browser
    print("\n🌐 Deseja abrir o site no navegador? (s/n): ", end="")
    try:
        resposta = input().lower().strip()
        if resposta in ['s', 'sim', 'y', 'yes']:
            print("🚀 Abrindo navegador...")
            webbrowser.open("https://noticiasontem.com.br")
            time.sleep(2)
            print("✅ Site aberto! Teste o modal clicando nas notícias!")
    except:
        pass

if __name__ == "__main__":
    teste_completo_site()
