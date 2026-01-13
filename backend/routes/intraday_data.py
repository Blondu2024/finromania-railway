"""
Intraday Data API - Pentru grafice PRO
Suportă intervale: 1min, 5min, 15min, 30min, 1hour
DOAR pentru PRO users!
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import os
import logging
import httpx
from config.database import get_database
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/intraday", tags=["intraday-pro"])

EODHD_API_KEY = os.environ.get("EODHD_API_KEY")
EODHD_BASE_URL = "https://eodhd.com/api"

# Intervale suportate pentru intraday
VALID_INTERVALS = ["1m", "5m", "15m", "30m", "1h"]

@router.get("/bvb/{symbol}")
async def get_bvb_intraday(
    symbol: str,
    interval: str = Query(default="5m", description="1m, 5m, 15m, 30m, 1h"),
    user: dict = Depends(require_auth)
):
    """
    Get intraday data pentru acțiuni BVB
    DOAR pentru PRO users!
    """
    db = await get_database()
    
    # Check PRO subscription
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    subscription_level = user_data.get("subscription_level", "free") if user_data else "free"
    
    if subscription_level != "pro":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "pro_required",
                "message": "Grafice INTRADAY sunt disponibile doar pentru utilizatorii PRO.",
                "feature": "Intraday Charts",
                "intervals": "1min, 5min, 15min, 30min, 1hour",
                "upgrade_url": "/pricing"
            }
        )
    
    if interval not in VALID_INTERVALS:
        raise HTTPException(status_code=400, detail=f"Interval invalid. Folosește: {', '.join(VALID_INTERVALS)}")
    
    if not EODHD_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            # EODHD Intraday API
            url = f"{EODHD_BASE_URL}/intraday/{symbol}.RO"
            params = {
                "api_token": EODHD_API_KEY,
                "fmt": "json",
                "interval": interval,
                "from": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),  # Last 5 days
                "to": datetime.now().strftime("%Y-%m-%d")
            }
            
            response = await client.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Format pentru frontend (OHLCV)
                formatted_data = []
                for item in data:
                    formatted_data.append({
                        "timestamp": item.get("datetime"),
                        "date": item.get("datetime"),
                        "open": item.get("open"),
                        "high": item.get("high"),
                        "low": item.get("low"),
                        "close": item.get("close"),
                        "volume": item.get("volume", 0)
                    })
                
                return {
                    "symbol": symbol,
                    "interval": interval,
                    "data": formatted_data,
                    "count": len(formatted_data),
                    "source": "EODHD Intraday API",
                    "is_pro": True
                }
            else:
                logger.error(f"EODHD error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=502, detail="Failed to fetch intraday data")
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="API timeout")
    except Exception as e:
        logger.error(f"Intraday error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/global/{symbol}")
async def get_global_intraday(
    symbol: str,
    interval: str = Query(default="5m"),
    user: dict = Depends(require_auth)
):
    """
    Get intraday data pentru piețe globale (S&P, NASDAQ, etc.)
    DOAR pentru PRO users!
    """
    db = await get_database()
    
    # Check PRO
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    subscription_level = user_data.get("subscription_level", "free") if user_data else "free"
    
    if subscription_level != "pro":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "pro_required",
                "message": "Grafice INTRADAY pentru piețe globale sunt disponibile doar pentru PRO.",
                "upgrade_url": "/pricing"
            }
        )
    
    if interval not in VALID_INTERVALS:
        raise HTTPException(status_code=400, detail=f"Interval invalid")
    
    if not EODHD_API_KEY:
        raise HTTPException(status_code=500, detail="API not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{EODHD_BASE_URL}/intraday/{symbol}"
            params = {
                "api_token": EODHD_API_KEY,
                "fmt": "json",
                "interval": interval,
                "from": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                "to": datetime.now().strftime("%Y-%m-%d")
            }
            
            response = await client.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                formatted_data = []
                for item in data:
                    formatted_data.append({
                        "timestamp": item.get("datetime"),
                        "date": item.get("datetime"),
                        "open": item.get("open"),
                        "high": item.get("high"),
                        "low": item.get("low"),
                        "close": item.get("close"),
                        "volume": item.get("volume", 0)
                    })
                
                return {
                    "symbol": symbol,
                    "interval": interval,
                    "data": formatted_data,
                    "count": len(formatted_data),
                    "source": "EODHD Intraday",
                    "is_pro": True
                }
            else:
                raise HTTPException(status_code=502, detail="Failed to fetch intraday")
                
    except Exception as e:
        logger.error(f"Global intraday error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
