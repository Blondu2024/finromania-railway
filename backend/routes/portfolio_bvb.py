"""
Portofoliu BVB cu sistem "3 Straturi" (3 Tiers)
ADAPTAT pentru FinRomania 2.0 Strategic Plan

Tierele:
- Începător: Acțiuni BET-index + tracking dividende
- Mediu: + Indicatori tehnici (RSI, MA) + diversificare AI
- Expert: + Analiză fundamentală completă (bilanț, cash flow)
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging
import os
import httpx
from config.database import get_database
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/portfolio-bvb", tags=["portfolio-bvb"])

EODHD_API_KEY = os.environ.get("EODHD_API_KEY")
EODHD_BASE_URL = "https://eodhd.com/api"

# BET Index Stocks (pentru nivel Începător)
BET_STOCKS = [
    "TLV",  # Banca Transilvania
    "H2O",  # Nuclearelectrica
    "SNP",  # OMV Petrom
    "FP",   # Fondul Proprietatea
    "BRD",  # BRD
    "SNG",  # Romgaz
    "SNN",  # Nuclearelectrica
    "TGN",  # Transgaz
    "EL",   # Electrica
    "ONE"   # One United
]

# Experience Levels Configuration
LEVEL_CONFIG = {
    "beginner": {
        "name": "Începător",
        "allowed_stocks": BET_STOCKS,
        "features": [
            "Doar acțiuni sigure din indicele BET",
            "Tracking dividende",
            "Preț și variație",
            "Randament dividend"
        ],
        "indicators": ["price", "volume", "dividend_yield"]
    },
    "intermediate": {
        "name": "Mediu",
        "allowed_stocks": "ALL_BVB",
        "features": [
            "Toate acțiunile BVB",
            "Indicatori tehnici (RSI, MA, MACD)",
            "Analiză diversificare AI",
            "Calendar dividende",
            "P/E Ratio"
        ],
        "indicators": ["price", "volume", "rsi", "ma", "macd", "dividend_yield", "pe_ratio"]
    },
    "advanced": {
        "name": "Expert",
        "allowed_stocks": "ALL_BVB",
        "features": [
            "Toate acțiunile BVB",
            "Analiză fundamentală completă",
            "Date bilanț (active, datorii)",
            "Cash Flow Analysis",
            "P/E, P/B, ROE, Debt/Equity",
            "AI trasează linii pe grafice"
        ],
        "indicators": ["all"]
    }
}


class PortfolioPosition(BaseModel):
    symbol: str
    shares: float
    avg_purchase_price: float
    current_price: float
    total_value: float
    profit_loss: float
    profit_loss_percent: float
    dividend_yield: Optional[float] = None
    technical_indicators: Optional[Dict] = None
    fundamentals: Optional[Dict] = None
    added_date: str


class AddPositionRequest(BaseModel):
    symbol: str
    shares: float = Field(gt=0)
    purchase_price: float = Field(gt=0)


class UpdatePositionRequest(BaseModel):
    shares: float = Field(gt=0)
    avg_purchase_price: float = Field(gt=0)


class PortfolioSummary(BaseModel):
    total_value: float
    total_invested: float
    total_profit_loss: float
    total_profit_loss_percent: float
    positions_count: int
    level: str
    level_name: str
    diversification_score: Optional[float] = None
    dividend_income_annual: Optional[float] = None


async def fetch_current_price(symbol: str) -> Dict:
    """Fetch current price from EODHD"""
    if not EODHD_API_KEY:
        return {"price": 0, "change_percent": 0}
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{EODHD_BASE_URL}/real-time/{symbol}.RO"
            params = {"api_token": EODHD_API_KEY, "fmt": "json"}
            response = await client.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "price": data.get("close", 0),
                    "change_percent": data.get("change_p", 0),
                    "volume": data.get("volume", 0)
                }
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
    return {"price": 0, "change_percent": 0}


async def fetch_technical_indicators(symbol: str) -> Dict:
    """Fetch RSI, MA for intermediate+ levels"""
    if not EODHD_API_KEY:
        return {}
    
    indicators = {}
    try:
        async with httpx.AsyncClient() as client:
            url = f"{EODHD_BASE_URL}/technical/{symbol}.RO"
            
            # RSI
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "rsi", "period": 14}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["rsi"] = data[-1].get("rsi")
            
            # SMA 50
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "sma", "period": 50}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["sma_50"] = data[-1].get("sma")
            
            # SMA 200
            params = {"api_token": EODHD_API_KEY, "fmt": "json", "function": "sma", "period": 200}
            response = await client.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    indicators["sma_200"] = data[-1].get("sma")
    except Exception as e:
        logger.error(f"Error fetching technical indicators for {symbol}: {e}")
    
    return indicators


async def fetch_fundamentals(symbol: str) -> Dict:
    """Fetch fundamental data for advanced level"""
    if not EODHD_API_KEY:
        return {}
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{EODHD_BASE_URL}/fundamentals/{symbol}.RO"
            params = {"api_token": EODHD_API_KEY, "fmt": "json"}
            response = await client.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                highlights = data.get("Highlights", {})
                valuation = data.get("Valuation", {})
                
                return {
                    "sector": data.get("General", {}).get("Sector"),
                    "market_cap": highlights.get("MarketCapitalization"),
                    "pe_ratio": highlights.get("PERatio"),
                    "pb_ratio": valuation.get("PriceBookMRQ"),
                    "dividend_yield": highlights.get("DividendYield"),
                    "roe": highlights.get("ReturnOnEquityTTM"),
                    "profit_margin": highlights.get("ProfitMargin"),
                    "debt_to_equity": valuation.get("DebtEquityMRQ")
                }
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {symbol}: {e}")
    return {}


def calculate_diversification_score(positions: List[Dict]) -> float:
    """Calculate diversification score (0-100)"""
    if len(positions) == 0:
        return 0
    
    # Simple diversification: more positions = better diversification
    # But diminishing returns after 8-10 positions
    score = min(100, (len(positions) / 10) * 100)
    
    # Check if all value is in one stock
    total_value = sum(p.get("total_value", 0) for p in positions)
    if total_value > 0:
        max_position_value = max(p.get("total_value", 0) for p in positions)
        concentration = (max_position_value / total_value) * 100
        
        # Penalize high concentration
        if concentration > 50:
            score *= 0.5
        elif concentration > 30:
            score *= 0.75
    
    return round(score, 1)


@router.get("/config")
async def get_portfolio_config(user: dict = Depends(require_auth)):
    """Get portfolio configuration based on user level"""
    db = await get_database()
    
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    level = user_data.get("experience_level", "beginner") if user_data else "beginner"
    
    config = LEVEL_CONFIG.get(level, LEVEL_CONFIG["beginner"])
    
    return {
        "level": level,
        "level_name": config["name"],
        "allowed_stocks": config["allowed_stocks"],
        "features": config["features"],
        "indicators": config["indicators"]
    }


@router.get("/")
async def get_portfolio(user: dict = Depends(require_auth)):
    """Get user's BVB portfolio"""
    db = await get_database()
    
    # Get user level
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    level = user_data.get("experience_level", "beginner") if user_data else "beginner"
    
    # Get portfolio
    portfolio_doc = await db.portfolio_bvb.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not portfolio_doc:
        return {
            "positions": [],
            "summary": PortfolioSummary(
                total_value=0,
                total_invested=0,
                total_profit_loss=0,
                total_profit_loss_percent=0,
                positions_count=0,
                level=level,
                level_name=LEVEL_CONFIG[level]["name"]
            )
        }
    
    positions = portfolio_doc.get("positions", [])
    level_config = LEVEL_CONFIG.get(level, LEVEL_CONFIG["beginner"])
    
    # Update current prices and add indicators based on level
    updated_positions = []
    total_value = 0
    total_invested = 0
    total_dividend_income = 0
    
    for pos in positions:
        symbol = pos["symbol"]
        
        # Fetch current price
        price_data = await fetch_current_price(symbol)
        current_price = price_data.get("price", pos.get("current_price", 0))
        
        total_val = pos["shares"] * current_price
        invested = pos["shares"] * pos["avg_purchase_price"]
        pl = total_val - invested
        pl_percent = (pl / invested * 100) if invested > 0 else 0
        
        position_data = {
            "symbol": symbol,
            "shares": pos["shares"],
            "avg_purchase_price": pos["avg_purchase_price"],
            "current_price": current_price,
            "total_value": total_val,
            "profit_loss": pl,
            "profit_loss_percent": pl_percent,
            "added_date": pos.get("added_date", "")
        }
        
        # Add indicators based on level
        if level in ["intermediate", "advanced"]:
            tech_data = await fetch_technical_indicators(symbol)
            position_data["technical_indicators"] = tech_data
        
        if level == "advanced":
            fund_data = await fetch_fundamentals(symbol)
            position_data["fundamentals"] = fund_data
            
            # Calculate annual dividend income
            if fund_data.get("dividend_yield"):
                annual_dividend = (fund_data["dividend_yield"] / 100) * total_val
                total_dividend_income += annual_dividend
                position_data["dividend_income_annual"] = annual_dividend
        
        # All levels get dividend yield
        fundamentals = await fetch_fundamentals(symbol)
        if fundamentals.get("dividend_yield"):
            position_data["dividend_yield"] = fundamentals["dividend_yield"]
        
        updated_positions.append(position_data)
        total_value += total_val
        total_invested += invested
    
    total_pl = total_value - total_invested
    total_pl_percent = (total_pl / total_invested * 100) if total_invested > 0 else 0
    
    # Calculate diversification for intermediate+
    diversification_score = None
    if level in ["intermediate", "advanced"]:
        diversification_score = calculate_diversification_score(updated_positions)
    
    summary = PortfolioSummary(
        total_value=total_value,
        total_invested=total_invested,
        total_profit_loss=total_pl,
        total_profit_loss_percent=total_pl_percent,
        positions_count=len(updated_positions),
        level=level,
        level_name=level_config["name"],
        diversification_score=diversification_score,
        dividend_income_annual=total_dividend_income if level == "advanced" else None
    )
    
    return {
        "positions": updated_positions,
        "summary": summary,
        "level_info": {
            "level": level,
            "name": level_config["name"],
            "features": level_config["features"]
        }
    }


