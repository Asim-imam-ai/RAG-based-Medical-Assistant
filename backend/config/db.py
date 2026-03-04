import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env
load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")

if not MONGO_URI:
    raise ValueError("MONGODB_URI not found in .env")

client = MongoClient(MONGO_URI)

db = client["medical_assistant"]
collection = db["users"]