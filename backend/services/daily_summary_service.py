"""
Daily Market Summary Service
Generează și trimite rezumatul zilnic BVB prin email
"""
import os
import resend
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from config.database import get_database

LUNI_RO = {
    1: "ianuarie", 2: "februarie", 3: "martie", 4: "aprilie",
    5: "mai", 6: "iunie", 7: "iulie", 8: "august",
    9: "septembrie", 10: "octombrie", 11: "noiembrie", 12: "decembrie"
}

logger = logging.getLogger(__name__)

# Configure Resend
resend.api_key = os.environ.get("RESEND_API_KEY")

class DailySummaryService:
    """Serviciu pentru generarea și trimiterea rezumatului zilnic BVB"""
    
    def __init__(self):
        self.from_email = "FinRomania <noreply@finromania.ro>"
        # Folosim domeniul Resend pentru test dacă nu avem domeniu verificat
        self.from_email_test = "FinRomania <onboarding@resend.dev>"
    
    async def get_market_data(self) -> Dict:
        """Colectează datele de piață pentru rezumat"""
        db = await get_database()
        
        # Obține toate acțiunile BVB
        stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        
        if not stocks:
            return None
        
        # Sortează pentru top gainers/losers
        sorted_by_change = sorted(stocks, key=lambda x: x.get("change_percent", 0), reverse=True)
        
        top_gainers = sorted_by_change[:3]
        top_losers = sorted_by_change[-3:][::-1]  # Reverse pentru a avea cel mai mare loss primul
        
        # Top volume
        sorted_by_volume = sorted(stocks, key=lambda x: x.get("volume", 0), reverse=True)
        top_volume = sorted_by_volume[:3]
        
        # Calculează media pieței (proxy pentru BET)
        avg_change = sum(s.get("change_percent", 0) for s in stocks) / len(stocks) if stocks else 0
        
        # Sentiment general
        positive = sum(1 for s in stocks if s.get("change_percent", 0) > 0)
        negative = sum(1 for s in stocks if s.get("change_percent", 0) < 0)
        neutral = len(stocks) - positive - negative
        
        # Obține știri recente
        news = await db.news_ro.find({}, {"_id": 0, "title": 1, "source": 1}).sort("published_at", -1).limit(5).to_list(5)
        
        return {
            "date": datetime.now(timezone.utc).strftime("%d ") + LUNI_RO[datetime.now(timezone.utc).month] + datetime.now(timezone.utc).strftime(" %Y"),
            "total_stocks": len(stocks),
            "avg_change": round(avg_change, 2),
            "sentiment": {
                "positive": positive,
                "negative": negative,
                "neutral": neutral
            },
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "top_volume": top_volume,
            "news": news
        }
    
    async def generate_ai_summary(self, market_data: Dict) -> str:
        """Generează rezumatul AI folosind Emergent LLM"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            # Construiește contextul pentru AI
            context = f"""
DATE PIAȚĂ {market_data['date']}:

STATISTICI GENERALE:
- Total acțiuni analizate: {market_data['total_stocks']}
- Variație medie piață: {market_data['avg_change']:+.2f}%
- Acțiuni în creștere: {market_data['sentiment']['positive']}
- Acțiuni în scădere: {market_data['sentiment']['negative']}

TOP 3 CREȘTERI:
"""
            for s in market_data['top_gainers']:
                context += f"- {s.get('symbol')} ({s.get('name', '')}): {s.get('change_percent', 0):+.2f}% | {s.get('price', 0):.2f} RON\n"
            
            context += "\nTOP 3 SCĂDERI:\n"
            for s in market_data['top_losers']:
                context += f"- {s.get('symbol')} ({s.get('name', '')}): {s.get('change_percent', 0):+.2f}% | {s.get('price', 0):.2f} RON\n"
            
            context += "\nCEL MAI TRANZACȚIONATE (VOLUM):\n"
            for s in market_data['top_volume']:
                vol = s.get('volume', 0)
                vol_str = f"{vol/1000000:.1f}M" if vol >= 1000000 else f"{vol/1000:.0f}K"
                context += f"- {s.get('symbol')}: {vol_str} acțiuni | {s.get('price', 0):.2f} RON\n"
            
            if market_data.get('news'):
                context += "\nȘTIRI RECENTE:\n"
                for n in market_data['news'][:3]:
                    context += f"- {n.get('title', '')}\n"
            
            system_prompt = """Ești un analist financiar profesionist care scrie rezumate de piață pentru investitori români.
