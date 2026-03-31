"""BVB Market Data - Indici, Top Movers, Statistici"""
from fastapi import APIRouter, HTTPException, Response
from typing import List, Dict, Optional
import logging
import yfinance as yf
from datetime import datetime, timezone
from config.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bvb", tags=["BVB Market"])

# BVB Indices - using Yahoo Finance symbols
BVB_INDICES = {
    "BET": {
        "symbol": "^BET",
        "name": "BET Index",
        "description": "Indicele principal BVB - Top 20 companii lichide",
        "components": 20
    },
    "BETTR": {
        "symbol": "^BETTR", 
        "name": "BET-TR Index",
        "description": "Total Return - Include dividendele reinvestite",
        "components": 20
    },
    "BETFI": {
        "symbol": "^BETFI",
        "name": "BET-FI Index", 
        "description": "Sectorul Financiar - Bănci și SIF-uri",
        "components": 5
    },
    "BETNG": {
        "symbol": "^BETNG",
        "name": "BET-NG Index",
        "description": "Sectorul Energie - Petrol, gaze, electricitate",
        "components": 10
    },
    "BETXT": {
        "symbol": "^BETXT",
        "name": "BET-XT Index",
        "description": "Extended - Top 25 cele mai lichide companii",
        "components": 25
    }
}

