"""Quiz System pentru deblocarea nivelurilor"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import random
from config.database import get_database
from routes.auth import require_auth

router = APIRouter(prefix="/quiz", tags=["quiz"])

# ============================================
# QUIZ QUESTIONS DATABASE
# ============================================

QUIZ_QUESTIONS = {
    "intermediate": [
        {
            "id": "int_1",
            "question": "Ce înseamnă RSI (Relative Strength Index)?",
            "options": [
                "Un indicator de volum",
                "Un indicator de momentum care măsoară viteza și magnitudinea mișcărilor de preț",
                "Rata dobânzii de referință",
                "Raportul dintre active și pasive"
            ],
            "correct": 1,
            "explanation": "RSI este un indicator de momentum care variază între 0 și 100. Valori sub 30 indică supravânzare, iar peste 70 supracumpărare."
        },
        {
            "id": "int_2",
            "question": "Ce reprezintă o medie mobilă (Moving Average)?",
            "options": [
                "Prețul maxim din ultimele zile",
                "Media prețurilor pe o perioadă specificată, care netezește fluctuațiile",
                "Diferența dintre preț și volum",
                "Numărul de acțiuni tranzacționate"
            ],
            "correct": 1,
            "explanation": "Media mobilă calculează media prețurilor pe o perioadă (ex: 50 zile) pentru a identifica tendințe și niveluri de suport/rezistență."
        },
        {
            "id": "int_3",
            "question": "Ce înseamnă 'suport' în analiza tehnică?",
            "options": [
                "Punctul în care cererea este suficient de puternică pentru a opri scăderea prețului",
                "Prețul maxim istoric",
                "Volumul mediu zilnic",
                "Dividendul anual"
            ],
            "correct": 0,
            "explanation": "Nivelul de suport este un prag de preț unde cererea tinde să fie mai mare decât oferta, oprind scăderea."
        },
        {
            "id": "int_4",
            "question": "Ce indică un volum ridicat însoțit de o creștere de preț?",
            "options": [
                "Slăbiciune a trendului",
                "Confirmare a trendului ascendent",
                "Inversare iminentă",
                "Nimic relevant"
            ],
            "correct": 1,
            "explanation": "Volumul ridicat la creștere de preț confirmă interesul cumpărătorilor și susține continuarea trendului ascendent."
        },
        {
            "id": "int_5",
            "question": "Ce este MACD?",
            "options": [
                "Un tip de ordin de tranzacționare",
                "Un indicator bazat pe diferența dintre două medii mobile exponențiale",
                "Maximul și minimul zilnic",
                "Un indice bursier"
            ],
            "correct": 1,
            "explanation": "MACD (Moving Average Convergence Divergence) este diferența dintre EMA(12) și EMA(26), folosit pentru identificarea momentum-ului."
        },
        {
            "id": "int_6",
            "question": "Ce este diversificarea portofoliului?",
            "options": [
                "Cumpărarea unei singure acțiuni în cantitate mare",
                "Distribuirea investițiilor în mai multe active pentru a reduce riscul",
                "Vânzarea tuturor acțiunilor",
                "Investiția doar în obligațiuni"
            ],
            "correct": 1,
            "explanation": "Diversificarea reduce riscul prin împărțirea investițiilor în active diferite care nu se corelează perfect."
        },
        {
            "id": "int_7",
            "question": "Ce înseamnă 'bear market'?",
            "options": [
                "O piață în creștere constantă",
                "O piață în scădere de cel puțin 20% de la maximele recente",
                "O piață cu volatilitate redusă",
                "O piață cu volum mare"
            ],
            "correct": 1,
            "explanation": "Bear market se definește ca o scădere de peste 20% de la maximele recente, caracterizată de pesimism generalizat."
        },
        {
            "id": "int_8",
            "question": "Ce rol are Stop Loss-ul?",
            "options": [
                "Să garanteze profit",
                "Să limiteze pierderile prin vânzare automată la un preț prestabilit",
                "Să crească volumul tranzacțiilor",
                "Să calculeze dividendele"
            ],
            "correct": 1,
            "explanation": "Stop Loss este un ordin automat de vânzare când prețul scade la un nivel stabilit, protejând capitalul."
        },
        {
            "id": "int_9",
            "question": "Ce înseamnă lichiditate pe bursă?",
            "options": [
                "Cât de ușor poți converti un activ în numerar fără a afecta semnificativ prețul",
                "Cantitatea de apă dintr-o companie",
                "Profitul net anual",
                "Numărul de angajați"
            ],
            "correct": 0,
            "explanation": "Lichiditatea măsoară facilitatea cu care un activ poate fi cumpărat sau vândut la prețuri stabile."
        },
        {
            "id": "int_10",
            "question": "Ce este 'rezistența' în analiza tehnică?",
            "options": [
                "Prețul minim al acțiunii",
                "Nivelul de preț unde presiunea de vânzare depășește cererea",
                "Volumul mediu",
                "Rata dividendului"
            ],
            "correct": 1,
            "explanation": "Rezistența este un nivel de preț unde vânzătorii tind să fie mai activi, împiedicând creșterea ulterioară."
        },
        {
            "id": "int_11",
            "question": "Ce indică un gap (gol) pe graficul de preț?",
            "options": [
                "O eroare tehnică",
                "O mișcare bruscă de preț fără tranzacții în acel interval",
                "Lipsa de lichiditate permanentă",
                "Dividendul acordat"
            ],
            "correct": 1,
            "explanation": "Gap-ul apare când prețul de deschidere diferă semnificativ de închiderea anterioară, indicând știri importante sau sentiment puternic."
        },
        {
            "id": "int_12",
            "question": "Ce este volatilitatea?",
            "options": [
                "Măsura stabilității unei companii",
                "Măsura variației prețului unui activ într-o perioadă",
                "Numărul de acțiuni disponibile",
                "Rata inflației"
            ],
            "correct": 1,
            "explanation": "Volatilitatea măsoară amplitudinea fluctuațiilor de preț. Volatilitate mare = risc mai mare, dar și oportunități."
        }
    ],
    "advanced": [
        {
            "id": "adv_1",
            "question": "Ce este raportul P/E (Price to Earnings)?",
            "options": [
                "Prețul acțiunii împărțit la câștigul pe acțiune (EPS)",
                "Profitul împărțit la numărul de angajați",
                "Prețul de vânzare al produselor",
                "Rata de creștere a veniturilor"
            ],
            "correct": 0,
            "explanation": "P/E arată cât plătesc investitorii pentru fiecare leu de profit. Un P/E mic poate indica subevaluare, unul mare poate indica așteptări de creștere."
        },
        {
            "id": "adv_2",
            "question": "Ce reprezintă Free Cash Flow (FCF)?",
            "options": [
                "Banii disponibili pentru marketing",
                "Numerarul generat după cheltuielile de capital, disponibil pentru dividende, achiziții sau reducerea datoriilor",
                "Profitul brut",
                "Totalul activelor"
            ],
            "correct": 1,
            "explanation": "FCF = Cash Flow Operațional - CapEx. Este esențial pentru evaluarea sănătății financiare și capacității de distribuție."
        },
        {
            "id": "adv_3",
            "question": "Ce înseamnă raportul Debt-to-Equity?",
            "options": [
                "Prețul acțiunii raportat la dividend",
                "Raportul dintre datoriile totale și capitalurile proprii",
                "Numărul de acțiuni emise",
                "Rata de creștere a profitului"
            ],
            "correct": 1,
            "explanation": "D/E măsoară gradul de îndatorare. Un raport mare poate indica risc financiar crescut, dar și leverage pentru creștere."
        },
        {
            "id": "adv_4",
            "question": "Ce este ROE (Return on Equity)?",
            "options": [
                "Randamentul dividendelor",
                "Profitul net raportat la capitalurile proprii, măsurând eficiența utilizării capitalului acționarilor",
                "Rata dobânzii la obligațiuni",
                "Creșterea veniturilor"
            ],
            "correct": 1,
            "explanation": "ROE = Profit Net / Capitaluri Proprii. Un ROE ridicat și constant indică o companie eficientă în generarea de profit."
        },
        {
            "id": "adv_5",
            "question": "Ce indică un raport P/B (Price to Book) sub 1?",
            "options": [
                "Compania este supraevaluată",
                "Piața evaluează compania sub valoarea sa contabilă, posibil subevaluată sau cu probleme",
                "Compania plătește dividende mari",
                "Acțiunea este foarte lichidă"
            ],
            "correct": 1,
            "explanation": "P/B < 1 înseamnă că prețul de piață este sub valoarea activelor nete. Poate indica oportunitate sau probleme fundamentale."
        },
        {
            "id": "adv_6",
            "question": "Ce este EBITDA?",
            "options": [
                "Un tip de obligațiune",
                "Câștigurile înainte de dobânzi, taxe, depreciere și amortizare",
                "Efectivul de personal",
                "Evaluarea de piață"
            ],
            "correct": 1,
            "explanation": "EBITDA elimină efectele structurii de capital și contabile, permițând comparații mai bune între companii."
        },
        {
            "id": "adv_7",
            "question": "Ce înseamnă 'margin of safety' în investiții?",
            "options": [
                "Pragul de rentabilitate",
                "Diferența dintre valoarea intrinsecă estimată și prețul de cumpărare",
                "Limita de îndatorare",
                "Garanția bancară"
            ],
            "correct": 1,
            "explanation": "Margin of safety protejează împotriva erorilor de evaluare cumpărând semnificativ sub valoarea estimată."
        },
        {
            "id": "adv_8",
            "question": "Ce este dilution (diluția) acțiunilor?",
            "options": [
                "Scăderea prețului din cauza știrilor negative",
                "Reducerea procentului de proprietate când compania emite acțiuni noi",
                "Creșterea datoriilor",
                "Reducerea dividendelor"
            ],
            "correct": 1,
            "explanation": "Diluția apare la emisiuni de acțiuni noi, reducând EPS și procentul de proprietate al acționarilor existenți."
        },
        {
            "id": "adv_9",
            "question": "Ce reprezintă Working Capital (Capital de Lucru)?",
            "options": [
                "Capitalul social",
                "Diferența dintre activele curente și pasivele curente",
                "Profitul operațional",
                "Investițiile pe termen lung"
            ],
            "correct": 1,
            "explanation": "Working Capital = Active Curente - Pasive Curente. Un WC pozitiv indică capacitatea de a acoperi obligațiile pe termen scurt."
        },
        {
            "id": "adv_10",
            "question": "Ce este DCF (Discounted Cash Flow)?",
            "options": [
                "O metodă de evaluare bazată pe fluxurile de numerar viitoare actualizate",
                "Un tip de dividend",
                "Un indicator tehnic",
                "O formă de obligațiune"
            ],
            "correct": 0,
            "explanation": "DCF estimează valoarea prezentă a fluxurilor de numerar viitoare, considerând valoarea în timp a banilor."
        },
        {
            "id": "adv_11",
            "question": "Ce indică un Current Ratio sub 1?",
            "options": [
                "Compania are lichiditate excelentă",
                "Compania poate avea dificultăți în achitarea datoriilor pe termen scurt",
                "Compania este foarte profitabilă",
                "Acțiunile sunt subevaluate"
            ],
            "correct": 1,
            "explanation": "Current Ratio < 1 înseamnă că pasivele curente depășesc activele curente, semnal de potențiale probleme de lichiditate."
        },
        {
            "id": "adv_12",
            "question": "Ce este Earnings Yield?",
            "options": [
                "Dividendul anual",
                "EPS împărțit la prețul acțiunii (inversul P/E)",
                "Creșterea câștigurilor",
                "Randamentul obligațiunilor"
            ],
            "correct": 1,
            "explanation": "Earnings Yield = EPS/Preț = 1/P/E. Permite compararea randamentului acțiunilor cu cel al obligațiunilor."
        }
    ]
}


class QuizSubmission(BaseModel):
    level: str  # "intermediate" or "advanced"
    answers: Dict[str, int]  # {question_id: selected_option_index}


@router.get("/{level}")
async def get_quiz(level: str, user: dict = Depends(require_auth)):
    """Get quiz questions for a specific level"""
    if level not in QUIZ_QUESTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid level: {level}")
    
    db = await get_database()
    user_data = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    # Check if PRO user (skip quiz)
    if user_data and user_data.get("subscription_level") == "pro":
        return {
            "skip_quiz": True,
            "message": "Ca utilizator PRO, ai acces direct la toate nivelurile fără quiz."
        }
    
    # Check if already unlocked
    unlocked = user_data.get("unlocked_levels", ["beginner"]) if user_data else ["beginner"]
    if level in unlocked:
        return {
            "already_unlocked": True,
            "message": f"Nivelul {level} este deja deblocat."
        }
    
    # Get random 10 questions
    all_questions = QUIZ_QUESTIONS[level]
    selected = random.sample(all_questions, min(10, len(all_questions)))
    
    # Remove correct answers for client
    questions_for_client = []
    for q in selected:
        questions_for_client.append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"]
        })
    
    return {
        "level": level,
        "level_name": "Mediu" if level == "intermediate" else "Expert",
        "questions": questions_for_client,
        "total_questions": len(questions_for_client),
        "pass_score": 7,
        "time_limit_minutes": 15,
        "instructions": f"Trebuie să răspunzi corect la minim 7 din 10 întrebări pentru a debloca nivelul {'Mediu' if level == 'intermediate' else 'Expert'}."
    }


@router.post("/submit")
async def submit_quiz(submission: QuizSubmission, user: dict = Depends(require_auth)):
    """Submit quiz answers and check if passed"""
    if submission.level not in QUIZ_QUESTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid level: {submission.level}")
    
    db = await get_database()
    
    # Get all questions to check answers
    all_questions = {q["id"]: q for q in QUIZ_QUESTIONS[submission.level]}
    
    # Calculate score
    correct_count = 0
    results = []
    
    for question_id, selected_answer in submission.answers.items():
        question = all_questions.get(question_id)
        if question:
            is_correct = selected_answer == question["correct"]
            if is_correct:
                correct_count += 1
            results.append({
                "question_id": question_id,
                "question": question["question"],
                "selected": selected_answer,
                "correct": question["correct"],
                "is_correct": is_correct,
                "explanation": question["explanation"]
            })
    
    total_questions = len(submission.answers)
    score = correct_count
    passed = score >= 7
    
    # Record quiz attempt
    quiz_record = {
        "user_id": user["user_id"],
        "level": submission.level,
        "score": score,
        "total": total_questions,
        "passed": passed,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.quiz_attempts.insert_one(quiz_record)
    
    # Update user if passed
    if passed:
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {
                "$addToSet": {"unlocked_levels": submission.level},
                "$set": {
                    "experience_level": submission.level,
                    f"quiz_scores.{submission.level}": score
                }
            },
            upsert=True
        )
    
    level_name = "Mediu" if submission.level == "intermediate" else "Expert"
    
    return {
        "score": score,
        "total": total_questions,
        "percentage": round(score / total_questions * 100),
        "passed": passed,
        "required_score": 7,
        "level": submission.level,
        "level_name": level_name,
        "message": f"Felicitări! Ai deblocat nivelul {level_name}! 🎉" if passed else f"Mai încearcă! Ai nevoie de minim 7 răspunsuri corecte. Scor: {score}/10",
        "results": results,
        "can_retry": not passed,
        "next_steps": {
            "unlocked": submission.level if passed else None,
            "features_unlocked": [
                "Indicatori tehnici (RSI, MA, MACD)",
                "Portofoliu BVB + Internațional",
                "AI Advisor avansat"
            ] if passed and submission.level == "intermediate" else [
                "Analiză fundamentală completă",
                "AI trasează linii pe grafice",
                "Calculator fiscal PF/SRL",
                "Toate piețele"
            ] if passed and submission.level == "advanced" else []
        }
    }


@router.get("/history/{level}")
async def get_quiz_history(level: str, user: dict = Depends(require_auth)):
    """Get user's quiz attempt history for a level"""
    db = await get_database()
    
    attempts = await db.quiz_attempts.find(
        {"user_id": user["user_id"], "level": level},
        {"_id": 0}
    ).sort("timestamp", -1).limit(10).to_list(10)
    
    return {
        "level": level,
        "attempts": attempts,
        "total_attempts": len(attempts),
        "best_score": max([a["score"] for a in attempts], default=0),
        "passed": any(a["passed"] for a in attempts)
    }
