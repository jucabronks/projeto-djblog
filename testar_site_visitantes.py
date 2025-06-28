import requests

try:
    print("🌐 TESTANDO SITE PARA VISITANTES")
    print("=" * 40)
    
    # Testar domínio principal
    print("🔍 Testando: https://noticiasontem.com.br")
    r1 = requests.get('https://noticiasontem.com.br', timeout=10)
    print(f"Status: {r1.status_code}")
    print(f"Tamanho: {len(r1.text)} chars")
    print(f"Content-Type: {r1.headers.get('content-type', 'N/A')}")
    
    # Verificar se é HTML válido
    if '<html' in r1.text.lower() or '<!doctype' in r1.text.lower():
        print("✅ Página HTML detectada")
        if '<title>' in r1.text.lower():
            print("✅ Título encontrado")
        if 'noticia' in r1.text.lower():
            print("✅ Conteúdo do blog detectado")
    else:
        print("❌ Não parece ser página HTML válida")
    
    print("\n" + "-" * 40)
    
    # Testar www
    print("🔍 Testando: https://www.noticiasontem.com.br")
    r2 = requests.get('https://www.noticiasontem.com.br', timeout=10)
    print(f"Status: {r2.status_code}")
    print(f"Tamanho: {len(r2.text)} chars")
    
    print("\n" + "=" * 40)
    print("📋 RESUMO:")
    if r1.status_code == 200:
        print("✅ Site principal funcionando")
    else:
        print(f"❌ Site principal com problema: {r1.status_code}")
        
    if r2.status_code == 200:
        print("✅ WWW funcionando")
    else:
        print(f"❌ WWW com problema: {r2.status_code}")

except Exception as e:
    print(f"❌ Erro ao testar: {e}")
