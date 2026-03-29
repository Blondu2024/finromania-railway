"""
SCREENER PRO - Advanced Stock Screener pentru FinRomania
Date LIVE de la EODHD: Indicatori Tehnici + Fundamentale + Semnale

POLITICĂ DE DATE (aplicată strict):
- Dividend Yield: DOAR din dividende confirmate BVB.ro (nu EODHD estimate)
- P/E: valid DOAR dacă EPS > 0 (raportat, nu proiecție)
- ROE: DOAR valoarea raportată de EODHD, fără estimări sau calcule derivate
- Debt/Equity: calculat din bilanț EODHD dacă disponibil, altfel null
- Dacă valoarea lipsește → null (nu 0, nu estimare)
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta
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
FUNDAMENTALS_CACHE_COLLECTION = "fundamentals_daily_cache"

# Flag pentru a preveni rulări simultane ale scan-ului
_scan_running = False


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


def _extract_debt_equity(data: dict) -> Optional[float]:
    """
    Extrage Datorie/Capitaluri proprii din bilanțul EODHD.
    Returnează null dacă datele nu sunt disponibile sau incomplete. Nu calculează/estimează.
    
    EODHD câmpuri confirmate: totalLiab, totalStockholderEquity, shortLongTermDebtTotal
    """
    try:
        yearly = (
            data.get("Financials", {})
                .get("Balance_Sheet", {})
                .get("yearly", {})
        )
        if not yearly:
            return None
        latest_key = max(yearly.keys())
        bs = yearly[latest_key]

        # Câmpuri confirmate din EODHD pentru BVB
        # Preferăm datorii financiare specifice (nu total liabilities care include și liabilities operaționale)
        total_debt = float(
            bs.get("shortLongTermDebtTotal") or
            bs.get("longTermDebtTotal") or
            bs.get("longTermDebt") or
            bs.get("totalLiab") or
            0
        )
        equity = float(
            bs.get("totalStockholderEquity") or
            bs.get("totalShareholderEquity") or
            bs.get("stockholdersEquity") or
            bs.get("commonStockEquity") or
            0
        )
        if equity > 0:
            return round(total_debt / equity, 2)
    except Exception:
        pass
    return None


async def fetch_fundamentals(client: httpx.AsyncClient, symbol: str) -> Optional[Dict]:
    """Fetch date fundamentale de la EODHD.

    POLITICĂ STRICTĂ DE DATE — nu estimăm, nu aproximăm, nu completăm lipsuri:
    - P/E: valid DOAR dacă EPS > 0 (Trailing P/E, nu Forward P/E estimat)
    - ROE: DOAR valoarea raportată de EODHD, fără calcule derivate sau estimări
    - EPS: DOAR valoarea reală raportată (EarningsShare sau DilutedEpsTTM), NU EPSEstimate
    - D/E: calculat din bilanț EODHD dacă disponibil, altfel null
    - Dividend Yield: NU se returnează (calculat separat STRICT din BVB.ro confirmat)
    """
    # Manual overrides pentru valori confirmate BVB.ro (EODHD incorect)
    MANUAL_OVERRIDES = {
        "M": {"eps_override": -0.02, "pe_override": None},
        "H2O": {"eps_override": 6.73, "pe_override": 21.98},  # Hidroelectrica: EPS=6.73 si P/E=21.98 conform BVB.ro
    }

    try:
        url = f"{EODHD_BASE}/fundamentals/{symbol}.RO"
        params = {"api_token": EODHD_API_KEY, "fmt": "json"}
        r = await client.get(url, params=params, timeout=15)
        if r.status_code == 200:
            data = r.json()
            highlights = data.get("Highlights", {})
            valuation = data.get("Valuation", {})

            pe_ratio_raw = highlights.get("PERatio")
            trailing_pe = valuation.get("TrailingPE")
            roe_raw = highlights.get("ReturnOnEquityTTM")
            eps_raw = highlights.get("EarningsShare")
            diluted_eps = highlights.get("DilutedEpsTTM")

            # Aplică manual overrides pentru valori EODHD cunoscute ca incorecte
            override = MANUAL_OVERRIDES.get(symbol, {})
            if "eps_override" in override:
                eps_raw = override["eps_override"]
                logger.info(f"{symbol}: Manual EPS override → {eps_raw}")
            if "pe_override" in override:
                pe_ratio_raw = override["pe_override"]
                trailing_pe = None
                logger.info(f"{symbol}: Manual P/E override → None")

            # === P/E: STRICT — Trailing P/E din EODHD, NU Forward P/E (proiecție) ===
            pe_ratio = None
            if pe_ratio_raw and 0 < float(pe_ratio_raw) < 500:
                pe_ratio = float(pe_ratio_raw)
            elif trailing_pe and 0 < float(trailing_pe) < 500:
                pe_ratio = float(trailing_pe)
            # ForwardPE exclus — este o proiecție, nu date reale raportate

            # === ROE: STRICT — valoarea raportată, fără estimări sau calcule derivate ===
            # Negative ROE este valid (companie cu pierderi). Nu estimăm din profit_margin.
            roe = float(roe_raw) if roe_raw is not None else None

            # === EPS: STRICT — EarningsShare sau DilutedEpsTTM, NU EPSEstimateCurrentYear ===
            eps = None
            if eps_raw is not None:
                eps = float(eps_raw)
            elif diluted_eps is not None:
                eps = float(diluted_eps)
            # EPSEstimateCurrentYear exclus — este o proiecție, nu date reale

            # === Debt/Equity din bilanțul EODHD ===
            debt_equity = _extract_debt_equity(data)

            technicals_data = data.get("Technicals", {})
            general_data = data.get("General", {})

            return {
                "logo_url": general_data.get("LogoURL"),
                "pe_ratio": pe_ratio,
                "eps": eps,
                "roe": roe,
                "roa": highlights.get("ReturnOnAssetsTTM"),
                "profit_margin": highlights.get("ProfitMargin"),
                "market_cap": highlights.get("MarketCapitalization"),
                "pb_ratio": valuation.get("PriceBookMRQ"),
                "ps_ratio": valuation.get("PriceSalesTTM"),
                "ev": valuation.get("EnterpriseValue"),
                "52_week_high": technicals_data.get("52WeekHigh"),
                "52_week_low": technicals_data.get("52WeekLow"),
                "beta": technicals_data.get("Beta"),
                "200_day_ma": technicals_data.get("200DayMA"),
                "book_value": highlights.get("BookValue"),
                "debt_equity": debt_equity,
            }
    except Exception as e:
        logger.warning(f"Error fetching fundamentals for {symbol}: {e}")
    return None


async def fetch_stock_technicals(client: httpx.AsyncClient, symbol: str) -> Dict:
    """Fetch toți indicatorii tehnici pentru o acțiune"""
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
        "macd_signal": macd_data.get("signal", macd_data.get("macd_signal")) if isinstance(macd_data, dict) else None,
        "macd_histogram": macd_data.get("divergence", macd_data.get("macd_hist")) if isinstance(macd_data, dict) else None,
        "bb_upper": bb_data.get("uband") if isinstance(bb_data, dict) else None,
        "bb_middle": bb_data.get("mband") if isinstance(bb_data, dict) else None,
        "bb_lower": bb_data.get("lband") if isinstance(bb_data, dict) else None,
        "sma20": sma20_data.get("sma") if isinstance(sma20_data, dict) else None,
        "sma50": sma50_data.get("sma") if isinstance(sma50_data, dict) else None,
        "ema12": ema12_data.get("ema") if isinstance(ema12_data, dict) else None,
    }


# ============================================
# DIVIDEND YIELD — STRICT din BVB.ro
# ============================================

def _get_confirmed_yield_from_bvb(
    symbol: str,
    price: float,
    bvb_records: list
) -> Optional[float]:
    """
    Dividend Yield = dividende confirmate BVB.ro (trailing ~12 luni) / preț curent.

    STRICT:
    - Folosește DOAR dividende confirmate de pe BVB.ro (din scraper)
    - Dacă nu există dividende confirmate → returnează None (nu 0, nu estimare)
    - Dacă prețul este 0 sau lipsă → returnează None
    - Nu folosește DividendYield din EODHD (poate fi estimat sau neactualizat)
    """
    if not price or price <= 0 or not bvb_records:
        return None
    cutoff = (datetime.now(timezone.utc) - timedelta(days=400)).strftime("%Y-%m-%d")
    payments = [
        r for r in bvb_records
        if r.get("symbol") == symbol and r.get("ex_date", "") >= cutoff
    ]
    if not payments:
        return None
    trailing = sum(float(r.get("dividend_per_share", 0)) for r in payments)
    if trailing <= 0:
        return None
    return round(trailing / price * 100, 2)


# ============================================
# SIGNAL CALCULATION
# ============================================

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
            signals.append(("Peste SMA20", "bullish", "Preț > SMA20"))
        else:
            score -= 10
            signals.append(("Sub SMA20", "bearish", "Preț < SMA20"))

    if price and sma50:
        if price > sma50:
            score += 10
            signals.append(("Peste SMA50", "bullish", "Preț > SMA50"))
        else:
            score -= 10
            signals.append(("Sub SMA50", "bearish", "Preț < SMA50"))

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
        roe_pct = roe * 100 if abs(roe) < 10 else roe
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
# DAILY FUNDAMENTALS CACHE
# ============================================

async def get_fundamentals_from_daily_cache(symbol: str) -> Optional[Dict]:
    """
    Returnează fundamentalele din cache-ul zilnic (< 24h).
    Cache-ul este actualizat o dată pe zi la 8:00 AM.
    Fundamentalele (P/E, ROE, EPS, D/E) nu se schimbă intraday.
    """
    try:
        db = await get_database()
        cached = await db[FUNDAMENTALS_CACHE_COLLECTION].find_one(
            {"symbol": symbol}, {"_id": 0}
        )
        if not cached:
            return None
        cached_at = cached.get("cached_at", "")
        if isinstance(cached_at, str):
            cached_at = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
        if cached_at.tzinfo is None:
            cached_at = cached_at.replace(tzinfo=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - cached_at).total_seconds() / 3600
        if age_hours > 24:
            return None
        return cached
    except Exception as e:
        logger.warning(f"Fundamentals cache read error for {symbol}: {e}")
        return None


async def refresh_fundamentals_daily_cache():
    """
    Actualizează cache-ul zilnic de fundamentale pentru toate acțiunile BVB.
    Salvează din EODHD: P/E, ROE, EPS, D/E (valori reale, fără estimări).
    Se rulează zilnic la 8:00 AM din scheduler.
    """
    try:
        db = await get_database()
        stocks = await db.stocks_bvb.find({}, {"_id": 0, "symbol": 1}).to_list(200)
        logger.info(f"[FUND CACHE] Starting daily refresh for {len(stocks)} stocks")

        async with httpx.AsyncClient() as client:
            for stock in stocks:
                symbol = stock.get("symbol")
                try:
                    fund = await fetch_fundamentals(client, symbol)
                    if fund:
                        await db[FUNDAMENTALS_CACHE_COLLECTION].replace_one(
                            {"symbol": symbol},
                            {
                                "symbol": symbol,
                                "logo_url": fund.get("logo_url"),
                                "pe_ratio": fund.get("pe_ratio"),
                                "eps": fund.get("eps"),
                                "roe": fund.get("roe"),
                                "roa": fund.get("roa"),
                                "profit_margin": fund.get("profit_margin"),
                                "market_cap": fund.get("market_cap"),
                                "pb_ratio": fund.get("pb_ratio"),
                                "beta": fund.get("beta"),
                                "book_value": fund.get("book_value"),
                                "52_week_high": fund.get("52_week_high"),
                                "52_week_low": fund.get("52_week_low"),
                                "debt_equity": fund.get("debt_equity"),
                                "cached_at": datetime.now(timezone.utc).isoformat(),
                            },
                            upsert=True
                        )
                    await asyncio.sleep(0.3)  # Rate limit EODHD
                except Exception as e:
                    logger.warning(f"[FUND CACHE] Error for {symbol}: {e}")

        logger.info("[FUND CACHE] Daily refresh complete")
    except Exception as e:
        logger.error(f"[FUND CACHE] Daily refresh error: {e}")


# ============================================
# HELPER: Screener Cache Management
# ============================================

async def get_scan_cache(max_age_minutes: int = 45):
    """Returnează cache-ul din MongoDB dacă e proaspăt."""
    try:
        db = await get_database()
        cache = await db.screener_pro_cache.find_one({}, {"_id": 0})
        if not cache:
            return None
        scanned_at = cache.get("scanned_at")
        if isinstance(scanned_at, str):
            scanned_at = datetime.fromisoformat(scanned_at.replace("Z", "+00:00"))
        if scanned_at.tzinfo is None:
            scanned_at = scanned_at.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - scanned_at
        if age.total_seconds() / 60 > max_age_minutes:
            return None
        return cache
    except Exception as e:
        logger.error(f"Error reading screener cache: {e}")
        return None


async def run_scan_and_cache():
    """Rulează scanarea completă și salvează în cache MongoDB."""
    global _scan_running
    if _scan_running:
        logger.info("Screener scan already running, skipping")
        return

    _scan_running = True
    logger.info("[SCREENER] Starting background scan...")

    try:
        db = await get_database()
        # Actiuni excluse din screener (delisting, date invalide)
        EXCLUDED_SYMBOLS = {"FP"}  # FP - Fondul Proprietatea: delisting in curs, date tehnice aberante

        stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        stocks = [s for s in stocks if s.get("symbol") not in EXCLUDED_SYMBOLS]

        if not stocks:
            return

        # Pre-fetch dividende confirmate BVB.ro O SINGURĂ DATĂ pentru toate acțiunile
        from scrapers.bvb_dividend_scraper import get_cached_dividends
        bvb_records, _ = await get_cached_dividends()
        logger.info(f"[SCREENER] Pre-fetched {len(bvb_records)} dividende confirmate BVB.ro")

        results = []

        async with httpx.AsyncClient() as client:
            batch_size = 5
            for i in range(0, len(stocks), batch_size):
                batch = stocks[i:i+batch_size]
                tasks = [process_stock(client, stock, bvb_records=bvb_records) for stock in batch]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, dict):
                        results.append(result)

                if i + batch_size < len(stocks):
                    await asyncio.sleep(0.5)

        results.sort(key=lambda x: x.get("signal_score", 0), reverse=True)

        scanned_at = datetime.now(timezone.utc).isoformat()
        await db.screener_pro_cache.replace_one(
            {},
            {
                "stocks": results,
                "count": len(results),
                "scanned_at": scanned_at,
                "is_live": True,
                "from_cache": True
            },
            upsert=True
        )
        logger.info(f"[SCREENER] Background scan complete: {len(results)} stocks cached")
    except Exception as e:
        logger.error(f"[SCREENER] Error in background scan: {e}")
    finally:
        _scan_running = False


# ============================================
# ENDPOINTS
# ============================================

@router.get("/scan")
async def scan_all_stocks(background_tasks: BackgroundTasks, user: dict = Depends(require_auth)):
    """
    PRO Feature: Scanează toate acțiunile BVB cu indicatori tehnici și fundamentale.
    Date reale și confirmate — fără estimări:
    - Dividend Yield: STRICT din dividende confirmate BVB.ro
    - P/E: STRICT EPS > 0, fără ForwardPE
    - ROE: STRICT valoare raportată EODHD
    - D/E: din bilanț EODHD sau null
    Returnează din cache (< 45 min) pentru viteză.
    """
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(status_code=403, detail="Screener PRO necesită abonament PRO")

    # Returnează din cache dacă e proaspăt
    cache = await get_scan_cache(max_age_minutes=45)
    if cache:
        return cache

    # Cache gol sau vechi — declanșează background scan dacă nu rulează deja
    if not _scan_running:
        background_tasks.add_task(run_scan_and_cache)
        logger.info("[SCREENER] Triggered background scan for fresh data")

    # Returnează cache-ul mai vechi dacă există (chiar dacă e expirat)
    db = await get_database()
    old_cache = await db.screener_pro_cache.find_one({}, {"_id": 0})
    if old_cache:
        old_cache["from_cache"] = True
        old_cache["cache_refreshing"] = True
        return old_cache

    # Niciun cache disponibil
    return {
        "stocks": [],
        "count": 0,
        "scanned_at": None,
        "is_live": False,
        "from_cache": False,
        "cache_refreshing": True,
        "message": "Se scanează toate acțiunile BVB. Reîncarcă în 2-3 minute pentru rezultate."
    }


async def process_stock(client: httpx.AsyncClient, stock: Dict, bvb_records: Optional[list] = None) -> Dict:
    """
    Procesează o acțiune: technicals LIVE + fundamentale din cache zilnic sau EODHD.

    POLITICĂ DATE FINANCIARE:
    - Technicals (RSI, MACD etc.): LIVE de la EODHD (se schimbă intraday)
    - Fundamentale (P/E, ROE, EPS, D/E): din cache zilnic → dacă lipsește, EODHD live
    - Dividend Yield: STRICT din dividende confirmate BVB.ro → null dacă nu există
    - P/E: valid DOAR dacă EPS > 0 (raportat real, nu proiecție)
    - ROE: STRICT valoare raportată, fără estimări din profit_margin
    - Dacă valoarea lipsește → null (nu 0, nu estimare)
    """
    symbol = stock.get("symbol")
    price = stock.get("price", 0)

    # Dacă bvb_records nu e pasat (apel individual), le fetch acum
    if bvb_records is None:
        try:
            from scrapers.bvb_dividend_scraper import get_cached_dividends
            bvb_records, _ = await get_cached_dividends()
        except Exception:
            bvb_records = []

    # Încearcă cache-ul zilnic de fundamentale (P/E, ROE, EPS nu se schimbă intraday)
    fundamentals = await get_fundamentals_from_daily_cache(symbol)

    if fundamentals is None:
        # Cache miss: fetch technicals + fundamentals în paralel
        tech_task = fetch_stock_technicals(client, symbol)
        fund_task = fetch_fundamentals(client, symbol)
        technicals, fundamentals = await asyncio.gather(tech_task, fund_task)
    else:
        # Cache hit: fetch doar technicals (date în timp real)
        technicals = await fetch_stock_technicals(client, symbol)

    # === P/E: STRICT — EPS > 0, fără proiecții ===
    pe_ratio = None
    if fundamentals:
        pe_raw = fundamentals.get("pe_ratio")
        eps = fundamentals.get("eps")

        if eps is not None and eps <= 0:
            pe_ratio = None  # Companie cu pierderi sau zero profit → P/E invalid
        elif pe_raw and 0 < pe_raw < 2000:
            pe_ratio = pe_raw
        elif price and price > 0 and eps and eps > 0.01:
            # Calculat din EPS real raportat (nu EPSEstimate)
            calc = price / eps
            if 0 < calc < 2000:
                pe_ratio = calc
    # Dacă nu avem date suficiente → pe_ratio rămâne None (nu estimăm)

    # === ROE: STRICT — valoare raportată convertită în %, fără estimări ===
    # Nu estimăm ROE din profit_margin sau alte surse derivate
    roe_value = None
    if fundamentals:
        roe_raw = fundamentals.get("roe")
        if roe_raw is not None:
            # EODHD returnează ca decimal (0.14 = 14%). Dacă > 10, e deja în %
            roe_value = roe_raw * 100 if abs(roe_raw) < 10 else roe_raw

    # === Dividend Yield: STRICT — DOAR din dividende confirmate BVB.ro ===
    confirmed_yield = _get_confirmed_yield_from_bvb(symbol, price, bvb_records)

    # === Debt/Equity din fundamentale (null dacă lipsesc date) ===
    debt_equity = fundamentals.get("debt_equity") if fundamentals else None

    # Calculate signal (uses raw fundamentals for internal calculations)
    signal_data = calculate_signal(price, technicals, fundamentals or {})

    return {
        "symbol": symbol,
        "name": stock.get("name"),
        "sector": stock.get("sector"),
        "logo_url": fundamentals.get("logo_url") if fundamentals else None,
        "price": price,
        "change": stock.get("change"),
        "change_percent": stock.get("change_percent"),
        "volume": stock.get("volume"),
        # Technicals — LIVE de la EODHD
        "rsi": round(technicals.get("rsi"), 2) if technicals.get("rsi") else None,
        "macd": round(technicals.get("macd"), 4) if technicals.get("macd") else None,
        "macd_signal": round(technicals.get("macd_signal"), 4) if technicals.get("macd_signal") else None,
        "sma20": round(technicals.get("sma20"), 2) if technicals.get("sma20") else None,
        "sma50": round(technicals.get("sma50"), 2) if technicals.get("sma50") else None,
        "bb_upper": round(technicals.get("bb_upper"), 2) if technicals.get("bb_upper") else None,
        "bb_lower": round(technicals.get("bb_lower"), 2) if technicals.get("bb_lower") else None,
        # Fundamentale — cache zilnic sau EODHD live (fără estimări)
        "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
        "roe": round(roe_value, 2) if roe_value is not None else None,
        "eps": round(fundamentals.get("eps"), 2) if fundamentals and fundamentals.get("eps") is not None else None,
        "dividend_yield": confirmed_yield,      # STRICT: BVB.ro confirmat sau null
        "debt_equity": round(debt_equity, 2) if debt_equity is not None else None,
        "market_cap": fundamentals.get("market_cap") if fundamentals else None,
        "pb_ratio": round(fundamentals.get("pb_ratio"), 2) if fundamentals and fundamentals.get("pb_ratio") else None,
        "52_week_high": round(fundamentals.get("52_week_high"), 2) if fundamentals and fundamentals.get("52_week_high") else None,
        "52_week_low": round(fundamentals.get("52_week_low"), 2) if fundamentals and fundamentals.get("52_week_low") else None,
        "beta": round(fundamentals.get("beta"), 3) if fundamentals and fundamentals.get("beta") else None,
        "200_day_ma": round(fundamentals.get("200_day_ma"), 2) if fundamentals and fundamentals.get("200_day_ma") else None,
        # Signal
        "signal": signal_data["signal"],
        "signal_text": signal_data["signal_text"],
        "signal_color": signal_data["signal_color"],
        "signal_score": signal_data["score"],
        "signal_reasons": signal_data["signals"],
        "warnings": signal_data["warnings"],
        # Indicatori sursă date
        "yield_source": "BVB.ro (confirmat)" if confirmed_yield is not None else "N/A",
    }


@router.post("/filter")
async def filter_stocks(request: ProScreenerRequest, user: dict = Depends(require_auth)):
    """
    PRO Feature: Filtrează acțiunile după criterii avansate.
    Toate filtrele de fundamentale exclud acțiunile cu date lipsă (null).
    """
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(status_code=403, detail="Screener PRO necesită abonament PRO")

    # Citește direct din cache (evită bug-ul de circular dependency cu BackgroundTasks)
    db = await get_database()
    cache = await db.screener_pro_cache.find_one({}, {"_id": 0})
    stocks = (cache or {}).get("stocks", [])

    # Aplică filtrele
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

        # Fundamental filters — exclude acțiunile cu date lipsă (null)
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
        if request.max_debt_equity and (stock.get("debt_equity") is None or stock.get("debt_equity") > request.max_debt_equity):
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
        # bvb_records=None → process_stock le va fetch intern
        result = await process_stock(client, stock, bvb_records=None)

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

    db = await get_database()
    cache = await db.screener_pro_cache.find_one({}, {"_id": 0})
    stocks = (cache or {}).get("stocks", [])

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
                "stocks": stocks_list[:5]
            }
            for signal, stocks_list in summary.items()
        },
        "total": len(stocks),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/refresh-fundamentals")
async def trigger_fundamentals_refresh(background_tasks: BackgroundTasks, user: dict = Depends(require_auth)):
    """
    PRO Feature: Declanșează refresh manual al cache-ului zilnic de fundamentale.
    Cache-ul este actualizat automat zilnic la 8:00 AM.
    Conține: P/E, ROE, EPS, Debt/Equity (date reale EODHD, fără estimări).
    """
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(status_code=403, detail="Funcție PRO")

    background_tasks.add_task(refresh_fundamentals_daily_cache)
    return {
        "message": "Cache fundamentale se actualizează în fundal (P/E, ROE, EPS, D/E din EODHD).",
        "status": "running",
        "note": "Datele vor fi disponibile în 2-3 minute."
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
                "description": "Dividend Yield > 5% (BVB.ro confirmat) + P/E < 12",
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
