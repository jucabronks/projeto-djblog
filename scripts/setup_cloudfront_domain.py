#!/usr/bin/env python3
"""
Script para configurar domínio customizado no CloudFront existente
Adiciona alias ao CloudFront atual
"""

import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError


class CloudFrontDomainSetup:
    """Configurar domínio no CloudFront existente"""
    
    def __init__(self, distribution_id: str, domain_name: str):
        self.distribution_id = distribution_id
        self.domain_name = domain_name
        self.cloudfront = boto3.client('cloudfront')
        self.acm = boto3.client('acm', region_name='us-east-1')  # ACM deve ser us-east-1
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        print(f"{icons.get(level, 'ℹ️')} [{timestamp}] {message}")
        
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
            
            self.log("📝 Configure os seguintes registros DNS para validar:")
            print()
            for option in validation_options:
                record = option['ResourceRecord']
                print(f"🌐 Domínio: {option['DomainName']}")
                print(f"📝 Nome: {record['Name']}")
                print(f"🏷️ Tipo: {record['Type']}")
                print(f"📋 Valor: {record['Value']}")
                print("-" * 60)
                
            return cert_arn
            
        except Exception as e:
            self.log(f"Erro ao solicitar certificado: {e}", "ERROR")
            return None
            
    def update_cloudfront_distribution(self, cert_arn: str) -> bool:
        """Atualizar distribuição CloudFront com domínio customizado"""
        self.log(f"Atualizando CloudFront com domínio {self.domain_name}")
        
        try:
            # Obter configuração atual
            response = self.cloudfront.get_distribution_config(Id=self.distribution_id)
            config = response['DistributionConfig']
            etag = response['ETag']
            
            # Adicionar aliases (domínios customizados)
            config['Aliases'] = {
                'Quantity': 2,
                'Items': [self.domain_name, f"www.{self.domain_name}"]
            }
            
            # Adicionar certificado SSL
            config['ViewerCertificate'] = {
                'ACMCertificateArn': cert_arn,
                'SSLSupportMethod': 'sni-only',
                'MinimumProtocolVersion': 'TLSv1.2_2021'
            }
            
            # Atualizar distribuição
            self.cloudfront.update_distribution(
                Id=self.distribution_id,
                DistributionConfig=config,
                IfMatch=etag
            )
            
            self.log("CloudFront atualizado com sucesso!", "SUCCESS")
            self.log("⏰ Aguarde 15-20 minutos para propagação", "WARNING")
            return True
            
        except Exception as e:
            self.log(f"Erro ao atualizar CloudFront: {e}", "ERROR")
            return False
            
    def generate_dns_instructions(self, cloudfront_domain: str):
        """Gerar instruções de DNS"""
        self.log("📝 Instruções para configurar DNS:")
        print()
        print("🔧 Configure estes registros no seu provedor de DNS:")
        print()
        print(f"📋 Registro A (raiz):")
        print(f"   Nome: {self.domain_name}")
        print(f"   Tipo: CNAME")
        print(f"   Valor: {cloudfront_domain}")
        print()
        print(f"📋 Registro CNAME (www):")
        print(f"   Nome: www.{self.domain_name}")
        print(f"   Tipo: CNAME") 
        print(f"   Valor: {cloudfront_domain}")
        print()
        
    def setup_domain(self, cloudfront_domain: str) -> bool:
        """Configurar domínio completo"""
        self.log(f"🚀 Configurando domínio {self.domain_name}")
        
        # 1. Solicitar certificado SSL
        cert_arn = self.request_ssl_certificate()
        if not cert_arn:
            return False
            
        self.log("⚠️ IMPORTANTE: Configure os registros DNS mostrados acima!")
        self.log("Aguarde alguns minutos para validação do certificado...")
        
        # Aguardar confirmação do usuário
        input("\\nPressione ENTER após configurar os registros DNS...")
        
        # 2. Verificar se certificado foi validado
        self.log("Verificando validação do certificado...")
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                cert_details = self.acm.describe_certificate(CertificateArn=cert_arn)
                status = cert_details['Certificate']['Status']
                
                if status == 'ISSUED':
                    self.log("Certificado validado com sucesso!", "SUCCESS")
                    break
                elif status == 'PENDING_VALIDATION':
                    self.log(f"Aguardando validação... (tentativa {attempt + 1}/{max_attempts})")
                    time.sleep(30)
                else:
                    self.log(f"Status do certificado: {status}", "WARNING")
                    time.sleep(30)
            except Exception as e:
                self.log(f"Erro ao verificar certificado: {e}", "ERROR")
                time.sleep(30)
        else:
            self.log("Timeout na validação do certificado", "ERROR")
            self.log("Continue manualmente no console AWS", "WARNING")
            return False
            
        # 3. Atualizar CloudFront
        if not self.update_cloudfront_distribution(cert_arn):
            return False
            
        # 4. Gerar instruções de DNS
        self.generate_dns_instructions(cloudfront_domain)
        
        self.log("🎉 Configuração concluída!", "SUCCESS")
        self.log(f"🌐 Seu site estará em: https://{self.domain_name}")
        
        return True


def main():
    """Função principal"""
    print("🌐 Configurar Domínio no CloudFront - DJBlog")
    print("=" * 50)
    
    # Informações do CloudFront atual
    distribution_id = "E3S1TW1RZGH9RL"
    cloudfront_domain = "d3q2d002qno2yn.cloudfront.net"
    
    print(f"CloudFront atual: {cloudfront_domain}")
    print(f"Distribution ID: {distribution_id}")
    print()
    
    # Solicitar domínio
    domain_name = input("Digite seu domínio (ex: noticiasdigitais.com.br): ").strip()
    
    if not domain_name:
        print("❌ Domínio é obrigatório!")
        return
        
    print(f"\\n📋 Configuração:")
    print(f"   Domínio: {domain_name}")
    print(f"   CloudFront: {cloudfront_domain}")
    print(f"   SSL: Será configurado automaticamente")
    
    print(f"\\n📝 Requisitos:")
    print(f"   1. Domínio registrado e funcionando")
    print(f"   2. Acesso ao painel DNS do domínio")
    print(f"   3. AWS ACM configurado")
    
    confirm = input("\\nContinuar? [y/N]: ").strip().lower()
    if confirm != 'y':
        print("Configuração cancelada.")
        return
        
    # Executar configuração
    domain_setup = CloudFrontDomainSetup(distribution_id, domain_name)
    success = domain_setup.setup_domain(cloudfront_domain)
    
    if success:
        print(f"\\n🎉 Domínio configurado!")
        print(f"🌐 Site: https://{domain_name}")
    else:
        print("\\n❌ Configuração falhou. Verifique os erros acima.")
        

if __name__ == "__main__":
    main()
