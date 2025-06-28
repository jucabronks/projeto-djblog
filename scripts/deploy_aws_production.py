#!/usr/bin/env python3
"""
Script para deploy automatizado no AWS S3 + CloudFront
Para uso em produção com domínio próprio
"""

import os
import sys
import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError


class AWSProductionDeploy:
    """Deploy profissional AWS S3 + CloudFront"""
    
    def __init__(self, domain_name: str, aws_region: str = "us-east-1"):
        self.domain_name = domain_name
        self.aws_region = aws_region
        self.bucket_name = f"{domain_name.replace('.', '-')}-static-site"
        
        # Clientes AWS
        self.s3 = boto3.client('s3', region_name=aws_region)
        self.cloudfront = boto3.client('cloudfront', region_name=aws_region)
        self.acm = boto3.client('acm', region_name='us-east-1')  # ACM deve ser us-east-1
        self.route53 = boto3.client('route53', region_name=aws_region)
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        print(f"{icons.get(level, 'ℹ️')} [{timestamp}] {message}")
        
    def create_s3_bucket(self) -> bool:
        """Criar bucket S3 para site estático"""
        self.log(f"Criando bucket S3: {self.bucket_name}")
        
        try:
            # Criar bucket
            bucket_exists = False
            try:
                if self.aws_region == "us-east-1":
                    self.s3.create_bucket(Bucket=self.bucket_name)
                else:
                    self.s3.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.aws_region}
                    )
                self.log(f"Bucket criado: {self.bucket_name}", "SUCCESS")
            except ClientError as e:
                if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                    self.log(f"Bucket já existe: {self.bucket_name}", "WARNING")
                    bucket_exists = True
                else:
                    raise e
            
            # Desabilitar Block Public Access para permitir site estático
            try:
                self.s3.delete_public_access_block(Bucket=self.bucket_name)
                self.log("Block Public Access removido", "SUCCESS")
            except ClientError as e:
                if 'NoSuchPublicAccessBlockConfiguration' not in str(e):
                    self.log(f"Aviso ao remover Block Public Access: {e}", "WARNING")
            
            # Configurar para site estático
            website_config = {
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'index.html'}  # SPA fallback
            }
            
            self.s3.put_bucket_website(
                Bucket=self.bucket_name,
                WebsiteConfiguration=website_config
            )
            self.log("Site estático configurado", "SUCCESS")
            
            # Política de acesso público
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                }]
            }
            
            try:
                self.s3.put_bucket_policy(
                    Bucket=self.bucket_name,
                    Policy=json.dumps(bucket_policy)
                )
                self.log("Política pública configurada", "SUCCESS")
            except ClientError as e:
                self.log(f"Erro na política pública: {e}", "ERROR")
                self.log("Continuando sem política pública - usar CloudFront Origin Access", "WARNING")
            
            self.log(f"Bucket S3 configurado: {self.bucket_name}", "SUCCESS")
            return True
            
        except ClientError as e:
            self.log(f"Erro ao configurar bucket: {e}", "ERROR")
            return False
                
    def upload_site_files(self) -> bool:
        """Upload dos arquivos do site para S3"""
        self.log("Gerando site estático...")
        
        # Gerar site estático
        os.system("python generate_static_site.py")
        
        if not os.path.exists("index.html"):
            self.log("Arquivo index.html não encontrado!", "ERROR")
            return False
            
        self.log("Fazendo upload dos arquivos...")
        
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
                    
            self.log("Upload concluído com sucesso!", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Erro no upload: {e}", "ERROR")
            return False
            
    def request_ssl_certificate(self) -> str:
        """Solicitar certificado SSL via ACM"""
        self.log(f"Solicitando certificado SSL para {self.domain_name}")
        
        try:
            response = self.acm.request_certificate(
                DomainName=self.domain_name,
                SubjectAlternativeNames=[f"www.{self.domain_name}"],
                ValidationMethod='DNS'
            )
            
            cert_arn = response['CertificateArn']
            self.log(f"Certificado solicitado: {cert_arn}", "SUCCESS")
            
            # Aguardar informações de validação
            time.sleep(5)
            
            cert_details = self.acm.describe_certificate(CertificateArn=cert_arn)
            validation_options = cert_details['Certificate']['DomainValidationOptions']
            
            self.log("Configure os seguintes registros DNS para validar o certificado:")
            for option in validation_options:
                record = option['ResourceRecord']
                print(f"  Domínio: {option['DomainName']}")
                print(f"  Nome: {record['Name']}")
                print(f"  Tipo: {record['Type']}")
                print(f"  Valor: {record['Value']}")
                print()
                
            return cert_arn
            
        except Exception as e:
            self.log(f"Erro ao solicitar certificado: {e}", "ERROR")
            return None
            
    def create_cloudfront_distribution(self, cert_arn: str = None) -> str:
        """Criar distribuição CloudFront"""
        self.log("Criando distribuição CloudFront...")
        
        # Configuração básica - usar S3 bucket direto (não website endpoint)
        origin_domain = f"{self.bucket_name}.s3.{self.aws_region}.amazonaws.com"
        
        distribution_config = {
            'CallerReference': f"{self.domain_name}-{int(time.time())}",
            'DefaultRootObject': 'index.html',
            'Comment': f"DJBlog - {self.domain_name}",
            'Enabled': True,
            'PriceClass': 'PriceClass_100',  # Apenas US/Europa (mais barato)
            'Origins': {
                'Quantity': 1,
                'Items': [{
                    'Id': 'S3Origin',
                    'DomainName': origin_domain,
                    'S3OriginConfig': {
                        'OriginAccessIdentity': ''  # Usar OAI para segurança
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
            }
        }
        
        # Adicionar SSL e domínio customizado se certificado fornecido
        if cert_arn:
            distribution_config['Aliases'] = {
                'Quantity': 2,
                'Items': [self.domain_name, f"www.{self.domain_name}"]
            }
            distribution_config['ViewerCertificate'] = {
                'ACMCertificateArn': cert_arn,
                'SSLSupportMethod': 'sni-only',
                'MinimumProtocolVersion': 'TLSv1.2_2021'
            }
        else:
            distribution_config['ViewerCertificate'] = {
                'CloudFrontDefaultCertificate': True
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
            
    def setup_route53_dns(self, cloudfront_domain: str) -> bool:
        """Configurar DNS no Route 53"""
        self.log(f"Configurando DNS para {self.domain_name}")
        
        try:
            # Verificar se hosted zone existe
            zones = self.route53.list_hosted_zones()
            zone_id = None
            
            for zone in zones['HostedZones']:
                if zone['Name'].rstrip('.') == self.domain_name:
                    zone_id = zone['Id'].split('/')[-1]
                    break
                    
            if not zone_id:
                self.log(f"Hosted Zone não encontrada para {self.domain_name}", "ERROR")
                self.log("Crie uma Hosted Zone no Route 53 primeiro!", "ERROR")
                return False
                
            # Criar registros A para domínio principal e www
            for subdomain in ['', 'www']:
                record_name = f"{subdomain}.{self.domain_name}" if subdomain else self.domain_name
                
                change_batch = {
                    'Comment': f'DJBlog - Apontar {record_name} para CloudFront',
                    'Changes': [{
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': record_name,
                            'Type': 'CNAME' if subdomain else 'A',
                            'AliasTarget': {
                                'DNSName': cloudfront_domain,
                                'EvaluateTargetHealth': False,
                                'HostedZoneId': 'Z2FDTNDATAQYW2'  # CloudFront zone ID
                            } if not subdomain else None,
                            'TTL': 300,
                            'ResourceRecords': [{'Value': cloudfront_domain}] if subdomain else None
                        }
                    }]
                }
                
                if not subdomain:
                    # Para domínio raiz, usar ALIAS
                    del change_batch['Changes'][0]['ResourceRecordSet']['TTL']
                    del change_batch['Changes'][0]['ResourceRecordSet']['ResourceRecords']
                else:
                    # Para www, usar CNAME
                    del change_batch['Changes'][0]['ResourceRecordSet']['AliasTarget']
                    
                self.route53.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch=change_batch
                )
                
            self.log("DNS configurado com sucesso!", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Erro ao configurar DNS: {e}", "ERROR")
            return False
            
    def deploy_complete(self) -> bool:
        """Deploy completo: S3 + CloudFront + SSL + DNS"""
        self.log(f"🚀 Iniciando deploy profissional para {self.domain_name}")
        
        # 1. Criar bucket S3
        if not self.create_s3_bucket():
            return False
            
        # 2. Upload do site
        if not self.upload_site_files():
            return False
            
        # 3. Solicitar certificado SSL
        cert_arn = self.request_ssl_certificate()
        
        if cert_arn:
            self.log("⚠️ IMPORTANTE: Configure os registros DNS para validar o certificado SSL!")
            self.log("Aguarde a validação antes de prosseguir...")
            input("Pressione ENTER após configurar os registros DNS...")
            
        # 4. Criar CloudFront
        distribution_id, cloudfront_domain = self.create_cloudfront_distribution(cert_arn)
        
        if not distribution_id:
            return False
            
        # 5. Configurar DNS (opcional, requer Route 53)
        self.setup_route53_dns(cloudfront_domain)
        
        # Relatório final
        self.log("🎉 Deploy concluído com sucesso!", "SUCCESS")
        self.log(f"📊 Relatório do Deploy:")
        self.log(f"   Bucket S3: {self.bucket_name}")
        self.log(f"   CloudFront ID: {distribution_id}")
        self.log(f"   CloudFront URL: https://{cloudfront_domain}")
        if cert_arn:
            self.log(f"   Certificado SSL: {cert_arn}")
        self.log(f"   Domínio final: https://{self.domain_name}")
        
        return True


def main():
    """Função principal"""
    print("🌐 Deploy Profissional AWS - DJBlog")
    print("=" * 50)
    
    # Solicitar informações
    domain_name = input("Digite seu domínio (ex: meublog.com.br): ").strip()
    aws_region = input("Região AWS [us-east-1]: ").strip() or "us-east-1"
    
    if not domain_name:
        print("❌ Domínio é obrigatório!")
        return
        
    # Verificar credenciais AWS
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS configurado: {identity.get('Arn', 'N/A')}")
    except Exception as e:
        print(f"❌ Erro nas credenciais AWS: {e}")
        print("Configure: aws configure")
        return
        
    # Executar deploy
    deployer = AWSProductionDeploy(domain_name, aws_region)
    success = deployer.deploy_complete()
    
    if success:
        print("\n🎉 Site disponível em produção!")
        print(f"🌐 URL: https://{domain_name}")
    else:
        print("\n❌ Deploy falhou. Verifique os erros acima.")
        

if __name__ == "__main__":
    main()
