#!/usr/bin/env python3
"""
Script para corrigir erro 403 do CloudFront
Verifica e corrige configurações do S3 e CloudFront
"""

import boto3
import json
import requests
import os
from datetime import datetime

def verificar_s3_bucket():
    """Verifica configurações do bucket S3"""
    print("🔍 VERIFICANDO BUCKET S3")
    print("=" * 40)
    
    try:
        s3 = boto3.client('s3')
        bucket_name = 'djblog-noticias-static-1750943590'
        
        # Lista objetos no bucket
        print("📁 Listando arquivos no bucket...")
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in response:
            print(f"✅ Encontrados {len(response['Contents'])} arquivos:")
            for obj in response['Contents'][:10]:  # Mostra apenas os primeiros 10
                print(f"   📄 {obj['Key']}")
                
            # Verifica se index.html existe
            index_exists = any(obj['Key'] == 'index.html' for obj in response['Contents'])
            if index_exists:
                print("✅ index.html encontrado!")
            else:
                print("❌ index.html NÃO encontrado!")
                return False
        else:
            print("❌ Bucket vazio!")
            return False
            
        # Verifica política do bucket
        print("\n🔒 Verificando política do bucket...")
        try:
            policy_response = s3.get_bucket_policy(Bucket=bucket_name)
            print("✅ Política do bucket existe")
        except s3.exceptions.NoSuchBucketPolicy:
            print("❌ Bucket não tem política pública!")
            return False
            
        # Verifica website configuration
        print("\n🌐 Verificando configuração de website...")
        try:
            website_config = s3.get_bucket_website(Bucket=bucket_name)
            print("✅ Configuração de website existe")
            if 'IndexDocument' in website_config:
                print(f"✅ Documento índice: {website_config['IndexDocument']['Suffix']}")
        except Exception:
            print("❌ Bucket não configurado como website!")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar S3: {e}")
        return False

def corrigir_s3_bucket():
    """Corrige configurações do bucket S3"""
    print("\n🔧 CORRIGINDO BUCKET S3")
    print("=" * 40)
    
    try:
        s3 = boto3.client('s3')
        bucket_name = 'djblog-noticias-static-1750943590'
        
        # 1. PRIMEIRO: Desbloquear acesso público
        print("1️⃣ Desbloqueando acesso público...")
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        print("✅ Acesso público desbloqueado")
        
        # 2. Configurar como website
        print("2️⃣ Configurando como website...")
        website_config = {
            'IndexDocument': {'Suffix': 'index.html'},
            'ErrorDocument': {'Key': 'error.html'}
        }
        s3.put_bucket_website(Bucket=bucket_name, WebsiteConfiguration=website_config)
        print("✅ Website configurado")
        
        # 3. Política pública para leitura
        print("3️⃣ Configurando política pública...")
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("✅ Política pública configurada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir S3: {e}")
        return False

def verificar_cloudfront():
    """Verifica configuração do CloudFront"""
    print("\n🔍 VERIFICANDO CLOUDFRONT")
    print("=" * 40)
    
    try:
        cloudfront = boto3.client('cloudfront')
        
        # Lista distribuições
        response = cloudfront.list_distributions()
        
        if 'DistributionList' in response and 'Items' in response['DistributionList']:
            for dist in response['DistributionList']['Items']:
                domain_name = dist['DomainName']
                if 'd3q2d002qno2yn.cloudfront.net' in domain_name:
                    print(f"✅ Distribuição encontrada: {domain_name}")
                    
                    # Verifica configuração
                    dist_id = dist['Id']
                    detail = cloudfront.get_distribution(Id=dist_id)
                    config = detail['Distribution']['DistributionConfig']
                    
                    # Verifica Default Root Object
                    if 'DefaultRootObject' in config and config['DefaultRootObject']:
                        print(f"✅ Default Root Object: {config['DefaultRootObject']}")
                    else:
                        print("❌ Default Root Object não configurado!")
                        return False, dist_id
                    
                    # Verifica origem
                    origins = config['Origins']['Items']
                    for origin in origins:
                        print(f"✅ Origem: {origin['DomainName']}")
                    
                    return True, dist_id
        
        print("❌ Distribuição CloudFront não encontrada!")
        return False, None
        
    except Exception as e:
        print(f"❌ Erro ao verificar CloudFront: {e}")
        return False, None

def corrigir_cloudfront(distribution_id):
    """Corrige configuração do CloudFront"""
    print("\n🔧 CORRIGINDO CLOUDFRONT")
    print("=" * 40)
    
    try:
        cloudfront = boto3.client('cloudfront')
        
        # Obtém configuração atual
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        # Atualiza Default Root Object
        config['DefaultRootObject'] = 'index.html'
        
        # Atualiza a distribuição
        cloudfront.update_distribution(
            DistributionConfig=config,
            Id=distribution_id,
            IfMatch=etag
        )
        
        print("✅ CloudFront atualizado com Default Root Object")
        print("⏳ Aguarde alguns minutos para propagação...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir CloudFront: {e}")
        return False

def testar_apos_correcao():
    """Testa acesso após correções"""
    print("\n🧪 TESTANDO APÓS CORREÇÕES")
    print("=" * 40)
    
    import time
    
    print("⏳ Aguardando 30 segundos para propagação...")
    time.sleep(30)
    
    url = "https://d3q2d002qno2yn.cloudfront.net"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"🌐 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 SUCESSO! Site funcionando!")
            return True
        elif response.status_code == 403:
            print("⚠️  Ainda com erro 403 - pode precisar de mais tempo")
            return False
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    print("🚨 CORREÇÃO ERRO 403 - AWS")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    # Verifica configuração atual
    s3_ok = verificar_s3_bucket()
    cloudfront_ok, dist_id = verificar_cloudfront()
    
    if not s3_ok:
        print("\n🔧 S3 precisa de correção...")
        if corrigir_s3_bucket():
            print("✅ S3 corrigido!")
        else:
            print("❌ Falha ao corrigir S3")
            return
    
    if not cloudfront_ok and dist_id:
        print("\n🔧 CloudFront precisa de correção...")
        if corrigir_cloudfront(dist_id):
            print("✅ CloudFront corrigido!")
        else:
            print("❌ Falha ao corrigir CloudFront")
            return
    
    # Testa após correções
    if testar_apos_correcao():
        print("\n🎉 PROBLEMA RESOLVIDO!")
    else:
        print("\n⏳ Aguarde mais tempo para propagação")
    
    print("\n" + "=" * 50)
    print("📝 RESUMO:")
    print("- S3 configurado como website público")
    print("- CloudFront com Default Root Object")
    print("- Teste realizado")
    print("=" * 50)

if __name__ == "__main__":
    main()
