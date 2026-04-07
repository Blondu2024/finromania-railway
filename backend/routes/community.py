"""
Community Chat LIVE pentru FinRomania — stil Discord/Telegram
WebSocket real-time: mesajele apar instant la toti userii din canal
PRO: citesc + scriu
FREE: doar citesc (paywall pe scriere)
"""
from fastapi import APIRouter, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict, Set
from datetime import datetime, timezone
import uuid
import json
import logging
from config.database import get_database
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/community", tags=["community"])

# ============================================
# CANALE CHAT PREDEFINITE
# ============================================
CHANNELS = [
    {
        "id": "dividende",
        "name": "Dividende BVB",
        "description": "Randamente, calendar ex-dividend, strategii dividende",
        "icon": "wallet",
        "color": "green"
    },
    {
        "id": "analiza-actiuni",
        "name": "Analiza Actiuni",
        "description": "Analize tehnice si fundamentale, opinii companii BVB",
        "icon": "chart",
        "color": "blue"
    },
    {
        "id": "incepatori",
        "name": "Intrebari Incepatori",
        "description": "Intrebari de baza, sfaturi pentru cei care incep",
        "icon": "graduation",
        "color": "purple"
    },
    {
        "id": "fiscal",
        "name": "Taxe & Fiscal",
        "description": "Impozite, Declaratia Unica, CASS, optimizare fiscala",
        "icon": "receipt",
        "color": "orange"
    },
    {
        "id": "piete-internationale",
        "name": "Piete Internationale",
        "description": "S&P 500, ETF-uri, actiuni US/EU, crypto",
        "icon": "globe",
        "color": "cyan"
    },
    {
        "id": "general",
        "name": "General",
        "description": "Discutii libere despre investitii si piete",
        "icon": "message",
        "color": "slate"
    }
]

CHANNEL_IDS = {c["id"] for c in CHANNELS}


# ============================================
# WEBSOCKET CONNECTION MANAGER
# ============================================
class ConnectionManager:
    """Gestioneaza conexiunile WebSocket per canal"""

    def __init__(self):
        # channel_id -> set of WebSocket connections
        self.channels: Dict[str, Set[WebSocket]] = {}
        # websocket -> user info
        self.users: Dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket, channel_id: str, user_info: dict):
        await websocket.accept()
        if channel_id not in self.channels:
            self.channels[channel_id] = set()
        self.channels[channel_id].add(websocket)
        self.users[websocket] = {**user_info, "channel_id": channel_id}

        # Broadcast cine e online
        await self.broadcast_online_count(channel_id)

    def disconnect(self, websocket: WebSocket):
        user = self.users.pop(websocket, None)
        if user:
            channel_id = user.get("channel_id")
            if channel_id and channel_id in self.channels:
                self.channels[channel_id].discard(websocket)

    async def broadcast_to_channel(self, channel_id: str, message: dict):
        """Trimite mesaj la TOTI userii din canal — instant"""
        if channel_id not in self.channels:
            return
        dead = set()
        for ws in self.channels[channel_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        # Curata conexiuni moarte
        for ws in dead:
            self.disconnect(ws)

    async def broadcast_online_count(self, channel_id: str):
        count = len(self.channels.get(channel_id, set()))
        await self.broadcast_to_channel(channel_id, {
            "type": "online_count",
            "count": count
        })

    def get_online_count(self, channel_id: str) -> int:
        return len(self.channels.get(channel_id, set()))


manager = ConnectionManager()


# ============================================
# MODELS
# ============================================
class SendMessageRequest(BaseModel):
    content: str


# ============================================
# REST ENDPOINTS
# ============================================

@router.get("/channels")
async def get_channels():
    """Lista canalelor cu numar mesaje si online count"""
    db = await get_database()

    channels_data = []
    for ch in CHANNELS:
        msg_count = await db.chat_messages.count_documents({"channel_id": ch["id"]})
        last_msg = await db.chat_messages.find_one(
            {"channel_id": ch["id"]},
            {"_id": 0, "created_at": 1, "author_name": 1, "content": 1},
            sort=[("created_at", -1)]
        )

        channels_data.append({
            **ch,
            "message_count": msg_count,
            "online_count": manager.get_online_count(ch["id"]),
            "last_message": {
                "author": last_msg.get("author_name"),
                "content": last_msg.get("content", "")[:50],
                "time": last_msg.get("created_at")
            } if last_msg else None
        })

    return {"channels": channels_data}


@router.get("/channels/{channel_id}/messages")
async def get_channel_messages(
    channel_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    before: Optional[str] = None
):
    """Incarca istoricul mesajelor (scroll up = mesaje mai vechi)"""
    if channel_id not in CHANNEL_IDS:
        raise HTTPException(status_code=404, detail="Canal negasit")

    db = await get_database()

    query = {"channel_id": channel_id}
    if before:
        query["created_at"] = {"$lt": before}

    messages = await db.chat_messages.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)

    # Inverseaza — cele mai vechi primele (cronologic)
    messages.reverse()

    channel_info = next((c for c in CHANNELS if c["id"] == channel_id), None)

    return {
        "channel": channel_info,
        "messages": messages,
        "online_count": manager.get_online_count(channel_id),
        "has_more": len(messages) == limit
    }


