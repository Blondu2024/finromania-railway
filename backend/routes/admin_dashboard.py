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


# ============================================
# IMPORT FIREBASE USERS (one-time migration)
# ============================================

@router.post("/import-firebase-users")
async def import_firebase_users(user: dict = Depends(require_admin)):
    """
    Importă toți userii din Firebase în MongoDB.
    - Userii care există deja (by email) sunt skipped
    - Userii noi primesc PRO gratuit până pe 5 iunie 2026
    - Returnează statistici detaliate
    """
    import uuid as _uuid
    from firebase_admin import auth as fb_auth

    db = await get_database()
    free_pro_deadline = datetime(2026, 6, 5, tzinfo=timezone.utc)

    stats = {"imported": 0, "skipped_existing": 0, "skipped_no_email": 0, "errors": 0, "users": []}

    try:
        # List ALL Firebase users (paginated automatically)
        page = fb_auth.list_users()
        while page:
            for fb_user in page.users:
                email = fb_user.email
                if not email:
                    stats["skipped_no_email"] += 1
                    continue

                # Check if already in MongoDB
                existing = await db.users.find_one({"email": email})
                if existing:
                    stats["skipped_existing"] += 1
                    stats["users"].append({"email": email, "status": "exists"})
                    continue

                # Create new user in MongoDB
                new_user = {
                    "user_id": str(_uuid.uuid4()),
                    "email": email,
                    "name": fb_user.display_name or email.split("@")[0],
                    "picture": fb_user.photo_url,
                    "firebase_uid": fb_user.uid,
                    "auth_provider": "firebase_google",
                    "created_at": datetime.fromtimestamp(fb_user.user_metadata.creation_timestamp / 1000, tz=timezone.utc).isoformat() if fb_user.user_metadata.creation_timestamp else datetime.now(timezone.utc).isoformat(),
                    "last_login": datetime.now(timezone.utc).isoformat(),
                    "is_admin": False,
                    "ai_credits_used": 0,
                    "total_logins": 0,
                    "is_early_adopter": True,
                    "subscription_level": "pro",
                    "subscription_expires_at": free_pro_deadline.isoformat(),
                    "subscription_source": "emergent_migration",
                    "unlocked_levels": ["beginner", "intermediate", "advanced"],
                    "experience_level": "advanced",
                    "daily_summary_enabled": True,
                    "migrated_from": "emergent",
                    "migrated_at": datetime.now(timezone.utc).isoformat()
                }

                try:
                    await db.users.insert_one(new_user)
                    stats["imported"] += 1
                    stats["users"].append({"email": email, "name": new_user["name"], "status": "imported"})
                    logger.info(f"✅ Imported Firebase user: {email}")
                except Exception as e:
                    stats["errors"] += 1
                    stats["users"].append({"email": email, "status": f"error: {e}"})
                    logger.error(f"Error importing {email}: {e}")

            # Next page
            page = page.get_next_page()

    except Exception as e:
        logger.error(f"Firebase list_users error: {e}")
        raise HTTPException(status_code=500, detail=f"Firebase error: {e}")

    logger.info(f"🔄 Firebase import done: {stats['imported']} imported, {stats['skipped_existing']} existing, {stats['errors']} errors")

    return {
        "success": True,
        "imported": stats["imported"],
        "skipped_existing": stats["skipped_existing"],
        "skipped_no_email": stats["skipped_no_email"],
        "errors": stats["errors"],
        "total_firebase_users": stats["imported"] + stats["skipped_existing"] + stats["skipped_no_email"] + stats["errors"],
        "users": stats["users"]
    }


