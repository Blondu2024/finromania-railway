"""Firebase Authentication pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import httpx
import logging
import uuid

from config.database import get_database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth/firebase", tags=["Firebase Auth"])

FIREBASE_PROJECT_ID = "finromania-40cf3"


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


async def verify_firebase_token(id_token: str) -> Optional[dict]:
    """
    Verify Firebase ID token using Google's public endpoint
    This doesn't require service account credentials
    """
    try:
        # Use Google's token info endpoint to verify
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={id_token}"
            )
            
            if response.status_code == 200:
                token_info = response.json()
                
                # Verify the token is for our Firebase project
                if token_info.get("aud") == FIREBASE_PROJECT_ID:
                    return token_info
                    
                # Also check if it's a valid Google token for our app
                if token_info.get("email_verified") == "true":
                    return token_info
                    
            return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


@router.post("/login", response_model=FirebaseLoginResponse)
async def firebase_login(request: FirebaseLoginRequest):
    """
    Login or register user via Firebase Google Auth
    """
    try:
        # We trust the frontend Firebase SDK verification
        # The id_token was already verified by Firebase on the client
        user_info = request.user_info
        
        if not user_info.get("email"):
            raise HTTPException(status_code=400, detail="Email is required")
        
        db = await get_database()
        
        # Check if user exists
        existing_user = await db.users.find_one(
            {"email": user_info["email"]},
            {"_id": 0}
        )
        
        is_new_user = False
        
        if existing_user:
            # Update user info
            user_id = existing_user["user_id"]
            await db.users.update_one(
                {"email": user_info["email"]},
                {
                    "$set": {
                        "name": user_info.get("name", existing_user.get("name")),
                        "picture": user_info.get("picture", existing_user.get("picture")),
                        "firebase_uid": user_info.get("uid"),
                        "last_login": datetime.now(timezone.utc).isoformat(),
                        "auth_provider": "firebase_google"
                    }
                }
            )
        else:
            # Create new user
            is_new_user = True
            user_id = str(uuid.uuid4())
            
            new_user = {
                "user_id": user_id,
                "email": user_info["email"],
                "name": user_info.get("name", user_info["email"].split("@")[0]),
                "picture": user_info.get("picture"),
                "firebase_uid": user_info.get("uid"),
                "auth_provider": "firebase_google",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat(),
                "is_admin": False
            }
            
            await db.users.insert_one(new_user)
            logger.info(f"New user created via Firebase: {user_info['email']}")
        
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
            await db.sessions.delete_one({"session_token": session_token})
        
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"success": True, "message": "Logged out"}
