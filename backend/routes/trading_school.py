"""Trading School Interactive - Educational Content & System"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timezone
from config.database import get_database
from routes.auth import require_auth

router = APIRouter(prefix="/trading-school", tags=["trading_school"])

# ============================================
# EDUCATIONAL CONTENT
# ============================================

TRADING_LESSONS = [
    {
        "id": "lesson_1",
        "module": 1,
        "order": 1,
        "title": "Ce Este o Acțiune?",
        "subtitle": "Fundamentele investițiilor",
        "duration": "5 min",
        "difficulty": "beginner",
        "emoji": "📈",
        "content": """
# Ce Este o Acțiune?

## 💡 Definiție Simplă

O **acțiune** este o bucată dintr-o companie. Când cumperi o acțiune, devii **proprietar parțial** al companiei!

## 🏦 Exemplu Concret: Banca Transilvania (TLV)

Imaginează-ți că Banca Transilvania este o pizza 🍕:
- Pizza întreagă = Întreaga companie
- O felie = O acțiune
- Tu cumperi 10 felii = Deții 10 acțiuni

**Dacă pizzeria valorează mai mult (compania crește) → feliile tale valorează mai mult!**

## 💰 Calculul Simplu

**Exemplu:**
- 1 acțiune TLV = 30 RON
- Cumperi 10 acțiuni = 300 RON investiți

**După 1 lună:**
- TLV crește la 33 RON (+10%)
- Ai acum: 10 × 33 = **330 RON**
- **Profit: +30 RON (+10%)**

## ✅ De Reținut

1. Acțiune = proprietate într-o companie
2. Preț crește → Tu câștigi
3. Preț scade → Tu pierzi
4. Poți vinde oricând (dacă e lichiditate)
""",
        "quiz": [
            {
                "question": "Dacă ai 10 acțiuni TLV la 30 RON și prețul crește la 33 RON, cât valorează investiția ta?",
                "options": ["300 RON (la fel)", "330 RON (crește!)", "270 RON (scade)", "360 RON"],
                "correct": 1,
                "explanation": "Corect! 10 acțiuni × 33 RON = 330 RON. Ai făcut +30 RON profit (+10%)!"
            },
            {
                "question": "Ce înseamnă să deții o acțiune?",
                "options": [
                    "Împrumuți bani companiei",
                    "Ești proprietar parțial al companiei",
                    "Ești angajat al companiei",
                    "Primești un discount la produse"
                ],
                "correct": 1,
                "explanation": "Exact! Când deții acțiuni, ești co-proprietar al companiei. Dacă compania merge bine, acțiunile cresc!"
            }
        ],
        "scenario": {
            "title": "Primul Tău Cumpărare",
            "description": "Hai să cumpărăm prima acțiune împreună!",
            "steps": [
                {
                    "step": 1,
                    "text": "Ai 1,000 RON în cont. Vrei să investești în Banca Transilvania (TLV).",
                    "question": "Câte acțiuni poți cumpăra dacă TLV costă 30 RON?",
                    "options": ["10 acțiuni", "30 acțiuni", "33 acțiuni", "100 acțiuni"],
                    "correct": 2,
                    "ai_hint": "Calculează: Bani disponibili ÷ Preț per acțiune = 1,000 ÷ 30 = ?"
                },
                {
                    "step": 2,
                    "text": "Bravo! Ai cumpărat 33 acțiuni TLV la 30 RON. Investiție: 990 RON.",
                    "question": "După 1 lună, TLV e la 33 RON. Vrei să vinzi?",
                    "options": ["DA - iau profit", "NU - aștept mai mult"],
                    "correct": null,
                    "ai_feedback": {
                        "0": "Bună decizie! Ai vândut la 33 RON × 33 = 1,089 RON. Profit: +99 RON (+10%)!",
                        "1": "Riști mai mult, dar poate crește și mai mult! Sau poate scade..."
                    }
                }
            ]
        }
    },
    {
        "id": "lesson_2",
        "module": 1,
        "order": 2,
        "title": "Long vs Short - Două Direcții",
        "subtitle": "Cum câștigi când piața scade?",
        "duration": "7 min",
        "difficulty": "beginner",
        "emoji": "↕️",
        "content": """
