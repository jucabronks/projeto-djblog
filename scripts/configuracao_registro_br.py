#!/usr/bin/env python3
"""
Guia específico para configuração DNS no Registro.br
Considera as limitações: não aceita "@", "*" e SRV
"""

import socket
import subprocess
import requests
from datetime import datetime

def obter_ip_cloudfront():
    """Obtém o IP do CloudFront"""
    print("🔍 OBTENDO IP DO CLOUDFRONT")
    print("=" * 40)
    
    try:
        # Resolve o IP do CloudFront
        cloudfront_domain = "d3q2d002qno2yn.cloudfront.net"
        ip = socket.gethostbyname(cloudfront_domain)
        print(f"✅ IP do CloudFront: {ip}")
        return ip
    except Exception as e:
        print(f"❌ Erro ao obter IP: {e}")
        return None

def gerar_configuracao_dns():
    """Gera configuração DNS específica para Registro.br"""
    
    ip_cloudfront = obter_ip_cloudfront()
    
    if not ip_cloudfront:
        print("❌ Não foi possível obter o IP do CloudFront")
        return
    
    print(f"\n📋 CONFIGURAÇÃO DNS PARA REGISTRO.BR")
    print("=" * 50)
    print(f"⏰ Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    print("🎯 REGISTROS PARA ADICIONAR NO PAINEL:")
    print("=" * 50)
    
    print("🔹 REGISTRO 1 - DOMÍNIO RAIZ:")
    print(f"   Nome: [DEIXAR VAZIO ou noticiasontem.com.br]")
    print(f"   Tipo: A")
    print(f"   Valor: {ip_cloudfront}")
    print(f"   TTL: 3600")
    print()
    
    print("🔹 REGISTRO 2 - SUBDOMÍNIO WWW:")
    print(f"   Nome: www")
    print(f"   Tipo: CNAME")
    print(f"   Valor: d3q2d002qno2yn.cloudfront.net")
    print(f"   TTL: 3600")
    print()
    
    print("⚠️  REGRAS DO REGISTRO.BR:")
    print("• NÃO usar '@' ou '*' no campo Nome")
    print("• Para domínio raiz: deixar Nome VAZIO")
    print("• Usar tipo A (IPv4) para domínio raiz")
    print("• Usar tipo CNAME para subdomínios")
    print("• TTL recomendado: 3600 (1 hora)")
    print()
    
    return ip_cloudfront

def testar_configuracao_atual():
    """Testa a configuração DNS atual"""
    print("🧪 TESTANDO CONFIGURAÇÃO ATUAL")
    print("=" * 40)
    
    dominios = [
        "noticiasontem.com.br",
        "www.noticiasontem.com.br"
    ]
    
    for dominio in dominios:
        print(f"\n🌐 Testando: {dominio}")
        try:
            ip = socket.gethostbyname(dominio)
            print(f"✅ IP: {ip}")
            
            # Testa acesso HTTP
            try:
                response = requests.get(f"https://{dominio}", timeout=5)
                print(f"✅ HTTPS: {response.status_code}")
                if response.status_code == 200:
                    print(f"🎉 {dominio} FUNCIONANDO!")
            except:
                print(f"❌ HTTPS: Falha na conexão")
                
        except socket.gaierror:
            print(f"❌ DNS: Não resolvido")

def criar_arquivo_configuracao(ip_cloudfront):
    """Cria arquivo com a configuração para referência"""
    config_content = f"""
CONFIGURAÇÃO DNS - REGISTRO.BR
==============================
Data: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
CloudFront IP: {ip_cloudfront}

REGISTROS PARA ADICIONAR:
========================

1. DOMÍNIO RAIZ (noticiasontem.com.br):
   Nome: [VAZIO]
   Tipo: A  
   Valor: {ip_cloudfront}
   TTL: 3600

2. SUBDOMÍNIO WWW:
   Nome: www
   Tipo: CNAME
   Valor: d3q2d002qno2yn.cloudfront.net
   TTL: 3600

PASSO A PASSO:
=============
1. Acesse: painel.registro.br
2. Login com CPF e senha
3. Meus Domínios → noticiasontem.com.br
4. DNS/Zona de DNS
5. Adicionar novos registros conforme acima
6. Salvar alterações
7. Aguardar 10-15 minutos para propagação

VERIFICAÇÃO:
===========
- Execute: ipconfig /flushdns
- Teste: https://noticiasontem.com.br
- Teste: https://www.noticiasontem.com.br

STATUS AWS:
==========
✅ S3: Configurado e funcionando
✅ CloudFront: Funcionando (200 OK)
✅ Site: https://d3q2d002qno2yn.cloudfront.net
"""

    with open("configuracao_dns_registro_br.txt", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print(f"📄 Configuração salva em: configuracao_dns_registro_br.txt")

def main():
    print("🌐 CONFIGURAÇÃO DNS - REGISTRO.BR")
    print("=" * 60)
    print("Guia específico para as regras do Registro.br")
    print()
    
    # Obtém IP e gera configuração
    ip_cloudfront = gerar_configuracao_dns()
    
    if ip_cloudfront:
        # Cria arquivo de referência
        criar_arquivo_configuracao(ip_cloudfront)
        
        print("🔧 DICAS IMPORTANTES:")
        print("• Use tipo A para domínio raiz (obrigatório no Registro.br)")
        print("• Use CNAME apenas para subdomínios (www)")
        print("• Campo Nome vazio = domínio raiz")
        print("• Aguarde propagação após salvar")
        print()
        
        # Testa configuração atual
        testar_configuracao_atual()
        
        print("\n" + "=" * 60)
        print("📞 PRÓXIMOS PASSOS:")
        print("1. Configure os registros DNS no painel")
        print("2. Aguarde 10-15 minutos")
        print("3. Execute: python scripts/testar_dns.py")
        print("4. Teste os domínios no navegador")
        print("=" * 60)

if __name__ == "__main__":
    main()
