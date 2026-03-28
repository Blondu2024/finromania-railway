"""Notification Service - Sistem de notificări pentru Early Adopter și alte alerte"""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging
import os
import asyncio
import resend
from config.database import get_database
import uuid

logger = logging.getLogger(__name__)

# Configure Resend for notifications
resend.api_key = os.environ.get("RESEND_API_KEY")
FROM_EMAIL = "FinRomania <noreply@finromania.ro>"
SITE_URL = "https://finromania.ro"

# Emergent LLM Key for AI commentary
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "sk-emergent-5C341A28678CfD18c0")

# ─── Helper: trimitere email non-blocking ────────────────────────────────────
async def _send_email(params: dict) -> bool:
    """Trimite email via Resend (non-blocking, async)"""
    try:
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent: {result}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


# ─── Helper: generare comentariu AI ─────────────────────────────────────────
async def _generate_ai_comment(context: str) -> str:
    """Generează 1-2 propoziții de context cu AI. Returnează '' dacă eșuează."""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"email-ai-{uuid.uuid4().hex[:8]}",
            system_message=(
                "Ești un asistent financiar concis pentru FinRomania.ro. "
                "Oferi un comentariu SCURT (1-2 propoziții) despre contextul financiar dat. "
                "NU inventa niciun preț sau cifră. Folosește DOAR datele furnizate în context. "
                "Scrie în română, profesional."
            )
        ).with_model("openai", "gpt-4o-mini")
        response = await chat.send_message(UserMessage(text=context))
        return response.strip()[:400]
    except Exception as e:
        logger.warning(f"AI comment generation failed: {e}")
        return ""



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
            # Trimite email de avertizare
            if user.get("email"):
                await self.send_early_adopter_expiring_email(
                    user_email=user["email"],
                    user_name=user.get("name", ""),
                    days_left=7,
                    expires_at=user.get("subscription_expires_at", "")
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
            if user.get("email"):
                await self.send_early_adopter_expiring_email(
                    user_email=user["email"],
                    user_name=user.get("name", ""),
                    days_left=3,
                    expires_at=user.get("subscription_expires_at", "")
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
            if user.get("email"):
                await self.send_early_adopter_expiring_email(
                    user_email=user["email"],
                    user_name=user.get("name", ""),
                    days_left=1,
                    expires_at=user.get("subscription_expires_at", "")
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
                "from": FROM_EMAIL,
                "to": [email],
                "subject": f"{icon} Alertă: {symbol} {direction} {current_price:.2f} RON",
                "html": html
            }
            
            result = await _send_email(params)
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


    # ─── EARLY ADOPTER EXPIRING EMAIL ────────────────────────────────────────
    async def send_early_adopter_expiring_email(
        self,
        user_email: str,
        user_name: str,
        days_left: int,
        expires_at: str
    ) -> bool:
        """Trimite email de avertizare că abonamentul PRO expiră."""
        try:
            name = user_name or "Investitorule"
            icon = "⏰" if days_left > 1 else "❗"
            urgency_color = "#dc2626" if days_left <= 1 else ("#d97706" if days_left <= 3 else "#2563eb")
            days_text = "mâine" if days_left <= 1 else f"în {days_left} zile"

            html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f5f5f5;">
  <div style="max-width:520px;margin:0 auto;background:#ffffff;">
    <div style="background:{urgency_color};padding:24px;text-align:center;">
      <h1 style="color:#fff;margin:0;font-size:22px;">{icon} Abonament PRO expiră {days_text}</h1>
    </div>
    <div style="padding:28px;">
      <p style="font-size:16px;color:#333;margin:0 0 16px;">Salut {name},</p>
      <p style="font-size:15px;color:#444;margin:0 0 20px;">
        Abonamentul tău <strong>FinRomania PRO</strong> expiră <strong>{days_text}</strong>.
        Nu vrei să pierzi accesul la funcțiile premium!
      </p>
      <div style="background:#f8fafc;border-left:4px solid {urgency_color};padding:16px;margin:20px 0;border-radius:4px;">
        <p style="margin:0;font-weight:bold;color:#1e3a5f;">Ce pierzi după expirare:</p>
        <ul style="margin:10px 0 0 0;padding-left:20px;color:#64748b;font-size:14px;">
          <li>Screener PRO cu indicatori tehnici (RSI, MACD)</li>
          <li>Calculator Fiscal AI</li>
          <li>Portofoliu BVB PRO cu date live</li>
          <li>Întrebări AI nelimitate</li>
          <li>Alerte preț watchlist prin email</li>
        </ul>
      </div>
      <a href="{SITE_URL}/pricing"
         style="display:block;background:{urgency_color};color:#fff;text-decoration:none;
                padding:14px 24px;border-radius:8px;font-weight:bold;text-align:center;margin:24px 0;">
        Continuă cu PRO — 49 RON/lună →
      </a>
      <p style="font-size:12px;color:#94a3b8;margin:20px 0 0;border-top:1px solid #e2e8f0;padding-top:16px;">
        Mulțumim că ești unul dintre primii utilizatori FinRomania.ro!
      </p>
    </div>
    <div style="background:#1e3a5f;padding:14px;text-align:center;">
      <p style="margin:0;color:#a0c4e8;font-size:12px;">
        <a href="{SITE_URL}" style="color:#60a5fa;">FinRomania.ro</a> •
        <a href="{SITE_URL}/notifications" style="color:#60a5fa;">Dezabonare</a>
      </p>
    </div>
  </div>
</body>
</html>"""

            return await _send_email({
                "from": FROM_EMAIL,
                "to": [user_email],
                "subject": f"{icon} PRO gratuit expiră {days_text} — FinRomania",
                "html": html
            })
        except Exception as e:
            logger.error(f"Error sending early adopter expiring email: {e}")
            return False


    # ─── WELCOME EMAIL ───────────────────────────────────────────────────────
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Trimite email de bun venit la prima înregistrare/logare."""
        try:
            name = user_name.split()[0] if user_name else "Investitorule"
            html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f5f5f5;">
  <div style="max-width:520px;margin:0 auto;background:#ffffff;">
    <div style="background:linear-gradient(135deg,#1e3a5f,#2563eb);padding:32px;text-align:center;">
      <h1 style="color:#fff;margin:0;font-size:26px;">🎉 Bun venit pe FinRomania!</h1>
      <p style="color:#bfdbfe;margin:8px 0 0;font-size:15px;">Investește Inteligent pe BVB</p>
    </div>
    <div style="padding:28px;">
      <p style="font-size:16px;color:#333;margin:0 0 16px;">Salut {name},</p>
      <p style="font-size:15px;color:#444;margin:0 0 20px;">
        Contul tău FinRomania este acum activ! Explorează platforma:
      </p>
      <div style="display:grid;gap:12px;">
        <a href="{SITE_URL}/stocks" style="display:block;background:#f0f9ff;border:1px solid #bae6fd;border-radius:8px;padding:14px 18px;text-decoration:none;color:#1e3a5f;">
          <strong>📊 Bursa BVB Live</strong><br>
          <span style="font-size:13px;color:#64748b;">Date live cu toate acțiunile BVB + heatmap</span>
        </a>
        <a href="{SITE_URL}/calculator-fiscal" style="display:block;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:14px 18px;text-decoration:none;color:#1e3a5f;">
          <strong>🧮 Calculator Fiscal</strong><br>
          <span style="font-size:13px;color:#64748b;">Calculează impozitul pe câștiguri BVB (1-3%)</span>
        </a>
        <a href="{SITE_URL}/rezumat-zilnic" style="display:block;background:#fefce8;border:1px solid #fef08a;border-radius:8px;padding:14px 18px;text-decoration:none;color:#1e3a5f;">
          <strong>📰 Rezumat Zilnic BVB</strong><br>
          <span style="font-size:13px;color:#64748b;">Analiza AI după fiecare zi de tranzacționare</span>
        </a>
      </div>
      <div style="background:#fef3c7;border:1px solid #fde68a;border-radius:8px;padding:16px;margin:20px 0;">
        <p style="margin:0;color:#92400e;font-size:14px;">
          🎁 <strong>PRO GRATUIT până pe 5 Iunie 2026!</strong><br>
          Ai acces complet la toate funcțiile PRO fără card bancar.
        </p>
      </div>
      <a href="{SITE_URL}" style="display:block;background:#2563eb;color:#fff;text-decoration:none;
              padding:14px 24px;border-radius:8px;font-weight:bold;text-align:center;margin:16px 0;">
        Explorează FinRomania →
      </a>
    </div>
    <div style="background:#1e3a5f;padding:14px;text-align:center;">
      <p style="margin:0;color:#a0c4e8;font-size:12px;">
        <a href="{SITE_URL}" style="color:#60a5fa;">FinRomania.ro</a> •
        Informații educative, NU sfaturi de investiții
      </p>
    </div>
  </div>
</body>
</html>"""

            return await _send_email({
                "from": FROM_EMAIL,
                "to": [user_email],
                "subject": "🎉 Bun venit pe FinRomania! Contul tău este activ",
                "html": html
            })
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return False


    # ─── WATCHLIST BIG MOVES CHECK ───────────────────────────────────────────
    async def check_watchlist_big_moves(self) -> dict:
        """
        Verifică dacă acțiunile din watchlist au variat cu peste 5% și trimite email.
        Rulează după fiecare update BVB (job scheduler).
        """
        db = await get_database()
        results = {"checked": 0, "emails_sent": 0, "errors": 0}

        try:
            # Obține toate watchlist-urile
            watchlists = await db.watchlists.find(
                {"items": {"$exists": True, "$ne": []}}
            ).to_list(2000)

            for wl in watchlists:
                user_id = wl.get("user_id")
                if not user_id:
                    continue

                # Verifică preferința utilizatorului
                prefs_doc = await db.notification_preferences.find_one(
                    {"user_id": user_id}, {"_id": 0}
                )
                prefs = prefs_doc.get("preferences", {}) if prefs_doc else {}
                if not prefs.get("watchlist_big_moves", True):
                    continue

                # Obține datele utilizatorului
                user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "email": 1, "name": 1})
                if not user or not user.get("email"):
                    continue

                # Colectează acțiunile cu variații mari
                big_movers = []
                for item in wl.get("items", []):
                    symbol = item.get("symbol")
                    if not symbol:
                        continue
                    results["checked"] += 1

                    stock = await db.stocks_bvb.find_one(
                        {"symbol": symbol},
                        {"_id": 0, "price": 1, "change_percent": 1, "name": 1}
                    )
                    if not stock:
                        continue

                    change_pct = stock.get("change_percent", 0) or 0
                    if abs(change_pct) >= 5.0:
                        big_movers.append({
                            "symbol": symbol,
                            "name": stock.get("name", symbol),
                            "price": stock.get("price", 0),
                            "change_pct": change_pct
                        })

                if not big_movers:
                    continue

                # Evită trimiterea de emailuri duble în aceeași zi
                today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                already_sent = await db.email_logs.find_one({
                    "user_id": user_id,
                    "email_type": "watchlist_big_moves",
                    "date": today
                })
                if already_sent:
                    continue

                # Trimite email
                sent = await self.send_watchlist_big_moves_email(
                    user_email=user["email"],
                    user_name=user.get("name", ""),
                    movers=big_movers
                )

                if sent:
                    # Înregistrează că am trimis emailul azi
                    await db.email_logs.insert_one({
                        "user_id": user_id,
                        "email_type": "watchlist_big_moves",
                        "date": today,
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                        "movers": [m["symbol"] for m in big_movers]
                    })
                    results["emails_sent"] += 1

        except Exception as e:
            logger.error(f"Error in check_watchlist_big_moves: {e}")
            results["errors"] += 1

        return results


    async def send_watchlist_big_moves_email(
        self,
        user_email: str,
        user_name: str,
        movers: list
    ) -> bool:
        """Trimite email cu mișcările mari din watchlist (>5%), cu comentariu AI scurt."""
        try:
            name = user_name.split()[0] if user_name else "Investitorule"

            # Construiește lista de mișcări (date REALE din DB)
            rows_html = ""
            context_for_ai = "Mișcări watchlist BVB azi:\n"
            for m in movers[:10]:  # Max 10
                pct = m["change_pct"]
                color = "#16a34a" if pct >= 0 else "#dc2626"
                arrow = "▲" if pct >= 0 else "▼"
                rows_html += f"""
                <tr style="border-bottom:1px solid #e2e8f0;">
                  <td style="padding:12px 8px;font-weight:bold;">{m['symbol']}</td>
                  <td style="padding:12px 8px;color:#64748b;font-size:13px;">{m['name'][:30]}</td>
                  <td style="padding:12px 8px;text-align:right;">{m['price']:.2f} RON</td>
                  <td style="padding:12px 8px;text-align:right;color:{color};font-weight:bold;">
                    {arrow} {abs(pct):.2f}%
                  </td>
                </tr>"""
                context_for_ai += f"  {m['symbol']} ({m['name']}): {'+' if pct >= 0 else ''}{pct:.2f}% la {m['price']:.2f} RON\n"

            # Comentariu AI (scurt, fără date inventate)
            ai_context = (
                f"Aceste acțiuni din watchlist-ul unui investitor au variat cu peste 5% astăzi:\n"
                f"{context_for_ai}\n"
                f"Adaugă un comentariu scurt (1-2 propoziții) despre ce ar trebui să știe un investitor "
                f"când vede astfel de variații mari. Nu inventa niciun preț sau cifră."
            )
            ai_comment = await _generate_ai_comment(ai_context)
            ai_section = ""
            if ai_comment:
                ai_section = f"""
                <div style="background:#f0f9ff;border-left:4px solid #2563eb;padding:14px 16px;margin:20px 0;border-radius:4px;">
                  <p style="margin:0;font-size:14px;color:#1e3a5f;font-style:italic;">
                    🤖 <strong>Context AI:</strong> {ai_comment}
                  </p>
                  <p style="margin:6px 0 0;font-size:11px;color:#94a3b8;">
                    ⚠️ Informație educativă, nu sfat de investiții.
                  </p>
                </div>"""

            html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f5f5f5;">
  <div style="max-width:560px;margin:0 auto;background:#ffffff;">
    <div style="background:linear-gradient(135deg,#1e3a5f,#2563eb);padding:24px;text-align:center;">
      <h1 style="color:#fff;margin:0;font-size:20px;">📊 Mișcări Mari în Watchlist</h1>
      <p style="color:#bfdbfe;margin:6px 0 0;font-size:13px;">Acțiunile tale au variat cu peste 5% astăzi</p>
    </div>
    <div style="padding:24px;">
      <p style="font-size:15px;color:#333;margin:0 0 16px;">Salut {name},</p>
      <p style="font-size:14px;color:#64748b;margin:0 0 20px;">
        Am detectat mișcări semnificative (≥5%) în watchlist-ul tău:
      </p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <thead>
          <tr style="background:#f8fafc;">
            <th style="padding:10px 8px;text-align:left;color:#64748b;font-size:12px;border-bottom:2px solid #e2e8f0;">SIMBOL</th>
            <th style="padding:10px 8px;text-align:left;color:#64748b;font-size:12px;border-bottom:2px solid #e2e8f0;">COMPANIE</th>
            <th style="padding:10px 8px;text-align:right;color:#64748b;font-size:12px;border-bottom:2px solid #e2e8f0;">PREȚ</th>
            <th style="padding:10px 8px;text-align:right;color:#64748b;font-size:12px;border-bottom:2px solid #e2e8f0;">VARIAȚIE</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
      {ai_section}
      <a href="{SITE_URL}/watchlist"
         style="display:block;background:#2563eb;color:#fff;text-decoration:none;
                padding:14px 24px;border-radius:8px;font-weight:bold;text-align:center;margin:20px 0;">
        Deschide Watchlist →
      </a>
    </div>
    <div style="background:#1e3a5f;padding:14px;text-align:center;">
      <p style="margin:0;color:#a0c4e8;font-size:12px;">
        <a href="{SITE_URL}" style="color:#60a5fa;">FinRomania.ro</a> •
        <a href="{SITE_URL}/notifications" style="color:#60a5fa;">Setări notificări</a> •
        Informații educative, NU sfaturi de investiții
      </p>
    </div>
  </div>
</body>
</html>"""

            return await _send_email({
                "from": FROM_EMAIL,
                "to": [user_email],
                "subject": f"📊 Watchlist: {', '.join(m['symbol'] for m in movers[:3])} au variat ≥5% azi",
                "html": html
            })
        except Exception as e:
            logger.error(f"Error sending watchlist big moves email: {e}")
            return False


notification_service = NotificationService()
