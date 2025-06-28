#!/usr/bin/env python3
"""
Obtém registros DNS necessários para validação do certificado SSL
"""

import boto3
import json
from datetime import datetime

def obter_registros_validacao_ssl():
    """Obtém registros DNS para validação do certificado"""
    print("🔒 REGISTROS DNS PARA VALIDAÇÃO SSL")
    print("=" * 50)
    
    try:
        acm = boto3.client('acm', region_name='us-east-1')
        
        # Lista certificados
        response = acm.list_certificates()
        
        for cert in response['CertificateSummaryList']:
            if 'noticiasontem.com.br' in cert['DomainName']:
                cert_arn = cert['CertificateArn']
                
                # Obtém detalhes do certificado
                details = acm.describe_certificate(CertificateArn=cert_arn)
                certificate = details['Certificate']
                
                print(f"📋 Certificado: {cert['DomainName']}")
                print(f"📋 Status: {certificate['Status']}")
                print(f"📋 ARN: {cert_arn}")
                print()
                
                if 'DomainValidationOptions' in certificate:
                    print("🎯 REGISTROS DNS PARA ADICIONAR NO REGISTRO.BR:")
                    print("=" * 60)
                    
                    for i, validation in enumerate(certificate['DomainValidationOptions'], 1):
                        print(f"\n🔹 REGISTRO {i} - {validation['DomainName']}:")
                        
                        if 'ResourceRecord' in validation:
                            record = validation['ResourceRecord']
                            print(f"   Nome: {record['Name']}")
                            print(f"   Tipo: {record['Type']}")
                            print(f"   Valor: {record['Value']}")
                        else:
                            print("   ⏳ Aguardando geração dos registros...")
                
                # Salva em arquivo para referência
                config_content = f"""
REGISTROS DNS PARA VALIDAÇÃO SSL - REGISTRO.BR
==============================================
Data: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
Certificado: {cert['DomainName']}
Status: {certificate['Status']}

REGISTROS PARA ADICIONAR:
========================
"""
                
                if 'DomainValidationOptions' in certificate:
                    for i, validation in enumerate(certificate['DomainValidationOptions'], 1):
                        config_content += f"\nREGISTRO {i} - {validation['DomainName']}:\n"
                        if 'ResourceRecord' in validation:
                            record = validation['ResourceRecord']
                            config_content += f"Nome: {record['Name']}\n"
                            config_content += f"Tipo: {record['Type']}\n"
                            config_content += f"Valor: {record['Value']}\n"
                            config_content += f"TTL: 300\n"
                
                config_content += f"""
INSTRUÇÕES:
==========
1. Acesse: painel.registro.br
2. Vá em: DNS/Zona de DNS
3. Adicione os registros CNAME acima
4. Aguarde 5-30 minutos para validação
5. Execute: python scripts/configurar_ssl_dominio.py

APÓS VALIDAÇÃO:
==============
- Certificado ficará com status ISSUED
- CloudFront será configurado automaticamente
- Site funcionará com HTTPS
"""

                with open("registros_validacao_ssl.txt", "w", encoding="utf-8") as f:
                    f.write(config_content)
                
                print(f"\n📄 Instruções salvas em: registros_validacao_ssl.txt")
                break
        
    except Exception as e:
        print(f"❌ Erro ao obter registros: {e}")

def main():
    print("🔍 VERIFICAÇÃO REGISTROS VALIDAÇÃO SSL")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    obter_registros_validacao_ssl()
    
    print("\n" + "=" * 60)
    print("📞 PRÓXIMOS PASSOS:")
    print("1. Adicione os registros CNAME no painel do Registro.br")
    print("2. Aguarde 5-30 minutos")
    print("3. Execute: python scripts/configurar_ssl_dominio.py")
    print("4. CloudFront será configurado automaticamente")
    print("=" * 60)

if __name__ == "__main__":
    main()
