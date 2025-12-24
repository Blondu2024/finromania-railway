"""Live Market Data - Simulated Real-time Feed"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
import random
import math
from datetime import datetime, timezone, timedelta
from config.database import get_database
import logging

router = APIRouter(prefix="/live", tags=["live_market"])
logger = logging.getLogger(__name__)

# Cache pentru simularea prețurilor
price_cache = {}
last_update = {}

def generate_realistic_tick(base_price: float, volatility: float = 0.001) -> Dict:
    """Generate realistic price movement (random walk)"""
    # Random walk cu drift
    change_percent = random.gauss(0, volatility)
    new_price = base_price * (1 + change_percent)
    
    # Bid/Ask spread (0.1% - 0.3% realistic)
    spread_percent = random.uniform(0.001, 0.003)
    spread = new_price * spread_percent
    
    bid = new_price - (spread / 2)
    ask = new_price + (spread / 2)
    
    return {
        "price": round(new_price, 4),
        "bid": round(bid, 4),
        "ask": round(ask, 4),
        "spread": round(spread, 4),
        "spread_percent": round(spread_percent * 100, 3),
        "change": round(new_price - base_price, 4),
        "change_percent": round(change_percent * 100, 3),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/quote/{symbol}")
async def get_live_quote(symbol: str, market_type: str = "bvb"):
    """Get live quote with bid/ask spread (simulated)"""
    try:
        db = await get_database()
        
        # Get base price from database
        if market_type == "bvb":
            stock = await db.stocks_bvb.find_one({"symbol": symbol.upper()}, {"_id": 0})
        else:
            stock = await db.stocks_global.find_one({"symbol": symbol.upper()}, {"_id": 0})
        
        if not stock:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        base_price = stock.get("price", 0)
        if base_price == 0:
            raise HTTPException(status_code=404, detail="Invalid price")
        
        # Determine volatility based on stock characteristics
        volatility = 0.002  # Default 0.2% per tick
        if stock.get("volatility") == "high":
            volatility = 0.004  # 0.4%
        elif stock.get("volatility") == "low":
            volatility = 0.001  # 0.1%
        
        # Check cache
        cache_key = f"{symbol}_{market_type}"
        now = datetime.now(timezone.utc)
        
        # Update every 5 seconds
        if cache_key in price_cache and cache_key in last_update:
            time_diff = (now - last_update[cache_key]).total_seconds()
            if time_diff < 5:
                return price_cache[cache_key]
        
        # Generate or update simulated price
        if cache_key in price_cache:
            # Continue from last price
            last_price = price_cache[cache_key]["price"]
            tick = generate_realistic_tick(last_price, volatility)
        else:
            # Start from base price
            tick = generate_realistic_tick(base_price, volatility)
        
        # Add stock info
        result = {
            "symbol": symbol.upper(),
            "name": stock.get("name", symbol),
            "market_type": market_type,
            **tick,
            "base_price": base_price,
            "volatility": volatility
        }
        
        # Update cache
        price_cache[cache_key] = result
        last_update[cache_key] = now
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting live quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/candles/{symbol}")
async def get_intraday_candles(
    symbol: str, 
    market_type: str = "bvb",
    interval: str = "5m",  # 1m, 5m, 15m, 1h
    limit: int = 100
):
    """Generate simulated intraday candles based on daily data"""
    try:
        db = await get_database()
        
        # Get base daily data
        if market_type == "bvb":
            stock = await db.stocks_bvb.find_one({"symbol": symbol.upper()}, {"_id": 0})
        else:
            stock = await db.stocks_global.find_one({"symbol": symbol.upper()}, {"_id": 0})
        
        if not stock:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        base_price = stock.get("price", 0)
        
        # Determine interval in minutes
        interval_map = {"1m": 1, "5m": 5, "15m": 15, "1h": 60}
        interval_minutes = interval_map.get(interval, 5)
        
        # Generate simulated candles
        candles = []
        current_time = datetime.now(timezone.utc)
        current_price = base_price
        
        for i in range(limit):
            # Random walk for each candle
            volatility = 0.003  # 0.3% per candle
            
            open_price = current_price
            close_change = random.gauss(0, volatility)
            close_price = open_price * (1 + close_change)
            
            # High/Low dentro do candle
            high_price = max(open_price, close_price) * (1 + abs(random.gauss(0, volatility * 0.5)))
            low_price = min(open_price, close_price) * (1 - abs(random.gauss(0, volatility * 0.5)))
            
            volume = int(random.uniform(50000, 500000))
            
            candle_time = current_time - timedelta(minutes=interval_minutes * (limit - i))
            
            candles.append({
                "time": int(candle_time.timestamp()),
                "open": round(open_price, 4),
                "high": round(high_price, 4),
                "low": round(low_price, 4),
                "close": round(close_price, 4),
                "volume": volume
            })
            
            current_price = close_price
        
        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "candles": candles,
            "total": len(candles)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating candles for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orderbook/{symbol}")
async def get_order_book_simulation(symbol: str, market_type: str = "bvb"):
    """Simulate order book (bid/ask levels)"""
    try:
        db = await get_database()
        
        if market_type == "bvb":
            stock = await db.stocks_bvb.find_one({"symbol": symbol.upper()}, {"_id": 0})
        else:
            stock = await db.stocks_global.find_one({"symbol": symbol.upper()}, {"_id": 0})
        
        if not stock:
            raise HTTPException(status_code=404, detail="Symbol not found")
        
        base_price = stock.get("price", 0)
        
        # Generate order book levels
        bids = []
        asks = []
        
        for i in range(5):
            # Bid levels (below current price)
            bid_price = base_price * (1 - (i + 1) * 0.001)
            bid_volume = int(random.uniform(100, 10000))
            bids.append({
                "price": round(bid_price, 4),
                "volume": bid_volume
            })
            
            # Ask levels (above current price)
            ask_price = base_price * (1 + (i + 1) * 0.001)
            ask_volume = int(random.uniform(100, 10000))
            asks.append({
                "price": round(ask_price, 4),
                "volume": ask_volume
            })
        
        return {
            "symbol": symbol.upper(),
            "bids": bids,
            "asks": asks,
            "spread": round(asks[0]["price"] - bids[0]["price"], 4),
            "mid_price": round((asks[0]["price"] + bids[0]["price"]) / 2, 4)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating order book: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-cache")
async def reset_price_cache():
    """Reset price simulation cache"""
    global price_cache, last_update
    price_cache = {}
    last_update = {}
    return {"message": "Price cache reset"}
