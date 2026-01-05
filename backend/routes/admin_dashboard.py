"""
Advanced Admin Dashboard API pentru FinRomania
Tracking complet: utilizatori, sesiuni, pagini, AI usage cu limite
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from config.database import get_database
from routes.auth import require_auth
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/v2", tags=["admin-v2"])

# ============================================
# CONSTANTS
# ============================================
AI_MONTHLY_LIMIT = 10  # Credite AI pe lună per user
ADMIN_EMAILS = ["tanasecristian2007@gmail.com", "contact@finromania.ro"]

# ============================================
# AUTH MIDDLEWARE
# ============================================
async def require_admin(user: dict = Depends(require_auth)):
    """Require admin privileges"""
    if not user.get("is_admin") and user.get("email") not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ============================================
# MODELS
# ============================================
class PageViewEvent(BaseModel):
    page: str
    referrer: Optional[str] = None
    user_agent: Optional[str] = None

# ============================================
# TRACKING ENDPOINTS (Public - pentru tracking)
# ============================================
@router.post("/track/pageview")
async def track_pageview(event: PageViewEvent, request: Request, user: dict = Depends(require_auth)):
    """Track a page view"""
    db = await get_database()
    
    await db.page_views.insert_one({
        "user_id": user.get("user_id"),
        "email": user.get("email"),
        "page": event.page,
        "referrer": event.referrer,
        "user_agent": event.user_agent or request.headers.get("user-agent"),
        "ip": request.client.host if request.client else None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"status": "tracked"}

@router.post("/track/session-start")
async def track_session_start(request: Request, user: dict = Depends(require_auth)):
    """Track session start"""
    db = await get_database()
    
    session_id = f"sess_{user.get('user_id')}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    
    await db.sessions.insert_one({
        "session_id": session_id,
        "user_id": user.get("user_id"),
        "email": user.get("email"),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "ended_at": None,
        "duration_seconds": 0,
        "pages_visited": 0,
        "is_active": True,
        "user_agent": request.headers.get("user-agent"),
        "ip": request.client.host if request.client else None
    })
    
    return {"session_id": session_id}

@router.post("/track/session-end/{session_id}")
async def track_session_end(session_id: str, pages_visited: int = 0):
    """Track session end"""
    db = await get_database()
    
    session = await db.sessions.find_one({"session_id": session_id})
    if session:
        started = datetime.fromisoformat(session["started_at"].replace("Z", "+00:00"))
        duration = (datetime.now(timezone.utc) - started).total_seconds()
        
        await db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": int(duration),
                "pages_visited": pages_visited,
                "is_active": False
            }}
        )
    
    return {"status": "ended"}

# ============================================
# ADMIN DASHBOARD ENDPOINTS
# ============================================

@router.get("/overview")
async def get_dashboard_overview(user: dict = Depends(require_admin)):
    """Get complete dashboard overview"""
    db = await get_database()
    
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # ===== USER STATS =====
    total_users = await db.users.count_documents({})
    users_today = await db.users.count_documents({"created_at": {"$gte": today_start.isoformat()}})
    users_week = await db.users.count_documents({"created_at": {"$gte": week_ago.isoformat()}})
    users_month = await db.users.count_documents({"created_at": {"$gte": month_ago.isoformat()}})
    
    # Active users (logged in last 24h)
    active_24h = await db.users.count_documents({"last_login": {"$gte": (now - timedelta(hours=24)).isoformat()}})
    active_7d = await db.users.count_documents({"last_login": {"$gte": week_ago.isoformat()}})
    active_30d = await db.users.count_documents({"last_login": {"$gte": month_ago.isoformat()}})
    
    # ===== SESSION STATS =====
    active_sessions = await db.sessions.count_documents({"is_active": True})
    sessions_today = await db.sessions.count_documents({"started_at": {"$gte": today_start.isoformat()}})
    
    # Average session duration (last 7 days)
    session_pipeline = [
        {"$match": {"started_at": {"$gte": week_ago.isoformat()}, "duration_seconds": {"$gt": 0}}},
        {"$group": {"_id": None, "avg_duration": {"$avg": "$duration_seconds"}, "total_sessions": {"$sum": 1}}}
    ]
    session_stats = await db.sessions.aggregate(session_pipeline).to_list(1)
    avg_session_duration = session_stats[0]["avg_duration"] if session_stats else 0
    total_sessions_week = session_stats[0]["total_sessions"] if session_stats else 0
    
    # ===== AI USAGE STATS =====
    ai_pipeline = [
        {"$group": {"_id": None, "total_credits": {"$sum": "$ai_credits_used"}}}
    ]
    ai_result = await db.users.aggregate(ai_pipeline).to_list(1)
    total_ai_credits = ai_result[0]["total_credits"] if ai_result else 0
    
    ai_today = await db.ai_usage_logs.count_documents({"timestamp": {"$gte": today_start.isoformat()}})
    ai_week = await db.ai_usage_logs.count_documents({"timestamp": {"$gte": week_ago.isoformat()}})
    
    # Users at/near limit
    users_at_limit = await db.users.count_documents({"ai_credits_used": {"$gte": AI_MONTHLY_LIMIT}})
    
    # ===== PAGE VIEWS =====
    pageviews_today = await db.page_views.count_documents({"timestamp": {"$gte": today_start.isoformat()}})
    pageviews_week = await db.page_views.count_documents({"timestamp": {"$gte": week_ago.isoformat()}})
    
    # ===== ENGAGEMENT =====
    total_watchlist = await db.watchlist.count_documents({})
    total_quiz_completions = await db.quiz_results.count_documents({})
    total_lessons_completed = await db.lesson_progress.count_documents({"completed": True})
    newsletter_subs = await db.newsletter.count_documents({})
    
    return {
        "users": {
            "total": total_users,
            "new_today": users_today,
            "new_this_week": users_week,
            "new_this_month": users_month,
            "active_24h": active_24h,
            "active_7d": active_7d,
            "active_30d": active_30d
        },
        "sessions": {
            "active_now": active_sessions,
            "today": sessions_today,
            "avg_duration_seconds": round(avg_session_duration, 1),
            "avg_duration_formatted": f"{int(avg_session_duration // 60)}m {int(avg_session_duration % 60)}s",
            "total_this_week": total_sessions_week
        },
        "ai_usage": {
            "total_credits_used": total_ai_credits,
            "requests_today": ai_today,
            "requests_this_week": ai_week,
            "monthly_limit_per_user": AI_MONTHLY_LIMIT,
            "users_at_limit": users_at_limit
        },
        "page_views": {
            "today": pageviews_today,
            "this_week": pageviews_week
        },
        "engagement": {
            "watchlist_items": total_watchlist,
            "quiz_completions": total_quiz_completions,
            "lessons_completed": total_lessons_completed,
            "newsletter_subscribers": newsletter_subs
        },
        "generated_at": now.isoformat()
    }

@router.get("/users/list")
async def get_users_list(
    user: dict = Depends(require_admin),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=25, ge=1, le=100),
    sort_by: str = Query(default="created_at", enum=["created_at", "last_login", "ai_credits_used", "total_logins"]),
    sort_order: str = Query(default="desc", enum=["asc", "desc"])
):
    """Get paginated users list with detailed info"""
    db = await get_database()
    
    sort_dir = -1 if sort_order == "desc" else 1
    
    users = await db.users.find(
        {},
        {"_id": 0, "password": 0}
    ).sort(sort_by, sort_dir).skip(skip).limit(limit).to_list(limit)
    
    # Add remaining AI credits
    for u in users:
        used = u.get("ai_credits_used", 0)
        u["ai_credits_remaining"] = max(0, AI_MONTHLY_LIMIT - used)
        u["ai_limit_reached"] = used >= AI_MONTHLY_LIMIT
    
    total = await db.users.count_documents({})
    
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@router.get("/users/{user_id}/details")
async def get_user_details(user_id: str, user: dict = Depends(require_admin)):
    """Get detailed info for a specific user"""
    db = await get_database()
    
    target_user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password": 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's sessions
    sessions = await db.sessions.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("started_at", -1).limit(10).to_list(10)
    
    # Get user's page views
    page_views = await db.page_views.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(50).to_list(50)
    
    # Get user's AI usage
    ai_logs = await db.ai_usage_logs.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(20).to_list(20)
    
    # Get user's watchlist
    watchlist = await db.watchlist.find_one({"user_id": user_id}, {"_id": 0})
    
    # Get user's lesson progress
    lessons = await db.lesson_progress.find(
        {"user_id": user_id},
        {"_id": 0}
    ).to_list(100)
    
    return {
        "user": target_user,
        "sessions": sessions,
        "recent_pages": page_views,
        "ai_usage_logs": ai_logs,
        "watchlist": watchlist.get("items", []) if watchlist else [],
        "lessons": lessons,
        "ai_credits_remaining": max(0, AI_MONTHLY_LIMIT - target_user.get("ai_credits_used", 0))
    }

@router.get("/analytics/pages")
async def get_page_analytics(
    user: dict = Depends(require_admin),
    days: int = Query(default=7, ge=1, le=30)
):
    """Get page view analytics"""
    db = await get_database()
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Top pages
    top_pages_pipeline = [
        {"$match": {"timestamp": {"$gte": start_date.isoformat()}}},
        {"$group": {"_id": "$page", "views": {"$sum": 1}, "unique_users": {"$addToSet": "$user_id"}}},
        {"$project": {"page": "$_id", "views": 1, "unique_users": {"$size": "$unique_users"}}},
        {"$sort": {"views": -1}},
        {"$limit": 20}
    ]
    top_pages = await db.page_views.aggregate(top_pages_pipeline).to_list(20)
    
    # Daily views
    daily_views = []
    for i in range(days):
        date = datetime.now(timezone.utc) - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        views = await db.page_views.count_documents({
            "timestamp": {"$gte": day_start.isoformat(), "$lt": day_end.isoformat()}
        })
        
        daily_views.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "views": views
        })
    
    return {
        "top_pages": top_pages,
        "daily_views": daily_views[::-1]
    }

@router.get("/analytics/ai-usage")
async def get_ai_usage_analytics(
    user: dict = Depends(require_admin),
    days: int = Query(default=7, ge=1, le=30)
):
    """Get AI usage analytics"""
    db = await get_database()
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Top AI users
    top_users = await db.users.find(
        {"ai_credits_used": {"$gt": 0}},
        {"_id": 0, "email": 1, "name": 1, "ai_credits_used": 1, "last_login": 1}
    ).sort("ai_credits_used", -1).limit(15).to_list(15)
    
    for u in top_users:
        u["ai_credits_remaining"] = max(0, AI_MONTHLY_LIMIT - u.get("ai_credits_used", 0))
        u["usage_percent"] = round((u.get("ai_credits_used", 0) / AI_MONTHLY_LIMIT) * 100, 1)
    
    # Usage by feature
    feature_pipeline = [
        {"$match": {"timestamp": {"$gte": start_date.isoformat()}}},
        {"$group": {"_id": "$feature", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    features = await db.ai_usage_logs.aggregate(feature_pipeline).to_list(10)
    
    # Daily usage
    daily_usage = []
    for i in range(days):
        date = datetime.now(timezone.utc) - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        count = await db.ai_usage_logs.count_documents({
            "timestamp": {"$gte": day_start.isoformat(), "$lt": day_end.isoformat()}
        })
        
        daily_usage.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "requests": count
        })
    
    return {
        "top_users": top_users,
        "usage_by_feature": [{"feature": f["_id"] or "unknown", "count": f["count"]} for f in features],
        "daily_usage": daily_usage[::-1],
        "monthly_limit": AI_MONTHLY_LIMIT
    }

@router.get("/analytics/growth")
async def get_growth_analytics(
    user: dict = Depends(require_admin),
    days: int = Query(default=30, ge=7, le=90)
):
    """Get user growth analytics"""
    db = await get_database()
    
    daily_data = []
    cumulative = 0
    
    # Get earliest user to find starting point
    earliest = await db.users.find_one({}, sort=[("created_at", 1)])
    if earliest:
        start_count = await db.users.count_documents({
            "created_at": {"$lt": (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()}
        })
        cumulative = start_count
    
    for i in range(days, -1, -1):
        date = datetime.now(timezone.utc) - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        new_users = await db.users.count_documents({
            "created_at": {"$gte": day_start.isoformat(), "$lt": day_end.isoformat()}
        })
        
        cumulative += new_users
        
        daily_data.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "new_users": new_users,
            "total_users": cumulative
        })
    
    return {
        "daily_growth": daily_data,
        "total_new_users": sum(d["new_users"] for d in daily_data),
        "current_total": cumulative
    }

@router.get("/realtime")
async def get_realtime_stats(user: dict = Depends(require_admin)):
    """Get real-time stats for live dashboard"""
    db = await get_database()
    
    now = datetime.now(timezone.utc)
    five_min_ago = now - timedelta(minutes=5)
    one_hour_ago = now - timedelta(hours=1)
    
    # Active sessions
    active_sessions = await db.sessions.count_documents({"is_active": True})
    
    # Recent page views (last 5 min)
    recent_views = await db.page_views.count_documents({
        "timestamp": {"$gte": five_min_ago.isoformat()}
    })
    
    # Recent AI requests (last hour)
    recent_ai = await db.ai_usage_logs.count_documents({
        "timestamp": {"$gte": one_hour_ago.isoformat()}
    })
    
    # Latest activities
    latest_logins = await db.login_logs.find(
        {},
        {"_id": 0, "email": 1, "timestamp": 1, "method": 1}
    ).sort("timestamp", -1).limit(5).to_list(5)
    
    latest_signups = await db.users.find(
        {},
        {"_id": 0, "email": 1, "name": 1, "created_at": 1}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "active_sessions": active_sessions,
        "page_views_5min": recent_views,
        "ai_requests_1hour": recent_ai,
        "latest_logins": latest_logins,
        "latest_signups": latest_signups,
        "timestamp": now.isoformat()
    }

# ============================================
# ADMIN ACTIONS
# ============================================

@router.post("/users/{user_id}/reset-ai-credits")
async def reset_user_ai_credits(user_id: str, user: dict = Depends(require_admin)):
    """Reset a user's AI credits to 0"""
    db = await get_database()
    
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"ai_credits_used": 0}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"AI credits reset for user {user_id}"}

@router.post("/users/{user_id}/set-ai-limit")
async def set_user_ai_limit(user_id: str, limit: int = Query(ge=0, le=1000), user: dict = Depends(require_admin)):
    """Set custom AI limit for a user"""
    db = await get_database()
    
    result = await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"custom_ai_limit": limit}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"AI limit set to {limit} for user {user_id}"}

@router.post("/users/{user_id}/toggle-admin")
async def toggle_admin(user_id: str, user: dict = Depends(require_admin)):
    """Toggle admin status for a user"""
    db = await get_database()
    
    target = await db.users.find_one({"user_id": user_id})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_status = not target.get("is_admin", False)
    
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"is_admin": new_status}}
    )
    
    return {"message": f"Admin status set to {new_status} for user {user_id}"}
