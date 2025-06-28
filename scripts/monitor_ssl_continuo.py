#!/usr/bin/env python3
"""
Monitor contínuo de SSL - Verifica automaticamente a validação
"""

import boto3
import subprocess
import time
from datetime import datetime

def test_cname_record(record_name, expected_target, dns_server="8.8.8.8"):
    """Testa se o registro CNAME está propagado globalmente"""
    try:
        result = subprocess.run(
            ['nslookup', record_name, dns_server],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout.lower()
        return expected_target.lower() in output and "non-existent" not in output
    except:
        return False

def check_certificate_status():
    """Verifica status do certificado SSL"""
    try:
        acm = boto3.client('acm', region_name='us-east-1')
        cert_arn = "arn:aws:acm:us-east-1:317304475005:certificate/be47a77b-fe2c-4446b-b697-b192ab1857c8"
        
        response = acm.describe_certificate(CertificateArn=cert_arn)
        return response['Certificate']['Status']
    except:
        return "ERROR"

def main():
    print("🔍 MONITOR CONTÍNUO SSL + DNS")
    print("=" * 50)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Dados dos registros
    records = [
        {
            'name': '_19837e8068f6a4d75e9bdfd772154663.noticiasontem.com.br',
            'target': '_a94a255a3c25cba74c95244e79562393.xlfgrmvvlj.acm-validations.aws'
        },
        {
            'name': '_88fe1a2469d7ce78bd80f82750e60fef.www.noticiasontem.com.br',
            'target': '_1aa1b9515605c723c3757c748117b9fa.xlfgrmvvlj.acm-validations.aws'
        }
    ]
    
    dns_servers = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
    
    for attempt in range(1, 31):  # 30 tentativas (15 minutos)
        print(f"🔄 Verificação {attempt}/30 - {datetime.now().strftime('%H:%M:%S')}")
        
        # Verificar propagação DNS
        dns_ok = 0
        for record in records:
            for dns in dns_servers:
                if test_cname_record(record['name'], record['target'], dns):
                    dns_ok += 1
                    break
        
        # Verificar certificado SSL
        ssl_status = check_certificate_status()
        
        print(f"📊 DNS propagado: {dns_ok}/2 registros")
        print(f"🔒 SSL Status: {ssl_status}")
        
        if ssl_status == "ISSUED":
            print("🎉 CERTIFICADO SSL VALIDADO COM SUCESSO!")
            print("✅ Pode executar: python scripts/configurar_ssl_dominio.py")
            print("🚀 Site funcionará com HTTPS!")
            break
        
        if dns_ok == 2:
            print("✅ DNS totalmente propagado!")
            if ssl_status == "PENDING_VALIDATION":
                print("⏳ Aguardando AWS validar...")
            elif ssl_status == "FAILED":
                print("❌ Certificado falhou - verifique configuração")
                break
        else:
            print("⏳ Aguardando propagação DNS global...")
        
        if attempt < 30:
            print("⏰ Aguardando 30 segundos...")
            print("-" * 50)
            time.sleep(30)
    
    print()
    print("📋 RESUMO FINAL:")
    print("• Se DNS propagou mas SSL ainda pendente: AWS pode demorar até 1h")
    print("• Se DNS não propagou: Aguarde mais tempo ou verifique Cloudflare")
    print("• Execute novamente: python scripts/monitor_ssl_continuo.py")

if __name__ == "__main__":
    main()
