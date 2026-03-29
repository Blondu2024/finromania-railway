"""Romanian RSS News Client - știri BVB și piața de capital"""
import feedparser
import requests
from datetime import datetime
from typing import List, Dict
import logging
import uuid
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

# Keywords pentru filtrare știri relevante BVB/piața de capital
BVB_KEYWORDS = [
    # Piața de capital
    'bursă', 'bursa', 'bvb', 'piata de capital', 'piață de capital',
    'acțiun', 'actiuni', 'acțiuni', 'listare', 'listează', 'listeaza',
    'tranzacți', 'tranzactii', 'tranzacționare',
    'investitor', 'investiți', 'portofoliu',
    # Instrumente financiare
    'dividende', 'dividend', 'obligațiun', 'obligatiuni', 'bond',
    'ipo', 'ofertă publică', 'oferta publica',
    'fond de investiții', 'fond de investitii', 'fond deschis', 'etf',
    'fidelis', 'titluri de stat',
    # Indici și indicatori
    'bet index', 'indice bet', 'indicele bet', 'bet-xt', 'bet-fi',
    'capitalizare', 'randament', 'profit net', 'cifra de afaceri',
    'p/e', 'eps', 'roe',
    # Reglementare
    'asf', 'cnvm', 'depozitarul central',
    'piata reglementata', 'piață reglementată', 'aero', 'smb',
    # Companii BVB frecvente
    'fondul proprietatea', 'banca transilvania', 'tlv', 'snp', 'petrom',
    'omv petrom', 'romgaz', 'sng', 'nuclearelectrica', 'snn',
    'electrica', 'transelectrica', 'tel', 'transgaz', 'tgn',
    'brd', 'one united', 'hidroelectrica', 'h2o',
    'sphera', 'digi', 'teraplast', 'conpet', 'antibiotice',
    'purcari', 'medlife', 'aquila',
]


