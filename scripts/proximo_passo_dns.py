#!/usr/bin/env python3
"""
Próximo passo: Configurar DNS no Registro.br
Agora que você encontrou a seção DNS
"""

def main():
    print("🎉 PERFEITO! Você encontrou a seção DNS!")
    print("=" * 45)
    print()
    
    print("🔍 VOCÊ ESTÁ VENDO:")
    print("• 'DNS'")
    print("• 'Os servidores DNS são responsáveis...'")
    print("• 'Você está utilizando os servidores DNS do Registro.br'")
    print("• 'Alterar servidores DNS'")
    print("• 'Configurar endereçamento'")
    print()
    
    print("🎯 PRÓXIMO PASSO:")
    print("👆 CLIQUE em 'Configurar endereçamento'")
    print()
    print("💡 POR QUE 'Configurar endereçamento'?")
    print("• É onde você adiciona os registros CNAME")
    print("• É onde você aponta seu domínio para o CloudFront")
    print("• NÃO clique em 'Alterar servidores DNS'")
    print()
    
    input("Clicou em 'Configurar endereçamento'? Pressione ENTER...")
    
    print("\n📋 DEPOIS DE CLICAR EM 'CONFIGURAR ENDEREÇAMENTO':")
    print("=" * 55)
    print()
    print("🔍 VOCÊ DEVE VER UMA DESSAS TELAS:")
    print()
    print("1️⃣ OPÇÃO 1: Lista de registros DNS")
    print("   • Tabela com Type, Name, Value")
    print("   • Botão 'Adicionar' ou '+' ")
    print("   • Registros A, CNAME, MX existentes")
    print()
    print("2️⃣ OPÇÃO 2: Formulário direto")
    print("   • Campos: Tipo, Nome, Valor")
    print("   • Dropdown para selecionar tipo")
    print()
    print("3️⃣ OPÇÃO 3: Abas separadas")
    print("   • Aba 'A Records'")
    print("   • Aba 'CNAME Records'")
    print("   • Aba 'MX Records'")
    print()
    
    print("📝 ME DIGA O QUE VOCÊ VÊ:")
    print("• Tem uma tabela/lista?")
    print("• Tem botão 'Adicionar'?")
    print("• Tem abas separadas?")
    print("• Tem campos para preencher?")
    
    response = input("\nDescreva o que você vê ou digite 'help': ").strip().lower()
    
    if 'tabela' in response or 'lista' in response or 'adicionar' in response:
        print("\n✅ ÓTIMO! Você vê uma tabela com botão Adicionar")
        show_table_instructions()
    elif 'formulario' in response or 'campos' in response:
        print("\n✅ ÓTIMO! Você vê um formulário direto")
        show_form_instructions()
    elif 'aba' in response or 'tab' in response:
        print("\n✅ ÓTIMO! Você vê abas separadas")
        show_tabs_instructions()
    else:
        print("\n📱 SEM PROBLEMAS! Vou te dar todas as opções:")
        show_all_instructions()

def show_table_instructions():
    print("\n🎯 INSTRUÇÕES PARA TABELA/LISTA:")
    print("=" * 35)
    print("1️⃣ Procure botão 'Adicionar', 'Novo' ou '+' ")
    print("2️⃣ Clique nesse botão")
    print("3️⃣ Aparecerá um formulário")
    print("4️⃣ Preencha conforme abaixo:")
    print()
    show_records()

def show_form_instructions():
    print("\n🎯 INSTRUÇÕES PARA FORMULÁRIO DIRETO:")
    print("=" * 38)
    print("1️⃣ Você já pode preencher os campos")
    print("2️⃣ Preencha conforme abaixo:")
    print()
    show_records()

def show_tabs_instructions():
    print("\n🎯 INSTRUÇÕES PARA ABAS:")
    print("=" * 25)
    print("1️⃣ Clique na aba 'CNAME Records' ou 'CNAME'")
    print("2️⃣ Procure botão 'Adicionar' nessa aba")
    print("3️⃣ Preencha conforme abaixo:")
    print()
    show_records()

def show_all_instructions():
    print("\n🎯 TODAS AS POSSIBILIDADES:")
    print("=" * 30)
    print("• Se vê TABELA → Clique 'Adicionar'")
    print("• Se vê FORMULÁRIO → Preencha direto")
    print("• Se vê ABAS → Clique aba 'CNAME'")
    print()
    show_records()

def show_records():
    print("📝 REGISTROS PARA ADICIONAR:")
    print("=" * 30)
    print()
    print("🔹 REGISTRO 1 (Domínio Principal):")
    print("   Tipo: CNAME")
    print("   Nome: @ (arroba) ou deixe vazio")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")
    print("   TTL: 300 (se pedir)")
    print()
    print("🔹 REGISTRO 2 (WWW):")
    print("   Tipo: CNAME") 
    print("   Nome: www")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")
    print("   TTL: 300 (se pedir)")
    print()
    print("💾 DEPOIS DE CADA REGISTRO:")
    print("• Clique 'Salvar' ou 'Adicionar'")
    print("• Repita para o próximo registro")
    print()
    print("🎯 CAMPOS PODEM TER NOMES DIFERENTES:")
    print("• Nome = Host = Subdomínio = Prefixo")
    print("• Valor = Destino = Target = Aponta para")
    print("• Tipo = Type = Record Type")
    print()
    print("⚠️ IMPORTANTE:")
    print("• Não precisa adicionar registros SSL agora")
    print("• Apenas os 2 CNAME acima")
    print("• SSL configuramos depois")

if __name__ == "__main__":
    main()
