"""Smart News Analysis - AI-powered asset recommendation"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import yfinance as yf
from datetime import datetime, timedelta, timezone
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/smart-analysis", tags=["Smart Analysis"])

# Asset categories for AI to choose from
ASSET_CATEGORIES = {
    "indices": {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "NASDAQ": "^IXIC",
        "DAX": "^GDAXI",
        "FTSE 100": "^FTSE",
        "Nikkei 225": "^N225",
        "Euro Stoxx 50": "^STOXX50E",
        "VIX (Volatility)": "^VIX",
    },
    "commodities": {
        "Aur (Gold)": "GC=F",
        "Argint (Silver)": "SI=F",
        "Petrol Brent": "BZ=F",
        "Petrol WTI": "CL=F",
        "Gaze Naturale": "NG=F",
        "Cupru": "HG=F",
        "Platină": "PL=F",
        "Grâu": "ZW=F",
        "Porumb": "ZC=F",
    },
    "currencies": {
        "EUR/USD": "EURUSD=X",
        "EUR/RON": "EURRON=X",
        "USD/RON": "USDRON=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "USDJPY=X",
        "Bitcoin USD": "BTC-USD",
        "Ethereum USD": "ETH-USD",
    },
    "sectors_etf": {
        "Energie (XLE)": "XLE",
        "Financiar (XLF)": "XLF",
        "Tehnologie (XLK)": "XLK",
        "Sănătate (XLV)": "XLV",
        "Imobiliare (XLRE)": "XLRE",
        "Utilități (XLU)": "XLU",
        "Industrie (XLI)": "XLI",
        "Materiale (XLB)": "XLB",
    },
    "popular_stocks": {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Google": "GOOGL",
        "Amazon": "AMZN",
        "Tesla": "TSLA",
        "NVIDIA": "NVDA",
        "Meta": "META",
        "Netflix": "NFLX",
        "Berkshire Hathaway": "BRK-B",
        "JPMorgan": "JPM",
        "ExxonMobil": "XOM",
        "Chevron": "CVX",
    },
    "bonds_rates": {
        "US 10Y Treasury": "^TNX",
        "US 2Y Treasury": "^IRX",
        "US 30Y Treasury": "^TYX",
    }
}

# Keywords to asset mapping for quick detection
KEYWORD_ASSETS = {
    # Energy
    "petrol": ["CL=F", "BZ=F", "XOM", "CVX"],
    "oil": ["CL=F", "BZ=F", "XOM", "CVX"],
    "crude": ["CL=F", "BZ=F"],
    "gaze": ["NG=F"],
    "gas": ["NG=F"],
    "natural gas": ["NG=F"],
    "energie": ["XLE", "CL=F"],
    "energy": ["XLE", "CL=F"],
    "opec": ["CL=F", "BZ=F"],
    
    # Precious metals
    "aur": ["GC=F"],
    "gold": ["GC=F"],
    "argint": ["SI=F"],
    "silver": ["SI=F"],
    "platina": ["PL=F"],
    "platinum": ["PL=F"],
    "metale pretioase": ["GC=F", "SI=F"],
    
    # Currencies & Crypto
    "dolar": ["EURUSD=X", "^DXY"],
    "dollar": ["EURUSD=X", "^DXY"],
    "euro": ["EURUSD=X", "EURRON=X"],
    "leu": ["EURRON=X", "USDRON=X"],
    "ron": ["EURRON=X", "USDRON=X"],
    "bitcoin": ["BTC-USD"],
    "crypto": ["BTC-USD", "ETH-USD"],
    "ethereum": ["ETH-USD"],
    
    # Geopolitics
    "rusia": ["CL=F", "NG=F", "GC=F"],
    "russia": ["CL=F", "NG=F", "GC=F"],
    "ucraina": ["CL=F", "NG=F", "ZW=F"],
    "ukraine": ["CL=F", "NG=F", "ZW=F"],
    "china": ["^HSI", "FXI"],
    "taiwan": ["TSM", "^TWII"],
    "razboi": ["GC=F", "CL=F", "^VIX"],
    "war": ["GC=F", "CL=F", "^VIX"],
    
    # Central Banks & Economy
    "fed": ["^GSPC", "^TNX", "GC=F"],
    "federal reserve": ["^GSPC", "^TNX"],
    "bce": ["^STOXX50E", "EURUSD=X"],
    "ecb": ["^STOXX50E", "EURUSD=X"],
    "dobanda": ["^TNX", "^GSPC"],
    "dobânzi": ["^TNX", "^GSPC"],
    "interest rate": ["^TNX", "^GSPC"],
    "inflatie": ["GC=F", "^TNX", "TIP"],
    "inflation": ["GC=F", "^TNX", "TIP"],
    "recession": ["^VIX", "^GSPC", "GC=F"],
    "recesiune": ["^VIX", "^GSPC", "GC=F"],
    
    # Tech
    "apple": ["AAPL"],
    "microsoft": ["MSFT"],
    "google": ["GOOGL"],
    "amazon": ["AMZN"],
    "tesla": ["TSLA"],
    "nvidia": ["NVDA"],
    "ai": ["NVDA", "MSFT", "GOOGL"],
    "artificial intelligence": ["NVDA", "MSFT"],
    "semiconductor": ["NVDA", "AMD", "TSM"],
    "chips": ["NVDA", "AMD", "TSM", "INTC"],
    
    # Markets
    "wall street": ["^GSPC", "^DJI"],
    "bursa": ["^GSPC", "^STOXX50E"],
    "stock market": ["^GSPC", "^DJI"],
    "nasdaq": ["^IXIC"],
    "s&p": ["^GSPC"],
    "dow jones": ["^DJI"],
    
    # Agriculture
    "grau": ["ZW=F"],
    "wheat": ["ZW=F"],
    "porumb": ["ZC=F"],
    "corn": ["ZC=F"],
    "agricultura": ["DBA", "ZW=F"],
}


class NewsAnalysisRequest(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None


class AssetRecommendation(BaseModel):
    symbol: str
    name: str
    category: str
    relevance_reason: str


@router.post("/recommend-assets")
async def recommend_assets_for_news(request: NewsAnalysisRequest):
    """Analyze news and recommend relevant assets to display"""
    try:
        full_text = f"{request.title} {request.description or ''} {request.content or ''}".lower()
        
        # Find matching assets based on keywords
        matched_assets = []
        matched_keywords = []
        
        for keyword, symbols in KEYWORD_ASSETS.items():
            if keyword in full_text:
                matched_keywords.append(keyword)
                for symbol in symbols:
                    if symbol not in [a["symbol"] for a in matched_assets]:
                        # Find asset name
                        asset_name = symbol
                        category = "other"
                        for cat, assets in ASSET_CATEGORIES.items():
                            for name, sym in assets.items():
                                if sym == symbol:
                                    asset_name = name
                                    category = cat
                                    break
                        
                        matched_assets.append({
                            "symbol": symbol,
                            "name": asset_name,
                            "category": category,
                            "matched_keyword": keyword
                        })
        
        # Limit to top 3 most relevant
        matched_assets = matched_assets[:3]
        
        # If no matches, suggest general market indices
        if not matched_assets:
            matched_assets = [
                {"symbol": "^GSPC", "name": "S&P 500", "category": "indices", "matched_keyword": "general"},
                {"symbol": "GC=F", "name": "Aur (Gold)", "category": "commodities", "matched_keyword": "general"},
            ]
        
        return {
            "recommendations": matched_assets,
            "keywords_found": list(set(matched_keywords)),
            "analysis_text": f"Am identificat {len(matched_assets)} active relevante bazat pe {len(matched_keywords)} cuvinte cheie din știre."
        }
        
    except Exception as e:
        logger.error(f"Error recommending assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/asset/{symbol}")
async def get_asset_data(symbol: str, period: str = "1m"):
    """Get historical data for any asset from Yahoo Finance"""
    try:
        # Determine period for yfinance
        period_map = {
            "1d": "5d",      # Last 5 days for daily view
            "1w": "1mo",     # Last month for weekly view  
            "1m": "3mo",     # Last 3 months for monthly view
            "3m": "6mo",
            "6m": "1y",
            "1y": "2y",
            "5y": "max"
        }
        yf_period = period_map.get(period, "3mo")
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=yf_period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Get ticker info
        info = ticker.info
        
        # Format historical data
        history = []
        for date, row in hist.iterrows():
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })
        
        # Calculate change
        if len(history) >= 2:
            first_close = history[0]["close"]
            last_close = history[-1]["close"]
            change = last_close - first_close
            change_percent = (change / first_close * 100) if first_close > 0 else 0
        else:
            change = 0
            change_percent = 0
        
        return {
            "symbol": symbol,
            "name": info.get("shortName") or info.get("longName") or symbol,
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange", ""),
            "type": info.get("quoteType", ""),
            "current_price": history[-1]["close"] if history else 0,
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "history": history,
            "period": period,
            "data_points": len(history),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching asset {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-analysis")
async def generate_smart_analysis(request: NewsAnalysisRequest):
    """Generate AI analysis for a news article with asset context"""
    try:
        # First get recommended assets
        full_text = f"{request.title} {request.description or ''}"
        
        # Find matching keywords
        matched_keywords = []
        for keyword in KEYWORD_ASSETS.keys():
            if keyword in full_text.lower():
                matched_keywords.append(keyword)
        
        # Build prompt for AI
        prompt = f"""Analizează această știre financiară și oferă o perspectivă profesională (max 200 cuvinte).

