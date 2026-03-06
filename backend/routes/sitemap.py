"""Sitemap Generator - Generează sitemap.xml dinamic cu toate paginile"""
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse
from datetime import datetime, timezone
from config.database import get_database
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sitemap"])

# Domeniul principal
DOMAIN = "https://finromania.ro"

# Pagini statice cu prioritățile lor
STATIC_PAGES = [
    {"loc": "/", "changefreq": "daily", "priority": "1.0"},
    {"loc": "/stocks", "changefreq": "hourly", "priority": "0.95"},
    {"loc": "/global", "changefreq": "hourly", "priority": "0.95"},
    {"loc": "/calculator-fiscal", "changefreq": "weekly", "priority": "0.9"},
    {"loc": "/news", "changefreq": "hourly", "priority": "0.85"},
    {"loc": "/pricing", "changefreq": "monthly", "priority": "0.8"},
    {"loc": "/trading-school", "changefreq": "weekly", "priority": "0.7"},
    {"loc": "/financial-education", "changefreq": "weekly", "priority": "0.7"},
    {"loc": "/advisor", "changefreq": "weekly", "priority": "0.7"},
    {"loc": "/converter", "changefreq": "daily", "priority": "0.6"},
    {"loc": "/calendar", "changefreq": "daily", "priority": "0.6"},
    {"loc": "/screener", "changefreq": "daily", "priority": "0.6"},
    {"loc": "/glossary", "changefreq": "monthly", "priority": "0.5"},
    {"loc": "/faq", "changefreq": "monthly", "priority": "0.5"},
    {"loc": "/about", "changefreq": "monthly", "priority": "0.4"},
    {"loc": "/contact", "changefreq": "monthly", "priority": "0.4"},
    {"loc": "/privacy", "changefreq": "yearly", "priority": "0.3"},
    {"loc": "/terms", "changefreq": "yearly", "priority": "0.3"},
    {"loc": "/disclaimer", "changefreq": "yearly", "priority": "0.3"},
    {"loc": "/cookies", "changefreq": "yearly", "priority": "0.3"},
]


