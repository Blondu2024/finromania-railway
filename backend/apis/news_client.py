"""NewsAPI client for financial news"""
import requests
from datetime import datetime
from typing import List, Dict
import logging
from ..config.settings import settings

logger = logging.getLogger(__name__)

class NewsAPIClient:
    """Client pentru NewsAPI - știri financiare"""
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self):
        self.api_key = settings.API_KEY_NEWSAPI
    
    def get_business_headlines(self, limit: int = 20) -> List[Dict]:
        """Obține top business headlines"""
        try:
            url = f"{self.BASE_URL}/top-headlines"
            params = {
                'category': 'business',
                'language': 'en',
                'pageSize': limit,
                'apiKey': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                return self._format_articles(data.get('articles', []))
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching business headlines: {e}")
            return []
    
    def get_financial_news(self, keywords: str = "stocks OR markets", limit: int = 20) -> List[Dict]:
        """Obține știri financiare după keywords"""
        try:
            url = f"{self.BASE_URL}/everything"
            params = {
                'q': keywords,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': limit,
                'apiKey': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                return self._format_articles(data.get('articles', []))
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching financial news: {e}")
            return []
    
    def _format_articles(self, articles: List[Dict]) -> List[Dict]:
        """Formatează articolele în structura noastră"""
        formatted = []
        
        for article in articles:
            if not article.get('title'):
                continue
            
            formatted.append({
                'title': article['title'],
                'description': article.get('description', ''),
                'content': article.get('content', ''),
                'url': article['url'],
                'image_url': article.get('urlToImage'),
                'source': {
                    'name': article['source']['name'],
                    'url': article['url']
                },
                'author': article.get('author'),
                'published_at': article['publishedAt'],
                'language': 'en',
                'fetched_at': datetime.utcnow()
            })
        
        return formatted
