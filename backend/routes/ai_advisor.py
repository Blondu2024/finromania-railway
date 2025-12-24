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

# Try to import emergent integrations for AI
try:
    from emergentintegrations.llm.chat import LlmChat
    HAS_AI = True
except ImportError:
    HAS_AI = False
    logger.warning("AI integration not available")

class AdviceRequest(BaseModel):
    symbol: Optional[str] = None
    stock_type: Optional[str] = None  # 'bvb' or 'global'
    question: Optional[str] = None

import uuid

async def get_ai_response(prompt: str, system_prompt: str = None) -> str:
    """Get AI response using Emergent Universal Key"""
    if not HAS_AI:
        return "Serviciul AI nu este disponibil momentan."
    
    api_key = os.environ.get("EMERGENT_UNIVERSAL_KEY")
    if not api_key:
        return "Configurare AI lipsă."
    
    try:
        # Generate unique session ID for each request
        session_id = f"advisor_{uuid.uuid4().hex[:8]}"
        
        # Use system prompt for context
        system_msg = system_prompt or "Ești un consilier financiar expert pentru investitori români. Răspunzi în română, ești prietenos și educativ."
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_msg
        )
        
        response = await chat.send_message_async(prompt)
        return response.message
    except Exception as e:
        logger.error(f"AI error: {e}")
        return f"Nu am putut genera răspunsul. Eroare: {str(e)[:100]}"

@router.get("/portfolio-advice")
async def get_portfolio_advice(user: dict = Depends(require_auth)):
    """Get AI-powered portfolio advice based on user's risk profile"""
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
    
    return {
        "advice": advice,
        "profile": profile_key,
        "holdings_count": len(holdings),
        "needs_assessment": False
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
    
    system_prompt = """Ești un consilier financiar educațional pentru investitori români începători.
Răspunzi doar la întrebări legate de investiții, finanțe personale și piețe de capital.
Răspunzi în română, ești prietenos și simplu de înțeles.
Nu oferi sfaturi de investiție specifice (ce să cumpere/vândă).
Dacă întrebarea nu e legată de finanțe, spui politicos că poți ajuta doar cu întrebări financiare.
Maxim 200 cuvinte per răspuns."""
    
    answer = await get_ai_response(request.question, system_prompt)
    
    # Log question for analytics
    db = await get_database()
    await db.advisor_questions.insert_one({
        "user_id": user["user_id"],
        "question": request.question[:500],  # Limit stored question
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {
        "question": request.question,
        "answer": answer,
        "disclaimer": "Răspunsurile sunt doar în scop educativ."
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
