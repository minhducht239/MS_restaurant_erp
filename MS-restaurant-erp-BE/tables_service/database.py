import os
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "tables_service")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]