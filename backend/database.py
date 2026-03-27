from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import certifi  # <-- Added to handle macOS SSL certificates

load_dotenv()

# --- CONFIGURATION ---
DEFAULT_CLOUD_URI = "mongodb+srv://olinmascarenhas_db_user:nhHZA4V1NBfjcjEk@cai-database.2r1xe3d.mongodb.net/?retryWrites=true&w=majority&appName=CAI-Database"

MONGODB_URL = os.getenv("MONGODB_URL", DEFAULT_CLOUD_URI)
DATABASE_NAME = os.getenv("DATABASE_NAME", "cai_gst_db")

# Create the client with the SSL certificate fix
# tlsCAFile=certifi.where() tells Python to use the certifi bundle instead of the missing macOS ones
client = AsyncIOMotorClient(
    MONGODB_URL,
    tlsCAFile=certifi.where()
)
db = client[DATABASE_NAME]

# --- COLLECTIONS ---
users_collection = db["users"]
clients_collection = db["clients"]
invoices_collection = db["invoices"]
reconciliations_collection = db["reconciliations"]
filings_collection = db["filings"]
audit_logs_collection = db["audit_logs"]

# --- INDEXES ---


async def create_indexes():
    try:
        await users_collection.create_index("email", unique=True)
        await clients_collection.create_index("gstin")
        print("Successfully connected to MongoDB and created indexes.")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
