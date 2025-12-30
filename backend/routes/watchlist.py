"""Watchlist & Alerts API pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
import logging

from config.database import get_database
from routes.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


# ============================================
# MODELS
# ============================================

class WatchlistItem(BaseModel):
    symbol: str
    added_at: Optional[str] = None
    notes: Optional[str] = None
    alert_above: Optional[float] = None  # Alert when price goes above
    alert_below: Optional[float] = None  # Alert when price goes below


class WatchlistResponse(BaseModel):
    items: List[dict]
    count: int


class PriceAlert(BaseModel):
    symbol: str
    alert_type: str  # "above" or "below"
    target_price: float
    note: Optional[str] = None


class NotificationPreferences(BaseModel):
    # Market notifications
    market_open_close: bool = False
    market_big_moves: bool = False
    daily_summary: bool = False
    
    # Stock notifications (requires watchlist)
    watchlist_price_alerts: bool = True
    watchlist_big_moves: bool = True
    dividend_announcements: bool = False
    
    # News notifications
    important_news: bool = False
    watchlist_news: bool = False
    
    # Education notifications
    lesson_reminders: bool = False


# ============================================
# WATCHLIST ENDPOINTS
# ============================================

@router.get("")
async def get_watchlist(current_user: dict = Depends(get_current_user)):
    """Get user's watchlist with current stock data"""
    try:
        db = await get_database()
        
        # Get user's watchlist
        watchlist = await db.watchlists.find_one(
            {"user_id": current_user["id"]},
            {"_id": 0}
        )
        
        if not watchlist or not watchlist.get("items"):
            return {"items": [], "count": 0}
        
        # Get current stock data for each item
        symbols = [item["symbol"] for item in watchlist["items"]]
        stocks = await db.stocks_bvb.find(
            {"symbol": {"$in": symbols}},
            {"_id": 0}
        ).to_list(100)
        
        stock_map = {s["symbol"]: s for s in stocks}
        
        # Combine watchlist items with stock data
        enriched_items = []
        for item in watchlist["items"]:
            stock_data = stock_map.get(item["symbol"], {})
            enriched_items.append({
                **item,
                "price": stock_data.get("price"),
                "change_percent": stock_data.get("change_percent"),
                "name": stock_data.get("name"),
                "volume": stock_data.get("volume"),
                "sector": stock_data.get("sector"),
                # Check if alerts are triggered
                "alert_triggered_above": (
                    item.get("alert_above") and 
                    stock_data.get("price") and 
                    stock_data["price"] >= item["alert_above"]
                ),
                "alert_triggered_below": (
                    item.get("alert_below") and 
                    stock_data.get("price") and 
                    stock_data["price"] <= item["alert_below"]
                )
            })
        
        return {
            "items": enriched_items,
            "count": len(enriched_items)
        }
        
    except Exception as e:
        logger.error(f"Error fetching watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add")
