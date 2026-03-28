"""
AI Advisor PRO - Conectat la piață cu EODHD
Analiză inteligentă fără recomandări directe de cumpărare/vânzare
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import logging
import httpx
from config.database import get_database
from routes.auth import require_auth
from utils.llm import LlmChat, UserMessage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-advisor", tags=["ai-advisor"])

# EODHD API Config
EODHD_API_KEY = os.environ.get("EODHD_API_KEY")
EODHD_BASE_URL = "https://eodhd.com/api"

# Experience Level Contexts
LEVEL_CONTEXTS = {
    "beginner": {
        "name": "Începător",
        "allowed_topics": ["dividende", "indice BET", "termeni de bază", "cum funcționează bursa", "acțiuni blue chip"],
        "stock_filter": ["TLV", "H2O", "SNP", "FP", "BRD", "SNG", "SNN", "TGN", "EL", "ONE"],  # BET stocks
        "indicators": ["price", "volume", "dividend_yield"],
        "system_prompt": """Ești un consilier financiar prietenos și răbdător pentru investitori ÎNCEPĂTORI în România.

REGULI STRICTE:
1. Explică TOTUL în termeni simpli, fără jargon tehnic
2. Concentrează-te DOAR pe acțiunile din indicele BET (cele mai sigure pentru începători)
3. Focus principal pe DIVIDENDE și investiții pe termen lung
4. NU da NICIODATĂ sfaturi de "cumpără acum" sau "vinde acum"
5. Încurajează educația și răbdarea
6. Menționează ÎNTOTDEAUNA riscurile
7. Răspunde în limba română

CÂND PRIMEȘTI DATE DE PIAȚĂ:
- Explică ce înseamnă fiecare indicator în termeni simpli
- Compară cu concepte din viața de zi cu zi
- Pune accent pe randamentul dividendelor

LIMITĂRI:
- NU discuta indicatori tehnici avansați (RSI, MACD, etc.)
- NU discuta leverage sau short selling
- NU discuta alte piețe în afară de BVB"""
    },
    "intermediate": {
        "name": "Mediu",
        "allowed_topics": ["indicatori tehnici", "RSI", "MA", "MACD", "analiză tehnică", "diversificare", "toate acțiunile BVB"],
        "stock_filter": "ALL_BVB",
        "indicators": ["price", "volume", "rsi", "ma", "macd", "dividend_yield", "pe_ratio"],
        "system_prompt": """Ești un analist tehnic profesionist pentru investitori cu experiență MEDIE în România.

REGULI STRICTE:
1. Poți discuta indicatori tehnici: RSI, Medii Mobile, MACD, volume, suport/rezistență
2. Accesezi TOATE acțiunile BVB, nu doar BET
3. Poți analiza grafice și tendințe
4. NU da sfaturi directe de "cumpără" sau "vinde" - în schimb, prezintă scenarii
5. Menționează ÎNTOTDEAUNA că analiza tehnică nu garantează rezultate
6. Răspunde în limba română

CÂND ANALIZEZI DATE DE PIAȚĂ:
- Identifică niveluri de suport și rezistență
- Interpretează RSI (supravândut <30, supracumpărat >70)
- Analizează tendințele mediilor mobile
- Corelează volumul cu mișcările de preț

STIL DE COMUNICARE:
- Profesional dar accesibil
- Prezintă multiple perspective
- Încurajează gândirea critică"""
    },
    "advanced": {
        "name": "Expert",
        "allowed_topics": ["analiză fundamentală", "bilanțuri", "cash flow", "P/E", "P/B", "ROE", "toate piețele", "strategie fiscală"],
        "stock_filter": "ALL",
        "indicators": ["all"],
        "system_prompt": """Ești un analist financiar EXPERT pentru investitori avansați în România.

CAPABILITĂȚI COMPLETE:
1. Analiză fundamentală aprofundată (P/E, P/B, ROE, Debt/Equity, Free Cash Flow)
2. Analiză tehnică completă cu toate indicatorii
3. Acces la toate piețele (BVB, internațional)
4. Poți sugera linii de trend și niveluri cheie pe grafice
5. Discuții despre optimizare fiscală (PF vs SRL)

REGULI:
1. NU da sfaturi directe de "cumpără" sau "vinde" - prezintă analize obiective
2. Menționează ÎNTOTDEAUNA riscurile și incertitudinile
3. Răspunde în limba română
4. Fii precis și bazat pe date