@router.post("/migrate-emergent-users")
async def migrate_emergent_users(secret: str = ""):
    """
    One-time migration: insert old Emergent users directly into MongoDB.
    Protected by secret key (no auth needed — runs once, then remove).
    """
    if secret != "finromania2026migrate":
        raise HTTPException(status_code=403, detail="Invalid secret")

    USERS = [
        {"email": "nicolaehag@gmail.com", "uid": "9TeEvPWMj6g4sQCTDZl5k24REo23", "created": "2026-03-29"},
        {"email": "kozma_attila7@yahoo.com", "uid": "OqQCZYVxKkgBulZYkDr8GJkTqk23", "created": "2026-03-28"},
        {"email": "silviugiurca@yahoo.com", "uid": "d0DpqP5hGhWy9iSaPAF0JNjoHtK2", "created": "2026-03-27"},
        {"email": "archir.constantin@gmail.com", "uid": "MImjTJB2Vkc98Bh253R039ljdQq1", "created": "2026-03-26"},
        {"email": "adrianionita4025@gmail.com", "uid": "tgjuTS4yXheGr5h602UEP7zOlu13", "created": "2026-03-26"},
        {"email": "buncescu@gmail.com", "uid": "CEIkPDVqNoehEAVvt0HmumROFl53", "created": "2026-03-25"},
        {"email": "vivisor72@gmail.com", "uid": "cEDE68CqDRPigVZPOKnGHscronv2", "created": "2026-03-23"},
        {"email": "gabrielavornicu06@gmail.com", "uid": "8DCU0ZaHyxgTPHu9ynKTykdhYfH3", "created": "2026-03-23"},
        {"email": "vasilemarian76@gmail.com", "uid": "0D9XTv7x1PfQq0V6vmYAx8xCa5V2", "created": "2026-03-22"},
        {"email": "adrian.sorocaniuc@yahoo.com", "uid": "hHVWjMkj1yOGJnSYWmsKiZXs5wk1", "created": "2026-03-21"},
        {"email": "dobroviciandrei@googlemail.com", "uid": "VwzKD4z8uIMy1PfTJLqZH5zKlqB2", "created": "2026-03-21"},
        {"email": "miciicercetasi@gmail.com", "uid": "nFsfguG8gETQar4cKVvP74wsPfj1", "created": "2026-03-21"},
        {"email": "evilush@gmail.com", "uid": "Kn5AZyrIxJbuHMpuYTHi6iShtHm1", "created": "2026-03-20"},
        {"email": "clasadeengleza6a@gmail.com", "uid": "wPMoIWlvO8Mwu7zBJGSm3tWIAJ23", "created": "2026-03-20"},
        {"email": "catalin_td@yahoo.com", "uid": "xqfbw5OQHsezZV7ZYpSkfNwr1Rl2", "created": "2026-03-20"},
        {"email": "olaridaniel@gmail.com", "uid": "PzAxznfITBSWaaUIhbvKjUYGKyE2", "created": "2026-03-20"},
        {"email": "pasulacatalin@gmail.com", "uid": "UYOARU84iMb8KCzArhrPartnRUW2", "created": "2026-03-20"},
        {"email": "serbandascal@gmail.com", "uid": "wFSlqFrdalbnEYSkleelzWo4hA82", "created": "2026-03-20"},
        {"email": "gabitzugabitu@gmail.com", "uid": "D92iAMPB7HWgTMdrWwMXUHHqUGt1", "created": "2026-03-19"},
        {"email": "sandaionutalin@gmail.com", "uid": "KEOfFa5K3YgvaoO9xS1oGrD37v32", "created": "2026-03-19"},
        {"email": "pmirceamd@gmail.com", "uid": "vFyf65Pk7Ghf53Beb9fAR0PBC422", "created": "2026-03-18"},
        {"email": "ovidiumelinte21@gmail.com", "uid": "A6E7Fb0LUFNgNeHhdBNwUKJhWon2", "created": "2026-03-18"},
        {"email": "cimpean.ioan@gmail.com", "uid": "Aq04sxoDBUcGzkIR0Vk89mOkAm53", "created": "2026-03-18"},
        {"email": "costidragnea@yahoo.com", "uid": "M0nOL08DtWMO7PvK5aNkKPTQygW2", "created": "2026-03-18"},
        {"email": "daniel.olteniceanu@gmail.com", "uid": "vZUXGw8aiCZT5k7DMWOXli3dBIE2", "created": "2026-03-18"},
        {"email": "dr.penamarian@gmail.com", "uid": "HZM8ueCsjSPODtlwRrcyFV9mqZW2", "created": "2026-03-17"},
        {"email": "flambartcluj@gmail.com", "uid": "edoXwwhK7ehEt6fdjvYuNsU0KL43", "created": "2026-03-17"},
        {"email": "bogdan.cercel@gmail.com", "uid": "G8gwG6CenHOcQs9YqASSg8z4H6n1", "created": "2026-03-16"},
        {"email": "raducannicolae@gmail.com", "uid": "50SgYbhEWbdFVUh7kvTHfpwqF7q1", "created": "2026-03-16"},
        {"email": "delfhinblue@gmail.com", "uid": "m9jHM7WvI9WnjEHb2eySarNlAjB3", "created": "2026-03-16"},
        {"email": "elasticbombastic3@gmail.com", "uid": "TRbGZPk04tayM7leQft2cKvchf03", "created": "2026-03-16"},
        {"email": "ctmmariana@gmail.com", "uid": "sMfqteinv4hGip5N99m1bmxpC1V2", "created": "2026-03-16"},
        {"email": "haloiu.mihai@gmail.com", "uid": "I6s3Gk3JwyPQjtoFWWr56jfA8d62", "created": "2026-03-16"},
        {"email": "alexandru.pos@gmail.com", "uid": "I39pTT0Yz2NMhTbV08wPgbmvFL13", "created": "2026-03-15"},
        {"email": "razvan.mirodotescu@gmail.com", "uid": "6bkTwI4YWcUaPoZ7bRUWQXoTWMy2", "created": "2026-03-15"},
        {"email": "biscacristian@gmail.com", "uid": "j0l8o5q1J2c7h1oQ6RXmrPbOpDF2", "created": "2026-03-15"},
        {"email": "valentin.panti@gmail.com", "uid": "KXh2dTT117Z2roGTwnnnNE8jamk2", "created": "2026-03-15"},
        {"email": "karatimad@gmail.com", "uid": "0QoCgw9iTuYk16UAS3uANa55nX82", "created": "2026-03-15"},
        {"email": "gentilomm@gmail.com", "uid": "nnk5RSMQdiXPKcxyOtJRC8eAK5q2", "created": "2026-03-14"},
        {"email": "shopping.melinte@gmail.com", "uid": "DBheUtaCyUPxGwH1WxEVea4Vl2I2", "created": "2026-03-14"},
        {"email": "catalin.ba@gmail.com", "uid": "6OIBCE75etX9gY3jdJRL39Hgi9a2", "created": "2026-03-14"},
        {"email": "bolojan@gmail.com", "uid": "ZzYv7oNWsbTYSpTgpz2EeekBz403", "created": "2026-03-14"},
        {"email": "claudia.pop89@gmail.com", "uid": "w3dJoWcSeBUZBqD1ghthpzAKMdb2", "created": "2026-03-14"},
        {"email": "sebastiangordan7@gmail.com", "uid": "saNtt9vedZhhn50xEBguiehDVcl2", "created": "2026-03-14"},
        {"email": "lucian82luci@yahoo.com", "uid": "3FPtn9zvJTctEsW2D8cJ6VUQkYJ2", "created": "2026-03-14"},
        {"email": "loveritza2020@gmail.com", "uid": "zO1rHogJNQMVmBtlySJsZW1kwfw1", "created": "2026-03-14"},
        {"email": "bogdan.catre@gmail.com", "uid": "UHjiaJxEuSXseae7toBop5FP6xv1", "created": "2026-03-14"},
        {"email": "marius.garip@gmail.com", "uid": "PSQS0ddXjKU8edBrog3oNffHTSf1", "created": "2026-03-14"},
        {"email": "alexmakerulzz@gmail.com", "uid": "YXgquOwKXpab3kPzfbgv58RsRBd2", "created": "2026-03-14"},
        {"email": "valibutuc17@gmail.com", "uid": "OgYChr9blKRBDutNdCs6R984lev1", "created": "2026-03-14"},
        {"email": "ghiorghitaionel@gmail.com", "uid": "hV8vYkYmj7RnIgZKYXQNeO2tt7m1", "created": "2026-03-14"},
        {"email": "ovi.paduraru@gmail.com", "uid": "LTZNZgz8YIfB49PJNsWAcnOJrFg2", "created": "2026-03-14"},
        {"email": "petcu.nicu131@gmail.com", "uid": "wzAwnvVAtbMeuyeJpUerdR20PrC2", "created": "2026-03-14"},
        {"email": "razvanbobon@yahoo.com", "uid": "sDwr0SO7x6cOk0aLznQjoMbQW783", "created": "2026-03-14"},
        {"email": "ambrozinightwish@gmail.com", "uid": "8WnqLaM18ScagCdhCYg7DHBtX3G2", "created": "2026-03-14"},
        {"email": "ramonasirb1@gmail.com", "uid": "6yHlGcNhN8VE2sDocLSZlnWmwp33", "created": "2026-03-14"},
        {"email": "dungatul@gmail.com", "uid": "0Q0rd5iClSVfXhNAJdT6e3asHGZ2", "created": "2026-03-14"},
        {"email": "gigi.diaconeasa@gmail.com", "uid": "K5bc8lCBvlbcIy5cmiFkXGgQyUq2", "created": "2026-03-14"},
        {"email": "cursuriav@gmail.com", "uid": "grBWSa8WgAVQ7WrXRxujdlfOMPg2", "created": "2026-03-14"},
        {"email": "custoom.11@gmail.com", "uid": "990vSRuJ7ze8asZFNd9MqmjKbfo2", "created": "2026-03-14"},
        {"email": "ionut.dumitru@gmail.com", "uid": "WnDyh3b0sdPZVhJURqHzcVvIP3D3", "created": "2026-03-14"},
        {"email": "flaviusburtescu@gmail.com", "uid": "1bQIBZaBHwO7bQkRyWPHrkWO42v1", "created": "2026-03-14"},
        {"email": "ciprian.belcea@gmail.com", "uid": "0zGImUFfOzfSdN8SK0HzTASueZI3", "created": "2026-03-14"},
        {"email": "homeass91@gmail.com", "uid": "yhVcNZ51xdU7rqzkVACoLPYQhbq2", "created": "2026-03-14"},
        {"email": "sergiucostea.cj@gmail.com", "uid": "BQUIoTYYkyLJ4CMq9OTd1VXJP1H3", "created": "2026-03-14"},
        {"email": "razvi.cr@gmail.com", "uid": "XgQC9TigykXjEWRQmIS90D2d6bL2", "created": "2026-03-14"},
        {"email": "catalin.monica@gmail.com", "uid": "8iVTgQWHjSWtoNDcqt9MYA0BkFo2", "created": "2026-03-14"},
        {"email": "corneliustrg71@gmail.com", "uid": "8rXCXNBFqQN0ggs5CMyYcQmyApo1", "created": "2026-03-14"},
        {"email": "puianmarius@gmail.com", "uid": "22Rnj5ejR7bWrmFafZx0VeqpOcj1", "created": "2026-03-14"},
        {"email": "luca_totto@yahoo.com", "uid": "A8Muuw5XCpdbRDJPpWMmalQJKs73", "created": "2026-03-14"},
        {"email": "kankuroandrei@yahoo.com", "uid": "ETsWyjNPQKOERkKLipZIJYAYv472", "created": "2026-03-14"},
        {"email": "danut.922@gmail.com", "uid": "E7C3JP2htcOAuKzNr20xUxgtlDc2", "created": "2026-03-14"},
        {"email": "alexmpopa@gmail.com", "uid": "5AIGF8lPsgX5x1qL0nroKnfegpp2", "created": "2026-03-13"},
        {"email": "ionut.negru87@gmail.com", "uid": "IZM7Q1immTW0696FLkPMZAgtlFo1", "created": "2026-03-13"},
        {"email": "nagy.christian@gmail.com", "uid": "8ub4rmM3BmaSiMx557itD7X9JMr2", "created": "2026-03-13"},
        {"email": "postolache11andrei@gmail.com", "uid": "jkVMco1nHlQjqti5d94VCSvgV8s2", "created": "2026-03-13"},
        {"email": "gourmetgift.ro@gmail.com", "uid": "fnCxHiPeEQNWNkfQtkkN1ETNAbo2", "created": "2026-03-13"},
        {"email": "ilie.cretu@yahoo.com", "uid": "HaCrbdPJw3U7TBerFtDYV9Z6yn23", "created": "2026-03-13"},
        {"email": "eg.toma@outlook.com", "uid": "Ce6L9CDJJ8R7VmFFUBjxKCXQiHu1", "created": "2026-03-13"},
        {"email": "polki101010@gmail.com", "uid": "JE0uIAfCoiPmEpKNWXV1xZPImbN2", "created": "2026-03-13"},
        {"email": "madalin.druga@yahoo.com", "uid": "RKXvcCIjWte8044VpwfSrWPghK13", "created": "2026-03-13"},
        {"email": "pop.silvium@gmail.com", "uid": "6nuQ9YwO5YUR3npU3ay7BZN9HqC2", "created": "2026-03-13"},
        {"email": "r.florin01@gmail.com", "uid": "U2DS2Pxs5CacgDFDJGI8eGUqjn22", "created": "2026-03-13"},
        {"email": "medinstpro@gmail.com", "uid": "KdkfVOqaJCUJxoVXp0x1ZjZrWeY2", "created": "2026-03-13"},
        {"email": "mitris.gelu@gmail.com", "uid": "nr3C24G05RfuO9dxx1h5nyayUWp2", "created": "2026-03-13"},
        {"email": "lazeahoratiu@gmail.com", "uid": "4t5uvzbVTLUPDavzpoPQXqVkVYL2", "created": "2026-03-13"},
        {"email": "calinxp@gmail.com", "uid": "IdNXVWUqRWOOyk5v4p6SA4c6Wpw1", "created": "2026-03-13"},
        {"email": "yo.spiro@gmail.com", "uid": "9iXPDX4ywQgXbpohyg2iDv39u7s2", "created": "2026-03-13"},
        {"email": "andreea.stoia@gmail.com", "uid": "nOcKZ9RaDRRXrzgXFlR7mjCPdbJ2", "created": "2026-03-13"},
        {"email": "lpizevska@gmail.com", "uid": "XQCunQs5RjZVV8k5RcKNUkgEo5p2", "created": "2026-03-13"},
        {"email": "ruscumihai@gmail.com", "uid": "sctlnCev8ZSRzcXzxy2CNJLQrpL2", "created": "2026-03-13"},
        {"email": "sergo3@gmail.com", "uid": "GZmuVIC41Ee3w2fwgRqcTnrdPbc2", "created": "2026-03-13"},
        {"email": "catalinmincu2002@yahoo.com", "uid": "1HbR7DMs6Jh2JuWt6CTSa9sAu522", "created": "2026-03-13"},
        {"email": "iulianpeptu@gmail.com", "uid": "U0dgZYfkekekzFeEMJIJwVIpPAR2", "created": "2026-03-13"},
        {"email": "george.burduhos@gmail.com", "uid": "3nT3itsTHSgMUFipFq3VHTzT1vT2", "created": "2026-03-13"},
        {"email": "dr.alexandar94@gmail.com", "uid": "3YpzZ1vXp1R8UQ2IWPgmVYnwTKi1", "created": "2026-03-13"},
        {"email": "vladadrianrusu@gmail.com", "uid": "SlQfIRYcgYNiSyUdU8LB2dsxVf03", "created": "2026-03-13"},
        {"email": "paulbode2000@gmail.com", "uid": "my6ApEkBLCcgV1ooDK5RcnOfnvv2", "created": "2026-03-13"},
        {"email": "sports6501@gmail.com", "uid": "F086x68CasYKjS6ATVJwNjwbi113", "created": "2026-03-13"},
        {"email": "nucului42c18@gmail.com", "uid": "Ev26IbkMg4M2I4UC41XvVs4nIsB3", "created": "2026-03-13"},
        {"email": "danny.fratean@gmail.com", "uid": "UFADB8WCUdVW3hai0OB77MUQWYm1", "created": "2026-03-13"},
        {"email": "paraschivu.alexandru@gmail.com", "uid": "J6nd7rleJAUFxTFjLblBz0bAtZE3", "created": "2026-03-13"},
        {"email": "goosila@gmail.com", "uid": "LVymcP5Ea5SH5HaRnGbsnT6zcBv2", "created": "2026-03-13"},
        {"email": "flavius.ionel99@e-uvt.ro", "uid": "zPO1RLJModcKJVUQ3eISYMWPTGy2", "created": "2026-03-13"},
        {"email": "lilian.marin21@gmail.com", "uid": "JZgxrY6qXmX0mjvLyakK4hG2zX62", "created": "2026-03-13"},
        {"email": "lcpcristi@gmail.com", "uid": "fGyjxcsXMGQMeB7CcLjDGusQc1t1", "created": "2026-03-13"},
        {"email": "dan741976@gmail.com", "uid": "7WUS6uzihPf1fdVPadwzqm5zvn82", "created": "2026-03-13"},
        {"email": "sorinat@gmail.com", "uid": "IaUemE6uxZTFufJSGaC2maYsnWS2", "created": "2026-03-13"},
        {"email": "stanculescu.dan@gmail.com", "uid": "910Wva5QzsT7NL6z5RrNTUNdWmy1", "created": "2026-03-13"},
        {"email": "petrovicistefan@gmail.com", "uid": "Qe6av1oICuRgnWkaYsACu0HPq722", "created": "2026-03-13"},
        {"email": "iulian.baiculescu@gmail.com", "uid": "8LgICChXQzfvmZtESXexRXwnhMm1", "created": "2026-03-13"},
        {"email": "cagil_ali@yahoo.com", "uid": "ub1ByxLfpIfFaggZvhoVYEYKmM03", "created": "2026-03-13"},
        {"email": "dand2408@gmail.com", "uid": "rgaZoJMyitUI3bulGvE9IzQ6Blf1", "created": "2026-03-13"},
        {"email": "aureliandraghici@gmail.com", "uid": "76pE8o21i4OaQiHUu7rLfPfQo7H3", "created": "2026-03-13"},
        {"email": "dadalau.cristi@gmail.com", "uid": "vKXozNYl44NaP31TRxiXbLZTF1k2", "created": "2026-03-13"},
        {"email": "botnariuc.dorin@gmail.com", "uid": "XwO1hlFeEYeVmJGBQ54Llyb3U892", "created": "2026-03-13"},
        {"email": "silviubadalache@gmail.com", "uid": "HROQv4UMC8Sc0miT2O9RvYmIZ7t2", "created": "2026-03-13"},
        {"email": "prohuf@gmail.com", "uid": "FKFx3mbIl9aOAPRO3DzpZU3K38G2", "created": "2026-03-13"},
        {"email": "iulimog@gmail.com", "uid": "0Qq4dt0v9MfkDAufvpOoayVc0Ug2", "created": "2026-03-13"},
        {"email": "florinzaharia007@gmail.com", "uid": "pP5bjlyKcaQXrkJFNQda6lN9np33", "created": "2026-03-13"},
        {"email": "eliseironcea1@gmail.com", "uid": "cOxYtOmMI6UFU8XmWrhRRn0aNeE2", "created": "2026-03-13"},
        {"email": "mihaelacozma68@gmail.com", "uid": "VpR8LUHeBkbNRRgUOY4BHabjqpv1", "created": "2026-03-13"},
        {"email": "mihaideneanu@gmail.com", "uid": "MlEKhXHKKEX68bvwIJDUAspcrKl2", "created": "2026-03-13"},
        {"email": "tomamihai091@gmail.com", "uid": "M9xu46xvNhfPV3U4DGcaZDxOp032", "created": "2026-03-13"},
        {"email": "rmanolescu@gmail.com", "uid": "kNtcS8EglEdk2WVvi2B9J90ii9K2", "created": "2026-03-13"},
        {"email": "ardeleanb.adriana@gmail.com", "uid": "8r7XAlJKBuRxys4DfP4QXGv4lED3", "created": "2026-03-13"},
        {"email": "dinca.alex04@gmail.com", "uid": "hYGLXeNAbHebJ2opvWp2OWr5Ujm2", "created": "2026-03-13"},
        {"email": "analarisa.bucur@gmail.com", "uid": "XarliiTjQFblr9iqNcaZII0Q15y1", "created": "2026-03-13"},
        {"email": "bpriceputu@gmail.com", "uid": "VmAQmSIEUSdpYhf8R13NPfbO3gp1", "created": "2026-03-13"},
        {"email": "maricelmatei@gmail.com", "uid": "5CgRbzJDaqRXz7FENBFo2cnyEQ23", "created": "2026-03-13"},
        {"email": "cristiantoma1984@gmail.com", "uid": "tgjt6lG3fDSNz6ESsgPDT4CHJnw1", "created": "2026-03-13"},
        {"email": "gsilviuu@gmail.com", "uid": "BrcYpRtW03Z3UvI3TRIEHakLWGD2", "created": "2026-03-13"},
        {"email": "adizbang@gmail.com", "uid": "XOxr02JUB2dWyLdXOCCa8CoinUT2", "created": "2026-03-13"},
        {"email": "gchristian27.cg@gmail.com", "uid": "mLUi1lLUa2fnpMY9mkBMnhClGYj1", "created": "2026-03-13"},
        {"email": "4netit2@gmail.com", "uid": "EqVBZEuzYmhNHvvZGOSaM70dW2D3", "created": "2026-03-13"},
        {"email": "mihai.rognean@gmail.com", "uid": "KKxrymiq7RWljYCDWXqN8sTnsFo1", "created": "2026-03-13"},
        {"email": "adicrocodyl@gmail.com", "uid": "hci1MMN2w3SU7DXZTtVhUB6vzP93", "created": "2026-03-12"},
        {"email": "clioapolo1@gmail.com", "uid": "E80nwdNsf3YNMd92bJeBi7H7M2i1", "created": "2026-03-12"},
        {"email": "pitesti1234@gmail.com", "uid": "H48ThXDo6qgLU8Q9SenJOyaE93S2", "created": "2026-03-12"},
        {"email": "juvete0758689601@gmail.com", "uid": "0uCMZ1zhmUhhnthnBQsOjIqkzH73", "created": "2026-03-12"},
        {"email": "sorinmunteanu1969@gmail.com", "uid": "urHKqaTlWLe8iHjQj37ptlICvjs1", "created": "2026-03-12"},
        {"email": "sitestiri@gmail.com", "uid": "qJpdN3XbiQOiVbUmCqqEEMTGjqB3", "created": "2026-03-12"},
        {"email": "danutza3@gmail.com", "uid": "47UBR7xgUuVGfXy74hVOK86q5li2", "created": "2026-03-12"},
        {"email": "vladilaoctavian@gmail.com", "uid": "bwaKCSwWPhfRXdVRbFpQz62gfb12", "created": "2026-03-12"},
        {"email": "alin.andries@gmail.com", "uid": "LmhP1mA7YTZ5U3KOTqxFJAHtkGj2", "created": "2026-03-12"},
        {"email": "dan.mihai.lunganul@gmail.com", "uid": "8uS84znoWWdCG0QfQkKbpftN7xI2", "created": "2026-03-12"},
        {"email": "maporumbescu@gmail.com", "uid": "KJN1Tt6woNU4DwFinw5lPyTH6f12", "created": "2026-03-12"},
        {"email": "eherisanu@gmail.com", "uid": "CWFUra2GMoa1YKIMTKleF2wfdlm2", "created": "2026-03-12"},
        {"email": "adryanleonte@gmail.com", "uid": "5lffo2dnggfzVhaPaBvJwo6OfQy1", "created": "2026-03-12"},
        {"email": "felix.stanculet@gmail.com", "uid": "1h8JRHCjVbfPmsDVcEcAMaPDCDP2", "created": "2026-03-12"},
        {"email": "nickpesca@gmail.com", "uid": "3s3L4cidFRQy8ShenQuSuSlXpiz1", "created": "2026-03-12"},
        {"email": "dumalex999@gmail.com", "uid": "9fyOQzz9k8YOE4kHCE9tQRuz4qs2", "created": "2026-03-12"},
        {"email": "ionutgardalean@gmail.com", "uid": "BUo79ev2OvML5X1YTVlCwoq1qy43", "created": "2026-03-12"},
        {"email": "mirceat3@gmail.com", "uid": "O1AYjE5SSSQQK7d36wCUPW3SkAp2", "created": "2026-03-12"},
        {"email": "cosmin.potrocamedrea@gmail.com", "uid": "QRmYxa2ptZTuAXfG9f27W6zlNaJ2", "created": "2026-03-12"},
        {"email": "mdan93s4@gmail.com", "uid": "BZxjyUYYdtfAvFn0yGj57UiPxSe2", "created": "2026-03-12"},
        {"email": "laminoarelor14@googlemail.com", "uid": "6jwXEy8o8caXHzLrYmnmZVBmB8V2", "created": "2026-03-12"},
        {"email": "fzamfir@gmail.com", "uid": "GZU9C0730Ea4vH8kdUaCvROCdpx2", "created": "2026-03-12"},
        {"email": "adrian.tanasescu.97@gmail.com", "uid": "AOk4yFay4jbk1DTNK98fMXs6SO92", "created": "2026-03-12"},
        {"email": "blondu2024@gmail.com", "uid": "Pbf63hG40JUwYcYIWEUYKxnVXKs2", "created": "2026-01-14"},
        {"email": "contact.smartconvertpro@gmail.com", "uid": "wF8BZWiysXdroqEC3T8Ba46v2CB2", "created": "2026-01-12"},
        {"email": "profirer@gmail.com", "uid": "6iWPoBzbysVEpmfK4KlCzsStFUa2", "created": "2026-01-07"},
        {"email": "nahidirayanxan@gmail.com", "uid": "rSBqXCjadnU8K7whpDsZC79pnCP2", "created": "2026-01-04"},
        {"email": "reitazafina@gmail.com", "uid": "6y6xIkZxppVutNpimDLKsytIBcB3", "created": "2026-01-02"},
        {"email": "profirecristiandaniel@gmail.com", "uid": "x5T7cw7ONkekDGNxrJheB70xysG2", "created": "2026-01-02"},
        {"email": "contact@finromania.ro", "uid": "TPEP1AE2GMUPtAXEdL0ozdOgg3h2", "created": "2025-12-30"},
        {"email": "tanasecristian2007@gmail.com", "uid": "oY2SBusXvDdrWR027XqAGAHtH053", "created": "2025-12-30"},
    ]

    import uuid as _uuid
    db = await get_database()
    free_pro_deadline = datetime(2026, 6, 5, tzinfo=timezone.utc)
    admin_emails = ["tanasecristian2007@gmail.com", "contact@finromania.ro"]

    imported = 0
    skipped = 0
    errors = 0

    for u in USERS:
        email = u["email"]
        existing = await db.users.find_one({"email": email})
        if existing:
            skipped += 1
            continue

        new_user = {
            "user_id": str(_uuid.uuid4()),
            "email": email,
            "name": email.split("@")[0],
            "firebase_uid": u["uid"],
            "auth_provider": "firebase_google",
            "created_at": f"{u['created']}T00:00:00+00:00",
            "last_login": f"{u['created']}T00:00:00+00:00",
            "is_admin": email.lower() in admin_emails,
            "ai_credits_used": 0,
            "total_logins": 0,
            "is_early_adopter": True,
            "subscription_level": "pro",
            "subscription_expires_at": free_pro_deadline.isoformat(),
            "subscription_source": "emergent_migration",
            "unlocked_levels": ["beginner", "intermediate", "advanced"],
            "experience_level": "advanced",
            "daily_summary_enabled": True,
            "migrated_from": "emergent",
            "migrated_at": datetime.now(timezone.utc).isoformat()
        }

        try:
            await db.users.insert_one(new_user)
            imported += 1
        except Exception as e:
            errors += 1
            logger.error(f"Error importing {email}: {e}")

    return {
        "success": True,
        "imported": imported,
        "skipped_existing": skipped,
        "errors": errors,
        "total": len(USERS)
    }
