"""Global Markets API - Indici, Comodități, Crypto - 100% EODHD"""
from fastapi import APIRouter, HTTPException, Response
from datetime import datetime, timezone
import asyncio
import logging
from utils.cache import get_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/global", tags=["Global Markets"])
cache = get_cache()

# Global indices - EODHD symbols pentru LIVE real-time data (All-in-One plan)
GLOBAL_INDICES = {
    # US Markets - Indici reali cu EODHD
    "GSPC.INDX": {"name": "S&P 500", "country": "USA", "flag": "🇺🇸", "category": "indices"},
    "NDX.INDX": {"name": "NASDAQ 100", "country": "USA", "flag": "🇺🇸", "category": "indices"},
    "DJI.INDX": {"name": "Dow Jones", "country": "USA", "flag": "🇺🇸", "category": "indices"},
    
    # European Markets
    "GDAXI.INDX": {"name": "DAX", "country": "Germania", "flag": "🇩🇪", "category": "indices"},
    "FTSE.INDX": {"name": "FTSE 100", "country": "UK", "flag": "🇬🇧", "category": "indices"},
    "FCHI.INDX": {"name": "CAC 40", "country": "Franța", "flag": "🇫🇷", "category": "indices"},
    
    # Asian Markets  
    "N225.INDX": {"name": "Nikkei 225", "country": "Japonia", "flag": "🇯🇵", "category": "indices"},
    "HSI.INDX": {"name": "Hang Seng", "country": "Hong Kong", "flag": "🇭🇰", "category": "indices"},
}

COMMODITIES = {
    # Using ETFs since EODHD doesn't have direct commodity futures
    "GLD.US": {"name": "Aur (GLD)", "flag": "🥇", "category": "commodities", "unit": "USD"},
    "USO.US": {"name": "Petrol WTI (USO)", "flag": "🛢️", "category": "commodities", "unit": "USD"},
    "UNG.US": {"name": "Gaze Naturale (UNG)", "flag": "🔥", "category": "commodities", "unit": "USD"},
}

CRYPTO = {
    # EODHD crypto symbols use .CC suffix
    "BTC-USD.CC": {"name": "Bitcoin", "flag": "₿", "category": "crypto"},
    "ETH-USD.CC": {"name": "Ethereum", "flag": "Ξ", "category": "crypto"},
}

FOREX = {
    "EURUSD.FOREX": {"name": "EUR/USD", "flag": "🇪🇺/🇺🇸", "category": "forex"},
    "GBPUSD.FOREX": {"name": "GBP/USD", "flag": "🇬🇧/🇺🇸", "category": "forex"},
    "USDJPY.FOREX": {"name": "USD/JPY", "flag": "🇺🇸/🇯🇵", "category": "forex"},
    "USDCHF.FOREX": {"name": "USD/CHF", "flag": "🇺🇸/🇨🇭", "category": "forex"},
    "USDRON.FOREX": {"name": "USD/RON", "flag": "🇺🇸/🇷🇴", "category": "forex"},
    "EURRON.FOREX": {"name": "EUR/RON", "flag": "🇪🇺/🇷🇴", "category": "forex"},
}

# Popular Global Stocks - LIVE cu EODHD
GLOBAL_STOCKS = {
    "AAPL.US": {"name": "Apple", "country": "USA", "flag": "🇺🇸", "category": "tech"},
    "MSFT.US": {"name": "Microsoft", "country": "USA", "flag": "🇺🇸", "category": "tech"},
    "GOOGL.US": {"name": "Alphabet (Google)", "country": "USA", "flag": "🇺🇸", "category": "tech"},
    "AMZN.US": {"name": "Amazon", "country": "USA", "flag": "🇺🇸", "category": "tech"},
    "NVDA.US": {"name": "NVIDIA", "country": "USA", "flag": "🇺🇸", "category": "tech"},
    "META.US": {"name": "Meta (Facebook)", "country": "USA", "flag": "🇺🇸", "category": "tech"},
    "TSLA.US": {"name": "Tesla", "country": "USA", "flag": "🇺🇸", "category": "auto"},
    "JPM.US": {"name": "JPMorgan Chase", "country": "USA", "flag": "🇺🇸", "category": "finance"},
    "V.US": {"name": "Visa", "country": "USA", "flag": "🇺🇸", "category": "finance"},
    "XOM.US": {"name": "Exxon Mobil", "country": "USA", "flag": "🇺🇸", "category": "energy"},
}


