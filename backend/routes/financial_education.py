"""Financial Education - Educație Financiară pentru Români"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timezone
from config.database import get_database
from routes.auth import require_auth

router = APIRouter(prefix="/financial-education", tags=["financial_education"])

# Complete Financial Education Curriculum
FINANCIAL_LESSONS = [
    {
        "id": "fin_lesson_1",
        "module": 1,
        "order": 1,
        "title": "Ce Este Educația Financiară și De Ce Contează",
        "subtitle": "Primul pas către libertate financiară",
        "duration": "8 min",
        "difficulty": "beginner",
        "emoji": "💡",
        "tier": "free",
        "content": """
# Educația Financiară - De Ce Contează?

## 💰 Realitatea din România

**Statistici șocante:**
- 70% din români trăiesc de pe o lună pe alta
- 60% nu au economii pentru urgențe
- 85% nu înțeleg cum funcționează dobânzile
- 90% nu au educație financiară formală

**De ce?** Pentru că **NIMENI nu ne învață despre bani!**
- În școală: NU
- În facultate: NU (doar dacă faci Economie)
- De la părinți: Rar (dacă ei știu)

## 🎯 Ce Înseamnă Educație Financiară?

**Nu e:**
- ❌ Cum să devii milionar overnight
- ❌ Scheme de "bani ușor"
- ❌ Doar pentru bogați

**Este:**
- ✅ Cum să-ți faci un buget
- ✅ Cum să economisești regulat
- ✅ Cum să eviți datorii proaste
- ✅ Cum să investești inteligent
- ✅ Cum să te pregătești pentru pensie

## 💡 Ce Vei Învăța în Acest Curs

**Modul 1: Fundamente**
1. Bugete și gestionarea banilor
2. Fond de urgență
3. Dobânzi și inflație

**Modul 2: Instrumente**
4. Conturi bancare
5. Credite smart
6. Asigurări
7. Pensii în RO

**Modul 3: Investiții**
8. De ce să investești
9. Unde să investești în RO
10. ETF-uri și diversificare

**Rezultat:** Vei avea control complet asupra banilor tăi! 💪

## ✅ Promisiunea Noastră

- 🆓 **100% GRATUIT** - Educația nu ar trebui să coste
- 🇷🇴 **Adaptat pentru România** - Exemple cu RON, bănci RO, taxe RO
- 📚 **Practic** - Apply imediat ce înveți
- 🎯 **Pas cu pas** - De la 0 la expert
- ❓ **Quiz-uri** - Verifică-ți înțelegerea

## 🎓 Gata să Începi?

Prima lecție: Cum să-ți faci un buget care funcționează!
""",
        "quiz": [
            {
                "question": "Ce procent din români NU au economii pentru urgențe?",
                "options": ["30%", "60%", "85%", "95%"],
                "correct": 1,
                "explanation": "Corect! ~60% din români nu au economii pentru urgențe. De aceea fondul de urgență e atât de important - Lecția 3!"
            },
            {
                "question": "Educația financiară înseamnă:",
                "options": [
                    "Scheme de îmbogățire rapidă",
                    "Doar pentru bogați",
                    "Cum să gestionezi banii inteligent",
                    "Cum să devii milionar"
                ],
                "correct": 2,
                "explanation": "Perfect! Educația financiară e despre gestionarea inteligentă a banilor - bugete, economii, investiții - pentru ORICINE!"
            }
        ]
    },
    {
        "id": "fin_lesson_2",
        "module": 1,
        "order": 2,
        "title": "Bugetul Personal - Fundația Succesului Financiar",
        "subtitle": "Regula 50/30/20 care funcționează",
        "duration": "12 min",
        "difficulty": "beginner",
        "emoji": "📊",
        "tier": "free",
        "content": """
# Bugetul Personal

## 💰 De Ce Ai Nevoie de Buget?

**Fără buget:**
- Nu știi pe ce se duc banii
- "Dispare" salariul până la final de lună
- Nu ai control
- Nu poți economisi

**Cu buget:**
- ✅ Știi EXACT pe ce cheltuiești
- ✅ Controlezi fiecare leu
- ✅ Economisești automat
- ✅ Atingi obiective financiare

## 📊 Regula 50/30/20

**Formula simplă care funcționează:**

**50% - NEVOI (Esențiale)**
- Chirie/rată
- Utilități (curent, gaz, apă)
- Mâncare (supermarket, nu restaurante!)
- Transport (abonament, benzină)
- Medicamente

