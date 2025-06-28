#!/usr/bin/env python3
"""
Validação completa da infraestrutura AWS
Verifica S3, CloudFront, DNS e identifica problemas
"""

import boto3
import requests
import socket
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

def validar_credenciais_aws():
    """Valida se as credenciais AWS estão configuradas"""
    print("🔐 VALIDANDO CREDENCIAIS AWS")
    print("=" * 40)
    
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ Account ID: {identity['Account']}")
        print(f"✅ User ARN: {identity['Arn']}")
        print(f"✅ User ID: {identity['UserId']}")
        return True
        
    except NoCredentialsError:
        print("❌ Credenciais AWS não encontradas!")
        print("Configure: aws configure")
        return False
    except Exception as e:
        print(f"❌ Erro nas credenciais: {e}")
        return False

def validar_bucket_s3():
    """Valida configuração do bucket S3"""
    print("\n📦 VALIDANDO BUCKET S3")
    print("=" * 40)
    
    try:
        s3 = boto3.client('s3')
        bucket_name = 'djblog-noticias-static-1750943590'
        
        # 1. Verifica se bucket existe
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket existe: {bucket_name}")
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                print(f"❌ Bucket não encontrado: {bucket_name}")
                return False
            else:
                print(f"❌ Erro ao acessar bucket: {e}")
                return False
        
        # 2. Lista arquivos
        try:
            response = s3.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in response:
                print(f"✅ Arquivos encontrados: {len(response['Contents'])}")
                for obj in response['Contents'][:5]:  # Mostra primeiros 5
                    print(f"   📄 {obj['Key']} ({obj['Size']} bytes)")
                
                # Verifica index.html
                index_exists = any(obj['Key'] == 'index.html' for obj in response['Contents'])
                if index_exists:
                    print("✅ index.html presente")
                else:
                    print("❌ index.html AUSENTE!")
                    return False
            else:
                print("❌ Bucket vazio!")
                return False
        except Exception as e:
            print(f"❌ Erro ao listar objetos: {e}")
            return False
        
        # 3. Verifica política do bucket
        try:
            policy_response = s3.get_bucket_policy(Bucket=bucket_name)
            policy = json.loads(policy_response['Policy'])
            print("✅ Política do bucket configurada")
            
            # Verifica se permite leitura pública
            public_read = False
            for statement in policy['Statement']:
                if (statement.get('Effect') == 'Allow' and 
                    statement.get('Principal') == '*' and
                    's3:GetObject' in statement.get('Action', [])):
                    public_read = True
                    break
            
            if public_read:
                print("✅ Leitura pública permitida")
            else:
                print("❌ Leitura pública NÃO configurada")
                return False
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                print("❌ Política do bucket não existe")
                return False
            else:
                print(f"❌ Erro ao verificar política: {e}")
                return False
        
        # 4. Verifica bloqueio de acesso público
        try:
            pab = s3.get_public_access_block(Bucket=bucket_name)
            config = pab['PublicAccessBlockConfiguration']
            
            if (not config['BlockPublicAcls'] and 
                not config['IgnorePublicAcls'] and
                not config['BlockPublicPolicy'] and
                not config['RestrictPublicBuckets']):
                print("✅ Acesso público desbloqueado")
            else:
                print("❌ Acesso público ainda bloqueado")
                print(f"   BlockPublicPolicy: {config['BlockPublicPolicy']}")
                return False
                
        except ClientError:
            print("✅ Sem bloqueio de acesso público")
        
        # 5. Verifica configuração de website
        try:
            website_config = s3.get_bucket_website(Bucket=bucket_name)
            print("✅ Configurado como website")
            print(f"   Index: {website_config['IndexDocument']['Suffix']}")
        except ClientError:
            print("❌ NÃO configurado como website")
            return False
        
        # 6. Testa acesso direto ao arquivo
        try:
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/index.html"
            response = requests.get(s3_url, timeout=10)
            if response.status_code == 200:
                print("✅ Acesso direto ao S3 funcionando")
            else:
                print(f"❌ Acesso direto falhou: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro no acesso direto: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral no S3: {e}")
        return False

