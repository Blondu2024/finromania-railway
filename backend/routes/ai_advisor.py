"""AI Advisor routes pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import logging
from config.database import get_database
from routes.auth import require_auth, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advisor", tags=["ai-advisor"])

# AI Monthly Limit
AI_MONTHLY_LIMIT = 10

# Try to import emergent integrations for AI
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    HAS_AI = True
except ImportError:
    HAS_AI = False
    logger.warning("AI integration not available")

class AdviceRequest(BaseModel):
    symbol: Optional[str] = None
    stock_type: Optional[str] = None  # 'bvb' or 'global'
    question: Optional[str] = None

class AssistantRequest(BaseModel):
    message: str


# ============================================
# FINROMANIA ASSISTANT - Platform Guide Bot
# ============================================

FINROMANIA_KNOWLEDGE = """
Tu ești **FinRomania Assistant** - asistentul virtual al platformei FinRomania.ro, cea mai completă platformă de investiții pentru piața românească.

## CUNOȘTINȚELE TALE DESPRE PLATFORMĂ:

### 📊 PAGINI PRINCIPALE:
1. **Homepage** (/) - Știri România + Internațional, ticker cu prețuri live, Early Adopter banner
2. **Acțiuni BVB** (/stocks) - Toate acțiunile de pe Bursa de Valori București cu prețuri live
3. **Piețe Globale** (/global) - Indici mondiali, crypto, mărfuri, forex
4. **Știri** (/news) - Tab România (ZF, Profit.ro) + Tab Internațional (CNBC, Reuters, Yahoo Finance)
5. **Screener** (/screener) - Filtrare acțiuni după criterii + Screener PRO cu P/E, ROE, EPS
6. **Calendar Dividende** (/calendar) - Calendar cu dividende BVB, export XLS (PRO)
7. **Trading School** (/trading-school) - 25 lecții educative cu quiz-uri
8. **Calculator Fiscal** (/calculator) - Comparație PF vs SRL pentru impozite (PRO)
9. **AI Advisor** (/ai-advisor) - Consilier AI pentru întrebări despre investiții
10. **Portofoliu** (/portfolio) - Gestionare portofoliu personal
11. **Watchlist** (/watchlist) - Urmărire acțiuni favorite cu alerte de preț

### ⭐ FUNCȚII WATCHLIST (pentru alerte de preț):
- Accesează **Watchlist** din meniu (pictograma ⭐)
- Apasă **+ Adaugă** pentru a adăuga o acțiune
- Pentru fiecare acțiune poți seta **alertă de preț** (când prețul ajunge la valoarea dorită)
- Vei primi **notificare** când prețul atinge nivelul setat

### 🔍 SCREENER (găsire acțiuni):
**Screener Basic (gratuit):**
- Filtrare după preț, variație %, volum
- Screener-e rapide: Top Creșteri, Top Scăderi, Blue Chips, Volume Mari

**Screener PRO (abonament):**
- Indicatori fundamentali: P/E, P/B, ROE, EPS, Dividend Yield
- Filtrare avansată după toți indicatorii
- Export rezultate

### 📅 CALENDAR DIVIDENDE:
- Vezi toate dividendele plătite și viitoare de companiile BVB
- **Export XLS** (PRO) - descarcă calendarul în Excel
- Tab Evenimente - AGA-uri și rapoarte financiare

### 🎓 TRADING SCHOOL:
- 25 de lecții gratuite pentru începători
- Quiz la finalul fiecărei lecții
- Certificat de absolvire după toate lecțiile
- Subiecte: Ce e o acțiune, Analiza tehnică, Dividende, ETF-uri, etc.

### 💰 ABONAMENT PRO (49 lei/lună):
**Include:**
- Screener PRO cu indicatori fundamentali
- Export Calendar XLS
- Calculator Fiscal PF vs SRL
- AI Advisor nelimitat (vs 10 întrebări/lună gratuit)
- Fără reclame

**Early Adopter:** Primii 100 utilizatori primesc PRO GRATUIT 3 luni!

### 🔔 NOTIFICĂRI:
- **Alerte preț** - din Watchlist când o acțiune atinge prețul setat
- **Expirare abonament** - 7 zile înainte de expirare PRO

### 📱 ACCES MOBIL:
- Platforma este **responsive** - funcționează pe telefon din browser
- Nu există aplicație separată, dar site-ul e optimizat pentru mobil

