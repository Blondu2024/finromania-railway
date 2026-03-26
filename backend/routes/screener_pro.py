"""
SCREENER PRO - Advanced Stock Screener pentru FinRomania
Date LIVE de la EODHD: Indicatori Tehnici + Fundamentale + Semnale
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import asyncio
import httpx
import logging
import os

from config.database import get_database
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/screener-pro", tags=["Screener PRO"])

EODHD_API_KEY = os.environ.get("EODHD_API_KEY")
EODHD_BASE = "https://eodhd.com/api"

# ============================================
# MODELS
# ============================================

class ProScreenerRequest(BaseModel):
    """Request pentru Screener PRO"""
    # Filtre tehnice
    min_rsi: Optional[float] = None
    max_rsi: Optional[float] = None
    rsi_signal: Optional[str] = None  # oversold, overbought, neutral
    macd_signal: Optional[str] = None  # bullish, bearish
    above_sma20: Optional[bool] = None
    above_sma50: Optional[bool] = None
    
    # Filtre fundamentale
    min_pe: Optional[float] = None
    max_pe: Optional[float] = None
    min_roe: Optional[float] = None
    min_eps: Optional[float] = None
    min_dividend_yield: Optional[float] = None
    max_debt_equity: Optional[float] = None
    
    # Filtre preț
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_change: Optional[float] = None
    max_change: Optional[float] = None
    
    # Semnale
    signal_filter: Optional[str] = None  # strong_buy, buy, hold, sell, strong_sell
    
    # Sortare și limită
    sort_by: str = "signal_score"
    sort_order: str = "desc"
    limit: int = 50


# ============================================
# EODHD API HELPERS
# ============================================

async def fetch_technical_indicator(client: httpx.AsyncClient, symbol: str, function: str, period: int = 14) -> Optional[Dict]:
    """Fetch un indicator tehnic de la EODHD"""
    try:
        url = f"{EODHD_BASE}/technical/{symbol}.RO"
        params = {
            "api_token": EODHD_API_KEY,
            "fmt": "json",
            "function": function,
            "period": period
        }
        r = await client.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data and len(data) > 0:
                return data[-1]  # Ultima valoare
    except Exception as e:
        logger.warning(f"Error fetching {function} for {symbol}: {e}")
    return None


async def fetch_fundamentals(client: httpx.AsyncClient, symbol: str) -> Optional[Dict]:
    """Fetch date fundamentale de la EODHD"""
    try:
        url = f"{EODHD_BASE}/fundamentals/{symbol}.RO"
        params = {"api_token": EODHD_API_KEY, "fmt": "json"}
        r = await client.get(url, params=params, timeout=15)
        if r.status_code == 200:
            data = r.json()
            highlights = data.get("Highlights", {})
            valuation = data.get("Valuation", {})
            return {
                "pe_ratio": highlights.get("PERatio"),
                "eps": highlights.get("EarningsShare"),
                "roe": highlights.get("ReturnOnEquityTTM"),
                "roa": highlights.get("ReturnOnAssetsTTM"),
                "profit_margin": highlights.get("ProfitMargin"),
                "dividend_yield": highlights.get("DividendYield"),
                "dividend_share": highlights.get("DividendShare"),
                "market_cap": highlights.get("MarketCapitalization"),
                "pb_ratio": valuation.get("PriceBookMRQ"),
                "ps_ratio": valuation.get("PriceSalesTTM"),
                "ev": valuation.get("EnterpriseValue"),
                "52_week_high": highlights.get("52WeekHigh"),
                "52_week_low": highlights.get("52WeekLow"),
                "beta": highlights.get("Beta"),
            }
    except Exception as e:
        logger.warning(f"Error fetching fundamentals for {symbol}: {e}")
    return None


async def fetch_stock_technicals(client: httpx.AsyncClient, symbol: str) -> Dict:
    """Fetch toți indicatorii tehnici pentru o acțiune"""
    # Parallel fetch pentru viteză
    rsi_task = fetch_technical_indicator(client, symbol, "rsi", 14)
    macd_task = fetch_technical_indicator(client, symbol, "macd")
    bbands_task = fetch_technical_indicator(client, symbol, "bbands")
    sma20_task = fetch_technical_indicator(client, symbol, "sma", 20)
    sma50_task = fetch_technical_indicator(client, symbol, "sma", 50)
    ema12_task = fetch_technical_indicator(client, symbol, "ema", 12)
    
    results = await asyncio.gather(
        rsi_task, macd_task, bbands_task, sma20_task, sma50_task, ema12_task,
        return_exceptions=True
    )
    
    rsi_data, macd_data, bb_data, sma20_data, sma50_data, ema12_data = results
    
    return {
        "rsi": rsi_data.get("rsi") if isinstance(rsi_data, dict) else None,
        "macd": macd_data.get("macd") if isinstance(macd_data, dict) else None,
        "macd_signal": macd_data.get("macd_signal") if isinstance(macd_data, dict) else None,
        "macd_histogram": macd_data.get("macd_hist") if isinstance(macd_data, dict) else None,
        "bb_upper": bb_data.get("uband") if isinstance(bb_data, dict) else None,
        "bb_middle": bb_data.get("mband") if isinstance(bb_data, dict) else None,
        "bb_lower": bb_data.get("lband") if isinstance(bb_data, dict) else None,
        "sma20": sma20_data.get("sma") if isinstance(sma20_data, dict) else None,
        "sma50": sma50_data.get("sma") if isinstance(sma50_data, dict) else None,
        "ema12": ema12_data.get("ema") if isinstance(ema12_data, dict) else None,
    }


def calculate_signal(price: float, technicals: Dict, fundamentals: Dict) -> Dict:
    """Calculează semnalul de tranzacționare bazat pe indicatori"""
    score = 50  # Neutral starting point
    signals = []
    warnings = []
    
    rsi = technicals.get("rsi")
    macd = technicals.get("macd")
    macd_sig = technicals.get("macd_signal")
    sma20 = technicals.get("sma20")
    sma50 = technicals.get("sma50")
    bb_lower = technicals.get("bb_lower")
    bb_upper = technicals.get("bb_upper")
    
    pe = fundamentals.get("pe_ratio") if fundamentals else None
    roe = fundamentals.get("roe") if fundamentals else None
    
    # === RSI Analysis ===
    if rsi is not None:
        if rsi < 30:
            score += 20
            signals.append(("RSI Supravândut", "bullish", f"RSI={rsi:.1f} < 30"))
        elif rsi < 40:
            score += 10
            signals.append(("RSI Favorabil", "bullish", f"RSI={rsi:.1f}"))
        elif rsi > 70:
            score -= 20
            signals.append(("RSI Supracumpărat", "bearish", f"RSI={rsi:.1f} > 70"))
        elif rsi > 60:
            score -= 10
            signals.append(("RSI Ridicat", "bearish", f"RSI={rsi:.1f}"))
    
    # === MACD Analysis ===
    if macd is not None and macd_sig is not None:
        if macd > macd_sig:
            score += 15
            signals.append(("MACD Bullish", "bullish", "MACD > Signal"))
        else:
            score -= 15
            signals.append(("MACD Bearish", "bearish", "MACD < Signal"))
    elif macd is not None:
        if macd > 0:
            score += 10
            signals.append(("MACD Pozitiv", "bullish", f"MACD={macd:.3f}"))
        else:
            score -= 10
            signals.append(("MACD Negativ", "bearish", f"MACD={macd:.3f}"))
    
    # === Moving Averages ===
    if price and sma20:
        if price > sma20:
            score += 10
            signals.append(("Peste SMA20", "bullish", f"Preț > SMA20"))
        else:
            score -= 10
            signals.append(("Sub SMA20", "bearish", f"Preț < SMA20"))
    
    if price and sma50:
        if price > sma50:
            score += 10
            signals.append(("Peste SMA50", "bullish", f"Preț > SMA50"))
        else:
            score -= 10
            signals.append(("Sub SMA50", "bearish", f"Preț < SMA50"))
    
    # Golden Cross / Death Cross
    if sma20 and sma50:
        if sma20 > sma50:
            score += 5
            signals.append(("Golden Cross", "bullish", "SMA20 > SMA50"))
        else:
            score -= 5
            signals.append(("Death Cross", "bearish", "SMA20 < SMA50"))
    
    # === Bollinger Bands ===
    if price and bb_lower and bb_upper:
        if price <= bb_lower:
            score += 15
            signals.append(("La Bollinger Inferior", "bullish", "Potențial rebound"))
        elif price >= bb_upper:
            score -= 15
            signals.append(("La Bollinger Superior", "bearish", "Potențial corecție"))
    
    # === Fundamentale ===
    if pe is not None:
        if 0 < pe < 10:
            score += 10
            signals.append(("P/E Atractiv", "bullish", f"P/E={pe:.1f} < 10"))
        elif pe > 25:
            score -= 5
            warnings.append(f"P/E ridicat: {pe:.1f}")
    
    if roe is not None:
        roe_pct = roe * 100 if roe < 1 else roe
        if roe_pct > 15:
            score += 10
            signals.append(("ROE Excelent", "bullish", f"ROE={roe_pct:.1f}%"))
    
    # === Determine Signal ===
    if score >= 75:
        signal = "STRONG_BUY"
        signal_text = "Cumpărare Puternică"
        color = "#16a34a"
    elif score >= 60:
        signal = "BUY"
        signal_text = "Cumpărare"
        color = "#22c55e"
    elif score <= 25:
        signal = "STRONG_SELL"
        signal_text = "Vânzare Puternică"
        color = "#dc2626"
    elif score <= 40:
        signal = "SELL"
        signal_text = "Vânzare"
        color = "#f97316"
    else:
        signal = "HOLD"
        signal_text = "Păstrare"
        color = "#6b7280"
    
    return {
        "signal": signal,
        "signal_text": signal_text,
        "signal_color": color,
        "score": score,
        "signals": signals,
        "warnings": warnings
    }


# ============================================
# ENDPOINTS
# ============================================

@router.get("/scan")
async def scan_all_stocks(user: dict = Depends(require_auth)):
    """
    PRO Feature: Scanează toate acțiunile BVB cu indicatori tehnici și fundamentale LIVE
    """
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(status_code=403, detail="Screener PRO necesită abonament PRO")
    
    db = await get_database()
    stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
    
    if not stocks:
        return {"stocks": [], "count": 0}
    
    results = []
    
    async with httpx.AsyncClient() as client:
        # Process in batches pentru a nu supraîncărca API-ul
        batch_size = 5
        for i in range(0, len(stocks), batch_size):
            batch = stocks[i:i+batch_size]
            
            tasks = []
            for stock in batch:
                symbol = stock.get("symbol")
                tasks.append(process_stock(client, stock))
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, dict):
                    results.append(result)
            
            # Small delay între batches
            if i + batch_size < len(stocks):
                await asyncio.sleep(0.5)
    
    # Sort by signal score descending
    results.sort(key=lambda x: x.get("signal_score", 0), reverse=True)
    
    return {
        "stocks": results,
        "count": len(results),
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "is_live": True
    }


async def process_stock(client: httpx.AsyncClient, stock: Dict) -> Dict:
    """Procesează o acțiune - fetch technicals + fundamentals + calculate signal"""
    symbol = stock.get("symbol")
    price = stock.get("price", 0)
    
    # Fetch în paralel
    tech_task = fetch_stock_technicals(client, symbol)
    fund_task = fetch_fundamentals(client, symbol)
    
    technicals, fundamentals = await asyncio.gather(tech_task, fund_task)
    
    # Calculate signal
    signal_data = calculate_signal(price, technicals, fundamentals or {})
    
    return {
        "symbol": symbol,
        "name": stock.get("name"),
        "sector": stock.get("sector"),
        "price": price,
        "change": stock.get("change"),
        "change_percent": stock.get("change_percent"),
        "volume": stock.get("volume"),
        # Technicals
        "rsi": round(technicals.get("rsi"), 2) if technicals.get("rsi") else None,
        "macd": round(technicals.get("macd"), 4) if technicals.get("macd") else None,
        "macd_signal": round(technicals.get("macd_signal"), 4) if technicals.get("macd_signal") else None,
        "sma20": round(technicals.get("sma20"), 2) if technicals.get("sma20") else None,
        "sma50": round(technicals.get("sma50"), 2) if technicals.get("sma50") else None,
        "bb_upper": round(technicals.get("bb_upper"), 2) if technicals.get("bb_upper") else None,
        "bb_lower": round(technicals.get("bb_lower"), 2) if technicals.get("bb_lower") else None,
        # Fundamentals
        "pe_ratio": round(fundamentals.get("pe_ratio"), 2) if fundamentals and fundamentals.get("pe_ratio") else None,
        "roe": round(fundamentals.get("roe") * 100, 2) if fundamentals and fundamentals.get("roe") else None,
        "eps": round(fundamentals.get("eps"), 2) if fundamentals and fundamentals.get("eps") else None,
        "dividend_yield": round(fundamentals.get("dividend_yield") * 100, 2) if fundamentals and fundamentals.get("dividend_yield") else None,
        "market_cap": fundamentals.get("market_cap") if fundamentals else None,
        "pb_ratio": round(fundamentals.get("pb_ratio"), 2) if fundamentals and fundamentals.get("pb_ratio") else None,
        "52_week_high": fundamentals.get("52_week_high") if fundamentals else None,
        "52_week_low": fundamentals.get("52_week_low") if fundamentals else None,
        # Signal
        "signal": signal_data["signal"],
        "signal_text": signal_data["signal_text"],
        "signal_color": signal_data["signal_color"],
        "signal_score": signal_data["score"],
        "signal_reasons": signal_data["signals"],
        "warnings": signal_data["warnings"],
    }


@router.post("/filter")
async def filter_stocks(request: ProScreenerRequest, user: dict = Depends(require_auth)):
    """
    PRO Feature: Filtrează acțiunile după criterii avansate
    """
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(status_code=403, detail="Screener PRO necesită abonament PRO")
    
    # First get all scanned stocks
    scan_result = await scan_all_stocks(user)
    stocks = scan_result.get("stocks", [])
    
    # Apply filters
    filtered = []
    for stock in stocks:
        # RSI filters
        if request.min_rsi and (stock.get("rsi") is None or stock.get("rsi") < request.min_rsi):
            continue
        if request.max_rsi and (stock.get("rsi") is None or stock.get("rsi") > request.max_rsi):
            continue
        
        # RSI signal filter
        if request.rsi_signal:
            rsi = stock.get("rsi")
            if rsi is None:
                continue
            if request.rsi_signal == "oversold" and rsi >= 30:
                continue
            if request.rsi_signal == "overbought" and rsi <= 70:
                continue
        
        # MACD filter
        if request.macd_signal:
            macd = stock.get("macd")
            macd_sig = stock.get("macd_signal")
            if macd is None:
                continue
            if request.macd_signal == "bullish" and (macd_sig is None or macd <= macd_sig):
                continue
            if request.macd_signal == "bearish" and (macd_sig is None or macd >= macd_sig):
                continue
        
        # SMA filters
        price = stock.get("price", 0)
        if request.above_sma20 is not None:
            sma20 = stock.get("sma20")
            if sma20 is None:
                continue
            if request.above_sma20 and price <= sma20:
                continue
            if not request.above_sma20 and price > sma20:
                continue
        
        if request.above_sma50 is not None:
            sma50 = stock.get("sma50")
            if sma50 is None:
                continue
            if request.above_sma50 and price <= sma50:
                continue
            if not request.above_sma50 and price > sma50:
                continue
        
        # Fundamental filters
        if request.min_pe and (stock.get("pe_ratio") is None or stock.get("pe_ratio") < request.min_pe):
            continue
        if request.max_pe and (stock.get("pe_ratio") is None or stock.get("pe_ratio") > request.max_pe):
            continue
        if request.min_roe and (stock.get("roe") is None or stock.get("roe") < request.min_roe):
            continue
        if request.min_eps and (stock.get("eps") is None or stock.get("eps") < request.min_eps):
            continue
        if request.min_dividend_yield and (stock.get("dividend_yield") is None or stock.get("dividend_yield") < request.min_dividend_yield):
            continue
        
        # Price filters
        if request.min_price and price < request.min_price:
            continue
        if request.max_price and price > request.max_price:
            continue
        if request.min_change and (stock.get("change_percent") is None or stock.get("change_percent") < request.min_change):
            continue
        if request.max_change and (stock.get("change_percent") is None or stock.get("change_percent") > request.max_change):
            continue
        
        # Signal filter
        if request.signal_filter:
            if stock.get("signal") != request.signal_filter.upper():
                continue
        
        filtered.append(stock)
    
    # Sort
    sort_key = request.sort_by
    reverse = request.sort_order == "desc"
    filtered.sort(key=lambda x: x.get(sort_key) or 0, reverse=reverse)
    
    # Limit
    filtered = filtered[:request.limit]
    
    return {
        "stocks": filtered,
        "count": len(filtered),
        "total_scanned": len(stocks),
        "filters_applied": request.dict(exclude_none=True)
    }


@router.get("/stock/{symbol}")
async def get_stock_analysis(symbol: str, user: dict = Depends(require_auth)):
    """
    PRO Feature: Analiză detaliată pentru o singură acțiune
    """
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(status_code=403, detail="Analiză PRO necesită abonament PRO")
    
    db = await get_database()
    stock = await db.stocks_bvb.find_one({"symbol": symbol.upper()}, {"_id": 0})
    
    if not stock:
        raise HTTPException(status_code=404, detail=f"Acțiunea {symbol} nu a fost găsită")
    
    async with httpx.AsyncClient() as client:
        result = await process_stock(client, stock)
    
    return {
        "stock": result,
        "analyzed_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/signals/summary")
async def get_signals_summary(user: dict = Depends(require_auth)):
    """
    PRO Feature: Sumar semnale - câte acțiuni sunt pe fiecare semnal
    """
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(status_code=403, detail="Screener PRO necesită abonament PRO")
    
    scan_result = await scan_all_stocks(user)
    stocks = scan_result.get("stocks", [])
    
    summary = {
        "STRONG_BUY": [],
        "BUY": [],
        "HOLD": [],
        "SELL": [],
        "STRONG_SELL": []
    }
    
    for stock in stocks:
        signal = stock.get("signal", "HOLD")
        if signal in summary:
            summary[signal].append({
                "symbol": stock.get("symbol"),
                "name": stock.get("name"),
                "price": stock.get("price"),
                "change_percent": stock.get("change_percent"),
                "score": stock.get("signal_score")
            })
    
    return {
        "summary": {
            signal: {
                "count": len(stocks_list),
                "stocks": stocks_list[:5]  # Top 5 per category
            }
            for signal, stocks_list in summary.items()
        },
        "total": len(stocks),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/presets")
async def get_screener_presets():
    """Preset-uri pentru Screener PRO"""
    return {
        "presets": [
            {
                "id": "oversold_quality",
                "name": "Supravândute + Calitate",
                "description": "RSI < 35 + ROE > 10% + P/E < 15",
                "icon": "gem",
                "filters": {
                    "max_rsi": 35,
                    "min_roe": 10,
                    "max_pe": 15
                }
            },
            {
                "id": "momentum_play",
                "name": "Momentum Bullish",
                "description": "RSI 50-70 + MACD Bullish + Peste SMA20",
                "icon": "rocket",
                "filters": {
                    "min_rsi": 50,
                    "max_rsi": 70,
                    "macd_signal": "bullish",
                    "above_sma20": True
                }
            },
            {
                "id": "dividend_hunters",
                "name": "Vânătorii de Dividende",
                "description": "Dividend Yield > 5% + P/E < 12",
                "icon": "coins",
                "filters": {
                    "min_dividend_yield": 5,
                    "max_pe": 12
                }
            },
            {
                "id": "value_play",
                "name": "Value Investing",
                "description": "P/E < 10 + ROE > 12% + EPS > 0",
                "icon": "target",
                "filters": {
                    "max_pe": 10,
                    "min_roe": 12,
                    "min_eps": 0.01
                }
            },
            {
                "id": "strong_buy",
                "name": "Semnale STRONG BUY",
                "description": "Acțiuni cu cel mai puternic semnal de cumpărare",
                "icon": "trophy",
                "filters": {
                    "signal_filter": "strong_buy"
                }
            },
            {
                "id": "contrarian",
                "name": "Contrarian Play",
                "description": "Scăderi > 5% azi + RSI < 40 (potențial rebound)",
                "icon": "refresh",
                "filters": {
                    "max_change": -5,
                    "max_rsi": 40
                }
            }
        ]
    }
