"""
Admin Panel - Manage Users & Subscriptions & Feedback
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from config.database import get_database
from routes.auth import require_auth
from bson import ObjectId

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Admin emails
ADMIN_EMAILS = ["tanasecristian2007@gmail.com", "contact@finromania.ro"]

async def require_admin(user: dict = Depends(require_auth)):
    """Verifică dacă user-ul e admin"""
    if not user.get("is_admin") and user.get("email") not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Access denied - Admin only")
    return user


class SetSubscriptionRequest(BaseModel):
    email: str
    subscription_level: str  # 'free' or 'pro'
    duration_days: Optional[int] = 30  # Câte zile PRO


@router.get("/users")
async def get_all_users(admin: dict = Depends(require_admin)):
    """Lista tuturor utilizatorilor"""
    db = await get_database()
    
    users = await db.users.find(
        {},
        {"_id": 0, "user_id": 1, "email": 1, "name": 1, "subscription_level": 1, 
         "experience_level": 1, "created_at": 1, "last_login": 1, "is_admin": 1,
         "ai_credits_used": 1}
    ).sort("created_at", -1).limit(100).to_list(100)
    
    return {
        "users": users,
        "total": len(users)
    }


@router.post("/set-subscription")
async def set_user_subscription(
    request: SetSubscriptionRequest,
    admin: dict = Depends(require_admin)
):
    """Setează subscription level pentru un utilizator"""
    db = await get_database()
    
    # Găsește user-ul
    user = await db.users.find_one({"email": request.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail=f"User {request.email} nu există")
    
    update_data = {
        "subscription_level": request.subscription_level,
    }
    
    if request.subscription_level == "pro":
        # Setează expirare PRO
        expires_at = datetime.now(timezone.utc) + timedelta(days=request.duration_days)
        update_data["subscription_expires_at"] = expires_at.isoformat()
        update_data["unlocked_levels"] = ["beginner", "intermediate", "advanced"]
        update_data["experience_level"] = "advanced"
    else:
        # Șterge expirare pentru FREE
        update_data["subscription_expires_at"] = None
        update_data["experience_level"] = "beginner"
        update_data["unlocked_levels"] = ["beginner"]
    
    # Update user
    await db.users.update_one(
        {"email": request.email},
        {"$set": update_data}
    )
    
    # Log action
    await db.admin_actions.insert_one({
        "admin_email": admin["email"],
        "action": "set_subscription",
        "target_email": request.email,
        "subscription_level": request.subscription_level,
        "duration_days": request.duration_days if request.subscription_level == "pro" else 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "success": True,
        "message": f"User {request.email} setat ca {request.subscription_level.upper()}",
        "expires_at": update_data.get("subscription_expires_at")
    }


@router.get("/stats")
async def get_admin_stats(admin: dict = Depends(require_admin)):
    """Statistici generale"""
    db = await get_database()
    
    total_users = await db.users.count_documents({})
    pro_users = await db.users.count_documents({"subscription_level": "pro"})
    free_users = total_users - pro_users
    
    # Recent signups (last 7 days)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_signups = await db.users.count_documents({
        "created_at": {"$gte": week_ago}
    })
    
    # Active users (logged in last 7 days)
    active_users = await db.users.count_documents({
        "last_login": {"$gte": week_ago}
    })
    
    # AI usage stats
    ai_queries_pipeline = [
        {"$group": {
            "_id": None,
            "total_queries": {"$sum": "$ai_credits_used"}
        }}
    ]
    ai_usage = await db.users.aggregate(ai_queries_pipeline).to_list(1)
    total_ai_queries = ai_usage[0]["total_queries"] if ai_usage else 0
    
    # Feedback stats
    total_feedback = await db.feedback.count_documents({})
    new_feedback = await db.feedback.count_documents({"status": "new"})
    
    return {
        "total_users": total_users,
        "pro_users": pro_users,
        "free_users": free_users,
        "recent_signups_7d": recent_signups,
        "active_users_7d": active_users,
        "total_ai_queries": total_ai_queries,
        "pro_percentage": round((pro_users / total_users * 100) if total_users > 0 else 0, 1),
        "total_feedback": total_feedback,
        "new_feedback": new_feedback
    }



@router.post("/upgrade-all-to-pro")
async def upgrade_all_users_to_pro(admin: dict = Depends(require_admin)):
    """Upgrade toți userii la PRO până pe 5 iunie 2026"""
    db = await get_database()
    deadline = datetime(2026, 6, 5, tzinfo=timezone.utc).isoformat()
    
    # Upgrade non-PRO users
    result = await db.users.update_many(
        {"$or": [
            {"subscription_level": {"$ne": "pro"}},
            {"subscription_level": {"$exists": False}}
        ]},
        {"$set": {
            "subscription_level": "pro",
            "subscription_expires_at": deadline,
            "subscription_source": "free_pro_june2026",
            "is_early_adopter": True,
            "unlocked_levels": ["beginner", "intermediate", "advanced"]
        }}
    )
    
    # Extend existing PRO that expire before June 5
    result2 = await db.users.update_many(
        {
            "subscription_level": "pro",
            "subscription_expires_at": {"$lt": deadline}
        },
        {"$set": {
            "subscription_expires_at": deadline,
            "subscription_source": "free_pro_june2026"
        }}
    )
    
    total = await db.users.count_documents({})
    pro_now = await db.users.count_documents({"subscription_level": "pro"})
    
    return {
        "success": True,
        "upgraded": result.modified_count,
        "extended": result2.modified_count,
        "total_users": total,
        "pro_users": pro_now,
        "message": f"Toți {pro_now} useri au acum PRO până pe 5 iunie 2026"
    }


# ============================================
# FEEDBACK MANAGEMENT
# ============================================

class UpdateFeedbackRequest(BaseModel):
    status: str  # new, in_progress, resolved


@router.get("/feedback")
async def get_all_feedback(
    status: Optional[str] = None,
    feedback_type: Optional[str] = None,
    admin: dict = Depends(require_admin)
):
    """Lista tuturor feedback-urilor cu filtrare opțională"""
    db = await get_database()
    
    # Build query filter
    query = {}
    if status:
        query["status"] = status
    if feedback_type:
        query["type"] = feedback_type
    
    feedback_items = await db.feedback.find(query).sort("created_at", -1).limit(200).to_list(200)
    
    # Convert ObjectId to string for JSON serialization
    for item in feedback_items:
        item["id"] = str(item.pop("_id"))
    
    return {
        "feedback": feedback_items,
        "total": len(feedback_items)
    }


@router.put("/feedback/{feedback_id}")
async def update_feedback_status(
    feedback_id: str,
    request: UpdateFeedbackRequest,
    admin: dict = Depends(require_admin)
):
    """Actualizează statusul unui feedback"""
    db = await get_database()
    
    valid_statuses = ["new", "in_progress", "resolved"]
    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Status invalid. Opțiuni: {', '.join(valid_statuses)}"
        )
    
    try:
        result = await db.feedback.update_one(
            {"_id": ObjectId(feedback_id)},
            {
                "$set": {
                    "status": request.status,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "updated_by": admin["email"]
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        return {
            "success": True,
            "message": f"Feedback actualizat: {request.status}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ID invalid: {str(e)}")



class TestEmailRequest(BaseModel):
    email: str
    email_type: str  # "welcome", "price_alert_test", "watchlist_big_moves_test"


@router.post("/test-email")
async def send_test_email(request: TestEmailRequest, admin: dict = Depends(require_admin)):
    """Trimite un email de test pentru diverse tipuri de notificări"""
    from services.notification_service import notification_service
    
    if request.email_type == "welcome":
        success = await notification_service.send_welcome_email(
            user_email=request.email,
            user_name="Test Admin"
        )
    elif request.email_type == "early_adopter_expiring":
        success = await notification_service.send_early_adopter_expiring_email(
            user_email=request.email,
            user_name="Test Admin",
            days_left=7,
            expires_at="2026-06-05T23:59:59Z"
        )
    elif request.email_type == "watchlist_big_moves_test":
        success = await notification_service.send_watchlist_big_moves_email(
            user_email=request.email,
            user_name="Test Admin",
            movers=[
                {"symbol": "TLV", "name": "Banca Transilvania SA", "price": 28.40, "change_pct": 5.8},
                {"symbol": "SNP", "name": "OMV Petrom SA", "price": 0.62, "change_pct": -6.2},
            ]
        )
    else:
        raise HTTPException(status_code=400, detail=f"Tip email necunoscut: {request.email_type}")
    
    return {
        "success": success,
        "message": f"Email '{request.email_type}' {'trimis' if success else 'EȘUAT'} la {request.email}"
    }


@router.post("/check-watchlist-moves")
async def trigger_watchlist_moves_check(admin: dict = Depends(require_admin)):
    """Declanșează manual verificarea mișcărilor mari din watchlist"""
    from services.notification_service import notification_service
    results = await notification_service.check_watchlist_big_moves()
    return {
        "success": True,
        "results": results
    }
