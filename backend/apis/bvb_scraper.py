"""
BVB Web Scraper - Date reale direct de pe m.bvb.ro
Gratuit, fara limita API, date oficiale BVB
"""
import httpx
import logging
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from config.database import get_database

logger = logging.getLogger(__name__)

BVB_SHARES_URL = "https://m.bvb.ro/financialinstruments/markets/shares"

# Map known symbols to full names and sectors
BVB_STOCK_INFO = {
    "SNP": {"name": "OMV Petrom", "sector": "Energie"},
    "TLV": {"name": "Banca Transilvania", "sector": "Financiar"},
    "H2O": {"name": "Hidroelectrica", "sector": "Energie"},
    "SNG": {"name": "Romgaz", "sector": "Energie"},
    "BRD": {"name": "BRD - Groupe Societe Generale", "sector": "Financiar"},
    "FP": {"name": "Fondul Proprietatea", "sector": "Investitii"},
    "TGN": {"name": "Transgaz", "sector": "Energie"},
    "M": {"name": "MedLife", "sector": "Sanatate"},
    "DIGI": {"name": "Digi Communications", "sector": "Telecom"},
    "BVB": {"name": "Bursa de Valori Bucuresti", "sector": "Financiar"},
    "EL": {"name": "Electrica", "sector": "Energie"},
    "SNN": {"name": "Nuclearelectrica", "sector": "Energie"},
    "TRP": {"name": "Teraplast", "sector": "Constructii"},
    "AQ": {"name": "Aquila Part Prod Com", "sector": "FMCG"},
    "ONE": {"name": "One United Properties", "sector": "Imobiliare"},
    "WINE": {"name": "Purcari Wineries", "sector": "Alimentar"},
    "ALR": {"name": "Alro Slatina", "sector": "Industrie"},
    "COTE": {"name": "Conpet", "sector": "Energie"},
    "TEL": {"name": "Transelectrica", "sector": "Energie"},
    "BIO": {"name": "Biofarm", "sector": "Farmaceutice"},
    "BNET": {"name": "Bittnet Systems", "sector": "IT"},
    "DN": {"name": "Digi Communications NV", "sector": "Telecom"},
    "PE": {"name": "Petrolexportimport", "sector": "Energie"},
    "ATB": {"name": "Antibiotice Iasi", "sector": "Farmaceutice"},
    "SIF1": {"name": "SIF Banat-Crisana", "sector": "Investitii"},
    "SIF2": {"name": "SIF Moldova", "sector": "Investitii"},
    "SIF3": {"name": "SIF Transilvania", "sector": "Investitii"},
    "SIF4": {"name": "SIF Muntenia", "sector": "Investitii"},
    "SIF5": {"name": "SIF Oltenia", "sector": "Investitii"},
    "ROCE": {"name": "Romanian Cargo Express", "sector": "Logistica"},
    "CFH": {"name": "Cris-Tim Family Holding", "sector": "Alimentar"},
    "LION": {"name": "Lion Capital", "sector": "Investitii"},
    "EVER": {"name": "Evergent Investments", "sector": "Investitii"},
    "TRANSI": {"name": "Transilvania Investments", "sector": "Investitii"},
}


async def scrape_bvb_shares(page: int = 1, page_size: int = 20) -> List[Dict]:
    """Scrape stock data from m.bvb.ro"""
    stocks = []
    
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            # BVB uses form data for pagination
            params = {"page": page}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "ro-RO,ro;q=0.9,en;q=0.8",
            }
            
            response = await client.get(BVB_SHARES_URL, params=params, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find the main data table
            tables = soup.find_all("table")
            
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 4:
                        # Extract symbol
                        symbol_link = cols[0].find("a")
                        if not symbol_link:
                            continue
                        
                        symbol = symbol_link.get_text(strip=True)
                        company = cols[1].get_text(strip=True)
                        
                        # Parse price (Romanian format: 1,0000)
                        price_text = cols[2].get_text(strip=True).replace(".", "").replace(",", ".")
                        try:
                            price = float(price_text)
                        except ValueError:
                            continue
                        
                        # Parse change percent
                        change_text = cols[3].get_text(strip=True).replace(",", ".")
                        try:
                            change_percent = float(change_text)
                        except ValueError:
                            change_percent = 0.0
                        
                        # Parse date
                        date_text = cols[4].get_text(strip=True) if len(cols) > 4 else ""
                        
                        # Category
                        category = cols[5].get_text(strip=True) if len(cols) > 5 else ""
                        
                        # Get stored info or use scraped company name
                        info = BVB_STOCK_INFO.get(symbol, {"name": company, "sector": "Altele"})
                        
                        stocks.append({
                            "symbol": symbol,
                            "name": info["name"],
                            "company_full": company,
                            "price": price,
                            "change": round(price * change_percent / 100, 4) if change_percent else 0,
                            "change_percent": change_percent,
                            "volume": 0,
                            "sector": info.get("sector", "Altele"),
                            "category": category,
                            "date_text": date_text,
                            "currency": "RON",
                            "market": "BVB",
                            "source": "bvb.ro",
                            "is_mock": False,
                            "last_updated": datetime.now(timezone.utc).isoformat()
                        })
            
    except Exception as e:
        logger.error(f"Error scraping BVB: {e}")
    
    return stocks


async def scrape_all_bvb_shares() -> List[Dict]:
    """Scrape all pages of BVB shares"""
    all_stocks = []
    
    for page in range(1, 10):  # Max 9 pages (87 stocks / 10 per page)
        stocks = await scrape_bvb_shares(page=page)
        if not stocks:
            break
        all_stocks.extend(stocks)
        logger.info(f"BVB scrape page {page}: {len(stocks)} stocks")
    
    # Deduplicate by symbol
    seen = set()
    unique = []
    for s in all_stocks:
        if s["symbol"] not in seen:
            seen.add(s["symbol"])
            unique.append(s)
    
    logger.info(f"BVB scrape total: {len(unique)} unique stocks")
    return unique


async def update_bvb_stocks_from_scrape():
    """Update MongoDB with real BVB data from scraping"""
    try:
        stocks = await scrape_all_bvb_shares()
        
        if not stocks:
            logger.warning("No stocks scraped from BVB")
            return 0
        
        db = await get_database()
        updated = 0
        
        for stock in stocks:
            await db.stocks_bvb.update_one(
                {"symbol": stock["symbol"]},
                {"$set": stock},
                upsert=True
            )
            updated += 1
        
        logger.info(f"Updated {updated} BVB stocks from bvb.ro scraping")
        return updated
        
    except Exception as e:
        logger.error(f"Error updating BVB stocks from scrape: {e}")
        return 0