ȘTIRE: "{request.title}"
{f'DESCRIERE: "{request.description}"' if request.description else ''}

CUVINTE CHEIE DETECTATE: {', '.join(matched_keywords) if matched_keywords else 'generale'}

Răspunde în română cu:

📊 **IMPACT PIAȚĂ**: Ce piețe/active sunt cel mai probabil afectate?

📈 **SCENARIUL OPTIMIST**: Ce s-ar putea întâmpla în cel mai bun caz?

📉 **SCENARIUL PESIMIST**: Ce riscuri există?

💡 **CONCLUZIE**: Ce ar trebui să urmărească un investitor?

⏱️ **ORIZONT**: Impact pe termen scurt vs lung

IMPORTANT: Aceasta este o analiză educațională, NU sfat de investiții."""

        # Call AI advisor endpoint (internal)
        from routes.ai_advisor import get_ai_response
        
        ai_response = await get_ai_response(prompt)
        
        return {
            "analysis": ai_response,
            "keywords": matched_keywords,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating analysis: {e}")
        # Return a fallback response
        return {
            "analysis": "Nu s-a putut genera analiza automată. Te rugăm să consulți secțiunea de educație financiară pentru a înțelege mai bine contextul acestei știri.",
            "keywords": [],
            "error": str(e)
        }