@router.get("/indices")
async def get_bvb_indices(response: Response):
    """Get all BVB indices with current values from TradingView (real-time data)"""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"

    try:
        from apis.tradingview_client import get_tradingview_client
        db = await get_database()

        tv_client = get_tradingview_client()
        indices = await tv_client.get_bvb_indices()

        if indices:
            # Cache successful result in MongoDB
            await db.bvb_indices_cache.replace_one(
                {"_id": "latest"},
                {"_id": "latest", "indices": indices, "updated_at": datetime.now(timezone.utc).isoformat(), "source": "TradingView"},
                upsert=True
            )
            return {
                "indices": indices,
                "source": "TradingView",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

        # Fallback: last successful data from MongoDB
        cached = await db.bvb_indices_cache.find_one({"_id": "latest"})
        if cached:
            logger.warning("TradingView unavailable, serving cached indices")
            return {
                "indices": cached["indices"],
                "source": "cache",
                "updated_at": cached.get("updated_at"),
                "is_cached": True
            }

        logger.error("No index data available (TradingView failed, no cache)")
        raise HTTPException(status_code=503, detail="Index data temporarily unavailable")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching BVB indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-movers")
async def get_top_movers(response: Response):
    """Get top gainers, losers, and most traded stocks"""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    
    try:
        db = await get_database()
        
        # Get all BVB stocks from database
        stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        
        if not stocks:
            return {
                "gainers": [],
                "losers": [],
                "most_traded": [],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        
        # Sort for top gainers (highest positive change)
        gainers = sorted(
            [s for s in stocks if s.get("change_percent", 0) > 0],
            key=lambda x: x.get("change_percent", 0),
            reverse=True
        )[:5]
        
        # Sort for top losers (most negative change)
        losers = sorted(
            [s for s in stocks if s.get("change_percent", 0) < 0],
            key=lambda x: x.get("change_percent", 0)
        )[:5]
        
        # Sort for most traded (highest volume)
        most_traded = sorted(
            stocks,
            key=lambda x: x.get("volume", 0),
            reverse=True
        )[:5]
        
        return {
            "gainers": gainers,
            "losers": losers,
            "most_traded": most_traded,
            "total_stocks": len(stocks),
            "market_sentiment": "bullish" if len(gainers) > len(losers) else "bearish" if len(losers) > len(gainers) else "neutral",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching top movers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-stats")
async def get_market_stats():
    """Get overall BVB market statistics"""
    try:
        db = await get_database()
        stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        
        if not stocks:
            return {"error": "No stocks data available"}
        
        # Calculate statistics
        total_volume = sum(s.get("volume", 0) for s in stocks)
        total_market_cap = sum(s.get("market_cap", 0) for s in stocks if s.get("market_cap"))
        
        gainers = [s for s in stocks if s.get("change_percent", 0) > 0]
        losers = [s for s in stocks if s.get("change_percent", 0) < 0]
        unchanged = [s for s in stocks if s.get("change_percent", 0) == 0]
        
        avg_change = sum(s.get("change_percent", 0) for s in stocks) / len(stocks) if stocks else 0
        
        # Best and worst performers
        best = max(stocks, key=lambda x: x.get("change_percent", 0)) if stocks else None
        worst = min(stocks, key=lambda x: x.get("change_percent", 0)) if stocks else None
        
        return {
            "total_stocks": len(stocks),
            "gainers_count": len(gainers),
            "losers_count": len(losers),
            "unchanged_count": len(unchanged),
            "average_change_percent": round(avg_change, 2),
            "total_volume": total_volume,
            "total_market_cap": total_market_cap,
            "best_performer": {
                "symbol": best.get("symbol"),
                "name": best.get("name"),
                "change_percent": best.get("change_percent")
            } if best else None,
            "worst_performer": {
                "symbol": worst.get("symbol"),
                "name": worst.get("name"),
                "change_percent": worst.get("change_percent")
            } if worst else None,
            "market_sentiment": "bullish" if avg_change > 0.5 else "bearish" if avg_change < -0.5 else "neutral",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching market stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sectors")
async def get_sector_performance():
    """Get performance breakdown by sector"""
    try:
        db = await get_database()
        stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        
        if not stocks:
            return {"sectors": []}
        
        # Group by sector
        sectors = {}
        for stock in stocks:
            sector = stock.get("sector", "Altele")
            if sector not in sectors:
                sectors[sector] = {
                    "name": sector,
                    "stocks": [],
                    "total_change": 0,
                    "stock_count": 0
                }
            sectors[sector]["stocks"].append(stock.get("symbol"))
            sectors[sector]["total_change"] += stock.get("change_percent", 0)
            sectors[sector]["stock_count"] += 1
        
        # Calculate averages
        sector_list = []
        for name, data in sectors.items():
            avg_change = data["total_change"] / data["stock_count"] if data["stock_count"] > 0 else 0
            sector_list.append({
                "name": name,
                "stocks": data["stocks"],
                "stock_count": data["stock_count"],
                "average_change_percent": round(avg_change, 2),
                "performance": "up" if avg_change > 0 else "down" if avg_change < 0 else "flat"
            })
        
        # Sort by performance
        sector_list.sort(key=lambda x: x["average_change_percent"], reverse=True)
        
        return {
            "sectors": sector_list,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching sector performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock/{symbol}/fundamentals")
async def get_stock_fundamentals(symbol: str):
    """Get fundamental data for a specific stock"""
    try:
        db = await get_database()
        stock = await db.stocks_bvb.find_one({"symbol": symbol.upper()}, {"_id": 0})
        
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
        
        # Try to get additional data from yfinance
        fundamentals = {
            "symbol": stock.get("symbol"),
            "name": stock.get("name"),
            "sector": stock.get("sector"),
            "price": stock.get("price"),
            "change_percent": stock.get("change_percent"),
            # Price metrics
            "open": stock.get("open"),
            "high": stock.get("high"),
            "low": stock.get("low"),
            "previous_close": stock.get("previous_close"),
            "volume": stock.get("volume"),
            # Fundamental metrics (if available)
            "pe_ratio": stock.get("pe_ratio"),
            "pb_ratio": stock.get("pb_ratio"),
            "eps": stock.get("eps"),
            "market_cap": stock.get("market_cap"),
            "dividend_yield": stock.get("dividend_yield"),
            "week_52_high": stock.get("week_52_high"),
            "week_52_low": stock.get("week_52_low"),
            "avg_volume_30d": stock.get("avg_volume_30d"),
            "beta": stock.get("beta"),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Calculate additional metrics
        if fundamentals["high"] and fundamentals["low"]:
            fundamentals["day_range"] = f"{fundamentals['low']} - {fundamentals['high']}"
        
        if fundamentals["week_52_high"] and fundamentals["week_52_low"]:
            fundamentals["year_range"] = f"{fundamentals['week_52_low']} - {fundamentals['week_52_high']}"
        
        return fundamentals
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
