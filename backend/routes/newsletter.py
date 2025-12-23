"""Newsletter routes pentru FinRomania"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
import uuid
from config.database import get_database

router = APIRouter(prefix="/newsletter", tags=["newsletter"])

class NewsletterSubscribe(BaseModel):
    email: EmailStr
    name: Optional[str] = None

from typing import Optional

@router.post("/subscribe")
async def subscribe(data: NewsletterSubscribe):
    """Subscribe to newsletter"""
    db = await get_database()
    
    # Check if already subscribed
    existing = await db.newsletter.find_one({"email": data.email})
    if existing:
        if existing.get("active"):
            return {"message": "Already subscribed", "status": "exists"}
        else:
            # Reactivate
            await db.newsletter.update_one(
                {"email": data.email},
                {"$set": {"active": True, "resubscribed_at": datetime.now(timezone.utc).isoformat()}}
            )
            return {"message": "Subscription reactivated", "status": "reactivated"}
    
    # New subscription
    await db.newsletter.insert_one({
        "id": f"nl_{uuid.uuid4().hex[:12]}",
        "email": data.email,
        "name": data.name,
        "active": True,
        "subscribed_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Successfully subscribed", "status": "subscribed"}

@router.post("/unsubscribe")
async def unsubscribe(email: str):
    """Unsubscribe from newsletter"""
    db = await get_database()
    
    result = await db.newsletter.update_one(
        {"email": email},
        {"$set": {"active": False, "unsubscribed_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Email not found")
    
    return {"message": "Successfully unsubscribed"}