Scrie un rezumat de 150-200 cuvinte în română.
Începe cu sentimentul general al pieței.
Menționează TOP performerii și ce ar fi putut cauza mișcările.
Folosește CIFRE EXACTE mereu (volume, prețuri, procente) - NU cuvinte vagi ca "semnificativ", "considerabil".
Încheie cu o perspectivă pentru mâine (generală, fără predicții concrete).
Ton: profesionist dar accesibil.
NU da sfaturi de investiții specifice."""

            chat = LlmChat(
                api_key=os.environ.get("EMERGENT_UNIVERSAL_KEY"),
                session_id=f"daily_summary_{market_data['date']}",
                system_message=system_prompt
            ).with_model("openai", "gpt-4o")
            
            user_message = UserMessage(text=context)
            response = await chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            # Fallback la rezumat simplu
            return self._generate_simple_summary(market_data)
    
    def _generate_simple_summary(self, market_data: Dict) -> str:
        """Rezumat simplu fără AI (fallback)"""
        sentiment = "pozitiv" if market_data['avg_change'] > 0 else "negativ" if market_data['avg_change'] < 0 else "neutru"
        
        top_vol = market_data['top_volume'][0]
        vol = top_vol.get('volume', 0)
        vol_str = f"{vol/1000000:.1f}M" if vol >= 1000000 else f"{vol/1000:.0f}K"
        
        summary = f"""Piața BVB a încheiat ziua cu un sentiment {sentiment}, cu o variație medie de {market_data['avg_change']:+.2f}%.

Din {market_data['total_stocks']} acțiuni analizate, {market_data['sentiment']['positive']} au închis în creștere, iar {market_data['sentiment']['negative']} în scădere.

Cele mai bune performanțe au fost înregistrate de {market_data['top_gainers'][0].get('symbol')} ({market_data['top_gainers'][0].get('change_percent', 0):+.2f}%), {market_data['top_gainers'][1].get('symbol')} ({market_data['top_gainers'][1].get('change_percent', 0):+.2f}%) și {market_data['top_gainers'][2].get('symbol')} ({market_data['top_gainers'][2].get('change_percent', 0):+.2f}%).