async def fetch_ticker_yfinance(symbol: str, info: dict) -> dict:
    """Fallback pentru crypto/commodities cu yfinance - WITH 60s CACHE & SHARED THREAD POOL"""
    import time
    
    # Check cache first (60 second TTL - longer to improve page load speed)
    cache_key = symbol
    if cache_key in _yfinance_cache:
        cache_age = time.time() - _yfinance_cache_time.get(cache_key, 0)
        if cache_age < 60:  # 60 second cache
            return _yfinance_cache[cache_key]
    
    def _fetch_sync():
        """Synchronous fetch in thread"""
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
            logger.debug(f"yfinance error for {symbol}: {e}")
            return None
    
    try:
        # Run yfinance in SHARED thread pool 
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_yfinance_executor, _fetch_sync)
        
        if result:
            # Store in cache
            _yfinance_cache[cache_key] = result
            _yfinance_cache_time[cache_key] = time.time()
            return result
        
        # Return cached data if available, even if stale
        if cache_key in _yfinance_cache:
            return _yfinance_cache[cache_key]
        return None
    except Exception as e:
        logger.debug(f"yfinance async error for {symbol}: {e}")
        if cache_key in _yfinance_cache:
            return _yfinance_cache[cache_key]
        return None


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
    """Fetch LIVE data from EODHD API - ALWAYS uses INTRADAY for real-time prices!"""
    import httpx
    import os
    
    api_key = os.environ.get("EODHD_API_KEY")
    if not api_key:
        logger.warning(f"EODHD API key not found, skipping {symbol}")
        return None
    
    def safe_float(val, default=0.0):
        """Safely convert to float, handling 'NA' strings"""
        if val is None or val == 'NA' or val == 'N/A' or val == '':
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default
    
    def safe_int(val, default=0):
        """Safely convert to int, handling 'NA' strings"""
        if val is None or val == 'NA' or val == 'N/A' or val == '':
            return default
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return default
    
    try:
        async with httpx.AsyncClient() as client:
            # ALWAYS get previous close from real-time endpoint first (for change calculation)
            rt_url = f"https://eodhd.com/api/real-time/{symbol}"
            rt_params = {"api_token": api_key, "fmt": "json"}
            rt_response = await client.get(rt_url, params=rt_params, timeout=5)
            
            prev_close = 0
            rt_data = {}
            if rt_response.status_code == 200:
                rt_data = rt_response.json()
                prev_close = safe_float(rt_data.get("previousClose"), 0)
            
            # ALWAYS try INTRADAY endpoint for LIVE current price
            intraday_url = f"https://eodhd.com/api/intraday/{symbol}"
            intraday_params = {"api_token": api_key, "fmt": "json", "interval": "1m"}
            
            intraday_response = await client.get(intraday_url, params=intraday_params, timeout=8)
            
            if intraday_response.status_code == 200:
                intraday_data = intraday_response.json()
                if isinstance(intraday_data, list) and len(intraday_data) > 0:
                    # Get the LATEST candle (most recent price!)
                    last_candle = intraday_data[-1]
                    current_price = safe_float(last_candle.get("close"))
                    timestamp = safe_int(last_candle.get("timestamp"))
                    
                    # Use prev_close from real-time if available, otherwise calculate from intraday
                    if prev_close == 0:
                        # Fallback: use first candle of the day as prev_close approximation
                        prev_close = safe_float(intraday_data[0].get("open"), current_price)
                    
                    if current_price > 0 and prev_close > 0:
                        change = current_price - prev_close
                        change_percent = (change / prev_close * 100)
                        
                        # Get today's high/low from all intraday candles
                        today_high = max(safe_float(c.get("high"), 0) for c in intraday_data[-500:])  # Last ~8 hours
                        today_low = min(safe_float(c.get("low"), float('inf')) for c in intraday_data[-500:] if safe_float(c.get("low"), 0) > 0)
                        if today_low == float('inf'):
                            today_low = current_price
                        
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
                            "high": round(today_high, 2),
                            "low": round(today_low, 2),
                            "volume": safe_int(last_candle.get("volume")),
                            "sparkline": [],
                            "is_positive": bool(change_percent >= 0),
                            "last_update": datetime.fromtimestamp(timestamp).isoformat() if timestamp else datetime.now(timezone.utc).isoformat(),
                            "source": "eodhd_intraday_live",
                            "is_live": True
                        }
            
            # Fallback to real-time endpoint only if intraday completely fails
            if not rt_data:
                return None
            
            current_price = safe_float(rt_data.get("close"))
            if prev_close == 0:
                prev_close = safe_float(rt_data.get("previousClose"), current_price)
            change = safe_float(rt_data.get("change"))
            change_percent = safe_float(rt_data.get("change_p"))
            high = safe_float(rt_data.get("high"), current_price)
            low = safe_float(rt_data.get("low"), current_price)
            volume = safe_int(rt_data.get("volume"))
            timestamp = safe_int(rt_data.get("timestamp"))
            
            # Skip if no valid price
            if current_price == 0:
                logger.warning(f"No valid price for {symbol}")
                return None
            
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
                "high": round(high, 2),
                "low": round(low, 2),
                "volume": volume,
                "sparkline": [],
                "is_positive": bool(change_percent >= 0),
                "last_update": datetime.fromtimestamp(timestamp).isoformat() if timestamp else datetime.now(timezone.utc).isoformat(),
                "source": "eodhd_realtime_fallback",
                "is_live": False  # Not truly live, last close
            }
    except Exception as e:
        logger.error(f"EODHD error for {symbol}: {e}")
        return None


