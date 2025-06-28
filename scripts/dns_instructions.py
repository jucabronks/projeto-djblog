#!/usr/bin/env python3
"""
Script para configurar CNAME simples enquanto aguarda certificado SSL
"""

def main():
    """Instruções simplificadas para configurar DNS"""
    
    print("🌐 Configuração DNS para noticiasontem.com.br")
    print("=" * 50)
    
    print("📋 REGISTROS DNS PARA ADICIONAR:")
    print()
    
    print("🔹 REGISTRO 1 (Validação SSL do domínio principal):")
    print("   Nome: _19837e8068f6a4d75e9bdfd772154663.noticiasontem.com.br.")
    print("   Tipo: CNAME")
    print("   Valor: _a94a255a3c25cba74c95244e79562393.xlfgrmvvlj.acm-validations.aws.")
    print()
    
    print("🔹 REGISTRO 2 (Validação SSL do www):")
    print("   Nome: _88fe1a2469d7ce78bd80f82750e60fef.www.noticiasontem.com.br.")
    print("   Tipo: CNAME") 
    print("   Valor: _1aa1b9515605c723c3757c748117b9fa.xlfgrmvvlj.acm-validations.aws.")
    print()
    
    print("🔹 REGISTRO 3 (Apontar domínio para CloudFront):")
    print("   Nome: noticiasontem.com.br")
    print("   Tipo: CNAME")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")
    print()
    
    print("🔹 REGISTRO 4 (Apontar www para CloudFront):")
    print("   Nome: www.noticiasontem.com.br")
    print("   Tipo: CNAME")
    print("   Valor: d3q2d002qno2yn.cloudfront.net")
    print()
    
    print("🎯 PASSOS PARA CONFIGURAR:")
    print("1. Acesse o painel DNS do seu registrador")
    print("2. Adicione os 4 registros CNAME acima")
    print("3. Aguarde 5-10 minutos para propagação")
    print("4. Execute novamente: python scripts/setup_cloudfront_domain.py")
    print()
    
    print("🌐 URLs ATUAIS (já funcionando):")
    print("✅ CloudFront: https://d3q2d002qno2yn.cloudfront.net")
    print("⏳ Seu domínio: https://noticiasontem.com.br (após DNS)")
    print()
    
    print("📞 DÚVIDAS COMUNS:")
    print("Q: Onde configurar DNS?")
    print("A: No painel do registrador onde você comprou o domínio")
    print()
    print("Q: Quanto tempo demora?")
    print("A: 5-15 minutos para propagação DNS")
    print()
    print("Q: Como testar?")
    print("A: Digite nslookup noticiasontem.com.br no cmd")
    

if __name__ == "__main__":
    main()
