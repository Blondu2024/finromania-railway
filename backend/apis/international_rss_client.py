"""International RSS News Client - știri financiare internaționale"""
import feedparser
from datetime import datetime
from typing import List, Dict
import logging
import uuid
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class InternationalRSSClient:
    """Client pentru știri financiare internaționale via RSS"""
    
    # Surse RSS internaționale de știri financiare
    RSS_SOURCES = [
        {
            'name': 'Yahoo Finance',
            'url': 'https://finance.yahoo.com/news/rssindex',
            'category': 'markets',
            'priority': 1
        },
        {
            'name': 'CNBC Top News',
            'url': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'category': 'markets',
            'priority': 1
        },
        {
            'name': 'CNBC World Markets',
            'url': 'https://www.cnbc.com/id/100727362/device/rss/rss.html',
            'category': 'world',
            'priority': 2
        },
        {
            'name': 'Reuters Business',
            'url': 'https://www.reutersagency.com/feed/?best-topics=business-finance',
            'category': 'business',
            'priority': 1
        },
        {
            'name': 'MarketWatch',
            'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'category': 'markets',
            'priority': 2
        },
        {
            'name': 'Investing.com',
            'url': 'https://www.investing.com/rss/news.rss',
            'category': 'markets',
            'priority': 2
        },
        {
            'name': 'Bloomberg Markets',
            'url': 'https://feeds.bloomberg.com/markets/news.rss',
            'category': 'markets',
            'priority': 1
        },
        {
            'name': 'Financial Times',
            'url': 'https://www.ft.com/rss/home',
            'category': 'business',
            'priority': 1
        }
    ]
    
    def __init__(self):
        self.timeout = 10
    
    def fetch_all_news(self, limit_per_source: int = 10) -> List[Dict]:
        """Obține știri de la toate sursele RSS internaționale"""
        all_articles = []
        
        for source in self.RSS_SOURCES:
            try:
                articles = self._fetch_from_source(source, limit_per_source)
                all_articles.extend(articles)
                if articles:
                    logger.info(f"Fetched {len(articles)} articles from {source['name']}")
            except Exception as e:
                logger.error(f"Error fetching from {source['name']}: {e}")
        
        # Sort by date (newest first)
        all_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        return all_articles
    
    def _fetch_from_source(self, source: Dict, limit: int) -> List[Dict]:
        """Obține știri de la o sursă RSS specifică"""
        try:
            # Parse RSS feed with timeout
            feed = feedparser.parse(source['url'])
            
            if not feed.entries:
                logger.warning(f"No entries found for {source['name']}")
                return []
            
            articles = []
            for entry in feed.entries[:limit]:
                article = self._parse_entry(entry, source)
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing RSS from {source['name']}: {e}")
            return []
    
    def _parse_entry(self, entry, source: Dict) -> Dict:
        """Parsează un entry RSS într-un articol"""
        try:
            # Get title
            title = entry.get('title', '').strip()
            if not title:
                return None
            
            # Get description/summary
            description = ''
            if 'summary' in entry:
                description = self._clean_html(entry.summary)
            elif 'description' in entry:
                description = self._clean_html(entry.description)
            
            # Get content
            content = ''
            if 'content' in entry and entry.content:
                content = self._clean_html(entry.content[0].get('value', ''))
            
            # Get link
            link = entry.get('link', '')
            
            # Get published date
            published = None
            if 'published_parsed' in entry and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif 'updated_parsed' in entry and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])
            else:
                published = datetime.utcnow()
            
            # Get image
            image_url = self._extract_image(entry)
            
            # Get author
            author = entry.get('author', source['name'])
            
            return {
                'id': str(uuid.uuid4()),
                'title': title,
                'description': description[:500] if description else '',
                'content': content[:2000] if content else description[:1000] if description else '',
                'url': link,
                'image_url': image_url,
                'source': {
                    'name': source['name'],
                    'url': link,
                    'category': source['category'],
                    'priority': source.get('priority', 2)
                },
                'author': author,
                'published_at': published.isoformat() if published else datetime.utcnow().isoformat(),
                'language': 'en',
                'fetched_at': datetime.utcnow().isoformat(),
                'is_international': True
            }
            
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None
    
    def _clean_html(self, html_text: str) -> str:
        """Curăță HTML și returnează text simplu"""
        if not html_text:
            return ''
        
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator=' ')
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except:
            # Fallback: simple regex cleanup
            text = re.sub(r'<[^>]+>', '', html_text)
            return re.sub(r'\s+', ' ', text).strip()
    
    def _extract_image(self, entry) -> str:
        """Extrage URL-ul imaginii din entry"""
        # Try media:content
        if 'media_content' in entry:
            for media in entry.media_content:
                if 'url' in media:
                    return media['url']
        
        # Try media:thumbnail
        if 'media_thumbnail' in entry:
            for thumb in entry.media_thumbnail:
                if 'url' in thumb:
                    return thumb['url']
        
        # Try enclosures
        if 'enclosures' in entry:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image'):
                    return enc.get('url', '')
        
        # Try to find image in content/summary
        content = entry.get('summary', '') or entry.get('description', '')
        if content:
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
            if img_match:
                return img_match.group(1)
        
        return None


international_rss_client = InternationalRSSClient()
