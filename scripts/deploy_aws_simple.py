#!/usr/bin/env python3
"""
Script simplificado para deploy no AWS S3 + CloudFront
Versão sem domínio customizado para teste inicial
"""

import os
import sys
import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError


class SimpleAWSDeploy:
    """Deploy simplificado AWS S3 + CloudFront"""
    
    def __init__(self, project_name: str = "djblog-noticias", aws_region: str = "us-east-1"):
        self.project_name = project_name
        self.aws_region = aws_region
        self.bucket_name = f"{project_name}-static-{int(time.time())}"
        
        # Clientes AWS
        self.s3 = boto3.client('s3', region_name=aws_region)
        self.cloudfront = boto3.client('cloudfront', region_name=aws_region)
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        print(f"{icons.get(level, 'ℹ️')} [{timestamp}] {message}")
        
    def create_s3_bucket(self) -> bool:
        """Criar bucket S3 simples"""
        self.log(f"Criando bucket S3: {self.bucket_name}")
        
        try:
            # Criar bucket
            if self.aws_region == "us-east-1":
                self.s3.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.aws_region}
                )
            
            self.log(f"Bucket criado: {self.bucket_name}", "SUCCESS")
            return True
            
        except ClientError as e:
            self.log(f"Erro ao criar bucket: {e}", "ERROR")
            return False
                
    def upload_site_files(self) -> bool:
        """Upload dos arquivos do site para S3"""
        self.log("Gerando site estático...")
        
        # Gerar site estático
        os.system("python generate_static_site.py")
        
        if not os.path.exists("index.html"):
            self.log("Arquivo index.html não encontrado!", "ERROR")
            return False
            
        self.log("Fazendo upload do site...")
        
        try:
            # Upload index.html
            self.s3.upload_file(
                "index.html",
                self.bucket_name,
                "index.html",
                ExtraArgs={
                    'ContentType': 'text/html',
                    'CacheControl': 'max-age=300'  # 5 minutos
                }
            )
            
            # Upload outros arquivos se existirem
            static_files = [
                ("favicon.ico", "image/x-icon"),
                ("robots.txt", "text/plain"),
                ("sitemap.xml", "application/xml")
            ]
            
            for filename, content_type in static_files:
                if os.path.exists(filename):
                    self.s3.upload_file(
                        filename,
                        self.bucket_name,
                        filename,
                        ExtraArgs={
                            'ContentType': content_type,
                            'CacheControl': 'max-age=86400'  # 1 dia
                        }
                    )
                    self.log(f"Uploaded: {filename}")
                    
            self.log("Upload concluído com sucesso!", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Erro no upload: {e}", "ERROR")
            return False
            
    def create_cloudfront_distribution(self) -> tuple:
        """Criar distribuição CloudFront"""
        self.log("Criando distribuição CloudFront...")
        
        # Configuração básica - usar S3 bucket direto
        origin_domain = f"{self.bucket_name}.s3.{self.aws_region}.amazonaws.com"
        
        distribution_config = {
            'CallerReference': f"{self.project_name}-{int(time.time())}",
            'DefaultRootObject': 'index.html',
            'Comment': f"DJBlog Static Site - {self.project_name}",
            'Enabled': True,
            'PriceClass': 'PriceClass_100',  # Apenas US/Europa (mais barato)
            'Origins': {
                'Quantity': 1,
                'Items': [{
                    'Id': 'S3Origin',
                    'DomainName': origin_domain,
                    'S3OriginConfig': {
                        'OriginAccessIdentity': ''
                    }
                }]
            },
            'DefaultCacheBehavior': {
                'TargetOriginId': 'S3Origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0
                },
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {'Forward': 'none'}
                },
                'MinTTL': 0,
                'DefaultTTL': 300,  # 5 minutos
                'MaxTTL': 86400,    # 1 dia
                'Compress': True
            },
            'CustomErrorResponses': {
                'Quantity': 1,
                'Items': [{
                    'ErrorCode': 404,
                    'ResponsePagePath': '/index.html',
                    'ResponseCode': '200',
                    'ErrorCachingMinTTL': 300
                }]
            },
            'ViewerCertificate': {
                'CloudFrontDefaultCertificate': True
            }
        }
            
        try:
            response = self.cloudfront.create_distribution(
                DistributionConfig=distribution_config
            )
            
            distribution_id = response['Distribution']['Id']
            domain_name = response['Distribution']['DomainName']
            
            self.log(f"CloudFront criado: {distribution_id}", "SUCCESS")
            self.log(f"URL CloudFront: https://{domain_name}")
            
            return distribution_id, domain_name
            
        except Exception as e:
            self.log(f"Erro ao criar CloudFront: {e}", "ERROR")
            return None, None
            
    def get_s3_website_url(self) -> str:
        """Obter URL do site S3"""
        if self.aws_region == "us-east-1":
            return f"http://{self.bucket_name}.s3-website.amazonaws.com"
        else:
            return f"http://{self.bucket_name}.s3-website-{self.aws_region}.amazonaws.com"
            
    def deploy_complete(self) -> bool:
        """Deploy completo simplificado"""
        self.log(f"🚀 Iniciando deploy simplificado no AWS...")
        
        # 1. Criar bucket S3
        if not self.create_s3_bucket():
            return False
            
        # 2. Upload do site
        if not self.upload_site_files():
            return False
            
        # 3. Obter URL S3 direto
        s3_url = self.get_s3_website_url()
        
        # 4. Criar CloudFront (opcional, demora alguns minutos)
        self.log("Criando CloudFront (pode demorar alguns minutos)...")
        distribution_id, cloudfront_domain = self.create_cloudfront_distribution()
        
        # Relatório final
        self.log("🎉 Deploy concluído com sucesso!", "SUCCESS")
        self.log(f"📊 Relatório do Deploy:")
        self.log(f"   Bucket S3: {self.bucket_name}")
        self.log(f"   URL S3 direto: {s3_url}")
        
        if distribution_id:
            self.log(f"   CloudFront ID: {distribution_id}")
            self.log(f"   URL CloudFront: https://{cloudfront_domain}")
            self.log("   ⏰ CloudFront pode demorar 15-20 min para ativar")
        
        self.log(f"📝 Próximos passos:")
        self.log(f"   1. Teste o S3 direto: {s3_url}")
        if cloudfront_domain:
            self.log(f"   2. Aguarde CloudFront: https://{cloudfront_domain}")
            self.log(f"   3. Use CloudFront para produção (HTTPS + CDN)")
        
        return True


