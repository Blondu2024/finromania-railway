"""
BVB Dividends API — Date oficiale de pe BVB.ro, cache-uite în MongoDB.
Actualizare automată 1x/zi.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime, timezone
import logging

from scrapers.bvb_dividend_scraper import (
    get_cached_dividends,
    get_cached_calendar,
    run_full_scrape,
)
from config.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bvb-dividends", tags=["BVB Dividends"])


@router.get("/all")
async def get_all_bvb_dividends():
    """Toate dividendele oficiale de pe BVB.ro (din cache MongoDB)."""
    records, last_scraped = await get_cached_dividends()

    if not records:
        return {
            "dividends": [],
            "count": 0,
            "source": "BVB.ro",
            "last_scraped": None,
            "message": "Nu există date încă. Rulați /api/bvb-dividends/refresh.",
        }

    return {
        "dividends": records,
        "count": len(records),
        "source": "BVB.ro (oficial)",
        "last_scraped": last_scraped,
    }


@router.get("/latest")
async def get_latest_dividends():
    """
    Ultimele dividende per simbol — cel mai recent dividend per acțiune.
    Folosit de Calculator Dividende pentru date exacte.
    """
    records, last_scraped = await get_cached_dividends()

    latest_per_symbol = {}
    for rec in records:
        sym = rec["symbol"]
        ex = rec.get("ex_date", "")
        if sym not in latest_per_symbol or ex > latest_per_symbol[sym].get("ex_date", ""):
            latest_per_symbol[sym] = rec

    sorted_dividends = sorted(
        latest_per_symbol.values(),
        key=lambda x: x.get("dividend_yield", 0),
        reverse=True,
    )

    return {
        "dividends": sorted_dividends,
        "count": len(sorted_dividends),
        "source": "BVB.ro (oficial)",
        "last_scraped": last_scraped,
    }


@router.get("/trailing/{symbol}")
async def get_trailing_dividend(symbol: str):
    """
    Dividend trailing 12 luni pentru un simbol — sumă tuturor plăților din ultimul an.
    """
    symbol = symbol.upper()
    records, last_scraped = await get_cached_dividends()

    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=400)).strftime("%Y-%m-%d")

    payments = [
        r for r in records
        if r["symbol"] == symbol and r.get("ex_date", "") >= cutoff
    ]

    if not payments:
        raise HTTPException(status_code=404, detail=f"Nu s-au găsit dividende pentru {symbol}")

    trailing_annual = sum(p["dividend_per_share"] for p in payments)
    latest = max(payments, key=lambda p: p.get("ex_date", ""))

    return {
        "symbol": symbol,
        "company": latest.get("company", symbol),
        "trailing_annual_dividend": round(trailing_annual, 6),
        "payments_count": len(payments),
        "payments": [
            {
                "dividend_per_share": p["dividend_per_share"],
                "ex_date": p["ex_date"],
                "payment_date": p["payment_date"],
                "year": p.get("year"),
            }
            for p in sorted(payments, key=lambda x: x.get("ex_date", ""), reverse=True)
        ],
        "latest_ex_date": latest.get("ex_date"),
        "latest_yield": latest.get("dividend_yield", 0),
        "source": "BVB.ro (oficial)",
        "last_scraped": last_scraped,
    }


@router.get("/upcoming")
async def get_upcoming_dividends():
    """Dividendele viitoare (ex-date >= azi)."""
    records, last_scraped = await get_cached_dividends()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    upcoming = [r for r in records if r.get("ex_date", "") >= today]
    upcoming.sort(key=lambda x: x.get("ex_date", ""))

    return {
        "dividends": upcoming,
        "count": len(upcoming),
        "source": "BVB.ro (oficial)",
        "last_scraped": last_scraped,
    }


@router.get("/history/{symbol}")
async def get_dividend_history(symbol: str):
    """Istoricul complet de dividende pentru un simbol."""
    symbol = symbol.upper()
    records, last_scraped = await get_cached_dividends()

    history = [r for r in records if r["symbol"] == symbol]
    history.sort(key=lambda x: x.get("ex_date", ""), reverse=True)

    if not history:
        raise HTTPException(status_code=404, detail=f"Nu s-au găsit dividende pentru {symbol}")

    return {
        "symbol": symbol,
        "company": history[0].get("company", symbol),
        "history": history,
        "count": len(history),
        "source": "BVB.ro (oficial)",
        "last_scraped": last_scraped,
    }


@router.get("/calendar")
async def get_bvb_calendar():
    """Calendarul financiar BVB.ro (AGA, rapoarte, ex-dates)."""
    events, last_scraped = await get_cached_calendar()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    upcoming = [e for e in events if e.get("date", "") >= today]
    upcoming.sort(key=lambda x: x.get("date", ""))

    return {
        "events": upcoming[:100],
        "count": len(upcoming),
        "source": "BVB.ro (oficial)",
        "last_scraped": last_scraped,
    }


@router.post("/refresh")
async def refresh_bvb_data(background_tasks: BackgroundTasks):
    """Forțează refresh-ul datelor de pe BVB.ro (rulează în fundal)."""
    background_tasks.add_task(run_full_scrape)
    return {
        "message": "Scraping BVB.ro pornit în fundal. Datele vor fi actualizate în câteva secunde.",
        "status": "running",
    }


@router.get("/status")
async def get_scrape_status():
    """Verifică ultima actualizare a datelor BVB."""
    db = await get_database()
    meta_div = await db.bvb_scrape_meta.find_one({"type": "dividends"}, {"_id": 0})
    meta_cal = await db.bvb_scrape_meta.find_one({"type": "calendar"}, {"_id": 0})

    return {
        "dividends": meta_div or {"status": "no data"},
        "calendar": meta_cal or {"status": "no data"},
        "source": "BVB.ro",
    }
