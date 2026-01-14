"""BVB Stock Charts - Date istorice și intraday pentru grafice"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging
from apis.eodhd_client import get_eodhd_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/bvb", tags=["BVB Charts"])


@router.get("/chart/{symbol}")
async def get_bvb_stock_chart(
    symbol: str,
    period: str = Query("1mo", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y")
):
    """
    Get historical chart data for BVB stock
    Similar to /api/global/chart endpoint for consistency
    """
    try:
        eodhd = get_eodhd_client()
        
        # Map yfinance periods to EODHD periods
        period_mapping = {
            "1d": "1d",
            "5d": "1w",
            "1mo": "1m",
            "3mo": "3m",
            "6mo": "6m",
            "1y": "1y"
        }
        
        eodhd_period = period_mapping.get(period, "1m")
        
        # Get historical data from EODHD
        data = await eodhd.get_historical_data(symbol, period=eodhd_period)
        
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No chart data available for {symbol}"
            )
        
        # Calculate period change
        period_change = 0
        if len(data) >= 2:
            first_close = data[0]["close"]
            last_close = data[-1]["close"]
            if first_close > 0:
                period_change = ((last_close - first_close) / first_close) * 100
        
        return {
            "symbol": symbol,
            "period": period,
            "data": data,
            "data_points": len(data),
            "period_change": round(period_change, 2),
            "source": "eodhd",
            "exchange": "BVB"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching BVB chart for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intraday/{symbol}")
async def get_bvb_intraday(
    symbol: str,
    interval: str = Query("1h", description="Interval: 1m, 5m, 15m, 30m, 1h")
):
    """
    Get intraday chart data for BVB stock (PRO feature)
    """
    try:
        eodhd = get_eodhd_client()
        
        # EODHD supports: 1m, 5m, 1h
        # Map 15m, 30m to closest available
        interval_mapping = {
            "1m": "1m",
            "5m": "5m",
            "15m": "5m",  # Use 5m data for 15m
            "30m": "5m",  # Use 5m data for 30m
            "1h": "1h"
        }
        
        eodhd_interval = interval_mapping.get(interval, "1h")
        
        # Get intraday data from EODHD
        data = await eodhd.get_intraday_data(symbol, interval=eodhd_interval)
        
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No intraday data available for {symbol}"
            )
        
        # If we used 5m for 15m/30m, sample the data
        if interval in ["15m", "30m"] and eodhd_interval == "5m":
            step = 3 if interval == "15m" else 6
            data = data[::step]
        
        return {
            "symbol": symbol,
            "interval": interval,
            "data": data,
            "data_points": len(data),
            "source": "eodhd",
            "exchange": "BVB"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching BVB intraday for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