@router.get("/sitemap.xml", response_class=PlainTextResponse)
async def generate_sitemap():
    """Generează sitemap.xml dinamic cu toate paginile"""
    try:
        db = await get_database()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Start XML
        xml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
            '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
            ''
        ]
        
        # 1. Pagini statice
        xml_parts.append('  <!-- Pagini Principale -->')
        for page in STATIC_PAGES:
            xml_parts.append(f'''  <url>
    <loc>{DOMAIN}{page["loc"]}</loc>
    <changefreq>{page["changefreq"]}</changefreq>
    <priority>{page["priority"]}</priority>
    <lastmod>{today}</lastmod>
  </url>''')
        
        # 2. Acțiuni BVB individuale
        xml_parts.append('')
        xml_parts.append('  <!-- Acțiuni BVB - Pagini Individuale -->')
        
        bvb_stocks = await db.stocks_bvb.find(
            {},
            {"symbol": 1, "name": 1, "_id": 0}
        ).to_list(500)
        
        for stock in bvb_stocks:
            symbol = stock.get("symbol", "").replace(".RO", "")
            if symbol:
                xml_parts.append(f'''  <url>
    <loc>{DOMAIN}/stocks/{symbol}</loc>
    <changefreq>hourly</changefreq>
    <priority>0.8</priority>
    <lastmod>{today}</lastmod>
  </url>''')
        
        logger.info(f"Sitemap: Added {len(bvb_stocks)} BVB stocks")
        
        # 3. Indici și active globale
        xml_parts.append('')
        xml_parts.append('  <!-- Piețe Globale - Pagini Individuale -->')
        
        global_indices = await db.stocks_global.find(
            {},
            {"symbol": 1, "name": 1, "_id": 0}
        ).to_list(100)
        
        for index in global_indices:
            symbol = index.get("symbol", "")
            if symbol:
                # Encode special characters
                safe_symbol = symbol.replace("^", "").replace("=", "")
                xml_parts.append(f'''  <url>
    <loc>{DOMAIN}/global/{safe_symbol}</loc>
    <changefreq>hourly</changefreq>
    <priority>0.75</priority>
    <lastmod>{today}</lastmod>
  </url>''')
        
        logger.info(f"Sitemap: Added {len(global_indices)} global indices")
        
        # 4. Știri recente (ultimele 100)
        xml_parts.append('')
        xml_parts.append('  <!-- Știri Financiare -->')
        
        articles = await db.articles.find(
            {},
            {"id": 1, "published_at": 1, "_id": 0}
        ).sort("published_at", -1).limit(100).to_list(100)
        
        for article in articles:
            article_id = article.get("id")
            if article_id:
                pub_date = article.get("published_at", today)[:10]
                xml_parts.append(f'''  <url>
    <loc>{DOMAIN}/news/{article_id}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
    <lastmod>{pub_date}</lastmod>
  </url>''')
        
        # Știri internaționale
        intl_articles = await db.articles_international.find(
            {},
            {"id": 1, "published_at": 1, "_id": 0}
        ).sort("published_at", -1).limit(100).to_list(100)
        
        for article in intl_articles:
            article_id = article.get("id")
            if article_id:
                pub_date = article.get("published_at", today)[:10]
                xml_parts.append(f'''  <url>
    <loc>{DOMAIN}/news/{article_id}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
    <lastmod>{pub_date}</lastmod>
  </url>''')
        
        logger.info(f"Sitemap: Added {len(articles) + len(intl_articles)} news articles")
        
        # 5. Lecții educație
        xml_parts.append('')
        xml_parts.append('  <!-- Lecții Trading School -->')
        
        # Trading School lessons (hardcoded IDs based on typical structure)
        trading_lessons = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        for lesson_id in trading_lessons:
            xml_parts.append(f'''  <url>
    <loc>{DOMAIN}/trading-school/{lesson_id}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.65</priority>
  </url>''')
        
        xml_parts.append('')
        xml_parts.append('  <!-- Lecții Educație Financiară -->')
        
        fin_lessons = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
        for lesson_id in fin_lessons:
            xml_parts.append(f'''  <url>
    <loc>{DOMAIN}/financial-education/{lesson_id}</loc>
    <changefreq>monthly</changefreq>
    <priority>0.65</priority>
  </url>''')
        
        # Close XML
        xml_parts.append('')
        xml_parts.append('</urlset>')
        
        sitemap_xml = '\n'.join(xml_parts)
        
        total_urls = (
            len(STATIC_PAGES) + 
            len(bvb_stocks) + 
            len(global_indices) + 
            len(articles) + 
            len(intl_articles) +
            len(trading_lessons) +
            len(fin_lessons)
        )
        logger.info(f"✅ Generated sitemap with {total_urls} URLs")
        
        return Response(
            content=sitemap_xml,
            media_type="application/xml",
            headers={
                "Content-Type": "application/xml; charset=utf-8",
                "Cache-Control": "public, max-age=3600"  # Cache 1 hour
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating sitemap: {e}")
        # Return basic sitemap on error
        return Response(
            content=_get_fallback_sitemap(),
            media_type="application/xml"
        )


@router.get("/robots.txt", response_class=PlainTextResponse)
async def get_robots_txt():
    """Generează robots.txt optimizat pentru SEO"""
    robots = f"""# FinRomania.ro - Robots.txt
# Actualizat: {datetime.now(timezone.utc).strftime("%Y-%m-%d")}

User-agent: *
Allow: /

# Sitemap
Sitemap: {DOMAIN}/sitemap.xml

# Pagini cu date live - permite crawling frecvent
Allow: /stocks
Allow: /global
Allow: /news

# Blochează paginile private
Disallow: /admin
Disallow: /api/
Disallow: /auth/
Disallow: /login

# Blochează parametrii de query inutili
Disallow: /*?_t=
Disallow: /*?token=

# Crawl-delay pentru a nu supraîncărca serverul
Crawl-delay: 1
"""
    return PlainTextResponse(content=robots, media_type="text/plain")


def _get_fallback_sitemap() -> str:
    """Sitemap de backup în caz de eroare"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{DOMAIN}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
    <lastmod>{today}</lastmod>
  </url>
  <url>
    <loc>{DOMAIN}/stocks</loc>
    <changefreq>hourly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>{DOMAIN}/global</loc>
    <changefreq>hourly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>{DOMAIN}/news</loc>
    <changefreq>hourly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>'''
