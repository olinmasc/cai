from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "cai_gst_db")

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

# Collections — think of these as tables
users_collection = db["users"]
clients_collection = db["clients"]
invoices_collection = db["invoices"]
reconciliations_collection = db["reconciliations"]
filings_collection = db["filings"]
audit_logs_collection = db["audit_logs"]  # FEATURE 3: AUDIT LOGS


async def create_indexes():
    await users_collection.create_index("email", unique=True)
    await clients_collection.create_index("gstin")