**30% - DORINȚE (Plăceri)**
- Restaurante, cafenele
- Haine, gadgeturi
- Vacanțe
- Hobby-uri
- Entertainment (Netflix, cinema)

**20% - ECONOMII & INVESTIȚII**
- Fond urgență (prima prioritate!)
- Investiții (după fond urgență)
- Obiective (mașină, casă, etc.)

## 💡 Exemplu Practic

**Salariu NET: 5,000 RON/lună**

**50% Nevoi (2,500 RON):**
- Chirie: 1,500 RON
- Utilități: 300 RON
- Mâncare: 600 RON
- Transport: 100 RON

**30% Dorințe (1,500 RON):**
- Restaurante: 500 RON
- Haine: 300 RON
- Entertainment: 200 RON
- Ieșiri: 500 RON

**20% Economii (1,000 RON):**
- Fond urgență: 500 RON (până ajungi la 3-6 luni)
- Investiții: 500 RON (după ce ai fond)

## 🎯 Cum Să-ți Faci Bugetul

**Pas 1: Calculează VENITUL**
- Salariu NET (după taxe)
- Alte venituri

**Pas 2: Înregistrează TOATE Cheltuielile**
- 1 lună completă
- FIECARE leu (da, și cafeaua!)
- Apps: Money Pro, Wallet, Excel

**Pas 3: Clasifică în 3 Categorii**
- Nevoi vs Dorințe vs Economii
- Calculează %

**Pas 4: Ajustează**
- Dacă Nevoi > 50% → Reduce chirie sau găsește soluții
- Dacă Economii < 20% → Reduce Dorințele
- Scopul: 50/30/20!

## ⚠️ Greșeli Comune

**1. "Nu-mi ajung banii pentru economii"**
→ Plătește-te PE TINE primul! Economii = prima cheltuială, nu ce rămâne!

**2. "Tracking e plictisitor"**
→ Folosește apps auto (conectare bancară) - Wallet, Revolut

**3. "E prea strict"**
→ 50/30/20 e ghid, nu lege! Adaptează la situația ta

## 💪 Challenge

**Urmărește cheltuielile 1 lună!**
- Fă-ți un spreadsheet simplu
- Sau folosește Wallet app
- La final, vezi unde se duc banii
- **Vei fi ȘOCAT!** (cafele, livrări, Uber...)
""",
        "quiz": [
            {
                "question": "Regula 50/30/20: Ce înseamnă 20%?",
                "options": [
                    "Cheltuieli esențiale",
                    "Plăceri și dorințe",
                    "Economii și investiții",
                    "Taxe"
                ],
                "correct": 2,
                "explanation": "Corect! 20% din venit trebuie să meargă la ECONOMII și INVESTIȚII. E fundația pentru viitorul tău financiar!"
            },
            {
                "question": "Ai salariu 4,000 RON. Cât ar trebui să economisești lunar (regula 20%)?",
                "options": ["400 RON", "800 RON", "1,200 RON", "2,000 RON"],
                "correct": 1,
                "explanation": "Perfect! 20% din 4,000 = 800 RON/lună. În 1 an = 9,600 RON economii! În 5 ani = 48,000 RON (fără dobândă)!"
            }
        ]
    },
    {
        "id": "fin_lesson_3",
        "module": 1,
        "order": 3,
        "title": "Fondul de Urgență - Perna Ta de Siguranță",
        "subtitle": "3-6 luni fără stres financiar",
        "duration": "10 min",
        "difficulty": "beginner",
        "emoji": "🛡️",
        "tier": "free",
        "content": """
# Fondul de Urgență

## 🚨 Ce E și De Ce E VITAL?

**Fond de urgență** = Bani puși deoparte pentru URGENȚE neprevăzute.

**Urgențe:**
- 🚗 Mașina se strică (reparație 2,000 RON)
- 🏥 Probleme medicale (stomatolog, analize)
- 💼 Pierzi job-ul (trebuie să trăiești 3-6 luni)
- 🏠 Locuința (țeava spartă, frigider stricat)

**Fără fond:** Împrumut (dobânzi!), stres, panică! 😰
**Cu fond:** Plătești cash, dormi liniștit! 😊

## 💰 Cât Trebuie Să Ai?

**Formula:**
```
Fond Urgență = Cheltuieli Lunare × 3-6 luni
```

**Exemplu:**
- Cheltuieli lunare: 3,000 RON
- **Minim:** 3,000 × 3 = **9,000 RON**
- **Ideal:** 3,000 × 6 = **18,000 RON**

