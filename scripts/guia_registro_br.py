#!/usr/bin/env python3
"""
Guia DETALHADO: Configurar DNS no Registro.br
Passo a passo com screenshots e explicações
"""

import webbrowser
import time


def main():
    """Guia completo Registro.br"""
    
    print("🎯 GUIA COMPLETO: DNS no Registro.br")
    print("=" * 45)
    print()
    
    print("Vou te guiar EXATAMENTE como configurar o DNS")
    print("Domínio: noticiasontem.com.br")
    print()
    
    input("Pressione ENTER para começar...")
    
    # PASSO 1: Acessar site
    print("\n📋 PASSO 1: ACESSAR O SITE")
    print("=" * 30)
    print("🌐 Abrindo https://registro.br")
    
    try:
        webbrowser.open("https://registro.br")
        print("✅ Site aberto no navegador")
    except:
        print("❌ Abra manualmente: https://registro.br")
    
    print("\n🔍 O QUE VOCÊ DEVE VER:")
    print("• Site azul do Registro.br")
    print("• Menu superior com 'Entrar'")
    print("• Logo do Registro.br")
    
    input("\\nVê o site? Pressione ENTER para continuar...")
    
    # PASSO 2: Login
    print("\\n📋 PASSO 2: FAZER LOGIN")
    print("=" * 30)
    print("🔐 Clique em 'ENTRAR' (canto superior direito)")
    print()
    print("📝 CAMPOS DE LOGIN:")
    print("• CPF: Digite seu CPF (sem pontos/traços)")
    print("• Senha: Digite sua senha")
    print("• Clique em 'Entrar'")
    print()
    print("⚠️ SE NÃO LEMBRA A SENHA:")
    print("• Clique em 'Esqueci minha senha'")
    print("• Digite seu CPF")
    print("• Verifique email/SMS")
    
    input("\\nFez login? Pressione ENTER para continuar...")
    
    # PASSO 3: Meus Domínios
    print("\\n📋 PASSO 3: ACESSAR MEUS DOMÍNIOS")
    print("=" * 30)
    print("🏠 Após login, você verá o painel principal")
    print()
    print("🔍 PROCURE POR:")
    print("• 'Meus Domínios' (menu lateral esquerdo)")
    print("• Ou 'Domínios' (menu superior)")
    print("• Ou link direto na página inicial")
    print()
    print("👆 CLIQUE em 'Meus Domínios'")
    
    input("\\nEntrou em Meus Domínios? Pressione ENTER...")
    
    # PASSO 4: Selecionar domínio
    print("\\n📋 PASSO 4: SELECIONAR O DOMÍNIO")
    print("=" * 30)
    print("📋 VOCÊ DEVE VER UMA LISTA DOS SEUS DOMÍNIOS")
    print()
    print("🎯 PROCURE POR: noticiasontem.com.br")
    print("👆 CLIQUE no domínio 'noticiasontem.com.br'")
    print()
    print("🔍 SE NÃO APARECER:")
    print("• Verifique se está na conta correta")
    print("• Procure em 'Todos os domínios'")
    print("• Use a busca/filtro")
    
    input("\\nClicou no domínio? Pressione ENTER...")
    
    # PASSO 5: Configurar DNS
    print("\\n📋 PASSO 5: ENCONTRAR CONFIGURAÇÃO DNS")
    print("=" * 30)
    print("🔍 AGORA VOCÊ ESTÁ NA PÁGINA DO DOMÍNIO")
    print()
    print("👀 PROCURE POR ESTAS OPÇÕES:")
    print("• 'DNS' (menu lateral)")
    print("• 'Configurar DNS'")
    print("• 'Serviços DNS'")
    print("• 'Zona DNS'")
    print("• 'Name Servers'")
    print()
    print("📍 LOCALIZAÇÃO COMUM:")
    print("• Menu lateral esquerdo")
    print("• Aba 'Serviços'")
    print("• Seção 'Configurações'")
    
    input("\\nEncontrou a opção DNS? Pressione ENTER...")
    
    # PASSO 6: Tipo de DNS
    print("\\n📋 PASSO 6: VERIFICAR TIPO DE DNS")
    print("=" * 30)
    print("⚙️ VOCÊ PODE VER DUAS OPÇÕES:")
    print()
    print("1️⃣ 'DNS do Registro.br' (GRATUITO)")
    print("   ✅ Use esta opção!")
    print("   👆 Clique em 'Configurar' ou 'Gerenciar'")
    print()
    print("2️⃣ 'DNS Externo' ou 'Delegar DNS'")
    print("   ❌ NÃO use esta opção agora")
    print()
    print("🎯 OBJETIVO: Usar o DNS do próprio Registro.br")
    
    input("\\nEscolheu DNS do Registro.br? Pressione ENTER...")
    
    # PASSO 7: Adicionar registros
    print("\\n📋 PASSO 7: ADICIONAR REGISTROS DNS")
    print("=" * 30)
    print("🔧 AGORA VOCÊ ESTÁ NA TELA DE CONFIGURAÇÃO DNS")
    print()
    print("🔍 PROCURE POR:")
    print("• Botão 'Adicionar Registro'")
    print("• 'Novo Registro'")
    print("• '+' (Adicionar)")
    print("• 'Criar Registro'")
    print()
    print("📋 VOCÊ VAI ADICIONAR 2 REGISTROS:")
    print("1. Domínio principal → CloudFront")
    print("2. WWW → CloudFront")
    
    input("\\nVê a opção de adicionar registro? ENTER...")
    
    # PASSO 8: Registro 1
    print("\\n📋 PASSO 8: REGISTRO 1 (Domínio Principal)")
    print("=" * 30)
    print("👆 CLIQUE em 'Adicionar Registro' ou similar")
    print()
    print("📝 PREENCHA OS CAMPOS:")
    print("🔹 Nome/Host/Subdomínio:")
    print("   → Digite: @ (arroba)")
    print("   → Ou deixe VAZIO")
    print("   → Ou digite: noticiasontem.com.br")
    print()
    print("🔹 Tipo:")
    print("   → Selecione: CNAME")
    print("   → Se não tiver CNAME, use A")
    print()
    print("🔹 Valor/Destino/Aponta para:")
    print("   → Digite: d3q2d002qno2yn.cloudfront.net")
    print()
    print("🔹 TTL (se aparecer):")
    print("   → Digite: 300")
    print("   → Ou deixe padrão")
    print()
    print("💾 CLIQUE EM 'SALVAR' ou 'ADICIONAR'")
    
    input("\\nAdicionou o REGISTRO 1? Pressione ENTER...")
    
    # PASSO 9: Registro 2
    print("\\n📋 PASSO 9: REGISTRO 2 (WWW)")
    print("=" * 30)
    print("👆 CLIQUE NOVAMENTE em 'Adicionar Registro'")
    print()
    print("📝 PREENCHA OS CAMPOS:")
    print("🔹 Nome/Host/Subdomínio:")
    print("   → Digite: www")
    print()
    print("🔹 Tipo:")
    print("   → Selecione: CNAME")
    print()
    print("🔹 Valor/Destino/Aponta para:")
    print("   → Digite: d3q2d002qno2yn.cloudfront.net")
    print()
    print("🔹 TTL (se aparecer):")
    print("   → Digite: 300")
    print()
    print("💾 CLIQUE EM 'SALVAR' ou 'ADICIONAR'")
    
    input("\\nAdicionou o REGISTRO 2? Pressione ENTER...")
    
    # PASSO 10: Confirmar
    print("\\n📋 PASSO 10: CONFIRMAR ALTERAÇÕES")
    print("=" * 30)
    print("✅ VERIFIQUE SE OS 2 REGISTROS APARECEM:")
    print()
    print("📋 REGISTRO 1:")
    print("   Nome: @ (ou vazio)")
    print("   Tipo: CNAME")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")
    print()
    print("📋 REGISTRO 2:")
    print("   Nome: www")
    print("   Tipo: CNAME")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")
    print()
    print("💾 SE TIVER BOTÃO 'APLICAR' OU 'CONFIRMAR':")
    print("   → CLIQUE NELE!")
    
    input("\\nConfirmou as alterações? Pressione ENTER...")
    
    # PASSO 11: Aguardar
    print("\\n📋 PASSO 11: AGUARDAR PROPAGAÇÃO")
    print("=" * 30)
    print("⏰ DNS DEMORA PARA PROPAGAR:")
    print("• Mínimo: 5 minutos")
    print("• Normal: 15-30 minutos")
    print("• Máximo: 24 horas")
    print()
    print("🔄 VAMOS TESTAR AGORA:")
    
    # Teste
    print("\\n🧪 TESTANDO DNS...")
    import subprocess
    try:
        result = subprocess.run(['nslookup', 'noticiasontem.com.br'], 
                              capture_output=True, text=True, timeout=10)
        
        if 'cloudfront' in result.stdout.lower():
            print("🎉 SUCESSO! DNS JÁ CONFIGURADO!")
            print("✅ Resultado encontrado: CloudFront")
            print("🌐 Teste: http://noticiasontem.com.br")
        elif 'timeout' in result.stderr.lower():
            print("⏳ DNS ainda não configurado")
            print("🔄 Execute o monitor: python scripts/monitor_dns.py")
        else:
            print("🔄 DNS propagando...")
            print("📋 Resultado atual:")
            print(result.stdout)
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        print("🔄 Teste manual: nslookup noticiasontem.com.br")
    
    print("\\n🎯 PRÓXIMOS PASSOS:")
    print("1. Aguarde propagação DNS (5-30 min)")
    print("2. Execute: python scripts/monitor_dns.py")
    print("3. Teste: http://noticiasontem.com.br")
    print("4. Me avise quando estiver funcionando!")
    
    print("\\n📞 SE TIVER PROBLEMAS:")
    print("• Screenshots da tela")
    print("• Qual erro apareceu")
    print("• Em que passo travou")


if __name__ == "__main__":
    main()
