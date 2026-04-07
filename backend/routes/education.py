"""Education routes pentru FinRomania - Curs și E-Book"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid
import os
from config.database import get_database
from routes.auth import get_current_user, require_auth
from utils.stripe_checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from routes.education_data import EDUCATION_PACKAGES, COURSE_LESSONS, GLOSSARY

router = APIRouter(prefix="/education", tags=["education"])

class CheckoutRequest(BaseModel):
    origin_url: str
    package_id: str = "starter"  # starter or premium

class LessonProgress(BaseModel):
    lesson_id: str
    completed: bool = False
    quiz_score: Optional[int] = None

@router.get("/packages")
async def get_education_packages():
    """Get all available education packages"""
    packages = []
    for key, pkg in EDUCATION_PACKAGES.items():
        lesson_count = len(pkg["lessons_included"]) if isinstance(pkg["lessons_included"], list) else len(COURSE_LESSONS)
        packages.append({
            **pkg,
            "lessons_count": lesson_count
        })
    return {"packages": packages}

@router.get("/package")
async def get_education_package(package_id: str = "starter"):
    """Get specific education package details"""
    pkg = EDUCATION_PACKAGES.get(package_id)
    if not pkg:
        raise HTTPException(status_code=404, detail="Pachet negăsit")
    
    lesson_count = len(pkg["lessons_included"]) if isinstance(pkg["lessons_included"], list) else len(COURSE_LESSONS)
    return {
        **pkg,
        "lessons_count": lesson_count,
        "includes": pkg.get("features", [])
    }

@router.get("/lessons")
async def get_lessons(request: Request, package_id: str = None):
    """Get all lessons - content based on user's purchase"""
    user = await get_current_user(request)
    
    # Check what user has purchased
    has_starter = False
    has_premium = False
    
    if user:
        db = await get_database()
        purchases = await db.education_purchases.find({
            "user_id": user["user_id"],
            "status": "completed"
        }).to_list(10)
        
        for purchase in purchases:
            if purchase.get("package_id") == "edu_premium_pack":
                has_premium = True
            elif purchase.get("package_id") == "edu_starter_pack":
                has_starter = True
    
    lessons = []
    for lesson in COURSE_LESSONS:
        tier = lesson.get("tier", "starter")
        
        # Determine if lesson is accessible
        is_free = tier == "free"
        is_starter = tier == "starter"
        is_premium = tier == "premium"
        
        can_access = is_free or \
                     (is_starter and (has_starter or has_premium)) or \
                     (is_premium and has_premium)
        
        lesson_data = {
            "id": lesson["id"],
            "order": lesson["order"],
            "title": lesson["title"],
            "description": lesson["description"],
            "duration": lesson["duration"],
            "tier": tier,
            "is_free": is_free,
            "is_locked": not can_access,
            "has_quiz": "quiz" in lesson
        }
        
        # Include content only if user has access
        if can_access:
            lesson_data["content"] = lesson["content"]
            if "quiz" in lesson:
                lesson_data["quiz"] = lesson["quiz"]
        
        lessons.append(lesson_data)
    
    return {
        "lessons": lessons,
        "has_starter": has_starter,
        "has_premium": has_premium,
        "total_lessons": len(lessons),
        "free_lessons": sum(1 for l in COURSE_LESSONS if l.get("tier") == "free"),
        "starter_lessons": sum(1 for l in COURSE_LESSONS if l.get("tier") in ["free", "starter"]),
        "premium_lessons": len(COURSE_LESSONS)
    }

@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str, request: Request):
    """Get single lesson content"""
    user = await get_current_user(request)
    
    lesson = next((l for l in COURSE_LESSONS if l["id"] == lesson_id), None)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lecția nu a fost găsită")
    
    tier = lesson.get("tier", "starter")
    
    # Check access
    can_access = tier == "free"
    
    if not can_access and user:
        db = await get_database()
        purchases = await db.education_purchases.find({
            "user_id": user["user_id"],
            "status": "completed"
        }).to_list(10)
        
        for purchase in purchases:
            if purchase.get("package_id") == "edu_premium_pack":
                can_access = True
                break
            elif purchase.get("package_id") == "edu_starter_pack" and tier in ["free", "starter"]:
                can_access = True
                break
    
    if not can_access:
        raise HTTPException(status_code=403, detail="Trebuie să achiziționezi pachetul pentru această lecție")
    
    return lesson

@router.get("/glossary")
async def get_glossary(search: str = None):
    """Get glossary of financial terms"""
    if search:
        filtered = {k: v for k, v in GLOSSARY.items() if search.lower() in k.lower() or search.lower() in v.lower()}
        return {"terms": filtered, "total": len(filtered)}
    return {"terms": GLOSSARY, "total": len(GLOSSARY)}