Cea mai mare lichiditate a fost pe {top_vol.get('symbol')}, cu un volum de {vol_str} acțiuni tranzacționate."""
        
        return summary
    
    async def get_user_watchlist_data(self, user_id: str) -> List[Dict]:
        """Obține datele watchlist-ului unui user cu prețuri curente"""
        db = await get_database()
        watchlist = await db.watchlists.find_one(
            {"user_id": user_id}, {"_id": 0}
        )
        if not watchlist or not watchlist.get("items"):
            return []
        
        symbols = [item["symbol"] for item in watchlist["items"]]
        stocks = await db.stocks_bvb.find(
            {"symbol": {"$in": symbols}}, {"_id": 0}
        ).to_list(100)
        stock_map = {s["symbol"]: s for s in stocks}
        
        results = []
        for item in watchlist["items"]:
            s = stock_map.get(item["symbol"])
            if s:
                results.append({
                    "symbol": s.get("symbol"),
                    "price": s.get("price", 0),
                    "change_percent": s.get("change_percent", 0)
                })
        return results

    def _generate_email_html(self, market_data: Dict, ai_summary: str, is_pro: bool = False, watchlist_data: List[Dict] = None) -> str:
        """Generează HTML-ul pentru email"""
        
        # Header
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rezumatul Zilei BVB</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); padding: 30px 20px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 24px;">📊 Rezumatul Zilei BVB</h1>
            <p style="color: #a0c4e8; margin: 10px 0 0 0; font-size: 14px;">{market_data['date']}</p>
        </div>
        
        <!-- Market Overview -->
        <div style="padding: 20px; background-color: #f8fafc;">
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div style="flex: 1; padding: 10px;">
                    <p style="margin: 0; color: #64748b; font-size: 12px;">Variație Medie</p>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: {'#16a34a' if market_data['avg_change'] >= 0 else '#dc2626'};">
                        {market_data['avg_change']:+.2f}%
                    </p>
                </div>
                <div style="flex: 1; padding: 10px; border-left: 1px solid #e2e8f0;">
                    <p style="margin: 0; color: #64748b; font-size: 12px;">Creșteri / Scăderi</p>
                    <p style="margin: 5px 0 0 0; font-size: 18px;">
                        <span style="color: #16a34a;">▲{market_data['sentiment']['positive']}</span>
                        <span style="color: #94a3b8;"> / </span>
                        <span style="color: #dc2626;">▼{market_data['sentiment']['negative']}</span>
                    </p>
                </div>
            </div>
        </div>
        
        <!-- AI Summary -->
        <div style="padding: 20px;">
            <h2 style="color: #1e3a5f; font-size: 16px; margin: 0 0 15px 0; border-bottom: 2px solid #3b82f6; padding-bottom: 5px;">
                💡 Analiza Zilei
            </h2>
            <p style="color: #374151; line-height: 1.6; font-size: 14px;">
                {ai_summary}
            </p>
        </div>
        
        <!-- Top Gainers -->
        <div style="padding: 0 20px 20px 20px;">
            <h2 style="color: #16a34a; font-size: 14px; margin: 0 0 10px 0;">🚀 Top Creșteri</h2>
            <table style="width: 100%; border-collapse: collapse;">
"""
        for s in market_data['top_gainers']:
            html += f"""
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 8px 0; font-weight: bold; color: #1e3a5f;">{s.get('symbol')}</td>
                    <td style="padding: 8px 0; color: #64748b; font-size: 12px;">{s.get('name', '')[:20]}</td>
                    <td style="padding: 8px 0; text-align: right; color: #16a34a; font-weight: bold;">{s.get('change_percent', 0):+.2f}%</td>
                </tr>
"""
        html += """
            </table>
        </div>
        
        <!-- Top Losers -->
        <div style="padding: 0 20px 20px 20px;">
            <h2 style="color: #dc2626; font-size: 14px; margin: 0 0 10px 0;">📉 Top Scăderi</h2>
            <table style="width: 100%; border-collapse: collapse;">
"""
        for s in market_data['top_losers']:
            html += f"""
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 8px 0; font-weight: bold; color: #1e3a5f;">{s.get('symbol')}</td>
                    <td style="padding: 8px 0; color: #64748b; font-size: 12px;">{s.get('name', '')[:20]}</td>
                    <td style="padding: 8px 0; text-align: right; color: #dc2626; font-weight: bold;">{s.get('change_percent', 0):+.2f}%</td>
                </tr>
"""
        html += """
            </table>
        </div>
"""
        
        # Secțiunea personalizată Watchlist
        if watchlist_data:
            html += """
        <!-- Watchlist Personal -->
        <div style="padding: 0 20px 20px 20px; background-color: #f0fdf4; border-top: 2px solid #22c55e; margin: 0 20px; border-radius: 8px;">
            <h2 style="color: #15803d; font-size: 14px; margin: 0; padding: 15px 0 10px 0;">⭐ Din watchlist-ul tău</h2>
            <table style="width: 100%; border-collapse: collapse;">
"""
            for w in watchlist_data:
                change = w.get('change_percent', 0)
                color = '#16a34a' if change >= 0 else '#dc2626'
                icon = '✅' if change >= 0 else '🔻'
                html += f"""
                <tr style="border-bottom: 1px solid #dcfce7;">
                    <td style="padding: 6px 0; font-weight: bold; color: #1e3a5f;">{w.get('symbol')}</td>
                    <td style="padding: 6px 0; text-align: right; color: {color}; font-weight: bold;">{change:+.2f}% {icon}</td>
                    <td style="padding: 6px 0; text-align: right; color: #64748b; font-size: 12px;">{w.get('price', 0):.2f} RON</td>
                </tr>
"""
            html += """
            </table>
        </div>
"""
        
        # CTA pentru non-PRO
        if not is_pro:
            html += """
        <!-- PRO CTA -->
        <div style="padding: 20px; background-color: #fef3c7; text-align: center;">
            <p style="margin: 0 0 10px 0; color: #92400e; font-size: 14px;">
                🔒 Vrei analiză detaliată + alerte de preț?
            </p>
            <a href="https://finromania.ro/pricing" style="display: inline-block; background-color: #f59e0b; color: #ffffff; text-decoration: none; padding: 10px 25px; border-radius: 5px; font-weight: bold;">
                Upgrade la PRO - 49 RON/lună
            </a>
        </div>
"""
        
        # Footer
        html += """
        <!-- Footer -->
        <div style="padding: 20px; background-color: #1e3a5f; text-align: center;">
            <p style="margin: 0; color: #a0c4e8; font-size: 12px;">
                📱 Vezi mai multe pe <a href="https://finromania.ro" style="color: #60a5fa;">FinRomania.ro</a>
            </p>
            <p style="margin: 10px 0 0 0; color: #64748b; font-size: 10px;">
                Acest email este trimis automat. Pentru a te dezabona, 
                <a href="https://finromania.ro/settings/notifications" style="color: #64748b;">click aici</a>.
            </p>
            <p style="margin: 10px 0 0 0; color: #64748b; font-size: 10px;">
                ⚠️ Informații educative, NU sfaturi de investiții.
            </p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    async def send_daily_summary(self, user_email: str, user_name: str = None, is_pro: bool = False, user_id: str = None) -> bool:
        """Trimite rezumatul zilnic către un user"""
        try:
            # Colectează datele
            market_data = await self.get_market_data()
            if not market_data:
                logger.error("No market data available for summary")
                return False
            
            # Generează rezumatul AI
            ai_summary = await self.generate_ai_summary(market_data)
            
            # Obține watchlist-ul userului
            watchlist_data = []
            if user_id:
                watchlist_data = await self.get_user_watchlist_data(user_id)
            
            # Generează HTML
            html = self._generate_email_html(market_data, ai_summary, is_pro, watchlist_data)
            
            # Trimite email
            params = {
                "from": self.from_email,
                "to": [user_email],
                "subject": f"Rezumatul Zilei BVB - {market_data['date']}",
                "html": html
            }
            
            email = resend.Emails.send(params)
            logger.info(f"Daily summary sent to {user_email}: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending daily summary to {user_email}: {e}")
            return False
    
    async def send_to_all_subscribers(self) -> Dict:
        """Trimite rezumatul zilnic la toți userii abonați (max 95/zi pt Resend free)"""
        db = await get_database()
        results = {"sent": 0, "failed": 0, "skipped": 0, "limit_reached": False}
        DAILY_LIMIT = 95  # Resend free = 100/zi, lăsăm 5 pentru test emails
        
        try:
            subscribers = await db.users.find({
                "daily_summary_enabled": True,
                "email": {"$exists": True, "$ne": ""}
            }, {"_id": 0, "email": 1, "name": 1, "subscription_level": 1, "user_id": 1}).to_list(500)
            
            logger.info(f"Found {len(subscribers)} subscribers for daily summary (limit: {DAILY_LIMIT})")
            
            for user in subscribers:
                if results["sent"] >= DAILY_LIMIT:
                    results["skipped"] += 1
                    results["limit_reached"] = True
                    continue
                
                email = user.get("email")
                if not email:
                    results["skipped"] += 1
                    continue
                
                is_pro = user.get("subscription_level") in ["pro", "premium", "early_adopter"]
                
                success = await self.send_daily_summary(
                    user_email=email,
                    user_name=user.get("name"),
                    is_pro=is_pro,
                    user_id=user.get("user_id")
                )
                
                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
            
            if results["limit_reached"]:
                logger.warning(f"⚠️ Daily email limit reached ({DAILY_LIMIT}). {results['skipped']} subscribers skipped.")
            logger.info(f"Daily summary results: {results}")
            
        except Exception as e:
            logger.error(f"Error in send_to_all_subscribers: {e}")
        
        return results


daily_summary_service = DailySummaryService()
