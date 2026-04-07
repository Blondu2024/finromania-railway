"""
Community Forum pentru FinRomania
PRO users: citesc + scriu
FREE users: doar citesc (paywall pe scriere)
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from config.database import get_database
from routes.auth import require_auth, get_current_user_optional

router = APIRouter(prefix="/community", tags=["community"])

# ============================================
# TOPICURI PREDEFINITE
# ============================================
TOPICS = [
    {
        "id": "dividende",
        "name": "Dividende BVB",
        "description": "Discuții despre dividende, randamente, calendar ex-dividend",
        "icon": "💰",
        "color": "green"
    },
    {
        "id": "analiza-actiuni",
        "name": "Analiză Acțiuni",
        "description": "Analize tehnice și fundamentale, opinii despre companii BVB",
        "icon": "📊",
        "color": "blue"
    },
    {
        "id": "incepatori",
        "name": "Întrebări Începători",
        "description": "Întrebări de bază, sfaturi pentru cei care încep să investească",
        "icon": "🎓",
        "color": "purple"
    },
    {
        "id": "fiscal",
        "name": "Taxe & Fiscal",
        "description": "Impozite pe investiții, Declarația Unică, CASS, optimizare fiscală",
        "icon": "🧾",
        "color": "orange"
    },
    {
        "id": "piete-internationale",
        "name": "Piețe Internaționale",
        "description": "S&P 500, ETF-uri, acțiuni US/EU, crypto",
        "icon": "🌍",
        "color": "cyan"
    },
    {
        "id": "strategii",
        "name": "Strategii & Portofoliu",
        "description": "DCA, value investing, dividend growth, alocarea portofoliului",
        "icon": "🎯",
        "color": "red"
    }
]

TOPIC_IDS = {t["id"] for t in TOPICS}


# ============================================
# MODELS
# ============================================
class CreatePostRequest(BaseModel):
    content: str
    title: Optional[str] = None


class CreateReplyRequest(BaseModel):
    content: str


# ============================================
# HELPERS
# ============================================
def _require_pro(user: dict):
    """Verifică dacă userul are PRO activ"""
    if user.get("subscription_level") != "pro":
        raise HTTPException(
            status_code=403,
            detail="Doar utilizatorii PRO pot scrie în comunitate. Upgrade la PRO pentru a participa!"
        )
    # Verifică expirare
    expires = user.get("subscription_expires_at")
    if expires:
        exp_dt = datetime.fromisoformat(expires.replace("Z", "+00:00")) if isinstance(expires, str) else expires
        if exp_dt < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=403,
                detail="Abonamentul PRO a expirat. Reînnoiește pentru a scrie în comunitate!"
            )


# ============================================
# ENDPOINTS
# ============================================

@router.get("/topics")
async def get_topics(request=None):
    """Lista topicurilor cu numărul de posturi"""
    db = await get_database()

    topics_with_counts = []
    for topic in TOPICS:
        post_count = await db.community_posts.count_documents({
            "topic_id": topic["id"],
            "parent_id": None  # Doar posturi principale, nu reply-uri
        })
        last_post = await db.community_posts.find_one(
            {"topic_id": topic["id"]},
            {"_id": 0, "created_at": 1, "author_name": 1},
            sort=[("created_at", -1)]
        )

        topics_with_counts.append({
            **topic,
            "post_count": post_count,
            "last_activity": last_post.get("created_at") if last_post else None,
            "last_author": last_post.get("author_name") if last_post else None
        })

    return {"topics": topics_with_counts}


@router.get("/topics/{topic_id}/posts")
async def get_topic_posts(
    topic_id: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50)
):
    """Listează posturile dintr-un topic (disponibil pentru toți)"""
    if topic_id not in TOPIC_IDS:
        raise HTTPException(status_code=404, detail="Topic negăsit")

    db = await get_database()

    # Posturi principale (nu reply-uri)
    posts = await db.community_posts.find(
        {"topic_id": topic_id, "parent_id": None},
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    # Pentru fiecare post, adaugă nr de reply-uri
    for post in posts:
        reply_count = await db.community_posts.count_documents({
            "parent_id": post["post_id"]
        })
        post["reply_count"] = reply_count

    total = await db.community_posts.count_documents({
        "topic_id": topic_id, "parent_id": None
    })

    topic_info = next((t for t in TOPICS if t["id"] == topic_id), None)

    return {
        "topic": topic_info,
        "posts": posts,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/posts/{post_id}")
async def get_post_with_replies(post_id: str):
    """Un post cu toate reply-urile (disponibil pentru toți)"""
    db = await get_database()

    post = await db.community_posts.find_one(
        {"post_id": post_id},
        {"_id": 0}
    )
    if not post:
        raise HTTPException(status_code=404, detail="Postare negăsită")

    # Reply-uri
    replies = await db.community_posts.find(
        {"parent_id": post_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(100)

    return {
        "post": post,
        "replies": replies
    }


@router.post("/topics/{topic_id}/posts")
async def create_post(
    topic_id: str,
    data: CreatePostRequest,
    user: dict = Depends(require_auth)
):
    """Creează un post nou (doar PRO)"""
    if topic_id not in TOPIC_IDS:
        raise HTTPException(status_code=404, detail="Topic negăsit")

    _require_pro(user)

    content = data.content.strip()
    if len(content) < 5:
        raise HTTPException(status_code=400, detail="Mesajul e prea scurt (minim 5 caractere)")
    if len(content) > 2000:
        raise HTTPException(status_code=400, detail="Mesajul e prea lung (maxim 2000 caractere)")

    db = await get_database()

    post = {
        "post_id": f"post_{uuid.uuid4().hex[:12]}",
        "topic_id": topic_id,
        "parent_id": None,
        "author_id": user["user_id"],
        "author_name": user.get("name", "Anonim"),
        "author_picture": user.get("picture"),
        "title": data.title.strip()[:100] if data.title else None,
        "content": content,
        "likes": [],
        "like_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.community_posts.insert_one(post)
    post.pop("_id", None)

    return {"post": post}


@router.post("/posts/{post_id}/reply")
async def reply_to_post(
    post_id: str,
    data: CreateReplyRequest,
    user: dict = Depends(require_auth)
):
    """Răspunde la un post (doar PRO)"""
    _require_pro(user)

    content = data.content.strip()
    if len(content) < 2:
        raise HTTPException(status_code=400, detail="Răspunsul e prea scurt")
    if len(content) > 1000:
        raise HTTPException(status_code=400, detail="Răspunsul e prea lung (maxim 1000 caractere)")

    db = await get_database()

    # Verifică că postul părinte există
    parent = await db.community_posts.find_one({"post_id": post_id}, {"_id": 0, "topic_id": 1})
    if not parent:
        raise HTTPException(status_code=404, detail="Postarea nu există")

    reply = {
        "post_id": f"reply_{uuid.uuid4().hex[:12]}",
        "topic_id": parent["topic_id"],
        "parent_id": post_id,
        "author_id": user["user_id"],
        "author_name": user.get("name", "Anonim"),
        "author_picture": user.get("picture"),
        "title": None,
        "content": content,
        "likes": [],
        "like_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.community_posts.insert_one(reply)
    reply.pop("_id", None)

    return {"reply": reply}


@router.post("/posts/{post_id}/like")
async def toggle_like(
    post_id: str,
    user: dict = Depends(require_auth)
):
    """Like/unlike un post (doar PRO)"""
    _require_pro(user)

    db = await get_database()

    post = await db.community_posts.find_one({"post_id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Postarea nu există")

    likes = post.get("likes", [])
    user_id = user["user_id"]

    if user_id in likes:
        # Unlike
        likes.remove(user_id)
        action = "unliked"
    else:
        # Like
        likes.append(user_id)
        action = "liked"

    await db.community_posts.update_one(
        {"post_id": post_id},
        {"$set": {"likes": likes, "like_count": len(likes)}}
    )

    return {"action": action, "like_count": len(likes)}


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    user: dict = Depends(require_auth)
):
    """Șterge un post (autor propriu sau admin)"""
    db = await get_database()

    post = await db.community_posts.find_one({"post_id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Postarea nu există")

    # Verifică permisiuni
    is_author = post.get("author_id") == user["user_id"]
    is_admin = user.get("is_admin", False)

    if not is_author and not is_admin:
        raise HTTPException(status_code=403, detail="Nu poți șterge postarea altcuiva")

    # Șterge postul + reply-urile
    await db.community_posts.delete_many({
        "$or": [
            {"post_id": post_id},
            {"parent_id": post_id}
        ]
    })

    return {"deleted": True}
