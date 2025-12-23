"""Analytics tracking pentru FinRomania"""
from fastapi import APIRouter, Request
from datetime import datetime, timezone
from config.database import get_database

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/track")
async def track_event(request: Request, event: str, page: str = None):
    """Track analytics event"""
    db = await get_database()
    
    # Get IP (for unique visitors - anonymized)
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hash(client_ip) % 1000000  # Anonymize
    
    await db.analytics.insert_one({
        "event": event,
        "page": page,
        "ip_hash": ip_hash,
        "user_agent": request.headers.get("user-agent", "")[:200],
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"status": "tracked"}
