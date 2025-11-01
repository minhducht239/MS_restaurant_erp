import motor.motor_asyncio
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
DB_NAME = os.getenv("DB_NAME", "staff_service")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]