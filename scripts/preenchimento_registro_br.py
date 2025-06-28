#!/usr/bin/env python3
"""
Script de apoio para preenchimento dos campos no Registro.br
Guia visual passo a passo
"""

import os
import time
from datetime import datetime

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Imprime o cabeçalho"""
    print("=" * 60)
    print("🎯 PREENCHIMENTO REGISTRO.BR - GUIA VISUAL")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print()

def main():
    clear_screen()
    print_header()
    
    print("📍 SITUAÇÃO ATUAL:")
    print("✅ Você está na tela de 'Configurar endereçamento'")
    print("✅ Você vê os campos para preencher")
    print()
    
    print("🎯 CAMPO 1: 'Endereço do site'")
    print("=" * 40)
    print("1️⃣ Procure um dropdown ou radio button")
    print("2️⃣ Selecione: 'Nome Alternativo (CNAME)'")
    print("   OU")
    print("   Selecione: 'CNAME'")
    print()
    
    print("3️⃣ No campo de texto, digite EXATAMENTE:")
    print("   📋 d3q2d002qno2yn.cloudfront.net")
    print()
    print("⚠️  ATENÇÃO:")
    print("   • NÃO digite www")
    print("   • NÃO digite http://")
    print("   • NÃO adicione ponto (.) no final")
    print()
    
    print("🎯 CAMPO 2: 'Servidor de e-mail'")
    print("=" * 40)
    print("🔹 OPÇÃO A (Recomendada): Deixe VAZIO")
    print("🔹 OPÇÃO B (Se obrigatório): aspmx.l.google.com")
    print()
    
    print("💾 SALVAR CONFIGURAÇÃO:")
    print("=" * 30)
    print("1️⃣ Confira se preencheu corretamente:")
    print("   ✅ Tipo: CNAME")
    print("   ✅ Valor: d3q2d002qno2yn.cloudfront.net")
    print()
    print("2️⃣ Clique em 'Salvar' ou 'Confirmar'")
    print()
    
    print("⏰ PRÓXIMOS PASSOS:")
    print("=" * 25)
    print("🔄 Aguardar 5-15 minutos para propagação DNS")
    print("📡 Monitor automático está rodando")
    print("🎉 Você receberá aviso quando estiver funcionando!")
    print()
    
    print("💡 DICA:")
    print("Mantenha esta janela aberta e volte ao navegador")
    print("para preencher os campos conforme as instruções acima.")
    print()
    
    input("Pressione ENTER quando terminar de preencher...")
    
    # Verificar se quer ajuda adicional
    print("\n🤔 Teve alguma dificuldade?")
    resposta = input("Digite 's' se precisar de mais ajuda, ou ENTER para continuar: ").lower()
    
    if resposta == 's':
        print("\n🆘 PROBLEMAS COMUNS:")
        print("=" * 25)
        print("❓ Não encontra opção CNAME?")
        print("   → Procure 'Nome Alternativo' ou 'Alias'")
        print()
        print("❓ Campo obrigatório de e-mail?")
        print("   → Use: aspmx.l.google.com")
        print()
        print("❓ Erro ao salvar?")
        print("   → Verifique se não tem espaços extras")
        print("   → Confirme: d3q2d002qno2yn.cloudfront.net")
        print()
        print("❓ Quer adicionar www também?")
        print("   → Procure botão 'Adicionar registro'")
        print("   → Nome: www")
        print("   → Tipo: CNAME")
        print("   → Valor: d3q2d002qno2yn.cloudfront.net")
        print()
    
    print("\n✅ Configuração salva!")
    print("🔄 Monitor DNS continuará rodando...")
    print("📧 Você será notificado quando estiver funcionando!")

if __name__ == "__main__":
    main()