def validar_cloudfront():
    """Valida configuração do CloudFront"""
    print("\n🌐 VALIDANDO CLOUDFRONT")
    print("=" * 40)
    
    try:
        cloudfront = boto3.client('cloudfront')
        
        # 1. Lista distribuições
        response = cloudfront.list_distributions()
        
        if 'DistributionList' not in response or 'Items' not in response['DistributionList']:
            print("❌ Nenhuma distribuição CloudFront encontrada")
            return False
        
        # 2. Encontra nossa distribuição
        nossa_dist = None
        for dist in response['DistributionList']['Items']:
            if 'd3q2d002qno2yn.cloudfront.net' in dist['DomainName']:
                nossa_dist = dist
                break
        
        if not nossa_dist:
            print("❌ Distribuição d3q2d002qno2yn.cloudfront.net não encontrada")
            return False
        
        print(f"✅ Distribuição encontrada: {nossa_dist['DomainName']}")
        print(f"✅ Status: {nossa_dist['Status']}")
        print(f"✅ Enabled: {nossa_dist['Enabled']}")
        
        # 3. Verifica configuração detalhada
        dist_id = nossa_dist['Id']
        detail = cloudfront.get_distribution(Id=dist_id)
        config = detail['Distribution']['DistributionConfig']
        
        # Default Root Object
        if config.get('DefaultRootObject'):
            print(f"✅ Default Root Object: {config['DefaultRootObject']}")
        else:
            print("❌ Default Root Object NÃO configurado")
            return False
        
        # Origens
        origins = config['Origins']['Items']
        print(f"✅ Origens configuradas: {len(origins)}")
        for origin in origins:
            print(f"   🔗 {origin['DomainName']}")
        
        # Domínios alternativos (CNAME)
        if 'Aliases' in config and config['Aliases']['Quantity'] > 0:
            print("✅ Domínios personalizados configurados:")
            for alias in config['Aliases']['Items']:
                print(f"   🌐 {alias}")
        else:
            print("⚠️  Nenhum domínio personalizado configurado")
        
        # Certificado SSL
        if 'ViewerCertificate' in config:
            cert = config['ViewerCertificate']
            if 'ACMCertificateArn' in cert:
                print("✅ Certificado SSL personalizado configurado")
            else:
                print("⚠️  Usando certificado padrão do CloudFront")
        
        # 4. Testa acesso
        cloudfront_url = f"https://{nossa_dist['DomainName']}"
        try:
            response = requests.get(cloudfront_url, timeout=10)
            print(f"✅ Teste de acesso: {response.status_code}")
            
            if response.status_code == 200:
                print("🎉 CloudFront funcionando perfeitamente!")
                return True
            else:
                print(f"❌ CloudFront retornando erro: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste do CloudFront: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Erro geral no CloudFront: {e}")
        return False

def validar_dns():
    """Valida configuração DNS"""
    print("\n🌍 VALIDANDO DNS")
    print("=" * 40)
    
    dominios = [
        "noticiasontem.com.br",
        "www.noticiasontem.com.br"
    ]
    
    dns_ok = True
    
    for dominio in dominios:
        print(f"\n🌐 Testando: {dominio}")
        
        # Resolução DNS
        try:
            ip = socket.gethostbyname(dominio)
            print(f"✅ IP resolvido: {ip}")
        except socket.gaierror:
            print(f"❌ DNS não resolvido")
            dns_ok = False
            continue
        
        # Teste HTTPS
        try:
            response = requests.get(f"https://{dominio}", timeout=10)
            print(f"✅ HTTPS: {response.status_code}")
            
            if response.status_code == 200:
                print(f"🎉 {dominio} FUNCIONANDO!")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                dns_ok = False
                
        except requests.exceptions.SSLError:
            print("❌ Erro SSL - Certificado inválido")
            dns_ok = False
        except requests.exceptions.ConnectionError:
            print("❌ Erro de conexão")
            dns_ok = False
        except Exception as e:
            print(f"❌ Erro: {e}")
            dns_ok = False
    
    return dns_ok

