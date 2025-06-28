#!/usr/bin/env python3
"""
Configuração de domínio personalizado no CloudFront
Adiciona domínios personalizados e certificado SSL
"""

import boto3
import json
import time
from datetime import datetime

def obter_certificado_ssl():
    """Verifica ou solicita certificado SSL"""
    print("🔒 VERIFICANDO CERTIFICADO SSL")
    print("=" * 40)
    
    try:
        acm = boto3.client('acm', region_name='us-east-1')  # ACM deve ser us-east-1 para CloudFront
        
        # Lista certificados
        response = acm.list_certificates()
        certificados = response['CertificateSummaryList']
        
        # Procura certificado para nosso domínio
        nosso_cert = None
        for cert in certificados:
            if 'noticiasontem.com.br' in cert['DomainName']:
                nosso_cert = cert
                break
        
        if nosso_cert:
            print(f"✅ Certificado encontrado: {nosso_cert['DomainName']}")
            print(f"✅ ARN: {nosso_cert['CertificateArn']}")
            print(f"✅ Status: {nosso_cert['Status']}")
            return nosso_cert['CertificateArn']
        else:
            print("❌ Certificado não encontrado")
            print("🔧 Solicitando novo certificado...")
            return solicitar_certificado_ssl()
            
    except Exception as e:
        print(f"❌ Erro ao verificar certificados: {e}")
        return None

def solicitar_certificado_ssl():
    """Solicita certificado SSL para o domínio"""
    print("\n🔒 SOLICITANDO CERTIFICADO SSL")
    print("=" * 40)
    
    try:
        acm = boto3.client('acm', region_name='us-east-1')
        
        # Solicita certificado para domínio e www
        response = acm.request_certificate(
            DomainName='noticiasontem.com.br',
            SubjectAlternativeNames=['www.noticiasontem.com.br'],
            ValidationMethod='DNS',
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'noticiasontem.com.br'
                },
                {
                    'Key': 'Project',
                    'Value': 'DJBlog'
                }
            ]
        )
        
        cert_arn = response['CertificateArn']
        print(f"✅ Certificado solicitado: {cert_arn}")
        
        # Aguarda detalhes do certificado
        print("⏳ Aguardando detalhes de validação...")
        time.sleep(5)
        
        # Obtém registros DNS necessários para validação
        cert_details = acm.describe_certificate(CertificateArn=cert_arn)
        
        print("\n📋 REGISTROS DNS PARA VALIDAÇÃO:")
        print("=" * 50)
        
        if 'DomainValidationOptions' in cert_details['Certificate']:
            for validation in cert_details['Certificate']['DomainValidationOptions']:
                if 'ResourceRecord' in validation:
                    record = validation['ResourceRecord']
                    print(f"\n🔹 Domínio: {validation['DomainName']}")
                    print(f"   Nome: {record['Name']}")
                    print(f"   Tipo: {record['Type']}")
                    print(f"   Valor: {record['Value']}")
        
        print("\n⚠️  IMPORTANTE:")
        print("1. Adicione os registros DNS acima no painel do Registro.br")
        print("2. Aguarde a validação (pode levar até 30 minutos)")
        print("3. Execute este script novamente após validação")
        
        return cert_arn
        
    except Exception as e:
        print(f"❌ Erro ao solicitar certificado: {e}")
        return None

def configurar_cloudfront_dominio(cert_arn):
    """Configura domínio personalizado no CloudFront"""
    print(f"\n🌐 CONFIGURANDO CLOUDFRONT COM DOMÍNIO PERSONALIZADO")
    print("=" * 60)
    
    try:
        cloudfront = boto3.client('cloudfront')
        
        # Encontra nossa distribuição
        response = cloudfront.list_distributions()
        nossa_dist = None
        
        for dist in response['DistributionList']['Items']:
            if 'd3q2d002qno2yn.cloudfront.net' in dist['DomainName']:
                nossa_dist = dist
                break
        
        if not nossa_dist:
            print("❌ Distribuição CloudFront não encontrada")
            return False
        
        dist_id = nossa_dist['Id']
        print(f"✅ Distribuição encontrada: {dist_id}")
        
        # Obtém configuração atual
        config_response = cloudfront.get_distribution_config(Id=dist_id)
        config = config_response['DistributionConfig']
        etag = config_response['ETag']
        
        print("🔧 Atualizando configuração...")
        
        # Adiciona domínios personalizados
        config['Aliases'] = {
            'Quantity': 2,
            'Items': ['noticiasontem.com.br', 'www.noticiasontem.com.br']
        }
        
        # Configura certificado SSL
        config['ViewerCertificate'] = {
            'ACMCertificateArn': cert_arn,
            'SSLSupportMethod': 'sni-only',
            'MinimumProtocolVersion': 'TLSv1.2_2021',
            'CertificateSource': 'acm'
        }
        
        # Atualiza a distribuição
        cloudfront.update_distribution(
            DistributionConfig=config,
            Id=dist_id,
            IfMatch=etag
        )
        
        print("✅ CloudFront atualizado com domínio personalizado!")
        print("⏳ Aguarde 10-15 minutos para deploy...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar CloudFront: {e}")
        return False

def testar_configuracao_final():
    """Testa configuração final com HTTPS"""
    print(f"\n🧪 TESTANDO CONFIGURAÇÃO FINAL")
    print("=" * 40)
    
    import requests
    
    dominios = [
        "https://noticiasontem.com.br",
        "https://www.noticiasontem.com.br"
    ]
    
    for url in dominios:
        print(f"\n🌐 Testando: {url}")
        try:
            response = requests.get(url, timeout=10, verify=True)
            print(f"✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"🎉 {url} FUNCIONANDO COM SSL!")
            else:
                print(f"⚠️  Status inesperado: {response.status_code}")
                
        except requests.exceptions.SSLError as e:
            print(f"❌ Erro SSL: {e}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Erro de conexão - aguarde propagação")
        except Exception as e:
            print(f"❌ Erro: {e}")

def main():
    print("🚀 CONFIGURAÇÃO DOMÍNIO PERSONALIZADO + SSL")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # 1. Verifica/solicita certificado SSL
    cert_arn = obter_certificado_ssl()
    
    if not cert_arn:
        print("\n❌ Não foi possível obter certificado SSL")
        return
    
    # 2. Verifica se certificado está validado
    print(f"\n🔍 Verificando status do certificado...")
    try:
        acm = boto3.client('acm', region_name='us-east-1')
        cert_details = acm.describe_certificate(CertificateArn=cert_arn)
        status = cert_details['Certificate']['Status']
        
        print(f"📋 Status do certificado: {status}")
        
        if status == 'ISSUED':
            print("✅ Certificado validado e emitido!")
            
            # 3. Configura CloudFront
            if configurar_cloudfront_dominio(cert_arn):
                print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
                print("⏳ Aguarde 10-15 minutos para propagação")
                
                # 4. Testa configuração
                time.sleep(10)  # Aguarda um pouco
                testar_configuracao_final()
            
        elif status == 'PENDING_VALIDATION':
            print("⏳ Certificado aguardando validação DNS")
            print("📋 Adicione os registros DNS mostrados acima")
            
        else:
            print(f"⚠️  Status inesperado: {status}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar certificado: {e}")
    
    print("\n" + "=" * 70)
    print("📝 RESUMO:")
    print("1. Certificado SSL solicitado/verificado")
    print("2. CloudFront configurado (se certificado válido)")
    print("3. Aguarde propagação para teste final")
    print("=" * 70)

if __name__ == "__main__":
    main()
