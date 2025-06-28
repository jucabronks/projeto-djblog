#!/usr/bin/env python3
"""
Deploy apenas do arquivo HTML atualizado
"""

import boto3
import os
from datetime import datetime

def upload_to_existing_bucket():
    """Upload apenas do index.html para o bucket existente"""
    try:
        s3 = boto3.client('s3')
        bucket_name = 'djblog-noticias-static-1750943590'
        
        print("🚀 ATUALIZANDO DESIGN DO SITE")
        print("=" * 40)
        print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        # Upload do index.html
        print("📄 Enviando index.html...")
        s3.upload_file(
            'index.html',
            bucket_name,
            'index.html',
            ExtraArgs={
                'ContentType': 'text/html',
                'CacheControl': 'max-age=300'  # 5 minutos de cache
            }
        )
        print("✅ index.html enviado!")
        
        # Invalidar cache do CloudFront
        print("\n🔄 Invalidando cache do CloudFront...")
        cloudfront = boto3.client('cloudfront')
        
        try:
            cloudfront.create_invalidation(
                DistributionId='E3S1TW1RZGH9RL',
                InvalidationBatch={
                    'Paths': {
                        'Quantity': 1,
                        'Items': ['/index.html']
                    },
                    'CallerReference': str(datetime.now().timestamp())
                }
            )
            print("✅ Cache invalidado!")
        except Exception as e:
            print(f"⚠️ Aviso - Cache: {e}")
        
        print("\n🎉 NOVO DESIGN IMPLANTADO COM SUCESSO!")
        print("=" * 40)
        print("🌐 Seu site foi atualizado:")
        print("• https://noticiasontem.com.br")
        print("• https://www.noticiasontem.com.br")
        print("\n⏰ Pode levar 1-2 minutos para aparecer")
        print("💡 Dica: Pressione Ctrl+F5 para forçar atualização")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no deploy: {e}")
        return False

if __name__ == "__main__":
    upload_to_existing_bucket()
