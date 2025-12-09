from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "auth_db")

_client = None
_db = None

def get_db():
    global _client, _db
    if _client is None:
        _client = MongoClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db

db = get_db()