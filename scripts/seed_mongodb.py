import os
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("A variável de ambiente MONGO_URI não está definida.")

FONTES = [
    # =============================================================================
    # NICHOS PRINCIPAIS
    # =============================================================================
    
    # Tecnologia
    {"name": "G1 Tecnologia", "rss": "https://g1.globo.com/dynamo/tecnologia/rss2.xml", "nicho": "tecnologia", "ativo": True},
    {"name": "Canaltech", "rss": "https://feed.canatech.com.br/", "nicho": "tecnologia", "ativo": True},
    {"name": "The Verge", "rss": "https://www.theverge.com/rss/index.xml", "nicho": "tecnologia", "ativo": True},
    {"name": "TechCrunch", "rss": "https://techcrunch.com/feed/", "nicho": "tecnologia", "ativo": True},
    {"name": "Wired", "rss": "https://www.wired.com/feed/rss", "nicho": "tecnologia", "ativo": True},
    
    # Esportes
    {"name": "Globo Esporte", "rss": "https://ge.globo.com/rss/ultimas.xml", "nicho": "esportes", "ativo": True},
    {"name": "ESPN Brasil", "rss": "https://www.espn.com.br/espn/rss/news", "nicho": "esportes", "ativo": True},
    {"name": "BBC Sport", "rss": "https://feeds.bbci.co.uk/sport/rss.xml", "nicho": "esportes", "ativo": True},
    {"name": "ESPN", "rss": "https://www.espn.com/espn/rss/news", "nicho": "esportes", "ativo": True},
    
    # Saúde
    {"name": "G1 Saúde", "rss": "https://g1.globo.com/dynamo/saude/rss2.xml", "nicho": "saude", "ativo": True},
    {"name": "BBC Health", "rss": "https://feeds.bbci.co.uk/news/health/rss.xml", "nicho": "saude", "ativo": True},
    {"name": "WHO News", "rss": "https://www.who.int/feeds/entity/mediacentre/news/en/rss.xml", "nicho": "saude", "ativo": True},
    {"name": "Medical News Today", "rss": "https://www.medicalnewstoday.com/rss.xml", "nicho": "saude", "ativo": True},
    
    # Economia
    {"name": "Valor Econômico", "rss": "https://valor.globo.com/rss.xml", "nicho": "economia", "ativo": True},
    {"name": "BBC Business", "rss": "https://feeds.bbci.co.uk/news/business/rss.xml", "nicho": "economia", "ativo": True},
    {"name": "CNN Business", "rss": "http://rss.cnn.com/rss/money_latest.rss", "nicho": "economia", "ativo": True},
    {"name": "Reuters Business", "rss": "https://www.reuters.com/arc/outboundfeeds/rss/", "nicho": "economia", "ativo": True},
    
    # =============================================================================
    # NICHOS EXPANDIDOS - RECOMENDAÇÕES
    # =============================================================================
    
    # Ciência
    {"name": "Nature", "rss": "https://www.nature.com/nature.rss", "nicho": "ciencia", "ativo": True},
    {"name": "Science Magazine", "rss": "https://www.science.org/rss/news_current.xml", "nicho": "ciencia", "ativo": True},
    {"name": "Scientific American", "rss": "https://rss.sciam.com/ScientificAmerican-Global", "nicho": "ciencia", "ativo": True},
    {"name": "BBC Science", "rss": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "nicho": "ciencia", "ativo": True},
    {"name": "New Scientist", "rss": "https://www.newscientist.com/feed/home/?cmpid=RSS", "nicho": "ciencia", "ativo": True},
    
    # Política
    {"name": "BBC Politics", "rss": "https://feeds.bbci.co.uk/news/politics/rss.xml", "nicho": "politica", "ativo": True},
    {"name": "CNN Politics", "rss": "http://rss.cnn.com/rss/edition_politics.rss", "nicho": "politica", "ativo": True},
    {"name": "Reuters Politics", "rss": "https://www.reuters.com/arc/outboundfeeds/rss/", "nicho": "politica", "ativo": True},
    {"name": "G1 Política", "rss": "https://g1.globo.com/dynamo/politica/rss2.xml", "nicho": "politica", "ativo": True},
    
    # Entretenimento
    {"name": "Variety", "rss": "https://variety.com/feed", "nicho": "entretenimento", "ativo": True},
    {"name": "Hollywood Reporter", "rss": "https://www.hollywoodreporter.com/feed", "nicho": "entretenimento", "ativo": True},
    {"name": "BBC Entertainment", "rss": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "nicho": "entretenimento", "ativo": True},
    {"name": "G1 Pop & Arte", "rss": "https://g1.globo.com/dynamo/pop-arte/rss2.xml", "nicho": "entretenimento", "ativo": True},
    
    # Educação
    {"name": "Times Higher Education", "rss": "https://www.timeshighereducation.com/rss", "nicho": "educacao", "ativo": True},
    {"name": "EdSurge", "rss": "https://www.edsurge.com/feed", "nicho": "educacao", "ativo": True},
    {"name": "BBC Education", "rss": "https://feeds.bbci.co.uk/news/education/rss.xml", "nicho": "educacao", "ativo": True},
    {"name": "G1 Educação", "rss": "https://g1.globo.com/dynamo/educacao/rss2.xml", "nicho": "educacao", "ativo": True},
    
    # =============================================================================
    # FONTES ESPECIALIZADAS
    # =============================================================================
    
    # Startups & Inovação
    {"name": "VentureBeat", "rss": "https://venturebeat.com/feed/", "nicho": "startups", "ativo": True},
    {"name": "Startup Grind", "rss": "https://www.startupgrind.com/feed/", "nicho": "startups", "ativo": True},
    {"name": "Crunchbase News", "rss": "https://news.crunchbase.com/feed/", "nicho": "startups", "ativo": True},
    
    # Fintech & Criptomoedas
    {"name": "Finextra", "rss": "https://www.finextra.com/rss/feed.aspx", "nicho": "fintech", "ativo": True},
    {"name": "CoinDesk", "rss": "https://www.coindesk.com/arc/outboundfeeds/rss/", "nicho": "fintech", "ativo": True},
    {"name": "CoinTelegraph", "rss": "https://cointelegraph.com/rss", "nicho": "fintech", "ativo": True},
    
    # Inteligência Artificial & Machine Learning
    {"name": "MIT Technology Review", "rss": "https://www.technologyreview.com/feed", "nicho": "ia", "ativo": True},
    {"name": "AI News", "rss": "https://artificialintelligence-news.com/feed/", "nicho": "ia", "ativo": True},
    {"name": "DeepAI", "rss": "https://deepai.org/feed", "nicho": "ia", "ativo": True},
    
    # Sustentabilidade & Meio Ambiente
    {"name": "BBC Environment", "rss": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "nicho": "sustentabilidade", "ativo": True},
    {"name": "GreenBiz", "rss": "https://www.greenbiz.com/rss.xml", "nicho": "sustentabilidade", "ativo": True},
    {"name": "Environmental News Network", "rss": "https://www.enn.com/rss.xml", "nicho": "sustentabilidade", "ativo": True},
    
    # =============================================================================
    # FONTES INTERNACIONAIS
    # =============================================================================
    
    # Inglês (Principais)
    {"name": "Reuters", "rss": "https://www.reuters.com/arc/outboundfeeds/rss/", "nicho": "internacional", "ativo": True},
    {"name": "Associated Press", "rss": "https://feeds.ap.org/ap/technology", "nicho": "internacional", "ativo": True},
    {"name": "The Guardian", "rss": "https://www.theguardian.com/world/rss", "nicho": "internacional", "ativo": True},
    
    # Espanhol
    {"name": "El País", "rss": "https://elpais.com/tag/rss/tecnologia/a/", "nicho": "internacional", "ativo": True},
    {"name": "BBC Mundo", "rss": "https://feeds.bbci.co.uk/mundo/rss.xml", "nicho": "internacional", "ativo": True},
    
    # Francês
    {"name": "Le Monde", "rss": "https://www.lemonde.fr/rss/une.xml", "nicho": "internacional", "ativo": True},
    {"name": "RFI", "rss": "https://www.rfi.fr/fr/rss", "nicho": "internacional", "ativo": True},
]

def seed_database():
    try:
        client = MongoClient(MONGO_URI)
        db = client.get_default_database()
        collection = db["fontes_noticias"]
        
        adicionadas = 0
        for fonte in FONTES:
            if not collection.find_one({"rss": fonte["rss"]}):
                collection.insert_one(fonte)
                adicionadas += 1
                logger.info(f"Adicionada: {fonte['name']} ({fonte['nicho']})")
        
        logger.info(f"População do banco concluída. {adicionadas} novas fontes adicionadas.")
        
        # Estatísticas por nicho
        pipeline = [
            {"$group": {"_id": "$nicho", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        stats = list(collection.aggregate(pipeline))
        
        logger.info("Estatísticas por nicho:")
        for stat in stats:
            logger.info(f"  {stat['_id']}: {stat['count']} fontes")
            
    except Exception as e:
        logger.error(f"Erro ao popular o banco de dados: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()

if __name__ == "__main__":
    seed_database() 