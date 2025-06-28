#!/usr/bin/env python3
"""
Script para ajudar a identificar e resolver conflitos de CNAME no Cloudflare
Parte do projeto DJBlog - Deploy em produção
"""

import sys
import os
from datetime import datetime

def main():
    print("🔧 CLOUDFLARE - RESOLVER ERRO CNAME DUPLICADO")
    print("=" * 55)
    print()
    
    print("❌ ERRO COMUM: 'A CNAME record with that host already exists'")
    print()
    
    print("🎯 SOLUÇÃO PASSO A PASSO:")
    print("-" * 30)
    print()
    
    print("1️⃣ ACESSE SEU PAINEL CLOUDFLARE:")
    print("   • https://dash.cloudflare.com")
    print("   • Clique em 'noticiasontem.com.br'")
    print("   • Vá na aba 'DNS' → 'Records'")
    print()
    
    print("2️⃣ PROCURE POR REGISTROS QUE COMEÇAM COM '_':")
    print("   • Role a página para baixo")
    print("   • Procure registros do tipo CNAME")
    print("   • Que começam com '_' (underscore)")
    print()
    
    print("3️⃣ REGISTROS PARA PROCURAR E DELETAR:")
    print("   ⚠️ Se encontrar QUALQUER um destes, DELETE:")
    print()
    print("   • _19837e8068f6a4d75e9bdfd772154663")
    print("   • _88fe1a2469d7ce78bd80f82750e60fef")
    print("   • Qualquer outro que comece com _ e termine com acm-validations.aws")
    print()
    
    print("4️⃣ COMO DELETAR:")
    print("   • Clique no ícone 🗑️ (lixeira) ao lado do registro")
    print("   • Confirme a exclusão")
    print("   • Aguarde alguns segundos")
    print()
    
    print("5️⃣ DEPOIS DE DELETAR, ADICIONE OS NOVOS:")
    print()
    print("   📝 REGISTRO 1:")
    print("   Type: CNAME")
    print("   Name: _19837e8068f6a4d75e9bdfd772154663")
    print("   Target: _a94a255a3c25cba74c95244e79562393.xlfgrmvvlj.acm-validations.aws")
    print("   Proxy status: 🔘 DNS only (cinza/desabilitado)")
    print()
    
    print("   📝 REGISTRO 2:")
    print("   Type: CNAME")
    print("   Name: _88fe1a2469d7ce78bd80f82750e60fef.www")
    print("   Target: _1aa1b9515605c723c3757c748117b9fa.xlfgrmvvlj.acm-validations.aws")
    print("   Proxy status: 🔘 DNS only (cinza/desabilitado)")
    print()
    
    print("⚠️ IMPORTANTE:")
    print("• NO CAMPO 'Name', NÃO adicione '.noticiasontem.com.br'")
    print("• O Cloudflare adiciona automaticamente")
    print("• Proxy status DEVE estar desabilitado (cinza)")
    print("• Se ainda der erro, tire um screenshot e me mostre")
    print()
    
    print("✅ APÓS ADICIONAR:")
    print("• Aguarde 5-10 minutos")
    print("• Execute: python scripts/configurar_ssl_dominio.py")
    print("• O SSL será configurado automaticamente")
    print()
    
    print("🆘 AINDA COM PROBLEMA?")
    print("• Tire um screenshot da tela de DNS do Cloudflare")
    print("• Mostre exatamente onde está dando erro")
    print("• Posso te ajudar com instruções específicas")
    print()
    
    print("=" * 55)
    print(f"📅 Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    main()
