#!/usr/bin/env python3
"""
Sistema Local Completo - Agregador de Notícias
Simula todas as funcionalidades do projeto sem AWS
"""

import feedparser
import json
import time
import schedule
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Configurações
ARQUIVO_NOTICIAS = "noticias_local.json"
ARQUIVO_FONTES = "fontes_local.json"
ARQUIVO_LOG = "sistema_local.log"

# Fontes expandidas (subconjunto das principais)
FONTES_SISTEMA = [
    # Tecnologia
    {"name": "TechCrunch", "rss": "https://techcrunch.com/feed/", "nicho": "tecnologia", "ativo": True},
    {"name": "The Verge", "rss": "https://www.theverge.com/rss/index.xml", "nicho": "tecnologia", "ativo": True},
    
    # Ciência
    {"name": "Nature", "rss": "https://www.nature.com/nature.rss", "nicho": "ciencia", "ativo": True},
    {"name": "BBC Science", "rss": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "nicho": "ciencia", "ativo": True},
    
    # Startups
    {"name": "VentureBeat", "rss": "https://venturebeat.com/feed/", "nicho": "startups", "ativo": True},
    
    # IA
    {"name": "MIT Technology Review", "rss": "https://www.technologyreview.com/feed", "nicho": "ia", "ativo": True},
    
    # Internacional
    {"name": "The Guardian", "rss": "https://www.theguardian.com/world/rss", "nicho": "internacional", "ativo": True},
    {"name": "BBC News", "rss": "https://feeds.bbci.co.uk/news/rss.xml", "nicho": "internacional", "ativo": True},
]

