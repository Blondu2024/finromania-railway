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
# Based on real BVB companies
# ============================================

BVB_DIVIDENDS_2024 = [
    {
        "symbol": "TLV",
        "name": "Banca Transilvania",
        "dividend_per_share": 0.12,
        "currency": "RON",
        "ex_date": "2024-06-15",
        "payment_date": "2024-07-01",
        "record_date": "2024-06-17",
        "dividend_yield": 4.2,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "SNP",
        "name": "OMV Petrom",
        "dividend_per_share": 0.035,
        "currency": "RON",
        "ex_date": "2024-05-20",
        "payment_date": "2024-06-05",
        "record_date": "2024-05-22",
        "dividend_yield": 3.5,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "BRD",
        "name": "BRD - Groupe Société Générale",
        "dividend_per_share": 1.64,
        "currency": "RON",
        "ex_date": "2024-04-25",
        "payment_date": "2024-05-15",
        "record_date": "2024-04-29",
        "dividend_yield": 6.1,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "SNN",
        "name": "Nuclearelectrica",
        "dividend_per_share": 3.20,
        "currency": "RON",
        "ex_date": "2024-07-10",
        "payment_date": "2024-08-01",
        "record_date": "2024-07-12",
        "dividend_yield": 5.8,
        "type": "cash",
        "status": "paid"
    },
    {
        "symbol": "TGN",
        "name": "Transgaz",
        "dividend_per_share": 25.50,
        "currency": "RON",
        "ex_date": "2024-06-20",
        "payment_date": "2024-07-10",
        "record_date": "2024-06-24",
        "dividend_yield": 7.2,
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
        "dividend_yield": 0.5,
        "type": "cash",
        "status": "paid"
    },
    # Upcoming 2025 estimates
    {
        "symbol": "TLV",
        "name": "Banca Transilvania",
        "dividend_per_share": 0.14,
        "currency": "RON",
        "ex_date": "2025-06-15",
        "payment_date": "2025-07-01",
        "record_date": "2025-06-17",
        "dividend_yield": 4.8,
        "type": "cash",
        "status": "estimated"
    },
    {
        "symbol": "SNP",
        "name": "OMV Petrom",
        "dividend_per_share": 0.04,
        "currency": "RON",
        "ex_date": "2025-05-20",
        "payment_date": "2025-06-05",
        "record_date": "2025-05-22",
        "dividend_yield": 4.0,
        "type": "cash",
        "status": "estimated"
    },
    {
        "symbol": "BRD",
        "name": "BRD - Groupe Société Générale",
        "dividend_per_share": 1.80,
        "currency": "RON",
        "ex_date": "2025-04-25",
        "payment_date": "2025-05-15",
        "record_date": "2025-04-29",
        "dividend_yield": 6.5,
        "type": "cash",
        "status": "estimated"
    },
    {
        "symbol": "SNN",
        "name": "Nuclearelectrica",
        "dividend_per_share": 3.50,
        "currency": "RON",
        "ex_date": "2025-07-10",
        "payment_date": "2025-08-01",
        "record_date": "2025-07-12",
        "dividend_yield": 6.2,
        "type": "cash",
        "status": "estimated"
    },
]

BVB_EVENTS = [
    {
        "type": "aga",
        "symbol": "TLV",
        "name": "Banca Transilvania",
        "title": "Adunare Generală Ordinară",
        "date": "2025-04-20",
        "time": "10:00",
        "location": "Cluj-Napoca",
        "description": "Aprobarea situațiilor financiare 2024 și distribuirea dividendelor"
    },
    {
        "type": "aga",
        "symbol": "SNP",
        "name": "OMV Petrom",
        "title": "Adunare Generală Ordinară",
        "date": "2025-04-25",
        "time": "10:00",
        "location": "București",
        "description": "Aprobarea raportului anual și propunere dividende"
    },
    {
        "type": "report",
        "symbol": "BRD",
        "name": "BRD - Groupe Société Générale",
        "title": "Raport Financiar Q4 2024",
        "date": "2025-02-15",
        "time": "08:00",
        "description": "Publicarea rezultatelor financiare pentru Q4 2024"
    },
    {
        "type": "report",
        "symbol": "TLV",
        "name": "Banca Transilvania",
        "title": "Raport Financiar Q4 2024",
        "date": "2025-02-20",
        "time": "08:00",
        "description": "Publicarea rezultatelor financiare pentru Q4 2024"
    },
    {
        "type": "report",
        "symbol": "DIGI",
        "name": "Digi Communications",
        "title": "Raport Anual 2024",
        "date": "2025-03-15",
        "time": "18:00",
        "description": "Publicarea raportului anual consolidat"
    },
    {
        "type": "ipo",
        "symbol": "NEW",
        "name": "Hidroelectrica",
        "title": "Listare Suplimentară",
        "date": "2025-03-01",
        "description": "Potențială ofertă secundară de acțiuni"
    }
]


# ============================================
# ENDPOINTS
# ============================================

