"""
AI Fiscal Advisor - Specializat pe fiscalitate bursieră România
Răspunde la întrebări despre impozite, declarații, CASS, etc.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import os
import logging
from config.database import get_database
from routes.auth import require_auth
from utils.llm import LlmChat, UserMessage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-fiscal", tags=["ai-fiscal"])

# Context fiscal pentru AI
FISCAL_CONTEXT = """
# LEGISLAȚIE FISCALĂ ROMÂNĂ PENTRU INVESTIȚII LA BURSĂ (2026)
# Actualizat conform Codului Fiscal 2026 și Legea 141/2025

## 1. IMPOZIT PE CÂȘTIGURI DE CAPITAL

### BVB (Bursa de Valori București):
- Deținere ≥ 365 zile: **3%** impozit (crescut de la 1% în 2025)
- Deținere < 365 zile: **6%** impozit (crescut de la 3% în 2025)
- Impozitul este reținut la sursă de broker, per tranzacție
- NU trebuie completată Declarația Unică pentru câștiguri BVB (broker-ul plătește)
- Pierderile NU se compensează cu câștigurile la nivel de investitor

### Piețe Internaționale (SUA, UE, etc.):
- Impozit: **16%** pe câștigul NET anual (crescut de la 10% în 2025)
- TREBUIE completată Declarația Unică (formularul 212)
- Termen: 25 mai anul următor
- Pierderile se pot compensa cu câștigurile (max 70% din câștiguri)
- Pierderile necompensate se pot reporta 7 ani

## 2. IMPOZIT PE DIVIDENDE

### Dividende BVB:
- Impozit: **16%** reținut la sursă (crescut de la 10% în 2025, conform Legea 141/2025)
- Compania plătește direct, nu trebuie să faci nimic

### Dividende Internaționale:
- SUA: **15%** reținut la sursă (cu W-8BEN) sau 30% (fără W-8BEN)
- În România se datorează **16%**, dar se acordă credit fiscal pentru impozitul plătit în străinătate
- Dacă s-a reținut 15% în SUA, mai datorezi doar 1% în RO (16% - 15% = 1%)
- UE: Variază 10-25% în funcție de țară, se aplică credit fiscal

## 3. CASS (Contribuția de Asigurări Sociale de Sănătate)

- Rată: **10%**
- Se datorează dacă venitul total din investiții > 6 salarii minime brute
- Prag 2026: **24.300 RON/an** (6 × 4.050 RON salariu minim Ian-Iun 2026)
- IMPORTANT: CASS se datorează INCLUSIV de cei cu salariu, dacă au venituri din investiții peste prag
- Baze de calcul plafonate:
  * Venit 24.300 - 48.600 RON → CASS = 2.430 RON (10% × 24.300)
  * Venit 48.600 - 97.200 RON → CASS = 4.860 RON (10% × 48.600)
  * Venit > 97.200 RON → CASS = 9.720 RON (10% × 97.200, plafonat)
- Termen plată: odată cu Declarația Unică

## 4. DECLARAȚIA UNICĂ (Formularul 212)

### Când trebuie depusă:
- Pentru câștiguri din piețe internaționale
- Pentru CASS (dacă e cazul)
- NU pentru câștiguri BVB (broker-ul reține)

### Termen: 25 mai anul următor
### Unde: Online pe SPV (Spațiul Privat Virtual) al ANAF

## 5. W-8BEN (Pentru investiții SUA)

- Formular fiscal american pentru nerezidenți
- Reduce impozitul pe dividende SUA de la 30% la 15%
- Se completează la broker (Interactive Brokers, Trading 212, etc.)
- Valabil 3 ani, apoi trebuie reînnoit
- OBLIGATORIU pentru a beneficia de tratatul de evitare a dublei impuneri RO-SUA

## 6. PFA/SRL PENTRU INVESTIȚII

### PFA:
- NU este recomandat pentru investiții pasive
- Impozit 10% + CAS 25% + CASS 10% = ~45%
- Are sens doar pentru trading activ ca activitate principală

