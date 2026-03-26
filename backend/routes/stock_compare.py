"""
Stock Comparison API - Comparație side-by-side pentru acțiuni BVB
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timezone
import logging
import os
import httpx

from config.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stocks", tags=["Stock Compare"])

EODHD_API_KEY = os.environ.get("EODHD_API_KEY")
EODHD_BASE = "https://eodhd.com/api"


@router.get("/compare")
async def compare_stocks(symbols: str = Query(..., description="Symbols separated by comma, max 4")):
    """
    Compară 2-4 acțiuni BVB side-by-side
    Returnează: preț, variație, volume, P/E, dividend yield, RSI, 52w high/low
    """
    db = await get_database()
    
    # Parse symbols
    symbol_list = [s.strip().upper() for s in symbols.split(",")][:4]
    
    if len(symbol_list) < 2:
        raise HTTPException(status_code=400, detail="Minimum 2 symbols required for comparison")
    
    comparison_data = []
    
    for symbol in symbol_list:
        # Get basic stock data from DB
        stock = await db.stocks_bvb.find_one({"symbol": symbol}, {"_id": 0})
        
        if not stock:
            comparison_data.append({
                "symbol": symbol,
                "error": "Stock not found"
            })
            continue
        
        # Fetch fundamentals and technicals from EODHD
        fundamentals = {}
        technicals = {}
        
        if EODHD_API_KEY:
            try:
                async with httpx.AsyncClient() as client:
                    # Fundamentals
                    fund_url = f"{EODHD_BASE}/fundamentals/{symbol}.RO"
                    fund_res = await client.get(fund_url, params={"api_token": EODHD_API_KEY, "fmt": "json"}, timeout=10)
                    if fund_res.status_code == 200:
                        fund_data = fund_res.json()
                        highlights = fund_data.get("Highlights", {})
                        fundamentals = {
                            "pe_ratio": highlights.get("PERatio"),
                            "eps": highlights.get("EarningsShare"),
                            "dividend_yield": highlights.get("DividendYield"),
                            "market_cap": highlights.get("MarketCapitalization"),
                            "52_week_high": highlights.get("52WeekHigh"),
                            "52_week_low": highlights.get("52WeekLow"),
                            "roe": highlights.get("ReturnOnEquityTTM"),
                            "profit_margin": highlights.get("ProfitMargin")
                        }
                    
                    # RSI
                    rsi_url = f"{EODHD_BASE}/technical/{symbol}.RO"
                    rsi_res = await client.get(rsi_url, params={
                        "api_token": EODHD_API_KEY, "fmt": "json", "function": "rsi", "period": 14
                    }, timeout=10)
                    if rsi_res.status_code == 200:
                        rsi_data = rsi_res.json()
                        if rsi_data and len(rsi_data) > 0:
                            technicals["rsi"] = rsi_data[-1].get("rsi")
                    
                    # SMA 50
                    sma_res = await client.get(rsi_url, params={
                        "api_token": EODHD_API_KEY, "fmt": "json", "function": "sma", "period": 50
                    }, timeout=10)
                    if sma_res.status_code == 200:
                        sma_data = sma_res.json()
                        if sma_data and len(sma_data) > 0:
                            technicals["sma_50"] = sma_data[-1].get("sma")
                            
            except Exception as e:
                logger.warning(f"Error fetching EODHD data for {symbol}: {e}")
        
        # Calculate distance from 52w high/low
        price = stock.get("price", 0)
        high_52w = fundamentals.get("52_week_high")
        low_52w = fundamentals.get("52_week_low")
        
        pct_from_high = None
        pct_from_low = None
        
        if high_52w and price:
            pct_from_high = round(((price - high_52w) / high_52w) * 100, 2)
        if low_52w and price:
            pct_from_low = round(((price - low_52w) / low_52w) * 100, 2)
        
        comparison_data.append({
            "symbol": symbol,
            "name": stock.get("name"),
            "sector": stock.get("sector"),
            "price": price,
            "change_percent": stock.get("change_percent"),
            "volume": stock.get("volume"),
            # Fundamentals
            "pe_ratio": round(fundamentals.get("pe_ratio"), 2) if fundamentals.get("pe_ratio") else None,
            "eps": round(fundamentals.get("eps"), 2) if fundamentals.get("eps") else None,
            "dividend_yield": round(fundamentals.get("dividend_yield", 0) * 100, 2) if fundamentals.get("dividend_yield") else None,
            "market_cap": fundamentals.get("market_cap"),
            "roe": round(fundamentals.get("roe", 0) * 100, 2) if fundamentals.get("roe") else None,
            "profit_margin": round(fundamentals.get("profit_margin", 0) * 100, 2) if fundamentals.get("profit_margin") else None,
            # 52 Week
            "52_week_high": high_52w,
            "52_week_low": low_52w,
            "pct_from_52w_high": pct_from_high,
            "pct_from_52w_low": pct_from_low,
            # Technicals
            "rsi": round(technicals.get("rsi"), 2) if technicals.get("rsi") else None,
            "sma_50": round(technicals.get("sma_50"), 2) if technicals.get("sma_50") else None,
            "above_sma_50": price > technicals.get("sma_50", 0) if technicals.get("sma_50") else None
        })
    
    return {
        "comparison": comparison_data,
        "symbols": symbol_list,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/52-week-extremes")
async def get_52_week_extremes():
    """
    Returnează acțiunile aproape de maximul/minimul pe 52 săptămâni
    """
    db = await get_database()
    stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
    
    near_high = []
    near_low = []
    
    if not EODHD_API_KEY:
        return {"near_52w_high": [], "near_52w_low": [], "error": "EODHD API key not configured"}
    
    async with httpx.AsyncClient() as client:
        for stock in stocks[:50]:  # Limit to top 50 to avoid rate limits
            symbol = stock.get("symbol")
            price = stock.get("price", 0)
            
            if not price:
                continue
            
            try:
                url = f"{EODHD_BASE}/fundamentals/{symbol}.RO"
                res = await client.get(url, params={"api_token": EODHD_API_KEY, "fmt": "json"}, timeout=8)
                
                if res.status_code != 200:
                    continue
                
                data = res.json()
                highlights = data.get("Highlights", {})
                high_52w = highlights.get("52WeekHigh")
                low_52w = highlights.get("52WeekLow")
                
                if not high_52w or not low_52w:
                    continue
                
                pct_from_high = ((price - high_52w) / high_52w) * 100
                pct_from_low = ((price - low_52w) / low_52w) * 100
                
                stock_data = {
                    "symbol": symbol,
                    "name": stock.get("name"),
                    "price": price,
                    "change_percent": stock.get("change_percent"),
                    "52_week_high": high_52w,
                    "52_week_low": low_52w,
                    "pct_from_high": round(pct_from_high, 2),
                    "pct_from_low": round(pct_from_low, 2)
                }
                
                # Aproape de maxim (în top 5% de la maxim)
                if pct_from_high >= -5:
                    near_high.append(stock_data)
                
                # Aproape de minim (în bottom 10% de la minim)
                if pct_from_low <= 15:
                    near_low.append(stock_data)
                    
            except Exception as e:
                logger.warning(f"Error fetching 52w data for {symbol}: {e}")
                continue
    
    # Sort by distance
    near_high.sort(key=lambda x: x["pct_from_high"], reverse=True)
    near_low.sort(key=lambda x: x["pct_from_low"])
    
    return {
        "near_52w_high": near_high[:10],
        "near_52w_low": near_low[:10],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/unusual-volume")
async def get_unusual_volume():
    """
    Returnează acțiunile cu volum neobișnuit (mult peste media)
    """
    db = await get_database()
    stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
    
    unusual = []
    
    # Calculează media volumului pentru fiecare acțiune
    for stock in stocks:
        volume = stock.get("volume", 0)
        avg_volume = stock.get("avg_volume_20d", 0)  # Presupunem că avem această valoare
        
        if not avg_volume:
            # Fallback: calculăm o medie simplă din toate acțiunile
            avg_volume = sum(s.get("volume", 0) for s in stocks) / len(stocks) if stocks else 1
        
        if volume and avg_volume and volume > 0:
            volume_ratio = volume / avg_volume
            
            # Volum de cel puțin 2x media
            if volume_ratio >= 2:
                unusual.append({
                    "symbol": stock.get("symbol"),
                    "name": stock.get("name"),
                    "price": stock.get("price"),
                    "change_percent": stock.get("change_percent"),
                    "volume": volume,
                    "avg_volume": round(avg_volume),
                    "volume_ratio": round(volume_ratio, 2),
                    "alert_level": "🔥 Foarte mare" if volume_ratio >= 5 else "📈 Mare" if volume_ratio >= 3 else "⚡ Peste medie"
                })
    
    # Sort by volume ratio descending
    unusual.sort(key=lambda x: x["volume_ratio"], reverse=True)
    
    return {
        "unusual_volume": unusual[:15],
        "total_found": len(unusual),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/bvb/filter-by-sector")
async def filter_stocks_by_sector(sector: Optional[str] = None):
    """
    Filtrează acțiunile BVB pe sector
    """
    db = await get_database()
    
    # Get all stocks
    query = {}
    if sector and sector != "all":
        query["sector"] = {"$regex": sector, "$options": "i"}
    
    stocks = await db.stocks_bvb.find(query, {"_id": 0}).to_list(100)
    
    # Get unique sectors
    all_stocks = await db.stocks_bvb.find({}, {"_id": 0, "sector": 1}).to_list(100)
    sectors = list(set(s.get("sector") for s in all_stocks if s.get("sector")))
    sectors.sort()
    
    return {
        "stocks": stocks,
        "count": len(stocks),
        "available_sectors": sectors,
        "current_filter": sector
    }