**Cât depinde de:**
- Job stabil (3 luni) vs instabil (6 luni)
- Singur (3 luni) vs Familie (6 luni)
- Asigurări multe (3 luni) vs puține (6 luni)

## 🏦 Unde Să-l Ții?

**❌ NU aici:**
- Acțiuni (pot scădea când ai nevoie!)
- Investiții pe termen lung
- Crypto (volatil!)
- Cash acasă (furat, incendiu)

**✅ DA aici:**
- **Cont curent** (acces instant!)
- **Cont economii** (dobândă mică dar OK)
- **Depozit la vedere** (retragere oricând)

**Criterii:**
1. ✅ **Lichiditate** - Acces în 24h
2. ✅ **Siguranță** - Garantat (FGDB în RO)
3. ✅ **Dobândă OK** - Măcar ceva (1-3%)

## 📊 Cum Să-l Construiești

**Pas cu Pas:**

**Luna 1-3:** Economisește 1,000 RON/lună
- După 3 luni: 3,000 RON (1 lună cheltuieli)

**Luna 4-6:** Continuă 1,000 RON/lună
- După 6 luni: 6,000 RON (2 luni)

**Luna 7-12:** 1,000 RON/lună
- După 12 luni: 12,000 RON (4 luni) ✅

**Luna 13-18:** 1,000 RON/lună
- După 18 luni: 18,000 RON (6 luni) 🎉

**Apoi:** Stop building fond → Start investing!

## ⚠️ Când Să-l Folosești

**DA:**
- ✅ Urgență medicală
- ✅ Job pierdut
- ✅ Mașină/casă stricate (urgent)

**NU:**
- ❌ Vacanță (economisești separat!)
- ❌ Gadgeturi noi (dorință, nu urgență)
- ❌ Cadouri (planifică în buget)

**Regula:** Dacă NU e urgență → NU atingi fondul!
""",
        "quiz": [
            {
                "question": "Ai cheltuieli de 4,000 RON/lună. Cât fond de urgență îți trebuie (minim)?",
                "options": ["4,000 RON", "8,000 RON", "12,000 RON", "24,000 RON"],
                "correct": 2,
                "explanation": "Corect! Minim 3 luni × 4,000 = 12,000 RON. Ideal ar fi 6 luni (24,000 RON) pentru siguranță maximă!"
            },
            {
                "question": "Unde NU ar trebui să ții fondul de urgență?",
                "options": [
                    "Cont curent",
                    "Cont economii",
                    "Acțiuni pe bursă",
                    "Depozit la vedere"
                ],
                "correct": 2,
                "explanation": "Corect! Acțiunile pot scădea când ai nevoie de bani! Fondul trebuie în conturi LICHIDE și SIGURE (curent, economii, depozit)."
            }
        ]
    },
    {
        "id": "fin_lesson_4",
        "module": 1,
        "order": 4,
        "title": "Dobânzi - Prietenul și Dușmanul Tău",
        "subtitle": "Cum dobânda compusă te poate îmbogăți sau sărăci",
        "duration": "11 min",
        "difficulty": "beginner",
        "emoji": "📈",
        "tier": "free",
        "content": """
# Dobânzi - Puterea Timpului

## 💰 Ce Sunt Dobânzile?

**Dobânda** = "Chiria" banilor.

**Când PRIMEȘTI dobândă:**
- Depozit bancar (tu împrumuți băncii)
- Obligațiuni (împrumuți statului/companiei)
- Conturi economii

**Când PLĂTEȘTI dobândă:**
- Credit (banca/IFN îți împrumută)
- Card de credit
- Overdraft

## 📊 Dobândă Simplă vs Compusă

### **Dobândă Simplă** (Rară)

**Formula:** Dobândă se calculează DOAR pe suma inițială

**Exemplu:**
- Depui: 10,000 RON
- Dobândă: 5%/an (simplă)
- **An 1:** 10,000 × 5% = +500 RON → Total 10,500 RON
- **An 2:** 10,000 × 5% = +500 RON → Total 11,000 RON
- **An 10:** 10,000 + (500 × 10) = **15,000 RON**

---

### **Dobândă Compusă** (Magică!)

**Formula:** Dobândă se calculează pe sumă + dobânzile anterioare

**"Dobândă la dobândă" = Exponențial!**

