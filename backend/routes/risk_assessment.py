"""Risk Assessment routes pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid
from config.database import get_database
from routes.auth import require_auth

router = APIRouter(prefix="/risk-assessment", tags=["risk-assessment"])

# Risk Assessment Questions
QUESTIONS = [
    {
        "id": "q1",
        "question": "Care este orizontul tău de investiție?",
        "options": [
            {"value": "short", "label": "Sub 3 ani", "score": 1},
            {"value": "medium", "label": "3-7 ani", "score": 2},
            {"value": "long", "label": "Peste 7 ani", "score": 3}
        ]
    },
    {
        "id": "q2",
        "question": "Cum ai reacționa dacă investiția ta ar scădea cu 20% într-o lună?",
        "options": [
            {"value": "sell", "label": "Aș vinde imediat pentru a limita pierderile", "score": 1},
            {"value": "wait", "label": "Aș aștepta să văd ce se întâmplă", "score": 2},
            {"value": "buy", "label": "Aș cumpăra mai mult la preț redus", "score": 3}
        ]
    },
    {
        "id": "q3",
        "question": "Care este obiectivul tău principal de investiție?",
        "options": [
            {"value": "preserve", "label": "Păstrarea capitalului (siguranță)", "score": 1},
            {"value": "balanced", "label": "Creștere echilibrată", "score": 2},
            {"value": "growth", "label": "Creștere maximă (accept riscuri)", "score": 3}
        ]
    },
    {
        "id": "q4",
        "question": "Care este experiența ta în investiții?",
        "options": [
            {"value": "none", "label": "Niciuna - sunt complet nou", "score": 1},
            {"value": "basic", "label": "Bază - am citit despre investiții", "score": 2},
            {"value": "experienced", "label": "Experimentat - am investit activ", "score": 3}
        ]
    },
    {
        "id": "q5",
        "question": "Ce procent din venitul lunar poți aloca investițiilor?",
        "options": [
            {"value": "low", "label": "Sub 10%", "score": 1},
            {"value": "medium", "label": "10-25%", "score": 2},
            {"value": "high", "label": "Peste 25%", "score": 3}
        ]
    },
    {
        "id": "q6",
        "question": "Ai un fond de urgență (3-6 luni de cheltuieli)?",
        "options": [
            {"value": "no", "label": "Nu, nu am economii de urgență", "score": 1},
            {"value": "partial", "label": "Parțial (1-3 luni)", "score": 2},
            {"value": "yes", "label": "Da, am 6+ luni acoperite", "score": 3}
        ]
    },
    {
        "id": "q7",
        "question": "Ce ai prefera pentru o investiție de 10.000 RON pe 5 ani?",
        "options": [
            {"value": "safe", "label": "Câștig garantat de 2.000 RON", "score": 1},
            {"value": "balanced", "label": "50% șanse să câștigi 5.000 RON, 50% să pierzi 2.000 RON", "score": 2},
            {"value": "risky", "label": "25% șanse să câștigi 15.000 RON, 75% să pierzi 3.000 RON", "score": 3}
        ]
    }
]

# Risk Profiles
RISK_PROFILES = {
    "conservative": {
        "name": "Conservator",
        "description": "Preferi siguranța capitalului. Ești dispus să accepți randamente mai mici pentru stabilitate.",
        "color": "#3B82F6",
        "icon": "shield",
        "allocation": {
            "stocks": 30,
            "bonds": 50,
            "cash": 20
        },
        "recommendations": [
            "Focusează-te pe obligațiuni guvernamentale și corporative de calitate",
            "Consideră ETF-uri cu volatilitate scăzută",
            "Păstrează o rezervă de lichidități mai mare",
            "Evită acțiunile speculative sau criptomonedele"
        ]
    },
    "moderate": {
        "name": "Moderat",
        "description": "Cauți un echilibru între creștere și siguranță. Accepți fluctuații moderate pentru randamente mai bune.",
        "color": "#10B981",
        "icon": "trending-up",
        "allocation": {
            "stocks": 60,
            "bonds": 30,
            "cash": 10
        },
        "recommendations": [
            "Investește în ETF-uri diversificate global (ex: VWCE)",
            "Combină acțiuni de creștere cu cele de valoare",
            "Include obligațiuni pentru stabilitate",
            "Rebalansează portofoliul anual"
        ]
    },
    "aggressive": {
        "name": "Agresiv",
        "description": "Urmărești creștere maximă și ești confortabil cu volatilitate ridicată. Ai orizont lung de investiție.",
        "color": "#EF4444",
        "icon": "zap",
        "allocation": {
            "stocks": 85,
            "bonds": 10,
            "cash": 5
        },
        "recommendations": [
            "Focus pe acțiuni de creștere și tehnologie",
            "Consideră piețe emergente pentru diversificare",
            "Poți aloca o mică parte (5-10%) în active alternative",
            "Folosește DCA pentru a reduce riscul de timing"
        ]
    }
}

class AssessmentAnswer(BaseModel):
    question_id: str
    answer_value: str

class AssessmentSubmission(BaseModel):
    answers: List[AssessmentAnswer]

@router.get("/questions")
async def get_questions():
    """Get all risk assessment questions"""
    return {
        "questions": QUESTIONS,
        "total_questions": len(QUESTIONS)
    }

@router.post("/submit")
async def submit_assessment(submission: AssessmentSubmission, user: dict = Depends(require_auth)):
    """Submit risk assessment and calculate profile"""
    db = await get_database()
    
    # Calculate score
    total_score = 0
    answers_detail = []
    
    for answer in submission.answers:
        question = next((q for q in QUESTIONS if q["id"] == answer.question_id), None)
        if not question:
            continue
        
        option = next((o for o in question["options"] if o["value"] == answer.answer_value), None)
        if option:
            total_score += option["score"]
            answers_detail.append({
                "question_id": answer.question_id,
                "question": question["question"],
                "answer": option["label"],
                "score": option["score"]
            })
    
    # Determine profile based on score
    max_score = len(QUESTIONS) * 3  # 21
    min_score = len(QUESTIONS) * 1  # 7
    
    # Score ranges: 7-11 conservative, 12-16 moderate, 17-21 aggressive
    if total_score <= 11:
        profile_key = "conservative"
    elif total_score <= 16:
        profile_key = "moderate"
    else:
        profile_key = "aggressive"
    
    profile = RISK_PROFILES[profile_key]
    
    # Save assessment
    assessment = {
        "id": f"assess_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "answers": answers_detail,
        "total_score": total_score,
        "max_score": max_score,
        "profile_key": profile_key,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.risk_assessments.insert_one(assessment)
    
    # Update user profile
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "risk_profile": profile_key,
            "risk_assessment_date": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "profile": {
            "key": profile_key,
            **profile
        },
        "score": total_score,
        "max_score": max_score,
        "answers": answers_detail
    }

@router.get("/my-profile")
async def get_my_profile(user: dict = Depends(require_auth)):
    """Get user's risk profile"""
    db = await get_database()
    
    # Get latest assessment
    assessment = await db.risk_assessments.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    
    if not assessment:
        return {
            "has_profile": False,
            "message": "Nu ai completat chestionarul de risc"
        }
    
    profile = RISK_PROFILES.get(assessment["profile_key"])
    
    return {
        "has_profile": True,
        "profile": {
            "key": assessment["profile_key"],
            **profile
        },
        "score": assessment["total_score"],
        "max_score": assessment["max_score"],
        "assessed_at": assessment["created_at"]
    }

@router.get("/profiles")
async def get_all_profiles():
    """Get all available risk profiles for reference"""
    return {
        "profiles": [
            {"key": k, **v} for k, v in RISK_PROFILES.items()
        ]
    }
