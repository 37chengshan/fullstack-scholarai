"""
MongoDB connection test script.
Run this script to verify your MongoDB connection is working correctly.
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import test_connection, get_db, init_db


def main():
    """Test MongoDB connection."""
    print("=" * 60)
    print("Testing MongoDB Connection")
    print("=" * 60)

    try:
        # Test the connection
        if test_connection():
            print("\n✅ MongoDB connection successful!")

            # Get database info
            db = get_db()
            print(f"\n📊 Database Information:")
            print(f"   Database Name: {db.name}")

            # List collections
            collections = db.list_collection_names()
            print(f"   Collections: {len(collections)}")
            if collections:
                for coll in collections:
                    count = db[coll].count_documents({})
                    print(f"      - {coll}: {count} documents")
            else:
                print(f"      (No collections yet)")

            # Test write operation
            print("\n📝 Testing write operation...")
            test_collection = db.test_connection
            result = test_collection.insert_one({
                'test': True,
                'timestamp': 'now',
                'message': 'MongoDB connection test'
            })
            print(f"   Inserted document with _id: {result.inserted_id}")

            # Clean up test document
            test_collection.delete_one({'_id': result.inserted_id})
            print(f"   Cleaned up test document")

            print("\n" + "=" * 60)
            print("All tests passed! MongoDB is ready to use.")
            print("=" * 60)
            return 0
        else:
            print("\n❌ MongoDB connection failed!")
            print("\nTroubleshooting:")
            print("1. Check your MongoDB connection string in .env")
            print("2. For MongoDB Atlas, ensure your IP is whitelisted")
            print("3. For local MongoDB, ensure mongod service is running")
            print("   - Windows: net start MongoDB")
            print("   - Linux/Mac: sudo systemctl start mongod")
            return 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
