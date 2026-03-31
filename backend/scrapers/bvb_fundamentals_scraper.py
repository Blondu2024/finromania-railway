"""
BVB.ro Fundamentals Scraper — Date oficiale de pe pagina de detaliu BVB.ro.

Sursa: https://m.bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s={SYMBOL}
Pagina publica BVB.ro cu: PER, Dividend, Capitalizare, 52w High/Low, Total actiuni.

Datele fundamentale NU se schimba la minut — scraping 2x/zi e suficient.
Rate limit: 1 request la 2-3 secunde (54 stocks ~ 2-3 minute)
Cache: MongoDB, refresh 2x/zi (07:30 + 18:30)
"""
import logging
import asyncio
import random
import re
from datetime import datetime, timezone
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from config.database import get_database

logger = logging.getLogger(__name__)

BVB_DETAIL_URL = "https://m.bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s={symbol}"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
]

COLLECTION = "bvb_fundamentals"
COLLECTION_META = "bvb_scrape_meta"

# All BVB symbols to scrape (same as eodhd_client.py BVB_STOCKS)
BVB_SYMBOLS = [
    "TLV", "H2O", "SNP", "BRD", "SNG", "SNN", "TGN", "DIGI", "M", "ONE",
    "TRP", "EL", "TEL", "WINE", "AQ", "BVB", "COTE", "SFG", "ALR",
    "EBS", "PE", "TTS", "EVER", "TRANSI", "DN", "AROBS", "BNET", "IMP",
    "NRF", "HAI", "MET",
    "ATB", "BIO", "RPH", "SCD",
    "IARV", "CMP", "ALU", "ELMA", "CRC", "SNO",
    "PBK", "BRK", "TBK", "LION", "ROC1", "SMTL", "OIL", "CMF", "VNC",
    "ROCE", "CEON", "ARTE", "FP",
]


def _parse_ro_number(val: str) -> Optional[float]:
    """Parse Romanian number format: '39.317.019.433,50' or '36,0600' or '8,63' to float."""
    if not val or not val.strip():
        return None
    val = val.strip().replace('\xa0', '').replace(' ', '')
    if val in ('-', 'N/A', 'n/a', ''):
        return None
    # Format: dots as thousands separator, comma as decimal
    # e.g. '39.317.019.433,50' -> 39317019433.50
    # e.g. '8,63' -> 8.63
    # e.g. '0,064400' -> 0.0644
    if ',' in val:
        val = val.replace('.', '').replace(',', '.')
    try:
        return float(val)
    except ValueError:
        return None


async def scrape_stock_fundamentals(client: httpx.AsyncClient, symbol: str) -> Optional[dict]:
    """
    Scrape fundamentals for a single stock from BVB.ro detail page.
    Returns dict with: per, dividend, dividend_year, market_cap, high_52w, low_52w, total_shares, nominal_value
    """
    url = BVB_DETAIL_URL.format(symbol=symbol)
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    try:
        resp = await client.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            logger.warning(f"BVB.ro returned {resp.status_code} for {symbol}")
            return None
    except Exception as e:
        logger.warning(f"Failed to fetch BVB.ro detail for {symbol}: {e}")
        return None

    soup = BeautifulSoup(resp.content, "lxml")
    tds = soup.find_all("td")

    # Build label->value map from consecutive td pairs
    cells = []
    for td in tds:
        text = td.get_text(separator=" ").strip()
        if text:
            cells.append(text)

    data = {
        "symbol": symbol,
        "per": None,
        "dividend": None,
        "dividend_year": None,
        "market_cap": None,
        "high_52w": None,
        "low_52w": None,
        "total_shares": None,
        "nominal_value": None,
        "dividend_yield": None,
        "eps": None,
        "pb_ratio": None,
        "divy_official": None,
        "source": "BVB.ro",
        "source_url": url,
    }

    ref_price = None

    for i, cell in enumerate(cells):
        next_val = cells[i + 1] if i + 1 < len(cells) else ""

        if cell == "PER":
            data["per"] = _parse_ro_number(next_val)

        elif cell.startswith("Dividend"):
            # "Dividend (2024)" -> extract year and value
            year_match = re.search(r'\((\d{4})\)', cell)
            if year_match:
                data["dividend_year"] = int(year_match.group(1))
            data["dividend"] = _parse_ro_number(next_val)

        elif cell == "Capitalizare":
            data["market_cap"] = _parse_ro_number(next_val)

        elif cell == "Max. 52 saptamani":
            data["high_52w"] = _parse_ro_number(next_val)

        elif cell == "Min. 52 saptamani":
            data["low_52w"] = _parse_ro_number(next_val)

        elif cell == "Numar total actiuni":
            data["total_shares"] = _parse_ro_number(next_val)

        elif cell == "Valoare Nominala":
            data["nominal_value"] = _parse_ro_number(next_val)

        elif cell == "EPS":
            data["eps"] = _parse_ro_number(next_val)

        elif cell == "P/BV":
            data["pb_ratio"] = _parse_ro_number(next_val)

        elif cell == "DIVY":
            data["divy_official"] = _parse_ro_number(next_val)

        elif cell == "Pret referinta":
            ref_price = _parse_ro_number(next_val)

    # Calculate dividend yield AFTER all cells parsed
    if ref_price and ref_price > 0 and data["dividend"] and data["dividend"] > 0:
        data["dividend_yield"] = round((data["dividend"] / ref_price) * 100, 2)

    return data


