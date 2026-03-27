"""
BVB.ro Dividend Scraper — SAFE scraping cu rate limiting și cache MongoDB.

Sursa: https://m.bvb.ro/financialinstruments/corporateactions/infodividend
Pagina publică BVB.ro cu datele oficiale despre dividende.

Rate limit: 1 request la 3-5 secunde
Cache: rezultatele se stochează în MongoDB, refresh 1x/zi
User-Agent: browser real
"""
import logging
import asyncio
import random
from datetime import datetime, timezone
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from config.database import get_database

logger = logging.getLogger(__name__)

BVB_DIVIDEND_URL = "https://m.bvb.ro/financialinstruments/corporateactions/infodividend"
BVB_CALENDAR_URL = "https://m.bvb.ro/financialinstruments/selecteddata/financialcalendar"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
]

COLLECTION_DIVIDENDS = "bvb_dividends_scraped"
COLLECTION_CALENDAR = "bvb_calendar_scraped"
COLLECTION_META = "bvb_scrape_meta"


def _parse_romanian_float(val: str) -> float:
    """Parse '1.058100' or '5.010.913,00' to float. BVB uses dot as thousands sep and comma as decimal for totals."""
    if not val or not val.strip():
        return 0.0
    val = val.strip()
    # Dividend per share uses dot as decimal: '0.223000'
    # Total dividends uses dot as thousands and comma as decimal: '5.010.913,00'
    if "," in val:
        val = val.replace(".", "").replace(",", ".")
    try:
        return float(val)
    except ValueError:
        return 0.0


