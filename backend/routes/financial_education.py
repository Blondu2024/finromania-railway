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
    }
]

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
