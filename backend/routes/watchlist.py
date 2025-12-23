"""Watchlist routes pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from config.database import get_database
from routes.auth import require_auth

router = APIRouter(prefix="/watchlist", tags=["watchlist"])

class WatchlistItem(BaseModel):
    symbol: str
    type: str  # 'bvb' or 'global'
    name: Optional[str] = None
    target_price: Optional[float] = None
    alert_enabled: bool = False

class WatchlistResponse(BaseModel):
    id: str
    user_id: str
    symbol: str
    type: str
    name: Optional[str] = None
    target_price: Optional[float] = None
    alert_enabled: bool = False
    created_at: str

@router.get("", response_model=List[WatchlistResponse])
async def get_watchlist(user: dict = Depends(require_auth)):
    """Get user's watchlist"""
    db = await get_database()
    items = await db.watchlist.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).to_list(100)
    return items

@router.post("", response_model=WatchlistResponse)
async def add_to_watchlist(item: WatchlistItem, user: dict = Depends(require_auth)):
    """Add item to watchlist"""
    db = await get_database()
    
    # Check if already exists
    existing = await db.watchlist.find_one({
        "user_id": user["user_id"],
        "symbol": item.symbol,
        "type": item.type
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Item already in watchlist")
    
    watchlist_item = {
        "id": f"wl_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "symbol": item.symbol,
        "type": item.type,
        "name": item.name,
        "target_price": item.target_price,
        "alert_enabled": item.alert_enabled,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.watchlist.insert_one(watchlist_item)
    return watchlist_item

@router.delete("/{item_id}")
async def remove_from_watchlist(item_id: str, user: dict = Depends(require_auth)):
    """Remove item from watchlist"""
    db = await get_database()
    result = await db.watchlist.delete_one({
        "id": item_id,
        "user_id": user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item removed from watchlist"}

@router.put("/{item_id}/alert")
async def update_alert(item_id: str, target_price: float, user: dict = Depends(require_auth)):
    """Update price alert"""
    db = await get_database()
    result = await db.watchlist.update_one(
        {"id": item_id, "user_id": user["user_id"]},
        {"$set": {
            "target_price": target_price,
            "alert_enabled": True
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Alert updated"}