**Exemplu:**
- Depui: 10,000 RON
- Dobândă: 5%/an (compusă)
- **An 1:** 10,000 × 5% = +500 RON → **10,500 RON**
- **An 2:** 10,500 × 5% = +525 RON → **11,025 RON**
- **An 3:** 11,025 × 5% = +551 RON → **11,576 RON**
- ...
- **An 10:** **16,289 RON** (vs 15,000 cu simplă!)

**+1,289 RON diferență DOAR din compunere!** 🎉

## 🚀 Puterea Timpului

**Același 10,000 RON la 5% compus:**

- **10 ani:** 16,289 RON (+63%)
- **20 ani:** 26,533 RON (+165%)
- **30 ani:** 43,219 RON (+332%)
- **40 ani:** 70,400 RON (+604%)

**Albert Einstein:** "Dobânda compusă e cea mai puternică forță din univers!"

## 💸 Partea Întunecată - Credite

**Dobânda compusă funcționează ȘI ÎMPOTRIVA TA!**

**Exemplu Credit:**
- Împrumuți: 10,000 RON
- DAE: 15%/an (compusă)
- **An 1:** Datorezi 11,500 RON
- **An 5:** Datorezi 20,114 RON (dublat!)
- **An 10:** Datorezi 40,456 RON (×4!)

**De aceea:**
- ✅ Dobândă la economii = PRIETENA ta
- ❌ Dobândă la credite = DUȘMANUL tău

## 🎯 Lecția Cheie

**Start EARLY!**

**Economii 500 RON/lună la 7% compus:**

**Start la 25 ani (40 ani până la 65):**
- Total investit: 500 × 12 × 40 = 240,000 RON
- **La 65 ani:** **1,310,000 RON!** 🎉

**Start la 35 ani (30 ani până la 65):**
- Total investit: 500 × 12 × 30 = 180,000 RON
- **La 65 ani:** 610,000 RON

**Diferență 10 ani = 700,000 RON pierdut!** 😱

**Timpul bate suma! Start NOW!** ⏰
""",
        "quiz": [
            {
                "question": "10,000 RON la 5% dobândă compusă timp de 20 ani devine aproximativ:",
                "options": ["15,000 RON", "20,000 RON", "26,500 RON", "50,000 RON"],
                "correct": 2,
                "explanation": "Corect! Cu dobândă compusă la 5%, 10,000 RON devine ~26,500 RON în 20 ani. Asta e puterea compunerii!"
            },
            {
                "question": "Când e dobânda compusă DUȘMANUL tău?",
                "options": [
                    "La depozite bancare",
                    "La credite și împrumuturi",
                    "La acțiuni",
                    "Niciodată"
                ],
                "correct": 1,
                "explanation": "Exact! La credite, dobânda compusă lucrează ÎMPOTRIVA ta - datoriile cresc exponențial. De aceea eviți creditele scumpe!"
            }
        ]
    },
    {
        "id": "fin_lesson_5",
        "module": 1,
        "order": 5,
        "title": "Inflația - Dușmanul Invizibil al Economiilor",
        "subtitle": "De ce banii tăi valorează mai puțin în fiecare an",
        "duration": "9 min",
        "difficulty": "beginner",
        "emoji": "📉",
        "tier": "free",
        "content": """
# Inflația

## 📉 Ce Este Inflația?

**Inflația** = Creșterea generală a prețurilor în timp

**Exemplu simplu:**
- **2020:** Pâine = 3 RON
- **2024:** Pâine = 5 RON
- **Inflație:** +67% în 4 ani!

**Rezultat:** Cu aceiași bani cumperi MAI PUȚIN! 😰

## 🇷🇴 Inflația în România

**Istoric recent:**
- **2021:** 5% inflație
- **2022:** 13% inflație (șoc!)
- **2023:** 10% inflație
- **2024:** 7% inflație

**Medie:** ~7-8%/an în România (vs 2-3% în UE)

## 💸 Cum Te Afectează

**Ai 10,000 RON în saltea (0% dobândă):**

**După 1 an (7% inflație):**
- Ai încă: 10,000 RON
- Dar puterea de cumpărare: **9,300 RON** echivalent
- **Pierdere:** -700 RON (-7%)!

**După 10 ani:**
- Ai: 10,000 RON
- Putere cumpărare: **~5,000 RON** echivalent
- **Pierdere:** -50%! Jumătate dispărută! 😱

**Inflația e un taxă invizibilă pe economii!**

## 🛡️ Cum Să Te Protejezi

