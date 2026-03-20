"""
Daily Summary Routes
Endpoint-uri pentru rezumatul zilnic BVB
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from config.database import get_database
from services.daily_summary_service import daily_summary_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/daily-summary", tags=["daily-summary"])


class SubscribeRequest(BaseModel):
    """Request pentru abonare la rezumatul zilnic"""
    email: EmailStr
    user_id: Optional[str] = None


class TestEmailRequest(BaseModel):
    """Request pentru test email"""
    email: EmailStr


@router.get("/preview")
async def preview_daily_summary():
    """
    Obține rezumatul zilnic pentru afișare.
    
    LOGICA:
    1. Dacă există un rezumat salvat pentru azi în DB, îl returnează (RAPID, fără AI)
    2. Dacă nu există, generează unul temporar (mai lent, apel AI)
    
    Rezumatul oficial se generează și salvează automat la 18:10 de către job-ul scheduler.
    """
    try:
        # Folosește noua metodă care servește din cache
        summary = await daily_summary_service.get_summary_for_display()
        
        if not summary:
            raise HTTPException(status_code=404, detail="Nu sunt date de piață disponibile")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting daily summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def force_generate_summary():
    """
    Forțează generarea și salvarea rezumatului zilnic.
    Util pentru admin sau pentru testare.
    """
    try:
        summary = await daily_summary_service.generate_and_save_daily_summary()
        if not summary:
            raise HTTPException(status_code=500, detail="Nu s-a putut genera rezumatul")
        return {"success": True, "message": "Rezumat generat și salvat", "date": summary.get("date")}
    except Exception as e:
        logger.error(f"Error forcing summary generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-email")
async def send_test_email(request: TestEmailRequest):
    """
    Trimite un email de test cu rezumatul zilnic.
    Doar pentru testare!
    """
    try:
        success = await daily_summary_service.send_daily_summary(
            user_email=request.email,
            user_name="Test User",
            is_pro=True  # Trimitem versiunea PRO pentru test
        )
        
        if success:
            return {"success": True, "message": f"Email trimis cu succes la {request.email}"}
        else:
            raise HTTPException(status_code=500, detail="Eroare la trimiterea emailului")
            
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscribe")
async def subscribe_to_daily_summary(request: SubscribeRequest):
    """
    Abonează un user la rezumatul zilnic.
    """
    db = await get_database()
    
    try:
        # Actualizează preferințele userului
        if request.user_id:
            result = await db.users.update_one(
                {"user_id": request.user_id},
                {
                    "$set": {
                        "daily_summary_enabled": True,
                        "email": request.email
                    }
                }
            )
        else:
            # Creează sau actualizează un subscriber anonim
            result = await db.daily_summary_subscribers.update_one(
                {"email": request.email},
                {
                    "$set": {
                        "email": request.email,
                        "subscribed": True,
                        "subscribed_at": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
                    }
                },
                upsert=True
            )
        
        return {
            "success": True,
            "message": f"Te-ai abonat cu succes la Rezumatul Zilei BVB! Vei primi emailul zilnic la {request.email} după închiderea pieței (18:15)."
        }
        
    except Exception as e:
        logger.error(f"Error subscribing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unsubscribe")
async def unsubscribe_from_daily_summary(request: SubscribeRequest):
    """
    Dezabonează un user de la rezumatul zilnic.
    """
    db = await get_database()
    
    try:
        if request.user_id:
            await db.users.update_one(
                {"user_id": request.user_id},
                {"$set": {"daily_summary_enabled": False}}
            )
        else:
            await db.daily_summary_subscribers.update_one(
                {"email": request.email},
                {"$set": {"subscribed": False}}
            )
        
        return {
            "success": True,
            "message": "Te-ai dezabonat de la Rezumatul Zilei BVB."
        }
        
    except Exception as e:
        logger.error(f"Error unsubscribing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscribers/count")
async def get_subscribers_count():
    """Returnează numărul de abonați."""
    db = await get_database()
    
    # Count users with daily_summary_enabled
    users_count = await db.users.count_documents({"daily_summary_enabled": True})
    
    # Count anonymous subscribers
    anon_count = await db.daily_summary_subscribers.count_documents({"subscribed": True})
    
    return {
        "total": users_count + anon_count,
        "registered_users": users_count,
        "anonymous": anon_count
    }
