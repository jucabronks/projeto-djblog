#!/usr/bin/env python3
"""
Script para testar as abas de categorias do site
"""

import requests
import webbrowser
import time

def testar_abas_categorias():
    """Testa se as abas estão funcionando corretamente"""
    print("🔍 TESTE DAS ABAS DE CATEGORIAS")
    print("="*50)
    
    url = "https://noticiasontem.com.br"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Site retornou status {response.status_code}")
            return False
        
        html = response.text
        
        # Verificar se as abas estão presentes
        categorias = [
            ("🗞️ Todas", "tab-todos"),
            ("🏛️ Política", "tab-politica"), 
            ("💰 Economia", "tab-economia"),
            ("💻 Tecnologia", "tab-tecnologia"),
            ("⚽ Esportes", "tab-esportes"),
            ("🏥 Saúde", "tab-saude"),
            ("🎭 Cultura", "tab-cultura"),
            ("🌍 Internacional", "tab-internacional")
        ]
        
        print("🏷️  VERIFICANDO ABAS:")
        for nome, id_tab in categorias:
            presente = id_tab in html
            contador_presente = f'id="count-{id_tab.replace("tab-", "")}"' in html
            status = "✅" if presente and contador_presente else "❌"
            print(f"   {nome}: {status}")
        
        # Verificar JavaScript das abas
        js_checks = {
            "Função switchTab": "function switchTab(" in html,
            "Função loadNewsForTab": "function loadNewsForTab(" in html,
            "Dados por categoria": "newsByCategory" in html,
            "Event listeners": "addEventListener" in html,
            "Contadores de abas": "updateTabCounters" in html
        }
        
        print("\n🔧 VERIFICANDO JAVASCRIPT:")
        for check, result in js_checks.items():
            status = "✅" if result else "❌"
            print(f"   {check}: {status}")
        
        # Verificar CSS das abas
        css_checks = {
            "CSS das abas": ".tabs-nav" in html,
            "Botões de aba": ".tab-btn" in html,
            "Estado ativo": ".tab-btn.active" in html,
            "Conteúdo das abas": ".tab-content" in html,
            "Animações": "@keyframes fadeIn" in html
        }
        
        print("\n🎨 VERIFICANDO CSS:")
        for check, result in css_checks.items():
            status = "✅" if result else "❌"
            print(f"   {check}: {status}")
        
        # Contar quantas notícias estão disponíveis
        noticias_count = html.count('class="news-card"')
        print(f"\n📰 Estruturas de notícias encontradas: {noticias_count}")
        
        all_checks = all(js_checks.values()) and all(css_checks.values())
        
        return all_checks
        
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
        return False

def demo_funcionalidades():
    """Mostra como usar as novas funcionalidades"""
    print("\n" + "="*50)
    print("🎯 COMO USAR AS NOVAS ABAS:")
    print("="*50)
    print("1. 🗞️  ABA 'TODAS' - Mostra todas as notícias em ordem cronológica")
    print("2. 🏛️  ABA 'POLÍTICA' - Notícias sobre governo, eleições e política")
    print("3. 💰 ABA 'ECONOMIA' - PIB, inflação, mercado financeiro")
    print("4. 💻 ABA 'TECNOLOGIA' - IA, 5G, inovações e startups")
    print("5. ⚽ ABA 'ESPORTES' - Futebol, atletismo e competições")
    print("6. 🏥 ABA 'SAÚDE' - Medicina, SUS e bem-estar")
    print("7. 🎭 ABA 'CULTURA' - Arte, cinema e entretenimento")
    print("8. 🌍 ABA 'INTERNACIONAL' - Notícias globais e diplomacia")
    print("\n💡 RECURSOS:")
    print("• Contadores mostram número de notícias por categoria")
    print("• Clique nas abas para filtrar por interesse")
    print("• Modal funciona em todas as categorias")
    print("• Design responsivo para mobile")

if __name__ == "__main__":
    print("🚀 TESTANDO NOVO SISTEMA DE ABAS...")
    
    # Aguardar propagação
    print("⏰ Aguardando propagação do CDN...")
    time.sleep(60)
    
    # Teste das funcionalidades
    sucesso = testar_abas_categorias()
    
    # Demo das funcionalidades
    demo_funcionalidades()
    
    print("\n" + "="*50)
    if sucesso:
        print("✅ TODAS AS FUNCIONALIDADES IMPLEMENTADAS COM SUCESSO!")
    else:
        print("⚠️ ALGUMAS FUNCIONALIDADES PODEM PRECISAR DE AJUSTES")
    
    # Perguntar se quer abrir o browser
    print("\n🌐 Deseja abrir o site para testar as abas? (s/n): ", end="")
    try:
        resposta = input().lower().strip()
        if resposta in ['s', 'sim', 'y', 'yes']:
            print("🚀 Abrindo navegador...")
            webbrowser.open("https://noticiasontem.com.br")
            print("✅ Site aberto! Teste clicando nas diferentes abas!")
    except:
        pass