### SRL Micro (2026):
- 1% impozit pe venit (plafon 100.000 EUR cifră de afaceri)
- + 16% impozit dividende la retragere (crescut de la 8%)
- Total: ~17% + costuri administrative (~8.000 RON/an)
- NU are sens vs PF pe BVB (3-6%)

## 7. SFATURI PRACTICE

1. Pentru BVB: Rămâi ca PF, e cel mai avantajos (3-6% vs 45% PFA)
2. Pentru internațional: Completează W-8BEN la broker
3. Păstrează toate rapoartele de la broker
4. Consultă un contabil CECCAR pentru sume mari (>100.000 RON)
5. Folosește SPV ANAF pentru declarații
"""

SYSTEM_PROMPT = f"""Ești un consultant fiscal virtual specializat pe investiții la bursă în România.

CONTEXT LEGISLATIV:
{FISCAL_CONTEXT}

REGULI STRICTE:
1. Răspunzi DOAR la întrebări despre fiscalitate bursieră în România
2. Pentru întrebări în afara domeniului, spune politicos că nu poți ajuta
3. NU oferi sfaturi specifice de tip "fă exact asta" - direcționează către contabil pentru cazuri complexe
4. Menționează ÎNTOTDEAUNA că legislația se poate schimba și că trebuie verificată
5. Răspunde în limba română, clar și concis
6. Folosește exemple concrete cu numere când e posibil
7. Pentru sume mari (>100.000 RON), recomandă consultarea unui contabil CECCAR

STIL:
- Profesionist dar accesibil
- Folosește bullet points și structură clară
- Include disclaimer-ul legal când e relevant
- Oferă link-uri către resurse oficiale (ANAF, etc.) când e cazul