@router.get("/dividends")
async def get_dividends(
    year: Optional[int] = Query(default=None, description="Filter by year"),
    symbol: Optional[str] = Query(default=None, description="Filter by symbol"),
    status: Optional[str] = Query(default=None, description="paid, estimated, announced"),
    upcoming_only: bool = Query(default=False, description="Show only upcoming dividends")
):
    """Get dividend calendar"""
    try:
        dividends = BVB_DIVIDENDS_2024.copy()
        
        # Filter by year
        if year:
            dividends = [d for d in dividends if d["ex_date"].startswith(str(year))]
        
        # Filter by symbol
        if symbol:
            dividends = [d for d in dividends if d["symbol"].upper() == symbol.upper()]
        
        # Filter by status
        if status:
            dividends = [d for d in dividends if d["status"] == status]
        
        # Filter upcoming only
        if upcoming_only:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            dividends = [d for d in dividends if d["ex_date"] >= today]
        
        # Sort by ex_date
        dividends.sort(key=lambda x: x["ex_date"])
        
        # Calculate statistics
        total_yield = sum(d["dividend_yield"] for d in dividends) / len(dividends) if dividends else 0
        
        return {
            "dividends": dividends,
            "count": len(dividends),
            "average_yield": round(total_yield, 2),
            "updated_at": datetime.now(timezone.utc).isoformat()
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
        today = datetime.now(timezone.utc)
        end_date = (today + timedelta(days=90)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        
        # Get upcoming dividends
        upcoming_dividends = [
            {**d, "calendar_type": "dividend", "calendar_date": d["ex_date"]}
            for d in BVB_DIVIDENDS_2024
            if today_str <= d["ex_date"] <= end_date
        ]
        
        # Get upcoming events
        upcoming_events = [
            {**e, "calendar_type": "event", "calendar_date": e["date"]}
            for e in BVB_EVENTS
            if today_str <= e["date"] <= end_date
        ]
        
        # Combine and sort
        all_upcoming = upcoming_dividends + upcoming_events
        all_upcoming.sort(key=lambda x: x["calendar_date"])
        
        # Group by month
        by_month = {}
        for item in all_upcoming:
            month_key = item["calendar_date"][:7]  # YYYY-MM
            if month_key not in by_month:
                by_month[month_key] = []
            by_month[month_key].append(item)
        
        return {
            "items": all_upcoming,
            "by_month": by_month,
            "total_dividends": len(upcoming_dividends),
            "total_events": len(upcoming_events),
            "period": f"{today_str} - {end_date}"
        }
        
    except Exception as e:
        logger.error(f"Error fetching upcoming calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dividend-kings")
async def get_dividend_kings():
    """Get stocks with best dividend yields"""
    try:
        db = await get_database()
        
        # Get unique symbols with dividends
        dividend_stocks = {}
        for d in BVB_DIVIDENDS_2024:
            if d["status"] == "paid":
                symbol = d["symbol"]
                if symbol not in dividend_stocks or d["ex_date"] > dividend_stocks[symbol]["ex_date"]:
                    dividend_stocks[symbol] = d
        
        # Get current prices
        symbols = list(dividend_stocks.keys())
        stocks = await db.stocks_bvb.find(
            {"symbol": {"$in": symbols}},
            {"_id": 0}
        ).to_list(100)
        
        stock_prices = {s["symbol"]: s.get("price", 0) for s in stocks}
        
        # Create dividend kings list
        kings = []
        for symbol, div_data in dividend_stocks.items():
            current_price = stock_prices.get(symbol, 0)
            kings.append({
                "symbol": symbol,
                "name": div_data["name"],
                "dividend_per_share": div_data["dividend_per_share"],
                "dividend_yield": div_data["dividend_yield"],
                "current_price": current_price,
                "last_ex_date": div_data["ex_date"],
                "status": div_data["status"]
            })
        
        # Sort by yield
        kings.sort(key=lambda x: x["dividend_yield"], reverse=True)
        
        return {
            "dividend_kings": kings,
            "count": len(kings),
            "best_yield": kings[0] if kings else None
        }
        
    except Exception as e:
        logger.error(f"Error fetching dividend kings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PRO FEATURE: EXPORT TO CSV/XLS
# ============================================

@router.get("/export/dividends")
async def export_dividends_csv(user: dict = Depends(require_auth)):
    """
    PRO Feature: Export dividend calendar to CSV
    Can be opened in Excel
    """
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(
            status_code=403,
            detail="Export necesită abonament PRO. Upgrade pentru acces."
        )
    
    try:
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Simbol", "Companie", "Dividend/Acțiune (RON)", "Randament (%)",
            "Data Ex-Dividend", "Data Înregistrare", "Data Plată", "Status"
        ])
        
        # Data
        for d in BVB_DIVIDENDS_2024:
            writer.writerow([
                d["symbol"],
                d["name"],
                d["dividend_per_share"],
                d["dividend_yield"],
                d["ex_date"],
                d["record_date"],
                d["payment_date"],
                "Plătit" if d["status"] == "paid" else "Estimat"
            ])
        
        output.seek(0)
        
        # Return as downloadable CSV
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),  # UTF-8 BOM for Excel
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
