#!/usr/bin/env python3
"""
Diagnóstico completo do erro 403 no CloudFront
Identifica e corrige problemas comuns de configuração
"""

import requests
import json
import socket
import subprocess
import sys
from datetime import datetime

def testar_acesso_direto():
    """Testa acesso direto ao CloudFront"""
    print("🔍 TESTE 1: Acesso direto ao CloudFront")
    print("=" * 50)
    
    cloudfront_url = "https://d3q2d002qno2yn.cloudfront.net"
    
    try:
        response = requests.get(cloudfront_url, timeout=10)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ CloudFront funcionando corretamente!")
            return True
        elif response.status_code == 403:
            print("❌ Erro 403 no CloudFront")
            print("🔍 Possíveis causas:")
            print("   - Arquivo index.html não existe no S3")
            print("   - Permissões do bucket S3 incorretas")
            print("   - Configuração de origem do CloudFront")
            return False
        else:
            print(f"⚠️  Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def testar_dominio_personalizado():
    """Testa acesso via domínio personalizado"""
    print("\n🔍 TESTE 2: Domínio personalizado")
    print("=" * 50)
    
    dominios = [
        "https://noticiasontem.com.br",
        "https://www.noticiasontem.com.br"
    ]
    
    for dominio in dominios:
        print(f"\n🌐 Testando: {dominio}")
        try:
            response = requests.get(dominio, timeout=10)
            print(f"✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ {dominio} funcionando!")
            elif response.status_code == 403:
                print(f"❌ Erro 403 em {dominio}")
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Conexão falhou - DNS não resolvido")
        except Exception as e:
            print(f"❌ Erro: {e}")

def verificar_dns_resolucao():
    """Verifica resolução DNS"""
    print("\n🔍 TESTE 3: Resolução DNS")
    print("=" * 50)
    
    dominios = ["noticiasontem.com.br", "www.noticiasontem.com.br"]
    
    for dominio in dominios:
        print(f"\n🌐 Resolvendo: {dominio}")
        try:
            ip = socket.gethostbyname(dominio)
            print(f"✅ IP resolvido: {ip}")
            
            # Verifica se é um IP do CloudFront (AWS)
            if ip.startswith(('52.', '54.', '18.', '13.')):
                print("✅ IP parece ser do AWS/CloudFront")
            else:
                print("⚠️  IP não parece ser do AWS")
                
        except socket.gaierror:
            print(f"❌ DNS não resolvido para {dominio}")

def testar_cache_navegador():
    """Testa com diferentes headers para evitar cache"""
    print("\n🔍 TESTE 4: Cache do navegador")
    print("=" * 50)
    
    url = "https://noticiasontem.com.br"
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status com headers no-cache: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Site funcionando sem cache!")
        elif response.status_code == 403:
            print("❌ Erro 403 persiste mesmo sem cache")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def verificar_arquivo_index():
    """Verifica se o arquivo index.html existe no CloudFront"""
    print("\n🔍 TESTE 5: Arquivo index.html")
    print("=" * 50)
    
    urls_teste = [
        "https://d3q2d002qno2yn.cloudfront.net/index.html",
        "https://d3q2d002qno2yn.cloudfront.net/"
    ]
    
    for url in urls_teste:
        print(f"\n📄 Testando: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Arquivo encontrado!")
                # Verifica se tem conteúdo HTML
                if 'html' in response.text.lower():
                    print("✅ Conteúdo HTML válido")
                else:
                    print("⚠️  Conteúdo não parece ser HTML")
                    
        except Exception as e:
            print(f"❌ Erro: {e}")

def gerar_relatorio_403():
    """Gera relatório completo do diagnóstico"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    relatorio = f"""
# RELATÓRIO DIAGNÓSTICO 403 - {timestamp}

## RESUMO EXECUTIVO
- **Data**: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
- **Problema**: Erro 403 no CloudFront
- **Domínio**: noticiasontem.com.br

## TESTES REALIZADOS
1. Acesso direto ao CloudFront
2. Domínio personalizado
3. Resolução DNS
4. Cache do navegador
5. Arquivo index.html

## POSSÍVEIS SOLUÇÕES

### 1. VERIFICAR S3 BUCKET
- Confirmar que index.html existe
- Verificar permissões públicas
- Confirmar política do bucket

### 2. VERIFICAR CLOUDFRONT
- Confirmar configuração de origem
- Verificar Default Root Object (index.html)
- Revisar comportamentos de cache

### 3. VERIFICAR DNS
- Confirmar CNAME no Registro.br
- Aguardar propagação completa
- Testar com diferentes DNS

### 4. COMANDOS ÚTEIS
```
ipconfig /flushdns
nslookup noticiasontem.com.br
nslookup www.noticiasontem.com.br
```

## PRÓXIMOS PASSOS
1. Executar diagnóstico completo
2. Verificar configurações AWS
3. Aguardar propagação DNS se necessário
4. Testar em modo anônimo
"""

    with open("DIAGNOSTICO_403_COMPLETO.txt", "w", encoding="utf-8") as f:
        f.write(relatorio)
    
    print(f"\n📄 Relatório salvo em: DIAGNOSTICO_403_COMPLETO.txt")

def main():
    print("🚨 DIAGNÓSTICO ERRO 403 - CLOUDFRONT")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Executa todos os testes
    testar_acesso_direto()
    testar_dominio_personalizado()
    verificar_dns_resolucao()
    testar_cache_navegador()
    verificar_arquivo_index()
    
    # Gera relatório
    gerar_relatorio_403()
    
    print("\n" + "=" * 60)
    print("🔧 RECOMENDAÇÕES IMEDIATAS:")
    print("1. Limpar cache DNS: ipconfig /flushdns")
    print("2. Testar em navegador anônimo")
    print("3. Verificar registros DNS no Registro.br")
    print("4. Aguardar mais tempo para propagação")
    print("=" * 60)

if __name__ == "__main__":
    main()