# Long vs Short

## 📈 LONG (Cumpărare Clasică)

**Cumperi acum, vinzi mai târziu LA PREȚ MAI MARE**

**Exemplu:**
- Cumperi TLV la 30 RON
- Vinzi la 35 RON
- **Profit: +5 RON per acțiune**

✅ Câștigi când prețul CREȘTE
❌ Pierzi când prețul SCADE

## 📉 SHORT (Vânzare în Lipsă)

**Vinzi acum (împrumutat), cumperi înapoi LA PREȚ MAI MIC**

**Exemplu:**
- "Împrumuți" și vinzi TLV la 30 RON
- Cumperi înapoi la 25 RON
- **Profit: +5 RON per acțiune**

✅ Câștigi când prețul SCADE
❌ Pierzi când prețul CREȘTE

## ⚠️ Risc SHORT

**LONG:** Pierdere maximă = Investiția ta (prețul ajunge la 0)
**SHORT:** Pierdere = INFINITĂ! (prețul poate crește la infinit)

**De aceea SHORT e pentru avansați!**

## 🎯 Când Folosești

**LONG:** Crezi că compania va merge bine
**SHORT:** Crezi că compania va merge prost (sau piața va scădea)
""",
        "quiz": [
            {
                "question": "Ai făcut SHORT pe TLV la 30 RON (100 acțiuni). Prețul crește la 35 RON. Cât ai pierdut?",
                "options": ["+500 RON (profit)", "-500 RON (pierdere)", "0 RON", "-100 RON"],
                "correct": 1,
                "explanation": "Corect, din păcate! SHORT înseamnă că câștigi când scade. Când crește, PIERZI! (35-30) × 100 = -500 RON"
            },
            {
                "question": "De ce SHORT e mai riscant decât LONG?",
                "options": [
                    "E ilegal",
                    "Pierderea poate fi infinită",
                    "Nu poți câștiga bani",
                    "E mai complicat"
                ],
                "correct": 1,
                "explanation": "Exact! La LONG, pierdere max = investiția (prețul ajunge la 0). La SHORT, prețul poate crește la infinit = pierdere infinită!"
            }
        ]
    },
    {
        "id": "lesson_3",
        "module": 2,
        "order": 3,
        "title": "Leverage - Sabie cu Două Tăișuri",
        "subtitle": "Cum să amplifici profitul... și pierderea",
        "duration": "10 min",
        "difficulty": "intermediate",
        "emoji": "⚡",
        "content": """
# Leverage (Efect de Levier)

## 💰 Ce Este?

**Leverage = Împrumuți bani de la broker pentru a controla mai mulți bani**

Exemplu simplu: E ca și cum ai cumpăra o casă cu credit!

## 🎯 Exemplu Fără Leverage (1x)

**Investești:**
- Ai: 1,000 RON
- Controlezi: 1,000 RON
- Cumperi Oil la 100 RON = 10 unități

**Oil crește la 110 RON (+10%):**
- Vinzi: 10 × 110 = 1,100 RON
- **Profit: +100 RON (+10%)**

## ⚡ Exemplu CU Leverage 5x

**Investești:**
- Ai: 1,000 RON (margin)
- Împrumuți: 4,000 RON de la broker
- Controlezi: 5,000 RON total!
- Cumperi Oil la 100 RON = 50 unități

**Oil crește la 110 RON (+10%):**
- Vinzi: 50 × 110 = 5,500 RON
- Returnezi împrumut: 4,000 RON
- Rămâi cu: 1,500 RON
- **Profit: +500 RON (+50%)** 🎉

## 🚨 DAR Dacă Scade?

**Oil scade la 90 RON (-10%):**
- Vinzi: 50 × 90 = 4,500 RON
- Returnezi împrumut: 4,000 RON
- Rămâi cu: 500 RON
- **Pierdere: -500 RON (-50%)** 😱

## ⚠️ Margin Call

**Dacă pierderile devin prea mari, brokerul ÎNCHIDE FORȚAT poziția!**

