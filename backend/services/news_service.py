"""Service pentru gestionarea știrilor"""
from typing import List, Dict, Optional
import logging
from datetime import datetime
import uuid
from apis.news_client import NewsAPIClient
from config.database import get_database
from services.ai_service import ai_service

logger = logging.getLogger(__name__)

class NewsService:
    """Service pentru știri"""
    
    def __init__(self):
        self.news_client = NewsAPIClient()
    
    async def fetch_and_store_news(self) -> int:
        """Fetch știri noi și salvează în DB"""
        try:
            logger.info("🔄 Fetching news...")
            
            # Get business headlines
            headlines = self.news_client.get_business_headlines(limit=20)
            
            # Get financial news
            financial = self.news_client.get_financial_news(
                keywords="stocks OR markets OR nasdaq OR sp500",
                limit=20
            )
            
            # Combine și deduplicate
            all_news = headlines + financial
            unique_news = self._deduplicate_news(all_news)
            
            if not unique_news:
                logger.warning("No news fetched")
                return 0
            
            db = await get_database()
            count = 0
            
            for article in unique_news:
                # Check dacă există deja
                existing = await db.articles.find_one({'url': article['url']})
                
                if not existing:
                    # Generate unique ID for internal routing
                    article['id'] = str(uuid.uuid4())
                    article['created_at'] = datetime.utcnow().isoformat()
                    article['is_translated'] = False
                    await db.articles.insert_one(article)
                    count += 1
            
            logger.info(f"✅ Stored {count} new articles")
            return count
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return 0
    
    def _deduplicate_news(self, news: List[Dict]) -> List[Dict]:
        """Remove duplicate news by URL"""
        seen_urls = set()
        unique = []
        
        for article in news:
            url = article.get('url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(article)
        
        return unique
    
    async def get_latest_news(self, limit: int = 20) -> List[Dict]:
        """Obține ultimele știri din DB"""
        db = await get_database()
        cursor = db.articles.find(
            {},
            {"_id": 0}
        ).sort('published_at', -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """Obține un articol specific și îl traduce dacă nu e tradus"""
        db = await get_database()
        article = await db.articles.find_one({'id': article_id}, {"_id": 0})
        
        if not article:
            return None
        
        # Translate if not already translated
        if not article.get('is_translated'):
            try:
                translated = await ai_service.translate_and_rewrite_article(article)
                # Update in DB
                await db.articles.update_one(
                    {'id': article_id},
                    {'$set': {
                        'title_ro': translated.get('title_ro'),
                        'description_ro': translated.get('description_ro'),
                        'content_ro': translated.get('content_ro'),
                        'is_translated': True
                    }}
                )
                return translated
            except Exception as e:
                logger.error(f"Error translating article: {e}")
                return article
        
        return article
    
    async def search_news_by_topic(self, topic: str, limit: int = 10) -> List[Dict]:
        """Caută știri legate de un topic (pentru pagina de detalii indici)"""
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
