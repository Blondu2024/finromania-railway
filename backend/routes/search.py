"""Search routes pentru FinRomania"""
from fastapi import APIRouter, Query
from typing import List, Optional
from config.database import get_database

router = APIRouter(prefix="/search", tags=["search"])

@router.get("")
async def search(
    q: str = Query(..., min_length=2, description="Search query"),
    type: Optional[str] = Query(default=None, description="Filter by type: stocks, news, all")
):
    """Search stocks and news"""
    db = await get_database()
    results = {
        "query": q,
        "stocks": [],
        "news": []
    }
    
    # Search stocks
    if type in [None, "all", "stocks"]:
        # BVB stocks
        bvb = await db.stocks_bvb.find(
            {"$or": [
                {"symbol": {"$regex": q, "$options": "i"}},
                {"name": {"$regex": q, "$options": "i"}}
            ]},
            {"_id": 0}
        ).limit(5).to_list(5)
        
        for stock in bvb:
            stock["stock_type"] = "bvb"
            results["stocks"].append(stock)
        
        # Global indices
        global_idx = await db.stocks_global.find(
            {"$or": [
                {"symbol": {"$regex": q, "$options": "i"}},
                {"name": {"$regex": q, "$options": "i"}}
            ]},
            {"_id": 0}
        ).limit(5).to_list(5)
        
        for idx in global_idx:
            idx["stock_type"] = "global"
            results["stocks"].append(idx)
    
    # Search news
    if type in [None, "all", "news"]:
        news = await db.articles.find(
            {"$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}}
            ]},
            {"_id": 0}
        ).sort("published_at", -1).limit(10).to_list(10)
        
        results["news"] = news
    
    results["total"] = len(results["stocks"]) + len(results["news"])
    
    return results
