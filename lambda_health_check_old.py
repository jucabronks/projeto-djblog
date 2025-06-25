import requests
from utils import setup_logging, get_collection

logger = setup_logging()

FAILURE_THRESHOLD = 3

def lambda_handler(event, context):
    try:
        client, db = get_collection("fontes_noticias")
        collection = db["fontes_noticias"]
        
        fontes_ativas = list(collection.find({"ativo": True}))
        logger.info(f"Verificando {len(fontes_ativas)} fontes ativas.")

        for fonte in fontes_ativas:
            try:
                response = requests.head(fonte["rss"], timeout=10)
                response.raise_for_status()
                # Se sucesso, reseta a contagem de falhas
                if "failure_count" in fonte:
                    collection.update_one({"_id": fonte["_id"]}, {"$unset": {"failure_count": ""}})
            except requests.RequestException as e:
                logger.warning(f"Falha ao verificar a fonte {fonte['name']} ({fonte['rss']}): {e}")
                
                # Incrementa a contagem de falhas
                failure_count = fonte.get("failure_count", 0) + 1
                
                if failure_count >= FAILURE_THRESHOLD:
                    # Desativa a fonte após atingir o limite
                    collection.update_one({"_id": fonte["_id"]}, {"$set": {"ativo": False, "failure_count": failure_count}})
                    logger.error(f"Fonte {fonte['name']} desativada após {failure_count} falhas consecutivas.")
                else:
                    collection.update_one({"_id": fonte["_id"]}, {"$set": {"failure_count": failure_count}})
        
        client.close()
        return {"status": "success", "checked_sources": len(fontes_ativas)}

    except Exception as e:
        logger.error(f"Erro no health check de fontes: {e}")
        raise

if __name__ == "__main__":
    lambda_handler({}, {}) 