"""
MongoDB database configuration and connection management.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConfig:
    """Database configuration settings."""

    def __init__(self):
        self.MONGODB_URI = os.getenv(
            'MONGODB_URI',
            'mongodb://localhost:27017/scholarai'
        )
        self.DATABASE_NAME = os.getenv('DATABASE_NAME', 'scholarai')
        self.CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', '5'))
        self.SERVER_SELECTION_TIMEOUT = int(os.getenv('DB_SERVER_SELECTION_TIMEOUT', '5'))


# Global MongoDB client and database instances
mongo_client: Optional[MongoClient] = None
mongo_db = None
db_config = DatabaseConfig()


def get_db():
    """
    Get the current database instance.

    Returns:
        Database: MongoDB database instance

    Raises:
        RuntimeError: If database is not initialized
    """
    if mongo_db is None:
        raise RuntimeError(
            "Database not initialized. Call init_db() before accessing the database."
        )
    return mongo_db


def init_db(app=None):
    """
    Initialize MongoDB connection.

    Args:
        app: Flask application instance (optional, for logging)

    Returns:
        MongoClient: MongoDB client instance

    Raises:
        ConnectionFailure: If unable to connect to MongoDB
    """
    global mongo_client, mongo_db

    if mongo_client is not None:
        # Already initialized
        return mongo_client

    try:
        # Create MongoDB client with connection settings
        mongo_client = MongoClient(
            db_config.MONGODB_URI,
            connectTimeoutMS=db_config.CONNECT_TIMEOUT * 1000,
            serverSelectionTimeoutMS=db_config.SERVER_SELECTION_TIMEOUT * 1000,
            # Retry settings
            retryWrites=True,
            w='majority',
        )

        # Test the connection
        mongo_client.admin.command('ping')

        # Extract database name from connection string or use default
        mongo_db = mongo_client[db_config.DATABASE_NAME]

        if app:
            app.logger.info(f"Successfully connected to MongoDB: {db_config.DATABASE_NAME}")
        else:
            print(f"✅ Successfully connected to MongoDB: {db_config.DATABASE_NAME}")

        return mongo_client

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        error_msg = (
            f"Failed to connect to MongoDB at {db_config.MONGODB_URI}. "
            f"Please ensure MongoDB is running and accessible."
        )
        if app:
            app.logger.error(error_msg)
        raise ConnectionFailure(error_msg) from e


def close_db():
    """Close MongoDB connection."""
    global mongo_client, mongo_db

    if mongo_client is not None:
        mongo_client.close()
        mongo_client = None
        mongo_db = None
        print("MongoDB connection closed")


def get_collection(collection_name: str):
    """
    Get a MongoDB collection.

    Args:
        collection_name: Name of the collection

    Returns:
        Collection: MongoDB collection instance
    """
    db = get_db()
    return db[collection_name]


def test_connection():
    """
    Test the MongoDB connection.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        init_db()
        # Ping the database
        mongo_client.admin.command('ping')
        return True
    except Exception as e:
        print(f"MongoDB connection test failed: {e}")
        return False


# Convenience exports
mongo = get_db
