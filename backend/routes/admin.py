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



@router.get("/ai-stats")
async def get_ai_stats(
    user: dict = Depends(require_admin),
    days: int = Query(default=7, ge=1, le=30)
):
    """Get AI usage statistics"""
    db = await get_database()
    
    # Total AI credits used
    pipeline = [
        {"$group": {"_id": None, "total_credits": {"$sum": "$ai_credits_used"}}}
    ]
    result = await db.users.aggregate(pipeline).to_list(1)
    total_credits = result[0]["total_credits"] if result else 0
    
    # AI usage by day
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    daily_usage = []
    
    for i in range(days):
        date = datetime.now(timezone.utc) - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        count = await db.ai_usage_logs.count_documents({
            "timestamp": {
                "$gte": day_start.isoformat(),
                "$lt": day_end.isoformat()
            }
        })
        
        daily_usage.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "credits": count
        })
    
    # Top users by AI usage
    top_users = await db.users.find(
        {"ai_credits_used": {"$gt": 0}},
        {"_id": 0, "email": 1, "name": 1, "ai_credits_used": 1, "last_login": 1}
    ).sort("ai_credits_used", -1).limit(10).to_list(10)
    
    # Usage by feature
    feature_pipeline = [
        {"$group": {"_id": "$feature", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    features = await db.ai_usage_logs.aggregate(feature_pipeline).to_list(10)
    
    return {
        "total_credits_used": total_credits,
        "daily_usage": daily_usage[::-1],  # Oldest first
        "top_users": top_users,
        "usage_by_feature": [{"feature": f["_id"], "count": f["count"]} for f in features]
    }


@router.get("/login-history")
async def get_login_history(
    user: dict = Depends(require_admin),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200)
):
    """Get login history"""
    db = await get_database()
    
    logs = await db.login_logs.find(
        {},
        {"_id": 0}
    ).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.login_logs.count_documents({})
    
    return {
        "logs": logs,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/dashboard")
async def get_admin_dashboard(user: dict = Depends(require_admin)):
    """Get complete admin dashboard data"""
    db = await get_database()
    
    # Basic stats
    total_users = await db.users.count_documents({})
    total_logins = await db.login_logs.count_documents({})
    
    # AI stats
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$ai_credits_used"}}}
    ]
    ai_result = await db.users.aggregate(pipeline).to_list(1)
    total_ai_credits = ai_result[0]["total"] if ai_result else 0
    
    # Recent users
    recent_users = await db.users.find(
        {},
        {"_id": 0, "email": 1, "name": 1, "created_at": 1, "last_login": 1, 
         "total_logins": 1, "ai_credits_used": 1, "is_admin": 1}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    # Today's activity
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_logins = await db.login_logs.count_documents({
        "timestamp": {"$gte": today.isoformat()}
    })
    today_ai_usage = await db.ai_usage_logs.count_documents({
        "timestamp": {"$gte": today.isoformat()}
    })
    
    # Active trading companion interactions
    companion_total = await db.companion_interactions.count_documents({})
    
    return {
        "overview": {
            "total_users": total_users,
            "total_logins": total_logins,
            "total_ai_credits_used": total_ai_credits,
            "companion_interactions": companion_total
        },
        "today": {
            "logins": today_logins,
            "ai_requests": today_ai_usage
        },
        "recent_users": recent_users
    }