class RomanianRSSClient:
    """Client pentru știri BVB și piața de capital din România"""

    # Surse RSS filtrate + BVB.ro scraping
    RSS_SOURCES = [
        {
            'name': 'Bursa.ro - Piața de Capital',
            'url': 'https://www.bursa.ro/piata-capital-bursa.xml',
            'category': 'capital_market',
            'filter': False,  # Dedicated capital market feed - no filter needed
        },
        {
            'name': 'Bursa.ro',
            'url': 'https://www.bursa.ro/titluri-bursa.xml',
            'category': 'capital_market',
            'filter': True,  # General feed - needs keyword filtering
        },
        {
            'name': 'Ziarul Financiar',
            'url': 'https://www.zf.ro/rss',
            'category': 'business',
            'filter': True,  # Filter to BVB-related only
        },
        {
            'name': 'Profit.ro',
            'url': 'https://www.profit.ro/rss',
            'category': 'business',
            'filter': True,  # Filter to BVB-related only
        },
    ]

    def __init__(self):
        self.timeout = 10

    def fetch_all_news(self, limit_per_source: int = 10) -> List[Dict]:
        """Obține știri BVB de la toate sursele"""
        all_articles = []

        # 1. Scrape BVB.ro press releases (sursa principală)
        try:
            bvb_articles = self._fetch_bvb_press_releases()
            all_articles.extend(bvb_articles)
            logger.info(f"Fetched {len(bvb_articles)} articles from BVB.ro")
        except Exception as e:
            logger.error(f"Error fetching BVB.ro press releases: {e}")

        # 2. Fetch from RSS sources (with keyword filtering where needed)
        for source in self.RSS_SOURCES:
            try:
                articles = self._fetch_from_source(source, limit_per_source)
                if source.get('filter'):
                    before = len(articles)
                    articles = self._filter_bvb_relevant(articles)
                    logger.info(f"Fetched {before} from {source['name']}, {len(articles)} BVB-relevant after filter")
                else:
                    logger.info(f"Fetched {len(articles)} articles from {source['name']}")
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error fetching from {source['name']}: {e}")

        # Sort by date (newest first)
        all_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)

        return all_articles

    def _fetch_bvb_press_releases(self) -> List[Dict]:
        """Scrape BVB.ro press releases page"""
        url = "https://bvb.ro/AboutUs/MediaCenter/PressReleases"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []

            # Find all press release links
            links = soup.find_all('a', href=re.compile(r'/AboutUs/MediaCenter/PressItem/'))

            for link in links:
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue

                    href = link.get('href', '')
                    full_url = f"https://bvb.ro{href}" if href.startswith('/') else href

                    # Extract ID from URL for dedup
                    id_match = re.search(r'/(\d+)$', href)
                    article_id = f"bvb_{id_match.group(1)}" if id_match else str(uuid.uuid4())

                    # Try to find date near the link
                    date_text = None
                    parent = link.parent
                    if parent:
                        text = parent.get_text()
                        date_match = re.search(r'(\d{1,2})\s*(ian|feb|mar|apr|mai|iun|iul|aug|sep|oct|nov|dec|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s*(\d{4})', text, re.IGNORECASE)
                        if date_match:
                            date_text = date_match.group(0)

                    published = datetime.utcnow()
                    if date_text:
                        try:
                            # Map Romanian month names
                            month_map = {
                                'ian': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'apr': 'Apr',
                                'mai': 'May', 'iun': 'Jun', 'iul': 'Jul', 'aug': 'Aug',
                                'sep': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dec': 'Dec',
                                'ianuarie': 'Jan', 'februarie': 'Feb', 'martie': 'Mar',
                                'aprilie': 'Apr', 'iunie': 'Jun', 'iulie': 'Jul',
                                'august': 'Aug', 'septembrie': 'Sep', 'octombrie': 'Oct',
                                'noiembrie': 'Nov', 'decembrie': 'Dec',
                            }
                            for ro, en in month_map.items():
                                date_text = re.sub(ro, en, date_text, flags=re.IGNORECASE)
                            published = datetime.strptime(date_text.strip(), '%d %b %Y')
                        except (ValueError, AttributeError):
                            pass

                    articles.append({
                        'id': article_id,
                        'title': title,
                        'description': title,
                        'content': '',
                        'url': full_url,
                        'image_url': 'https://bvb.ro/Content/img/logo-bvb.png',
                        'source': {
                            'name': 'BVB.ro',
                            'url': full_url,
                            'category': 'official',
                        },
                        'author': 'Bursa de Valori București',
                        'published_at': published.isoformat() if published else datetime.utcnow().isoformat(),
                        'language': 'ro',
                        'fetched_at': datetime.utcnow().isoformat(),
                        'is_romanian_source': True,
                        'is_bvb_official': True,
                    })
                except Exception as e:
                    logger.error(f"Error parsing BVB press release: {e}")
                    continue

            return articles

        except Exception as e:
            logger.error(f"Error scraping BVB.ro: {e}")
            return []

    def _filter_bvb_relevant(self, articles: List[Dict]) -> List[Dict]:
        """Filtrează articolele păstrând doar cele relevante BVB/piața de capital"""
        relevant = []
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            if any(kw in text for kw in BVB_KEYWORDS):
                relevant.append(article)
        return relevant

    def _fetch_from_source(self, source: Dict, limit: int) -> List[Dict]:
        """Obține știri de la o sursă RSS specifică"""
        try:
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
            title = entry.get('title', '').strip()
            if not title:
                return None

            description = ''
            if 'summary' in entry:
                description = self._clean_html(entry.summary)
            elif 'description' in entry:
                description = self._clean_html(entry.description)

            content = ''
            if 'content' in entry and entry.content:
                content = self._clean_html(entry.content[0].get('value', ''))

            link = entry.get('link', '')

            published = None
            if 'published_parsed' in entry and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif 'updated_parsed' in entry and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])
            else:
                published = datetime.utcnow()

            image_url = self._extract_image(entry)
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
                },
                'author': author,
                'published_at': published.isoformat() if published else datetime.utcnow().isoformat(),
                'language': 'ro',
                'fetched_at': datetime.utcnow().isoformat(),
                'is_romanian_source': True,
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
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator=' ')
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception:
            text = re.sub(r'<[^>]+>', '', html_text)
            return re.sub(r'\s+', ' ', text).strip()

    def _extract_image(self, entry) -> str:
        """Extrage URL-ul imaginii din entry"""
        if 'media_content' in entry:
            for media in entry.media_content:
                if 'url' in media:
                    return media['url']

        if 'media_thumbnail' in entry:
            for thumb in entry.media_thumbnail:
                if 'url' in thumb:
                    return thumb['url']

        if 'enclosures' in entry:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image'):
                    return enc.get('url', '')

        content = entry.get('summary', '') or entry.get('description', '')
        if content:
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
            if img_match:
                return img_match.group(1)

        return None


romanian_rss_client = RomanianRSSClient()
