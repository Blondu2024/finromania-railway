"""
Migration script to add subscription fields to existing users
Run this once to update the schema
"""
import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = "finromania"

async def migrate_users():
    """Add subscription fields to all existing users"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔄 Starting migration: Adding subscription fields...")
    
    # Update all users to have subscription fields
    result = await db.users.update_many(
        {},  # All users
        {
            "$set": {
                "subscription_level": "free",
                "ai_queries_today": 0,
                "ai_queries_reset_at": datetime.now(timezone.utc).isoformat(),
                "experience_level": "beginner",
                "unlocked_levels": ["beginner"]
            }
        }
    )
    
    print(f"✅ Migration complete!")
    print(f"   - Modified {result.modified_count} users")
    print(f"   - Matched {result.matched_count} users")
    
    # Show sample user
    sample = await db.users.find_one({}, {"_id": 0})
    if sample:
        print(f"\n📋 Sample user after migration:")
        print(f"   - subscription_level: {sample.get('subscription_level', 'N/A')}")
        print(f"   - experience_level: {sample.get('experience_level', 'N/A')}")
        print(f"   - unlocked_levels: {sample.get('unlocked_levels', [])}")
        print(f"   - ai_queries_today: {sample.get('ai_queries_today', 0)}")
    
    # Create indexes for performance
    print("\n🔧 Creating indexes...")
    await db.users.create_index("user_id", unique=True)
    await db.users.create_index("email", unique=True)
    await db.users.create_index("subscription_level")
    await db.quiz_attempts.create_index([("user_id", 1), ("timestamp", -1)])
    await db.fiscal_calculations.create_index([("user_id", 1), ("timestamp", -1)])
    await db.ai_interactions.create_index([("user_id", 1), ("timestamp", -1)])
    
    print("✅ Indexes created successfully!")
    
    client.close()
    print("\n✨ Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(migrate_users())
