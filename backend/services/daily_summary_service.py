"""
Daily Market Summary Service
Generează și trimite rezumatul zilnic BVB prin email
IMPORTANT: Rezumatul se generează O SINGURĂ DATĂ pe zi și se salvează în MongoDB
"""
import os
import asyncio
import resend
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from config.database import get_database
from apis.eodhd_client import get_eodhd_client
import pytz

LUNI_RO = {
    1: "ianuarie", 2: "februarie", 3: "martie", 4: "aprilie",
    5: "mai", 6: "iunie", 7: "iulie", 8: "august",
    9: "septembrie", 10: "octombrie", 11: "noiembrie", 12: "decembrie"
}

BUCHAREST_TZ = pytz.timezone('Europe/Bucharest')

logger = logging.getLogger(__name__)

# Configure Resend
resend.api_key = os.environ.get("RESEND_API_KEY")

class DailySummaryService:
    """
    Serviciu pentru generarea și trimiterea rezumatului zilnic BVB.
    
    FLOW:
    1. La 18:10 (după închiderea BVB), job-ul generează rezumatul și îl salvează în MongoDB
    2. Când un utilizator accesează /rezumat-zilnic, se servește rezumatul din DB
    3. Emailurile se trimit din același rezumat salvat
    """
    
    def __init__(self):
        self.from_email = "FinRomania <noreply@finromania.ro>"
        self.from_email_test = "FinRomania <onboarding@resend.dev>"
        self.eodhd_client = get_eodhd_client()
    
    def _get_today_date_key(self) -> str:
        """Returnează cheia pentru data de azi în format YYYY-MM-DD (timezone Bucharest)"""
        now = datetime.now(BUCHAREST_TZ)
        return now.strftime("%Y-%m-%d")
    
    def _get_romanian_date(self) -> str:
        """Returnează data în format românesc (ex: 20 martie 2026)"""
        now = datetime.now(BUCHAREST_TZ)
        return f"{now.day} {LUNI_RO[now.month]} {now.year}"
    
    async def get_saved_summary(self, date_key: str = None) -> Optional[Dict]:
        """
        Obține rezumatul salvat pentru o anumită dată.
        Dacă date_key este None, folosește data de azi.
        """
        db = await get_database()
        if date_key is None:
            date_key = self._get_today_date_key()
        
        summary = await db.daily_summaries.find_one(
            {"date_key": date_key},
            {"_id": 0}
        )
        return summary
    
    async def save_summary(self, summary_data: Dict) -> bool:
        """Salvează rezumatul în MongoDB"""
        db = await get_database()
        date_key = self._get_today_date_key()
        
        logger.info(f"Saving summary for date_key: {date_key}")
        
        # Upsert - actualizează dacă există, creează dacă nu
        try:
            result = await db.daily_summaries.update_one(
                {"date_key": date_key},
                {"$set": {
                    "date_key": date_key,
                    "date_display": summary_data.get("date"),
                    "market_data": summary_data.get("market_data"),
                    "ai_summary": summary_data.get("ai_summary"),
                    "generated_at": datetime.now(timezone.utc),
                    "emails_sent": 0
                }},
                upsert=True
            )
            
            logger.info(f"Save result: matched={result.matched_count}, modified={result.modified_count}, upserted_id={result.upserted_id}")
            
            # Verify it was saved
            saved = await db.daily_summaries.find_one({"date_key": date_key})
            if saved:
                logger.info(f"✅ Verified: Summary saved for {date_key}")
            else:
                logger.error(f"❌ Verification failed: Summary NOT found for {date_key}")
            
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
            return False
    
    def _is_market_day(self) -> bool:
        """Verifică dacă azi e zi de bursă (Luni-Vineri, nu sărbătoare)"""
        now = datetime.now(BUCHAREST_TZ)
        # Weekend
        if now.weekday() >= 5:
            logger.info(f"⏭️ Weekend ({now.strftime('%A')}) - skip daily summary")
            return False
        return True

    async def generate_and_save_daily_summary(self) -> Dict:
        """
        Generează rezumatul zilnic și îl salvează în MongoDB.
        Această funcție se apelează O SINGURĂ DATĂ pe zi de către job-ul scheduler.
        """
        # Verifică dacă e zi de bursă
        if not self._is_market_day():
            return None

        # Check if already generated today (prevent duplicates on redeploy)
        db = await get_database()
        date_key = self._get_today_date_key()
        existing = await db.daily_summaries.find_one({"date_key": date_key})
        if existing:
            logger.info(f"Daily summary already exists for {date_key}, skipping generation")
            return existing

        logger.info("🔄 Generating daily summary...")

        # Colectează datele de piață
        market_data = await self.get_market_data()
        if not market_data:
            logger.error("No market data available for summary")
            return None

        # Verifică dacă bursa a fost efectiv deschisă (volum > 0 pe actiuni)
        traded = [s for s in market_data.get("top_volume", []) if (s.get("volume") or 0) > 0]
        if not traded:
            logger.info("⏭️ No trading volume today (holiday?) - skip daily summary")
            return None
        
        # Generează rezumatul AI
        ai_summary = await self.generate_ai_summary(market_data)
        
        # Construiește obiectul complet
        summary = {
            "success": True,
            "date": market_data["date"],
            "market_data": {
                "bet_change": market_data.get("bet_change"),
                "avg_change": market_data["avg_change"],
                "indices": market_data.get("indices", {}),
                "sentiment": market_data["sentiment"],
                "top_gainers": [
                    {"symbol": s.get("symbol"), "name": s.get("name"), "change_percent": s.get("change_percent"), "price": s.get("price")}
                    for s in market_data["top_gainers"]
                ],
                "top_losers": [
                    {"symbol": s.get("symbol"), "name": s.get("name"), "change_percent": s.get("change_percent"), "price": s.get("price")}
                    for s in market_data["top_losers"]
                ],
                "top_volume": [
                    {"symbol": s.get("symbol"), "volume": s.get("volume"), "price": s.get("price")}
                    for s in market_data["top_volume"]
                ]
            },
            "ai_summary": ai_summary
        }
        
        # Salvează în MongoDB
        await self.save_summary(summary)
        
        logger.info(f"✅ Daily summary generated and saved for {self._get_today_date_key()}")
        return summary
    
    async def get_summary_for_display(self) -> Optional[Dict]:
        """
        Obține rezumatul pentru afișare pe site.
        
        IMPORTANT: NU generează rezumat nou! Doar returnează ce e salvat în DB.
        - Dacă există rezumat pentru azi → îl returnează
        - Dacă nu există pentru azi → returnează cel mai recent rezumat (de ieri)
        - Dacă nu există deloc → returnează None
        
        Rezumatul se generează DOAR de job-ul de la 18:10, nu la cererea utilizatorului!
        """
        db = await get_database()
        
        # 1. Încearcă să obțină rezumatul pentru azi
        today_key = self._get_today_date_key()
        saved = await db.daily_summaries.find_one(
            {"date_key": today_key},
            {"_id": 0}
        )
        
        if saved:
            logger.info(f"Serving today's summary: {today_key}")
            return {
                "success": True,
                "date": saved.get("date_display"),
                "market_data": saved.get("market_data"),
                "ai_summary": saved.get("ai_summary"),
                "cached": True,
                "is_today": True,
                "generated_at": saved.get("generated_at")
            }
        
        # 2. Dacă nu există pentru azi, caută cel mai recent rezumat
        latest = await db.daily_summaries.find_one(
            {},
            {"_id": 0},
            sort=[("date_key", -1)]  # Cel mai recent
        )
        
        if latest:
            logger.info(f"No summary for today, serving latest: {latest.get('date_key')}")
            return {
                "success": True,
                "date": latest.get("date_display"),
                "market_data": latest.get("market_data"),
                "ai_summary": latest.get("ai_summary"),
                "cached": True,
                "is_today": False,
                "from_date": latest.get("date_key"),
                "generated_at": latest.get("generated_at"),
                "note": f"Rezumatul din {latest.get('date_display')}. Cel de azi va fi disponibil la 18:10."
            }
        
        # 3. Nu există niciun rezumat salvat
        logger.warning("No saved summaries found in database")
        return None
    
    async def get_market_data(self) -> Dict:
        """Colectează datele de piață pentru rezumat"""
        db = await get_database()
        
        # Obține toate acțiunile BVB
        stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        
        if not stocks:
            return None
        
        # Obține indicii BVB din TradingView (date exacte în timp real)
        indices = {}
        try:
            from apis.tradingview_client import get_tradingview_client
            
            tv_client = get_tradingview_client()
            tv_indices = await tv_client.get_bvb_indices()
            
            for idx in tv_indices:
                indices[idx["id"]] = {
                    "value": idx.get("value"),
                    "change_percent": idx.get("change_percent"),
                    "is_live": idx.get("is_live", True)
                }
            
            logger.info(f"Daily Summary: Got {len(indices)} indices from TradingView")
        except Exception as e:
            logger.warning(f"Could not fetch BVB indices from TradingView: {e}")
            # Fallback: use last cached indices from MongoDB
            try:
                db_cache = await get_database()
                cached = await db_cache.bvb_indices_cache.find_one({"_id": "latest"})
                if cached:
                    for idx in cached.get("indices", []):
                        indices[idx["id"]] = {
                            "value": idx.get("value"),
                            "change_percent": idx.get("change_percent"),
                            "is_live": False
                        }
                    logger.info(f"Daily Summary: Using {len(indices)} cached indices")
            except Exception as e2:
                logger.error(f"Could not load cached indices: {e2}")
        
        # Sortează pentru top gainers/losers
        # IMPORTANT: Excludem acțiunile cu volum 0 (nu s-au tranzacționat azi = prețuri vechi)
        # Aceste acțiuni "nelichide" apar cu +10%/+15% din sesiuni anterioare → date false
        traded_stocks = [
            s for s in stocks
            if (s.get("volume") or 0) > 0 and s.get("price", 0) > 0
        ]
        
        # Dacă nu avem suficiente acțiuni tranzacționate, coborâm pragul
        if len(traded_stocks) < 6:
            traded_stocks = [s for s in stocks if s.get("price", 0) > 0]
        
        sorted_by_change = sorted(traded_stocks, key=lambda x: x.get("change_percent", 0), reverse=True)
        
        top_gainers = sorted_by_change[:3]
        top_losers = sorted_by_change[-3:][::-1]
        
        # Top volume — cele mai lichide (tranzacționate) azi
        sorted_by_volume = sorted(stocks, key=lambda x: x.get("volume", 0), reverse=True)
        top_volume = [s for s in sorted_by_volume if (s.get("volume") or 0) > 0][:3]
        
        # Calculează media pieței — doar acțiuni tranzacționate azi
        if traded_stocks:
            avg_change = sum(s.get("change_percent", 0) for s in traded_stocks) / len(traded_stocks)
        else:
            avg_change = sum(s.get("change_percent", 0) for s in stocks) / len(stocks) if stocks else 0
        
        # Folosește BET ca indicator principal dacă e disponibil
        bet_change = indices.get("BET", {}).get("change_percent")
        headline_change = bet_change if bet_change is not None else round(avg_change, 2)
        
        # Sentiment general — pe acțiunile tranzacționate (nu cele cu vol=0)
        ref_stocks = traded_stocks if len(traded_stocks) >= 10 else stocks
        positive = sum(1 for s in ref_stocks if s.get("change_percent", 0) > 0)
        negative = sum(1 for s in ref_stocks if s.get("change_percent", 0) < 0)
        neutral = len(ref_stocks) - positive - negative
        
        # Obține știri recente
        news = await db.news_ro.find({}, {"_id": 0, "title": 1, "source": 1}).sort("published_at", -1).limit(5).to_list(5)
        
        return {
            "date": datetime.now(BUCHAREST_TZ).strftime("%d ") + LUNI_RO[datetime.now(BUCHAREST_TZ).month] + datetime.now(BUCHAREST_TZ).strftime(" %Y"),
            "total_stocks": len(stocks),
            "avg_change": round(avg_change, 2),
            "bet_change": headline_change,  # Indicele BET real sau media ca fallback
            "indices": indices,  # Toți indicii BVB
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
            from utils.llm import LlmChat, UserMessage
            
            # Construiește contextul pentru AI cu indicii BVB reali
            indices = market_data.get('indices', {})
            bet_info = indices.get('BET', {})
            bettr_info = indices.get('BETTR', {})
            betfi_info = indices.get('BETFI', {})
            betng_info = indices.get('BETNG', {})
            betxt_info = indices.get('BETXT', {})
            betaero_info = indices.get('BETAeRO', {})
            
            context = f"""DATE OFICIALE BVB - {market_data['date']}

====== INDICII BVB (VALORI EXACTE) ======
• BET: {bet_info.get('value', 'N/A')} puncte ({bet_info.get('change_percent', 0):+.2f}%)
• BET-TR (Total Return): {bettr_info.get('value', 'N/A')} ({bettr_info.get('change_percent', 0):+.2f}%)
• BET-FI (Financiar): {betfi_info.get('value', 'N/A')} ({betfi_info.get('change_percent', 0):+.2f}%)
• BET-NG (Energie): {betng_info.get('value', 'N/A')} ({betng_info.get('change_percent', 0):+.2f}%)
• BET-XT (Extended): {betxt_info.get('value', 'N/A')} ({betxt_info.get('change_percent', 0):+.2f}%)
• BETAeRO: {betaero_info.get('value', 'N/A')} ({betaero_info.get('change_percent', 0):+.2f}%)

====== STATISTICI PIAȚĂ ======
• Acțiuni analizate: {market_data['total_stocks']}
• În creștere: {market_data['sentiment']['positive']}
• În scădere: {market_data['sentiment']['negative']}
• Nemodificate: {market_data['sentiment']['neutral']}

====== TOP 3 CREȘTERI (CÂȘTIGĂTORI) ======"""
            for s in market_data['top_gainers']:
                context += f"\n• {s.get('symbol')} ({s.get('name', 'N/A')}): {s.get('change_percent', 0):+.2f}% → {s.get('price', 0):.4f} RON"
            
            context += "\n\n====== TOP 3 SCĂDERI (PERDANȚI) ======"
            for s in market_data['top_losers']:
                context += f"\n• {s.get('symbol')} ({s.get('name', 'N/A')}): {s.get('change_percent', 0):+.2f}% → {s.get('price', 0):.4f} RON"
            
            context += "\n\n====== CELE MAI LICHIDE ACȚIUNI (VOLUM) ======"
            for s in market_data['top_volume']:
                vol = s.get('volume', 0)
                vol_str = f"{vol:,.0f}".replace(',', '.') if vol else "0"
                context += f"\n• {s.get('symbol')}: {vol_str} acțiuni tranzacționate → {s.get('price', 0):.4f} RON ({s.get('change_percent', 0):+.2f}%)"
            
            context += """

====== AVERTISMENT PENTRU AI ======
FOLOSEȘTE DOAR DATELE DE MAI SUS!
NU inventa cauze, NU specula, NU prezice.
Dacă nu ai o informație, NU o menționa."""
            
            system_prompt = """Ești un analist financiar care redactează rezumate FACTUALE pentru Bursa de Valori București (BVB).

REGULI OBLIGATORII - ÎNCĂLCAREA = REZUMAT INVALID:

❌ INTERZIS TOTAL:
- NU inventa cauze/motive (ex: "din cauza tensiunilor geopolitice", "datorită rezultatelor financiare")
- NU specula (ex: "ar putea", "probabil", "posibil")
- NU da sfaturi sau predicții (ex: "se recomandă", "investitorii ar trebui")
- NU scrie cifre pe care NU le ai în date (ex: capitalizare de piață, P/E ratio)
- NU compara cu zilele anterioare dacă nu ai acele date

✅ OBLIGATORIU:
- Folosește DOAR cifrele exacte din datele primite
- Indicele BET = referință principală (valoare + variație %)
- Menționează TOȚI indicii (BET-TR, BET-FI, BET-NG) cu cifrele lor
- Listează TOP 3 creșteri și scăderi cu % și preț
- Menționează cel puțin o acțiune cu volum mare

STRUCTURĂ FIXĂ:
1. "Indicele BET a închis la [VALOARE] puncte ([±X.XX]%)."
2. Ceilalți indici cu cifrele lor
3. Acțiuni câștigătoare (simbol, %, preț)
4. Acțiuni perdante (simbol, %, preț)
5. Volum/lichiditate
6. O frază neutră de încheiere (fără predicții)

LUNGIME: 100-130 cuvinte. TON: factual, profesionist, fără emoție."""

            chat = LlmChat(
                api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_UNIVERSAL_KEY"),
                session_id=f"daily_summary_{market_data['date']}",
                system_message=system_prompt
            ).with_model("openai", "gpt-4o-mini")
            
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
        """
        Trimite rezumatul zilnic către un user.
        Folosește rezumatul salvat în DB (nu regenerează AI pentru fiecare email!)
        """
        try:
            # Obține rezumatul salvat din DB
            saved_summary = await self.get_saved_summary()
            
            if not saved_summary:
                logger.error("No saved summary found for today - run generate_and_save_daily_summary first")
                return False
            
            market_data = saved_summary.get("market_data", {})
            ai_summary = saved_summary.get("ai_summary", "")
            
            # Adaugă câmpuri necesare pentru email
            market_data["date"] = saved_summary.get("date_display", self._get_romanian_date())
            market_data["total_stocks"] = market_data.get("sentiment", {}).get("positive", 0) + \
                                          market_data.get("sentiment", {}).get("negative", 0) + \
                                          market_data.get("sentiment", {}).get("neutral", 0)
            
            # Obține watchlist-ul userului (personalizat per user)
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
            
            email = await asyncio.to_thread(resend.Emails.send, params)
            logger.info(f"Daily summary sent to {user_email}: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending daily summary to {user_email}: {e}")
            return False
    
    async def send_to_all_subscribers(self) -> Dict:
        """Trimite rezumatul zilnic la toți userii abonați (plan Resend $20 = 10k/lună)"""
        db = await get_database()
        date_key = self._get_today_date_key()

        # Check if emails were already sent today (prevent duplicates on redeploy)
        lock = await db.email_send_locks.find_one({"date_key": date_key})
        if lock and lock.get("emails_sent"):
            logger.info(f"Emails already sent for {date_key}, skipping")
            return {"sent": 0, "failed": 0, "skipped": 0, "already_sent": True}

        # Mark as sending (lock)
        await db.email_send_locks.update_one(
            {"date_key": date_key},
            {"$set": {"date_key": date_key, "emails_sent": True, "sent_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )

        results = {"sent": 0, "failed": 0, "skipped": 0, "limit_reached": False}
        DAILY_LIMIT = 500  # Plan $20 Resend = 10k/lună, ~330/zi - lăsăm buffer pentru alerte

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
