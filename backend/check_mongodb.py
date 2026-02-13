# Simple MongoDB connection checker
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/scholarai')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'scholarai')

print(f"Testing connection to: {MONGODB_URI[:30]}...")
print(f"Database: {DATABASE_NAME}")

try:
    client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Ping the database
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    print(f"✅ Database '{DATABASE_NAME}' is accessible")

    # List databases
    dbs = client.list_database_names()
    print(f"📊 Available databases: {len(dbs)}")

    # Get our database
    db = client[DATABASE_NAME]
    collections = db.list_collection_names()
    print(f"📁 Collections in '{DATABASE_NAME}': {len(collections)}")

except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting tips:")
    print("1. For MongoDB Atlas:")
    print("   - Check your connection string in .env")
    print("   - Whitelist your IP in MongoDB Atlas")
    print("2. For local MongoDB:")
    print("   - Ensure mongod service is running")
    print("   - Check port 27017 is accessible")
