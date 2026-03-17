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
    Vizualizează rezumatul zilnic fără a-l trimite.
    Util pentru preview și testare.
    """
    try:
        # Colectează datele
        market_data = await daily_summary_service.get_market_data()
        if not market_data:
            raise HTTPException(status_code=404, detail="Nu sunt date de piață disponibile")
        
        # Generează rezumatul AI
        ai_summary = await daily_summary_service.generate_ai_summary(market_data)
        
        return {
            "success": True,
            "date": market_data["date"],
            "market_data": {
                "avg_change": market_data["avg_change"],
                "sentiment": market_data["sentiment"],
                "top_gainers": [
                    {"symbol": s.get("symbol"), "name": s.get("name"), "change": s.get("change_percent")}
                    for s in market_data["top_gainers"]
                ],
                "top_losers": [
                    {"symbol": s.get("symbol"), "name": s.get("name"), "change": s.get("change_percent")}
                    for s in market_data["top_losers"]
                ],
                "top_volume": [
                    {"symbol": s.get("symbol"), "volume": s.get("volume")}
                    for s in market_data["top_volume"]
                ]
            },
            "ai_summary": ai_summary
        }
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
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
