#!/usr/bin/env python3
"""
Guia interativo para adicionar registros CNAME de validação SSL
"""

import webbrowser
from datetime import datetime

def mostrar_registros_ssl():
    """Mostra os registros que precisam ser adicionados"""
    print("🔒 REGISTROS CNAME PARA VALIDAÇÃO SSL")
    print("=" * 60)
    print()
    
    print("📋 VOCÊ PRECISA ADICIONAR ESTES 2 REGISTROS:")
    print()
    
    print("🔹 REGISTRO 1:")
    print("   Nome: _19837e8068f6a4d75e9bdfd772154663.noticiasontem.com.br")
    print("   Tipo: CNAME")
    print("   Valor: _a94a255a3c25cba74c95244e79562393.xlfgrmvvlj.acm-validations.aws")
    print("   TTL: 3600")
    print()
    
    print("🔹 REGISTRO 2:")
    print("   Nome: _88fe1a2469d7ce78bd80f82750e60fef.www.noticiasontem.com.br")
    print("   Tipo: CNAME")
    print("   Valor: _1aa1b9515605c723c3757c748117b9fa.xlfgrmvvlj.acm-validations.aws")
    print("   TTL: 3600")

def guia_passo_a_passo():
    """Guia passo a passo interativo"""
    print("\n🚀 PASSO A PASSO:")
    print("=" * 60)
    
    print("\n1️⃣ ABRIR PAINEL DO REGISTRO.BR")
    try:
        webbrowser.open("https://painel.registro.br")
        print("   ✅ Abrindo painel.registro.br...")
    except:
        print("   📱 Acesse: https://painel.registro.br")
    
    input("\n   Pressione ENTER quando estiver logado no painel...")
    
    print("\n2️⃣ NAVEGAR PARA DNS")
    print("   • Clique em 'Meus Domínios'")
    print("   • Clique em 'noticiasontem.com.br'")
    print("   • Clique em 'DNS' ou 'Zona de DNS'")
    
    input("\n   Pressione ENTER quando estiver na página de DNS...")
    
    print("\n3️⃣ ADICIONAR PRIMEIRO REGISTRO")
    print("   • Clique em 'Adicionar Registro' ou 'Novo'")
    print("   • Preencha:")
    print("     Nome: _19837e8068f6a4d75e9bdfd772154663.noticiasontem.com.br")
    print("     Tipo: CNAME")
    print("     Valor: _a94a255a3c25cba74c95244e79562393.xlfgrmvvlj.acm-validations.aws")
    print("   • Clique em 'Salvar'")
    
    input("\n   Pressione ENTER quando adicionar o primeiro registro...")
    
    print("\n4️⃣ ADICIONAR SEGUNDO REGISTRO")
    print("   • Clique em 'Adicionar Registro' novamente")
    print("   • Preencha:")
    print("     Nome: _88fe1a2469d7ce78bd80f82750e60fef.www.noticiasontem.com.br")
    print("     Tipo: CNAME")
    print("     Valor: _1aa1b9515605c723c3757c748117b9fa.xlfgrmvvlj.acm-validations.aws")
    print("   • Clique em 'Salvar'")
    
    input("\n   Pressione ENTER quando adicionar o segundo registro...")
    
    print("\n5️⃣ CONFIRMAR ALTERAÇÕES")
    print("   • Verifique se os 2 registros apareceram na lista")
    print("   • Clique em 'Salvar Alterações' se necessário")
    
    input("\n   Pressione ENTER quando confirmar as alterações...")

def aguardar_validacao():
    """Aguarda e verifica validação"""
    print("\n⏰ AGUARDANDO VALIDAÇÃO SSL")
    print("=" * 60)
    print("⏳ A validação pode levar de 5 a 30 minutos")
    print("📋 O AWS vai verificar os registros DNS automaticamente")
    
    print("\n🔄 Vou verificar o status do certificado em alguns minutos...")
    
    import time
    print("⏳ Aguardando 2 minutos antes de verificar...")
    time.sleep(120)  # Aguarda 2 minutos
    
    # Verifica status do certificado
    try:
        import boto3
        acm = boto3.client('acm', region_name='us-east-1')
        cert_arn = "arn:aws:acm:us-east-1:317304475005:certificate/be47a77b-fe2c-4446b-b697-b192ab1857c8"
        
        details = acm.describe_certificate(CertificateArn=cert_arn)
        status = details['Certificate']['Status']
        
        print(f"\n📋 Status atual do certificado: {status}")
        
        if status == 'ISSUED':
            print("🎉 CERTIFICADO VALIDADO COM SUCESSO!")
            print("🚀 Executando configuração automática do CloudFront...")
            return True
        else:
            print("⏳ Ainda em validação. Aguarde mais alguns minutos.")
            print("🔄 Execute: python scripts/configurar_ssl_dominio.py em 10 minutos")
            return False
            
    except Exception as e:
        print(f"⚠️  Erro ao verificar: {e}")
        print("🔄 Execute: python scripts/configurar_ssl_dominio.py em 10 minutos")
        return False

def main():
    print("🔒 CONFIGURAÇÃO SSL - CERTIFICADO AUTOMÁTICO")
    print("=" * 70)
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Mostra registros
    mostrar_registros_ssl()
    
    # Pergunta se quer guia passo a passo
    resp = input("\n❓ Quer um guia passo a passo interativo? (s/n): ").lower()
    
    if resp == 's':
        guia_passo_a_passo()
        
        # Aguarda validação
        resp2 = input("\n❓ Quer aguardar e verificar a validação automaticamente? (s/n): ").lower()
        if resp2 == 's':
            validado = aguardar_validacao()
            
            if validado:
                print("\n🚀 Configurando CloudFront automaticamente...")
                import subprocess
                subprocess.run(['python', 'scripts/configurar_ssl_dominio.py'])
    
    print("\n" + "=" * 70)
    print("📝 RESUMO:")
    print("1. Adicione os 2 registros CNAME no painel do Registro.br")
    print("2. Aguarde 5-30 minutos para validação")
    print("3. Execute: python scripts/configurar_ssl_dominio.py")
    print("4. 🎉 Site funcionará com HTTPS!")
    print("=" * 70)

if __name__ == "__main__":
    main()
