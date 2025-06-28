#!/usr/bin/env python3
"""
Guia específico: ENCONTRAR DNS no Registro.br
Para quando não consegue localizar a opção
"""

import webbrowser
import time


def main():
    """Guia para encontrar DNS no Registro.br"""
    
    print("🔍 ENCONTRAR OPÇÃO DNS no Registro.br")
    print("=" * 40)
    print()
    
    print("Vou te ajudar a ENCONTRAR onde está o DNS")
    print("Domínio: noticiasontem.com.br")
    print()
    
    # Abrir site
    print("🌐 Abrindo Registro.br...")
    try:
        webbrowser.open("https://registro.br")
        print("✅ Site aberto")
    except:
        print("❌ Abra: https://registro.br")
    
    input("Pressione ENTER quando estiver no site...")
    
    print("\n📋 LOCALIZANDO DNS - MÉTODO 1")
    print("=" * 35)
    print("Após fazer LOGIN, você está no painel principal:")
    print()
    print("🔍 PROCURE no MENU LATERAL ESQUERDO:")
    print("• 'Meus Domínios'")
    print("• 'Domínios'") 
    print("• 'Serviços'")
    print()
    print("👆 CLIQUE em 'Meus Domínios'")
    
    input("\\nClicou em Meus Domínios? ENTER...")
    
    print("\\n📋 MÉTODO 1: Lista de Domínios")
    print("=" * 35)
    print("🔍 VOCÊ DEVE VER:")
    print("• Lista com seus domínios")
    print("• noticiasontem.com.br na lista")
    print()
    print("👆 CLIQUE DIRETAMENTE no nome: noticiasontem.com.br")
    print("(NÃO em botões, clique no NOME do domínio)")
    
    input("\\nClicou no nome do domínio? ENTER...")
    
    print("\\n📋 DENTRO DA PÁGINA DO DOMÍNIO")
    print("=" * 35)
    print("Agora você está na página específica do domínio")
    print()
    print("🔍 PROCURE POR ESSAS OPÇÕES (em qualquer lugar):")
    print("• 'DNS'")
    print("• 'Configurar DNS'")
    print("• 'Serviços DNS'")
    print("• 'Zona DNS'")
    print("• 'Name Servers'")
    print("• 'Configurações'")
    print()
    print("📍 ONDE PROCURAR:")
    print("1. Menu lateral esquerdo")
    print("2. Abas no topo")
    print("3. Seção 'Serviços'")
    print("4. Botões na página")
    
    choice = input("\\nEncontrou alguma opção de DNS? (s/n): ").lower()
    
    if choice == 's':
        print("\\n✅ ÓTIMO! Clique na opção DNS que encontrou")
        print("Depois me avise o que aparece na tela")
    else:
        print("\\n📋 MÉTODO 2: Procurar em SERVIÇOS")
        print("=" * 35)
        print("🔍 SE NÃO ENCONTROU DNS, PROCURE:")
        print("• Aba 'SERVIÇOS' (no topo)")
        print("• Seção 'SERVIÇOS' (na página)")
        print("• Menu 'CONFIGURAÇÕES'")
        print()
        print("👆 CLIQUE em qualquer 'SERVIÇOS' que encontrar")
        
        input("\\nClicou em Serviços? ENTER...")
        
        print("\\n📋 DENTRO DE SERVIÇOS")
        print("=" * 25)
        print("🔍 PROCURE POR:")
        print("• DNS")
        print("• Configurar DNS")
        print("• Name Servers")
        print("• Zona DNS")
        
        choice2 = input("\\nEncontrou DNS em Serviços? (s/n): ").lower()
        
        if choice2 == 's':
            print("\\n✅ PERFEITO! Clique na opção DNS")
        else:
            print("\\n📋 MÉTODO 3: Buscar por CONFIGURAÇÕES")
            print("=" * 40)
            print("🔍 ÚLTIMA TENTATIVA:")
            print("• Procure 'CONFIGURAÇÕES'")
            print("• Ou 'CONFIGURAR'")
            print("• Ou 'GERENCIAR'")
            print("• Ou ícone de engrenagem ⚙️")
            
            choice3 = input("\\nEncontrou Configurações? (s/n): ").lower()
            
            if choice3 == 's':
                print("\\n✅ CLIQUE em Configurações e procure DNS dentro")
            else:
                print("\\n❌ MÉTODO ALTERNATIVO")
                print("=" * 25)
                print("🔍 TENTE ESTE LINK DIRETO:")
                print("Após fazer login, cole na barra de endereços:")
                print("https://registro.br/painel/dns/")
                print()
                print("OU procure por:")
                print("• 'Delegar DNS'")
                print("• 'Name Servers'")
                print("• 'Configurar Servidor DNS'")
    
    print("\\n" + "=" * 50)
    print("📸 SE AINDA NÃO ENCONTROU:")
    print("=" * 50)
    print("🤳 Me envie screenshot da tela que você está vendo")
    print("📝 Me diga exatamente o que aparece no menu")
    print("🔍 Posso te ajudar a encontrar baseado no que você vê")
    print()
    print("💡 DICAS PARA SCREENSHOT:")
    print("• Capture a tela inteira do painel")
    print("• Certifique-se que está logado")
    print("• Mostre todos os menus/opções visíveis")
    
    print("\\n🎯 QUANDO ENCONTRAR DNS:")
    print("=" * 30)
    print("📝 ADICIONE APENAS 2 REGISTROS:")
    print()
    print("🔹 REGISTRO 1:")
    print("   Nome: @ (ou vazio)")
    print("   Tipo: CNAME")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")
    print()
    print("🔹 REGISTRO 2:")
    print("   Nome: www")
    print("   Tipo: CNAME")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")


if __name__ == "__main__":
    main()