Exemplu: Oil scade la 80 RON (-20%)
- Valoare: 50 × 80 = 4,000 RON
- Trebuie să returnezi: 4,000 RON
- **Rămâi cu: 0 RON - Ai pierdut TOT!** 💀

## 📊 Regula de Aur

**Cu leverage 5x:**
- Dacă prețul scade 20% → PIERZI 100% (TOT!)
- **NU folosi leverage mare dacă nu știi ce faci!**

## 💡 Pentru Începători

- Leverage 1x = SAFE (fără împrumut)
- Leverage 2x = OK (cu Stop Loss!)
- Leverage 5x+ = PERICOL (doar pentru experți)
""",
        "quiz": [
            {
                "question": "Ai 1,000 RON, leverage 5x. Cumperi Oil la 100 RON. Oil scade la 80 RON (-20%). Cât ai pierdut?",
                "options": ["200 RON", "500 RON", "1,000 RON (TOT!)", "100 RON"],
                "correct": 2,
                "explanation": "CORECT! Cu 5x leverage, o scădere de 20% = pierdere de 100% din margin! Asta e MARGIN CALL - ai pierdut tot!"
            },
            {
                "question": "De ce leverage e 'sabie cu două tăișuri'?",
                "options": [
                    "E ilegal",
                    "Amplifică profitul ȘI pierderea",
                    "Costă mult",
                    "E complicat"
                ],
                "correct": 1,
                "explanation": "Exact! Leverage amplifică AMBELE direcții. +10% devine +50%, dar -10% devine -50%!"
            },
            {
                "question": "Ce leverage e sigur pentru începători?",
                "options": ["10x", "5x", "2x cu Stop Loss", "1x (fără leverage)"],
                "correct": 3,
                "explanation": "Bravo! 1x (fără leverage) e cel mai sigur pentru început. După ce înveți, poți încerca 2x cu Stop Loss."
            }
        ],
        "scenario": {
            "title": "Criza Leverage - Învață din Greșeli",
            "steps": [
                {
                    "step": 1,
                    "text": "Ai 5,000 RON. Ești încrezător și alegi leverage 10x pentru Oil.",
                    "ai": "⚠️ Atenție! Cu 10x leverage, controlezi 50,000 RON! O mișcare de doar -10% și pierzi TOT!",
                    "question": "Vrei să continui cu 10x sau schimbi la 2x?",
                    "options": ["10x - sunt sigur!", "2x - mai sigur"],
                    "correct": 1
                },
                {
                    "step": 2,
                    "text": "Ai ales 2x (smart!). Cumperi Oil la 75 RON.",
                    "ai": "Bună decizie! Cu 2x leverage și 5,000 RON margin, controlezi 10,000 RON.",
                    "question": "Setezi Stop Loss?",
                    "options": ["DA - la -5% (71.25 RON)", "NU - risc tot"],
                    "correct": 0
                },
                {
                    "step": 3,
                    "text": "Perfect! Ai setat SL la 71.25 RON. Oil scade la 70 RON (-6.7%).",
                    "ai": "🛡️ STOP LOSS ACTIVAT! Poziția închisă la 71.25 RON. Pierdere: -500 RON (-10%). DAR te-a salvat de pierderi mai mari!",
                    "question": "Ce s-ar fi întâmplat FĂRĂ Stop Loss?",
                    "calculation": "La 70 RON: Pierdere = (75-70) × 133 × 2 = -1,330 RON (-26.6%)"
                }
            ]
        }
    },
    {
        "id": "lesson_4",
        "module": 2,
        "order": 4,
        "title": "Stop Loss - Asigurarea Ta",
        "subtitle": "Cum să nu pierzi tot",
        "duration": "8 min",
        "difficulty": "beginner",
        "emoji": "🛡️",
        "content": """
# Stop Loss - Asigurarea Ta

## 💡 Ce Este?

**Stop Loss** = Ordin automat de vânzare când prețul scade la un nivel setat de tine.

**E ca o plasă de siguranță la circ!** 🎪

## 🎯 Cum Funcționează?

