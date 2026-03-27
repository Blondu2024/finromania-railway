"""Dividend Calendar & Events API pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import logging
import io
import csv

from config.database import get_database
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/calendar", tags=["Calendar"])


# ============================================
# SAMPLE DIVIDEND & EVENTS DATA
# Updated: March 2026 - Based on TradeVille estimates
# Source: https://www.bursa.ro/tradeville-3-6-procente-media-randamentelor-dividendelor
# ============================================

BVB_DIVIDENDS_2024 = [
    # ========== 2024 - PLĂTITE ==========
    {
        "symbol": "TLV",
        "name": "Banca Transilvania",
        "dividend_per_share": 1.27,
        "currency": "RON",
        "ex_date": "2024-05-24",
        "payment_date": "2024-06-14",
        "record_date": "2024-05-27",
        "dividend_yield": 4.5,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "SNP",
        "name": "OMV Petrom",
        "dividend_per_share": 0.06,
        "currency": "RON",
        "ex_date": "2024-05-20",
        "payment_date": "2024-06-05",
        "record_date": "2024-05-22",
        "dividend_yield": 6.0,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "BRD",
        "name": "BRD - Groupe Société Générale",
        "dividend_per_share": 1.97,
        "currency": "RON",
        "ex_date": "2024-04-25",
        "payment_date": "2024-05-15",
        "record_date": "2024-04-29",
        "dividend_yield": 9.1,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "SNN",
        "name": "Nuclearelectrica",
        "dividend_per_share": 3.83,
        "currency": "RON",
        "ex_date": "2024-06-10",
        "payment_date": "2024-07-01",
        "record_date": "2024-06-12",
        "dividend_yield": 6.2,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "TGN",
        "name": "Transgaz",
        "dividend_per_share": 1.08,
        "currency": "RON",
        "ex_date": "2024-06-20",
        "payment_date": "2024-07-10",
        "record_date": "2024-06-24",
        "dividend_yield": 2.1,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "H2O",
        "name": "Hidroelectrica",
        "dividend_per_share": 2.03,
        "currency": "RON",
        "ex_date": "2024-06-28",
        "payment_date": "2024-07-22",
        "record_date": "2024-07-01",
        "dividend_yield": 1.8,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "DIGI",
        "name": "Digi Communications",
        "dividend_per_share": 0.50,
        "currency": "RON",
        "ex_date": "2024-08-15",
        "payment_date": "2024-09-01",
        "record_date": "2024-08-19",
        "dividend_yield": 0.4,
        "type": "cash",
        "status": "paid"
    },
    # ========== 2025 - PLĂTITE / ANUNȚATE ==========
    {
        "symbol": "BRD",
        "name": "BRD - Groupe Société Générale",
        "dividend_per_share": 2.10,
        "currency": "RON",
        "ex_date": "2025-04-25",
        "payment_date": "2025-05-15",
        "record_date": "2025-04-29",
        "dividend_yield": 8.5,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "SNP",
        "name": "OMV Petrom",
        "dividend_per_share": 0.065,
        "currency": "RON",
        "ex_date": "2025-05-19",
        "payment_date": "2025-06-05",
        "record_date": "2025-05-21",
        "dividend_yield": 6.5,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "TLV",
        "name": "Banca Transilvania",
        "dividend_per_share": 1.35,
        "currency": "RON",
        "ex_date": "2025-05-23",
        "payment_date": "2025-06-13",
        "record_date": "2025-05-26",
        "dividend_yield": 4.8,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "SNN",
        "name": "Nuclearelectrica",
        "dividend_per_share": 4.10,
        "currency": "RON",
        "ex_date": "2025-06-09",
        "payment_date": "2025-06-30",
        "record_date": "2025-06-11",
        "dividend_yield": 6.5,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "TGN",
        "name": "Transgaz",
        "dividend_per_share": 2.14,
        "currency": "RON",
        "ex_date": "2025-06-19",
        "payment_date": "2025-07-10",
        "record_date": "2025-06-23",
        "dividend_yield": 2.8,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "H2O",
        "name": "Hidroelectrica",
        "dividend_per_share": 2.45,
        "currency": "RON",
        "ex_date": "2025-06-27",
        "payment_date": "2025-07-21",
        "record_date": "2025-06-30",
        "dividend_yield": 1.9,
        "type": "cash",
        "status": "paid"
    },
    # ========== 2026 - ESTIMATE TradeVille ==========
    # Sursa: https://www.bursa.ro/tradeville-3-6-procente-media-randamentelor
    # Media randament BETPlus: 3.6% (dec 2025)
    {
        "symbol": "TLV",
        "name": "Banca Transilvania",
        "dividend_per_share": 1.46,
        "currency": "RON",
        "ex_date": "2026-05-22",
        "payment_date": "2026-06-12",
        "record_date": "2026-05-25",
        "dividend_yield": 5.2,
        "type": "cash",
        "status": "estimated",
        "notes": "Estimare TradeVille, payout ratio ~50%"
    },
    {
        "symbol": "SNP",
        "name": "OMV Petrom",
        "dividend_per_share": 0.07,
        "currency": "RON",
        "ex_date": "2026-05-18",
        "payment_date": "2026-06-04",
        "record_date": "2026-05-20",
        "dividend_yield": 7.0,
        "type": "cash",
        "status": "estimated",
        "notes": "Estimare bazată pe profit 2025"
    },
    {
        "symbol": "BRD",
        "name": "BRD - Groupe Société Générale",
        "dividend_per_share": 2.25,
        "currency": "RON",
        "ex_date": "2026-04-24",
        "payment_date": "2026-05-14",
        "record_date": "2026-04-28",
        "dividend_yield": 4.4,
        "type": "cash",
        "status": "estimated",
        "notes": "Estimare, payout ratio ~50%"
    },
    {
        "symbol": "SNN",
        "name": "Nuclearelectrica",
        "dividend_per_share": 4.50,
        "currency": "RON",
        "ex_date": "2026-06-08",
        "payment_date": "2026-06-29",
        "record_date": "2026-06-10",
        "dividend_yield": 6.8,
        "type": "cash",
        "status": "estimated",
        "notes": "Estimare TradeVille"
    },
    {
        "symbol": "TGN",
        "name": "Transgaz",
        "dividend_per_share": 2.39,
        "currency": "RON",
        "ex_date": "2026-06-18",
        "payment_date": "2026-07-09",
        "record_date": "2026-06-22",
        "dividend_yield": 3.8,
        "type": "cash",
        "status": "estimated",
        "notes": "Estimare TradeVille (creștere de la 1.08 în 2024)"
    },
    {
        "symbol": "H2O",
        "name": "Hidroelectrica",
        "dividend_per_share": 2.80,
        "currency": "RON",
        "ex_date": "2026-06-26",
        "payment_date": "2026-07-20",
        "record_date": "2026-06-29",
        "dividend_yield": 1.9,
        "type": "cash",
        "status": "estimated",
        "notes": "Randament scăzut, dar volum mare"
    },
    {
        "symbol": "TEL",
        "name": "Transelectrica",
        "dividend_per_share": 1.78,
        "currency": "RON",
        "ex_date": "2026-06-05",
        "payment_date": "2026-06-26",
        "record_date": "2026-06-09",
        "dividend_yield": 2.5,
        "type": "cash",
        "status": "estimated",
        "notes": "Estimare TradeVille (scădere de la 3.81 în 2024)"
    },
    {
        "symbol": "FP",
        "name": "Fondul Proprietatea",
        "dividend_per_share": 0.08,
        "currency": "RON",
        "ex_date": "2026-05-15",
        "payment_date": "2026-06-05",
        "record_date": "2026-05-18",
        "dividend_yield": 4.2,
        "type": "cash",
        "status": "estimated",
        "notes": "Istoric constant de dividende"
    },
    # ========== 2026 - COMPANII ADĂUGATE ==========
    {
        "symbol": "SNG",
        "name": "Romgaz",
        "dividend_per_share": 3.60,
        "currency": "RON",
        "ex_date": "2026-06-01",
        "payment_date": "2026-06-25",
        "record_date": "2026-06-03",
        "dividend_yield": 6.55,
        "type": "cash",
        "status": "estimated",
        "notes": "Estimare TradeVille - dividend yield stabil"
    },
    {
        "symbol": "DIGI",
        "name": "Digi Communications",
        "dividend_per_share": 2.60,
        "currency": "RON",
        "ex_date": "2026-05-10",
        "payment_date": "2026-05-30",
        "record_date": "2026-05-12",
        "dividend_yield": 5.00,
        "type": "cash",
        "status": "estimated",
        "notes": "Estimare - creștere constantă dividende"
    },
    {
        "symbol": "EL",
        "name": "Electrica",
        "dividend_per_share": 0.85,
        "currency": "RON",
        "ex_date": "2026-06-02",
        "payment_date": "2026-06-22",
        "record_date": "2026-06-04",
        "dividend_yield": 5.15,
        "type": "cash",
        "status": "estimated",
        "notes": "Estimare TradeVille"
    },
    {
        "symbol": "ONE",
        "name": "One United Properties",
        "dividend_per_share": 0.048,
        "currency": "RON",
        "ex_date": "2026-05-15",
        "payment_date": "2026-06-05",
        "record_date": "2026-05-18",
        "dividend_yield": 4.36,
        "type": "cash",
        "status": "estimated",
        "notes": "Growth company - payout ratio redus"
    },
    {
        "symbol": "WINE",
        "name": "Purcari Wineries",
        "dividend_per_share": 0.55,
        "currency": "RON",
        "ex_date": "2026-06-03",
        "payment_date": "2026-06-23",
        "record_date": "2026-06-05",
        "dividend_yield": 3.24,
        "type": "cash",
        "status": "estimated",
        "notes": "Estimare - creștere graduală"
    },
    {
        "symbol": "M",
        "name": "MedLife",
        "dividend_per_share": 0.15,
        "currency": "RON",
        "ex_date": "2026-05-20",
        "payment_date": "2026-06-10",
        "record_date": "2026-05-22",
        "dividend_yield": 2.00,
        "type": "cash",
        "status": "estimated",
        "notes": "Growth company - dividend mic, reinvestire"
    },
    {
        "symbol": "AQ",
        "name": "Aquila Part Prod Com",
        "dividend_per_share": 0.09,
        "currency": "RON",
        "ex_date": "2026-05-25",
        "payment_date": "2026-06-15",
        "record_date": "2026-05-27",
        "dividend_yield": 5.00,
        "type": "cash",
        "status": "estimated",
        "notes": "Estimare TradeVille"
    },
]

BVB_EVENTS = [
    # ========== 2026 - EVENIMENTE VIITOARE ==========
    {
        "type": "aga",
        "symbol": "BRD",
        "name": "BRD - Groupe Société Générale",
        "title": "Adunare Generală Ordinară",
        "date": "2026-04-15",
        "time": "10:00",
        "location": "București",
        "description": "Aprobarea situațiilor financiare 2025 și propunere dividende"
    },
    {
        "type": "aga",
        "symbol": "TLV",
        "name": "Banca Transilvania",
        "title": "Adunare Generală Ordinară",
        "date": "2026-04-22",
        "time": "10:00",
        "location": "Cluj-Napoca",
        "description": "Aprobarea situațiilor financiare 2025 și distribuirea dividendelor"
    },
    {
        "type": "aga",
        "symbol": "SNP",
        "name": "OMV Petrom",
        "title": "Adunare Generală Ordinară",
        "date": "2026-04-28",
        "time": "10:00",
        "location": "București",
        "description": "Aprobarea raportului anual și propunere dividende"
    },
    {
        "type": "aga",
        "symbol": "SNN",
        "name": "Nuclearelectrica",
        "title": "Adunare Generală Ordinară",
        "date": "2026-05-05",
        "time": "11:00",
        "location": "București",
        "description": "Aprobarea dividendelor și a raportului anual 2025"
    },
    {
        "type": "aga",
        "symbol": "H2O",
        "name": "Hidroelectrica",
        "title": "Adunare Generală Ordinară",
        "date": "2026-05-12",
        "time": "10:00",
        "location": "București",
        "description": "Aprobarea dividendelor și planul de investiții 2026"
    },
    {
        "type": "report",
        "symbol": "TLV",
        "name": "Banca Transilvania",
        "title": "Raport Financiar Q1 2026",
        "date": "2026-05-08",
        "time": "08:00",
        "description": "Publicarea rezultatelor financiare pentru Q1 2026"
    },
    {
        "type": "report",
        "symbol": "BRD",
        "name": "BRD - Groupe Société Générale",
        "title": "Raport Financiar Q1 2026",
        "date": "2026-05-10",
        "time": "08:00",
        "description": "Publicarea rezultatelor financiare pentru Q1 2026"
    },
    {
        "type": "report",
        "symbol": "SNP",
        "name": "OMV Petrom",
        "title": "Raport Financiar Q1 2026",
        "date": "2026-05-07",
        "time": "07:00",
        "description": "Rezultate financiare Q1 2026 și update operațional"
    },
]


# ============================================
# ENDPOINTS
# ============================================

@router.get("/dividends")
async def get_dividends(
    year: Optional[int] = Query(default=None, description="Filter by year"),
    symbol: Optional[str] = Query(default=None, description="Filter by symbol"),
    status: Optional[str] = Query(default=None, description="paid, estimated, announced"),
    upcoming_only: bool = Query(default=True, description="Show only upcoming dividends (default: True)"),
    include_past: bool = Query(default=False, description="Include past dividends")
):
    """Get dividend calendar — date oficiale BVB.ro + fallback hardcoded"""
    try:
        db = await get_database()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # ── Try BVB.ro scraped data first ──
        bvb_records = await db.bvb_dividends_scraped.find({}, {"_id": 0}).to_list(500)
        bvb_meta = await db.bvb_scrape_meta.find_one({"type": "dividends"}, {"_id": 0})
        last_scraped = bvb_meta.get("last_scraped") if bvb_meta else None

        dividends = []
        if bvb_records:
            for rec in bvb_records:
                ex_date = rec.get("ex_date", "")
                is_upcoming = ex_date >= today
                div_status = "estimated" if is_upcoming else "paid"

                dividends.append({
                    "symbol": rec["symbol"],
                    "name": rec.get("company", rec["symbol"]),
                    "dividend_per_share": rec.get("dividend_per_share", 0),
                    "currency": "RON",
                    "ex_date": ex_date,
                    "payment_date": rec.get("payment_date", ""),
                    "record_date": rec.get("record_date", ""),
                    "dividend_yield": rec.get("dividend_yield", 0),
                    "type": "cash",
                    "status": div_status,
                    "total_dividends": rec.get("total_dividends", 0),
                    "year": rec.get("year", ""),
                    "data_source": "BVB.ro (oficial)",
                })
        else:
            # Fallback to hardcoded data
            for d in BVB_DIVIDENDS_2024:
                dividends.append({**d, "data_source": "Estimare TradeVille"})

        # Filters
        if upcoming_only and not include_past:
            dividends = [d for d in dividends if d["ex_date"] >= today]

        if year:
            dividends = [d for d in dividends if d["ex_date"].startswith(str(year))]

        if symbol:
            dividends = [d for d in dividends if d["symbol"].upper() == symbol.upper()]

        if status:
            dividends = [d for d in dividends if d["status"] == status]

        dividends.sort(key=lambda x: x["ex_date"])

        total_yield = sum(d["dividend_yield"] for d in dividends) / len(dividends) if dividends else 0

        return {
            "dividends": dividends,
            "count": len(dividends),
            "average_yield": round(total_yield, 2),
            "data_source": "BVB.ro (oficial)" if bvb_records else "Estimare TradeVille",
            "bvb_last_scraped": last_scraped,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching dividends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events")
async def get_events(
    type: Optional[str] = Query(default=None, description="aga, report, ipo"),
    symbol: Optional[str] = Query(default=None, description="Filter by symbol"),
    upcoming_only: bool = Query(default=True, description="Show only upcoming events")
):
    """Get corporate events calendar"""
    try:
        events = BVB_EVENTS.copy()
        
        # Filter by type
        if type:
            events = [e for e in events if e["type"] == type]
        
        # Filter by symbol
        if symbol:
            events = [e for e in events if e["symbol"].upper() == symbol.upper()]
        
        # Filter upcoming only
        if upcoming_only:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            events = [e for e in events if e["date"] >= today]
        
        # Sort by date
        events.sort(key=lambda x: x["date"])
        
        return {
            "events": events,
            "count": len(events),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/upcoming")
async def get_upcoming_calendar():
    """Get combined upcoming dividends and events for next 90 days"""
    try:
        db = await get_database()
        today = datetime.now(timezone.utc)
        end_date = (today + timedelta(days=90)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")

        # ── BVB.ro scraped dividends ──
        bvb_records = await db.bvb_dividends_scraped.find({}, {"_id": 0}).to_list(500)
        upcoming_dividends = []

        if bvb_records:
            for d in bvb_records:
                ex = d.get("ex_date", "")
                if today_str <= ex <= end_date:
                    upcoming_dividends.append({
                        "symbol": d["symbol"],
                        "name": d.get("company", d["symbol"]),
                        "dividend_per_share": d.get("dividend_per_share", 0),
                        "ex_date": ex,
                        "payment_date": d.get("payment_date", ""),
                        "dividend_yield": d.get("dividend_yield", 0),
                        "calendar_type": "dividend",
                        "calendar_date": ex,
                        "data_source": "BVB.ro",
                    })
        else:
            upcoming_dividends = [
                {**d, "calendar_type": "dividend", "calendar_date": d["ex_date"]}
                for d in BVB_DIVIDENDS_2024
                if today_str <= d["ex_date"] <= end_date
            ]

        # ── BVB.ro scraped calendar events ──
        bvb_events = await db.bvb_calendar_scraped.find({}, {"_id": 0}).to_list(2000)
        upcoming_events = []

        if bvb_events:
            for e in bvb_events:
                dt = e.get("date", "")
                if today_str <= dt <= end_date:
                    upcoming_events.append({
                        "type": "event",
                        "symbol": e["symbol"],
                        "name": e.get("company", ""),
                        "title": e.get("event_type", ""),
                        "date": dt,
                        "calendar_type": "event",
                        "calendar_date": dt,
                        "data_source": "BVB.ro",
                    })
        else:
            upcoming_events = [
                {**e, "calendar_type": "event", "calendar_date": e["date"]}
                for e in BVB_EVENTS
                if today_str <= e["date"] <= end_date
            ]

        all_upcoming = upcoming_dividends + upcoming_events
        all_upcoming.sort(key=lambda x: x["calendar_date"])

        by_month = {}
        for item in all_upcoming:
            month_key = item["calendar_date"][:7]
            if month_key not in by_month:
                by_month[month_key] = []
            by_month[month_key].append(item)

        return {
            "items": all_upcoming,
            "by_month": by_month,
            "total_dividends": len(upcoming_dividends),
            "total_events": len(upcoming_events),
            "period": f"{today_str} - {end_date}",
            "data_source": "BVB.ro (oficial)" if bvb_records else "Estimare",
        }

    except Exception as e:
        logger.error(f"Error fetching upcoming calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dividend-kings")
async def get_dividend_kings():
    """Get stocks with best dividend yields — date oficiale BVB.ro"""
    try:
        db = await get_database()

        # ── BVB.ro scraped data ──
        bvb_records = await db.bvb_dividends_scraped.find({}, {"_id": 0}).to_list(500)

        dividend_stocks = {}
        if bvb_records:
            for d in bvb_records:
                sym = d["symbol"]
                ex = d.get("ex_date", "")
                if sym not in dividend_stocks or ex > dividend_stocks[sym].get("ex_date", ""):
                    dividend_stocks[sym] = d
        else:
            for d in BVB_DIVIDENDS_2024:
                if d["status"] == "paid":
                    sym = d["symbol"]
                    if sym not in dividend_stocks or d["ex_date"] > dividend_stocks[sym]["ex_date"]:
                        dividend_stocks[sym] = d

        symbols = list(dividend_stocks.keys())
        stocks = await db.stocks_bvb.find(
            {"symbol": {"$in": symbols}},
            {"_id": 0}
        ).to_list(100)

        stock_prices = {s["symbol"]: s.get("price", 0) for s in stocks}

        kings = []
        for sym, div_data in dividend_stocks.items():
            current_price = stock_prices.get(sym, 0)
            div_yield = div_data.get("dividend_yield", 0)
            div_per_share = div_data.get("dividend_per_share", 0)
            name = div_data.get("company") or div_data.get("name", sym)

            if div_yield <= 0 and current_price > 0 and div_per_share > 0:
                div_yield = round(div_per_share / current_price * 100, 2)

            kings.append({
                "symbol": sym,
                "name": name,
                "dividend_per_share": div_per_share,
                "dividend_yield": div_yield,
                "current_price": current_price,
                "last_ex_date": div_data.get("ex_date", ""),
                "status": "paid" if div_data.get("ex_date", "") < datetime.now(timezone.utc).strftime("%Y-%m-%d") else "upcoming",
                "data_source": "BVB.ro" if bvb_records else "Estimare",
            })

        kings.sort(key=lambda x: x["dividend_yield"], reverse=True)

        return {
            "dividend_kings": kings[:15],
            "count": len(kings),
            "best_yield": kings[0] if kings else None,
            "data_source": "BVB.ro (oficial)" if bvb_records else "Estimare",
        }

    except Exception as e:
        logger.error(f"Error fetching dividend kings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PRO FEATURE: EXPORT TO CSV/XLS
# ============================================

@router.get("/export/dividends")
async def export_dividends_csv(user: dict = Depends(require_auth)):
    """PRO Feature: Export dividend calendar to CSV — date BVB.ro"""
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(
            status_code=403,
            detail="Export necesită abonament PRO. Upgrade pentru acces."
        )
    
    try:
        db = await get_database()
        bvb_records = await db.bvb_dividends_scraped.find({}, {"_id": 0}).to_list(500)

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Simbol", "Companie", "Dividend/Acțiune (RON)", "Randament (%)",
            "Data Ex-Dividend", "Data Înregistrare", "Data Plată", "An", "Sursă"
        ])

        data_rows = []
        if bvb_records:
            for d in sorted(bvb_records, key=lambda x: x.get("ex_date", "")):
                data_rows.append([
                    d["symbol"],
                    d.get("company", ""),
                    d.get("dividend_per_share", 0),
                    d.get("dividend_yield", 0),
                    d.get("ex_date", ""),
                    d.get("record_date", ""),
                    d.get("payment_date", ""),
                    d.get("year", ""),
                    "BVB.ro",
                ])
        else:
            for d in BVB_DIVIDENDS_2024:
                data_rows.append([
                    d["symbol"],
                    d["name"],
                    d["dividend_per_share"],
                    d["dividend_yield"],
                    d["ex_date"],
                    d.get("record_date", ""),
                    d["payment_date"],
                    "",
                    "Estimare",
                ])

        for row in data_rows:
            writer.writerow(row)

        output.seek(0)

        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=dividende_bvb_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )

    except Exception as e:
        logger.error(f"Error exporting dividends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/events")
async def export_events_csv(user: dict = Depends(require_auth)):
    """
    PRO Feature: Export corporate events to CSV
    """
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(
            status_code=403,
            detail="Export necesită abonament PRO. Upgrade pentru acces."
        )
    
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Tip", "Simbol", "Companie", "Titlu", "Data", "Ora", "Descriere"
        ])
        
        # Data
        type_labels = {"aga": "AGA", "report": "Raport", "ipo": "IPO"}
        for e in BVB_EVENTS:
            writer.writerow([
                type_labels.get(e["type"], e["type"]),
                e["symbol"],
                e["name"],
                e["title"],
                e["date"],
                e.get("time", ""),
                e["description"]
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=evenimente_bvb_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/all")
async def export_all_calendar_csv(user: dict = Depends(require_auth)):
    """
    PRO Feature: Export complete calendar (dividends + events) to CSV
    """
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(
            status_code=403,
            detail="Export necesită abonament PRO. Upgrade pentru acces."
        )
    
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Dividends section
        writer.writerow(["=== CALENDAR DIVIDENDE BVB ==="])
        writer.writerow([])
        writer.writerow([
            "Simbol", "Companie", "Dividend/Acțiune (RON)", "Randament (%)",
            "Data Ex-Dividend", "Data Plată", "Status"
        ])
        
        for d in sorted(BVB_DIVIDENDS_2024, key=lambda x: x["ex_date"]):
            writer.writerow([
                d["symbol"],
                d["name"],
                d["dividend_per_share"],
                d["dividend_yield"],
                d["ex_date"],
                d["payment_date"],
                "Plătit" if d["status"] == "paid" else "Estimat"
            ])
        
        writer.writerow([])
        writer.writerow([])
        
        # Events section
        writer.writerow(["=== EVENIMENTE CORPORATIVE ==="])
        writer.writerow([])
        writer.writerow(["Tip", "Simbol", "Companie", "Titlu", "Data", "Descriere"])
        
        type_labels = {"aga": "AGA", "report": "Raport", "ipo": "IPO"}
        for e in sorted(BVB_EVENTS, key=lambda x: x["date"]):
            writer.writerow([
                type_labels.get(e["type"], e["type"]),
                e["symbol"],
                e["name"],
                e["title"],
                e["date"],
                e["description"]
            ])
        
        writer.writerow([])
        writer.writerow([f"Generat la: {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
        writer.writerow(["Sursa: FinRomania.ro"])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=calendar_complet_bvb_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))