CÂND ANALIZEZI:
- Prezintă date concrete din bilanț și rezultate financiare
- Calculează și interpretează multiplii de evaluare
- Compară cu industria și competitorii
- Identifică catalizatori și riscuri
- Sugerează niveluri tehnice importante pentru grafice

OUTPUT PENTRU GRAFICE (când e relevant):
Când utilizatorul cere analiză grafică, include un bloc JSON cu liniile sugerate:
```json
{
  "chart_lines": [
    {"type": "support", "price": 25.50, "label": "Suport Major"},
    {"type": "resistance", "price": 28.00, "label": "Rezistență"},
    {"type": "trendline", "points": [[date1, price1], [date2, price2]], "label": "Trend Ascendent"}
  ]
}
```"""
    }
}


class AIQuery(BaseModel):
    message: str
    symbol: Optional[str] = None
    market_type: Optional[str] = "bvb"
    include_market_data: bool = True
    session_id: Optional[str] = None


class ChartAnalysisRequest(BaseModel):
    symbol: str
    market_type: str = "bvb"
    period: str = "3m"


# ============================================
# HELPER FUNCTIONS - DATA FETCHING
# ============================================

async def fetch_stock_fundamentals(symbol: str) -> Dict:
    """Fetch COMPLETE fundamental data from EODHD - All-in-One plan ($100/month)"""
    if not EODHD_API_KEY:
        return {}
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{EODHD_BASE_URL}/fundamentals/{symbol}.RO"
            params = {"api_token": EODHD_API_KEY, "fmt": "json"}
            response = await client.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract ALL key metrics from EODHD
                general = data.get("General", {})
                highlights = data.get("Highlights", {})
                valuation = data.get("Valuation", {})
                shares_stats = data.get("SharesStats", {})
                financials = data.get("Financials", {})
                earnings = data.get("Earnings", {})
                
                # Get latest balance sheet data
                balance_sheet = {}
                if financials.get("Balance_Sheet", {}).get("quarterly"):
                    latest_quarter = list(financials["Balance_Sheet"]["quarterly"].keys())[0] if financials["Balance_Sheet"]["quarterly"] else None
                    if latest_quarter:
                        balance_sheet = financials["Balance_Sheet"]["quarterly"][latest_quarter]
                
                # Get latest income statement
                income_stmt = {}
                if financials.get("Income_Statement", {}).get("quarterly"):
                    latest_quarter = list(financials["Income_Statement"]["quarterly"].keys())[0] if financials["Income_Statement"]["quarterly"] else None
                    if latest_quarter:
                        income_stmt = financials["Income_Statement"]["quarterly"][latest_quarter]
                
                return {
                    # General Info
                    "name": general.get("Name", symbol),
                    "sector": general.get("Sector", "N/A"),
                    "industry": general.get("Industry", "N/A"),
                    "description": general.get("Description", "")[:500],  # First 500 chars
                    "employees": general.get("FullTimeEmployees"),
                    "ipo_date": general.get("IPODate"),
                    
                    # Valuation Metrics
                    "market_cap": highlights.get("MarketCapitalization"),
                    "pe_ratio": highlights.get("PERatio"),
                    "peg_ratio": highlights.get("PEGRatio"),
                    "pb_ratio": valuation.get("PriceBookMRQ"),
                    "ps_ratio": valuation.get("PriceSalesTTM"),
                    "enterprise_value": valuation.get("EnterpriseValue"),
                    "ev_to_revenue": valuation.get("EnterpriseValueRevenue"),
                    "ev_to_ebitda": valuation.get("EnterpriseValueEbitda"),
                    
                    # Profitability Metrics
                    "eps": highlights.get("EarningsShare"),
                    "eps_growth_yoy": highlights.get("EPSEstimateCurrentYear"),
                    "roe": highlights.get("ReturnOnEquityTTM"),
                    "roa": highlights.get("ReturnOnAssetsTTM"),
                    "profit_margin": highlights.get("ProfitMargin"),
                    "operating_margin": highlights.get("OperatingMarginTTM"),
                    "gross_margin": highlights.get("GrossProfitTTM"),
                    
                    # Dividend Info
                    "dividend_yield": highlights.get("DividendYield"),
                    "dividend_share": highlights.get("DividendShare"),
                    "payout_ratio": highlights.get("PayoutRatio"),
                    "ex_dividend_date": highlights.get("ExDividendDate"),
                    
                    # Financial Health
                    "current_ratio": highlights.get("CurrentRatio"),
                    "debt_to_equity": highlights.get("DebtEquity"),
                    "total_debt": balance_sheet.get("totalDebt"),
                    "total_cash": balance_sheet.get("cash"),
                    "book_value": highlights.get("BookValue"),
                    
                    # Growth & Revenue
                    "revenue": highlights.get("RevenueTTM"),
                    "revenue_per_share": highlights.get("RevenuePerShareTTM"),
                    "quarterly_revenue_growth": highlights.get("QuarterlyRevenueGrowthYOY"),
                    "quarterly_earnings_growth": highlights.get("QuarterlyEarningsGrowthYOY"),
                    
                    # Shares Info
                    "shares_outstanding": shares_stats.get("SharesOutstanding"),
                    "float_shares": shares_stats.get("SharesFloat"),
                    "percent_insiders": shares_stats.get("PercentInsiders"),
                    "percent_institutions": shares_stats.get("PercentInstitutions"),
                    
                    # Price Levels
                    "52_week_high": highlights.get("52WeekHigh"),
                    "52_week_low": highlights.get("52WeekLow"),
                    "50_day_ma": highlights.get("50DayMA"),
                    "200_day_ma": highlights.get("200DayMA"),
                    "beta": highlights.get("Beta"),
                    
                    # Analyst Ratings (if available)
                    "target_price": highlights.get("WallStreetTargetPrice"),
                    
                    # Latest Earnings
                    "last_earnings_date": earnings.get("History", {}).get(list(earnings.get("History", {}).keys())[0] if earnings.get("History") else None, {}).get("reportDate"),
                }
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {symbol}: {e}")
    return {}


async def fetch_technical_indicators(symbol: str) -> Dict:
    """Fetch ALL technical indicators from EODHD - Complete analysis"""
    if not EODHD_API_KEY:
        return {}
    
    indicators = {}
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{EODHD_BASE_URL}/technical/{symbol}.RO"
            
            # Fetch RSI
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "rsi", "period": 14}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["rsi"] = data[-1].get("rsi") if data else None
            
            # Fetch SMA 20 (short term)
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "sma", "period": 20}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["sma_20"] = data[-1].get("sma") if data else None
            
            # Fetch SMA 50
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "sma", "period": 50}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["sma_50"] = data[-1].get("sma") if data else None
            
            # Fetch SMA 200
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "sma", "period": 200}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["sma_200"] = data[-1].get("sma") if data else None
            
            # Fetch EMA 12 and EMA 26 (for MACD confirmation)
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "ema", "period": 12}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["ema_12"] = data[-1].get("ema") if data else None
            
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "ema", "period": 26}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["ema_26"] = data[-1].get("ema") if data else None
            
            # Fetch MACD
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "macd"}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    latest = data[-1] if data else {}
                    indicators["macd"] = latest.get("macd")
                    indicators["macd_signal"] = latest.get("macd_signal")
                    indicators["macd_histogram"] = latest.get("macd_hist")
            
            # Fetch Bollinger Bands
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "bbands", "period": 20}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    latest = data[-1] if data else {}
                    indicators["bb_upper"] = latest.get("uband")
                    indicators["bb_middle"] = latest.get("mband")
                    indicators["bb_lower"] = latest.get("lband")
            
            # Fetch Stochastic Oscillator
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "stoch"}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    latest = data[-1] if data else {}
                    indicators["stoch_k"] = latest.get("slow_k")
                    indicators["stoch_d"] = latest.get("slow_d")
            
            # Fetch ADX (Average Directional Index) - trend strength
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "adx", "period": 14}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["adx"] = data[-1].get("adx") if data else None
            
            # Fetch ATR (Average True Range) - volatility
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "atr", "period": 14}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["atr"] = data[-1].get("atr") if data else None
                    
    except Exception as e:
        logger.error(f"Error fetching technical indicators for {symbol}: {e}")
    
    return indicators


async def fetch_current_price(symbol: str) -> Dict:
    """Fetch current price and basic info"""
    if not EODHD_API_KEY:
        return {}
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{EODHD_BASE_URL}/real-time/{symbol}.RO"
            params = {"api_token": EODHD_API_KEY, "fmt": "json"}
            response = await client.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "price": data.get("close"),
                    "open": data.get("open"),
                    "high": data.get("high"),
                    "low": data.get("low"),
                    "volume": data.get("volume"),
                    "change": data.get("change"),
                    "change_percent": data.get("change_p"),
                    "previous_close": data.get("previousClose")
                }
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
    return {}


async def fetch_historical_for_analysis(symbol: str, days: int = 90) -> List[Dict]:
    """Fetch historical data for chart analysis"""
    if not EODHD_API_KEY:
        return []
    
    try:
        async with httpx.AsyncClient() as client:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            url = f"{EODHD_BASE_URL}/eod/{symbol}.RO"
            params = {
                "api_token": EODHD_API_KEY,
                "fmt": "json",
                "from": start_date.strftime("%Y-%m-%d"),
                "to": end_date.strftime("%Y-%m-%d")
            }
            response = await client.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
    return []


def identify_support_resistance(historical_data: List[Dict]) -> Dict:
    """Identify support and resistance levels from historical data"""
    if not historical_data or len(historical_data) < 20:
        return {"supports": [], "resistances": []}
    
    closes = [d["close"] for d in historical_data]
    highs = [d["high"] for d in historical_data]
    lows = [d["low"] for d in historical_data]
    
    # Simple pivot point analysis
    current_price = closes[-1]
    recent_high = max(highs[-20:])
    recent_low = min(lows[-20:])
    
    # Identify potential levels
    supports = []
    resistances = []
    
    # Recent low as support
    supports.append({
        "price": round(recent_low, 2),
        "strength": "strong",
        "label": "Suport recent (minim 20 zile)"
    })
    
    # 52-week low if available
    if len(lows) >= 250:
        year_low = min(lows)
        if year_low < recent_low * 0.95:
            supports.append({
                "price": round(year_low, 2),
                "strength": "major",
                "label": "Suport anual"
            })
    
    # Recent high as resistance
    resistances.append({
        "price": round(recent_high, 2),
        "strength": "strong",
        "label": "Rezistență recentă (maxim 20 zile)"
    })
    
    # 52-week high
    if len(highs) >= 250:
        year_high = max(highs)
        if year_high > recent_high * 1.05:
            resistances.append({
                "price": round(year_high, 2),
                "strength": "major",
                "label": "Rezistență anuală"
            })
    
    return {
        "supports": supports,
        "resistances": resistances,
        "current_price": round(current_price, 2)
    }


# ============================================
# MAIN AI ENDPOINTS
# ============================================

@router.post("/chat")
async def ai_chat(query: AIQuery, user: dict = Depends(require_auth)):
    """
    Main AI chat endpoint with market data integration
    """
    db = await get_database()
    
    # Get user subscription and level
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not user_data:
        # Initialize user
        user_data = {
            "user_id": user["user_id"],
            "subscription_level": "free",
            "experience_level": "beginner",
            "ai_queries_today": 0,
            "ai_queries_reset_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": user_data},
            upsert=True
        )
    
    subscription_level = user_data.get("subscription_level", "free")
    experience_level = user_data.get("experience_level", "beginner")
    
    # Check AI query limits
    if subscription_level == "free":
        ai_used = user_data.get("ai_queries_today", 0)
        
        # Check reset
        reset_at = user_data.get("ai_queries_reset_at")
        if reset_at:
            reset_time = datetime.fromisoformat(reset_at.replace("Z", "+00:00")) if isinstance(reset_at, str) else reset_at
            if datetime.now(timezone.utc) - reset_time > timedelta(hours=24):
                ai_used = 0
                await db.users.update_one(
                    {"user_id": user["user_id"]},
                    {"$set": {
                        "ai_queries_today": 0,
                        "ai_queries_reset_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
        
        if ai_used >= 5:
            return {
                "success": False,
                "error": "limit_reached",
                "message": "Ai atins limita de 5 întrebări gratuite pe zi.",
                "upgrade_prompt": {
                    "title": "Deblochează întrebări nelimitate",
                    "description": "Treci la PRO pentru acces nelimitat la AI Advisor și funcții avansate.",
                    "price": "49 RON/lună",
                    "cta": "Activează PRO"
                },
                "queries_used": ai_used,
                "queries_limit": 5
            }
    
    # Get level context
    level_config = LEVEL_CONTEXTS.get(experience_level, LEVEL_CONTEXTS["beginner"])
    
    # Build market context if symbol provided
    market_context = ""
    chart_lines = None
    
    if query.symbol and query.include_market_data:
        symbol = query.symbol.upper()
        
        # Check if symbol is allowed for this level
        if experience_level == "beginner":
            if symbol not in level_config["stock_filter"]:
                return {
                    "success": False,
                    "error": "symbol_not_allowed",
                    "message": f"La nivelul Începător poți analiza doar acțiunile din indicele BET. {symbol} nu este în BET.",
                    "allowed_symbols": level_config["stock_filter"],
                    "upgrade_hint": "Treci la nivelul Mediu pentru a accesa toate acțiunile BVB."
                }
        
        # Fetch market data based on level
        price_data = await fetch_current_price(symbol)
        
        if price_data:
            market_context += f"\n\n📊 DATE CURENTE pentru {symbol}:\n"
            market_context += f"- Preț: {price_data.get('price', 'N/A')} RON\n"
            market_context += f"- Variație: {price_data.get('change_percent', 'N/A')}%\n"
            market_context += f"- Volum: {price_data.get('volume', 'N/A'):,}\n"
        
        # Technical indicators for intermediate+
        if experience_level in ["intermediate", "advanced"]:
            tech_data = await fetch_technical_indicators(symbol)
            if tech_data:
                market_context += f"\n📈 INDICATORI TEHNICI COMPLETI:\n"
                
                # Trend Indicators
                market_context += f"[TREND]\n"
                if tech_data.get("rsi"):
                    rsi = tech_data["rsi"]
                    rsi_status = "SUPRAVÂNDUT ⬆️" if rsi < 30 else "SUPRACUMPĂRAT ⬇️" if rsi > 70 else "NEUTRU ➡️"
                    market_context += f"- RSI(14): {rsi:.1f} ({rsi_status})\n"
                
                if tech_data.get("adx"):
                    adx = tech_data["adx"]
                    trend_strength = "FĂRĂ TREND" if adx < 20 else "TREND SLAB" if adx < 25 else "TREND PUTERNIC" if adx < 50 else "TREND FOARTE PUTERNIC"
                    market_context += f"- ADX(14): {adx:.1f} ({trend_strength})\n"
                
                # Moving Averages
                market_context += f"[MEDII MOBILE]\n"
                if tech_data.get("sma_20"):
                    market_context += f"- SMA 20: {tech_data['sma_20']:.2f}\n"
                if tech_data.get("sma_50"):
                    market_context += f"- SMA 50: {tech_data['sma_50']:.2f}\n"
                if tech_data.get("sma_200"):
                    market_context += f"- SMA 200: {tech_data['sma_200']:.2f}\n"
                if tech_data.get("ema_12"):
                    market_context += f"- EMA 12: {tech_data['ema_12']:.2f}\n"
                if tech_data.get("ema_26"):
                    market_context += f"- EMA 26: {tech_data['ema_26']:.2f}\n"
                
                # MACD
                market_context += f"[MACD]\n"
                if tech_data.get("macd") is not None:
                    macd_val = tech_data.get("macd", 0) or 0
                    macd_sig = tech_data.get("macd_signal", 0) or 0
                    macd_signal = "BULLISH ⬆️" if macd_val > macd_sig else "BEARISH ⬇️"
                    market_context += f"- MACD: {macd_val:.4f}\n"
                    market_context += f"- Signal: {macd_sig:.4f}\n"
                    hist_val = tech_data.get('macd_histogram', 0) or 0
                    market_context += f"- Histogram: {hist_val:.4f} ({macd_signal})\n"
                
                # Bollinger Bands
                if tech_data.get("bb_upper"):
                    market_context += f"[BOLLINGER BANDS]\n"
                    market_context += f"- Upper: {tech_data['bb_upper']:.2f}\n"
                    market_context += f"- Middle: {tech_data.get('bb_middle', 0):.2f}\n"
                    market_context += f"- Lower: {tech_data.get('bb_lower', 0):.2f}\n"
                
                # Stochastic
                if tech_data.get("stoch_k"):
                    stoch_status = "SUPRAVÂNDUT" if tech_data["stoch_k"] < 20 else "SUPRACUMPĂRAT" if tech_data["stoch_k"] > 80 else "NEUTRU"
                    market_context += f"[STOCHASTIC]\n"
                    market_context += f"- %K: {tech_data['stoch_k']:.1f}\n"
                    market_context += f"- %D: {tech_data.get('stoch_d', 0):.1f} ({stoch_status})\n"
                
                # Volatility
                if tech_data.get("atr"):
                    market_context += f"[VOLATILITATE]\n"
                    market_context += f"- ATR(14): {tech_data['atr']:.4f}\n"
        
        # Fundamental data for advanced - NOW WITH COMPLETE DATA!
        if experience_level == "advanced":
            fund_data = await fetch_stock_fundamentals(symbol)
            if fund_data:
                market_context += f"\n📋 DATE FUNDAMENTALE COMPLETE:\n"
                
                # General Info
                market_context += f"- Companie: {fund_data.get('name', symbol)}\n"
                market_context += f"- Sector: {fund_data.get('sector', 'N/A')} | Industrie: {fund_data.get('industry', 'N/A')}\n"
                
                # Valuation
                market_context += f"\n💰 EVALUARE:\n"
                if fund_data.get("market_cap"):
                    mc = fund_data["market_cap"]
                    mc_str = f"{mc/1e9:.2f}B RON" if mc > 1e9 else f"{mc/1e6:.0f}M RON"
                    market_context += f"- Capitalizare: {mc_str}\n"
                if fund_data.get("pe_ratio"):
                    market_context += f"- P/E Ratio: {fund_data['pe_ratio']:.2f}\n"
                if fund_data.get("peg_ratio"):
                    market_context += f"- PEG Ratio: {fund_data['peg_ratio']:.2f}\n"
                if fund_data.get("pb_ratio"):
                    market_context += f"- P/B Ratio: {fund_data['pb_ratio']:.2f}\n"
                if fund_data.get("ps_ratio"):
                    market_context += f"- P/S Ratio: {fund_data['ps_ratio']:.2f}\n"
                if fund_data.get("ev_to_ebitda"):
                    market_context += f"- EV/EBITDA: {fund_data['ev_to_ebitda']:.2f}\n"
                
                # Profitability
                market_context += f"\n📈 PROFITABILITATE:\n"
                if fund_data.get("eps"):
                    market_context += f"- EPS: {fund_data['eps']:.2f} RON\n"
                if fund_data.get("roe"):
                    market_context += f"- ROE: {fund_data['roe']*100 if fund_data['roe'] < 1 else fund_data['roe']:.2f}%\n"
                if fund_data.get("roa"):
                    market_context += f"- ROA: {fund_data['roa']*100 if fund_data['roa'] < 1 else fund_data['roa']:.2f}%\n"
                if fund_data.get("profit_margin"):
                    market_context += f"- Marjă Profit: {fund_data['profit_margin']*100 if fund_data['profit_margin'] < 1 else fund_data['profit_margin']:.2f}%\n"
                if fund_data.get("operating_margin"):
                    market_context += f"- Marjă Operațională: {fund_data['operating_margin']*100 if fund_data['operating_margin'] < 1 else fund_data['operating_margin']:.2f}%\n"
                
                # Dividends
                if fund_data.get("dividend_yield"):
                    market_context += f"\n🎯 DIVIDENDE:\n"
                    market_context += f"- Randament Dividend: {fund_data['dividend_yield']*100 if fund_data['dividend_yield'] < 1 else fund_data['dividend_yield']:.2f}%\n"
                    if fund_data.get("dividend_share"):
                        market_context += f"- Dividend/Acțiune: {fund_data['dividend_share']:.2f} RON\n"
                    if fund_data.get("payout_ratio"):
                        market_context += f"- Payout Ratio: {fund_data['payout_ratio']:.0f}%\n"
                
                # Financial Health
                market_context += f"\n🏦 SĂNĂTATE FINANCIARĂ:\n"
                if fund_data.get("current_ratio"):
                    market_context += f"- Current Ratio: {fund_data['current_ratio']:.2f}\n"
                if fund_data.get("debt_to_equity"):
                    market_context += f"- Debt/Equity: {fund_data['debt_to_equity']:.2f}\n"
                if fund_data.get("book_value"):
                    market_context += f"- Book Value: {fund_data['book_value']:.2f} RON\n"
                
                # Growth
                market_context += f"\n📊 CREȘTERE:\n"
                if fund_data.get("quarterly_revenue_growth"):
                    market_context += f"- Creștere Venituri (YoY): {fund_data['quarterly_revenue_growth']*100:.1f}%\n"
                if fund_data.get("quarterly_earnings_growth"):
                    market_context += f"- Creștere Profit (YoY): {fund_data['quarterly_earnings_growth']*100:.1f}%\n"
                
                # Price Levels
                market_context += f"\n📍 NIVELURI PREȚ:\n"
                if fund_data.get("52_week_high"):
                    market_context += f"- Max 52 săpt: {fund_data['52_week_high']:.2f} RON\n"
                if fund_data.get("52_week_low"):
                    market_context += f"- Min 52 săpt: {fund_data['52_week_low']:.2f} RON\n"
                if fund_data.get("50_day_ma"):
                    market_context += f"- MA 50 zile: {fund_data['50_day_ma']:.2f} RON\n"
                if fund_data.get("200_day_ma"):
                    market_context += f"- MA 200 zile: {fund_data['200_day_ma']:.2f} RON\n"
                if fund_data.get("beta"):
                    market_context += f"- Beta: {fund_data['beta']:.2f}\n"
                
                # Ownership
                if fund_data.get("percent_insiders") or fund_data.get("percent_institutions"):
                    market_context += f"\n👥 STRUCTURĂ ACȚIONARIAT:\n"
                    if fund_data.get("percent_insiders"):
                        market_context += f"- Deținere Insideri: {fund_data['percent_insiders']:.1f}%\n"
                    if fund_data.get("percent_institutions"):
                        market_context += f"- Deținere Instituții: {fund_data['percent_institutions']:.1f}%\n"
            
            # Get chart analysis for advanced
            historical = await fetch_historical_for_analysis(symbol)
            if historical:
                levels = identify_support_resistance(historical)
                market_context += f"\n📐 NIVELURI TEHNICE CHEIE:\n"
                market_context += f"- Preț curent: {levels['current_price']} RON\n"
                for s in levels['supports']:
                    market_context += f"- Suport: {s['price']} RON ({s['label']})\n"
                for r in levels['resistances']:
                    market_context += f"- Rezistență: {r['price']} RON ({r['label']})\n"
                
                # Prepare chart lines for frontend
                chart_lines = {
                    "supports": levels['supports'],
                    "resistances": levels['resistances']
                }
    
    # Build the AI prompt
    full_message = query.message
    if market_context:
        full_message = f"{query.message}\n\n[CONTEXT DATE PIAȚĂ]{market_context}"
    
    # Call AI
    try:
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_UNIVERSAL_KEY") or os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        session_id = query.session_id or f"advisor_{user['user_id']}_{datetime.now().strftime('%Y%m%d')}"
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=level_config["system_prompt"]
        ).with_model("openai", "gpt-4o-mini")
        
        user_message = UserMessage(text=full_message)
        response = await chat.send_message(user_message)
        
        # Increment query counter for free users
        if subscription_level == "free":
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$inc": {"ai_queries_today": 1}}
            )
        
        # Log interaction
        await db.ai_interactions.insert_one({
            "user_id": user["user_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": experience_level,
            "symbol": query.symbol,
            "query": query.message[:500],
            "response_length": len(response)
        })
        
        # Get updated query count
        updated_user = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
        queries_used = updated_user.get("ai_queries_today", 0) if updated_user else 0
        
        return {
            "success": True,
            "response": response,
            "level": experience_level,
            "level_name": level_config["name"],
            "symbol_analyzed": query.symbol,
            "chart_lines": chart_lines,
            "queries_info": {
                "used": queries_used,
                "limit": 5 if subscription_level == "free" else -1,
                "remaining": 5 - queries_used if subscription_level == "free" else -1,
                "is_unlimited": subscription_level == "pro"
            },
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"AI chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-chart")
async def analyze_chart(request: ChartAnalysisRequest, user: dict = Depends(require_auth)):
    """
    Generate chart analysis with support/resistance lines
    Only available for advanced users
    """
    db = await get_database()
    
    # Check user level
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    experience_level = user_data.get("experience_level", "beginner") if user_data else "beginner"
    
    if experience_level != "advanced":
        return {
            "success": False,
            "error": "level_required",
            "message": "Analiza grafică cu linii automate este disponibilă doar pentru nivelul Expert.",
            "required_level": "advanced",
            "current_level": experience_level,
            "how_to_unlock": "Trece quiz-ul Expert (7/10) sau activează PRO"
        }
    
    symbol = request.symbol.upper()
    
    # Fetch data
    historical = await fetch_historical_for_analysis(symbol, days=180)
    if not historical:
        raise HTTPException(status_code=404, detail=f"Nu am găsit date pentru {symbol}")
    
    # Get technical data
    tech_data = await fetch_technical_indicators(symbol)
    fund_data = await fetch_stock_fundamentals(symbol)
    levels = identify_support_resistance(historical)
    
    # Generate AI analysis
    try:
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_UNIVERSAL_KEY") or os.environ.get("EMERGENT_LLM_KEY")
        
        analysis_prompt = f"""Analizează acțiunea {symbol} și oferă o analiză tehnică și fundamentală completă.

