"""Stripe Payment Integration pentru FinRomania PRO"""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timezone, timedelta
import os
import logging
from config.database import get_database
from routes.auth import get_current_user_optional
from utils.stripe_checkout import StripeCheckout, CheckoutSessionRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payments", tags=["Payments"])

# PRO Subscription Packages cu Stripe Price IDs
SUBSCRIPTION_PACKAGES = {
    "pro_monthly": {
        "stripe_price_id": "price_1SpR6gHYGAlAOMyTTxLNRB9a",
        "amount": 49.0,
        "currency": "RON",
        "duration_days": 30,
        "name": "PRO Lunar",
        "description": "Abonament PRO recurent lunar - 49 RON/lună"
    },
    "pro_yearly": {
        "stripe_price_id": "price_1SpRAtHYGAlAOMyTxwQNbG0N",
        "amount": 490.0,
        "currency": "RON",
        "duration_days": 365,
        "name": "PRO Anual",
        "description": "Abonament PRO recurent anual - 490 RON/an (2 luni gratuite!)"
    }
}


class CheckoutRequest(BaseModel):
    package_id: str  # 'pro_monthly' or 'pro_yearly'
    origin_url: str  # Frontend URL pentru redirect


@router.post("/checkout")
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Creează sesiune Stripe checkout pentru PRO subscription
    """
    try:
        # Validate package
        if request.package_id not in SUBSCRIPTION_PACKAGES:
            raise HTTPException(status_code=400, detail="Pachet invalid")
        
        package = SUBSCRIPTION_PACKAGES[request.package_id]
        
        # Get Stripe API key
        api_key = os.environ.get("STRIPE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Stripe not configured")
        
        # Build webhook URL
        webhook_url = f"{request.origin_url}/api/webhook/stripe"
        
        # Initialize Stripe
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        # Build success/cancel URLs
        success_url = f"{request.origin_url}/payment/success?session_id={{{{CHECKOUT_SESSION_ID}}}}"
        cancel_url = f"{request.origin_url}/pricing"
        
        # Metadata pentru identificare
        metadata = {
            "package_id": request.package_id,
            "user_id": current_user.get("user_id") if current_user else "anonymous",
            "email": current_user.get("email") if current_user else "none",
            "duration_days": str(package["duration_days"])
        }
        
        # Create checkout session cu Stripe Price ID (subscription recurent)
        checkout_request = CheckoutSessionRequest(
            stripe_price_id=package["stripe_price_id"],
            quantity=1,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Save transaction in database
        db = await get_database()
        await db.payment_transactions.insert_one({
            "session_id": session.session_id,
            "user_id": current_user.get("user_id") if current_user else None,
            "email": current_user.get("email") if current_user else None,
            "package_id": request.package_id,
            "amount": package["amount"],
            "currency": package["currency"],
            "payment_status": "pending",
            "status": "initiated",
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"Checkout session created: {session.session_id} for {current_user.get('email') if current_user else 'anonymous'}")
        
        return {
            "url": session.url,
            "session_id": session.session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{session_id}")
async def get_payment_status(session_id: str):
    """
    Verifică status-ul plății
    """
    try:
        api_key = os.environ.get("STRIPE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Stripe not configured")
        
        # Initialize Stripe
        webhook_url = "https://placeholder.com/webhook"  # Not used for status check
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        # Get checkout status from Stripe
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        db = await get_database()
        
        # Find transaction
        transaction = await db.payment_transactions.find_one(
            {"session_id": session_id},
            {"_id": 0}
        )
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Update transaction if status changed and not already processed
        if checkout_status.payment_status == "paid" and transaction.get("payment_status") != "paid":
            # Update subscription ONLY if not already done
            user_id = transaction.get("user_id")
            if user_id:
                package_id = transaction.get("package_id")
                package = SUBSCRIPTION_PACKAGES.get(package_id, SUBSCRIPTION_PACKAGES["pro_monthly"])
                
                expires_at = datetime.now(timezone.utc) + timedelta(days=package["duration_days"])
                
                # Update user to PRO
                await db.users.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "subscription_level": "pro",
                        "subscription_expires_at": expires_at.isoformat(),
                        "experience_level": "advanced",
                        "unlocked_levels": ["beginner", "intermediate", "advanced"],
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                
                logger.info(f"User {transaction.get('email')} upgraded to PRO via Stripe")
            
            # Update transaction
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "payment_status": checkout_status.payment_status,
                    "status": checkout_status.status,
                    "amount_total": checkout_status.amount_total,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
        
        return {
            "session_id": session_id,
            "payment_status": checkout_status.payment_status,
            "status": checkout_status.status,
            "package": transaction.get("package_id"),
            "amount": transaction.get("amount"),
            "currency": transaction.get("currency")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
