"""Admin routes pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from datetime import datetime, timezone, timedelta
from config.database import get_database
from routes.auth import require_auth

router = APIRouter(prefix="/admin", tags=["admin"])

async def require_admin(user: dict = Depends(require_auth)):
    """Require admin privileges"""
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.get("/stats")
async def get_stats(user: dict = Depends(require_admin)):
    """Get platform statistics"""
    db = await get_database()
    
    # Count totals
    total_users = await db.users.count_documents({})
    total_articles = await db.articles.count_documents({})
    total_watchlist = await db.watchlist.count_documents({})
    total_portfolio_txns = await db.portfolio_transactions.count_documents({})
    total_newsletter = await db.newsletter.count_documents({})
    
    # Today's stats
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_logins = await db.analytics.count_documents({
        "event": "login",
        "timestamp": {"$gte": today_start.isoformat()}
    })
    today_visits = await db.analytics.count_documents({
        "event": "visit",
        "timestamp": {"$gte": today_start.isoformat()}
    })
    
    # Last 7 days
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_users_week = await db.users.count_documents({
        "created_at": {"$gte": week_ago.isoformat()}
    })
    
    return {
        "totals": {
            "users": total_users,
            "articles": total_articles,
            "watchlist_items": total_watchlist,
            "portfolio_transactions": total_portfolio_txns,
            "newsletter_subscribers": total_newsletter
        },
        "today": {
            "logins": today_logins,
            "page_visits": today_visits
        },
        "last_7_days": {
            "new_users": new_users_week
        }
    }

@router.get("/users")
async def get_users(
    user: dict = Depends(require_admin),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100)
):
    """Get all users"""
    db = await get_database()
    users = await db.users.find(
        {},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.users.count_documents({})
    
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/analytics/visits")
async def get_visit_analytics(
    user: dict = Depends(require_admin),
    days: int = Query(default=7, ge=1, le=30)
):
    """Get visit analytics for last N days"""
    db = await get_database()
    
    results = []
    for i in range(days):
        date = datetime.now(timezone.utc) - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        visits = await db.analytics.count_documents({
            "event": "visit",
            "timestamp": {
                "$gte": day_start.isoformat(),
                "$lt": day_end.isoformat()
            }
        })
        
        logins = await db.analytics.count_documents({
            "event": "login",
            "timestamp": {
                "$gte": day_start.isoformat(),
                "$lt": day_end.isoformat()
            }
        })
        
        results.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "visits": visits,
            "logins": logins
        })
    
    return results[::-1]  # Reverse to show oldest first

@router.post("/make-admin/{user_id}")
async def make_admin(user_id: str, user: dict = Depends(require_admin)):
    """Make a user admin"""
    db = await get_database()
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"is_admin": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User {user_id} is now admin"}