**❌ PROST: Cash în saltea**
- 0% dobândă
- Pierdere 7%/an din inflație
- **Rezultat:** Sărăcești în fiecare an

**⚠️ OK: Depozit bancar (3-5% dobândă)**
- +5% dobândă
- -7% inflație
- **Rezultat:** Tot pierzi -2%/an (dar mai puțin!)

**✅ BUN: Investiții (8-12% return mediu)**
- +10% return anual
- -7% inflație
- **Rezultat:** +3% REAL gain! Bații inflația! 🎉

## 🎯 Lecția Critică

**"Economisirea" în cont cu 0% dobândă = PIERDERE sigură!**

**De aceea:**
1. Fond urgență → Depozit cu dobândă (minim)
2. Restul economii → **INVESTIȚII** (bate inflația!)

**Investițiile NU sunt opționale - sunt NECESARE pentru a-ți păstra puterea de cumpărare!**

## 📊 Exemplu Real

**Ai 50,000 RON economii în 2024:**

**Opțiunea A: Cash acasă (0%)**
- 2034: Putere cumpărare = **25,000 RON**
- **Pierdere:** -25,000 RON! 😱

**Opțiunea B: Depozit 4%**
- 2034: ~74,000 RON
- Minus inflație: Putere = ~37,000 RON
- **Pierdere:** -13,000 RON 😐

**Opțiunea C: Investiții 10%**
- 2034: ~130,000 RON
- Minus inflație: Putere = ~65,000 RON
- **CÂȘTIG:** +15,000 RON! 🎉

**Concluzie:** Investițiile nu sunt "risc" - CASH-ul e riscul real!
""",
        "quiz": [
            {
                "question": "Ai 10,000 RON în saltea. Cu inflație 7%/an, după 10 ani puterea lor de cumpărare e:",
                "options": ["10,000 RON (la fel)", "~7,000 RON", "~5,000 RON", "~15,000 RON"],
                "correct": 2,
                "explanation": "Corect! Cu 7% inflație compusă 10 ani, 10,000 RON valorează ~5,000 RON în putere de cumpărare. AI PIERDUT JUMĂTATE!"
            }
        ]
    }
]

# Total lessons tracking
FREE_FIN_LESSONS = len([l for l in FINANCIAL_LESSONS if l.get("tier", "free") == "free"])
TOTAL_FIN_LESSONS = len(FINANCIAL_LESSONS)

# Quiz submission
class QuizAnswer(BaseModel):
    lesson_id: str
    answers: List[int]

@router.get("/lessons")
async def get_financial_lessons():
    """Get all financial education lessons"""
    return {
        "lessons": FINANCIAL_LESSONS,
        "total": len(FINANCIAL_LESSONS),
        "modules": {
            "module_1": "Fundamente Finanțe Personale",
            "module_2": "Instrumente Financiare în România",
            "module_3": "Introducere în Investiții"
        }
    }

@router.get("/lessons/{lesson_id}")
async def get_financial_lesson(lesson_id: str):
    """Get specific lesson"""
    for lesson in FINANCIAL_LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
    raise HTTPException(status_code=404, detail="Lesson not found")

@router.post("/quiz/submit")
async def submit_financial_quiz(quiz_data: QuizAnswer, user: dict = Depends(require_auth)):
    """Submit quiz answers"""
    db = await get_database()
    
    lesson = None
    for l in FINANCIAL_LESSONS:
        if l["id"] == quiz_data.lesson_id:
            lesson = l
            break
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
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
    await db.user_financial_progress.update_one(
        {"user_id": user["user_id"]},
        {
            "$set": {
                f"lessons.{quiz_data.lesson_id}": {
                    "completed": passed,
                    "score": score_percent,
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
async def get_financial_progress(user: dict = Depends(require_auth)):
    """Get learning progress"""
    db = await get_database()
    
    progress = await db.user_financial_progress.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    if not progress:
        return {
            "completed_lessons": [],
            "total_lessons": len(FINANCIAL_LESSONS),
            "progress_percent": 0
        }
    
    completed = progress.get("lessons", {})
    completed_count = sum(1 for l in completed.values() if l.get("completed"))
    
    return {
        "completed_lessons": list(completed.keys()),
        "total_lessons": len(FINANCIAL_LESSONS),
        "progress_percent": (completed_count / len(FINANCIAL_LESSONS)) * 100,
        "lessons_detail": completed
    }
    # Lecția 6-10 vor fi adăugate aici...
]

# Placeholder for remaining lessons - will be added
