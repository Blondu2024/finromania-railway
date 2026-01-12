"""Subscription Management & AI Query Limits"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import os
from config.database import get_database
from routes.auth import require_auth

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class SubscriptionLevel(str, Enum):
    FREE = "free"
    PRO = "pro"


class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"      # Începător
    INTERMEDIATE = "intermediate"  # Mediu
    ADVANCED = "advanced"      # Expert


# Pricing
PRICING = {
    "pro_monthly": {
        "price": 49.00,
        "currency": "RON",
        "period": "monthly",
        "stripe_price_id": "price_pro_monthly"
    },
    "pro_yearly": {
        "price": 490.00,
        "currency": "RON",
        "period": "yearly",
        "stripe_price_id": "price_pro_yearly",
        "savings": "2 luni gratuite"
    }
}

# AI Query Limits
AI_LIMITS = {
    SubscriptionLevel.FREE: 5,  # 5 queries per day
    SubscriptionLevel.PRO: -1   # Unlimited (-1 = no limit)
}

# Experience Level Access
LEVEL_ACCESS = {
    ExperienceLevel.BEGINNER: {
        "features": ["basic_charts", "dividends", "bet_stocks", "basic_ai"],
        "ai_context": "Doar acțiuni BET, focus pe dividende, explicații simple",
        "stock_filter": "BET",  # Doar acțiuni din indicele BET
        "indicators": ["price", "volume", "dividend_yield"],
        "quiz_required": False
    },
    ExperienceLevel.INTERMEDIATE: {
        "features": ["technical_indicators", "global_stocks", "portfolio", "advanced_ai"],
        "ai_context": "Indicatori tehnici (RSI, MA, MACD), BVB + Internațional",
        "stock_filter": "ALL_BVB",  # Toate acțiunile BVB
        "indicators": ["price", "volume", "rsi", "ma", "macd", "dividend_yield"],
        "quiz_required": True,
        "quiz_pass_score": 7  # 7 din 10
    },
    ExperienceLevel.ADVANCED: {
        "features": ["fundamental_data", "all_markets", "advanced_portfolio", "expert_ai", "chart_drawing"],
        "ai_context": "Analiză fundamentală completă, bilanțuri, cash flow, strategii avansate",
        "stock_filter": "ALL",  # Toate piețele
        "indicators": ["all"],
        "quiz_required": True,
        "quiz_pass_score": 7  # 7 din 10
    }
}


class SubscriptionUpdate(BaseModel):
    level: SubscriptionLevel


class ExperienceLevelUpdate(BaseModel):
    level: ExperienceLevel


# ============================================
# SUBSCRIPTION ENDPOINTS
# ============================================

@router.get("/status")
async def get_subscription_status(user: dict = Depends(require_auth)):
    """Get user's subscription and experience level status"""
    db = await get_database()
    
    user_data = await db.users.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not user_data:
        # Initialize user subscription data
        user_data = {
            "user_id": user["user_id"],
            "subscription_level": SubscriptionLevel.FREE,
            "experience_level": ExperienceLevel.BEGINNER,
            "ai_queries_today": 0,
            "ai_queries_reset_at": datetime.now(timezone.utc).isoformat(),
            "unlocked_levels": [ExperienceLevel.BEGINNER],
            "quiz_scores": {},
            "subscription_expires_at": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": user_data},
            upsert=True
        )
    
    # Check if queries should reset (new day)
    reset_at = user_data.get("ai_queries_reset_at")
    if reset_at:
        reset_time = datetime.fromisoformat(reset_at.replace("Z", "+00:00")) if isinstance(reset_at, str) else reset_at
        if datetime.now(timezone.utc) - reset_time > timedelta(hours=24):
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": {
                    "ai_queries_today": 0,
                    "ai_queries_reset_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            user_data["ai_queries_today"] = 0
    
    subscription_level = user_data.get("subscription_level", SubscriptionLevel.FREE)
    experience_level = user_data.get("experience_level", ExperienceLevel.BEGINNER)
    
    # Get limits
    ai_limit = AI_LIMITS.get(subscription_level, 5)
    ai_used = user_data.get("ai_queries_today", 0)
    ai_remaining = -1 if ai_limit == -1 else max(0, ai_limit - ai_used)
    
    # Get level access info
    level_access = LEVEL_ACCESS.get(experience_level, LEVEL_ACCESS[ExperienceLevel.BEGINNER])
    
    return {
        "user_id": user["user_id"],
        "subscription": {
            "level": subscription_level,
            "is_pro": subscription_level == SubscriptionLevel.PRO,
            "expires_at": user_data.get("subscription_expires_at")
        },
        "experience": {
            "current_level": experience_level,
            "unlocked_levels": user_data.get("unlocked_levels", [ExperienceLevel.BEGINNER]),
            "features": level_access["features"],
            "ai_context": level_access["ai_context"],
            "stock_filter": level_access["stock_filter"],
            "available_indicators": level_access["indicators"]
        },
        "ai_queries": {
            "used_today": ai_used,
            "limit": ai_limit,
            "remaining": ai_remaining,
            "is_unlimited": ai_limit == -1,
            "resets_at": user_data.get("ai_queries_reset_at")
        },
        "quiz_scores": user_data.get("quiz_scores", {}),
        "pricing": PRICING
    }


