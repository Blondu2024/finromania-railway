"""Auth routes pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import httpx
import uuid
import logging
import os
from config.database import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Emergent Auth API URL (configurable via environment)
EMERGENT_AUTH_URL = os.getenv("EMERGENT_AUTH_URL", "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data")

# Models
class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: Optional[str] = None
    is_admin: bool = False
    subscription_level: Optional[str] = None
    is_early_adopter: bool = False
    subscription_expires_at: Optional[str] = None

class SessionRequest(BaseModel):
    session_id: str

# Helper to get current user
async def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session token"""
    # Try cookie first
    session_token = request.cookies.get("session_token")
    
    # Fallback to Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        return None
    
    db = await get_database()
    session = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session:
        return None
    
    # Check expiry
    expires_at = session.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    
    # Get user
    user = await db.users.find_one(
        {"user_id": session["user_id"]},
        {"_id": 0}
    )
    
    return user

# Dependency for protected routes
async def require_auth(request: Request) -> dict:
    """Require authentication"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

# Dependency for optional auth (user can be None)
async def get_current_user_optional(request: Request) -> Optional[dict]:
    """Get current user if logged in, None otherwise (no error)"""
    return await get_current_user(request)

@router.post("/session")
async def create_session(data: SessionRequest, response: Response):
    """Exchange session_id for session_token"""
    try:
        # Call Emergent auth API
        async with httpx.AsyncClient() as client:
            auth_response = await client.get(
                EMERGENT_AUTH_URL,
                headers={"X-Session-ID": data.session_id},
                timeout=10.0
            )
        
        if auth_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        user_data = auth_response.json()
        session_token = user_data.get("session_token")
        
        if not session_token:
            raise HTTPException(status_code=401, detail="No session token received")
        
        db = await get_database()
        
        # Check if user exists
        existing_user = await db.users.find_one(
            {"email": user_data["email"]},
            {"_id": 0}
        )
        
        if existing_user:
            user_id = existing_user["user_id"]
            # Update user data
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "name": user_data["name"],
                    "picture": user_data.get("picture"),
                    "last_login": datetime.now(timezone.utc).isoformat()
                }}
            )
        else:
            # Create new user
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            
            # Check Early Adopter availability
            # PRO GRATUIT pentru TOȚI userii până pe 5 iunie 2026
            free_pro_deadline = datetime(2026, 6, 5, tzinfo=timezone.utc)
            is_free_pro_period = datetime.now(timezone.utc) < free_pro_deadline
            
            new_user_data = {
                "user_id": user_id,
                "email": user_data["email"],
                "name": user_data["name"],
                "picture": user_data.get("picture"),
                "is_admin": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat()
            }
            
            # Auto-activate PRO gratuit pentru toți userii până pe 5 iunie 2026
            if is_free_pro_period:
                new_user_data.update({
                    "is_early_adopter": True,
                    "subscription_level": "pro",
                    "subscription_expires_at": free_pro_deadline.isoformat(),
                    "subscription_source": "free_pro_june2026",
                    "unlocked_levels": ["beginner", "intermediate", "advanced"]
                })
                logger.info(f"🎉 New FREE PRO user (until June 5): {user_data['email']}")
            
            await db.users.insert_one(new_user_data)
        
        # Store session
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        await db.user_sessions.insert_one({
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Set cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
            max_age=7*24*60*60
        )
        
        # Get full user data
        user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        
        # Log visit for analytics
        await db.analytics.insert_one({
            "event": "login",
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Return user with session token for localStorage persistence
        return {
            **user,
            "session_token": session_token
        }
        
    except httpx.RequestError as e:
        logger.error(f"Auth request error: {e}")
        raise HTTPException(status_code=500, detail="Authentication service error")

@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(require_auth)):
    """Get current user"""
    return user


# Demo login for automated testing (Playwright, etc.)
DEMO_SECRET = os.environ.get("DEMO_LOGIN_SECRET", "finromania-demo-2026")

@router.get("/demo-login")
async def demo_login(secret: str, response: Response):
    """
    Demo login endpoint for automated testing tools like Playwright.
    Creates a valid session for a PRO user without going through Google OAuth.
    
    Usage: GET /api/auth/demo-login?secret=YOUR_SECRET
    
    Returns a session cookie that can be used for subsequent requests.
    """
    if secret != DEMO_SECRET:
        raise HTTPException(status_code=403, detail="Invalid demo secret")
    
    db = await get_database()
    
    # Find or create demo user
    demo_email = "demo@finromania.ro"
    demo_user = await db.users.find_one({"email": demo_email}, {"_id": 0})
    
    if not demo_user:
        # Create demo PRO user with ADVANCED experience level
        demo_user_id = f"demo_{uuid.uuid4().hex[:12]}"
        demo_user = {
            "user_id": demo_user_id,
            "email": demo_email,
            "name": "Demo User (PRO)",
            "picture": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_admin": False,
            "subscription_level": "pro",
            "subscription_expires_at": "2026-06-05T23:59:59Z",
            "is_early_adopter": False,
            "daily_summary_enabled": True,
            "experience_level": "advanced"  # IMPORTANT pentru AI Analysis complet!
        }
        await db.users.insert_one(demo_user)
        logger.info(f"Created demo PRO user: {demo_email}")
    else:
        demo_user_id = demo_user["user_id"]
        # Update experience level if missing
        if not demo_user.get("experience_level"):
            await db.users.update_one(
                {"email": demo_email},
                {"$set": {"experience_level": "advanced"}}
            )
            logger.info(f"Updated demo user experience level to advanced")
    
    # Create session
    session_token = f"demo_{uuid.uuid4().hex}"
    session_data = {
        "session_token": session_token,
        "user_id": demo_user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    }
    
    await db.user_sessions.insert_one(session_data)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=86400,  # 24 hours
        path="/"
    )
    
    logger.info(f"Demo login successful for automated testing")
    
    return {
        "message": "Demo login successful",
        "user": {
            "email": demo_email,
            "name": demo_user.get("name", "Demo User"),
            "subscription_level": "pro"
        },
        "session_token": session_token,
        "expires_in": "24 hours"
    }

@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    session_token = request.cookies.get("session_token")
    
    if session_token:
        db = await get_database()
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(
        key="session_token",
        path="/",
        secure=True,
        samesite="none"
    )
    
    return {"message": "Logged out successfully"}
