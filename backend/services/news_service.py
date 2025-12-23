"""Service pentru gestionarea știrilor"""
from typing import List, Dict, Optional
import logging
from datetime import datetime
import uuid
from apis.romanian_rss_client import romanian_rss_client
from config.database import get_database

logger = logging.getLogger(__name__)

class NewsService:
    """Service pentru știri din surse românești"""
    
    def __init__(self):
        self.rss_client = romanian_rss_client
    
    async def fetch_and_store_news(self) -> int:
        """Fetch știri noi din surse românești și salvează în DB"""
        try:
            logger.info("🔄 Fetching Romanian news from RSS sources...")
            
            # Get news from Romanian RSS sources
            articles = self.rss_client.fetch_all_news(limit_per_source=15)
            
            if not articles:
                logger.warning("No Romanian news fetched")
                return 0
            
            db = await get_database()
            count = 0
            
            for article in articles:
                # Check dacă există deja (by URL)
                existing = await db.articles.find_one({'url': article['url']})
                
                if not existing:
                    article['created_at'] = datetime.utcnow().isoformat()
                    await db.articles.insert_one(article)
                    count += 1
            
            logger.info(f"✅ Stored {count} new Romanian articles")
            return count
            
        except Exception as e:
            logger.error(f"Error fetching Romanian news: {e}")
            return 0
    
    async def get_latest_news(self, limit: int = 20) -> List[Dict]:
        """Obține ultimele știri din DB"""
        db = await get_database()
        cursor = db.articles.find(
            {},
            {"_id": 0}
        ).sort('published_at', -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """Obține un articol specific"""
        db = await get_database()
        article = await db.articles.find_one({'id': article_id}, {"_id": 0})
        return article
    
    async def search_news_by_topic(self, topic: str, limit: int = 10) -> List[Dict]:
        """Caută știri legate de un topic"""
        db = await get_database()
        
        # Search in title and description
        cursor = db.articles.find(
            {
                '$or': [
                    {'title': {'$regex': topic, '$options': 'i'}},
                    {'description': {'$regex': topic, '$options': 'i'}}
                ]
            },
            {"_id": 0}
        ).sort('published_at', -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def clear_old_articles(self, days: int = 30) -> int:
        """Șterge articolele mai vechi de X zile"""
        from datetime import timedelta
        
        db = await get_database()
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        result = await db.articles.delete_many({
            'published_at': {'$lt': cutoff_date}
        })
        
        logger.info(f"Deleted {result.deleted_count} old articles")
        return result.deleted_count