@router.post("/position")
async def add_position(data: AddPositionRequest, user: dict = Depends(require_auth)):
    """Add a new position to portfolio"""
    db = await get_database()
    
    # Get user level
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    level = user_data.get("experience_level", "beginner") if user_data else "beginner"
    level_config = LEVEL_CONFIG.get(level, LEVEL_CONFIG["beginner"])
    
    # Check if symbol is allowed for this level
    if isinstance(level_config["allowed_stocks"], list):
        if data.symbol.upper() not in level_config["allowed_stocks"]:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "symbol_not_allowed",
                    "message": f"La nivelul {level_config['name']}, poți adăuga doar acțiuni din indicele BET.",
                    "allowed_stocks": level_config["allowed_stocks"],
                    "upgrade_hint": "Treci la nivelul Mediu pentru a accesa toate acțiunile BVB."
                }
            )
    
    # Fetch current price to validate
    price_data = await fetch_current_price(data.symbol.upper())
    if price_data.get("price", 0) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Acțiunea {data.symbol} nu a fost găsită."
        )
    
    # Add position
    position = {
        "symbol": data.symbol.upper(),
        "shares": data.shares,
        "avg_purchase_price": data.purchase_price,
        "current_price": price_data["price"],
        "added_date": datetime.now(timezone.utc).isoformat()
    }
    
    await db.portfolio_bvb.update_one(
        {"user_id": user["user_id"]},
        {
            "$push": {"positions": position},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        },
        upsert=True
    )
    
    return {
        "success": True,
        "message": f"Poziție adăugată: {data.shares} acțiuni {data.symbol} @ {data.purchase_price} RON",
        "position": position
    }