@router.post("/channels/{channel_id}/messages")
async def send_message_rest(
    channel_id: str,
    data: SendMessageRequest,
    user: dict = Depends(require_auth)
):
    """Trimite mesaj via REST (fallback daca WebSocket nu merge)"""
    if channel_id not in CHANNEL_IDS:
        raise HTTPException(status_code=404, detail="Canal negasit")

    if user.get("subscription_level") != "pro":
        raise HTTPException(status_code=403, detail="Doar PRO pot scrie")

    content = data.content.strip()
    if not content or len(content) > 1000:
        raise HTTPException(status_code=400, detail="Mesaj invalid (1-1000 caractere)")

    db = await get_database()

    msg = {
        "message_id": f"msg_{uuid.uuid4().hex[:12]}",
        "channel_id": channel_id,
        "author_id": user["user_id"],
        "author_name": user.get("name", "Anonim"),
        "author_picture": user.get("picture"),
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.chat_messages.insert_one(msg)
    msg.pop("_id", None)

    # Broadcast la toti din canal
    await manager.broadcast_to_channel(channel_id, {
        "type": "new_message",
        "message": msg
    })

    return {"message": msg}


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    user: dict = Depends(require_auth)
):
    """Sterge mesaj (autor sau admin)"""
    db = await get_database()

    msg = await db.chat_messages.find_one({"message_id": message_id})
    if not msg:
        raise HTTPException(status_code=404, detail="Mesaj negasit")

    if msg.get("author_id") != user["user_id"] and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Nu poti sterge mesajul altcuiva")

    channel_id = msg.get("channel_id")
    await db.chat_messages.delete_one({"message_id": message_id})

    # Broadcast stergere
    await manager.broadcast_to_channel(channel_id, {
        "type": "message_deleted",
        "message_id": message_id
    })

    return {"deleted": True}


# ============================================
# WEBSOCKET — CHAT LIVE
# ============================================

@router.websocket("/ws/{channel_id}")
async def websocket_chat(websocket: WebSocket, channel_id: str):
    """
    WebSocket endpoint pentru chat live.
    Client trimite: {"type": "auth", "token": "..."} la connect
    Apoi: {"type": "message", "content": "text"}
    Server trimite: {"type": "new_message", "message": {...}}
    """
    if channel_id not in CHANNEL_IDS:
        await websocket.close(code=4004, reason="Canal negasit")
        return

    db = await get_database()
    user = None

    try:
        await websocket.accept()

        # Asteapta auth message
        auth_data = await websocket.receive_json()

        if auth_data.get("type") != "auth" or not auth_data.get("token"):
            # User FREE — poate asculta dar nu scrie
            user = {"user_id": "anon", "name": "Vizitator", "subscription_level": "free"}
            await websocket.send_json({"type": "auth_ok", "can_write": False})
        else:
            # Verifica token
            token = auth_data["token"]
            session = await db.user_sessions.find_one(
                {"session_token": token}, {"_id": 0}
            )

            if session:
                user_data = await db.users.find_one(
                    {"user_id": session["user_id"]}, {"_id": 0}
                )
                if user_data:
                    user = user_data
                    is_pro = user.get("subscription_level") == "pro"
                    await websocket.send_json({
                        "type": "auth_ok",
                        "can_write": is_pro,
                        "user_name": user.get("name")
                    })
                else:
                    user = {"user_id": "anon", "name": "Vizitator", "subscription_level": "free"}
                    await websocket.send_json({"type": "auth_ok", "can_write": False})
            else:
                user = {"user_id": "anon", "name": "Vizitator", "subscription_level": "free"}
                await websocket.send_json({"type": "auth_ok", "can_write": False})

        # Inregistreaza in canal
        if channel_id not in manager.channels:
            manager.channels[channel_id] = set()
        manager.channels[channel_id].add(websocket)
        manager.users[websocket] = {**user, "channel_id": channel_id}

        # Broadcast online count
        await manager.broadcast_online_count(channel_id)

        # Asteapta mesaje
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "message":
                # Verifica PRO
                if user.get("subscription_level") != "pro":
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Doar utilizatorii PRO pot scrie. Upgrade la PRO!"
                    })
                    continue

                content = data.get("content", "").strip()
                if not content or len(content) > 1000:
                    await websocket.send_json({
                        "type": "error",
                        "detail": "Mesaj invalid (1-1000 caractere)"
                    })
                    continue

                # Salveaza in DB
                msg = {
                    "message_id": f"msg_{uuid.uuid4().hex[:12]}",
                    "channel_id": channel_id,
                    "author_id": user["user_id"],
                    "author_name": user.get("name", "Anonim"),
                    "author_picture": user.get("picture"),
                    "content": content,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }

                await db.chat_messages.insert_one(msg)
                msg.pop("_id", None)

                # Broadcast la TOTI din canal — INSTANT
                await manager.broadcast_to_channel(channel_id, {
                    "type": "new_message",
                    "message": msg
                })

            elif data.get("type") == "typing":
                # Broadcast typing indicator
                await manager.broadcast_to_channel(channel_id, {
                    "type": "typing",
                    "user_name": user.get("name", "Cineva")
                })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)
        if channel_id in manager.channels:
            await manager.broadcast_online_count(channel_id)
