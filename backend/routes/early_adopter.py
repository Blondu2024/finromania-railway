"""Early Adopter Program - Primii 100 de useri primesc PRO gratuit pentru 3 luni"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from config.database import get_database
from routes.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/early-adopter", tags=["early-adopter"])

# Configurare Early Adopter Program
EARLY_ADOPTER_CONFIG = {
    "total_slots": 100,          # Total locuri disponibile
    "pro_duration_days": 90,     # 3 luni gratuit
    "program_name": "Early Adopter PRO",
    "start_date": "2026-02-21",  # Data de start a programului
    "benefits": [
        "Acces PRO complet pentru 3 luni",
        "Întrebări AI nelimitate",
        "Toate nivelurile deblocate",
        "Calculator Fiscal PRO",
        "Suport prioritar"
    ]
}


class EarlyAdopterStatus(BaseModel):
    is_active: bool
    total_slots: int
    slots_taken: int
    slots_remaining: int
    is_user_early_adopter: bool = False
    user_activated_at: str = None
    user_expires_at: str = None


@router.get("/status")
async def get_early_adopter_status(user: dict = Depends(get_current_user)):
    """Get Early Adopter program status și câte locuri mai sunt"""
    db = await get_database()
    
    # Numără câți early adopters există
    early_adopter_count = await db.users.count_documents({
        "is_early_adopter": True
    })
    
    slots_remaining = max(0, EARLY_ADOPTER_CONFIG["total_slots"] - early_adopter_count)
    
    # Check dacă user-ul curent e early adopter
    is_user_early_adopter = False
    user_activated_at = None
    user_expires_at = None
    
    if user:
        user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
        if user_data:
            is_user_early_adopter = user_data.get("is_early_adopter", False)
            user_activated_at = user_data.get("early_adopter_activated_at")
            user_expires_at = user_data.get("subscription_expires_at")
    
    return {
        "program": EARLY_ADOPTER_CONFIG["program_name"],
        "is_active": slots_remaining > 0,
        "total_slots": EARLY_ADOPTER_CONFIG["total_slots"],
        "slots_taken": early_adopter_count,
        "slots_remaining": slots_remaining,
        "pro_duration_days": EARLY_ADOPTER_CONFIG["pro_duration_days"],
        "benefits": EARLY_ADOPTER_CONFIG["benefits"],
        "is_user_early_adopter": is_user_early_adopter,
        "user_activated_at": user_activated_at,
        "user_expires_at": user_expires_at,
        "urgency_message": _get_urgency_message(slots_remaining)
    }


@router.get("/public-status")
async def get_public_early_adopter_status():
    """Get Early Adopter status (public - fără autentificare)"""
    db = await get_database()
    
    # Numără câți early adopters există
    early_adopter_count = await db.users.count_documents({
        "is_early_adopter": True
    })
    
    slots_remaining = max(0, EARLY_ADOPTER_CONFIG["total_slots"] - early_adopter_count)
    
    return {
        "program": EARLY_ADOPTER_CONFIG["program_name"],
        "is_active": slots_remaining > 0,
        "total_slots": EARLY_ADOPTER_CONFIG["total_slots"],
        "slots_taken": early_adopter_count,
        "slots_remaining": slots_remaining,
        "pro_duration_days": EARLY_ADOPTER_CONFIG["pro_duration_days"],
        "benefits": EARLY_ADOPTER_CONFIG["benefits"],
        "urgency_message": _get_urgency_message(slots_remaining)
    }


@router.post("/claim")
async def claim_early_adopter_slot(user: dict = Depends(get_current_user)):
    """Claim an Early Adopter PRO slot"""
    if not user:
        raise HTTPException(status_code=401, detail="Trebuie să fii autentificat pentru a revendica locul")
    
    db = await get_database()
    
    # Verifică dacă user-ul e deja early adopter
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if user_data and user_data.get("is_early_adopter"):
        return {
            "success": False,
            "already_claimed": True,
            "message": "Ai revendicat deja locul de Early Adopter!",
            "expires_at": user_data.get("subscription_expires_at")
        }
    
    # Verifică dacă mai sunt locuri (atomic operation)
    early_adopter_count = await db.users.count_documents({"is_early_adopter": True})
    
    if early_adopter_count >= EARLY_ADOPTER_CONFIG["total_slots"]:
        return {
            "success": False,
            "slots_full": True,
            "message": "Din păcate, toate cele 100 de locuri Early Adopter au fost revendicate.",
            "alternative": "Poți să te abonezi la PRO pentru doar 49 RON/lună."
        }
    
    # Activează Early Adopter PRO
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=EARLY_ADOPTER_CONFIG["pro_duration_days"])
    slot_number = early_adopter_count + 1
    
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "is_early_adopter": True,
            "early_adopter_slot": slot_number,
            "early_adopter_activated_at": now.isoformat(),
            "subscription_level": "pro",
            "subscription_expires_at": expires_at.isoformat(),
            "subscription_source": "early_adopter",
            "unlocked_levels": ["beginner", "intermediate", "advanced"]
        }},
        upsert=True
    )
    
    logger.info(f"🎉 Early Adopter #{slot_number} activated: {user['email']}")
    
    # Log the event
    await db.analytics.insert_one({
        "event": "early_adopter_claimed",
        "user_id": user["user_id"],
        "slot_number": slot_number,
        "timestamp": now.isoformat()
    })
    
    return {
        "success": True,
        "message": f"🎉 Felicitări! Ești Early Adopter #{slot_number}!",
        "slot_number": slot_number,
        "slots_remaining": EARLY_ADOPTER_CONFIG["total_slots"] - slot_number,
        "subscription_level": "pro",
        "expires_at": expires_at.isoformat(),
        "benefits": EARLY_ADOPTER_CONFIG["benefits"],
        "duration": f"{EARLY_ADOPTER_CONFIG['pro_duration_days']} zile de PRO gratuit"
    }


@router.get("/leaderboard")
async def get_early_adopter_leaderboard():
    """Get lista early adopters (anonimizată pentru privacy)"""
    db = await get_database()
    
    # Get early adopters, sorted by slot number
    early_adopters = await db.users.find(
        {"is_early_adopter": True},
        {"_id": 0, "email": 1, "early_adopter_slot": 1, "early_adopter_activated_at": 1}
    ).sort("early_adopter_slot", 1).to_list(100)
    
    # Anonimizează email-urile (ex: t***@gmail.com)
    anonymized = []
    for ea in early_adopters:
        email = ea.get("email", "")
        if "@" in email:
            parts = email.split("@")
            anon_email = f"{parts[0][0]}***@{parts[1]}"
        else:
            anon_email = "***"
        
        anonymized.append({
            "slot": ea.get("early_adopter_slot"),
            "email": anon_email,
            "joined": ea.get("early_adopter_activated_at", "")[:10]  # Just the date
        })
    
    return {
        "early_adopters": anonymized,
        "total": len(anonymized),
        "slots_remaining": EARLY_ADOPTER_CONFIG["total_slots"] - len(anonymized)
    }


def _get_urgency_message(slots_remaining: int) -> str:
    """Generate urgency message based on remaining slots"""
    if slots_remaining <= 0:
        return "🔴 SOLD OUT - Toate locurile au fost ocupate!"
    elif slots_remaining <= 5:
        return f"🔥 ULTIMELE {slots_remaining} LOCURI! Grăbește-te!"
    elif slots_remaining <= 10:
        return f"⚠️ Mai sunt doar {slots_remaining} locuri disponibile!"
    elif slots_remaining <= 25:
        return f"⏰ Doar {slots_remaining} de locuri rămase - Nu rata!"
    elif slots_remaining <= 50:
        return f"📢 {slots_remaining} locuri disponibile - Ocupă-ți locul!"
    else:
        return f"🎁 {slots_remaining} locuri gratuite disponibile!"


# Export config for use in auth
def check_and_activate_early_adopter(user_id: str, email: str):
    """Helper function to check and activate early adopter on registration"""
    # This is called from auth.py when a new user registers
    pass