@router.delete("/position/{symbol}")
async def remove_position(symbol: str, user: dict = Depends(require_auth)):
    """Remove a position from portfolio"""
    db = await get_database()
    
    result = await db.portfolio_bvb.update_one(
        {"user_id": user["user_id"]},
        {
            "$pull": {"positions": {"symbol": symbol.upper()}},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Poziție nu a fost găsită")
    
    return {
        "success": True,
        "message": f"Poziție {symbol} ștearsă cu succes"
    }


@router.post("/ai-analysis")
async def get_ai_portfolio_analysis(user: dict = Depends(require_auth)):
    """Get AI analysis of portfolio diversification (intermediate+ only)"""
    db = await get_database()
    
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    level = user_data.get("experience_level", "beginner") if user_data else "beginner"
    
    if level == "beginner":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "feature_locked",
                "message": "Analiza AI a portofoliului este disponibilă de la nivelul Mediu.",
                "required_level": "intermediate"
            }
        )
    
    # Get portfolio
    portfolio_doc = await db.portfolio_bvb.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not portfolio_doc or not portfolio_doc.get("positions"):
        return {
            "analysis": "Nu ai încă poziții în portofoliu. Adaugă câteva acțiuni pentru a primi o analiză AI."
        }
    
    positions = portfolio_doc["positions"]
    
    # Build AI prompt
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    api_key = os.environ.get("EMERGENT_UNIVERSAL_KEY") or os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="AI service not configured")
    
    prompt = f"""Analizează următorul portofoliu BVB și oferă recomandări de diversificare:

Poziții:
{chr(10).join([f"- {p['symbol']}: {p['shares']} acțiuni @ {p['avg_purchase_price']} RON" for p in positions])}

Oferă:
1. Evaluarea diversificării (bună/medie/slabă)
2. Riscurile identificate
3. Sugestii de îmbunătățire (sectoare lipsă, concentrare prea mare)
4. Acțiuni BVB pe care ar trebui să le considere pentru diversificare

Răspunde în română, concis."""
    
    chat = LlmChat(
        api_key=api_key,
        session_id=f"portfolio_{user['user_id']}",
        system_message="Ești un consultant financiar expert pentru piața BVB."
    ).with_model("openai", "gpt-4o-mini")
    
    response = await chat.send_message(UserMessage(text=prompt))
    
    return {
        "analysis": response,
        "diversification_score": calculate_diversification_score(positions)
    }