def _parse_bvb_date(date_str: str) -> Optional[str]:
    """Convert BVB date 'DD.MM.YYYY' to ISO 'YYYY-MM-DD'."""
    if not date_str or not date_str.strip():
        return None
    try:
        dt = datetime.strptime(date_str.strip(), "%d.%m.%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None


async def scrape_bvb_dividends() -> list[dict]:
    """
    Scrape dividend data from BVB.ro official page.
    Returns list of dividend records.
    """
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(BVB_DIVIDEND_URL, headers=headers)
            resp.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch BVB dividend page: {e}")
        return []

    soup = BeautifulSoup(resp.content, "lxml")
    table = soup.find("table", id="gv")
    if not table:
        logger.error("Dividend table not found on BVB page")
        return []

    rows = table.find_all("tr")
    records = []

    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 8:
            continue

        symbol_link = cols[0].find("a")
        symbol = symbol_link.text.strip() if symbol_link else ""
        if not symbol:
            continue

        company = cols[1].text.strip()
        dividend_per_share = _parse_romanian_float(cols[2].text.strip())
        dividend_yield = _parse_romanian_float(cols[3].text.strip())
        ex_date = _parse_bvb_date(cols[4].text.strip())
        payment_date = _parse_bvb_date(cols[5].text.strip())
        year = cols[6].text.strip()
        record_date = _parse_bvb_date(cols[7].text.strip())
        total_dividends = _parse_romanian_float(cols[8].text.strip()) if len(cols) > 8 else 0

        records.append({
            "symbol": symbol,
            "company": company,
            "dividend_per_share": dividend_per_share,
            "dividend_yield": dividend_yield,
            "ex_date": ex_date,
            "payment_date": payment_date,
            "year": year,
            "record_date": record_date,
            "total_dividends": total_dividends,
            "source": "BVB.ro",
            "source_url": BVB_DIVIDEND_URL,
        })

    logger.info(f"Scraped {len(records)} dividend records from BVB.ro")
    return records


async def scrape_bvb_financial_calendar() -> list[dict]:
    """
    Scrape financial calendar from BVB.ro (AGA, rapoarte, ex-dates).
    Returns list of calendar event records.
    """
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(BVB_CALENDAR_URL, headers=headers)
            resp.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch BVB calendar page: {e}")
        return []

    soup = BeautifulSoup(resp.content, "lxml")
    table = soup.find("table")
    if not table:
        logger.error("Calendar table not found on BVB page")
        return []

    rows = table.find_all("tr")
    events = []

    for row in rows:
        cols = row.find_all("td")
        if not cols:
            continue

        cell_text = cols[0].get_text(separator="\n").strip()
        lines = [line.strip() for line in cell_text.split("\n") if line.strip()]
        if len(lines) < 3:
            continue

        date_str = lines[0]
        symbol_link = cols[0].find("a")
        symbol = symbol_link.text.strip() if symbol_link else ""

        company = ""
        event_type = ""
        for i, line in enumerate(lines):
            if line.startswith(symbol) and " - " in line:
                company = line.split(" - ", 1)[1] if " - " in line else ""
            elif i == len(lines) - 1:
                event_type = line

        date_iso = _parse_bvb_date(date_str.replace(" ", "").split(",")[-1].strip() if "," in date_str else date_str)
        if not date_iso:
            parts = date_str.split()
            if len(parts) >= 3:
                day = parts[0]
                month_map = {
                    "Ianuarie": "01", "Februarie": "02", "Martie": "03",
                    "Aprilie": "04", "Mai": "05", "Iunie": "06",
                    "Iulie": "07", "August": "08", "Septembrie": "09",
                    "Octombrie": "10", "Noiembrie": "11", "Decembrie": "12"
                }
                month = month_map.get(parts[1], "01")
                year = parts[2]
                try:
                    date_iso = f"{year}-{month}-{day.zfill(2)}"
                except Exception:
                    date_iso = None

        if symbol and date_iso:
            events.append({
                "symbol": symbol,
                "company": company,
                "date": date_iso,
                "event_type": event_type,
                "source": "BVB.ro",
            })

    logger.info(f"Scraped {len(events)} calendar events from BVB.ro")
    return events


async def save_dividends_to_db(records: list[dict]) -> int:
    """Save scraped dividend records to MongoDB, replacing old data."""
    if not records:
        return 0

    db = await get_database()
    now = datetime.now(timezone.utc).isoformat()

    for rec in records:
        rec["scraped_at"] = now

    await db[COLLECTION_DIVIDENDS].delete_many({})
    result = await db[COLLECTION_DIVIDENDS].insert_many(records)

    await db[COLLECTION_META].update_one(
        {"type": "dividends"},
        {"$set": {
            "last_scraped": now,
            "record_count": len(records),
            "source": "BVB.ro",
        }},
        upsert=True,
    )

    logger.info(f"Saved {len(result.inserted_ids)} dividend records to MongoDB")
    return len(result.inserted_ids)


async def save_calendar_to_db(events: list[dict]) -> int:
    """Save scraped calendar events to MongoDB."""
    if not events:
        return 0

    db = await get_database()
    now = datetime.now(timezone.utc).isoformat()

    for ev in events:
        ev["scraped_at"] = now

    await db[COLLECTION_CALENDAR].delete_many({})
    result = await db[COLLECTION_CALENDAR].insert_many(events)

    await db[COLLECTION_META].update_one(
        {"type": "calendar"},
        {"$set": {
            "last_scraped": now,
            "record_count": len(events),
            "source": "BVB.ro",
        }},
        upsert=True,
    )

    logger.info(f"Saved {len(result.inserted_ids)} calendar events to MongoDB")
    return len(result.inserted_ids)


async def get_cached_dividends() -> tuple[list[dict], Optional[str]]:
    """Get cached dividend data from MongoDB. Returns (records, last_scraped)."""
    db = await get_database()
    records = await db[COLLECTION_DIVIDENDS].find({}, {"_id": 0}).to_list(500)
    meta = await db[COLLECTION_META].find_one({"type": "dividends"}, {"_id": 0})
    last_scraped = meta.get("last_scraped") if meta else None
    return records, last_scraped


async def get_cached_calendar() -> tuple[list[dict], Optional[str]]:
    """Get cached calendar events from MongoDB."""
    db = await get_database()
    events = await db[COLLECTION_CALENDAR].find({}, {"_id": 0}).to_list(2000)
    meta = await db[COLLECTION_META].find_one({"type": "calendar"}, {"_id": 0})
    last_scraped = meta.get("last_scraped") if meta else None
    return events, last_scraped


async def run_full_scrape():
    """Run complete BVB scrape — dividends + calendar with rate limiting."""
    logger.info("Starting full BVB.ro scrape...")

    dividends = await scrape_bvb_dividends()
    div_count = await save_dividends_to_db(dividends)

    await asyncio.sleep(random.uniform(3, 5))

    calendar = await scrape_bvb_financial_calendar()
    cal_count = await save_calendar_to_db(calendar)

    logger.info(f"BVB scrape complete: {div_count} dividends, {cal_count} calendar events")
    return {"dividends": div_count, "calendar": cal_count}
