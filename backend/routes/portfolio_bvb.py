"""
Portofoliu BVB PRO — Exclusiv pentru utilizatori PRO
Date reale din EODHD, fără improvizații sau estimări.
Faza 1: CRUD + Live P&L + RSI
Faza 2: Grafic evoluție + Alocare sector + Fundamentale
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone
import asyncio
import logging
import os
import httpx

from config.database import get_database
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/portfolio-bvb", tags=["Portfolio BVB PRO"])

EODHD_API_KEY = os.environ.get("EODHD_API_KEY")
EODHD_BASE = "https://eodhd.com/api"


# ─────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────

class AddPositionRequest(BaseModel):
    symbol: str
    shares: float = Field(gt=0, description="Număr acțiuni")
    purchase_price: float = Field(gt=0, description="Preț mediu de intrare (RON)")
    purchase_date: Optional[str] = None   # YYYY-MM-DD
    notes: Optional[str] = None


class UpdatePositionRequest(BaseModel):
    shares: float = Field(gt=0)
    purchase_price: float = Field(gt=0)
    purchase_date: Optional[str] = None
    notes: Optional[str] = None


# ─────────────────────────────────────────
# EODHD HELPERS — date reale, fără fallback inventat
# ─────────────────────────────────────────

async def _get_live_price(client: httpx.AsyncClient, symbol: str) -> Dict:
    """Preț live din EODHD. Dacă nu există → null (nu inventăm)."""
    if not EODHD_API_KEY:
        return {"price": None, "change": None, "change_percent": None, "volume": None}
    try:
        r = await client.get(
            f"{EODHD_BASE}/real-time/{symbol}.RO",
            params={"api_token": EODHD_API_KEY, "fmt": "json"},
            timeout=10,
        )
        if r.status_code == 200:
            d = r.json()
            price = d.get("close") or d.get("previousClose")
            return {
                "price": float(price) if price else None,
                "change": d.get("change"),
                "change_percent": d.get("change_p"),
                "volume": d.get("volume"),
            }
    except Exception as e:
        logger.warning(f"[PORTFOLIO] Live price error for {symbol}: {e}")
    return {"price": None, "change": None, "change_percent": None, "volume": None}


async def _get_rsi(client: httpx.AsyncClient, symbol: str) -> Optional[float]:
    """RSI(14) din EODHD. Dacă nu există → null."""
    if not EODHD_API_KEY:
        return None
    try:
        r = await client.get(
            f"{EODHD_BASE}/technical/{symbol}.RO",
            params={"api_token": EODHD_API_KEY, "fmt": "json", "function": "rsi", "period": 14},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            if data and isinstance(data, list) and len(data) > 0:
                return data[-1].get("rsi")
    except Exception as e:
        logger.warning(f"[PORTFOLIO] RSI error for {symbol}: {e}")
    return None


def _rsi_signal(rsi: Optional[float]) -> Optional[str]:
    if rsi is None:
        return None
    if rsi < 30:
        return "SUPRAVÂNDUT"
    if rsi < 45:
        return "FAVORABIL"
    if rsi > 70:
        return "SUPRACUMPĂRAT"
    if rsi > 55:
        return "RIDICAT"
    return "NEUTRU"


def _rsi_color(signal: Optional[str]) -> str:
    colors = {
        "SUPRAVÂNDUT": "green",
        "FAVORABIL": "green",
        "NEUTRU": "gray",
        "RIDICAT": "orange",
        "SUPRACUMPĂRAT": "red",
    }
    return colors.get(signal, "gray")


def _require_pro(user: dict):
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(
            status_code=403,
            detail="Portofoliu PRO este exclusiv pentru abonații PRO."
        )


# ─────────────────────────────────────────
# ENDPOINT: GET PORTFOLIO
# ─────────────────────────────────────────

@router.get("/")
async def get_portfolio(user: dict = Depends(require_auth)):
    """
    Returnează portofoliul PRO cu date live EODHD.
    - Prețuri actuale (nu estimate)
    - P&L RON și % per poziție
    - RSI(14) per simbol
    - Sumar total (valoare, P&L, P&L azi)
    """
    _require_pro(user)

    db = await get_database()
    raw = await db.portfolio_bvb_pro.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).sort("added_at", 1).to_list(200)

    if not raw:
        return {
            "positions": [],
            "summary": {
                "total_value": 0,
                "total_invested": 0,
                "pl_ron": 0,
                "pl_percent": 0,
                "today_pl": 0,
                "positions_count": 0,
            },
        }

    symbols = [p["symbol"] for p in raw]

    # Fetch live data în paralel
    async with httpx.AsyncClient() as client:
        price_tasks = [_get_live_price(client, sym) for sym in symbols]
        rsi_tasks = [_get_rsi(client, sym) for sym in symbols]
        prices, rsis = await asyncio.gather(
            asyncio.gather(*price_tasks),
            asyncio.gather(*rsi_tasks),
        )

    # Company info din MongoDB (cache)
    stocks_db = await db.stocks_bvb.find(
        {"symbol": {"$in": symbols}},
        {"_id": 0, "symbol": 1, "name": 1, "sector": 1},
    ).to_list(200)
    info_map = {s["symbol"]: s for s in stocks_db}

    positions = []
    total_value = 0.0
    total_invested = 0.0
    today_pl = 0.0

    for i, pos in enumerate(raw):
        sym = pos["symbol"]
        pd = prices[i]
        rsi_val = rsis[i]

        current_price = pd.get("price")
        shares = pos["shares"]
        purchase_price = pos["purchase_price"]
        invested = round(shares * purchase_price, 2)

        current_value = round(shares * current_price, 2) if current_price else None
        pl_ron = round(current_value - invested, 2) if current_value is not None else None
        pl_pct = round((current_price - purchase_price) / purchase_price * 100, 2) if current_price else None

        chg_pct = pd.get("change_percent") or 0
        if current_value:
            today_pl += round(chg_pct / 100 * current_value, 2)

        total_invested += invested
        if current_value is not None:
            total_value += current_value

        rsi_sig = _rsi_signal(rsi_val)
        info = info_map.get(sym, {})

        positions.append({
            "symbol": sym,
            "name": info.get("name", sym),
            "sector": info.get("sector"),
            "shares": shares,
            "purchase_price": purchase_price,
            "purchase_date": pos.get("purchase_date"),
            "notes": pos.get("notes"),
            "added_at": pos.get("added_at"),
            # Live date
            "current_price": current_price,
            "price_change_percent": round(chg_pct, 2) if chg_pct else None,
            "current_value": current_value,
            "invested": invested,
            "pl_ron": pl_ron,
            "pl_percent": pl_pct,
            # Tehnic
            "rsi": round(rsi_val, 1) if rsi_val is not None else None,
            "rsi_signal": rsi_sig,
            "rsi_color": _rsi_color(rsi_sig),
        })

    total_pl = round(total_value - total_invested, 2)
    total_pl_pct = round(total_pl / total_invested * 100, 2) if total_invested > 0 else 0

    # Sortează descendent după valoare curentă
    positions.sort(key=lambda x: x.get("current_value") or 0, reverse=True)

    return {
        "positions": positions,
        "summary": {
            "total_value": round(total_value, 2),
            "total_invested": round(total_invested, 2),
            "pl_ron": total_pl,
            "pl_percent": total_pl_pct,
            "today_pl": round(today_pl, 2),
            "positions_count": len(positions),
        },
    }


# ─────────────────────────────────────────
# ENDPOINT: ADD POSITION
# ─────────────────────────────────────────

@router.post("/position")
async def add_position(data: AddPositionRequest, user: dict = Depends(require_auth)):
    """Adaugă o poziție nouă în portofoliu."""
    _require_pro(user)

    symbol = data.symbol.strip().upper()
    if not symbol:
        raise HTTPException(status_code=400, detail="Simbolul nu poate fi gol")

    db = await get_database()

    # Verifică dacă există deja
    existing = await db.portfolio_bvb_pro.find_one(
        {"user_id": user["user_id"], "symbol": symbol}
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"{symbol} există deja în portofoliu. Folosește update pentru a modifica."
        )

    # Verifică că simbolul există în BVB
    stock = await db.stocks_bvb.find_one({"symbol": symbol}, {"_id": 0, "name": 1})
    if not stock:
        raise HTTPException(status_code=404, detail=f"Acțiunea {symbol} nu a fost găsită pe BVB")

    doc = {
        "user_id": user["user_id"],
        "symbol": symbol,
        "shares": data.shares,
        "purchase_price": data.purchase_price,
        "purchase_date": data.purchase_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "notes": data.notes,
        "added_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.portfolio_bvb_pro.insert_one(doc)
    logger.info(f"[PORTFOLIO] Added {symbol} for user {user['user_id']}")

    return {
        "status": "ok",
        "message": f"{symbol} ({stock.get('name', '')}) adăugat în portofoliu",
        "symbol": symbol,
    }


# ─────────────────────────────────────────
# ENDPOINT: UPDATE POSITION
# ─────────────────────────────────────────

@router.put("/position/{symbol}")
async def update_position(symbol: str, data: UpdatePositionRequest, user: dict = Depends(require_auth)):
    """Actualizează o poziție existentă."""
    _require_pro(user)

    symbol = symbol.upper()
    db = await get_database()

    result = await db.portfolio_bvb_pro.update_one(
        {"user_id": user["user_id"], "symbol": symbol},
        {"$set": {
            "shares": data.shares,
            "purchase_price": data.purchase_price,
            "purchase_date": data.purchase_date,
            "notes": data.notes,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"{symbol} nu a fost găsit în portofoliu")

    return {"status": "ok", "message": f"{symbol} actualizat"}


# ─────────────────────────────────────────
# ENDPOINT: DELETE POSITION
# ─────────────────────────────────────────

@router.delete("/position/{symbol}")
async def delete_position(symbol: str, user: dict = Depends(require_auth)):
    """Șterge o poziție din portofoliu."""
    _require_pro(user)

    symbol = symbol.upper()
    db = await get_database()

    result = await db.portfolio_bvb_pro.delete_one(
        {"user_id": user["user_id"], "symbol": symbol}
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"{symbol} nu a fost găsit")

    return {"status": "ok", "message": f"{symbol} eliminat din portofoliu"}


# ─────────────────────────────────────────
# ENDPOINT: EXPORT CSV
# ─────────────────────────────────────────

@router.get("/export")
async def export_portfolio(user: dict = Depends(require_auth)):
    """Export poziții ca CSV (fără date live — doar date de intrare)."""
    _require_pro(user)

    db = await get_database()
    raw = await db.portfolio_bvb_pro.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).sort("added_at", 1).to_list(200)

    rows = [["Simbol", "Cantitate", "Preț Intrare (RON)", "Dată Intrare", "Note"]]
    for p in raw:
        rows.append([
            p["symbol"],
            p["shares"],
            p["purchase_price"],
            p.get("purchase_date", ""),
            p.get("notes", ""),
        ])

    csv = "\n".join([",".join([f'"{c}"' for c in row]) for row in rows])

    from fastapi.responses import Response as FResponse
    return FResponse(
        content="\ufeff" + csv,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=portofoliu_bvb_{datetime.now().strftime('%Y%m%d')}.csv"},
    )



# ─────────────────────────────────────────
# FAZA 2: ANALIZĂ — Grafic + Sector + Fundamentale
# ─────────────────────────────────────────

@router.get("/analysis")
async def get_portfolio_analysis(user: dict = Depends(require_auth)):
    """
    Faza 2 — Analiză completă portofoliu:
    - Istoric valoare zilnică (pentru grafic evoluție)
    - Alocare per sector (pentru donut chart)
    - Fundamentale per poziție din cache zilnic (P/E, ROE, EPS, D/E)
      STRICT: null dacă nu există în cache — fără improvizații
    """
    _require_pro(user)

    db = await get_database()
    raw = await db.portfolio_bvb_pro.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).to_list(200)

    if not raw:
        return {"sector_allocation": [], "fundamentals": [], "history": []}

    symbols = [p["symbol"] for p in raw]

    # ── Prețuri live pentru calcul valori actuale ──
    async with httpx.AsyncClient() as client:
        price_tasks = [_get_live_price(client, sym) for sym in symbols]
        prices = await asyncio.gather(*price_tasks)

    # ── Info stocuri din MongoDB ──
    stocks_db = await db.stocks_bvb.find(
        {"symbol": {"$in": symbols}},
        {"_id": 0, "symbol": 1, "sector": 1, "name": 1},
    ).to_list(200)
    info_map = {s["symbol"]: s for s in stocks_db}

    # ── Calcul valori per poziție ──
    position_values: Dict[str, float] = {}
    total_value = 0.0
    for i, pos in enumerate(raw):
        price = prices[i].get("price") or pos["purchase_price"]
        val = pos["shares"] * price
        position_values[pos["symbol"]] = round(val, 2)
        total_value += val

    # ── Alocare per sector ──
    sector_totals: Dict[str, float] = {}
    for sym, val in position_values.items():
        sector = info_map.get(sym, {}).get("sector") or "Altele"
        sector_totals[sector] = sector_totals.get(sector, 0) + val

    sector_allocation = sorted(
        [
            {
                "sector": sector,
                "value": round(val, 2),
                "percent": round(val / total_value * 100, 1) if total_value > 0 else 0,
            }
            for sector, val in sector_totals.items()
        ],
        key=lambda x: -x["value"],
    )

    # ── Fundamentale din cache zilnic (STRICT: null dacă lipsesc) ──
    fundamentals = []
    for sym in symbols:
        cached = await db.fundamentals_daily_cache.find_one(
            {"symbol": sym}, {"_id": 0}
        )
        roe_raw = cached.get("roe") if cached else None
        roe_pct = round(roe_raw * 100, 1) if roe_raw is not None and abs(roe_raw) < 10 else roe_raw
        fundamentals.append({
            "symbol": sym,
            "name": info_map.get(sym, {}).get("name", sym),
            "pe_ratio": cached.get("pe_ratio") if cached else None,
            "roe_percent": roe_pct,
            "eps": cached.get("eps") if cached else None,
            "debt_equity": cached.get("debt_equity") if cached else None,
            "pb_ratio": cached.get("pb_ratio") if cached else None,
            "cached_at": cached.get("cached_at") if cached else None,
        })

    # ── Salvare snapshot zilnic (o dată pe zi) ──
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    existing_snap = await db.portfolio_value_history.find_one(
        {"user_id": user["user_id"], "date": today}
    )
    if not existing_snap and total_value > 0:
        await db.portfolio_value_history.insert_one({
            "user_id": user["user_id"],
            "date": today,
            "value": round(total_value, 2),
        })
        logger.info(f"[PORTFOLIO] Snapshot saved for {user['user_id']}: {total_value:.2f} RON")

    # ── Istoric (ultimele 90 de zile) ──
    history_docs = await db.portfolio_value_history.find(
        {"user_id": user["user_id"]},
        {"_id": 0, "date": 1, "value": 1},
    ).sort("date", 1).limit(90).to_list(90)

    history = [{"date": h["date"], "value": h["value"]} for h in history_docs]

    return {
        "sector_allocation": sector_allocation,
        "fundamentals": fundamentals,
        "history": history,
        "total_value": round(total_value, 2),
    }