## REGULI DE RĂSPUNS:
1. Răspunzi DOAR în română
2. Ești prietenos și concis
3. Ghidezi utilizatorul pas cu pas când întreabă "cum fac să..."
4. Dacă funcția nu există, spui clar "Această funcție nu e disponibilă încă"
5. Pentru întrebări despre investiții specifice, redirecționează către AI Advisor (/ai-advisor)
6. Menționezi dacă o funcție e PRO sau gratuită
7. Maximum 150 cuvinte per răspuns
"""

import uuid

async def get_assistant_response(user_message: str) -> str:
    """Get AI Assistant response using platform knowledge"""
    if not HAS_AI:
        return "Asistentul FinRomania nu este disponibil momentan. Te rog încearcă mai târziu."
    
    api_key = os.environ.get("EMERGENT_UNIVERSAL_KEY")
    if not api_key:
        return "Configurare AI lipsă."
    
    try:
        session_id = f"assistant_{uuid.uuid4().hex[:8]}"
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=FINROMANIA_KNOWLEDGE
        )
        
        user_msg = UserMessage(text=user_message)
        response = await chat.send_message(user_msg)
        return response
    except Exception as e:
        logger.error(f"Assistant AI error: {e}")
        return "Nu am putut procesa întrebarea. Te rog încearcă din nou."


@router.post("/assistant")
async def ask_assistant(request: AssistantRequest, user: dict = Depends(get_current_user)):
    """
    FinRomania Assistant - The platform guide bot
    Helps users discover features and navigate the platform
    Free for all users (doesn't count against AI limit)
    """
    if not request.message or len(request.message.strip()) < 2:
        raise HTTPException(status_code=400, detail="Te rog scrie o întrebare.")
    
    # Get response from AI
    answer = await get_assistant_response(request.message)
    
    # Log the interaction (for improving the bot)
    db = await get_database()
    await db.assistant_logs.insert_one({
        "user_id": user.get("user_id") if user else "anonymous",
        "message": request.message[:500],
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "message": request.message,
        "response": answer,
        "bot_name": "FinRomania Assistant"
    }


@router.get("/assistant/suggestions")
async def get_assistant_suggestions():
    """Get suggested questions for the assistant"""
    return {
        "suggestions": [
            "Cum setez o alertă de preț pentru o acțiune?",
            "Unde găsesc acțiunile cu cele mai mari dividende?",
            "Ce este Screener PRO și ce include?",
            "Cum devin utilizator PRO?",
            "Unde văd știrile internaționale?",
            "Cum export calendarul de dividende în Excel?",
            "Ce lecții are Trading School?",
            "Cum compar impozitele PF vs SRL?",
        ]
    }


async def check_ai_limit(user: dict) -> tuple[bool, int, int]:
    """Check if user has reached AI limit. Returns (can_use, used, remaining)"""
    db = await get_database()
    user_data = await db.users.find_one({"user_id": user["user_id"]})
    
    if not user_data:
        return True, 0, AI_MONTHLY_LIMIT
    
    # Check for custom limit
    limit = user_data.get("custom_ai_limit", AI_MONTHLY_LIMIT)
    used = user_data.get("ai_credits_used", 0)
    remaining = max(0, limit - used)
    
    # Admin bypass
    if user_data.get("is_admin"):
        return True, used, 999
    
    return remaining > 0, used, remaining

async def increment_ai_usage(user: dict, feature: str):
    """Increment AI usage for user"""
    db = await get_database()
    
    await db.ai_usage_logs.insert_one({
        "user_id": user["user_id"],
        "email": user.get("email"),
        "feature": feature,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "credits_used": 1
    })
    
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$inc": {"ai_credits_used": 1}}
    )

@router.get("/credits")
async def get_ai_credits(user: dict = Depends(require_auth)):
    """Get user's AI credits info"""
    can_use, used, remaining = await check_ai_limit(user)
    
    return {
        "credits_used": used,
        "credits_remaining": remaining,
        "monthly_limit": AI_MONTHLY_LIMIT,
        "can_use_ai": can_use,
        "resets_on": "1st of next month"
    }

async def get_ai_response(prompt: str, system_prompt: str = None) -> str:
    """Get AI response using Emergent Universal Key"""
    if not HAS_AI:
        return "Serviciul AI nu este disponibil momentan."
    
    api_key = os.environ.get("EMERGENT_UNIVERSAL_KEY")
    if not api_key:
        return "Configurare AI lipsă."
    
    try:
        session_id = f"advisor_{uuid.uuid4().hex[:8]}"
        system_msg = system_prompt or "Ești un consilier financiar expert pentru investitori români. Răspunzi în română, ești prietenos și educativ."
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_msg
        )
        
        user_msg = UserMessage(text=prompt)
        response = await chat.send_message(user_msg)  # Use await since it's async
        return response
    except Exception as e:
        logger.error(f"AI error: {e}")
        return f"Nu am putut genera răspunsul. Eroare: {str(e)[:100]}"

