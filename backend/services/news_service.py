"""Service pentru gestionarea știrilor"""
from typing import List, Dict
import logging
from datetime import datetime
from apis.news_client import NewsAPIClient
from config.database import get_database

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
                    article['created_at'] = datetime.utcnow()
                    article['is_rewritten'] = False
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
    
    async def get_latest_news(self, limit: int = 20, language: str = 'en') -> List[Dict]:
        """Obține ultimele știri din DB"""
        db = await get_database()
        cursor = db.articles.find(
            {'language': language}
        ).sort('published_at', -1).limit(limit)
        
        return await cursor.to_list(length=limit)
