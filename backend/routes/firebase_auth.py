"""Firebase Authentication pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import asyncio
import logging
import uuid
import os

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth_sdk

from config.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth/firebase", tags=["Firebase Auth"])

# Initialize Firebase Admin SDK
def _init_firebase():
    """Initialize Firebase Admin SDK from environment variables"""
    if firebase_admin._apps:
        return  # Already initialized

    project_id = os.environ.get("FIREBASE_PROJECT_ID", "fin-romania")
    client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
    private_key = os.environ.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")

    if client_email and private_key:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": project_id,
            "private_key": private_key,
            "client_email": client_email,
            "token_uri": "https://oauth2.googleapis.com/token",
        })
        firebase_admin.initialize_app(cred)
        logger.info("✅ Firebase Admin SDK initialized with service account")
    else:
        # Fallback: initialize with just project ID (limited functionality)
        firebase_admin.initialize_app(options={"projectId": project_id})
        logger.warning("⚠️ Firebase Admin SDK initialized WITHOUT service account - token verification disabled")

_init_firebase()


class FirebaseLoginRequest(BaseModel):
    id_token: str
    user_info: dict  # Contains uid, email, name, picture from frontend


class FirebaseLoginResponse(BaseModel):
    success: bool
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    session_token: str
    is_new_user: bool = False


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify Firebase ID token using Firebase Admin SDK.
    Raises HTTPException if token is invalid.
    """
    try:
        decoded_token = firebase_auth_sdk.verify_id_token(id_token)
        logger.info(f"✅ Token verified for: {decoded_token.get('email')}")
        return decoded_token
    except Exception as e:
        logger.error(f"❌ Token verification failed: {type(e).__name__}: {e}")
        raise HTTPException(status_code=401, detail=f"Token verification failed: {type(e).__name__}")


@router.post("/login", response_model=FirebaseLoginResponse)
async def firebase_login(request: FirebaseLoginRequest):
    """
    Login or register user via Firebase Google Auth
    """
    try:
        # Verify the Firebase ID token (REQUIRED - prevents impersonation)
        token_data = verify_firebase_token(request.id_token)

        # Use verified email from token, not from user_info (prevents spoofing)
        verified_email = token_data.get("email")
        if not verified_email:
            raise HTTPException(status_code=400, detail="Email not found in token")

        # Use user_info for display data, but email comes from verified token
        user_info = request.user_info
        user_info["email"] = verified_email

        db = await get_database()

        # Check if user exists
        existing_user = await db.users.find_one(
            {"email": verified_email},
            {"_id": 0}
        )

        is_new_user = False

        if existing_user:
            # Update user info and increment login count
            user_id = existing_user["user_id"]
            await db.users.update_one(
                {"email": verified_email},
                {
                    "$set": {
                        "name": user_info.get("name", existing_user.get("name")),
                        "picture": user_info.get("picture", existing_user.get("picture")),
                        "firebase_uid": token_data.get("uid"),
                        "last_login": datetime.now(timezone.utc).isoformat(),
                        "auth_provider": "firebase_google"
                    },
                    "$inc": {
                        "total_logins": 1
                    }
                }
            )

            # Log login for analytics
            await db.login_logs.insert_one({
                "user_id": user_id,
                "email": verified_email,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ip": "unknown",
                "user_agent": "unknown"
            })
        else:
            # Create new user
            is_new_user = True
            user_id = str(uuid.uuid4())

            # Admin emails from env or default
            admin_emails_str = os.environ.get("ADMIN_EMAILS", "tanasecristian2007@gmail.com,contact@finromania.ro")
            admin_emails = [e.strip() for e in admin_emails_str.split(",")]

            new_user = {
                "user_id": user_id,
                "email": verified_email,
                "name": user_info.get("name", verified_email.split("@")[0]),
                "picture": user_info.get("picture"),
                "firebase_uid": token_data.get("uid"),
                "auth_provider": "firebase_google",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat(),
                "is_admin": verified_email.lower() in [e.lower() for e in admin_emails],
                "ai_credits_used": 0,
                "total_logins": 1
            }

            # Auto-activate PRO gratuit pentru toți userii până pe 5 iunie 2026
            free_pro_deadline = datetime(2026, 6, 5, tzinfo=timezone.utc)
            if datetime.now(timezone.utc) < free_pro_deadline:
                new_user.update({
                    "is_early_adopter": True,
                    "subscription_level": "pro",
                    "subscription_expires_at": free_pro_deadline.isoformat(),
                    "subscription_source": "free_pro_june2026",
                    "unlocked_levels": ["beginner", "intermediate", "advanced"],
                    "experience_level": "advanced",
                    "daily_summary_enabled": True
                })
                logger.info(f"🎉 New FREE PRO user (until June 5): {verified_email}")

            await db.users.insert_one(new_user)
            logger.info(f"New user created via Firebase: {verified_email} (admin: {new_user['is_admin']})")

            # Trimite email de bun venit (non-blocking, în background)
            try:
                from services.notification_service import notification_service
                asyncio.create_task(notification_service.send_welcome_email(
                    user_email=verified_email,
                    user_name=user_info.get("name", "")
                ))
            except Exception as e:
                logger.warning(f"Welcome email task failed: {e}")

        # Create session token
        session_token = str(uuid.uuid4())

        # Session expires in 7 days
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        # Store session in user_sessions collection (same as auth.py uses)
        await db.user_sessions.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "session_token": session_token,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "expires_at": expires_at.isoformat(),
                    "auth_provider": "firebase_google"
                }
            },
            upsert=True
        )

        # Get full user data
        user_data = await db.users.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )

        return FirebaseLoginResponse(
            success=True,
            user_id=user_id,
            email=user_data["email"],
            name=user_data.get("name", ""),
            picture=user_data.get("picture"),
            session_token=session_token,
            is_new_user=is_new_user
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Firebase login error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@router.post("/logout")
async def firebase_logout(request: Request):
    """
    Logout user - invalidate session
    """
    try:
        # Get session token from header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]

            db = await get_database()
            await db.user_sessions.delete_one({"session_token": session_token})

        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"success": True, "message": "Logged out"}
