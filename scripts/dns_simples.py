#!/usr/bin/env python3
"""
Método alternativo: Configurar domínio sem SSL primeiro
Para acelerar o processo e testar
"""

import webbrowser
import time


def main():
    """Configuração DNS simplificada"""
    
    print("🚀 MÉTODO RÁPIDO: Configurar Domínio")
    print("=" * 40)
    print()
    
    print("Vamos configurar primeiro SEM SSL para testar rapidamente")
    print("Depois adicionamos SSL quando estiver funcionando")
    print()
    
    # Confirmar domínio correto
    print("🔍 CONFIRME O DOMÍNIO:")
    print("• noticiasontem.com.br (original)")
    print("• noticiasdeontem.com.br (você digitou)")
    print()
    
    domain = input("Digite o domínio correto: ").strip()
    
    if not domain:
        print("❌ Domínio é obrigatório!")
        return
        
    print(f"\n📋 CONFIGURAÇÃO SIMPLES PARA: {domain}")
    print("=" * 50)
    print()
    
    print("🎯 ADICIONE APENAS ESTES 2 REGISTROS DNS:")
    print()
    
    print("🔹 REGISTRO 1 (Domínio principal):")
    print(f"   Nome: {domain} (ou deixe vazio/@)")
    print("   Tipo: CNAME")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")
    print("   TTL: 300")
    print()
    
    print("🔹 REGISTRO 2 (WWW):")
    print("   Nome: www")
    print("   Tipo: CNAME")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")
    print("   TTL: 300")
    print()
    
    print("💡 IMPORTANTE:")
    print("• NÃO adicione os registros SSL ainda")
    print("• Apenas estes 2 registros CNAME")
    print("• SSL configuramos depois que estiver funcionando")
    print()
    
    # Abrir registro.br
    print("🌐 Abrindo Registro.br...")
    try:
        webbrowser.open("https://registro.br")
        print("✅ Site aberto no navegador")
    except:
        print("❌ Abra manualmente: https://registro.br")
    
    print("\n🔧 PASSOS NO REGISTRO.BR:")
    print("1. Login → Meus Domínios")
    print(f"2. Clique em '{domain}'")
    print("3. Vá em 'DNS' ou 'Configurar DNS'")
    print("4. Adicione os 2 registros CNAME acima")
    print("5. Salve as alterações")
    print()
    
    input("Pressione ENTER quando terminar de configurar...")
    
    print("\n🔄 Testando DNS...")
    
    # Teste simples de DNS
    import subprocess
    try:
        result = subprocess.run(['nslookup', domain], 
                              capture_output=True, text=True, timeout=10)
        
        if 'cloudfront' in result.stdout.lower():
            print("✅ SUCESSO! DNS configurado corretamente!")
            print(f"🌐 Teste seu site: http://{domain}")
            print("⚠️ Ainda não tem SSL (HTTPS), apenas HTTP")
            print()
            print("🎯 PRÓXIMOS PASSOS:")
            print("1. Teste se o site carrega")
            print("2. Me avise que está funcionando")
            print("3. Configuramos SSL depois")
            
        else:
            print("⏳ DNS ainda propagando...")
            print("🔄 Execute este teste em 5 minutos:")
            print(f"nslookup {domain}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        print(f"🔄 Teste manualmente: nslookup {domain}")
    
    print(f"\n📝 TESTE MANUAL:")
    print(f"• CMD: nslookup {domain}")
    print(f"• Browser: http://{domain}")
    print(f"• Se carregar = DNS OK!")


if __name__ == "__main__":
    main()
