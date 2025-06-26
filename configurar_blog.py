#!/usr/bin/env python3
"""
🏷️ Configurador de Nome do Blog
Script para configurar o nome e identidade do blog automaticamente
"""

import os
import json
import re
from datetime import datetime


def print_header():
    print("🏷️ CONFIGURADOR DE NOME DO BLOG")
    print("=" * 50)
    print()


def get_blog_suggestions():
    """Retorna sugestões de nomes para o blog"""
    return {
        1: {
            "nome": "NewsFlow IA",
            "slogan": "Notícias inteligentes, curadas por IA",
            "descricao": "Agregador automatizado de notícias usando inteligência artificial para curar e resumir as informações mais relevantes do dia.",
            "dominio_sugerido": "newsflow-ia.com",
            "cor_tema": "#2196F3"
        },
        2: {
            "nome": "IntelliNews Brasil",
            "slogan": "Inteligência artificial a serviço da informação",
            "descricao": "Plataforma brasileira de notícias processadas por IA, oferecendo resumos inteligentes e análises relevantes.",
            "dominio_sugerido": "intellinews.com.br",
            "cor_tema": "#4CAF50"
        },
        3: {
            "nome": "SmartDigest",
            "slogan": "Resumos inteligentes do que realmente importa",
            "descricao": "Curadoria automatizada de notícias com foco em relevância e qualidade, alimentada por inteligência artificial.",
            "dominio_sugerido": "smartdigest.com.br",
            "cor_tema": "#FF9800"
        },
        4: {
            "nome": "FlashNews IA",
            "slogan": "Notícias relevantes em tempo real",
            "descricao": "Informação rápida e precisa com processamento inteligente de fontes confiáveis do Brasil e mundo.",
            "dominio_sugerido": "flashnews-ia.com",
            "cor_tema": "#F44336"
        },
        5: {
            "nome": "RelevantDaily",
            "slogan": "Só o que é relevante, todos os dias",
            "descricao": "Seleção diária das notícias mais importantes, processadas e resumidas por inteligência artificial.",
            "dominio_sugerido": "relevantdaily.com.br",
            "cor_tema": "#9C27B0"
        }
    }


def show_suggestions():
    """Mostra as sugestões de nomes"""
    suggestions = get_blog_suggestions()
    
    print("📰 SUGESTÕES DE NOMES:")
    print()
    
    for num, config in suggestions.items():
        print(f"{num}. 🌟 **{config['nome']}**")
        print(f"   💬 {config['slogan']}")
        print(f"   🌐 {config['dominio_sugerido']}")
        print()
    
    print("6. ✍️ **Personalizado** (você escolhe)")
    print()


