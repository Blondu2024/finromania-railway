"""Notification Service - Sistem de notificări pentru Early Adopter și alte alerte"""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging
from config.database import get_database
import uuid

logger = logging.getLogger(__name__)


class NotificationService:
    """Service pentru gestionarea notificărilor utilizatorilor"""
    
    # Tipuri de notificări
    NOTIFICATION_TYPES = {
        "early_adopter_expiring_7days": {
            "title": "⏰ PRO gratuit expiră în 7 zile!",
            "message": "Abonamentul tău Early Adopter PRO expiră în 7 zile. Continuă cu PRO la doar 49 RON/lună pentru a nu pierde accesul la funcțiile premium!",
            "action_url": "/pricing",
            "action_text": "Vezi Planuri PRO",
            "priority": "high",
            "icon": "clock"
        },
        "early_adopter_expiring_3days": {
            "title": "🔴 PRO gratuit expiră în 3 zile!",
            "message": "Mai ai doar 3 zile de PRO gratuit! Nu pierde accesul la AI nelimitat, Calculator Fiscal și toate funcțiile premium.",
            "action_url": "/pricing",
            "action_text": "Upgrade la PRO",
            "priority": "critical",
            "icon": "alert"
        },
        "early_adopter_expiring_1day": {
            "title": "❗ ULTIMA ZI de PRO gratuit!",
            "message": "Mâine pierzi accesul PRO. Fă upgrade acum și păstrează toate beneficiile!",
            "action_url": "/pricing",
            "action_text": "Upgrade ACUM",
            "priority": "critical",
            "icon": "alert-triangle"
        },
        "early_adopter_expired": {
            "title": "PRO gratuit a expirat",
            "message": "Perioada ta de Early Adopter PRO s-a încheiat. Îți mulțumim că ai fost unul dintre primii utilizatori! Poți continua cu PRO la doar 49 RON/lună.",
            "action_url": "/pricing",
            "action_text": "Reactivează PRO",
            "priority": "medium",
            "icon": "crown"
        },
        "early_adopter_welcome": {
            "title": "🎉 Bun venit în Early Adopter PRO!",
            "message": "Felicitări! Ai acces PRO gratuit pentru 90 de zile. Explorează toate funcțiile premium!",
            "action_url": "/dashboard",
            "action_text": "Explorează",
            "priority": "low",
            "icon": "gift"
        }
    }
    
    async def create_notification(
        self, 
        user_id: str, 
        notification_type: str,
        custom_data: dict = None
    ) -> dict:
        """Creează o notificare nouă pentru un utilizator"""
        db = await get_database()
        
        if notification_type not in self.NOTIFICATION_TYPES:
            logger.warning(f"Unknown notification type: {notification_type}")
            return None
        
        template = self.NOTIFICATION_TYPES[notification_type]
        
        # Check dacă există deja o notificare similară necitită
        existing = await db.notifications.find_one({
            "user_id": user_id,
            "type": notification_type,
            "read": False
        })
        
        if existing:
            logger.info(f"Notification {notification_type} already exists for user {user_id}")
            return existing
        
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": notification_type,
            "title": template["title"],
            "message": template["message"],
            "action_url": template["action_url"],
            "action_text": template["action_text"],
            "priority": template["priority"],
            "icon": template["icon"],
            "read": False,
            "email_sent": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "custom_data": custom_data or {}
        }
        
        await db.notifications.insert_one(notification)
        logger.info(f"Created notification {notification_type} for user {user_id}")
        
        return notification
    
    async def get_user_notifications(
        self, 
        user_id: str, 
        unread_only: bool = False,
        limit: int = 20
    ) -> List[dict]:
        """Obține notificările unui utilizator"""
        db = await get_database()
        
        query = {"user_id": user_id}
        if unread_only:
            query["read"] = False
        
        notifications = await db.notifications.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return notifications
    
    async def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """Marchează o notificare ca citită"""
        db = await get_database()
        
        result = await db.notifications.update_one(
            {"id": notification_id, "user_id": user_id},
            {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return result.modified_count > 0
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Marchează toate notificările ca citite"""
        db = await get_database()
        
        result = await db.notifications.update_many(
            {"user_id": user_id, "read": False},
            {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return result.modified_count
    
    async def get_unread_count(self, user_id: str) -> int:
        """Numără notificările necitite"""
        db = await get_database()
        return await db.notifications.count_documents({"user_id": user_id, "read": False})
    
    async def check_expiring_subscriptions(self) -> dict:
        """Verifică și creează notificări pentru abonamentele care expiră"""
        db = await get_database()
        now = datetime.now(timezone.utc)
        
        results = {
            "7_days": 0,
            "3_days": 0,
            "1_day": 0,
            "expired": 0
        }
        
        # Utilizatori Early Adopter care expiră în 7 zile
        expiry_7days = now + timedelta(days=7)
        expiry_7days_start = now + timedelta(days=6)
        
        users_7days = await db.users.find({
            "is_early_adopter": True,
            "subscription_expires_at": {
                "$gte": expiry_7days_start.isoformat(),
                "$lt": expiry_7days.isoformat()
            }
        }).to_list(1000)
        
        for user in users_7days:
            await self.create_notification(
                user["user_id"], 
                "early_adopter_expiring_7days",
                {"expires_at": user.get("subscription_expires_at")}
            )
            results["7_days"] += 1
        
        # Utilizatori care expiră în 3 zile
        expiry_3days = now + timedelta(days=3)
        expiry_3days_start = now + timedelta(days=2)
        
        users_3days = await db.users.find({
            "is_early_adopter": True,
            "subscription_expires_at": {
                "$gte": expiry_3days_start.isoformat(),
                "$lt": expiry_3days.isoformat()
            }
        }).to_list(1000)
        
        for user in users_3days:
            await self.create_notification(
                user["user_id"], 
                "early_adopter_expiring_3days",
                {"expires_at": user.get("subscription_expires_at")}
            )
            results["3_days"] += 1
        
        # Utilizatori care expiră în 1 zi
        expiry_1day = now + timedelta(days=1)
        expiry_1day_start = now
        
        users_1day = await db.users.find({
            "is_early_adopter": True,
            "subscription_expires_at": {
                "$gte": expiry_1day_start.isoformat(),
                "$lt": expiry_1day.isoformat()
            }
        }).to_list(1000)
        
        for user in users_1day:
            await self.create_notification(
                user["user_id"], 
                "early_adopter_expiring_1day",
                {"expires_at": user.get("subscription_expires_at")}
            )
            results["1_day"] += 1
        
        # Utilizatori care au expirat (downgrade la free)
        expired_users = await db.users.find({
            "is_early_adopter": True,
            "subscription_level": "pro",
            "subscription_expires_at": {"$lt": now.isoformat()}
        }).to_list(1000)
        
        for user in expired_users:
            # Downgrade la free
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": {
                    "subscription_level": "free",
                    "early_adopter_expired": True,
                    "early_adopter_expired_at": now.isoformat()
                }}
            )
            
            await self.create_notification(
                user["user_id"], 
                "early_adopter_expired",
                {"expired_at": now.isoformat()}
            )
            results["expired"] += 1
            logger.info(f"Early Adopter expired for user {user['user_id']}")
        
        return results


notification_service = NotificationService()
