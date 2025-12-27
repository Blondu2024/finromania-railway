"""Stock Screener API pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import logging

from config.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/screener", tags=["Stock Screener"])


# ============================================
# MODELS
# ============================================

class ScreenerFilters(BaseModel):
    # Price filters
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    
    # Change filters
    min_change: Optional[float] = None
    max_change: Optional[float] = None
    
    # Volume filters
    min_volume: Optional[int] = None
    max_volume: Optional[int] = None
    
    # Sector filter
    sectors: Optional[List[str]] = None
    
    # Performance filters
    gainers_only: bool = False
    losers_only: bool = False
    
    # Sort
    sort_by: str = "change_percent"  # price, change_percent, volume, symbol
    sort_order: str = "desc"  # asc, desc
    
    # Limit
    limit: int = 50


# ============================================
# PREDEFINED SCREENERS
# ============================================

PREDEFINED_SCREENERS = {
    "top_gainers": {
        "name": "🚀 Top Creșteri",
        "description": "Acțiunile cu cele mai mari creșteri azi",
        "filters": {
            "gainers_only": True,
            "sort_by": "change_percent",
            "sort_order": "desc",
            "limit": 10
        }
    },
    "top_losers": {
        "name": "📉 Top Scăderi",
        "description": "Acțiunile cu cele mai mari scăderi azi",
        "filters": {
            "losers_only": True,
            "sort_by": "change_percent",
            "sort_order": "asc",
            "limit": 10
        }
    },
    "most_active": {
        "name": "📊 Cele Mai Tranzacționate",
        "description": "Acțiunile cu cel mai mare volum",
        "filters": {
            "sort_by": "volume",
            "sort_order": "desc",
            "limit": 10
        }
    },
    "penny_stocks": {
        "name": "💰 Penny Stocks",
        "description": "Acțiuni sub 1 RON",
        "filters": {
            "max_price": 1.0,
            "sort_by": "change_percent",
            "sort_order": "desc",
            "limit": 20
        }
    },
    "blue_chips": {
        "name": "🏆 Blue Chips",
        "description": "Acțiuni mari (peste 50 RON)",
        "filters": {
            "min_price": 50.0,
            "sort_by": "volume",
            "sort_order": "desc",
            "limit": 10
        }
    },
    "high_volume_gainers": {
        "name": "⚡ Creșteri + Volum Mare",
        "description": "Acțiuni în creștere cu volum mare",
        "filters": {
            "gainers_only": True,
            "min_volume": 10000,
            "sort_by": "change_percent",
            "sort_order": "desc",
            "limit": 10
        }
    },
    "banking_sector": {
        "name": "🏦 Sector Bancar",
        "description": "Bănci și instituții financiare",
        "filters": {
            "sectors": ["Financiar", "Bănci"],
            "sort_by": "change_percent",
            "sort_order": "desc",
            "limit": 20
        }
    },
    "energy_sector": {
        "name": "⚡ Sector Energie",
        "description": "Petrol, gaze, electricitate",
        "filters": {
            "sectors": ["Energie", "Petrol & Gaze"],
            "sort_by": "change_percent",
            "sort_order": "desc",
            "limit": 20
        }
    }
}


# ============================================
# ENDPOINTS
# ============================================

@router.get("/predefined")
async def get_predefined_screeners():
    """Get list of predefined screeners"""
    return {
        "screeners": [
            {"id": k, **v}
            for k, v in PREDEFINED_SCREENERS.items()
        ],
        "count": len(PREDEFINED_SCREENERS)
    }


@router.get("/run/{screener_id}")
async def run_predefined_screener(screener_id: str):
    """Run a predefined screener"""
    if screener_id not in PREDEFINED_SCREENERS:
        raise HTTPException(status_code=404, detail=f"Screener '{screener_id}' not found")
    
    screener = PREDEFINED_SCREENERS[screener_id]
    filters = ScreenerFilters(**screener["filters"])
    
    results = await apply_screener_filters(filters)
    
    return {
        "screener": {
            "id": screener_id,
            "name": screener["name"],
            "description": screener["description"]
        },
        "results": results["stocks"],
        "count": results["count"],
        "filters_applied": screener["filters"]
    }


@router.post("/custom")
async def run_custom_screener(filters: ScreenerFilters):
    """Run a custom screener with user-defined filters"""
    results = await apply_screener_filters(filters)
    
    return {
        "results": results["stocks"],
        "count": results["count"],
        "filters_applied": filters.dict(exclude_none=True)
    }


@router.get("/sectors")
async def get_available_sectors():
    """Get list of available sectors for filtering"""
    try:
        db = await get_database()
        
        stocks = await db.stocks_bvb.find({}, {"_id": 0, "sector": 1}).to_list(100)
        sectors = list(set(s.get("sector") for s in stocks if s.get("sector")))
        sectors.sort()
        
        return {
            "sectors": sectors,
            "count": len(sectors)
        }
        
    except Exception as e:
        logger.error(f"Error fetching sectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick")
async def quick_screen(
    min_change: Optional[float] = Query(default=None),
    max_change: Optional[float] = Query(default=None),
    min_price: Optional[float] = Query(default=None),
    max_price: Optional[float] = Query(default=None),
    sector: Optional[str] = Query(default=None),
    sort_by: str = Query(default="change_percent"),
    limit: int = Query(default=20, le=100)
):
    """Quick screen with URL parameters"""
    filters = ScreenerFilters(
        min_change=min_change,
        max_change=max_change,
        min_price=min_price,
        max_price=max_price,
        sectors=[sector] if sector else None,
        sort_by=sort_by,
        limit=limit
    )
    
    results = await apply_screener_filters(filters)
    return results


# ============================================
# HELPER FUNCTIONS
# ============================================

async def apply_screener_filters(filters: ScreenerFilters) -> dict:
    """Apply filters to stock data"""
    try:
        db = await get_database()
        
        # Build MongoDB query
        query = {}
        
        # Price filters
        if filters.min_price is not None or filters.max_price is not None:
            query["price"] = {}
            if filters.min_price is not None:
                query["price"]["$gte"] = filters.min_price
            if filters.max_price is not None:
                query["price"]["$lte"] = filters.max_price
        
        # Change filters
        if filters.min_change is not None or filters.max_change is not None:
            query["change_percent"] = {}
            if filters.min_change is not None:
                query["change_percent"]["$gte"] = filters.min_change
            if filters.max_change is not None:
                query["change_percent"]["$lte"] = filters.max_change
        
        # Gainers/Losers only
        if filters.gainers_only:
            query["change_percent"] = {"$gt": 0}
        elif filters.losers_only:
            query["change_percent"] = {"$lt": 0}
        
        # Volume filters
        if filters.min_volume is not None or filters.max_volume is not None:
            query["volume"] = {}
            if filters.min_volume is not None:
                query["volume"]["$gte"] = filters.min_volume
            if filters.max_volume is not None:
                query["volume"]["$lte"] = filters.max_volume
        
        # Sector filter
        if filters.sectors:
            query["sector"] = {"$in": filters.sectors}
        
        # Execute query
        stocks = await db.stocks_bvb.find(query, {"_id": 0}).to_list(1000)
        
        # Sort
        sort_key = filters.sort_by
        reverse = filters.sort_order == "desc"
        stocks.sort(key=lambda x: x.get(sort_key, 0) or 0, reverse=reverse)
        
        # Limit
        stocks = stocks[:filters.limit]
        
        return {
            "stocks": stocks,
            "count": len(stocks),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error applying screener filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_market_screening_stats():
    """Get overall market stats for screening overview"""
    try:
        db = await get_database()
        
        stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        
        if not stocks:
            return {"error": "No stocks data"}
        
        gainers = [s for s in stocks if s.get("change_percent", 0) > 0]
        losers = [s for s in stocks if s.get("change_percent", 0) < 0]
        unchanged = [s for s in stocks if s.get("change_percent", 0) == 0]
        
        prices = [s.get("price", 0) for s in stocks if s.get("price")]
        changes = [s.get("change_percent", 0) for s in stocks]
        volumes = [s.get("volume", 0) for s in stocks if s.get("volume")]
        
        return {
            "total_stocks": len(stocks),
            "gainers": len(gainers),
            "losers": len(losers),
            "unchanged": len(unchanged),
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "avg": sum(prices) / len(prices) if prices else 0
            },
            "change_range": {
                "min": min(changes) if changes else 0,
                "max": max(changes) if changes else 0,
                "avg": sum(changes) / len(changes) if changes else 0
            },
            "volume_range": {
                "min": min(volumes) if volumes else 0,
                "max": max(volumes) if volumes else 0,
                "total": sum(volumes) if volumes else 0
            },
            "market_sentiment": "bullish" if len(gainers) > len(losers) else "bearish" if len(losers) > len(gainers) else "neutral"
        }
        
    except Exception as e:
        logger.error(f"Error fetching screening stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
