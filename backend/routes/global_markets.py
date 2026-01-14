"""Global Markets API - Indici, Comodități, Crypto"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import yfinance as yf
import logging
from utils.cache import get_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/global", tags=["Global Markets"])
cache = get_cache()

# Global indices and assets configuration
GLOBAL_INDICES = {
    # US Markets
    "^GSPC": {"name": "S&P 500", "country": "USA", "flag": "🇺🇸", "category": "indices"},
    "^IXIC": {"name": "NASDAQ", "country": "USA", "flag": "🇺🇸", "category": "indices"},
    "^DJI": {"name": "Dow Jones", "country": "USA", "flag": "🇺🇸", "category": "indices"},
    
    # European Markets
    "^GDAXI": {"name": "DAX", "country": "Germania", "flag": "🇩🇪", "category": "indices"},
    "^FTSE": {"name": "FTSE 100", "country": "UK", "flag": "🇬🇧", "category": "indices"},
    "^FCHI": {"name": "CAC 40", "country": "Franța", "flag": "🇫🇷", "category": "indices"},
    "^STOXX50E": {"name": "Euro Stoxx 50", "country": "Europa", "flag": "🇪🇺", "category": "indices"},
    
    # Asian Markets  
    "^N225": {"name": "Nikkei 225", "country": "Japonia", "flag": "🇯🇵", "category": "indices"},
    "^HSI": {"name": "Hang Seng", "country": "Hong Kong", "flag": "🇭🇰", "category": "indices"},
    "000001.SS": {"name": "Shanghai", "country": "China", "flag": "🇨🇳", "category": "indices"},
}

COMMODITIES = {
    "CL=F": {"name": "Petrol WTI", "flag": "🛢️", "category": "commodities", "unit": "USD/bbl"},
    "BZ=F": {"name": "Petrol Brent", "flag": "🛢️", "category": "commodities", "unit": "USD/bbl"},
    "GC=F": {"name": "Aur", "flag": "🥇", "category": "commodities", "unit": "USD/oz"},
    "SI=F": {"name": "Argint", "flag": "🥈", "category": "commodities", "unit": "USD/oz"},
    "NG=F": {"name": "Gaze Naturale", "flag": "🔥", "category": "commodities", "unit": "USD/MMBtu"},
    "HG=F": {"name": "Cupru", "flag": "🔶", "category": "commodities", "unit": "USD/lb"},
}

CRYPTO = {
    "BTC-USD": {"name": "Bitcoin", "flag": "₿", "category": "crypto"},
    "ETH-USD": {"name": "Ethereum", "flag": "Ξ", "category": "crypto"},
    "BNB-USD": {"name": "Binance Coin", "flag": "🔸", "category": "crypto"},
    "SOL-USD": {"name": "Solana", "flag": "◎", "category": "crypto"},
    "XRP-USD": {"name": "XRP", "flag": "✕", "category": "crypto"},
}

FOREX = {
    "EURUSD=X": {"name": "EUR/USD", "flag": "🇪🇺/🇺🇸", "category": "forex"},
    "GBPUSD=X": {"name": "GBP/USD", "flag": "🇬🇧/🇺🇸", "category": "forex"},
    "USDJPY=X": {"name": "USD/JPY", "flag": "🇺🇸/🇯🇵", "category": "forex"},
    "USDCHF=X": {"name": "USD/CHF", "flag": "🇺🇸/🇨🇭", "category": "forex"},
}


def fetch_ticker_data(symbol: str, info: dict) -> dict:
    """Fetch data for a single ticker"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        
        if hist.empty:
            return None
            
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        change = current_price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close else 0
        
        # Get more data for sparkline
        week_data = hist['Close'].tolist()[-5:]
        
        return {
            "symbol": symbol,
            "name": info["name"],
            "flag": info.get("flag", "📊"),
            "country": info.get("country", ""),
            "category": info.get("category", ""),
            "unit": info.get("unit", ""),
            "price": float(round(current_price, 2)),
            "change": float(round(change, 2)),
            "change_percent": float(round(change_percent, 2)),
            "prev_close": float(round(prev_close, 2)),
            "sparkline": [float(round(p, 2)) for p in week_data],
            "is_positive": bool(change_percent >= 0)
        }
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return None


