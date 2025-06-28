#!/usr/bin/env python3
"""
Listar certificados SSL
"""

import boto3

def main():
    try:
        acm = boto3.client('acm', region_name='us-east-1')
        response = acm.list_certificates()
        
        print("🔍 CERTIFICADOS SSL ENCONTRADOS:")
        print("=" * 50)
        
        for cert in response['CertificateSummaryList']:
            domain = cert['DomainName']
            arn = cert['CertificateArn']
            status = cert.get('Status', 'UNKNOWN')
            
            if 'noticiasontem' in domain.lower():
                print(f"📋 Domínio: {domain}")
                print(f"📋 ARN: {arn}")
                print(f"📋 Status: {status}")
                print("-" * 50)
                
        print("✅ Busca concluída")
                
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