@router.post("/use-ai-query")
async def use_ai_query(user: dict = Depends(require_auth)):
    """
    Increment AI query counter. 
    Returns whether the query is allowed.
    """
    db = await get_database()
    
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    subscription_level = user_data.get("subscription_level", SubscriptionLevel.FREE)
    ai_limit = AI_LIMITS.get(subscription_level, 5)
    ai_used = user_data.get("ai_queries_today", 0)
    
    # Check if reset needed
    reset_at = user_data.get("ai_queries_reset_at")
    if reset_at:
        reset_time = datetime.fromisoformat(reset_at.replace("Z", "+00:00")) if isinstance(reset_at, str) else reset_at
        if datetime.now(timezone.utc) - reset_time > timedelta(hours=24):
            ai_used = 0
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": {
                    "ai_queries_today": 0,
                    "ai_queries_reset_at": datetime.now(timezone.utc).isoformat()
                }}
            )
    
    # Check if allowed
    if ai_limit != -1 and ai_used >= ai_limit:
        return {
            "allowed": False,
            "reason": "daily_limit_reached",
            "used": ai_used,
            "limit": ai_limit,
            "upgrade_message": "Ai atins limita de 5 întrebări gratuite pe zi. Treci la PRO pentru acces nelimitat!",
            "pricing": PRICING
        }
    
    # Increment counter
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$inc": {"ai_queries_today": 1}}
    )
    
    return {
        "allowed": True,
        "used": ai_used + 1,
        "limit": ai_limit,
        "remaining": -1 if ai_limit == -1 else ai_limit - ai_used - 1
    }


@router.post("/change-experience-level")
async def change_experience_level(
    data: ExperienceLevelUpdate,
    user: dict = Depends(require_auth)
):
    """Change user's experience level (requires quiz for higher levels)"""
    db = await get_database()
    
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    target_level = data.level
    subscription_level = user_data.get("subscription_level", SubscriptionLevel.FREE)
    unlocked_levels = user_data.get("unlocked_levels", [ExperienceLevel.BEGINNER])
    
    # PRO users can access any level without quiz
    if subscription_level == SubscriptionLevel.PRO:
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {
                "experience_level": target_level,
                "unlocked_levels": list(set(unlocked_levels + [target_level]))
            }}
        )
        return {
            "success": True,
            "level": target_level,
            "message": f"Nivel schimbat la {target_level}. Ca utilizator PRO, ai acces la toate nivelurile."
        }
    
    # Check if level is already unlocked
    if target_level in unlocked_levels:
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"experience_level": target_level}}
        )
        return {
            "success": True,
            "level": target_level,
            "message": f"Nivel schimbat la {target_level}."
        }
    
    # Check if quiz is required
    level_config = LEVEL_ACCESS.get(target_level, {})
    if level_config.get("quiz_required", False):
        return {
            "success": False,
            "reason": "quiz_required",
            "message": f"Pentru a accesa nivelul {target_level}, trebuie să treci quiz-ul (minim 7/10).",
            "quiz_endpoint": f"/api/quiz/{target_level}"
        }
    
    # Update level
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "experience_level": target_level,
            "unlocked_levels": list(set(unlocked_levels + [target_level]))
        }}
    )
    
    return {
        "success": True,
        "level": target_level,
        "message": f"Nivel schimbat la {target_level}."
    }


