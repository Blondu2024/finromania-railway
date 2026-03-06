"""Notifications API - Endpoint-uri pentru notificări utilizatori"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from routes.auth import get_current_user
from services.notification_service import notification_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    action_url: str
    action_text: str
    priority: str
    icon: str
    read: bool
    created_at: str


class NotificationCountResponse(BaseModel):
    unread_count: int


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 20,
    user: dict = Depends(get_current_user)
):
    """Obține notificările utilizatorului curent"""
    if not user:
        raise HTTPException(status_code=401, detail="Autentificare necesară")
    
    notifications = await notification_service.get_user_notifications(
        user["user_id"], 
        unread_only=unread_only,
        limit=limit
    )
    
    return notifications


@router.get("/count", response_model=NotificationCountResponse)
async def get_unread_count(user: dict = Depends(get_current_user)):
    """Obține numărul de notificări necitite"""
    if not user:
        raise HTTPException(status_code=401, detail="Autentificare necesară")
    
    count = await notification_service.get_unread_count(user["user_id"])
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    user: dict = Depends(get_current_user)
):
    """Marchează o notificare ca citită"""
    if not user:
        raise HTTPException(status_code=401, detail="Autentificare necesară")
    
    success = await notification_service.mark_as_read(user["user_id"], notification_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notificare negăsită")
    
    return {"success": True, "message": "Notificare marcată ca citită"}


@router.post("/read-all")
async def mark_all_notifications_read(user: dict = Depends(get_current_user)):
    """Marchează toate notificările ca citite"""
    if not user:
        raise HTTPException(status_code=401, detail="Autentificare necesară")
    
    count = await notification_service.mark_all_as_read(user["user_id"])
    
    return {"success": True, "marked_count": count}


@router.get("/check-expirations")
async def check_subscription_expirations(user: dict = Depends(get_current_user)):
    """Manual trigger pentru verificare expirări (doar admin)"""
    if not user:
        raise HTTPException(status_code=401, detail="Autentificare necesară")
    
    # Verifică dacă e admin
    from config.database import get_database
    db = await get_database()
    user_data = await db.users.find_one({"user_id": user["user_id"]})
    
    if not user_data or not user_data.get("is_admin"):
        raise HTTPException(status_code=403, detail="Acces permis doar pentru administratori")
    
    results = await notification_service.check_expiring_subscriptions()
    
    return {
        "success": True,
        "message": "Verificare expirări completă",
        "results": results
    }
