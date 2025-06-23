from pymongo import MongoClient
import os

MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)

db_names = client.list_database_names()
print("Bancos disponíveis:")
for db_name in db_names:
    db = client[db_name]
    print(f"- {db_name}: {db.list_collection_names()}") 