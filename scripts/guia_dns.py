#!/usr/bin/env python3
"""
Guia interativo para configurar DNS
Te ajuda a encontrar onde configurar o DNS do seu domínio
"""

import webbrowser
import time


def main():
    """Guia interativo para DNS"""
    
    print("🔧 Guia Interativo: Configurar DNS")
    print("=" * 40)
    print()
    
    print("Vou te ajudar a configurar o DNS do noticiasontem.com.br")
    print()
    
    # Descobrir onde o domínio foi registrado
    print("📋 PRIMEIRO: Onde você registrou o domínio?")
    print("1. Registro.br (oficial .com.br)")
    print("2. UOL Host") 
    print("3. GoDaddy")
    print("4. Locaweb")
    print("5. Hostgator")
    print("6. Outro / Não sei")
    print()
    
    choice = input("Digite o número da opção (1-6): ").strip()
    
    if choice == "1":
        print("\n🎯 REGISTRO.BR - Configuração DNS")
        print("=" * 40)
        print("1. Acesse: https://registro.br")
        print("2. Clique em 'Entrar' (canto superior direito)")
        print("3. Faça login com CPF e senha")
        print("4. Vá em 'Meus Domínios'")
        print("5. Clique em 'noticiasontem.com.br'")
        print("6. Procure por 'DNS' ou 'Configurar DNS'")
        print()
        
        # Abrir site automaticamente
        try:
            webbrowser.open("https://registro.br")
            print("✅ Abrindo Registro.br no navegador...")
        except:
            pass
            
    elif choice == "2":
        print("\n🎯 UOL HOST - Configuração DNS")
        print("=" * 40)
        print("1. Acesse: https://painel.uolhost.com.br")
        print("2. Faça login com seus dados")
        print("3. Vá em 'Meus Produtos' ou 'Domínios'")
        print("4. Clique em 'noticiasontem.com.br'")
        print("5. Procure por 'DNS' ou 'Zona DNS'")
        print()
        
        try:
            webbrowser.open("https://painel.uolhost.com.br")
            print("✅ Abrindo UOL Host no navegador...")
        except:
            pass
            
    elif choice == "3":
        print("\n🎯 GODADDY - Configuração DNS")
        print("=" * 40)
        print("1. Acesse: https://sso.godaddy.com")
        print("2. Faça login com seus dados")
        print("3. Vá em 'My Products' → 'Domains'")
        print("4. Clique em 'noticiasontem.com.br'")
        print("5. Clique em 'DNS' ou 'Manage DNS'")
        print()
        
        try:
            webbrowser.open("https://sso.godaddy.com")
            print("✅ Abrindo GoDaddy no navegador...")
        except:
            pass
            
    elif choice == "4":
        print("\n🎯 LOCAWEB - Configuração DNS")
        print("=" * 40)
        print("1. Acesse: https://painel.locaweb.com.br")
        print("2. Faça login com seus dados")
        print("3. Vá em 'Domínios'")
        print("4. Clique em 'noticiasontem.com.br'")
        print("5. Procure por 'DNS' ou 'Zona de DNS'")
        print()
        
        try:
            webbrowser.open("https://painel.locaweb.com.br")
            print("✅ Abrindo Locaweb no navegador...")
        except:
            pass
            
    elif choice == "5":
        print("\n🎯 HOSTGATOR - Configuração DNS")
        print("=" * 40)
        print("1. Acesse: https://financeiro.hostgator.com.br")
        print("2. Faça login com seus dados")
        print("3. Vá em 'Meus Produtos' → 'Domínios'")
        print("4. Clique em 'noticiasontem.com.br'")
        print("5. Procure por 'DNS' ou 'Gerenciar DNS'")
        print()
        
        try:
            webbrowser.open("https://financeiro.hostgator.com.br")
            print("✅ Abrindo HostGator no navegador...")
        except:
            pass
            
    else:
        print("\n🔍 DESCOBRIR ONDE O DOMÍNIO FOI REGISTRADO")
        print("=" * 50)
        print("Vou te ajudar a descobrir onde foi registrado...")
        print()
        
        try:
            import subprocess
            result = subprocess.run(['nslookup', 'noticiasontem.com.br'], 
                                  capture_output=True, text=True)
            print("📊 Informações do domínio:")
            print(result.stdout)
        except:
            print("Execute no cmd: nslookup noticiasontem.com.br")
        print()
        print("🔍 Ou verifique no WHOIS:")
        print("https://registro.br/tecnologia/ferramentas/whois/")
        
        try:
            webbrowser.open("https://registro.br/tecnologia/ferramentas/whois/")
            print("✅ Abrindo consulta WHOIS...")
        except:
            pass
    
    print("\n" + "=" * 50)
    print("📋 REGISTROS PARA ADICIONAR NO PAINEL DNS:")
    print("=" * 50)
    print()
    
    print("🔹 REGISTRO 1:")
    print("   Nome: _19837e8068f6a4d75e9bdfd772154663.noticiasontem.com.br")
    print("   Tipo: CNAME")
    print("   Valor: _a94a255a3c25cba74c95244e79562393.xlfgrmvvlj.acm-validations.aws.")
    print()
    
    print("🔹 REGISTRO 2:")
    print("   Nome: _88fe1a2469d7ce78bd80f82750e60fef.www.noticiasontem.com.br")
    print("   Tipo: CNAME")
    print("   Valor: _1aa1b9515605c723c3757c748117b9fa.xlfgrmvvlj.acm-validations.aws.")
    print()
    
    print("🔹 REGISTRO 3:")
    print("   Nome: noticiasontem.com.br (ou deixe vazio para raiz)")
    print("   Tipo: CNAME")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")
    print()
    
    print("🔹 REGISTRO 4:")
    print("   Nome: www")
    print("   Tipo: CNAME")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")
    print()
    
    print("🎯 DICAS IMPORTANTES:")
    print("• Se pedir 'TTL', use 300 (5 minutos)")
    print("• Alguns painéis não precisam do ponto final (.)")
    print("• Se não conseguir CNAME na raiz, use A record")
    print("• Aguarde 5-15 minutos após salvar")
    print()
    
    print("📞 PRECISA DE MAIS AJUDA?")
    print("• Me diga qual painel você está vendo")
    print("• Tire uma screenshot se necessário")
    print("• Posso te guiar passo a passo")
    print()
    
    input("Pressione ENTER quando terminar de configurar...")
    
    print("\n🔄 Testando propagação DNS...")
    try:
        import subprocess
        result = subprocess.run(['nslookup', 'noticiasontem.com.br'], 
                              capture_output=True, text=True)
        if 'cloudfront' in result.stdout.lower():
            print("✅ DNS propagado com sucesso!")
            print("🚀 Execute: python scripts/setup_cloudfront_domain.py")
        else:
            print("⏳ DNS ainda propagando... aguarde mais alguns minutos")
            print("🔄 Teste novamente em 5 minutos")
    except:
        print("🔄 Teste manualmente: nslookup noticiasontem.com.br")


if __name__ == "__main__":
    main()
