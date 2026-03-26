"""Notification Service - Sistem de notificări pentru Early Adopter și alte alerte"""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging
import os
import resend
from config.database import get_database
import uuid

logger = logging.getLogger(__name__)

# Configure Resend for notifications
resend.api_key = os.environ.get("RESEND_API_KEY")


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
        },
        # PRICE ALERTS - NOU
        "price_alert_above": {
            "title": "🔔 Alertă preț - {symbol}",
            "message": "{symbol} a ajuns la {price} RON (peste {target} RON)",
            "action_url": "/stocks/bvb/{symbol}",
            "action_text": "Vezi detalii",
            "priority": "high",
            "icon": "trending-up"
        },
        "price_alert_below": {
            "title": "🔔 Alertă preț - {symbol}",
            "message": "{symbol} a scăzut la {price} RON (sub {target} RON)",
            "action_url": "/stocks/bvb/{symbol}",
            "action_text": "Vezi detalii",
            "priority": "high",
            "icon": "trending-down"
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

    async def check_price_alerts(self) -> dict:
        """Verifică toate alertele de preț și trimite notificări"""
        db = await get_database()
        
        results = {
            "alerts_checked": 0,
            "notifications_sent": 0,
            "errors": 0
        }
        
        try:
            # Obține toate watchlist-urile cu alerte active
            watchlists = await db.watchlists.find({
                "items": {"$exists": True, "$ne": []}
            }).to_list(1000)
            
            for watchlist in watchlists:
                user_id = watchlist.get("user_id")
                if not user_id:
                    continue
                
                for item in watchlist.get("items", []):
                    symbol = item.get("symbol")
                    alert_above = item.get("alert_above")
                    alert_below = item.get("alert_below")
                    
                    # Skip dacă nu are alerte setate
                    if not alert_above and not alert_below:
                        continue
                    
                    results["alerts_checked"] += 1
                    
                    # Obține prețul curent
                    stock = await db.stocks_bvb.find_one(
                        {"symbol": symbol},
                        {"_id": 0, "price": 1, "name": 1}
                    )
                    
                    if not stock or not stock.get("price"):
                        continue
                    
                    price = stock["price"]
                    
                    # Verifică alerta "above"
                    if alert_above and price >= alert_above:
                        # Verifică dacă am trimis deja notificare pentru această alertă
                        alert_key = f"price_alert_above_{symbol}_{alert_above}"
                        existing = await db.notifications.find_one({
                            "user_id": user_id,
                            "custom_data.alert_key": alert_key,
                            "read": False
                        })
                        
                        if not existing:
                            await self.create_price_alert_notification(
                                user_id=user_id,
                                symbol=symbol,
                                alert_type="above",
                                target_price=alert_above,
                                current_price=price,
                                stock_name=stock.get("name", symbol)
                            )
                            results["notifications_sent"] += 1
                            logger.info(f"Price alert (above) sent: {symbol} at {price} >= {alert_above}")
                    
                    # Verifică alerta "below"
                    if alert_below and price <= alert_below:
                        alert_key = f"price_alert_below_{symbol}_{alert_below}"
                        existing = await db.notifications.find_one({
                            "user_id": user_id,
                            "custom_data.alert_key": alert_key,
                            "read": False
                        })
                        
                        if not existing:
                            await self.create_price_alert_notification(
                                user_id=user_id,
                                symbol=symbol,
                                alert_type="below",
                                target_price=alert_below,
                                current_price=price,
                                stock_name=stock.get("name", symbol)
                            )
                            results["notifications_sent"] += 1
                            logger.info(f"Price alert (below) sent: {symbol} at {price} <= {alert_below}")
            
            logger.info(f"Price alerts check complete: {results}")
            
        except Exception as e:
            logger.error(f"Error checking price alerts: {e}")
            results["errors"] += 1
        
        return results

    async def create_price_alert_notification(
        self,
        user_id: str,
        symbol: str,
        alert_type: str,  # "above" or "below"
        target_price: float,
        current_price: float,
        stock_name: str = None
    ) -> dict:
        """Creează notificare pentru alertă de preț și trimite email"""
        db = await get_database()
        
        notification_type = f"price_alert_{alert_type}"
        template = self.NOTIFICATION_TYPES.get(notification_type, {})
        
        # Formatare mesaj cu date reale
        title = template.get("title", "🔔 Alertă preț").format(symbol=symbol)
        message = template.get("message", "").format(
            symbol=symbol,
            price=f"{current_price:.2f}",
            target=f"{target_price:.2f}"
        )
        
        alert_key = f"price_alert_{alert_type}_{symbol}_{target_price}"
        
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "action_url": f"/stocks/bvb/{symbol}",
            "action_text": "Vezi acțiunea",
            "priority": "high",
            "icon": "trending-up" if alert_type == "above" else "trending-down",
            "read": False,
            "email_sent": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "custom_data": {
                "symbol": symbol,
                "stock_name": stock_name,
                "alert_type": alert_type,
                "target_price": target_price,
                "triggered_price": current_price,
                "alert_key": alert_key
            }
        }
        
        await db.notifications.insert_one(notification)
        logger.info(f"Created price alert notification for {user_id}: {symbol} {alert_type} {target_price}")
        
        # Trimite email pentru alertă de preț
        await self.send_price_alert_email(user_id, symbol, stock_name, alert_type, target_price, current_price)
        
        return notification
    
    async def send_price_alert_email(
        self,
        user_id: str,
        symbol: str,
        stock_name: str,
        alert_type: str,
        target_price: float,
        current_price: float
    ) -> bool:
        """Trimite email pentru alertă de preț"""
        db = await get_database()
        
        try:
            # Obține datele utilizatorului
            user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
            if not user or not user.get("email"):
                logger.warning(f"User {user_id} has no email for price alert")
                return False
            
            email = user.get("email")
            name = user.get("name", "Investitor")
            
            # Determină culoarea și iconița
            is_above = alert_type == "above"
            color = "#16a34a" if is_above else "#dc2626"
            icon = "📈" if is_above else "📉"
            direction = "a crescut la" if is_above else "a scăzut la"
            threshold = "peste" if is_above else "sub"
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff;">
        <!-- Header -->
        <div style="background: {color}; padding: 25px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">{icon} Alertă de Preț</h1>
        </div>
        
        <!-- Content -->
        <div style="padding: 25px;">
            <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">
                Salut{' ' + name if name else ''},
            </p>
            
            <div style="background: #f8fafc; border-left: 4px solid {color}; padding: 20px; margin: 20px 0;">
                <h2 style="margin: 0 0 10px 0; color: #1e3a5f; font-size: 20px;">
                    {symbol} {direction} {current_price:.2f} RON
                </h2>
                <p style="margin: 0; color: #64748b; font-size: 14px;">
                    {stock_name or symbol}
                </p>
                <p style="margin: 15px 0 0 0; color: #64748b; font-size: 14px;">
                    Ai setat o alertă pentru când prețul ajunge {threshold} <strong>{target_price:.2f} RON</strong>.
                </p>
            </div>
            
            <a href="https://finromania.ro/stocks/bvb/{symbol}" 
               style="display: block; background: {color}; color: #ffffff; text-decoration: none; 
                      padding: 15px 25px; border-radius: 8px; font-weight: bold; text-align: center; margin: 25px 0;">
                Vezi Detalii {symbol} →
            </a>
            
            <p style="font-size: 12px; color: #94a3b8; margin: 20px 0 0 0; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                ⚠️ Această alertă a fost declanșată o singură dată. Pentru a primi din nou notificări, 
                actualizează alerta din watchlist.
            </p>
        </div>
        
        <!-- Footer -->
        <div style="background: #1e3a5f; padding: 15px; text-align: center;">
            <p style="margin: 0; color: #a0c4e8; font-size: 12px;">
                <a href="https://finromania.ro" style="color: #60a5fa;">FinRomania.ro</a> • 
                Informații educative, NU sfaturi de investiții
            </p>
        </div>
    </div>
</body>
</html>
"""
            
            params = {
                "from": "FinRomania <noreply@finromania.ro>",
                "to": [email],
                "subject": f"{icon} Alertă: {symbol} {direction} {current_price:.2f} RON",
                "html": html
            }
            
            result = resend.Emails.send(params)
            logger.info(f"Price alert email sent to {email} for {symbol}: {result}")
            
            # Marchează notificarea ca email trimis
            await db.notifications.update_one(
                {"user_id": user_id, "custom_data.alert_key": f"price_alert_{alert_type}_{symbol}_{target_price}"},
                {"$set": {"email_sent": True}}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending price alert email: {e}")
            return False


notification_service = NotificationService()
