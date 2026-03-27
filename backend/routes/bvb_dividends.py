"""
BVB Dividends API — Date oficiale de pe BVB.ro, cache-uite în MongoDB.
Actualizare automată 1x/zi.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from datetime import datetime, timezone, timedelta
from typing import Optional
from collections import defaultdict
import logging
import httpx
import os
import math

from scrapers.bvb_dividend_scraper import (
    get_cached_dividends,
    get_cached_calendar,
    run_full_scrape,
)
from config.database import get_database
from routes.auth import get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bvb-dividends", tags=["BVB Dividends"])

EODHD_API_KEY = os.environ.get("EODHD_API_KEY")
EODHD_BASE = "https://eodhd.com/api"


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



# ============================================================
# EODHD Deep History Helper
# ============================================================

async def _fetch_eodhd_dividend_history(symbol: str) -> list[dict]:
    """Fetch full dividend history from EODHD (5+ years)."""
    if not EODHD_API_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            url = f"{EODHD_BASE}/div/{symbol}.RO"
            resp = await client.get(url, params={
                "api_token": EODHD_API_KEY,
                "fmt": "json",
                "from": "2018-01-01",
            })
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return [
                        {
                            "date": d.get("date", ""),
                            "dividend": float(d.get("unadjustedValue", 0)),
                            "adjusted": float(d.get("value", 0)),
                        }
                        for d in data
                        if float(d.get("unadjustedValue", 0)) > 0.0001
                    ]
    except Exception as e:
        logger.warning(f"EODHD div history for {symbol}: {e}")
    return []


def _aggregate_by_year(payments: list[dict], date_key: str = "date", div_key: str = "dividend") -> dict[int, float]:
    """Sum dividends per calendar year."""
    by_year = defaultdict(float)
    for p in payments:
        dt = p.get(date_key, "")
        if len(dt) >= 4:
            try:
                year = int(dt[:4])
                by_year[year] += p.get(div_key, 0)
            except ValueError:
                pass
    return dict(sorted(by_year.items()))


def _calculate_cagr(yearly: dict[int, float]) -> Optional[float]:
    """Compound Annual Growth Rate of dividends."""
    years = sorted(yearly.keys())
    if len(years) < 2:
        return None
    first_val = yearly[years[0]]
    last_val = yearly[years[-1]]
    n = years[-1] - years[0]
    if n <= 0 or first_val <= 0 or last_val <= 0:
        return None
    return (math.pow(last_val / first_val, 1 / n) - 1) * 100


def _calculate_stability(yearly: dict[int, float]) -> dict:
    """
    Stability metrics:
    - consecutive_years: how many years in a row dividends were paid
    - total_paying_years: total years with dividends
    - consistency: stdev/mean (lower = more stable)
    """
    if not yearly:
        return {"consecutive_years": 0, "total_paying_years": 0, "consistency": 0}

    years = sorted(yearly.keys())
    total_paying = len([y for y in years if yearly[y] > 0])

    # Count max consecutive from the end (most recent)
    consecutive = 0
    for y in reversed(years):
        if yearly[y] > 0:
            consecutive += 1
        else:
            break

    # Coefficient of variation (lower = more consistent)
    vals = [yearly[y] for y in years if yearly[y] > 0]
    if len(vals) >= 2:
        mean_val = sum(vals) / len(vals)
        variance = sum((v - mean_val) ** 2 for v in vals) / len(vals)
        stdev = math.sqrt(variance)
        cv = (stdev / mean_val) * 100 if mean_val > 0 else 100
    else:
        cv = 0

    return {
        "consecutive_years": consecutive,
        "total_paying_years": total_paying,
        "consistency_cv": round(cv, 1),
    }


def _calculate_dividend_score(
    cagr: Optional[float],
    stability: dict,
    current_yield: float,
    years_of_data: int,
) -> dict:
    """
    Dividend Score 0–100:
    - Stability (40%): consecutive years + low CV
    - Growth (30%): CAGR
    - Yield (30%): current dividend yield
    """
    # Stability score (0-40)
    consec = stability.get("consecutive_years", 0)
    cv = stability.get("consistency_cv", 100)
    stability_pts = min(consec * 5, 25)  # max 25 pts for 5+ consecutive years
    consistency_pts = max(0, 15 - cv * 0.15)  # lower CV = more points, max 15
    stability_score = min(stability_pts + consistency_pts, 40)

    # Growth score (0-30)
    if cagr is not None:
        if cagr >= 10:
            growth_score = 30
        elif cagr >= 5:
            growth_score = 20 + (cagr - 5) * 2
        elif cagr >= 0:
            growth_score = 10 + cagr * 2
        elif cagr >= -5:
            growth_score = max(0, 10 + cagr * 2)
        else:
            growth_score = 0
    else:
        growth_score = 5  # unknown = minimal

    # Yield score (0-30)
    if current_yield >= 8:
        yield_score = 30
    elif current_yield >= 5:
        yield_score = 20 + (current_yield - 5) * 3.33
    elif current_yield >= 2:
        yield_score = 10 + (current_yield - 2) * 3.33
    elif current_yield > 0:
        yield_score = current_yield * 5
    else:
        yield_score = 0

    total = round(stability_score + growth_score + yield_score)
    total = max(0, min(100, total))

    # Rating label
    if total >= 80:
        rating = "Excelent"
    elif total >= 65:
        rating = "Foarte Bun"
    elif total >= 50:
        rating = "Bun"
    elif total >= 35:
        rating = "Mediu"
    else:
        rating = "Slab"

    return {
        "score": total,
        "rating": rating,
        "breakdown": {
            "stability": round(stability_score, 1),
            "growth": round(growth_score, 1),
            "yield_score": round(yield_score, 1),
        },
    }


# ============================================================
# ANALYSIS ENDPOINT
# ============================================================

@router.get("/analysis/{symbol}")
async def get_dividend_analysis(symbol: str):
    """
    Analiză completă dividende per acțiune.
    Combină BVB.ro (recent) + EODHD (istoric profund).
    Include: CAGR, Stability Score, Dividend Score 0-100.
    """
    symbol = symbol.upper()

    # ── 1. BVB.ro scraped data ──
    records, _ = await get_cached_dividends()
    bvb_payments = [r for r in records if r["symbol"] == symbol]

    # ── 2. EODHD deep history ──
    eodhd_payments = await _fetch_eodhd_dividend_history(symbol)

    if not bvb_payments and not eodhd_payments:
        raise HTTPException(status_code=404, detail=f"Nu s-au găsit dividende pentru {symbol}")

    # ── 3. Merge & deduplicate by date ──
    all_payments = {}

    # EODHD first (lower priority)
    for p in eodhd_payments:
        dt = p["date"]
        all_payments[dt] = {
            "date": dt,
            "dividend": p["dividend"],
            "source": "EODHD",
        }

    # BVB.ro overrides (higher priority)
    for p in bvb_payments:
        dt = p.get("ex_date", "")
        if dt:
            all_payments[dt] = {
                "date": dt,
                "dividend": p["dividend_per_share"],
                "source": "BVB.ro",
            }

    payments_list = sorted(all_payments.values(), key=lambda x: x["date"])

    # ── 4. Aggregate by year ──
    yearly = _aggregate_by_year(payments_list, "date", "dividend")

    # ── 5. Calculate metrics ──
    cagr = _calculate_cagr(yearly)
    stability = _calculate_stability(yearly)

    # Get current yield
    db = await get_database()
    stock = await db.stocks_bvb.find_one({"symbol": symbol}, {"_id": 0, "price": 1})
    current_price = stock.get("price", 0) if stock else 0
    current_year = datetime.now().year
    recent_annual = yearly.get(current_year, 0) or yearly.get(current_year - 1, 0)
    current_yield = (recent_annual / current_price * 100) if current_price > 0 else 0

    # Average yield over available years
    yields = []
    for yr, div_amt in yearly.items():
        if div_amt > 0 and current_price > 0:
            yields.append(div_amt / current_price * 100)
    avg_yield = sum(yields) / len(yields) if yields else 0

    score = _calculate_dividend_score(cagr, stability, current_yield, len(yearly))

    # Company name
    company = symbol
    if bvb_payments:
        company = bvb_payments[0].get("company", symbol)

    return {
        "symbol": symbol,
        "company": company,
        "current_price": round(current_price, 2),
        "current_yield": round(current_yield, 2),
        "average_yield_5y": round(avg_yield, 2),
        "yearly_dividends": [
            {"year": yr, "dividend": round(div, 6)}
            for yr, div in yearly.items()
        ],
        "payments": [
            {"date": p["date"], "dividend": round(p["dividend"], 6), "source": p["source"]}
            for p in payments_list
        ],
        "metrics": {
            "cagr": round(cagr, 2) if cagr is not None else None,
            "consecutive_years": stability["consecutive_years"],
            "total_paying_years": stability["total_paying_years"],
            "consistency_cv": stability["consistency_cv"],
        },
        "dividend_score": score,
        "data_years": len(yearly),
        "source": "BVB.ro + EODHD",
    }


# ============================================================
# RANKINGS ENDPOINT (with MongoDB cache)
# ============================================================

RANKINGS_CACHE_COLLECTION = "dividend_rankings_cache"


async def _compute_rankings() -> list[dict]:
    """Compute rankings for all stocks (slow — calls EODHD for each)."""
    records, _ = await get_cached_dividends()
    if not records:
        return []

    by_symbol = defaultdict(list)
    for rec in records:
        by_symbol[rec["symbol"]].append(rec)

    db = await get_database()
    all_stocks = await db.stocks_bvb.find({}, {"_id": 0, "symbol": 1, "price": 1}).to_list(200)
    price_map = {s["symbol"]: s.get("price", 0) for s in all_stocks}

    rankings = []
    import asyncio
    for sym, bvb_payments in by_symbol.items():
        eodhd_payments = await _fetch_eodhd_dividend_history(sym)
        await asyncio.sleep(0.3)  # rate limit EODHD

        all_p = {}
        for p in eodhd_payments:
            all_p[p["date"]] = {"date": p["date"], "dividend": p["dividend"]}
        for p in bvb_payments:
            dt = p.get("ex_date", "")
            if dt:
                all_p[dt] = {"date": dt, "dividend": p["dividend_per_share"]}

        payments_list = sorted(all_p.values(), key=lambda x: x["date"])
        yearly = _aggregate_by_year(payments_list, "date", "dividend")

        if not yearly:
            continue

        cagr = _calculate_cagr(yearly)
        stability = _calculate_stability(yearly)

        current_price = price_map.get(sym, 0)
        current_year = datetime.now().year
        recent_annual = yearly.get(current_year, 0) or yearly.get(current_year - 1, 0)
        current_yield = (recent_annual / current_price * 100) if current_price > 0 else 0

        score = _calculate_dividend_score(cagr, stability, current_yield, len(yearly))
        company = bvb_payments[0].get("company", sym)

        rankings.append({
            "symbol": sym,
            "company": company,
            "dividend_score": score["score"],
            "rating": score["rating"],
            "current_yield": round(current_yield, 2),
            "cagr": round(cagr, 2) if cagr is not None else None,
            "consecutive_years": stability["consecutive_years"],
            "data_years": len(yearly),
            "breakdown": score["breakdown"],
        })

    rankings.sort(key=lambda x: x["dividend_score"], reverse=True)
    return rankings


@router.get("/rankings")
async def get_dividend_rankings(background_tasks: BackgroundTasks):
    """
    Clasament acțiuni BVB după Dividend Score (0–100).
    Servit din cache MongoDB. Se actualizează în fundal dacă e vechi.
    """
    db = await get_database()
    cache = await db[RANKINGS_CACHE_COLLECTION].find_one({"type": "rankings"}, {"_id": 0})

    if cache and cache.get("rankings"):
        # Check if cache is less than 6 hours old
        cached_at = cache.get("computed_at", "")
        try:
            cached_time = datetime.fromisoformat(cached_at)
            age_hours = (datetime.now(timezone.utc) - cached_time).total_seconds() / 3600
            if age_hours > 6:
                background_tasks.add_task(_refresh_rankings_cache)
        except Exception:
            background_tasks.add_task(_refresh_rankings_cache)

        return {
            "rankings": cache["rankings"],
            "count": len(cache["rankings"]),
            "last_scraped": cache.get("computed_at"),
            "source": "BVB.ro + EODHD (cache)",
            "cache_refreshing": False,
        }

    # No cache — compute in background and return empty for now
    background_tasks.add_task(_refresh_rankings_cache)
    return {
        "rankings": [],
        "count": 0,
        "source": "BVB.ro + EODHD",
        "cache_refreshing": True,
        "message": "Se calculează clasamentul... Reîncărcați pagina în câteva secunde.",
    }


async def _refresh_rankings_cache():
    """Background task to compute and cache rankings."""
    try:
        logger.info("Computing dividend rankings...")
        rankings = await _compute_rankings()
        db = await get_database()
        await db[RANKINGS_CACHE_COLLECTION].update_one(
            {"type": "rankings"},
            {"$set": {
                "type": "rankings",
                "rankings": rankings,
                "computed_at": datetime.now(timezone.utc).isoformat(),
                "count": len(rankings),
            }},
            upsert=True,
        )
        logger.info(f"Rankings cache updated: {len(rankings)} stocks")
    except Exception as e:
        logger.error(f"Error computing rankings: {e}")