def get_user_choice():
    """Obtém a escolha do usuário"""
    while True:
        try:
            choice = input("Digite o número da sua escolha (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return int(choice)
            else:
                print("❌ Escolha inválida. Digite um número de 1 a 6.")
        except KeyboardInterrupt:
            print("\n👋 Operação cancelada.")
            exit(0)


def get_custom_config():
    """Obtém configuração personalizada do usuário"""
    print("\n✍️ CONFIGURAÇÃO PERSONALIZADA:")
    print("=" * 30)
    
    nome = input("📰 Nome do blog: ").strip()
    slogan = input("💬 Slogan: ").strip()
    descricao = input("📝 Descrição (opcional): ").strip()
    
    if not descricao:
        descricao = f"Blog de notícias automatizado com inteligência artificial - {nome}"
    
    return {
        "nome": nome,
        "slogan": slogan,
        "descricao": descricao,
        "dominio_sugerido": nome.lower().replace(" ", "-") + ".com",
        "cor_tema": "#2196F3"
    }


def update_config_file(blog_config):
    """Atualiza o arquivo config.py"""
    config_content = f'''"""
Configurações do DJBlog - {blog_config['nome']}
Gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import os

# Configuração do Blog
BLOG_CONFIG = {{
    "nome": "{blog_config['nome']}",
    "slogan": "{blog_config['slogan']}",
    "descricao": "{blog_config['descricao']}",
    "autor": "Sistema IA Automatizado",
    "email": "contato@{blog_config['dominio_sugerido']}",
    "url": "https://jucabronks.github.io/projeto-djblog",
    "cor_tema": "{blog_config['cor_tema']}",
    "categorias": ["Tecnologia", "Ciência", "Brasil", "Mundo", "Economia", "Saúde"],
    "versao": "2.0"
}}

# ...resto das configurações existentes...

def get_config():
    """Retorna configurações do sistema"""
    return {{
        **BLOG_CONFIG,
        "aws_region": os.environ.get("AWS_REGION", "us-east-1"),
        "dynamodb_table_name": os.environ.get("DYNAMODB_TABLE_NAME", "djblog-noticias"),
        "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
        "wp_url": os.environ.get("WP_URL", ""),
        "wp_user": os.environ.get("WP_USER", ""),
        "wp_app_password": os.environ.get("WP_APP_PASSWORD", "")
    }}
'''
    
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ config.py atualizado com {blog_config['nome']}")


def update_generate_static_site(blog_config):
    """Atualiza o gerador de site estático"""
    # Lê o arquivo atual
    with open('generate_static_site.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substitui o título e metadados
    content = re.sub(
        r'<title>.*?</title>',
        f'<title>{blog_config["nome"]} - {blog_config["slogan"]}</title>',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'<meta name="description" content=".*?">',
        f'<meta name="description" content="{blog_config["descricao"]}">',
        content
    )
    
    # Atualiza o H1 principal
    content = re.sub(
        r'<h1[^>]*>.*?</h1>',
        f'<h1>{blog_config["nome"]}</h1>',
        content,
        flags=re.DOTALL
    )
    
    with open('generate_static_site.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ generate_static_site.py atualizado")


def update_readme(blog_config):
    """Atualiza o README.md"""
    # Lê o arquivo atual
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substitui o título
    new_title = f"# 🚀 {blog_config['nome']} - Agregador de Notícias Serverless"
    content = re.sub(r'^# 🚀.*', new_title, content, flags=re.MULTILINE)
    
    # Adiciona descrição do blog
    blog_section = f'''

## 📰 **Sobre o {blog_config['nome']}**

**{blog_config['slogan']}**

{blog_config['descricao']}

### 🌟 **Características:**
- 🤖 **IA Integrada:** Resumos automáticos com OpenAI GPT
- 🔍 **Fontes Confiáveis:** CNN, BBC, Reuters, G1, UOL, etc.
- ⚡ **Tempo Real:** Coleta 4x por dia (21:00-21:30 BRT)
- 📱 **Responsivo:** Design otimizado para mobile e desktop
- 🚀 **Serverless:** Custo $3-5/mês, zero manutenção
- 🎯 **SEO Otimizado:** Seguindo normas do Google

'''
    
    # Insere após o cabeçalho principal
    content = re.sub(
        r'(# 🚀.*?\n\n)',
        f'\\1{blog_section}',
        content,
        flags=re.DOTALL
    )
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ README.md atualizado")


def create_blog_info_file(blog_config):
    """Cria arquivo com informações do blog"""
    info_content = f"""# 📰 {blog_config['nome']} - Informações do Blog

## 🎯 **Identidade**
- **Nome:** {blog_config['nome']}
- **Slogan:** {blog_config['slogan']}
- **Domínio sugerido:** {blog_config['dominio_sugerido']}
- **Cor tema:** {blog_config['cor_tema']}

## 📝 **Descrição**
{blog_config['descricao']}

## 🌐 **URLs**
- **Site:** https://jucabronks.github.io/projeto-djblog
- **Repositório:** https://github.com/jucabronks/projeto-djblog
- **Actions:** https://github.com/jucabronks/projeto-djblog/actions

## 🚀 **Configuração Concluída**
- ✅ Identidade definida
- ✅ Arquivos atualizados automaticamente
- ✅ Site pronto para deploy

## 📞 **Próximos Passos**
1. Execute: `python deploy_oneclick.py`
2. Aguarde o deploy (2-5 minutos)
3. Acesse o site e veja seu blog funcionando!

---
*Configurado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}*
"""
    
    with open('BLOG_INFO.md', 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print(f"✅ BLOG_INFO.md criado")


def main():
    print_header()
    
    # Mostra sugestões
    show_suggestions()
    
    # Obtém escolha do usuário
    choice = get_user_choice()
    
    # Configura baseado na escolha
    if choice == 6:
        blog_config = get_custom_config()
    else:
        suggestions = get_blog_suggestions()
        blog_config = suggestions[choice]
    
    # Confirma a escolha
    print(f"\n🎯 CONFIGURAÇÃO ESCOLHIDA:")
    print(f"📰 Nome: {blog_config['nome']}")
    print(f"💬 Slogan: {blog_config['slogan']}")
    print(f"🌐 Domínio: {blog_config['dominio_sugerido']}")
    print()
    
    confirm = input("Confirma esta configuração? (s/N): ").strip().lower()
    if confirm not in ['s', 'sim', 'y', 'yes']:
        print("❌ Configuração cancelada.")
        return
    
    # Atualiza os arquivos
    print(f"\n🔧 ATUALIZANDO ARQUIVOS...")
    print("=" * 30)
    
    try:
        update_config_file(blog_config)
        update_generate_static_site(blog_config)
        update_readme(blog_config)
        create_blog_info_file(blog_config)
        
        print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
        print("=" * 40)
        print(f"✅ Seu blog '{blog_config['nome']}' está configurado!")
        print()
        print("🚀 PRÓXIMOS PASSOS:")
        print("1. Execute: python deploy_oneclick.py")
        print("2. Aguarde o deploy (2-5 minutos)")
        print("3. Acesse: https://jucabronks.github.io/projeto-djblog")
        print()
        print("💡 Para verificar: python verificar_site.py --open")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar arquivos: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()