def main():
    """Função principal"""
    print("🚀 Deploy Simplificado AWS S3 + CloudFront - DJBlog")
    print("=" * 60)
    
    # Verificar credenciais AWS
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS configurado: {identity.get('Arn', 'N/A')}")
    except Exception as e:
        print(f"❌ Erro nas credenciais AWS: {e}")
        print("Configure: aws configure")
        return
        
    # Solicitar informações básicas
    project_name = input("Nome do projeto [djblog-noticias]: ").strip() or "djblog-noticias"
    aws_region = input("Região AWS [us-east-1]: ").strip() or "us-east-1"
    
    print(f"\\n📋 Configuração:")
    print(f"   Projeto: {project_name}")
    print(f"   Região: {aws_region}")
    print(f"   Bucket: {project_name}-static-{int(time.time())}")
    
    confirm = input("\\nContinuar com deploy? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Deploy cancelado.")
        return
        
    # Executar deploy
    deployer = SimpleAWSDeploy(project_name, aws_region)
    success = deployer.deploy_complete()
    
    if success:
        print("\\n🎉 Site disponível na AWS!")
        print("🌐 Use a URL CloudFront para produção (HTTPS + CDN)")
    else:
        print("\\n❌ Deploy falhou. Verifique os erros acima.")
        

if __name__ == "__main__":
    main()
