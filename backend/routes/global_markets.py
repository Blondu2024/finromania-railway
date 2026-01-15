"""Global Markets API - Indici, Comodități, Crypto"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import yfinance as yf
import logging
from utils.cache import get_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/global", tags=["Global Markets"])
cache = get_cache()

# Global indices - EODHD symbols pentru real-time data
GLOBAL_INDICES = {
    # US Markets - folosim ETF-uri pentru real-time (SPY = S&P 500, QQQ = NASDAQ, DIA = Dow)
    "SPY.US": {"name": "S&P 500", "country": "USA", "flag": "🇺🇸", "category": "indices"},
    "QQQ.US": {"name": "NASDAQ", "country": "USA", "flag": "🇺🇸", "category": "indices"},
    "DIA.US": {"name": "Dow Jones", "country": "USA", "flag": "🇺🇸", "category": "indices"},
    
    # European Markets
    "EWG.US": {"name": "DAX (Germany ETF)", "country": "Germania", "flag": "🇩🇪", "category": "indices"},
    "EWU.US": {"name": "FTSE 100 (UK ETF)", "country": "UK", "flag": "🇬🇧", "category": "indices"},
    "EWQ.US": {"name": "CAC 40 (France ETF)", "country": "Franța", "flag": "🇫🇷", "category": "indices"},
    
    # Asian Markets  
    "EWJ.US": {"name": "Nikkei 225 (Japan ETF)", "country": "Japonia", "flag": "🇯🇵", "category": "indices"},
    "EWH.US": {"name": "Hang Seng (HK ETF)", "country": "Hong Kong", "flag": "🇭🇰", "category": "indices"},
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
    "BTC-USD": {"name": "Bitcoin", "flag": "₿", "category": "crypto", "use_yfinance": True},
    "ETH-USD": {"name": "Ethereum", "flag": "Ξ", "category": "crypto", "use_yfinance": True},
    "BNB-USD": {"name": "Binance Coin", "flag": "🔸", "category": "crypto", "use_yfinance": True},
    "SOL-USD": {"name": "Solana", "flag": "◎", "category": "crypto", "use_yfinance": True},
    "XRP-USD": {"name": "XRP", "flag": "✕", "category": "crypto", "use_yfinance": True},
}

FOREX = {
    "EURUSD=X": {"name": "EUR/USD", "flag": "🇪🇺/🇺🇸", "category": "forex"},
    "GBPUSD=X": {"name": "GBP/USD", "flag": "🇬🇧/🇺🇸", "category": "forex"},
    "USDJPY=X": {"name": "USD/JPY", "flag": "🇺🇸/🇯🇵", "category": "forex"},
    "USDCHF=X": {"name": "USD/CHF", "flag": "🇺🇸/🇨🇭", "category": "forex"},
}


async def fetch_ticker_yfinance(symbol: str, info: dict) -> dict:
    """Fallback pentru crypto/commodities cu yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d", interval="5m")
        
        if hist.empty:
            hist = ticker.history(period="2d")
            
        if hist.empty:
            return None
            
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[0] if len(hist) > 1 else current_price
        change = current_price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close else 0
        
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
            "sparkline": [],
            "is_positive": bool(change_percent >= 0),
            "source": "yfinance"
        }
    except Exception as e:
        logger.error(f"yfinance error for {symbol}: {e}")


async def fetch_ticker_data(symbol: str, info: dict) -> dict:
    """Unified function - route la EODHD sau yfinance based on asset type"""
    # Folosește yfinance pentru crypto și commodities (EODHD nu le suportă)
    if info.get("use_yfinance"):
        return await fetch_ticker_yfinance(symbol, info)
    else:
        # Folosește EODHD pentru US indices și forex (real-time <50ms!)
        return await fetch_ticker_data_eodhd(symbol, info)

        return None


async def fetch_ticker_data_eodhd(symbol: str, info: dict) -> dict:
    """Fetch REAL-TIME data from EODHD API ($100/month) - <1s delay!"""
    import httpx
    import os
    
    api_key = os.environ.get("EODHD_API_KEY")
    if not api_key:
        logger.warning(f"EODHD API key not found, skipping {symbol}")
        return None
    
    try:
        # EODHD real-time endpoint
        url = f"https://eodhd.com/api/real-time/{symbol}"
        params = {"api_token": api_key, "fmt": "json"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=5)
            data = response.json() if response.status_code == 200 else None
        
        if not data:
            return None
        
        current_price = float(data.get("close", 0))
        prev_close = float(data.get("previousClose", current_price))
        change = float(data.get("change", 0))
        change_percent = float(data.get("change_p", 0))
        
        return {
            "symbol": symbol,
            "name": info["name"],
            "flag": info.get("flag", "📊"),
            "country": info.get("country", ""),
            "category": info.get("category", ""),
            "unit": info.get("unit", ""),
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "prev_close": round(prev_close, 2),
            "sparkline": [],  # Optional: can add intraday sparkline
            "is_positive": bool(change_percent >= 0),
            "last_update": datetime.fromtimestamp(data.get("timestamp", 0)).isoformat(),
            "source": "eodhd_realtime"
        }
    except Exception as e:
        logger.error(f"EODHD error for {symbol}: {e}")
        return None


@router.get("/indices")
async def get_global_indices():
    """Get all global indices"""
    try:
        results = []
        for symbol, info in GLOBAL_INDICES.items():
            data = await fetch_ticker_data(symbol, info)
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
            data = await fetch_ticker_data(symbol, info)
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
            data = await fetch_ticker_data(symbol, info)
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
            data = await fetch_ticker_data(symbol, info)
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
    """Get complete global market overview cu date LIVE (NO CACHE pentru real-time)"""
    try:
        logger.info("Fetching LIVE global market data (no cache)...")
        all_assets = {}
        
        # Fetch all categories - EODHD pentru US, yfinance pentru crypto
        for symbol, info in {**GLOBAL_INDICES, **COMMODITIES, **CRYPTO, **FOREX}.items():
            # Folosește yfinance pentru crypto (EODHD nu are)
            if info.get("use_yfinance"):
                data = await fetch_ticker_yfinance(symbol, info)
            else:
                data = await fetch_ticker_data_eodhd(symbol, info)
            
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
        
        # NO CACHE - pentru date LIVE!
        logger.info(f"Returning LIVE data ({len(all_items)} assets)")
        
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