ÎNTREBĂRI FRECVENTE PE CARE LE POȚI ABORDA:
- Cum completez Declarația Unică?
- Ce e W-8BEN și cum îl completez?
- Cum calculez CASS pentru investiții?
- Diferența între impozitare BVB vs internațional
- Compensarea pierderilor
- Când trebuie să declar câștigurile?
- PF vs PFA vs SRL pentru investiții
"""


class FiscalQuestion(BaseModel):
    question: str
    context: Optional[str] = None  # Ex: "Am câștigat 50k pe BVB și 20k pe Trading 212"
    session_id: Optional[str] = None


@router.post("/ask")
async def ask_fiscal_question(
    data: FiscalQuestion,
    user: dict = Depends(require_auth)
):
    """
    Întreabă AI-ul despre fiscalitate bursieră.
    DOAR pentru utilizatori PRO!
    """
    db = await get_database()
    
    # Verifică dacă utilizatorul are PRO
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    subscription_level = user_data.get("subscription_level", "free") if user_data else "free"
    
    # AI Fiscal este DOAR pentru PRO
    if subscription_level != "pro":
        return {
            "success": False,
            "error": "pro_required",
            "message": "AI Fiscal Advisor este disponibil doar pentru utilizatorii PRO.",
            "upgrade_message": "Activează PRO pentru acces complet la Calculator Fiscal și AI Advisor!",
            "pricing": {
                "monthly": "49 RON/lună",
                "yearly": "490 RON/an (economisești 2 luni)"
            }
        }
    
    # Construiește mesajul
    full_question = data.question
    if data.context:
        full_question = f"Context: {data.context}\n\nÎntrebare: {data.question}"
    
    try:
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_UNIVERSAL_KEY") or os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        session_id = data.session_id or f"fiscal_{user['user_id']}_{datetime.now().strftime('%Y%m%d')}"
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=SYSTEM_PROMPT
        ).with_model("openai", "gpt-4o-mini")
        
        response = await chat.send_message(UserMessage(text=full_question))
        
        # Increment counter pentru FREE users
        if subscription_level == "free":
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {
                    "$inc": {"fiscal_queries_today": 1},
                    "$setOnInsert": {"fiscal_queries_reset_at": datetime.now(timezone.utc).isoformat()}
                },
                upsert=True
            )
        
        # Log pentru analytics
        await db.fiscal_ai_logs.insert_one({
            "user_id": user["user_id"],
            "question": data.question[:500],
            "response_length": len(response),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Get updated count
        updated_user = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
        queries_used = updated_user.get("fiscal_queries_today", 0) if updated_user else 0
        
        return {
            "success": True,
            "response": response,
            "session_id": session_id,
            "queries_info": {
                "used": queries_used,
                "limit": 5 if subscription_level == "free" else -1,
                "remaining": 5 - queries_used if subscription_level == "free" else -1,
                "is_unlimited": subscription_level == "pro"
            },
            "disclaimer": "⚠️ Informațiile sunt orientative. Consultă un contabil pentru situația ta specifică."
        }
        
    except Exception as e:
        logger.error(f"Fiscal AI error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/faq")
async def get_fiscal_faq():
    """Întrebări frecvente despre fiscalitate bursieră"""
    return {
        "categories": [
            {
                "name": "Declarația Unică",
                "questions": [
                    "Când trebuie să depun Declarația Unică?",
                    "Cum completez Declarația Unică pentru investiții?",
                    "Ce documente am nevoie pentru declarație?"
                ]
            },
            {
                "name": "Impozite BVB",
                "questions": [
                    "Cât e impozitul pe câștig pe BVB?",
                    "Trebuie să declar câștigurile de pe BVB?",
                    "Cum se calculează impozitul pe dividende?"
                ]
            },
            {
                "name": "Piețe Internaționale",
                "questions": [
                    "Ce e W-8BEN și de ce am nevoie?",
                    "Cum declar câștigurile din SUA?",
                    "Ce se întâmplă cu impozitul pe dividende americane?"
                ]
            },
            {
                "name": "CASS",
                "questions": [
                    "Când datorez CASS pentru investiții?",
                    "Cât e CASS dacă nu am salariu?",
                    "Cum se calculează baza de CASS?"
                ]
            },
            {
                "name": "PF vs PFA vs SRL",
                "questions": [
                    "Merită să fac PFA pentru investiții?",
                    "E mai avantajos SRL pentru bursă?",
                    "Care e cea mai bună structură fiscală?"
                ]
            }
        ],
        "popular_questions": [
            "Cât plătesc impozit dacă am câștigat 50.000 RON pe BVB?",
            "Trebuie să declar investițiile de pe Trading 212?",
            "Am salariu, mai datorez CASS pentru investiții?",
            "Cum completez W-8BEN la Interactive Brokers?",
            "Pot compensa pierderile cu câștigurile?"
        ]
    }


@router.get("/quick-answers")
async def get_quick_answers():
    """Răspunsuri rapide la cele mai comune întrebări"""
    return {
        "answers": [
            {
                "question": "Cât e impozitul pe BVB?",
                "answer": "3% pentru deținere ≥1 an, 6% pentru <1 an (2026). Reținut automat de broker."
            },
            {
                "question": "Cât e impozitul pe dividende?",
                "answer": "16% pentru dividende românești (reținut la sursă, 2026). Pentru SUA: 15% cu W-8BEN."
            },
            {
                "question": "Trebuie să fac Declarația Unică?",
                "answer": "DA pentru piețe internaționale și CASS. NU pentru câștiguri BVB (broker-ul plătește)."
            },
            {
                "question": "Ce e W-8BEN?",
                "answer": "Formular fiscal SUA care reduce impozitul pe dividende de la 30% la 15%. Se completează la broker."
            },
            {
                "question": "Când datorez CASS?",
                "answer": "Dacă venitul din investiții > 24.300 RON/an (6 salarii minime 2026). Se aplică inclusiv celor cu salariu."
            },
            {
                "question": "PFA sau PF pentru investiții?",
                "answer": "PF aproape întotdeauna! Pe BVB plătești 3-6% vs ~45% ca PFA."
            }
        ]
    }
