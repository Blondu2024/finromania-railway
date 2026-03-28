"""Drop-in replacement for emergentintegrations.payments.stripe.checkout using Stripe SDK directly"""
import stripe
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

@dataclass
class CheckoutSessionRequest:
    success_url: str = ""
    cancel_url: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Subscription mode (pass stripe_price_id)
    stripe_price_id: Optional[str] = None
    quantity: int = 1
    # One-time payment mode (pass amount + currency)
    amount: Optional[float] = None
    price: Optional[float] = None  # alias for amount (legacy)
    currency: str = "RON"
    product_name: Optional[str] = None
    product_description: Optional[str] = None

@dataclass
class CheckoutSessionResponse:
    session_id: str
    id: str  # alias for session_id (legacy)
    url: str

@dataclass
class CheckoutStatusResponse:
    payment_status: str
    status: str
    amount_total: Optional[int] = None
    session_id: Optional[str] = None

class StripeCheckout:
    def __init__(self, api_key: str, webhook_url: str = None):
        self.api_key = api_key
        self.webhook_url = webhook_url
        stripe.api_key = api_key

    async def create_checkout_session(self, request: CheckoutSessionRequest) -> CheckoutSessionResponse:
        try:
            if request.stripe_price_id:
                # Subscription mode
                session = stripe.checkout.Session.create(
                    mode="subscription",
                    line_items=[{"price": request.stripe_price_id, "quantity": request.quantity}],
                    success_url=request.success_url,
                    cancel_url=request.cancel_url,
                    metadata=request.metadata or {},
                )
            else:
                # One-time payment mode
                amount_value = request.amount or request.price or 0
                amount_cents = int(amount_value * 100)
                product_data = {"name": request.product_name or "FinRomania PRO"}
                if request.product_description:
                    product_data["description"] = request.product_description
                session = stripe.checkout.Session.create(
                    mode="payment",
                    line_items=[{
                        "price_data": {
                            "currency": request.currency.lower(),
                            "product_data": product_data,
                            "unit_amount": amount_cents,
                        },
                        "quantity": request.quantity,
                    }],
                    success_url=request.success_url,
                    cancel_url=request.cancel_url,
                    metadata=request.metadata or {},
                )
            return CheckoutSessionResponse(
                session_id=session.id,
                id=session.id,
                url=session.url,
            )
        except Exception as e:
            logger.error(f"Stripe checkout error: {e}")
            raise

    async def get_checkout_status(self, session_id: str) -> CheckoutStatusResponse:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return CheckoutStatusResponse(
                payment_status=session.payment_status or "unpaid",
                status=session.status or "open",
                amount_total=session.amount_total,
                session_id=session.id,
            )
        except Exception as e:
            logger.error(f"Stripe status error: {e}")
            raise

    async def handle_webhook(self, body: bytes, signature: str) -> CheckoutStatusResponse:
        import os
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        try:
            if webhook_secret:
                event = stripe.Webhook.construct_event(body, signature, webhook_secret)
            else:
                import json
                event = stripe.Event.construct_from(json.loads(body), stripe.api_key)

            session_id = None
            payment_status = "unpaid"
            status = "open"

            if event.type in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
                session = event.data.object
                session_id = session.id
                payment_status = session.payment_status or "paid"
                status = session.status or "complete"

            return CheckoutStatusResponse(
                payment_status=payment_status,
                status=status,
                session_id=session_id,
            )
        except Exception as e:
            logger.error(f"Stripe webhook error: {e}")
            raise
