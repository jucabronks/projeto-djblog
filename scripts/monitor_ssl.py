#!/usr/bin/env python3
"""
Monitor de validação SSL - Verifica automaticamente se o certificado foi validado
Parte do projeto DJBlog - Deploy em produção
"""

import boto3
import time
import sys
from datetime import datetime

def main():
    print("🔍 MONITOR DE VALIDAÇÃO SSL")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Configurar cliente ACM
    try:
        acm = boto3.client('acm', region_name='us-east-1')
        print("✅ Conectado à AWS ACM")
    except Exception as e:
        print(f"❌ Erro ao conectar AWS: {e}")
        return
    
    # ARN do certificado
    cert_arn = "arn:aws:acm:us-east-1:317304475005:certificate/be47a77b-fe2c-4446b-b697-b192ab1857c8"
    
    print("🔒 Verificando status do certificado...")
    print()
    
    # Verificar status várias vezes
    for tentativa in range(1, 11):  # 10 tentativas
        try:
            response = acm.describe_certificate(CertificateArn=cert_arn)
            cert = response['Certificate']
            status = cert['Status']
            
            print(f"🔄 Tentativa {tentativa}/10")
            print(f"📋 Status: {status}")
            
            if status == 'ISSUED':
                print("🎉 CERTIFICADO VALIDADO COM SUCESSO!")
                print("✅ SSL está pronto para uso")
                print()
                print("🚀 PRÓXIMOS PASSOS:")
                print("• Execute: python scripts/configurar_ssl_dominio.py")
                print("• O CloudFront será configurado automaticamente")
                print("• Teste: https://noticiasontem.com.br")
                print("• Teste: https://www.noticiasontem.com.br")
                return
            
            elif status == 'PENDING_VALIDATION':
                print("⏳ Ainda aguardando validação DNS...")
                
                # Mostrar registros necessários
                if 'DomainValidationOptions' in cert:
                    print("📋 Registros DNS necessários:")
                    for domain_validation in cert['DomainValidationOptions']:
                        if 'ResourceRecord' in domain_validation:
                            record = domain_validation['ResourceRecord']
                            domain = domain_validation['DomainName']
                            print(f"   • {domain}: {record['Name']} → {record['Value']}")
                
            elif status == 'FAILED':
                print("❌ CERTIFICADO FALHOU NA VALIDAÇÃO")
                print("🔍 Verifique se os registros CNAME estão corretos")
                return
            
            else:
                print(f"🤔 Status desconhecido: {status}")
            
            print(f"⏰ Aguardando 30 segundos... ({tentativa}/10)")
            print("-" * 50)
            
            if tentativa < 10:
                time.sleep(30)  # Aguardar 30 segundos
                
        except Exception as e:
            print(f"❌ Erro ao verificar certificado: {e}")
            break
    
    print()
    print("⏰ MONITORAMENTO FINALIZADO")
    print("📋 Se o certificado ainda não foi validado:")
    print("• Verifique se os registros CNAME estão corretos no Cloudflare")
    print("• Aguarde mais alguns minutos (pode levar até 30 min)")
    print("• Execute novamente: python scripts/monitor_ssl.py")
    print("• Ou execute: python scripts/configurar_ssl_dominio.py")

if __name__ == "__main__":
    main()