@router.get("/indices")
async def get_global_indices():
    """Get all global indices - LIVE from EODHD with DB fallback"""
    from config.database import get_database
    
    try:
        db = await get_database()
        results = []
        
        for symbol, info in GLOBAL_INDICES.items():
            data = await fetch_ticker_data(symbol, info)
            
            if data:
                # Got live data from EODHD
                results.append(data)
            else:
                # Fallback to DB cache
                cached = await db.stocks_global.find_one({"symbol": symbol}, {"_id": 0})
                if cached:
                    cached["source"] = "db_cache"
                    cached["is_live"] = False
                    cached["name"] = info.get("name", cached.get("name", symbol))
                    cached["flag"] = info.get("flag", cached.get("flag", "📊"))
                    cached["country"] = info.get("country", cached.get("country", ""))
                    results.append(cached)
                    logger.info(f"Using DB cache for {symbol} (EODHD unavailable)")
        
        # Sort by change percent
        results.sort(key=lambda x: x.get("change_percent", 0), reverse=True)
        
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
    """Get forex rates - LIVE cu EODHD"""
    try:
        results = []
        for symbol, info in FOREX.items():
            data = await fetch_ticker_data_eodhd(symbol, info)
            if data:
                results.append(data)
        
        return {
            "forex": results,
            "count": len(results),
            "is_live": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching forex: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks")
async def get_global_stocks():
    """Get popular global stocks - LIVE cu EODHD All-in-One plan"""
    try:
        results = []
        for symbol, info in GLOBAL_STOCKS.items():
            data = await fetch_ticker_data_eodhd(symbol, info)
            if data:
                results.append(data)
        
        # Sort by market cap or change
        results.sort(key=lambda x: x["change_percent"], reverse=True)
        
        return {
            "stocks": results,
            "count": len(results),
            "is_live": True,
            "source": "EODHD All-in-One",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching global stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def fetch_multiple_tickers_eodhd(symbols_info: dict) -> dict:
    """Fetch from EODHD - uses real-time batch (most reliable source)"""
    import httpx
    import os
    
    api_key = os.environ.get("EODHD_API_KEY")
    if not api_key:
        return {}
    
    def safe_float(val, default=0.0):
        if val is None or val == 'NA' or val == 'N/A' or val == '':
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default
    
    def safe_int(val, default=0):
        if val is None or val == 'NA' or val == 'N/A' or val == '':
            return default
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return default
    
    results = {}
    eodhd_symbols = {s: i for s, i in symbols_info.items() if not i.get("use_yfinance")}
    
    if not eodhd_symbols:
        return results
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # Single batch request for ALL assets - real-time is most reliable
            all_symbols_str = ",".join(eodhd_symbols.keys())
            rt_url = f"https://eodhd.com/api/real-time/{all_symbols_str}"
            rt_params = {"api_token": api_key, "fmt": "json"}
            
            rt_response = await client.get(rt_url, params=rt_params)
            
            if rt_response.status_code == 200:
                rt_data = rt_response.json()
                rt_items = rt_data if isinstance(rt_data, list) else [rt_data]
                
                for item in rt_items:
                    code = item.get("code", "")
                    if code not in eodhd_symbols:
                        continue
                    
                    info = eodhd_symbols[code]
                    price = safe_float(item.get("close"))
                    prev_close = safe_float(item.get("previousClose"), price)
                    
                    if price == 0:
                        continue
                    
                    timestamp = safe_int(item.get("timestamp"))
                    
                    results[code] = {
                        "symbol": code,
                        "name": info["name"],
                        "flag": info.get("flag", "📊"),
                        "country": info.get("country", ""),
                        "category": info.get("category", ""),
                        "unit": info.get("unit", ""),
                        "price": round(price, 2),
                        "change": round(safe_float(item.get("change")), 2),
                        "change_percent": round(safe_float(item.get("change_p")), 2),
                        "prev_close": round(prev_close, 2),
                        "high": round(safe_float(item.get("high"), price), 2),
                        "low": round(safe_float(item.get("low"), price), 2),
                        "volume": safe_int(item.get("volume")),
                        "sparkline": [],
                        "is_positive": bool(safe_float(item.get("change_p")) >= 0),
                        "last_update": datetime.fromtimestamp(timestamp).isoformat() if timestamp else datetime.now(timezone.utc).isoformat(),
                        "source": "eodhd_realtime",
                        "is_live": True  
                    }
                    
    except Exception as e:
        logger.error(f"EODHD fetch error: {e}")
    
    return results


@router.get("/overview")
async def get_global_overview(response: Response):
    """Get complete global market overview - 100% EODHD, no yfinance!"""
    from config.database import get_database
    
    # Prevent ALL caching
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        db = await get_database()
        logger.info("Fetching LIVE global market data (EODHD only)...")
        
        # ALL symbols now use EODHD - no more yfinance!
        all_symbols = {**GLOBAL_INDICES, **GLOBAL_STOCKS, **COMMODITIES, **CRYPTO, **FOREX}
        
        # Single EODHD batch fetch (ultra fast!)
        all_data = await fetch_multiple_tickers_eodhd(all_symbols)
        
        # Organize by category
        all_assets = {}
        for symbol, info in all_symbols.items():
            data = all_data.get(symbol)
            if not data:
                # Fallback to DB cache
                cached = await db.stocks_global.find_one({"symbol": symbol}, {"_id": 0})
                if cached:
                    cached["source"] = "db_cache"
                    cached["is_live"] = False
                    data = cached
            
            if data:
                category = info["category"]
                if category not in all_assets:
                    all_assets[category] = []
                all_assets[category].append(data)
        
        # Calculate market sentiment
        all_items = [item for cat in all_assets.values() for item in cat]
        gainers = sum(1 for item in all_items if item.get("change_percent", 0) > 0)
        losers = sum(1 for item in all_items if item.get("change_percent", 0) < 0)
        avg_change = sum(item.get("change_percent", 0) for item in all_items) / len(all_items) if all_items else 0
        
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
            "stocks": all_assets.get("tech", []) + all_assets.get("finance", []) + all_assets.get("energy", []) + all_assets.get("auto", []),
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
            "is_live": True,
            "source": "EODHD All-in-One (Batch)",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Returning LIVE data ({len(all_items)} assets) - BATCH mode")
        
        return result
    except Exception as e:
        logger.error(f"Error fetching global overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chart/{symbol}")
async def get_asset_chart(
    symbol: str, 
    period: str = "1mo",
    interval: str = "1d"
):
    """
    Get historical/intraday chart data for an asset
    
    EODHD Intraday intervals: 1m, 5m, 15m, 30m, 1h
    EOD periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y
    """
    import httpx
    import os
    from datetime import datetime, timedelta
    
    api_key = os.environ.get("EODHD_API_KEY")
    
    # Map period to EODHD format
    period_days = {
        "1d": 1,
        "5d": 5,
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365,
        "5y": 1825
    }
    
    # Intraday intervals supported by EODHD
    intraday_intervals = ["1m", "5m", "15m", "30m", "1h"]
    
    try:
        # Convert symbol format if needed (e.g., GSPC.INDX -> ^GSPC for yfinance fallback)
        eodhd_symbol = symbol
        
        # Determine if we need intraday data
        use_intraday = interval in intraday_intervals
        
        async with httpx.AsyncClient() as client:
            if use_intraday:
                # Use EODHD Intraday API (LIVE with $100 plan!)
                url = f"https://eodhd.com/api/intraday/{eodhd_symbol}"
                params = {
                    "api_token": api_key,
                    "fmt": "json",
                    "interval": interval
                }
                
                # Calculate date range - EODHD needs UNIX timestamp!
                days = period_days.get(period, 30)
                from_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
                params["from"] = from_timestamp
                
                logger.info(f"Fetching EODHD intraday for {eodhd_symbol}, interval={interval}, from_ts={from_timestamp}")
                
                response = await client.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if not data:
                        raise HTTPException(status_code=404, detail=f"No intraday data for {symbol}")
                    
                    chart_data = [
                        {
                            "date": item.get("datetime") or item.get("date"),
                            "timestamp": item.get("timestamp"),
                            "open": float(item.get("open") or 0),
                            "high": float(item.get("high") or 0),
                            "low": float(item.get("low") or 0),
                            "close": float(item.get("close") or 0),
                            "volume": int(item.get("volume") or 0)
                        }
                        for item in data
                        if item.get("close") is not None
                    ]
                    
                    # Get asset info
                    all_assets = {**GLOBAL_INDICES, **GLOBAL_STOCKS, **COMMODITIES, **CRYPTO, **FOREX}
                    asset_info = all_assets.get(symbol, {"name": symbol, "flag": "📊"})
                    
                    return {
                        "symbol": symbol,
                        "name": asset_info.get("name", symbol),
                        "flag": asset_info.get("flag", "📊"),
                        "period": period,
                        "interval": interval,
                        "data": chart_data,
                        "data_points": len(chart_data),
                        "current_price": chart_data[-1]["close"] if chart_data else None,
                        "period_change": round(
                            ((chart_data[-1]["close"] - chart_data[0]["close"]) / chart_data[0]["close"]) * 100, 2
                        ) if chart_data and chart_data[0]["close"] > 0 else 0,
                        "source": "eodhd_intraday",
                        "is_live": True
                    }
                else:
                    logger.warning(f"EODHD intraday failed for {symbol}: {response.status_code}")
            
            # Fallback to EOD data or use yfinance
            # Try EODHD EOD first
            url = f"https://eodhd.com/api/eod/{eodhd_symbol}"
            days = period_days.get(period, 30)
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            params = {
                "api_token": api_key,
                "fmt": "json",
                "from": from_date
            }
            
            response = await client.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    chart_data = [
                        {
                            "date": item.get("date"),
                            "open": float(item.get("open", 0)),
                            "high": float(item.get("high", 0)),
                            "low": float(item.get("low", 0)),
                            "close": float(item.get("close", 0)),
                            "volume": int(item.get("volume", 0))
                        }
                        for item in data
                    ]
                    
                    all_assets = {**GLOBAL_INDICES, **GLOBAL_STOCKS, **COMMODITIES, **CRYPTO, **FOREX}
                    asset_info = all_assets.get(symbol, {"name": symbol, "flag": "📊"})
                    
                    return {
                        "symbol": symbol,
                        "name": asset_info.get("name", symbol),
                        "flag": asset_info.get("flag", "📊"),
                        "period": period,
                        "interval": "1d",
                        "data": chart_data,
                        "data_points": len(chart_data),
                        "current_price": chart_data[-1]["close"] if chart_data else None,
                        "period_change": round(
                            ((chart_data[-1]["close"] - chart_data[0]["close"]) / chart_data[0]["close"]) * 100, 2
                        ) if chart_data and chart_data[0]["close"] > 0 else 0,
                        "source": "eodhd_eod",
                        "is_live": False
                    }
        
        # Final fallback to yfinance
        ticker = yf.Ticker(symbol.replace(".US", "").replace(".INDX", ""))
        hist = ticker.history(period=period, interval=interval if interval != "1d" else None)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")
        
        chart_data = [
            {
                "date": index.strftime("%Y-%m-%d %H:%M:%S") if interval in intraday_intervals else index.strftime("%Y-%m-%d"),
                "open": float(round(row["Open"], 2)),
                "high": float(round(row["High"], 2)),
                "low": float(round(row["Low"], 2)),
                "close": float(round(row["Close"], 2)),
                "volume": int(row["Volume"])
            }
            for index, row in hist.iterrows()
        ]
        
        all_assets = {**GLOBAL_INDICES, **GLOBAL_STOCKS, **COMMODITIES, **CRYPTO, **FOREX}
        asset_info = all_assets.get(symbol, {"name": symbol, "flag": "📊"})
        
        return {
            "symbol": symbol,
            "name": asset_info.get("name", symbol),
            "flag": asset_info.get("flag", "📊"),
            "period": period,
            "interval": interval,
            "data": chart_data,
            "data_points": len(chart_data),
            "current_price": chart_data[-1]["close"] if chart_data else None,
            "period_change": round(
                ((chart_data[-1]["close"] - chart_data[0]["close"]) / chart_data[0]["close"]) * 100, 2
            ) if chart_data and chart_data[0]["close"] > 0 else 0,
            "source": "yfinance",
            "is_live": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chart for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