async def add_to_watchlist(
    item: WatchlistItem,
    current_user: dict = Depends(get_current_user)
):
    """Add a stock to watchlist"""
    try:
        db = await get_database()
        
        # Verify stock exists
        stock = await db.stocks_bvb.find_one({"symbol": item.symbol.upper()})
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {item.symbol} not found")
        
        # Get or create watchlist
        watchlist = await db.watchlists.find_one({"user_id": current_user["id"]})
        
        new_item = {
            "symbol": item.symbol.upper(),
            "added_at": datetime.now(timezone.utc).isoformat(),
            "notes": item.notes,
            "alert_above": item.alert_above,
            "alert_below": item.alert_below
        }
        
        if watchlist:
            # Check if already in watchlist
            existing_symbols = [i["symbol"] for i in watchlist.get("items", [])]
            if item.symbol.upper() in existing_symbols:
                raise HTTPException(status_code=400, detail="Stock already in watchlist")
            
            # Add to existing watchlist
            await db.watchlists.update_one(
                {"user_id": current_user["id"]},
                {"$push": {"items": new_item}}
            )
        else:
            # Create new watchlist
            await db.watchlists.insert_one({
                "user_id": current_user["id"],
                "items": [new_item],
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        
        return {
            "success": True,
            "message": f"{item.symbol.upper()} added to watchlist",
            "item": new_item
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/remove/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a stock from watchlist"""
    try:
        db = await get_database()
        
        result = await db.watchlists.update_one(
            {"user_id": current_user["id"]},
            {"$pull": {"items": {"symbol": symbol.upper()}}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Stock not found in watchlist")
        
        return {
            "success": True,
            "message": f"{symbol.upper()} removed from watchlist"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{symbol}")
async def update_watchlist_item(
    symbol: str,
    item: WatchlistItem,
    current_user: dict = Depends(get_current_user)
):
    """Update alerts/notes for a watchlist item"""
    try:
        db = await get_database()
        
        result = await db.watchlists.update_one(
            {
                "user_id": current_user["id"],
                "items.symbol": symbol.upper()
            },
            {
                "$set": {
                    "items.$.notes": item.notes,
                    "items.$.alert_above": item.alert_above,
                    "items.$.alert_below": item.alert_below
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Stock not found in watchlist")
        
        return {
            "success": True,
            "message": f"Alerts updated for {symbol.upper()}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating watchlist item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# NOTIFICATION PREFERENCES ENDPOINTS
# ============================================

@router.get("/notifications/preferences")
async def get_notification_preferences(current_user: dict = Depends(get_current_user)):
    """Get user's notification preferences"""
    try:
        db = await get_database()
        
        prefs = await db.notification_preferences.find_one(
            {"user_id": current_user["id"]},
            {"_id": 0}
        )
        
        if not prefs:
            # Return defaults
            return NotificationPreferences().dict()
        
        return prefs.get("preferences", NotificationPreferences().dict())
        
    except Exception as e:
        logger.error(f"Error fetching notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/notifications/preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: dict = Depends(get_current_user)
):
    """Update user's notification preferences"""
    try:
        db = await get_database()
        
        await db.notification_preferences.update_one(
            {"user_id": current_user["id"]},
            {
                "$set": {
                    "preferences": preferences.dict(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Notification preferences updated",
            "preferences": preferences.dict()
        }
        
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# TRIGGERED ALERTS CHECK
# ============================================

@router.get("/alerts/check")
async def check_triggered_alerts(current_user: dict = Depends(get_current_user)):
    """Check if any price alerts have been triggered"""
    try:
        db = await get_database()
        
        watchlist = await db.watchlists.find_one(
            {"user_id": current_user["id"]},
            {"_id": 0}
        )
        
        if not watchlist or not watchlist.get("items"):
            return {"triggered": [], "count": 0}
        
        triggered = []
        
        for item in watchlist["items"]:
            if not item.get("alert_above") and not item.get("alert_below"):
                continue
                
            stock = await db.stocks_bvb.find_one(
                {"symbol": item["symbol"]},
                {"_id": 0}
            )
            
            if not stock or not stock.get("price"):
                continue
            
            price = stock["price"]
            
            if item.get("alert_above") and price >= item["alert_above"]:
                triggered.append({
                    "symbol": item["symbol"],
                    "name": stock.get("name"),
                    "type": "above",
                    "target": item["alert_above"],
                    "current_price": price,
                    "message": f"🔔 {item['symbol']} a atins {price} RON (peste {item['alert_above']} RON)"
                })
            
            if item.get("alert_below") and price <= item["alert_below"]:
                triggered.append({
                    "symbol": item["symbol"],
                    "name": stock.get("name"),
                    "type": "below",
                    "target": item["alert_below"],
                    "current_price": price,
                    "message": f"🔔 {item['symbol']} a scăzut la {price} RON (sub {item['alert_below']} RON)"
                })
        
        return {
            "triggered": triggered,
            "count": len(triggered)
        }
        
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