**Exemplu:**
1. Cumperi TLV la 30 RON (100 acțiuni = 3,000 RON)
2. Setezi **Stop Loss la 28.5 RON** (-5%)
3. Dacă TLV scade la 28.5 → VINDE AUTOMAT!

**Rezultat:** Pierdere maximă = -150 RON (-5%)

## 📊 Scenariul Fără SL

**Ce se întâmplă dacă NU setezi Stop Loss?**

**Ziua 1:** TLV = 29 RON (-3.3%) → "Mai aștept..."
**Ziua 2:** TLV = 27 RON (-10%) → "Sigur crește..."
**Ziua 3:** TLV = 24 RON (-20%) → "😱 Am pierdut 600 RON!"

**Cu Stop Loss:** Ai fi pierdut doar 150 RON și închideai la -5%!

## ⚡ Stop Loss + Leverage

**CRITIC:** Cu leverage, Stop Loss e OBLIGATORIU!

Exemplu leverage 5x:
- Investești: 1,000 RON
- Controlezi: 5,000 RON
- Fără SL: O scădere de -20% = PIERZI TOT!
- Cu SL la -5%: Pierdere max = -250 RON (controlabil)

## 💡 Unde Setezi SL?

**Reguli practice:**
- **Day trading:** -2% până -5%
- **Swing trading:** -5% până -10%
- **Long-term:** -10% până -15%

**Cu leverage:** ÎNTOTDEAUNA mai strict! (-3% max cu 5x leverage)
""",
        "quiz": [
            {
                "question": "Ai 3,000 RON investiți în TLV la 30 RON. Setezi SL la 28.5 RON (-5%). Prețul scade la 27 RON. Ce se întâmplă?",
                "options": [
                    "Pierzi tot (3,000 RON)",
                    "Poziția se închide la 28.5, pierzi ~150 RON",
                    "Nu se întâmplă nimic",
                    "Trebuie să vinzi manual"
                ],
                "correct": 1,
                "explanation": "Corect! SL se activează automat la 28.5 RON, limitând pierderea la -5% (~150 RON). Te salvează de scăderea la 27 RON!"
            },
            {
                "question": "Cu leverage 5x, unde e SIGUR să setezi Stop Loss?",
                "options": ["-20%", "-10%", "-3%", "Nu e nevoie"],
                "correct": 2,
                "explanation": "Corect! Cu 5x leverage, -20% în preț = -100% pierdere (TOT). SL la -3% te protejează: -3% × 5 = -15% pierdere (controlabil)."
            }
        ]
    },
    {
        "id": "lesson_5",
        "module": 2,
        "order": 5,
        "title": "Diversificarea - Nu Pune Toate Ouăle într-un Coș",
        "subtitle": "Cum să reduci riscul",
        "duration": "6 min",
        "difficulty": "intermediate",
        "emoji": "🎯",
        "content": """
# Diversificarea Portofoliului

## 🥚 Regula Ouălor

**"Nu pune toate ouăle într-un singur coș"**

Dacă scapi coșul → TOATE ouăle se sparg! 😱

În trading:
- 1 coș = 1 acțiune = RISC MARE
- 5-10 coșuri = 5-10 acțiuni = RISC REDUS

## 📊 Exemplu Practic

**Portofoliu PROST (nediversificat):**
- 10,000 RON → TOT în TLV
- TLV scade 20% → Pierzi 2,000 RON (-20%)

**Portofoliu BUN (diversificat):**
- 2,000 RON → TLV (bancă)
- 2,000 RON → H2O (energie)
- 2,000 RON → SNP (petrol)
- 2,000 RON → Gold (aur)
- 2,000 RON → S&P 500 (indice US)

**Dacă TLV scade 20%:**
- TLV: -400 RON
- Celelalte stabile sau cresc
- **Pierdere totală: -200 RON (-2%)** în loc de -20%!

## 🎯 Reguli de Diversificare

1. **Sectoare diferite:** Bancă + Energie + Tech
2. **Geografii diferite:** România + SUA + Europa
3. **Clase de active:** Acțiuni + Aur + Forex
4. **5-10 poziții** diferite (nu 1, nu 100)

