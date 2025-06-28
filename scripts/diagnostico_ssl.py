#!/usr/bin/env python3
"""
Diagnóstico completo da validação SSL
"""

import subprocess
import time
from datetime import datetime

def run_nslookup(domain, dns_server="8.8.8.8"):
    """Executa nslookup e retorna o resultado"""
    try:
        result = subprocess.run(
            ['nslookup', domain, dns_server],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout, result.returncode == 0
    except Exception as e:
        return f"Erro: {e}", False

def main():
    print("🔍 DIAGNÓSTICO VALIDAÇÃO SSL")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Registros para verificar
    registros = [
        "_19837e8068f6a4d75e9bdfd772154663.noticiasontem.com.br",
        "_88fe1a2469d7ce78bd80f82750e60fef.www.noticiasontem.com.br"
    ]
    
    valores_esperados = [
        "_a94a255a3c25cba74c95244e79562393.xlfgrmvvlj.acm-validations.aws",
        "_1aa1b9515605c723c3757c748117b9fa.xlfgrmvvlj.acm-validations.aws"
    ]
    
    dns_servers = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
    
    print("🔍 VERIFICANDO PROPAGAÇÃO DOS REGISTROS SSL:")
    print("-" * 60)
    
    for i, registro in enumerate(registros):
        print(f"\n📋 REGISTRO {i+1}: {registro}")
        print(f"📋 Valor esperado: {valores_esperados[i]}")
        print("-" * 40)
        
        encontrado = False
        for dns in dns_servers:
            print(f"🔍 Testando DNS {dns}...")
            output, success = run_nslookup(registro, dns)
            
            if success and "Non-existent domain" not in output:
                print(f"✅ ENCONTRADO em {dns}")
                if valores_esperados[i] in output:
                    print(f"✅ VALOR CORRETO!")
                    encontrado = True
                else:
                    print(f"⚠️ Valor diferente do esperado")
                print(f"📝 Resposta: {output.strip()}")
            else:
                print(f"❌ NÃO ENCONTRADO em {dns}")
        
        if not encontrado:
            print(f"❌ Registro {i+1} ainda não propagou")
        else:
            print(f"✅ Registro {i+1} propagado corretamente")
        print()
    
    print("🔍 VERIFICANDO NAMESERVERS DO DOMÍNIO:")
    print("-" * 60)
    
    # Verificar nameservers
    print("📋 Nameservers atuais:")
    ns_output, ns_success = run_nslookup("noticiasontem.com.br", "8.8.8.8")
    if "nameserver" in ns_output.lower() or "ns" in ns_output.lower():
        print("✅ Nameservers encontrados")
        print(f"📝 {ns_output}")
    else:
        print("❌ Problema com nameservers")
        print(f"📝 {ns_output}")
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DO DIAGNÓSTICO:")
    print("=" * 60)
    print("• Se os registros NÃO foram encontrados:")
    print("  - Verifique se adicionou corretamente no Cloudflare")
    print("  - Aguarde mais tempo (até 30 minutos)")
    print("  - Resolva questão do 'domínio pendente' no Cloudflare")
    print()
    print("• Se os registros foram encontrados:")
    print("  - AWS pode estar demorando para validar")
    print("  - Aguarde mais alguns minutos")
    print("  - Execute: python scripts/configurar_ssl_dominio.py")
    print()
    print("📞 PRÓXIMOS PASSOS:")
    print("1. Resolver 'domínio pendente' no Cloudflare (se necessário)")
    print("2. Aguardar propagação completa")
    print("3. Executar configuração SSL novamente")

if __name__ == "__main__":
    main()
