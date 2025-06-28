#!/usr/bin/env python3
"""
Script para testar se o modal está funcionando no site atual
"""

import requests
import re

def testar_modal_local():
    """Testa se o modal está presente no HTML"""
    try:
        # Ler arquivo local
        with open(r'c:\Users\dgajr\OneDrive\Área de Trabalho\projeto-djblog\index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Verificar elementos essenciais do modal
        checks = {
            'Modal HTML': 'id="newsModal"' in html_content,
            'Função openModal': 'function openModal(' in html_content,
            'Função closeModal': 'function closeModal(' in html_content,
            'Event Listener': 'addEventListener' in html_content,
            'onclick handlers': 'onclick="openModal(' in html_content,
            'Modal CSS': '.modal' in html_content and '.modal.active' in html_content
        }
        
        print("=== TESTE DO MODAL - ARQUIVO LOCAL ===")
        for check, result in checks.items():
            status = "✅ OK" if result else "❌ ERRO"
            print(f"{check}: {status}")
        
        # Contar elementos clicáveis
        onclick_count = len(re.findall(r'onclick="openModal\(', html_content))
        print(f"\nElementos clicáveis encontrados: {onclick_count}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"❌ Erro ao testar modal local: {e}")
        return False

def testar_modal_online():
    """Testa se o modal está funcionando no site online"""
    try:
        url = "https://noticiasontem.com.br"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Site retornou status {response.status_code}")
            return False
        
        html_content = response.text
        
        # Verificar elementos essenciais do modal
        checks = {
            'Modal HTML': 'id="newsModal"' in html_content,
            'Função openModal': 'function openModal(' in html_content,
            'Função closeModal': 'function closeModal(' in html_content,
            'Event Listener': 'addEventListener' in html_content,
            'onclick handlers': 'onclick="openModal(' in html_content
        }
        
        print("\n=== TESTE DO MODAL - SITE ONLINE ===")
        for check, result in checks.items():
            status = "✅ OK" if result else "❌ ERRO"
            print(f"{check}: {status}")
        
        # Contar elementos clicáveis
        onclick_count = len(re.findall(r'onclick="openModal\(', html_content))
        print(f"\nElementos clicáveis encontrados online: {onclick_count}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"❌ Erro ao testar modal online: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testando funcionalidade do modal...")
    
    # Teste local
    local_ok = testar_modal_local()
    
    # Teste online  
    online_ok = testar_modal_online()
    
    print("\n" + "="*50)
    print("RESUMO DOS TESTES:")
    print(f"Modal local: {'✅ Funcionando' if local_ok else '❌ Com problemas'}")
    print(f"Modal online: {'✅ Funcionando' if online_ok else '❌ Com problemas'}")
    
    if not online_ok and local_ok:
        print("\n💡 O modal está funcionando localmente mas não online.")
        print("   Isso indica que o arquivo no S3 pode estar desatualizado.")
        print("   Recomendo fazer novo deploy!")
