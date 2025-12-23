"""Database configuration and connection"""
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def get_database():
    """Get database instance"""
    return db_instance.db

async def connect_to_mongodb():
    """Connect to MongoDB"""
    try:
        logger.info(f"Connecting to MongoDB: {settings.MONGO_URL}")
        db_instance.client = AsyncIOMotorClient(settings.MONGO_URL)
        db_instance.db = db_instance.client[settings.DB_NAME]
        
        # Test connection
        await db_instance.client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB: {settings.DB_NAME}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"❌ Could not connect to MongoDB: {e}")
        raise

async def close_mongodb_connection():
    """Close MongoDB connection"""
    try:
        if db_instance.client:
            db_instance.client.close()
            logger.info("✅ MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB: {e}")

async def create_indexes():
    """Create database indexes for performance"""
    db = db_instance.db
    
    # Articles indexes
    await db.articles.create_index('link', unique=True)
    await db.articles.create_index('published_at')
    await db.articles.create_index('source.name')
    await db.articles.create_index('language')
    
    # Stocks indexes
    await db.stocks_bvb.create_index('symbol', unique=True)
    await db.stocks_bvb.create_index('last_updated')
    
    await db.stocks_global.create_index('symbol', unique=True)
    await db.stocks_global.create_index('last_updated')
    
    # Currencies indexes
    await db.currencies.create_index('date', unique=True)
    
    logger.info("✅ Database indexes created")
