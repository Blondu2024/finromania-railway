"""Stock Screener API pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import logging

from config.database import get_database
from routes.auth import require_auth

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


class ProScreenerFilters(BaseModel):
    """PRO Screener with fundamental indicators"""
    # Basic filters
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    
    # Fundamental filters (PRO)
    min_pe: Optional[float] = None
    max_pe: Optional[float] = None
    min_pb: Optional[float] = None  # Price to Book
    max_pb: Optional[float] = None
    min_roe: Optional[float] = None  # Return on Equity %
    max_roe: Optional[float] = None
    min_eps: Optional[float] = None  # Earnings per Share
    max_eps: Optional[float] = None
    min_dividend_yield: Optional[float] = None
    max_dividend_yield: Optional[float] = None
    min_debt_equity: Optional[float] = None  # Debt to Equity ratio
    max_debt_equity: Optional[float] = None
    min_profit_margin: Optional[float] = None  # Profit Margin %
    max_profit_margin: Optional[float] = None
    
    # Sort
    sort_by: str = "pe_ratio"
    sort_order: str = "asc"
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


# ============================================
# PRO SCREENER - Fundamental Indicators
# ============================================

# Mock fundamental data for BVB stocks (in production, this comes from EODHD API)
FUNDAMENTAL_DATA = {
    "TLV": {"pe_ratio": 5.2, "pb_ratio": 0.8, "roe": 15.4, "eps": 1.85, "dividend_yield": 8.2, "debt_equity": 0.45, "profit_margin": 22.1, "ev": 12500000000},
    "SNP": {"pe_ratio": 4.8, "pb_ratio": 0.6, "roe": 18.2, "eps": 0.42, "dividend_yield": 10.5, "debt_equity": 0.32, "profit_margin": 18.5, "ev": 8900000000},
    "BRD": {"pe_ratio": 6.1, "pb_ratio": 1.1, "roe": 14.8, "eps": 2.45, "dividend_yield": 7.8, "debt_equity": 0.55, "profit_margin": 25.3, "ev": 9800000000},
    "FP": {"pe_ratio": 8.5, "pb_ratio": 0.9, "roe": 10.2, "eps": 1.12, "dividend_yield": 6.5, "debt_equity": 0.28, "profit_margin": 15.2, "ev": 15200000000},
    "TGN": {"pe_ratio": 7.2, "pb_ratio": 1.2, "roe": 12.5, "eps": 45.5, "dividend_yield": 5.8, "debt_equity": 0.18, "profit_margin": 28.4, "ev": 7500000000},
    "DIGI": {"pe_ratio": 12.5, "pb_ratio": 2.1, "roe": 22.4, "eps": 3.85, "dividend_yield": 2.1, "debt_equity": 0.82, "profit_margin": 12.8, "ev": 11200000000},
    "H2O": {"pe_ratio": 18.2, "pb_ratio": 3.5, "roe": 8.5, "eps": 0.28, "dividend_yield": 1.2, "debt_equity": 0.65, "profit_margin": 8.5, "ev": 850000000},
    "ONE": {"pe_ratio": 15.8, "pb_ratio": 2.8, "roe": 18.5, "eps": 0.52, "dividend_yield": 0, "debt_equity": 0.95, "profit_margin": 10.2, "ev": 1200000000},
    "M": {"pe_ratio": 22.5, "pb_ratio": 4.2, "roe": 25.8, "eps": 0.15, "dividend_yield": 0, "debt_equity": 0.42, "profit_margin": 5.8, "ev": 2100000000},
    "SNG": {"pe_ratio": 3.8, "pb_ratio": 0.5, "roe": 12.8, "eps": 0.95, "dividend_yield": 12.5, "debt_equity": 0.22, "profit_margin": 32.5, "ev": 4500000000},
    "SNN": {"pe_ratio": 9.5, "pb_ratio": 1.4, "roe": 11.2, "eps": 1.25, "dividend_yield": 4.5, "debt_equity": 0.35, "profit_margin": 18.2, "ev": 6800000000},
    "TEL": {"pe_ratio": 11.2, "pb_ratio": 1.8, "roe": 9.8, "eps": 0.85, "dividend_yield": 5.2, "debt_equity": 0.48, "profit_margin": 14.5, "ev": 3200000000},
    "WINE": {"pe_ratio": 14.5, "pb_ratio": 2.2, "roe": 8.2, "eps": 0.18, "dividend_yield": 3.8, "debt_equity": 0.28, "profit_margin": 12.2, "ev": 180000000},
    "AQ": {"pe_ratio": 25.8, "pb_ratio": 5.5, "roe": 28.5, "eps": 0.08, "dividend_yield": 0, "debt_equity": 0.15, "profit_margin": 8.5, "ev": 950000000},
    "ALR": {"pe_ratio": 8.8, "pb_ratio": 1.2, "roe": 14.2, "eps": 0.65, "dividend_yield": 4.2, "debt_equity": 0.52, "profit_margin": 15.8, "ev": 420000000},
    "COTE": {"pe_ratio": 6.5, "pb_ratio": 0.9, "roe": 16.5, "eps": 1.42, "dividend_yield": 6.8, "debt_equity": 0.38, "profit_margin": 22.5, "ev": 580000000},
    "EL": {"pe_ratio": 10.2, "pb_ratio": 1.5, "roe": 13.8, "eps": 0.52, "dividend_yield": 3.5, "debt_equity": 0.45, "profit_margin": 16.2, "ev": 2800000000},
    "ROCE": {"pe_ratio": 7.8, "pb_ratio": 1.1, "roe": 15.2, "eps": 0.38, "dividend_yield": 5.5, "debt_equity": 0.32, "profit_margin": 19.8, "ev": 320000000},
    "TRP": {"pe_ratio": 4.2, "pb_ratio": 0.7, "roe": 18.8, "eps": 0.28, "dividend_yield": 9.5, "debt_equity": 0.25, "profit_margin": 28.5, "ev": 1100000000},
    "BVB": {"pe_ratio": 16.5, "pb_ratio": 2.5, "roe": 12.5, "eps": 1.85, "dividend_yield": 4.8, "debt_equity": 0.12, "profit_margin": 35.2, "ev": 180000000},
}


@router.get("/pro/fundamentals")
async def get_pro_screener_data(user: dict = Depends(require_auth)):
    """
    PRO Feature: Get stocks with fundamental indicators
    Requires PRO subscription
    """
    # Check PRO subscription
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(
            status_code=403,
            detail="Această funcție necesită abonament PRO. Upgrade pentru acces la indicatori fundamentali."
        )
    
    try:
        db = await get_database()
        stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        
        # Enrich with fundamental data
        enriched = []
        for stock in stocks:
            symbol = stock.get("symbol", "")
            fundamentals = FUNDAMENTAL_DATA.get(symbol, {})
            
            enriched.append({
                **stock,
                "pe_ratio": fundamentals.get("pe_ratio"),
                "pb_ratio": fundamentals.get("pb_ratio"),
                "roe": fundamentals.get("roe"),
                "eps": fundamentals.get("eps"),
                "dividend_yield": fundamentals.get("dividend_yield"),
                "debt_equity": fundamentals.get("debt_equity"),
                "profit_margin": fundamentals.get("profit_margin"),
                "ev": fundamentals.get("ev"),
            })
        
        return {
            "stocks": enriched,
            "count": len(enriched),
            "is_pro": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in PRO screener: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pro/filter")
async def run_pro_screener(filters: ProScreenerFilters, user: dict = Depends(require_auth)):
    """
    PRO Feature: Advanced screening with fundamental filters
    """
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(
            status_code=403,
            detail="Această funcție necesită abonament PRO."
        )
    
    try:
        db = await get_database()
        stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        
        # Enrich and filter
        results = []
        for stock in stocks:
            symbol = stock.get("symbol", "")
            fundamentals = FUNDAMENTAL_DATA.get(symbol, {})
            
            # Skip if no fundamental data
            if not fundamentals:
                continue
            
            enriched = {
                **stock,
                "pe_ratio": fundamentals.get("pe_ratio"),
                "pb_ratio": fundamentals.get("pb_ratio"),
                "roe": fundamentals.get("roe"),
                "eps": fundamentals.get("eps"),
                "dividend_yield": fundamentals.get("dividend_yield"),
                "debt_equity": fundamentals.get("debt_equity"),
                "profit_margin": fundamentals.get("profit_margin"),
                "ev": fundamentals.get("ev"),
            }
            
            # Apply filters
            if filters.min_price and stock.get("price", 0) < filters.min_price:
                continue
            if filters.max_price and stock.get("price", 0) > filters.max_price:
                continue
            if filters.min_pe and fundamentals.get("pe_ratio", 999) < filters.min_pe:
                continue
            if filters.max_pe and fundamentals.get("pe_ratio", 0) > filters.max_pe:
                continue
            if filters.min_pb and fundamentals.get("pb_ratio", 999) < filters.min_pb:
                continue
            if filters.max_pb and fundamentals.get("pb_ratio", 0) > filters.max_pb:
                continue
            if filters.min_roe and fundamentals.get("roe", 0) < filters.min_roe:
                continue
            if filters.max_roe and fundamentals.get("roe", 999) > filters.max_roe:
                continue
            if filters.min_eps and fundamentals.get("eps", -999) < filters.min_eps:
                continue
            if filters.max_eps and fundamentals.get("eps", 999) > filters.max_eps:
                continue
            if filters.min_dividend_yield and fundamentals.get("dividend_yield", 0) < filters.min_dividend_yield:
                continue
            if filters.max_dividend_yield and fundamentals.get("dividend_yield", 999) > filters.max_dividend_yield:
                continue
            if filters.min_debt_equity and fundamentals.get("debt_equity", 999) < filters.min_debt_equity:
                continue
            if filters.max_debt_equity and fundamentals.get("debt_equity", 0) > filters.max_debt_equity:
                continue
            if filters.min_profit_margin and fundamentals.get("profit_margin", 0) < filters.min_profit_margin:
                continue
            if filters.max_profit_margin and fundamentals.get("profit_margin", 999) > filters.max_profit_margin:
                continue
            
            results.append(enriched)
        
        # Sort
        sort_key = filters.sort_by
        reverse = filters.sort_order == "desc"
        results.sort(key=lambda x: x.get(sort_key, 0) or 0, reverse=reverse)
        
        # Limit
        results = results[:filters.limit]
        
        return {
            "results": results,
            "count": len(results),
            "filters_applied": filters.dict(exclude_none=True),
            "is_pro": True
        }
        
    except Exception as e:
        logger.error(f"Error in PRO filter: {e}")
        raise HTTPException(status_code=500, detail=str(e))
