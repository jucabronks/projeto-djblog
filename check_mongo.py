from pymongo import MongoClient
import os
from datetime import datetime, timezone, timedelta

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_default_database()
col = db["noticias_coletadas"]
BRT = timezone(timedelta(hours=-3))

for n in col.find().sort("data_insercao", -1):
    dt_utc = n.get("data_insercao")
    if isinstance(dt_utc, datetime):
        dt_brt = dt_utc.astimezone(BRT)
        print(f"UTC: {dt_utc} | BRT: {dt_brt} | {n.get('titulo')}")
    else:
        print(dt_utc, n.get("titulo")) 