async def scrape_all_fundamentals() -> list[dict]:
    """
    Scrape fundamentals for ALL BVB stocks.
    Rate limited: ~2 seconds between requests.
    """
    results = []
    failed = []

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for i, symbol in enumerate(BVB_SYMBOLS):
            if i > 0:
                await asyncio.sleep(random.uniform(1.5, 2.5))

            data = await scrape_stock_fundamentals(client, symbol)
            if data and (data["per"] is not None or data["market_cap"] is not None):
                results.append(data)
                logger.debug(f"[{i+1}/{len(BVB_SYMBOLS)}] {symbol}: PER={data['per']}, Div={data['dividend']}, MCap={data['market_cap']}")
            else:
                failed.append(symbol)
                logger.warning(f"[{i+1}/{len(BVB_SYMBOLS)}] {symbol}: no data found")

    logger.info(f"Scraped {len(results)}/{len(BVB_SYMBOLS)} stocks ({len(failed)} failed: {failed})")
    return results


async def save_fundamentals_to_db(records: list[dict]) -> int:
    """Save scraped fundamentals to MongoDB, upserting by symbol."""
    if not records:
        return 0

    db = await get_database()
    now = datetime.now(timezone.utc).isoformat()
    count = 0

    for rec in records:
        rec["scraped_at"] = now
        await db[COLLECTION].update_one(
            {"symbol": rec["symbol"]},
            {"$set": rec},
            upsert=True,
        )
        count += 1

    # Update meta
    await db[COLLECTION_META].update_one(
        {"type": "fundamentals"},
        {"$set": {
            "last_scraped": now,
            "record_count": count,
            "source": "BVB.ro",
            "symbols": [r["symbol"] for r in records],
        }},
        upsert=True,
    )

    logger.info(f"Saved {count} fundamental records to MongoDB")
    return count


async def get_cached_fundamentals() -> tuple[dict, Optional[str]]:
    """
    Get cached fundamentals from MongoDB.
    Returns (dict keyed by symbol, last_scraped timestamp).
    """
    db = await get_database()
    records = await db[COLLECTION].find({}, {"_id": 0}).to_list(200)
    meta = await db[COLLECTION_META].find_one({"type": "fundamentals"}, {"_id": 0})
    last_scraped = meta.get("last_scraped") if meta else None

    by_symbol = {r["symbol"]: r for r in records}
    return by_symbol, last_scraped


async def get_fundamentals_for_symbol(symbol: str) -> Optional[dict]:
    """Get cached fundamentals for a single symbol."""
    db = await get_database()
    return await db[COLLECTION].find_one({"symbol": symbol.upper()}, {"_id": 0})


async def run_fundamentals_scrape():
    """Run full fundamentals scrape — all BVB stocks."""
    logger.info("Starting BVB.ro fundamentals scrape...")
    records = await scrape_all_fundamentals()
    count = await save_fundamentals_to_db(records)
    logger.info(f"BVB fundamentals scrape complete: {count} stocks updated")
    return {"count": count, "symbols": [r["symbol"] for r in records]}