@router.get("/portfolio-advice")
async def get_portfolio_advice(user: dict = Depends(require_auth)):
    """Get AI-powered portfolio advice based on user's risk profile"""
    
    # Check AI limit
    can_use, used, remaining = await check_ai_limit(user)
    if not can_use:
        raise HTTPException(
            status_code=429, 
            detail=f"Ai atins limita lunară de {AI_MONTHLY_LIMIT} credite AI. Limita se resetează luna viitoare."
        )
    
    db = await get_database()
    
    # Get user's risk profile
    assessment = await db.risk_assessments.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    
    if not assessment:
        return {
            "advice": "Înainte de a primi sfaturi personalizate, te rugăm să completezi chestionarul de evaluare a riscului.",
            "needs_assessment": True
        }
    
    profile_key = assessment["profile_key"]
    
    # Get user's holdings
    holdings = await db.portfolio_holdings.find(
        {"user_id": user["user_id"], "quantity": {"$gt": 0}},
        {"_id": 0}
    ).to_list(50)
    
    holdings_text = ""
    if holdings:
        holdings_text = "\nPortofoliul actual:\n"
        for h in holdings:
            holdings_text += f"- {h['symbol']} ({h['type']}): {h['quantity']} acțiuni, preț mediu {h.get('avg_price', 0):.2f}\n"
    else:
        holdings_text = "\nPortofoliul este gol - nu ai nicio deținere."
    
    system_prompt = """Ești un consilier financiar expert pentru investitori români. 
Răspunzi în română, ești prietenos și educativ.
Nu oferi sfaturi de investiție specifice, ci principii generale de educație financiară.
Menționezi mereu că utilizatorul ar trebui să consulte un specialist înainte de decizii importante."""
    
    prompt = f"""Utilizatorul are profilul de risc: {profile_key.upper()}
Scor evaluare: {assessment['total_score']}/{assessment['max_score']}
{holdings_text}

Oferă sfaturi generale despre:
1. Dacă alocarea actuală se potrivește profilului de risc
2. Sugestii de diversificare
3. Ce să aibă în vedere pentru obiectivele pe termen lung

Fii concis (max 200 cuvinte) și prietenos."""
    
    advice = await get_ai_response(prompt, system_prompt)
    
    # Track AI usage
    await increment_ai_usage(user, "portfolio_advice")
    
    # Get updated credits
    _, used_now, remaining_now = await check_ai_limit(user)
    
    return {
        "advice": advice,
        "profile": profile_key,
        "holdings_count": len(holdings),
        "needs_assessment": False,
        "credits_remaining": remaining_now
    }

@router.get("/stock-analysis/{symbol}")
async def get_stock_analysis(
    symbol: str,
    stock_type: str = Query(default="global", enum=["bvb", "global"])
):
    """Get AI analysis for a specific stock"""
    db = await get_database()
    
    # Get stock data
    if stock_type == "bvb":
        stock = await db.stocks_bvb.find_one({"symbol": symbol.upper()}, {"_id": 0})
    else:
        stock = await db.stocks_global.find_one({"symbol": symbol.upper()}, {"_id": 0})
    
    if not stock:
        raise HTTPException(status_code=404, detail="Acțiunea nu a fost găsită")
    
    system_prompt = """Ești un analist financiar educațional pentru România.
Oferești analize educative despre acțiuni, nu sfaturi de cumpărare/vânzare.
Răspunzi în română, concis și clar.
Menționezi că datele pot fi întârziate și utilizatorul trebuie să facă propria cercetare."""
    
    is_mock = stock.get("is_mock", False)
    mock_notice = "(ATENȚIE: Acestea sunt date simulate pentru demonstrație)" if is_mock else ""
    
    prompt = f"""Analizează această acțiune {mock_notice}:

Simbol: {stock.get('symbol')}
Nume: {stock.get('name')}
Preț curent: {stock.get('price', 0):.2f}
Variație: {stock.get('change_percent', 0):.2f}%
Tip: {'BVB (România)' if stock_type == 'bvb' else 'Internațional'}

Oferă o analiză educativă scurtă (max 150 cuvinte) care include:
1. Ce face compania (dacă știi)
2. Contextul pieței
3. Factori de urmărit

NU recomanda cumpărare sau vânzare."""
    
    analysis = await get_ai_response(prompt, system_prompt)
    
    return {
        "symbol": symbol.upper(),
        "name": stock.get("name"),
        "analysis": analysis,
        "is_mock": is_mock,
        "disclaimer": "Această analiză este doar în scop educativ și nu constituie sfat de investiții."
    }

