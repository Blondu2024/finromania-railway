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
from emergentintegrations.llm.chat import LlmChat, UserMessage

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
    """Fetch fundamental data from EODHD"""
    if not EODHD_API_KEY:
        return {}
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{EODHD_BASE_URL}/fundamentals/{symbol}.RO"
            params = {"api_token": EODHD_API_KEY, "fmt": "json"}
            response = await client.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key metrics
                highlights = data.get("Highlights", {})
                valuation = data.get("Valuation", {})
                
                return {
                    "name": data.get("General", {}).get("Name", symbol),
                    "sector": data.get("General", {}).get("Sector", "N/A"),
                    "industry": data.get("General", {}).get("Industry", "N/A"),
                    "market_cap": highlights.get("MarketCapitalization"),
                    "pe_ratio": highlights.get("PERatio"),
                    "pb_ratio": valuation.get("PriceBookMRQ"),
                    "dividend_yield": highlights.get("DividendYield"),
                    "eps": highlights.get("EarningsShare"),
                    "roe": highlights.get("ReturnOnEquityTTM"),
                    "profit_margin": highlights.get("ProfitMargin"),
                    "52_week_high": highlights.get("52WeekHigh"),
                    "52_week_low": highlights.get("52WeekLow"),
                    "beta": highlights.get("Beta")
                }
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {symbol}: {e}")
    return {}


async def fetch_technical_indicators(symbol: str) -> Dict:
    """Fetch technical indicators from EODHD"""
    if not EODHD_API_KEY:
        return {}
    
    indicators = {}
    
    try:
        async with httpx.AsyncClient() as client:
            # RSI
            url = f"{EODHD_BASE_URL}/technical/{symbol}.RO"
            
            # Fetch RSI
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "rsi", "period": 14}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["rsi"] = data[-1].get("rsi") if data else None
            
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
                market_context += f"\n📈 INDICATORI TEHNICI:\n"
                if tech_data.get("rsi"):
                    rsi = tech_data["rsi"]
                    rsi_status = "SUPRAVÂNDUT" if rsi < 30 else "SUPRACUMPĂRAT" if rsi > 70 else "NEUTRU"
                    market_context += f"- RSI(14): {rsi:.1f} ({rsi_status})\n"
                if tech_data.get("sma_50"):
                    market_context += f"- SMA 50: {tech_data['sma_50']:.2f}\n"
                if tech_data.get("sma_200"):
                    market_context += f"- SMA 200: {tech_data['sma_200']:.2f}\n"
                if tech_data.get("macd"):
                    market_context += f"- MACD: {tech_data['macd']:.3f}\n"
        
        # Fundamental data for advanced
        if experience_level == "advanced":
            fund_data = await fetch_stock_fundamentals(symbol)
            if fund_data:
                market_context += f"\n📋 DATE FUNDAMENTALE:\n"
                market_context += f"- Sector: {fund_data.get('sector', 'N/A')}\n"
                if fund_data.get("pe_ratio"):
                    market_context += f"- P/E: {fund_data['pe_ratio']:.2f}\n"
                if fund_data.get("pb_ratio"):
                    market_context += f"- P/B: {fund_data['pb_ratio']:.2f}\n"
                if fund_data.get("dividend_yield"):
                    market_context += f"- Dividend Yield: {fund_data['dividend_yield']:.2f}%\n"
                if fund_data.get("roe"):
                    market_context += f"- ROE: {fund_data['roe']:.2f}%\n"
                if fund_data.get("profit_margin"):
                    market_context += f"- Profit Margin: {fund_data['profit_margin']:.2f}%\n"
            
            # Get chart analysis for advanced
            historical = await fetch_historical_for_analysis(symbol)
            if historical:
                levels = identify_support_resistance(historical)
                market_context += f"\n📐 NIVELURI TEHNICE:\n"
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
        api_key = os.environ.get("EMERGENT_UNIVERSAL_KEY") or os.environ.get("EMERGENT_LLM_KEY")
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
        api_key = os.environ.get("EMERGENT_UNIVERSAL_KEY") or os.environ.get("EMERGENT_LLM_KEY")
        
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