class SistemaLocalNoticias:
    def __init__(self):
        self.noticias = self.carregar_noticias()
        self.fontes = FONTES_SISTEMA
        self.log_file = ARQUIVO_LOG
        
    def carregar_noticias(self):
        """Carrega notícias do arquivo JSON"""
        try:
            if os.path.exists(ARQUIVO_NOTICIAS):
                with open(ARQUIVO_NOTICIAS, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar notícias: {e}")
        return []
    
    def salvar_noticias(self):
        """Salva notícias no arquivo JSON"""
        try:
            with open(ARQUIVO_NOTICIAS, 'w', encoding='utf-8') as f:
                json.dump(self.noticias, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar notícias: {e}")
    
    def log_evento(self, mensagem):
        """Registra evento no log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {mensagem}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Erro ao escrever log: {e}")
    
    def checar_plagio_local(self, title, resumo):
        """Verifica plágio local"""
        for noticia in self.noticias:
            sim_titulo = SequenceMatcher(None, noticia.get("titulo", ""), title).ratio()
            sim_resumo = SequenceMatcher(None, noticia.get("resumo", ""), resumo).ratio()
            if sim_titulo > 0.8 or sim_resumo > 0.8:
                return True
        return False
    
    def coletar_noticias(self):
        """Coleta notícias das fontes RSS"""
        self.log_evento("🚀 Iniciando coleta de notícias")
        
        total_salvas = 0
        total_existentes = 0
        
        for fonte in self.fontes:
            if not fonte.get("ativo", True):
                continue
                
            try:
                self.log_evento(f"📰 Coletando de: {fonte['name']} ({fonte['nicho']})")
                feed = feedparser.parse(fonte["rss"])
                
                if not feed.entries:
                    self.log_evento(f"⚠️  {fonte['name']}: Sem notícias disponíveis")
                    continue
                
                for entry in feed.entries[:3]:  # Máximo 3 notícias por fonte
                    title = entry.get("title", "(Sem título)")
                    link = entry.get("link", "")
                    description = entry.get("summary", "")
                    
                    # Criar resumo
                    resumo = " ".join(description.split()[:60]) + ("..." if len(description.split()) > 60 else "")
                    
                    # Verificar se já existe
                    if any(n["link"] == link for n in self.noticias):
                        total_existentes += 1
                        continue
                    
                    # Verificar plágio
                    is_plagio = self.checar_plagio_local(title, resumo)
                    
                    if not is_plagio:
                        noticia = {
                            "titulo": title,
                            "link": link,
                            "resumo": resumo,
                            "fonte": fonte["name"],
                            "nicho": fonte["nicho"],
                            "data_insercao": datetime.now().isoformat(),
                            "aprovado": True,
                            "plagio_local": False,
                            "publicado": False
                        }
                        
                        self.noticias.append(noticia)
                        total_salvas += 1
                        self.log_evento(f"✅ {fonte['name']}: {title[:50]}...")
                    else:
                        total_existentes += 1
                        self.log_evento(f"❌ {fonte['name']}: {title[:50]}... (duplicada)")
                        
            except Exception as e:
                self.log_evento(f"❌ Erro ao coletar de {fonte['name']}: {e}")
        
        self.salvar_noticias()
        self.log_evento(f"📊 Coleta concluída: {total_salvas} salvas, {total_existentes} existentes")
        return total_salvas, total_existentes
    
    def limpar_noticias_antigas(self):
        """Remove notícias com mais de 7 dias"""
        self.log_evento("🧹 Iniciando limpeza de notícias antigas")
        
        data_limite = datetime.now() - timedelta(days=7)
        noticias_antes = len(self.noticias)
        
        self.noticias = [
            n for n in self.noticias 
            if datetime.fromisoformat(n["data_insercao"]) > data_limite
        ]
        
        noticias_removidas = noticias_antes - len(self.noticias)
        self.salvar_noticias()
        
        self.log_evento(f"🧹 Limpeza concluída: {noticias_removidas} notícias removidas")
        return noticias_removidas
    
    def health_check_fontes(self):
        """Verifica se as fontes RSS estão funcionando"""
        self.log_evento("🔍 Iniciando health check das fontes")
        
        fontes_quebradas = []
        
        for fonte in self.fontes:
            try:
                feed = feedparser.parse(fonte["rss"])
                if not feed.entries:
                    fontes_quebradas.append(fonte["name"])
                    self.log_evento(f"⚠️  {fonte['name']}: Sem notícias")
                else:
                    self.log_evento(f"✅ {fonte['name']}: OK ({len(feed.entries)} notícias)")
            except Exception as e:
                fontes_quebradas.append(fonte["name"])
                self.log_evento(f"❌ {fonte['name']}: Erro - {e}")
        
        if fontes_quebradas:
            self.log_evento(f"⚠️  Fontes com problemas: {', '.join(fontes_quebradas)}")
        else:
            self.log_evento("✅ Todas as fontes estão funcionando")
        
        return len(fontes_quebradas) == 0
    
    def publicar_noticias(self):
        """Simula publicação de notícias (1 por nicho)"""
        self.log_evento("📤 Iniciando publicação de notícias")
        
        nichos_publicados = set()
        publicadas = 0
        
        # Ordenar por data de inserção (mais recentes primeiro)
        noticias_ordenadas = sorted(
            [n for n in self.noticias if n["aprovado"] and not n["publicado"]],
            key=lambda x: x["data_insercao"],
            reverse=True
        )
        
        for noticia in noticias_ordenadas:
            if noticia["nicho"] not in nichos_publicados:
                noticia["publicado"] = True
                noticia["data_publicacao"] = datetime.now().isoformat()
                nichos_publicados.add(noticia["nicho"])
                publicadas += 1
                
                self.log_evento(f"📤 Publicada: {noticia['titulo'][:50]}... ({noticia['nicho']})")
        
        self.salvar_noticias()
        self.log_evento(f"📤 Publicação concluída: {publicadas} notícias publicadas")
        return publicadas
    
    def mostrar_estatisticas(self):
        """Mostra estatísticas do sistema"""
        if not self.noticias:
            print("Nenhuma notícia no sistema.")
            return
        
        print("\n📊 ESTATÍSTICAS DO SISTEMA")
        print("=" * 50)
        
        # Estatísticas gerais
        total = len(self.noticias)
        aprovadas = len([n for n in self.noticias if n["aprovado"]])
        publicadas = len([n for n in self.noticias if n.get("publicado", False)])
        
        print(f"📰 Total de notícias: {total}")
        print(f"✅ Aprovadas: {aprovadas}")
        print(f"📤 Publicadas: {publicadas}")
        print(f"⏳ Aguardando: {aprovadas - publicadas}")
        
        # Por nicho
        nichos = {}
        for noticia in self.noticias:
            nicho = noticia["nicho"]
            nichos[nicho] = nichos.get(nicho, 0) + 1
        
        print(f"\n📈 POR NICHO:")
        for nicho, count in sorted(nichos.items()):
            print(f"  {nicho.capitalize()}: {count} notícias")
        
        # Por fonte
        fontes = {}
        for noticia in self.noticias:
            fonte = noticia["fonte"]
            fontes[fonte] = fontes.get(fonte, 0) + 1
        
        print(f"\n📰 POR FONTE:")
        for fonte, count in sorted(fontes.items()):
            print(f"  {fonte}: {count} notícias")
    
    def executar_ciclo_completo(self):
        """Executa um ciclo completo do sistema"""
        print("🔄 EXECUTANDO CICLO COMPLETO DO SISTEMA")
        print("=" * 60)
        
        # 1. Coletar notícias
        salvas, existentes = self.coletar_noticias()
        print(f"📰 Coleta: {salvas} novas, {existentes} existentes")
        
        # 2. Health check
        health_ok = self.health_check_fontes()
        print(f"🔍 Health check: {'✅ OK' if health_ok else '❌ Problemas'}")
        
        # 3. Publicar notícias
        publicadas = self.publicar_noticias()
        print(f"📤 Publicação: {publicadas} notícias")
        
        # 4. Mostrar estatísticas
        self.mostrar_estatisticas()
        
        print("\n✅ Ciclo completo executado com sucesso!")

def agendar_tarefas(sistema):
    """Agenda as tarefas do sistema"""
    # Coleta: 4x por dia
    schedule.every().day.at("20:00").do(sistema.coletar_noticias)
    schedule.every().day.at("20:10").do(sistema.coletar_noticias)
    schedule.every().day.at("20:20").do(sistema.coletar_noticias)
    schedule.every().day.at("20:30").do(sistema.coletar_noticias)
    
    # Publicação: 3x por semana às 6:40
    schedule.every().monday.at("06:40").do(sistema.publicar_noticias)
    schedule.every().tuesday.at("06:40").do(sistema.publicar_noticias)
    schedule.every().wednesday.at("06:40").do(sistema.publicar_noticias)
    schedule.every().friday.at("06:40").do(sistema.publicar_noticias)
    
    # Limpeza: Domingo às 3:00
    schedule.every().sunday.at("03:00").do(sistema.limpar_noticias_antigas)
    
    # Health check: Diário às 8:00
    schedule.every().day.at("08:00").do(sistema.health_check_fontes)

def main():
    """Função principal"""
    print("🎯 SISTEMA LOCAL COMPLETO - AGREGAÇÃO DE NOTÍCIAS")
    print("=" * 70)
    print("Este sistema simula todas as funcionalidades do projeto:")
    print("  ✅ Coleta automática de RSS")
    print("  ✅ Verificação de plágio")
    print("  ✅ Publicação por nicho")
    print("  ✅ Limpeza automática")
    print("  ✅ Health check das fontes")
    print("  ✅ Agendamento de tarefas")
    print("  ✅ Logs e estatísticas")
    print("=" * 70)
    
    sistema = SistemaLocalNoticias()
    
    # Executar ciclo inicial
    sistema.executar_ciclo_completo()
    
    # Perguntar se quer agendar tarefas
    resposta = input("\n🤔 Quer agendar as tarefas para execução automática? (s/n): ")
    
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        print("\n⏰ Agendando tarefas...")
        agendar_tarefas(sistema)
        
        print("📅 Tarefas agendadas:")
        print("  📰 Coleta: 20:00, 20:10, 20:20, 20:30 (diário)")
        print("  📤 Publicação: 6:40 (seg, ter, qua, sex)")
        print("  🧹 Limpeza: 3:00 (domingo)")
        print("  🔍 Health check: 8:00 (diário)")
        
        print("\n🔄 Sistema rodando... Pressione Ctrl+C para parar")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        except KeyboardInterrupt:
            print("\n⏹️  Sistema parado pelo usuário")
    else:
        print("\n✅ Sistema executado uma vez. Use 'python sistema_local_completo.py' para executar novamente.")

if __name__ == "__main__":
    main() 