@router.post("/ask")
async def ask_advisor(request: AdviceRequest, user: dict = Depends(require_auth)):
    """Ask the AI advisor a custom question"""
    if not request.question:
        raise HTTPException(status_code=400, detail="Întrebarea este obligatorie")
    
    # Check AI limit
    can_use, used, remaining = await check_ai_limit(user)
    if not can_use:
        raise HTTPException(
            status_code=429, 
            detail=f"Ai atins limita lunară de {AI_MONTHLY_LIMIT} credite AI. Limita se resetează luna viitoare."
        )
    
    system_prompt = """Ești un consilier financiar educațional pentru investitori români începători.
Răspunzi doar la întrebări legate de investiții, finanțe personale și piețe de capital.
Răspunzi în română, ești prietenos și simplu de înțeles.
Nu oferi sfaturi de investiție specifice (ce să cumpere/vândă).
Dacă întrebarea nu e legată de finanțe, spui politicos că poți ajuta doar cu întrebări financiare.
Maxim 200 cuvinte per răspuns."""
    
    answer = await get_ai_response(request.question, system_prompt)
    
    # Log and increment usage
    db = await get_database()
    await db.advisor_questions.insert_one({
        "user_id": user["user_id"],
        "question": request.question[:500],
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    await increment_ai_usage(user, "ask_advisor")
    
    # Get updated credits
    _, used_now, remaining_now = await check_ai_limit(user)
    
    return {
        "question": request.question,
        "answer": answer,
        "disclaimer": "Răspunsurile sunt doar în scop educativ.",
        "credits_remaining": remaining_now
    }

@router.get("/tip-of-the-day")
async def get_tip_of_the_day():
    """Get a daily investment tip"""
    import random
    
    tips = [
        {
            "tip": "Regula 72: Împarte 72 la rata de randament pentru a afla în câți ani se dublează investiția. Ex: 72/8% = 9 ani.",
            "category": "Matematică financiară"
        },
        {
            "tip": "Nu încerca să 'prinzi' minimul sau maximul pieței. Chiar și profesioniștii eșuează la timing. DCA este prietenul tău.",
            "category": "Strategie"
        },
        {
            "tip": "Diversificarea este singurul 'free lunch' în investiții. Nu pune toate ouăle într-un singur coș.",
            "category": "Risc"
        },
        {
            "tip": "Costurile contează! Un ETF cu comision de 0.1% vs 1% poate însemna zeci de mii de RON diferență pe 30 ani.",
            "category": "Costuri"
        },
        {
            "tip": "Investește doar bani pe care îți permiți să îi pierzi și pe care nu îi vei avea nevoie în următorii 5+ ani.",
            "category": "Principii"
        },
        {
            "tip": "Emoțiile sunt dușmanul investitorului. Când alții sunt fricoși, fii lacom. Când alții sunt lacomi, fii precaut.",
            "category": "Psihologie"
        },
        {
            "tip": "Verifică-ți portofoliul o dată pe lună, nu zilnic. Verificarea obsesivă duce la decizii emoționale.",
            "category": "Comportament"
        },
        {
            "tip": "Înainte de orice investiție, asigură-te că ai un fond de urgență de 3-6 luni de cheltuieli.",
            "category": "Bază financiară"
        },
        {
            "tip": "Citește raportul anual al companiei înainte de a investi. Dacă nu înțelegi ce face, probabil nu ar trebui să investești.",
            "category": "Cercetare"
        },
        {
            "tip": "Rebalansează-ți portofoliul o dată pe an pentru a menține alocarea țintă și a reduce riscul.",
            "category": "Management portofoliu"
        }
    ]
    
    # Use date as seed for consistent daily tip
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    random.seed(hash(today))
    tip = random.choice(tips)
    
    return {
        "tip": tip["tip"],
        "category": tip["category"],
        "date": today
    }
