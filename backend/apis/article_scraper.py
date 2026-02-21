"""Web Scraper pentru extragerea conținutului complet al articolelor"""
import requests
from bs4 import BeautifulSoup
import logging
import re
from typing import Optional, Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ArticleScraper:
    """Scraper pentru extragerea conținutului complet din articole"""
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8',
    }
    
    # Configurări specifice pentru fiecare sursă
    SITE_CONFIGS = {
        'zf.ro': {
            'content_selector': 'div.article-content, div.article__content, article .content, .article-body',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement', '.social-share', 'figure.related', '.related-articles'],
            'image_selector': 'article img, .article-content img, meta[property="og:image"]'
        },
        'profit.ro': {
            'content_selector': 'div.article-content, div.entry-content, article .content, .article-body',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement', '.social-share', '.related'],
            'image_selector': 'article img, .article-image img, meta[property="og:image"]'
        },
        'bursa.ro': {
            'content_selector': 'div.article-content, div.content-article, article .text, .article-text',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement'],
            'image_selector': 'article img, meta[property="og:image"]'
        },
        'wall-street.ro': {
            'content_selector': 'div.article-content, div.entry-content, .single-content, article .content',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement', '.social-share'],
            'image_selector': 'article img, meta[property="og:image"]'
        },
        'capital.ro': {
            'content_selector': 'div.article-content, div.entry-content, .article__content, article .content',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement', '.related', '.social'],
            'image_selector': 'article img, .featured-image img, meta[property="og:image"]'
        },
        'economica.net': {
            'content_selector': 'div.article-content, div.entry-content, article .content',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement'],
            'image_selector': 'article img, meta[property="og:image"]'
        },
        # ===== INTERNATIONAL SOURCES =====
        'cnbc.com': {
            'content_selector': 'div.ArticleBody-articleBody, .ArticleBody, article .group, [data-module="ArticleBody"]',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement', '.RelatedContent', '.InlineVideo', '.Promo'],
            'image_selector': 'meta[property="og:image"], .InlineImage img'
        },
        'finance.yahoo.com': {
            'content_selector': 'div.caas-body, .article-body, article .body, [data-test="article-body"]',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement', '.caas-da', '.related'],
            'image_selector': 'meta[property="og:image"], .caas-img img'
        },
        'reuters.com': {
            'content_selector': 'div.article-body, article .body, [data-testid="article-body"]',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement', '.related-articles'],
            'image_selector': 'meta[property="og:image"], .article-image img'
        },
        'bloomberg.com': {
            'content_selector': 'div.body-content, article .body, .article-body',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement', '.paywall'],
            'image_selector': 'meta[property="og:image"]'
        },
        'marketwatch.com': {
            'content_selector': 'div.article__body, .article-wrap, article .content',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement', '.related'],
            'image_selector': 'meta[property="og:image"], .article__figure img'
        },
        'investing.com': {
            'content_selector': 'div.articlePage, article .WYSIWYG, .article-content',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement', '.relatedArticles'],
            'image_selector': 'meta[property="og:image"], .articlePage img'
        },
        'ft.com': {
            'content_selector': 'div.article-body, article .body, .article__content-body',
            'remove_selectors': ['script', 'style', 'aside', '.ad', '.advertisement', '.o-ads'],
            'image_selector': 'meta[property="og:image"]'
        }
    }
    
    # Configurare generică pentru site-uri necunoscute
    DEFAULT_CONFIG = {
        'content_selector': 'article, .article-content, .entry-content, .post-content, .content, main',
        'remove_selectors': ['script', 'style', 'aside', 'nav', 'header', 'footer', '.ad', '.advertisement', '.comments', '.related', '.social-share'],
        'image_selector': 'article img, meta[property="og:image"]'
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def get_site_config(self, url: str) -> Dict:
        """Obține configurarea specifică pentru un site"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        for site_key, config in self.SITE_CONFIGS.items():
            if site_key in domain:
                return config
        
        return self.DEFAULT_CONFIG
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Extrage conținutul complet al unui articol"""
        try:
            logger.info(f"Scraping article: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            config = self.get_site_config(url)
            
            # Extrage titlul
            title = self._extract_title(soup)
            
            # Extrage imaginea principală
            image_url = self._extract_image(soup, config, url)
            
            # Elimină elementele nedorite
            for selector in config['remove_selectors']:
                for element in soup.select(selector):
                    element.decompose()
            
            # Extrage conținutul
            content = self._extract_content(soup, config)
            
            if not content:
                logger.warning(f"No content found for: {url}")
                return None
            
            return {
                'title': title,
                'content': content,
                'image_url': image_url,
                'scraped': True
            }
            
        except requests.Timeout:
            logger.error(f"Timeout scraping: {url}")
            return None
        except requests.RequestException as e:
            logger.error(f"Request error scraping {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrage titlul articolului"""
        # Încearcă og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Încearcă h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Încearcă title tag
        title = soup.find('title')
        if title:
            return title.get_text(strip=True)
        
        return None
    
    def _extract_image(self, soup: BeautifulSoup, config: Dict, base_url: str) -> Optional[str]:
        """Extrage imaginea principală"""
        # Încearcă og:image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        
        # Încearcă selectoarele specifice
        for selector in config['image_selector'].split(', '):
            img = soup.select_one(selector)
            if img:
                src = img.get('src') or img.get('data-src') or img.get('content')
                if src:
                    # Convertește URL relativ în absolut
                    if src.startswith('//'):
                        return 'https:' + src
                    elif src.startswith('/'):
                        parsed = urlparse(base_url)
                        return f"{parsed.scheme}://{parsed.netloc}{src}"
                    return src
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup, config: Dict) -> Optional[str]:
        """Extrage conținutul principal al articolului"""
        content_parts = []
        
        # Încearcă fiecare selector
        for selector in config['content_selector'].split(', '):
            content_elem = soup.select_one(selector)
            if content_elem:
                # Extrage paragrafele
                paragraphs = content_elem.find_all(['p', 'h2', 'h3', 'h4', 'li', 'blockquote'])
                
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # Ignoră paragrafele prea scurte
                        # Adaugă formatare pentru headings
                        if p.name in ['h2', 'h3', 'h4']:
                            content_parts.append(f"\n\n**{text}**\n")
                        elif p.name == 'blockquote':
                            content_parts.append(f"\n> {text}\n")
                        elif p.name == 'li':
                            content_parts.append(f"• {text}")
                        else:
                            content_parts.append(text)
                
                if content_parts:
                    break
        
        if not content_parts:
            # Fallback: extrage tot textul din body
            body = soup.find('body')
            if body:
                text = body.get_text(separator='\n', strip=True)
                # Curăță și păstrează doar paragrafele relevante
                lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 50]
                content_parts = lines[:30]  # Primele 30 de linii relevante
        
        if content_parts:
            # Combină și curăță conținutul
            content = '\n\n'.join(content_parts)
            # Elimină spații multiple
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = re.sub(r' {2,}', ' ', content)
            return content.strip()
        
        return None


article_scraper = ArticleScraper()
