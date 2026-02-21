"""Service pentru gestionarea știrilor"""
from typing import List, Dict, Optional
import logging
from datetime import datetime
import uuid
from apis.romanian_rss_client import romanian_rss_client
from apis.international_rss_client import international_rss_client
from apis.article_scraper import article_scraper
from config.database import get_database

logger = logging.getLogger(__name__)

class NewsService:
    """Service pentru știri din surse românești și internaționale"""
    
    def __init__(self):
        self.ro_rss_client = romanian_rss_client
        self.intl_rss_client = international_rss_client
        self.scraper = article_scraper
    
    async def fetch_and_store_news(self) -> int:
        """Fetch știri noi din surse românești și salvează în DB"""
        try:
            logger.info("🔄 Fetching Romanian news from RSS sources...")
            
            # Get news from Romanian RSS sources
            articles = self.ro_rss_client.fetch_all_news(limit_per_source=15)
            
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
                    article['full_content_scraped'] = False
                    article['news_type'] = 'romania'  # Tag for Romanian news
                    await db.articles.insert_one(article)
                    count += 1
            
            logger.info(f"✅ Stored {count} new Romanian articles")
            return count
            
        except Exception as e:
            logger.error(f"Error fetching Romanian news: {e}")
            return 0
    
    async def fetch_and_store_international_news(self) -> int:
        """Fetch știri internaționale și salvează în DB"""
        try:
            logger.info("🔄 Fetching International news from RSS sources...")
            
            # Get news from international RSS sources
            articles = self.intl_rss_client.fetch_all_news(limit_per_source=10)
            
            if not articles:
                logger.warning("No international news fetched")
                return 0
            
            db = await get_database()
            count = 0
            
            for article in articles:
                # Check dacă există deja (by URL)
                existing = await db.articles_international.find_one({'url': article['url']})
                
                if not existing:
                    article['created_at'] = datetime.utcnow().isoformat()
                    article['full_content_scraped'] = False
                    article['news_type'] = 'international'
                    await db.articles_international.insert_one(article)
                    count += 1
            
            logger.info(f"✅ Stored {count} new international articles")
            return count
            
        except Exception as e:
            logger.error(f"Error fetching international news: {e}")
            return 0
    
    async def get_latest_news(self, limit: int = 20, news_type: str = 'all') -> List[Dict]:
        """Obține ultimele știri din DB
        
        Args:
            limit: numărul maxim de știri
            news_type: 'romania', 'international', sau 'all'
        """
        db = await get_database()
        
        if news_type == 'international':
            cursor = db.articles_international.find(
                {},
                {"_id": 0}
            ).sort('published_at', -1).limit(limit)
            return await cursor.to_list(length=limit)
        elif news_type == 'romania':
            cursor = db.articles.find(
                {},
                {"_id": 0}
            ).sort('published_at', -1).limit(limit)
            return await cursor.to_list(length=limit)
        else:
            # Get both and merge
            ro_cursor = db.articles.find({}, {"_id": 0}).sort('published_at', -1).limit(limit // 2)
            intl_cursor = db.articles_international.find({}, {"_id": 0}).sort('published_at', -1).limit(limit // 2)
            
            ro_articles = await ro_cursor.to_list(length=limit // 2)
            intl_articles = await intl_cursor.to_list(length=limit // 2)
            
            # Merge and sort by date
            all_articles = ro_articles + intl_articles
            all_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
            return all_articles[:limit]
    
    async def get_international_news(self, limit: int = 20) -> List[Dict]:
        """Obține ultimele știri internaționale"""
        db = await get_database()
        cursor = db.articles_international.find(
            {},
            {"_id": 0}
        ).sort('published_at', -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """Obține un articol specific și extrage conținutul complet dacă nu există"""
        db = await get_database()
        article = await db.articles.find_one({'id': article_id}, {"_id": 0})
        
        if not article:
            return None
        
        # Dacă nu avem conținutul complet, facem scraping
        if not article.get('full_content_scraped') and article.get('url'):
            try:
                logger.info(f"Scraping full content for article: {article_id}")
                scraped_data = self.scraper.scrape_article(article['url'])
                
                if scraped_data and scraped_data.get('content'):
                    # Actualizăm articolul cu conținutul complet
                    update_data = {
                        'content': scraped_data['content'],
                        'full_content_scraped': True,
                        'scraped_at': datetime.utcnow().isoformat()
                    }
                    
                    # Actualizăm imaginea dacă nu există
                    if not article.get('image_url') and scraped_data.get('image_url'):
                        update_data['image_url'] = scraped_data['image_url']
                    
                    await db.articles.update_one(
                        {'id': article_id},
                        {'$set': update_data}
                    )
                    
                    # Actualizăm articolul local
                    article['content'] = scraped_data['content']
                    article['full_content_scraped'] = True
                    if not article.get('image_url') and scraped_data.get('image_url'):
                        article['image_url'] = scraped_data['image_url']
                    
                    logger.info(f"✅ Successfully scraped full content for: {article_id}")
                else:
                    # Marcăm că am încercat să facem scraping
                    await db.articles.update_one(
                        {'id': article_id},
                        {'$set': {'full_content_scraped': True, 'scrape_failed': True}}
                    )
                    article['full_content_scraped'] = True
                    article['scrape_failed'] = True
                    logger.warning(f"Could not scrape content for: {article_id}")
                    
            except Exception as e:
                logger.error(f"Error scraping article {article_id}: {e}")
        
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