DATE DISPONIBILE:
- Preț curent: {levels['current_price']} RON
- RSI: {tech_data.get('rsi', 'N/A')}
- SMA 50: {tech_data.get('sma_50', 'N/A')}
- SMA 200: {tech_data.get('sma_200', 'N/A')}
- P/E: {fund_data.get('pe_ratio', 'N/A')}
- Dividend Yield: {fund_data.get('dividend_yield', 'N/A')}%
- Suporturi identificate: {[s['price'] for s in levels['supports']]}
- Rezistențe identificate: {[r['price'] for r in levels['resistances']]}

Oferă:
1. Interpretarea nivelurilor de suport/rezistență
2. Analiza indicatorilor tehnici
3. Scenarii posibile (bullish/bearish/neutru)
4. Puncte de atenție pentru investitor

NU oferi sfaturi directe de cumpărare/vânzare."""

        chat = LlmChat(
            api_key=api_key,
            session_id=f"chart_{user['user_id']}_{symbol}",
            system_message=LEVEL_CONTEXTS["advanced"]["system_prompt"]
        ).with_model("openai", "gpt-4o-mini")
        
        response = await chat.send_message(UserMessage(text=analysis_prompt))
        
        return {
            "success": True,
            "symbol": symbol,
            "analysis": response,
            "chart_data": {
                "current_price": levels['current_price'],
                "supports": levels['supports'],
                "resistances": levels['resistances'],
                "technical_indicators": tech_data,
                "fundamentals": fund_data
            },
            "lines_for_chart": [
                *[{"type": "support", "price": s["price"], "label": s["label"], "color": "#22c55e"} for s in levels['supports']],
                *[{"type": "resistance", "price": r["price"], "label": r["label"], "color": "#ef4444"} for r in levels['resistances']]
            ]
        }
        
    except Exception as e:
        logger.error(f"Chart analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context/{symbol}")
async def get_ai_context(symbol: str, user: dict = Depends(require_auth)):
    """
    Get market context for a symbol without using AI query
    Useful for displaying data before asking questions
    """
    db = await get_database()
    
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    experience_level = user_data.get("experience_level", "beginner") if user_data else "beginner"
    level_config = LEVEL_CONTEXTS.get(experience_level, LEVEL_CONTEXTS["beginner"])
    
    symbol = symbol.upper()
    
    # Check symbol access
    if experience_level == "beginner":
        if symbol not in level_config["stock_filter"]:
            return {
                "allowed": False,
                "message": f"Simbolul {symbol} nu este disponibil la nivelul Începător.",
                "allowed_symbols": level_config["stock_filter"]
            }
    
    # Fetch basic data
    context = {
        "symbol": symbol,
        "level": experience_level,
        "allowed": True
    }
    
    # Price data (all levels)
    price_data = await fetch_current_price(symbol)
    if price_data:
        context["price_data"] = price_data
    
    # Technical data (intermediate+)
    if experience_level in ["intermediate", "advanced"]:
        tech_data = await fetch_technical_indicators(symbol)
        if tech_data:
            context["technical"] = tech_data
    
    # Fundamental data (advanced only)
    if experience_level == "advanced":
        fund_data = await fetch_stock_fundamentals(symbol)
        if fund_data:
            context["fundamentals"] = fund_data
        
        # Chart levels
        historical = await fetch_historical_for_analysis(symbol)
        if historical:
            levels = identify_support_resistance(historical)
            context["chart_levels"] = levels
    
    return context