@router.get("/pricing")
async def get_pricing():
    """Get subscription pricing"""
    return {
        "plans": PRICING,
        "features": {
            "free": {
                "name": "Gratuit",
                "price": "0 RON",
                "features": [
                    "5 întrebări AI pe zi",
                    "Acces nivel Începător",
                    "Date BVB de bază",
                    "Fear & Greed Index",
                    "Știri financiare"
                ]
            },
            "pro": {
                "name": "PRO",
                "price": "49 RON/lună",
                "price_yearly": "490 RON/an (economisești 2 luni)",
                "features": [
                    "Întrebări AI NELIMITATE",
                    "Acces toate nivelurile FĂRĂ quiz",
                    "Indicatori tehnici avansați",
                    "Analiză fundamentală completă",
                    "AI trasează linii pe grafice",
                    "Calculator fiscal PF/SRL",
                    "Portofoliu avansat",
                    "Suport prioritar"
                ]
            }
        },
        "currency": "RON"
    }


# ============================================
# STRIPE INTEGRATION (placeholder)
# ============================================

class CreateCheckoutSession(BaseModel):
    plan: str  # "pro_monthly" or "pro_yearly"


@router.post("/create-checkout")
async def create_checkout_session(
    data: CreateCheckoutSession,
    user: dict = Depends(require_auth)
):
    """Create Stripe checkout session for PRO subscription"""
    try:
        import stripe
        stripe.api_key = os.environ.get("STRIPE_API_KEY")
        
        if not stripe.api_key or stripe.api_key == "sk_test_emergent":
            # Return mock for development
            return {
                "checkout_url": f"/payment-mock?plan={data.plan}&user={user['user_id']}",
                "is_mock": True,
                "message": "Stripe not configured - using mock checkout"
            }
        
        plan_config = PRICING.get(data.plan)
        if not plan_config:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        # Get frontend URL
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": plan_config["stripe_price_id"],
                "quantity": 1
            }],
            mode="subscription",
            success_url=f"{frontend_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{frontend_url}/payment/cancel",
            client_reference_id=user["user_id"],
            metadata={
                "user_id": user["user_id"],
                "plan": data.plan
            }
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def stripe_webhook():
    """Handle Stripe webhook events"""
    # This would be implemented with proper signature verification
    # For now, return placeholder
    return {"received": True}


@router.post("/activate-pro")
async def activate_pro_manually(user: dict = Depends(require_auth)):
    """
    Manual PRO activation (for testing or manual payments)
    In production, this would be triggered by Stripe webhook
    """
    db = await get_database()
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "subscription_level": SubscriptionLevel.PRO,
            "subscription_expires_at": expires_at.isoformat(),
            "unlocked_levels": [
                ExperienceLevel.BEGINNER,
                ExperienceLevel.INTERMEDIATE,
                ExperienceLevel.ADVANCED
            ]
        }},
        upsert=True
    )
    
    return {
        "success": True,
        "subscription_level": SubscriptionLevel.PRO,
        "expires_at": expires_at.isoformat(),
        "message": "Abonament PRO activat cu succes!"
    }
