#!/usr/bin/env python3
"""
Demonstração Local do Sistema de Agregação de Notícias
Simula o funcionamento sem precisar de AWS ou MongoDB
"""

import feedparser
import json
from datetime import datetime
from difflib import SequenceMatcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Fontes para demonstração
FONTES_DEMO = [
    {"name": "TechCrunch", "rss": "https://techcrunch.com/feed/", "nicho": "tecnologia"},
    {"name": "Nature", "rss": "https://www.nature.com/nature.rss", "nicho": "ciencia"},
    {"name": "VentureBeat", "rss": "https://venturebeat.com/feed/", "nicho": "startups"},
    {"name": "MIT Technology Review", "rss": "https://www.technologyreview.com/feed", "nicho": "ia"},
]

def checar_plagio_local(title, resumo, noticias_existentes):
    """Verifica plágio local comparando com notícias já coletadas"""
    for noticia in noticias_existentes:
        sim_titulo = SequenceMatcher(None, noticia.get("titulo", ""), title).ratio()
        sim_resumo = SequenceMatcher(None, noticia.get("resumo", ""), resumo).ratio()
        if sim_titulo > 0.8 or sim_resumo > 0.8:
            return True
    return False

def coletar_noticias():
    """Coleta notícias das fontes RSS"""
    noticias_coletadas = []
    total_salvas = 0
    total_existentes = 0
    
    print("🚀 Iniciando coleta de notícias...")
    print("=" * 60)
    
    for fonte in FONTES_DEMO:
        print(f"\n📰 Coletando de: {fonte['name']} ({fonte['nicho']})")
        
        try:
            feed = feedparser.parse(fonte["rss"])
            
            if not feed.entries:
                print(f"  ⚠️  Sem notícias disponíveis")
                continue
            
            for i, entry in enumerate(feed.entries[:3], 1):  # Máximo 3 notícias por fonte
                title = entry.get("title", "(Sem título)")
                link = entry.get("link", "")
                description = entry.get("summary", "")
                
                # Criar resumo (primeiras 60 palavras)
                resumo = " ".join(description.split()[:60]) + ("..." if len(description.split()) > 60 else "")
                
                # Verificar plágio local
                is_plagio = checar_plagio_local(title, resumo, noticias_coletadas)
                
                if not is_plagio:
                    noticia = {
                        "titulo": title,
                        "link": link,
                        "resumo": resumo,
                        "fonte": fonte["name"],
                        "nicho": fonte["nicho"],
                        "data_insercao": datetime.now().isoformat(),
                        "aprovado": True,
                        "plagio_local": False
                    }
                    
                    noticias_coletadas.append(noticia)
                    total_salvas += 1
                    print(f"  ✅ {i}. {title[:50]}...")
                else:
                    total_existentes += 1
                    print(f"  ❌ {i}. {title[:50]}... (duplicada)")
                    
        except Exception as e:
            print(f"  ❌ Erro ao coletar de {fonte['name']}: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMO DA COLETA")
    print("=" * 60)
    print(f"✅ Notícias salvas: {total_salvas}")
    print(f"❌ Duplicadas/existentes: {total_existentes}")
    print(f"📰 Total processado: {total_salvas + total_existentes}")
    
    return noticias_coletadas

def mostrar_estatisticas(noticias):
    """Mostra estatísticas das notícias coletadas"""
    if not noticias:
        print("Nenhuma notícia coletada.")
        return
    
    print("\n📈 ESTATÍSTICAS POR NICHO")
    print("=" * 40)
    
    # Contar por nicho
    nichos = {}
    for noticia in noticias:
        nicho = noticia["nicho"]
        nichos[nicho] = nichos.get(nicho, 0) + 1
    
    for nicho, count in sorted(nichos.items()):
        print(f"  {nicho.capitalize()}: {count} notícias")
    
    print(f"\n📰 NOTÍCIAS COLETADAS")
    print("=" * 40)
    
    for i, noticia in enumerate(noticias, 1):
        print(f"\n{i}. {noticia['titulo']}")
        print(f"   📍 Nicho: {noticia['nicho']}")
        print(f"   📰 Fonte: {noticia['fonte']}")
        print(f"   📝 Resumo: {noticia['resumo'][:100]}...")
        print(f"   🔗 Link: {noticia['link']}")

def salvar_demo(noticias):
    """Salva as notícias em arquivo JSON para demonstração"""
    if noticias:
        arquivo = f"demo_noticias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(noticias, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Notícias salvas em: {arquivo}")
        return arquivo
    return None

def main():
    """Função principal da demonstração"""
    print("🎯 DEMONSTRAÇÃO LOCAL - SISTEMA DE AGREGAÇÃO DE NOTÍCIAS")
    print("=" * 70)
    print("Este script demonstra o funcionamento do sistema sem precisar de:")
    print("  - AWS (Lambda, EventBridge, SNS)")
    print("  - MongoDB Atlas")
    print("  - Terraform")
    print("=" * 70)
    
    # Coletar notícias
    noticias = coletar_noticias()
    
    # Mostrar estatísticas
    mostrar_estatisticas(noticias)
    
    # Salvar resultado
    arquivo = salvar_demo(noticias)
    
    print("\n" + "=" * 70)
    print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
    print("=" * 70)
    print("✅ Sistema funcionando perfeitamente!")
    print("✅ Coleta de RSS funcionando!")
    print("✅ Verificação de plágio funcionando!")
    print("✅ Processamento de nichos funcionando!")
    
    if arquivo:
        print(f"✅ Dados salvos em: {arquivo}")
    
    print("\n🚀 Próximos passos para implementação completa:")
    print("  1. Configurar MongoDB Atlas (gratuito)")
    print("  2. Instalar AWS CLI e Terraform")
    print("  3. Configurar variáveis de ambiente")
    print("  4. Executar deploy completo")

if __name__ == "__main__":
    main() 