@router.post("/quiz/{lesson_id}/submit")
async def submit_quiz(lesson_id: str, answers: List[int], user: dict = Depends(require_auth)):
    """Submit quiz answers and get score"""
    lesson = next((l for l in COURSE_LESSONS if l["id"] == lesson_id), None)
    if not lesson or "quiz" not in lesson:
        raise HTTPException(status_code=404, detail="Quiz negăsit")
    
    quiz = lesson["quiz"]
    if len(answers) != len(quiz):
        raise HTTPException(status_code=400, detail="Număr incorect de răspunsuri")
    
    correct = sum(1 for i, a in enumerate(answers) if a == quiz[i]["correct"])
    score = int((correct / len(quiz)) * 100)
    passed = score >= 70
    
    # Save progress
    db = await get_database()
    await db.lesson_progress.update_one(
        {"user_id": user["user_id"], "lesson_id": lesson_id},
        {"$set": {
            "quiz_score": score,
            "quiz_passed": passed,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    return {
        "score": score,
        "correct": correct,
        "total": len(quiz),
        "passed": passed,
        "message": "Felicitări! Ai trecut quiz-ul!" if passed else "Mai încearcă! Trebuie minim 70%."
    }

@router.post("/checkout")
async def create_checkout(data: CheckoutRequest, request: Request):
    """Create Stripe checkout session for education package"""
    user = await get_current_user(request)
    
    if not user:
        raise HTTPException(status_code=401, detail="Trebuie să fii autentificat pentru a cumpăra")
    
    # Get package
    pkg = EDUCATION_PACKAGES.get(data.package_id)
    if not pkg:
        raise HTTPException(status_code=400, detail="Pachet invalid")
    
    db = await get_database()
    
    # Check if already purchased this package
    existing = await db.education_purchases.find_one({
        "user_id": user["user_id"],
        "package_id": pkg["id"],
        "status": "completed"
    })
    if existing:
        raise HTTPException(status_code=400, detail="Ai achiziționat deja acest pachet")
    
    # Initialize Stripe
    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
    
    # Build URLs from frontend origin
    success_url = f"{data.origin_url}/education/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{data.origin_url}/education"
    
    # Create checkout session
    checkout_request = CheckoutSessionRequest(
        amount=pkg["price"],
        currency=pkg["currency"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user["user_id"],
            "user_email": user["email"],
            "package_id": pkg["id"],
            "package_name": pkg["name"],
            "product_type": "education_package"
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create pending transaction record
    await db.payment_transactions.insert_one({
        "id": f"txn_{uuid.uuid4().hex[:12]}",
        "session_id": session.session_id,
        "user_id": user["user_id"],
        "email": user["email"],
        "amount": pkg["price"],
        "currency": pkg["currency"],
        "product_type": "education_package",
        "package_id": pkg["id"],
        "package_name": pkg["name"],
        "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "url": session.url,
        "session_id": session.session_id
    }

@router.get("/checkout/status/{session_id}")
async def check_checkout_status(session_id: str, request: Request):
    """Check payment status and grant access if paid"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db = await get_database()
    
    # Get transaction
    transaction = await db.payment_transactions.find_one({
        "session_id": session_id,
        "user_id": user["user_id"]
    })
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # If already completed, return success
    if transaction.get("payment_status") == "paid":
        return {
            "status": "complete",
            "payment_status": "paid",
            "access_granted": True
        }
    
    # Check with Stripe
    api_key = os.environ.get("STRIPE_API_KEY")
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
    
    status = await stripe_checkout.get_checkout_status(session_id)
    
    # Update transaction
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": {
            "payment_status": status.payment_status,
            "status": status.status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # If paid, grant access (only once)
    if status.payment_status == "paid":
        existing_purchase = await db.education_purchases.find_one({
            "session_id": session_id
        })
        
        if not existing_purchase:
            await db.education_purchases.insert_one({
                "id": f"edu_{uuid.uuid4().hex[:12]}",
                "user_id": user["user_id"],
                "email": user["email"],
                "session_id": session_id,
                "package_id": transaction.get("package_id"),
                "package_name": transaction.get("package_name"),
                "amount": transaction.get("amount"),
                "currency": transaction.get("currency"),
                "status": "completed",
                "purchased_at": datetime.now(timezone.utc).isoformat()
            })
    
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "access_granted": status.payment_status == "paid"
    }

@router.get("/my-access")
async def check_my_access(user: dict = Depends(require_auth)):
    """Check current user's access to education content"""
    db = await get_database()
    purchases = await db.education_purchases.find({
        "user_id": user["user_id"],
        "status": "completed"
    }, {"_id": 0}).to_list(10)
    
    has_starter = any(p.get("package_id") == "edu_starter_pack" for p in purchases)
    has_premium = any(p.get("package_id") == "edu_premium_pack" for p in purchases)
    
    return {
        "has_starter": has_starter,
        "has_premium": has_premium,
        "purchases": purchases
    }

@router.get("/my-progress")
async def get_my_progress(user: dict = Depends(require_auth)):
    """Get user's course progress"""
    db = await get_database()
    progress = await db.lesson_progress.find({
        "user_id": user["user_id"]
    }, {"_id": 0}).to_list(50)
    
    completed = len(progress)
    total = len(COURSE_LESSONS)
    
    return {
        "completed_lessons": completed,
        "total_lessons": total,
        "progress_percent": int((completed / total) * 100) if total > 0 else 0,
        "lessons": progress
    }