## ⚠️ Greșeală Comună

**"Diversific în 10 acțiuni din același sector"**

Exemplu: 10 bănci românești → TOATE scad când sectorul bancar scade!

**Diversificare REALĂ:** Bancă + Energie + Tech + Aur + Forex
""",
        "quiz": [
            {
                "question": "Ai 10,000 RON. Ce portofoliu e mai bine diversificat?",
                "options": [
                    "10,000 RON în TLV",
                    "5,000 TLV + 5,000 BRD (ambele bănci)",
                    "2,000 TLV + 2,000 H2O + 2,000 SNP + 2,000 Gold + 2,000 S&P500",
                    "1,000 RON în 10 acțiuni diferite"
                ],
                "correct": 2,
                "explanation": "Perfect! Opțiunea C diversifică pe sectoare (bancă, energie, petrol, aur, indice global). Celelalte sunt fie concentrate (A,B) fie prea fragmentate (D)."
            }
        ]
    }
]

# ============================================
# MODELS
# ============================================

class QuizAnswer(BaseModel):
    lesson_id: str
    answers: List[int]  # List of selected answer indices

class ScenarioProgress(BaseModel):
    lesson_id: str
    scenario_step: int
    answer: int

# ============================================
# ROUTES
# ============================================

@router.get("/lessons")
async def get_all_lessons():
    """Get all trading school lessons"""
    return {
        "lessons": TRADING_LESSONS,
        "total": len(TRADING_LESSONS),
        "modules": {
            "module_1": "Fundamentele (Beginner)",
            "module_2": "Risk Management (Intermediate)"
        }
    }

@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    """Get specific lesson"""
    for lesson in TRADING_LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
    raise HTTPException(status_code=404, detail="Lesson not found")

@router.post("/quiz/submit")
async def submit_quiz(quiz_data: QuizAnswer, user: dict = Depends(require_auth)):
    """Submit quiz answers and get score"""
    db = await get_database()
    
    # Find lesson
    lesson = None
    for l in TRADING_LESSONS:
        if l["id"] == quiz_data.lesson_id:
            lesson = l
            break
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Calculate score
    quiz = lesson.get("quiz", [])
    correct_count = 0
    results = []
    
    for idx, answer in enumerate(quiz_data.answers):
        if idx < len(quiz):
            is_correct = answer == quiz[idx]["correct"]
            if is_correct:
                correct_count += 1
            
            results.append({
                "question": quiz[idx]["question"],
                "your_answer": quiz[idx]["options"][answer] if answer < len(quiz[idx]["options"]) else "Invalid",
                "correct": is_correct,
                "explanation": quiz[idx]["explanation"]
            })
    
    score_percent = (correct_count / len(quiz)) * 100 if len(quiz) > 0 else 0
    passed = score_percent >= 80
    
    # Save progress
    await db.user_progress.update_one(
        {"user_id": user["user_id"]},
        {
            "$set": {
                f"lessons.{quiz_data.lesson_id}": {
                    "completed": passed,
                    "score": score_percent,
                    "attempts": 1,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        },
        upsert=True
    )
    
    return {
        "lesson_id": quiz_data.lesson_id,
        "score": score_percent,
        "correct": correct_count,
        "total": len(quiz),
        "passed": passed,
        "results": results,
        "message": "Felicitări! Ai trecut!" if passed else "Mai încearcă! Trebuie 80%+ pentru a trece."
    }

@router.get("/progress")
async def get_progress(user: dict = Depends(require_auth)):
    """Get user learning progress"""
    db = await get_database()
    
    progress = await db.user_progress.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not progress:
        return {
            "completed_lessons": [],
            "total_lessons": len(TRADING_LESSONS),
            "progress_percent": 0,
            "current_module": 1
        }
    
    completed = progress.get("lessons", {})
    completed_count = sum(1 for l in completed.values() if l.get("completed"))
    
    return {
        "completed_lessons": list(completed.keys()),
        "total_lessons": len(TRADING_LESSONS),
        "progress_percent": (completed_count / len(TRADING_LESSONS)) * 100,
        "lessons_detail": completed
    }
