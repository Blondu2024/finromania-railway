"""Push Notifications API pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import json
import logging

try:
    from pywebpush import webpush, WebPushException
    WEBPUSH_AVAILABLE = True
except ImportError:
    WEBPUSH_AVAILABLE = False

from config.database import get_database
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/push", tags=["Push Notifications"])

# VAPID Keys from environment
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")
VAPID_EMAIL = os.environ.get("VAPID_EMAIL", "contact@finromania.ro")


# ============================================
# MODELS
# ============================================

class PushSubscription(BaseModel):
    endpoint: str
    keys: dict  # {"p256dh": "...", "auth": "..."}


class PushMessage(BaseModel):
    title: str
    body: str
    icon: Optional[str] = "/logo192.png"
    badge: Optional[str] = "/logo192.png"
    tag: Optional[str] = None
    url: Optional[str] = "/"
    data: Optional[dict] = None


# ============================================
# ENDPOINTS
# ============================================

@router.get("/vapid-key")
async def get_vapid_public_key():
    """Get VAPID public key for client subscription"""
    if not VAPID_PUBLIC_KEY:
        raise HTTPException(status_code=500, detail="VAPID key not configured")
    return {"publicKey": VAPID_PUBLIC_KEY}


@router.post("/subscribe")
async def subscribe_to_push(
    subscription: PushSubscription,
    current_user: dict = Depends(require_auth)
):
    """Subscribe user to push notifications"""
    try:
        db = await get_database()
        
        # Store subscription
        await db.push_subscriptions.update_one(
            {"user_id": current_user["user_id"], "endpoint": subscription.endpoint},
            {
                "$set": {
                    "user_id": current_user["user_id"],
                    "endpoint": subscription.endpoint,
                    "keys": subscription.keys,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "active": True
                }
            },
            upsert=True
        )
        
        logger.info(f"Push subscription added for user {current_user['user_id']}")
        
        return {
            "success": True,
            "message": "Subscribed to push notifications"
        }
        
    except Exception as e:
        logger.error(f"Error subscribing to push: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/unsubscribe")
async def unsubscribe_from_push(
    subscription: PushSubscription,
    current_user: dict = Depends(get_current_user)
):
    """Unsubscribe user from push notifications"""
    try:
        db = await get_database()
        
        result = await db.push_subscriptions.delete_one({
            "user_id": current_user["user_id"],
            "endpoint": subscription.endpoint
        })
        
        if result.deleted_count == 0:
            # Try to mark as inactive instead
            await db.push_subscriptions.update_one(
                {"user_id": current_user["user_id"], "endpoint": subscription.endpoint},
                {"$set": {"active": False}}
            )
        
        return {
            "success": True,
            "message": "Unsubscribed from push notifications"
        }
        
    except Exception as e:
        logger.error(f"Error unsubscribing from push: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_push_status(current_user: dict = Depends(get_current_user)):
    """Check if user has active push subscriptions"""
    try:
        db = await get_database()
        
        count = await db.push_subscriptions.count_documents({
            "user_id": current_user["user_id"],
            "active": True
        })
        
        return {
            "subscribed": count > 0,
            "subscription_count": count
        }
        
    except Exception as e:
        logger.error(f"Error checking push status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def send_test_notification(current_user: dict = Depends(get_current_user)):
    """Send a test push notification to the user"""
    if not WEBPUSH_AVAILABLE:
        raise HTTPException(status_code=500, detail="WebPush not available")
    
    if not VAPID_PRIVATE_KEY:
        raise HTTPException(status_code=500, detail="VAPID keys not configured")
    
    try:
        db = await get_database()
        
        # Get user's subscriptions
        subscriptions = await db.push_subscriptions.find({
            "user_id": current_user["user_id"],
            "active": True
        }).to_list(10)
        
        if not subscriptions:
            raise HTTPException(status_code=404, detail="No active subscriptions found")
        
        # Prepare notification
        notification = {
            "title": "🔔 Test FinRomania",
            "body": "Notificările funcționează! Vei primi alerte pentru acțiunile tale.",
            "icon": "/logo192.png",
            "badge": "/logo192.png",
            "tag": "test-notification",
            "data": {"url": "/watchlist"}
        }
        
        sent = 0
        failed = 0
        
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub["endpoint"],
                        "keys": sub["keys"]
                    },
                    data=json.dumps(notification),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": f"mailto:{VAPID_EMAIL}"}
                )
                sent += 1
            except WebPushException as e:
                logger.warning(f"Push failed for subscription: {e}")
                # Mark subscription as inactive if it's gone
                if e.response and e.response.status_code in [404, 410]:
                    await db.push_subscriptions.update_one(
                        {"_id": sub["_id"]},
                        {"$set": {"active": False}}
                    )
                failed += 1
            except Exception as e:
                logger.error(f"Push error: {e}")
                failed += 1
        
        return {
            "success": True,
            "sent": sent,
            "failed": failed,
            "message": f"Test notification sent to {sent} device(s)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# UTILITY FUNCTIONS (for other modules)
# ============================================

async def send_notification_to_user(user_id: str, notification: dict):
    """
    Send push notification to a specific user.
    Called by other modules (alerts, news, etc.)
    """
    if not WEBPUSH_AVAILABLE or not VAPID_PRIVATE_KEY:
        logger.warning("WebPush not available, skipping notification")
        return {"sent": 0, "failed": 0}
    
    try:
        db = await get_database()
        
        subscriptions = await db.push_subscriptions.find({
            "user_id": user_id,
            "active": True
        }).to_list(10)
        
        if not subscriptions:
            return {"sent": 0, "failed": 0}
        
        sent = 0
        failed = 0
        
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub["endpoint"],
                        "keys": sub["keys"]
                    },
                    data=json.dumps(notification),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": f"mailto:{VAPID_EMAIL}"}
                )
                sent += 1
            except Exception as e:
                logger.warning(f"Push failed: {e}")
                failed += 1
        
        return {"sent": sent, "failed": failed}
        
    except Exception as e:
        logger.error(f"Error in send_notification_to_user: {e}")
        return {"sent": 0, "failed": 0}


async def send_notification_to_all(notification: dict, user_filter: dict = None):
    """
    Send push notification to all subscribed users (or filtered subset).
    Useful for market alerts, news, etc.
    """
    if not WEBPUSH_AVAILABLE or not VAPID_PRIVATE_KEY:
        return {"sent": 0, "failed": 0}
    
    try:
        db = await get_database()
        
        query = {"active": True}
        if user_filter:
            # Get users matching filter
            users = await db.notification_preferences.find(
                user_filter,
                {"user_id": 1}
            ).to_list(1000)
            user_ids = [u["user_id"] for u in users]
            query["user_id"] = {"$in": user_ids}
        
        subscriptions = await db.push_subscriptions.find(query).to_list(10000)
        
        sent = 0
        failed = 0
        
        for sub in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": sub["endpoint"],
                        "keys": sub["keys"]
                    },
                    data=json.dumps(notification),
                    vapid_private_key=VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": f"mailto:{VAPID_EMAIL}"}
                )
                sent += 1
            except Exception:
                failed += 1
        
        logger.info(f"Broadcast notification: {sent} sent, {failed} failed")
        return {"sent": sent, "failed": failed}
        
    except Exception as e:
        logger.error(f"Error in send_notification_to_all: {e}")
        return {"sent": 0, "failed": 0}
