"""
Portofoliu BVB PRO — Exclusiv pentru utilizatori PRO
Date reale din EODHD, fără improvizații sau estimări.
Faza 1: CRUD + Live P&L + RSI
Faza 2: Grafic evoluție + Alocare sector + Fundamentale
Faza 3: AI Advisor — recomandări per poziție + sumar risc portofoliu
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta
import asyncio
import logging
import json
import os
import httpx

from config.database import get_database
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/portfolio-bvb", tags=["Portfolio BVB PRO"])

EODHD_API_KEY = os.environ.get("EODHD_API_KEY")
EODHD_BASE = "https://eodhd.com/api"
EMERGENT_KEY = os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_UNIVERSAL_KEY") or os.environ.get("EMERGENT_LLM_KEY")
AI_CACHE_MINUTES = 60  # cache AI response 1 oră


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
            "pb_ratio": cached.get("pb_ratio") if cached and cached.get("pb_ratio") else None,
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


# ─────────────────────────────────────────
# FAZA 3: AI ADVISOR — Recomandări per poziție + sumar risc
# ─────────────────────────────────────────

def _build_portfolio_prompt(positions_data: list, summary: dict) -> str:
    """
    Construiește prompt-ul pentru analiză AI cu date reale.
    POLITICĂ STRICTĂ: Bazat EXCLUSIV pe datele furnizate, fără inventare.
    """
    lines = [
        "Ești un analist financiar PRO specializat pe Bursa de Valori București (BVB).",
        "Analizează portofoliul de mai jos și oferă recomandări concrete bazate EXCLUSIV pe datele furnizate.",
        "",
        "POLITICĂ STRICTĂ DE DATE:",
        "- Folosești DOAR datele de mai jos, fără să inventezi sau să estimezi valori lipsă",
        "- Dacă un indicator lipsește (null/N/A), menționează că nu îl poți evalua",
        "- Nu da sfaturi generice — fi specific bazat pe valorile numerice furnizate",
        "- Prioritizează acuratețea în fața completitudinii",
        "",
        "═══ PORTOFOLIU CURENT ═══",
        f"Valoare totală: {summary.get('total_value', 0):,.2f} RON",
        f"Total investit: {summary.get('total_invested', 0):,.2f} RON",
        f"P&L Total: {summary.get('pl_ron', 0):+,.2f} RON ({summary.get('pl_percent', 0):+.2f}%)",
        f"P&L Azi: {summary.get('today_pl', 0):+,.2f} RON",
        f"Nr. poziții: {summary.get('positions_count', 0)}",
        "",
        "═══ POZIȚII (date reale EODHD) ═══",
    ]

    for p in positions_data:
        sym = p.get("symbol", "?")
        name = p.get("name", sym)
        lines.append(f"\n▸ {sym} ({name})")
        lines.append(f"  Cantitate: {p.get('shares', 0)} acțiuni")
        lines.append(f"  Preț intrare: {p.get('purchase_price', 0):.4f} RON | Preț curent: {p.get('current_price', 'N/A')} RON")

        pl_r = p.get("pl_ron")
        pl_p = p.get("pl_percent")
        if pl_r is not None:
            lines.append(f"  P&L: {pl_r:+,.2f} RON ({pl_p:+.2f}%)")
        else:
            lines.append("  P&L: date indisponibile")

        rsi = p.get("rsi")
        rsi_sig = p.get("rsi_signal", "N/A")
        lines.append(f"  RSI(14): {f'{rsi:.1f}' if rsi else 'N/A'} [{rsi_sig}]")

        today_chg = p.get("price_change_percent")
        if today_chg is not None:
            lines.append(f"  Variație azi: {today_chg:+.2f}%")

        # Fundamentale
        fund = p.get("fundamentals", {})
        f_parts = []
        if fund.get("pe_ratio") is not None:
            f_parts.append(f"P/E={fund['pe_ratio']:.2f}")
        if fund.get("roe_percent") is not None:
            f_parts.append(f"ROE={fund['roe_percent']:.1f}%")
        if fund.get("eps") is not None:
            f_parts.append(f"EPS={fund['eps']:.2f} RON")
        if fund.get("debt_equity") is not None:
            f_parts.append(f"D/E={fund['debt_equity']:.2f}")
        if fund.get("pb_ratio"):
            f_parts.append(f"P/B={fund['pb_ratio']:.2f}")

        lines.append(f"  Fundamentale: {', '.join(f_parts) if f_parts else 'date indisponibile din EODHD'}")

    lines += [
        "",
        "═══ FORMAT RĂSPUNS (JSON strict, fără text în afara JSON) ═══",
        "",
        'Returnează EXCLUSIV un obiect JSON valid, fără markdown, fără explicații în afara JSON-ului:',
        "{",
        '  "portfolio_summary": {',
        '    "overall_signal": "HOLD",  // HOLD | BUY_MORE | REDUCE',
        '    "risk_level": "MEDIU",     // SCĂZUT | MEDIU | RIDICAT',
        '    "diversification_note": "scurt comentariu 1 frază",',
        '    "global_recommendation": "2-3 fraze concrete bazate pe datele de mai sus"',
        "  },",
        '  "positions": [',
        "    {",
        '      "symbol": "SYM",',
        '      "signal": "PĂSTREAZĂ",  // PĂSTREAZĂ | CUMPĂRĂ MAI MULT | CONSIDERĂ VÂNZARE',
        '      "confidence": "RIDICAT", // RIDICAT | MEDIU | SCĂZUT',
        '      "reason": "1-2 fraze concrete cu numărul exact (ex: RSI=57, P/E=8.45)",',
        '      "key_metric": "indicatorul principal pozitiv sau de risc"',
        "    }",
        "  ]",
        "}",
    ]
    return "\n".join(lines)


@router.get("/ai-analysis")
async def get_ai_portfolio_analysis(user: dict = Depends(require_auth)):
    """
    Faza 3 — AI Advisor per portofoliu:
    - Recomandare per poziție: PĂSTREAZĂ / CUMPĂRĂ MAI MULT / CONSIDERĂ VÂNZARE
    - Nivel de risc global: SCĂZUT / MEDIU / RIDICAT
    - Rezumat global 2-3 fraze cu date reale

    Cache: 1 oră per user (nu se regenerează la fiecare request).
    Input AI: RSI, P/E, ROE, D/E, EPS, P&L%, variație azi — STRICT din EODHD.
    """
    _require_pro(user)

    if not EMERGENT_KEY:
        raise HTTPException(status_code=503, detail="AI Advisor temporar indisponibil")

    db = await get_database()

    # ── Verificare cache AI (1 oră) ──
    cache_cutoff = datetime.now(timezone.utc) - timedelta(minutes=AI_CACHE_MINUTES)
    cached_ai = await db.portfolio_ai_cache.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    if cached_ai:
        generated_at = cached_ai.get("generated_at", "")
        try:
            gen_dt = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
            if gen_dt.tzinfo is None:
                gen_dt = gen_dt.replace(tzinfo=timezone.utc)
            if gen_dt > cache_cutoff:
                result = cached_ai.get("result", {})
                result["from_cache"] = True
                result["generated_at"] = generated_at
                return result
        except Exception:
            pass

    # ── Adună datele pentru prompt ──
    raw = await db.portfolio_bvb_pro.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).to_list(200)

    if not raw:
        raise HTTPException(status_code=400, detail="Portofoliu gol — adaugă poziții înainte de analiză AI")

    symbols = [p["symbol"] for p in raw]

    # Prețuri live + RSI în paralel
    async with httpx.AsyncClient() as client:
        prices, rsis = await asyncio.gather(
            asyncio.gather(*[_get_live_price(client, sym) for sym in symbols]),
            asyncio.gather(*[_get_rsi(client, sym) for sym in symbols]),
        )

    # Info companii
    stocks_db = await db.stocks_bvb.find(
        {"symbol": {"$in": symbols}}, {"_id": 0, "symbol": 1, "name": 1}
    ).to_list(200)
    info_map = {s["symbol"]: s for s in stocks_db}

    # Calculează P&L per poziție
    total_value = 0.0
    total_invested = 0.0
    positions_data = []

    for i, pos in enumerate(raw):
        sym = pos["symbol"]
        price_data = prices[i]
        current_price = price_data.get("price")
        shares = pos["shares"]
        purchase_price = pos["purchase_price"]
        invested = shares * purchase_price
        current_value = shares * current_price if current_price else None
        pl_ron = round(current_value - invested, 2) if current_value else None
        pl_pct = round((current_price - purchase_price) / purchase_price * 100, 2) if current_price else None

        rsi_val = rsis[i]
        total_invested += invested
        if current_value:
            total_value += current_value

        # Fundamentale din cache
        fund_cached = await db.fundamentals_daily_cache.find_one(
            {"symbol": sym}, {"_id": 0}
        )
        roe_raw = fund_cached.get("roe") if fund_cached else None
        roe_pct = round(roe_raw * 100, 1) if roe_raw is not None and abs(roe_raw) < 10 else roe_raw

        positions_data.append({
            "symbol": sym,
            "name": info_map.get(sym, {}).get("name", sym),
            "shares": shares,
            "purchase_price": purchase_price,
            "current_price": current_price,
            "price_change_percent": price_data.get("change_percent"),
            "current_value": round(current_value, 2) if current_value else None,
            "invested": round(invested, 2),
            "pl_ron": pl_ron,
            "pl_percent": pl_pct,
            "rsi": round(rsi_val, 1) if rsi_val else None,
            "rsi_signal": _rsi_signal(rsi_val),
            "fundamentals": {
                "pe_ratio": fund_cached.get("pe_ratio") if fund_cached else None,
                "roe_percent": roe_pct,
                "eps": fund_cached.get("eps") if fund_cached else None,
                "debt_equity": fund_cached.get("debt_equity") if fund_cached else None,
                "pb_ratio": fund_cached.get("pb_ratio") if fund_cached and fund_cached.get("pb_ratio") else None,
            } if fund_cached else {},
        })

    summary = {
        "total_value": round(total_value, 2),
        "total_invested": round(total_invested, 2),
        "pl_ron": round(total_value - total_invested, 2),
        "pl_percent": round((total_value - total_invested) / total_invested * 100, 2) if total_invested > 0 else 0,
        "today_pl": round(sum(
            (p.get("price_change_percent") or 0) / 100 * (p.get("current_value") or 0)
            for p in positions_data
        ), 2),
        "positions_count": len(positions_data),
    }

    # ── Apel AI ──
    prompt = _build_portfolio_prompt(positions_data, summary)
    logger.info(f"[AI PORTFOLIO] Generating analysis for user {user['user_id']} ({len(positions_data)} positions)")

    try:
        from utils.llm import LlmChat, UserMessage

        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f"portfolio_ai_{user['user_id']}",
            system_message=(
                "Ești un analist financiar expert pe piața BVB. "
                "Răspunzi EXCLUSIV în format JSON valid, fără text în afara JSON-ului. "
                "Ești direct, concis și bazat pe date reale. "
                "Folosești date financiare reale și confirmate. "
                "Nu estimezi, nu aproximezi, nu completezi lipsuri. "
                "Dacă o valoare nu există, marchezi ca N/A în comentarii."
            ),
        ).with_model("openai", "gpt-4o-mini")

        response = await chat.send_message(UserMessage(text=prompt))

        # Curăță răspunsul (scoate markdown dacă există)
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
        if clean.endswith("```"):
            clean = clean.rsplit("```", 1)[0]
        clean = clean.strip()

        ai_result = json.loads(clean)

    except json.JSONDecodeError as e:
        logger.error(f"[AI PORTFOLIO] JSON parse error: {e}\nResponse: {response[:300]}")
        raise HTTPException(status_code=500, detail="Răspuns AI invalid — încearcă din nou")
    except Exception as e:
        logger.error(f"[AI PORTFOLIO] AI error: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare AI: {str(e)[:100]}")

    generated_at = datetime.now(timezone.utc).isoformat()
    result = {
        **ai_result,
        "from_cache": False,
        "generated_at": generated_at,
        "positions_analyzed": len(positions_data),
    }

    # ── Salvare cache ──
    await db.portfolio_ai_cache.replace_one(
        {"user_id": user["user_id"]},
        {"user_id": user["user_id"], "result": result, "generated_at": generated_at},
        upsert=True,
    )

    logger.info(f"[AI PORTFOLIO] Analysis complete for {user['user_id']}")
    return result


# ─────────────────────────────────────────
# FAZA 4A: DIVIDENDE — Date reale BVB.ro per poziție
# ─────────────────────────────────────────

@router.get("/dividends")
async def get_portfolio_dividends(user: dict = Depends(require_auth)):
    """
    Faza 4 — Dividende pentru fiecare poziție deținută:
    - Dividend trailing 12 luni (din BVB.ro scraper, confirmat)
    - Randament dividend pe baza prețului curent EODHD
    - Income anual estimat = dividend/acțiune × cantitate deținută
    STRICT: null dacă nu există date confirmate BVB.ro
    """
    _require_pro(user)

    db = await get_database()
    raw = await db.portfolio_bvb_pro.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).to_list(200)

    if not raw:
        return {"dividends": [], "total_annual_income": 0}

    symbols = [p["symbol"] for p in raw]
    shares_map = {p["symbol"]: p["shares"] for p in raw}

    # Prețuri curente pentru calcul yield
    async with httpx.AsyncClient() as client:
        prices = await asyncio.gather(*[_get_live_price(client, sym) for sym in symbols])
    price_map = {sym: (prices[i].get("price")) for i, sym in enumerate(symbols)}

    # Trailing 12 luni dividende din BVB.ro scraper (date confirmate)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=400)).strftime("%Y-%m-%d")

    dividends = []
    total_income = 0.0

    for sym in symbols:
        payments = await db.bvb_dividends_scraped.find(
            {"symbol": sym, "ex_date": {"$gte": cutoff}},
            {"_id": 0, "dividend_per_share": 1, "ex_date": 1, "payment_date": 1}
        ).sort("ex_date", -1).to_list(20)

        trailing_annual = sum(float(p.get("dividend_per_share", 0)) for p in payments)
        current_price = price_map.get(sym)
        shares = shares_map.get(sym, 0)

        # Yield calculat strict pe baza prețului EODHD și dividendelor BVB.ro
        yield_pct = round(trailing_annual / current_price * 100, 2) if current_price and trailing_annual > 0 else None
        annual_income = round(trailing_annual * shares, 2) if trailing_annual > 0 else None

        if annual_income:
            total_income += annual_income

        dividends.append({
            "symbol": sym,
            "trailing_annual_dividend": round(trailing_annual, 6) if trailing_annual > 0 else None,
            "dividend_yield_pct": yield_pct,
            "annual_income_ron": annual_income,
            "shares": shares,
            "payments_count": len(payments),
            "last_ex_date": payments[0].get("ex_date") if payments else None,
            "source": "BVB.ro (confirmat)" if payments else "N/A",
        })

    return {
        "dividends": dividends,
        "total_annual_income": round(total_income, 2),
        "source": "BVB.ro (oficial)",
    }


# ─────────────────────────────────────────
# FAZA 4B: ȘTIRI — Filtrate per simboluri din portofoliu
# ─────────────────────────────────────────

# Mapping simbol → termeni de căutare (simbol + denumire companie)
SYMBOL_SEARCH_TERMS = {
    "TLV": ["TLV", "Banca Transilvania"],
    "BRD": ["BRD", "Société Générale"],
    "SNP": ["SNP", "OMV Petrom", "Petrom"],
    "SNG": ["SNG", "Romgaz"],
    "H2O": ["H2O", "Hidroelectrica"],
    "SNN": ["SNN", "Nuclearelectrica"],
    "TGN": ["TGN", "Transgaz"],
    "EL": ["EL", "Electrica"],
    "ONE": ["ONE", "One United"],
    "FP": ["FP", "Fondul Proprietatea"],
    "TEL": ["TEL", "Transgaz"],
    "TRP": ["TRP", "Teraplast"],
    "M": ["MedLife"],
    "COTE": ["COTE", "Conpet"],
    "WINE": ["Purcari"],
    "AQ": ["AQ", "Aquila"],
}


@router.get("/news")
async def get_portfolio_news(user: dict = Depends(require_auth)):
    """
    Faza 4 — Știri relevante filtrate pentru simbolurile din portofoliu.
    Caută în colecția articles după titlu cu termenii de căutare per simbol.
    """
    _require_pro(user)

    db = await get_database()
    raw = await db.portfolio_bvb_pro.find(
        {"user_id": user["user_id"]}, {"_id": 0, "symbol": 1}
    ).to_list(200)

    if not raw:
        return {"news": [], "symbols_searched": []}

    symbols = [p["symbol"] for p in raw]

    # Construiește termenii de căutare pentru fiecare simbol
    search_terms = []
    for sym in symbols:
        terms = SYMBOL_SEARCH_TERMS.get(sym, [sym])
        search_terms.extend(terms)

    # Query în DB: titlul conține oricare dintre termeni
    regex_pattern = "|".join(search_terms)

    articles = await db.articles.find(
        {
            "title": {"$regex": regex_pattern, "$options": "i"},
        },
        {
            "_id": 0,
            "id": 1,
            "title": 1,
            "title_ro": 1,
            "description": 1,
            "description_ro": 1,
            "image_url": 1,
            "source": 1,
            "published_at": 1,
            "url": 1,
        }
    ).sort("published_at", -1).limit(8).to_list(8)

    # Tag each article with which symbol(s) it's related to
    tagged = []
    for art in articles:
        title = (art.get("title") or "") + " " + (art.get("title_ro") or "")
        related = []
        for sym in symbols:
            terms = SYMBOL_SEARCH_TERMS.get(sym, [sym])
            if any(t.lower() in title.lower() for t in terms):
                related.append(sym)
        tagged.append({
            **art,
            "related_symbols": related,
        })

    return {
        "news": tagged,
        "symbols_searched": symbols,
        "count": len(tagged),
    }


# ─────────────────────────────────────────
# CSV IMPORT — Parse + Bulk Import
# ─────────────────────────────────────────

from fastapi import UploadFile, File
import csv
import io
import re


# BVB symbols whitelist (known valid symbols — fallback: accept anything 2-6 uppercase letters)
BVB_SYMBOL_RE = re.compile(r'^[A-Z0-9]{2,6}$')


def _normalize_symbol(raw: str) -> str:
    """Normalizează simbolul: elimină sufixe broker (RO, .BVB, etc.)"""
    s = raw.strip().upper()
    # XTB: TLVRO → TLV, SNPRO → SNP
    if s.endswith('RO') and len(s) > 4:
        candidate = s[:-2]
        if BVB_SYMBOL_RE.match(candidate):
            return candidate
    # Tradeville/generic: TLV.BVB → TLV
    s = s.split('.')[0].split('/')[0]
    return s


def _detect_broker(headers: list[str]) -> str:
    """Detectează brokerul din antetul CSV."""
    h = [c.lower().strip() for c in headers]
    # XTB: Position, Symbol, Type, Open price, Volume
    if any(x in h for x in ['position', 'open price', 'volume', 'open time']):
        return 'xtb'
    # Tradeville: Simbol, Cantitate, Pret mediu cumparare
    if any(x in h for x in ['simbol', 'cantitate', 'pret mediu', 'pret mediu cumparare']):
        return 'tradeville'
    return 'generic'


def _parse_xtb(reader) -> tuple[list, list]:
    """Parsează CSV de la XTB — poziții deschise."""
    positions = []
    errors = []
    for i, row in enumerate(reader):
        try:
            # XTB headers: Position, Symbol, Type, Open time, Open price, Nominal value, ...
            # sau: Position ID, Symbol, Volume, Open Price, ...
            symbol_raw = row.get('Symbol') or row.get('symbol') or ''
            volume_raw = row.get('Volume') or row.get('volume') or row.get('Qty') or ''
            price_raw = (
                row.get('Open price') or row.get('Open Price') or
                row.get('open price') or row.get('Open_price') or ''
            )
            if not symbol_raw or not volume_raw or not price_raw:
                errors.append(f"Rând {i+2}: câmpuri lipsă ({symbol_raw})")
                continue

            symbol = _normalize_symbol(symbol_raw)
            if not BVB_SYMBOL_RE.match(symbol):
                errors.append(f"Rând {i+2}: simbol invalid '{symbol_raw}'")
                continue

            shares = float(str(volume_raw).replace(',', '.'))
            price = float(str(price_raw).replace(',', '.'))

            if shares <= 0 or price <= 0:
                errors.append(f"Rând {i+2}: cantitate/preț invalid")
                continue

            positions.append({
                "symbol": symbol,
                "shares": shares,
                "purchase_price": round(price, 4),
            })
        except (ValueError, TypeError) as e:
            errors.append(f"Rând {i+2}: eroare de parsare — {e}")

    return positions, errors


def _parse_tradeville(reader) -> tuple[list, list]:
    """Parsează CSV de la Tradeville."""
    positions = []
    errors = []
    for i, row in enumerate(reader):
        try:
            symbol_raw = (
                row.get('Simbol') or row.get('simbol') or
                row.get('Symbol') or row.get('symbol') or ''
            )
            qty_raw = (
                row.get('Cantitate') or row.get('cantitate') or
                row.get('Qty') or row.get('Quantity') or ''
            )
            price_raw = (
                row.get('Pret mediu cumparare') or row.get('Pret mediu') or
                row.get('Pret') or row.get('Price') or row.get('price') or ''
            )
            if not symbol_raw or not qty_raw or not price_raw:
                errors.append(f"Rând {i+2}: câmpuri lipsă")
                continue

            symbol = _normalize_symbol(symbol_raw)
            if not BVB_SYMBOL_RE.match(symbol):
                errors.append(f"Rând {i+2}: simbol invalid '{symbol_raw}'")
                continue

            shares = float(str(qty_raw).replace(',', '.').replace(' ', ''))
            price = float(str(price_raw).replace(',', '.').replace(' ', ''))

            if shares <= 0 or price <= 0:
                errors.append(f"Rând {i+2}: cantitate/preț invalid")
                continue

            positions.append({
                "symbol": symbol,
                "shares": shares,
                "purchase_price": round(price, 4),
            })
        except (ValueError, TypeError) as e:
            errors.append(f"Rând {i+2}: eroare — {e}")

    return positions, errors


def _parse_generic(reader) -> tuple[list, list]:
    """Parsează CSV generic: Symbol/Simbol, Quantity/Cantitate, Price/Pret."""
    positions = []
    errors = []
    for i, row in enumerate(reader):
        try:
            symbol_raw = (
                row.get('Symbol') or row.get('symbol') or
                row.get('Simbol') or row.get('simbol') or
                row.get('Ticker') or row.get('ticker') or ''
            )
            qty_raw = (
                row.get('Quantity') or row.get('quantity') or
                row.get('Cantitate') or row.get('cantitate') or
                row.get('Shares') or row.get('shares') or
                row.get('Qty') or row.get('qty') or ''
            )
            price_raw = (
                row.get('Price') or row.get('price') or
                row.get('Pret') or row.get('pret') or
                row.get('Avg Price') or row.get('Purchase Price') or
                row.get('Pret mediu') or ''
            )
            if not symbol_raw or not qty_raw or not price_raw:
                errors.append(f"Rând {i+2}: câmpuri lipsă")
                continue

            symbol = _normalize_symbol(symbol_raw)
            if not BVB_SYMBOL_RE.match(symbol):
                errors.append(f"Rând {i+2}: simbol invalid '{symbol_raw}'")
                continue

            shares = float(str(qty_raw).replace(',', '.').replace(' ', ''))
            price = float(str(price_raw).replace(',', '.').replace(' ', ''))

            if shares <= 0 or price <= 0:
                errors.append(f"Rând {i+2}: cantitate/preț invalid")
                continue

            positions.append({
                "symbol": symbol,
                "shares": shares,
                "purchase_price": round(price, 4),
            })
        except (ValueError, TypeError) as e:
            errors.append(f"Rând {i+2}: eroare — {e}")

    return positions, errors


@router.post("/parse-csv")
async def parse_csv(
    file: UploadFile = File(...),
    user: dict = Depends(require_auth)
):
    """
    Parsează un CSV de la XTB, Tradeville sau format generic.
    Returnează pozițiile detectate + eventuale erori de parsare.
    Nu salvează nimic — doar preview.
    """
    _require_pro(user)

    if not file.filename.endswith(('.csv', '.txt')):
        raise HTTPException(status_code=400, detail="Fișierul trebuie să fie .csv")

    if file.size and file.size > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="Fișierul este prea mare (max 5MB)")

    try:
        content = await file.read()
        # Detectează encoding
        try:
            text = content.decode('utf-8-sig')  # BOM handling
        except UnicodeDecodeError:
            text = content.decode('latin-1')

        # Detectează delimitatorul (comma sau semicolon)
        delimiter = ';' if text.count(';') > text.count(',') else ','

        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
        headers = reader.fieldnames or []

        if not headers:
            raise HTTPException(status_code=400, detail="CSV gol sau fără antet")

        broker = _detect_broker(list(headers))

        rows = list(reader)
        if broker == 'xtb':
            positions, errors = _parse_xtb(rows)
        elif broker == 'tradeville':
            positions, errors = _parse_tradeville(rows)
        else:
            positions, errors = _parse_generic(rows)

        # Deduplicare — merge poziții cu același simbol (preț mediu ponderat)
        merged = {}
        for p in positions:
            sym = p['symbol']
            if sym in merged:
                existing = merged[sym]
                total_shares = existing['shares'] + p['shares']
                avg_price = (
                    (existing['shares'] * existing['purchase_price']) +
                    (p['shares'] * p['purchase_price'])
                ) / total_shares
                merged[sym] = {
                    'symbol': sym,
                    'shares': total_shares,
                    'purchase_price': round(avg_price, 4),
                }
            else:
                merged[sym] = p

        final_positions = list(merged.values())

        return {
            "broker": broker,
            "positions": final_positions,
            "errors": errors,
            "total_rows": len(rows),
            "valid_positions": len(final_positions),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CSV parse error: {e}")
        raise HTTPException(status_code=500, detail=f"Eroare la parsarea CSV: {str(e)}")


class ImportPositionsRequest(BaseModel):
    positions: List[AddPositionRequest]


@router.post("/import-positions")
async def import_positions(
    data: ImportPositionsRequest,
    user: dict = Depends(require_auth)
):
    """
    Importă bulk pozițiile parsate din CSV în portofoliu.
    Dacă există deja o poziție cu același simbol, face medie ponderată.
    """
    _require_pro(user)
    db = await get_database()
    user_id = user["user_id"]

    imported = 0
    updated = 0
    skipped = 0
    errors = []

    for pos in data.positions:
        try:
            symbol = pos.symbol.upper()

            existing = await db.portfolio_holdings.find_one(
                {"user_id": user_id, "symbol": symbol},
                {"_id": 0}
            )

            if existing:
                # Medie ponderată pentru preț de intrare
                old_shares = existing.get("shares", 0)
                old_price = existing.get("purchase_price", 0)
                new_shares = old_shares + pos.shares
                new_price = (
                    (old_shares * old_price + pos.shares * pos.purchase_price) / new_shares
                )

                await db.portfolio_holdings.update_one(
                    {"user_id": user_id, "symbol": symbol},
                    {"$set": {
                        "shares": new_shares,
                        "purchase_price": round(new_price, 4),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }}
                )
                updated += 1
            else:
                await db.portfolio_holdings.insert_one({
                    "user_id": user_id,
                    "symbol": symbol,
                    "shares": pos.shares,
                    "purchase_price": pos.purchase_price,
                    "purchase_date": pos.purchase_date,
                    "notes": pos.notes,
                    "added_at": datetime.now(timezone.utc).isoformat(),
                })
                imported += 1

        except Exception as e:
            logger.error(f"Import error for {pos.symbol}: {e}")
            errors.append(str(e))
            skipped += 1

    logger.info(f"CSV import for {user_id}: {imported} imported, {updated} updated, {skipped} skipped")

    return {
        "success": True,
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
        "message": f"Import complet: {imported} noi, {updated} actualizate",
    }