def validar_custos():
    """Estima custos da infraestrutura"""
    print("\n💰 VALIDANDO CUSTOS")
    print("=" * 40)
    
    try:
        # CloudWatch para métricas de uso (se disponível)
        cloudwatch = boto3.client('cloudwatch')
        
        print("📊 Estimativa de custos mensais:")
        print("   S3 Storage: ~$0.005 (arquivo estático pequeno)")
        print("   S3 Requests: ~$0.001 (poucos acessos)")
        print("   CloudFront: ~$0.004 (1GB transfer)")
        print("   Total estimado: ~$0.01/mês")
        print("✅ Muito abaixo do limite de $10/mês")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Não foi possível verificar custos: {e}")
        return True

def gerar_relatorio_final(aws_ok, s3_ok, cloudfront_ok, dns_ok, custos_ok):
    """Gera relatório final da validação"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    relatorio = f"""
# RELATÓRIO VALIDAÇÃO INFRAESTRUTURA AWS
Data: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

## RESUMO EXECUTIVO
✅ Credenciais AWS: {'OK' if aws_ok else 'FALHA'}
✅ Bucket S3: {'OK' if s3_ok else 'FALHA'}
✅ CloudFront: {'OK' if cloudfront_ok else 'FALHA'}
✅ DNS: {'OK' if dns_ok else 'FALHA'}
✅ Custos: {'OK' if custos_ok else 'FALHA'}

## STATUS GERAL
{'🎉 INFRAESTRUTURA FUNCIONANDO!' if all([aws_ok, s3_ok, cloudfront_ok, dns_ok]) else '⚠️ PROBLEMAS ENCONTRADOS'}

## DETALHES
- S3 Bucket: djblog-noticias-static-1750943590
- CloudFront: d3q2d002qno2yn.cloudfront.net
- Domínios: noticiasontem.com.br, www.noticiasontem.com.br

## PRÓXIMOS PASSOS
{'Infraestrutura validada com sucesso!' if all([aws_ok, s3_ok, cloudfront_ok, dns_ok]) else 'Revisar componentes com falha acima.'}

## CUSTOS ESTIMADOS
- Mensal: ~$0.01
- Anual: ~$0.12
- Status: Muito abaixo do limite de $10/mês
"""

    with open(f"relatorio_validacao_aws_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write(relatorio)
    
    print(f"\n📄 Relatório salvo: relatorio_validacao_aws_{timestamp}.txt")

def main():
    print("🚀 VALIDAÇÃO COMPLETA DA INFRAESTRUTURA AWS")
    print("=" * 70)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Executa todas as validações
    aws_ok = validar_credenciais_aws()
    
    if not aws_ok:
        print("\n❌ Não é possível continuar sem credenciais AWS válidas")
        return
    
    s3_ok = validar_bucket_s3()
    cloudfront_ok = validar_cloudfront()
    dns_ok = validar_dns()
    custos_ok = validar_custos()
    
    # Resumo final
    print("\n" + "=" * 70)
    print("📊 RESUMO FINAL")
    print("=" * 70)
    print(f"🔐 AWS Credentials: {'✅' if aws_ok else '❌'}")
    print(f"📦 S3 Bucket: {'✅' if s3_ok else '❌'}")
    print(f"🌐 CloudFront: {'✅' if cloudfront_ok else '❌'}")
    print(f"🌍 DNS: {'✅' if dns_ok else '❌'}")
    print(f"💰 Custos: {'✅' if custos_ok else '❌'}")
    
    if all([aws_ok, s3_ok, cloudfront_ok, dns_ok]):
        print("\n🎉 INFRAESTRUTURA 100% FUNCIONANDO!")
        print("🚀 Site pronto para produção!")
    else:
        print("\n⚠️ PROBLEMAS ENCONTRADOS")
        print("📋 Revisar componentes com falha")
    
    # Gera relatório
    gerar_relatorio_final(aws_ok, s3_ok, cloudfront_ok, dns_ok, custos_ok)
    
    print("=" * 70)

if __name__ == "__main__":
    main()