@router.get("/indices")
async def get_global_indices():
    """Get all global indices"""
    try:
        results = []
        for symbol, info in GLOBAL_INDICES.items():
            data = fetch_ticker_data(symbol, info)
            if data:
                results.append(data)
        
        # Sort by change percent
        results.sort(key=lambda x: x["change_percent"], reverse=True)
        
        return {
            "indices": results,
            "count": len(results),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commodities")
async def get_commodities():
    """Get commodity prices"""
    try:
        results = []
        for symbol, info in COMMODITIES.items():
            data = fetch_ticker_data(symbol, info)
            if data:
                results.append(data)
        
        return {
            "commodities": results,
            "count": len(results),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching commodities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crypto")
async def get_crypto():
    """Get cryptocurrency prices"""
    try:
        results = []
        for symbol, info in CRYPTO.items():
            data = fetch_ticker_data(symbol, info)
            if data:
                results.append(data)
        
        # Sort by market cap (approximated by price for simplicity)
        results.sort(key=lambda x: x["price"], reverse=True)
        
        return {
            "crypto": results,
            "count": len(results),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching crypto: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forex")
async def get_forex():
    """Get forex rates"""
    try:
        results = []
        for symbol, info in FOREX.items():
            data = fetch_ticker_data(symbol, info)
            if data:
                results.append(data)
        
        return {
            "forex": results,
            "count": len(results),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching forex: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overview")
async def get_global_overview():
    """Get complete global market overview with caching"""
    try:
        # Check cache first (30 seconds TTL)
        cache_key = "global_overview"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("Returning cached global overview")
            return cached_data
        
        logger.info("Fetching fresh global market data...")
        all_assets = {}
        
        # Fetch all categories
        for symbol, info in {**GLOBAL_INDICES, **COMMODITIES, **CRYPTO, **FOREX}.items():
            data = fetch_ticker_data(symbol, info)
            if data:
                category = info["category"]
                if category not in all_assets:
                    all_assets[category] = []
                all_assets[category].append(data)
        
        # Calculate market sentiment
        all_items = [item for cat in all_assets.values() for item in cat]
        gainers = sum(1 for item in all_items if item["change_percent"] > 0)
        losers = sum(1 for item in all_items if item["change_percent"] < 0)
        avg_change = sum(item["change_percent"] for item in all_items) / len(all_items) if all_items else 0
        
        # Market status for different regions
        now = datetime.now(timezone.utc)
        hour = now.hour
        
        market_status = {
            "us": {"name": "🇺🇸 Wall Street", "open": 14 <= hour < 21, "hours": "14:30 - 21:00 UTC"},
            "europe": {"name": "🇪🇺 Europa", "open": 8 <= hour < 16, "hours": "08:00 - 16:30 UTC"},
            "asia": {"name": "🇯🇵 Asia", "open": 0 <= hour < 7, "hours": "00:00 - 07:00 UTC"},
            "crypto": {"name": "₿ Crypto", "open": True, "hours": "24/7"},
        }
        
        result = {
            "indices": all_assets.get("indices", []),
            "commodities": all_assets.get("commodities", []),
            "crypto": all_assets.get("crypto", []),
            "forex": all_assets.get("forex", []),
            "sentiment": {
                "gainers": gainers,
                "losers": losers,
                "avg_change": round(avg_change, 2),
                "status": "bullish" if avg_change > 0 else "bearish"
            },
            "market_status": market_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache pentru 10 secunde (permite refresh mai frecvent)
        cache.set(cache_key, result, ttl_seconds=10)
        logger.info(f"Cached global overview ({len(all_items)} assets) for 10s")
        
        return result
    except Exception as e:
        logger.error(f"Error fetching global overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chart/{symbol}")
async def get_asset_chart(symbol: str, period: str = "1mo"):
    """Get historical chart data for an asset"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")
        
        chart_data = [
            {
                "date": index.strftime("%Y-%m-%d"),
                "open": float(round(row["Open"], 2)),
                "high": float(round(row["High"], 2)),
                "low": float(round(row["Low"], 2)),
                "close": float(round(row["Close"], 2)),
                "volume": int(row["Volume"])
            }
            for index, row in hist.iterrows()
        ]
        
        # Get asset info
        all_assets = {**GLOBAL_INDICES, **COMMODITIES, **CRYPTO, **FOREX}
        asset_info = all_assets.get(symbol, {"name": symbol, "flag": "📊"})
        
        return {
            "symbol": symbol,
            "name": asset_info.get("name", symbol),
            "flag": asset_info.get("flag", "📊"),
            "period": period,
            "data": chart_data,
            "current_price": chart_data[-1]["close"] if chart_data else None,
            "period_change": round(
                ((chart_data[-1]["close"] - chart_data[0]["close"]) / chart_data[0]["close"]) * 100, 2
            ) if chart_data else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chart for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
