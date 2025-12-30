"""AI Trading Companion - "Verifică Înainte" pentru FinRomania"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import os
import logging
import uuid

from config.database import get_database
from routes.auth import require_auth, get_current_user_optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/companion", tags=["AI Trading Companion"])

# Try to import emergent integrations for AI
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    HAS_AI = True
except ImportError:
    HAS_AI = False
    logger.warning("AI integration not available for Trading Companion")


class CompanionRequest(BaseModel):
    symbol: str
    stock_name: Optional[str] = None
    current_price: Optional[float] = None
    change_percent: Optional[float] = None
    user_question: str
    user_level: Optional[str] = "incepator"  # incepator, intermediar, expert
    stock_type: Optional[str] = "bvb"  # bvb or global


class CompanionResponse(BaseModel):
    response: str
    disclaimer: str = "⚠️ Acest răspuns NU este un sfat financiar profesional. Consultă un specialist înainte de orice decizie de investiții."


# System prompt for the AI companion
COMPANION_SYSTEM_PROMPT = """Ești "Verifică Înainte" - un companion de trading pentru investitori români. 

ROLUL TĂU:
- NU ești un consilier financiar licențiat
- NU dai sfaturi de tipul "cumpără" sau "vinde"
- EȘTI un prieten care pune întrebări inteligente pentru a ajuta utilizatorul să gândească clar
- Scopul tău e să PREVII deciziile emoționale și pierderile

REGULI STRICTE:
1. NICIODATĂ nu zici "ar trebui să cumperi" sau "ar trebui să vinzi"
2. Întotdeauna pui ÎNTREBĂRI care fac utilizatorul să gândească
3. Evidențiezi RISCURILE pe care utilizatorul poate să nu le vadă
4. Adaptezi limbajul la nivelul utilizatorului (începător/intermediar/expert)
5. Răspunzi DOAR în română
6. Ești empatic - mulți au pierdut bani din decizii pripite
7. Folosești emoji-uri moderat pentru a fi prietenos

STRUCTURA RĂSPUNSULUI:
1. Recunoaște situația utilizatorului
2. Pune 2-3 întrebări cheie care îl fac să gândească
3. Menționează un risc potențial pe care poate nu l-a considerat
4. Încheie cu încurajare să ia decizia DUPĂ ce a răspuns la aceste întrebări

PENTRU ÎNCEPĂTORI - folosește limbaj simplu, explică termenii, pune întrebări de bază:
- "Ai stabilit cât poți pierde maxim fără să te afecteze?"
- "Ai alte investiții sau doar această acțiune?"
- "De ce vrei să cumperi acum și nu săptămâna viitoare?"

PENTRU INTERMEDIARI - întrebări mai tehnice:
- "Ai verificat volumul de tranzacționare?"
- "Care e strategia ta de ieșire (stop-loss)?"
- "Cum se încadrează asta în alocarea ta de portofoliu?"

PENTRU EXPERȚI - conversație de la egal la egal:
- "Ce indicatori tehnici ai analizat?"
- "Cum vezi raportul risc/recompensă?"
- "Ce catalizatori aștepți pe termen scurt/mediu?"
"""


async def get_companion_response(prompt: str, user_level: str = "incepator") -> str:
    """Get AI companion response"""
    if not HAS_AI:
        return "Serviciul AI nu este disponibil momentan. Dar amintește-ți: nu lua decizii bazate pe emoții! Gândește-te de ce vrei să faci această mișcare și care e planul tău dacă merge prost."
    
    api_key = os.environ.get("EMERGENT_UNIVERSAL_KEY")
    if not api_key:
        return "Configurare AI lipsă. Între timp, întreabă-te: ai un plan clar? Știi cât poți pierde maxim?"
    
    try:
        session_id = f"companion_{uuid.uuid4().hex[:8]}"
        
        # Customize system prompt based on user level
        level_context = {
            "incepator": "\n\nUTILIZATORUL ESTE ÎNCEPĂTOR - folosește limbaj foarte simplu, explică orice termen tehnic, fii foarte protector.",
            "intermediar": "\n\nUTILIZATORUL ESTE INTERMEDIAR - poate înțelege termeni de bază, dar verifică să nu facă greșeli din încredere excesivă.",
            "expert": "\n\nUTILIZATORUL ESTE EXPERT - poți folosi termeni tehnici, dar tot verifică să nu fie sub influența emoțiilor."
        }
        
        system_msg = COMPANION_SYSTEM_PROMPT + level_context.get(user_level, level_context["incepator"])
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_msg
        )
        
        user_msg = UserMessage(text=prompt)
        response = await chat.send_message(user_msg)
        return response
    except Exception as e:
        logger.error(f"AI Companion error: {e}")
        return "Nu am putut genera răspunsul. Dar ține minte: înainte de orice decizie, întreabă-te - care e planul meu dacă merge prost?"


@router.post("/ask", response_model=CompanionResponse)
async def ask_companion(
    request: CompanionRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    Ask the AI Trading Companion for guidance
    Works for both logged-in and anonymous users
    """
    try:
        # Build context for AI
        stock_context = f"""
CONTEXT ACȚIUNE:
- Simbol: {request.symbol}
- Nume: {request.stock_name or 'Necunoscut'}
- Preț curent: {request.current_price or 'Necunoscut'} {'RON' if request.stock_type == 'bvb' else 'USD'}
- Variație: {'+' if (request.change_percent or 0) >= 0 else ''}{request.change_percent or 0}%
- Tip: {'Acțiune BVB' if request.stock_type == 'bvb' else 'Activ Global'}

ÎNTREBAREA UTILIZATORULUI:
{request.user_question}
"""
        
        # Get user level from their profile if logged in
        user_level = request.user_level
        if current_user:
            try:
                db = await get_database()
                profile = await db.risk_profiles.find_one(
                    {"user_id": current_user.get("user_id")},
                    {"_id": 0}
                )
                if profile:
                    risk_score = profile.get("risk_score", 50)
                    if risk_score < 30:
                        user_level = "incepator"
                    elif risk_score < 70:
                        user_level = "intermediar"
                    else:
                        user_level = "expert"
            except Exception:
                pass
        
        # Get AI response
        response = await get_companion_response(stock_context, user_level)
        
        # Log interaction (anonymized for non-logged users)
        try:
            db = await get_database()
            await db.companion_interactions.insert_one({
                "user_id": current_user.get("user_id") if current_user else None,
                "symbol": request.symbol,
                "stock_type": request.stock_type,
                "question": request.user_question[:500],  # Limit stored question
                "user_level": user_level,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "anonymous": current_user is None
            })
            
            # Increment AI credits used for logged-in users
            if current_user and current_user.get("user_id"):
                await db.users.update_one(
                    {"user_id": current_user.get("user_id")},
                    {"$inc": {"ai_credits_used": 1}}
                )
                
                # Also log to AI usage collection for detailed tracking
                await db.ai_usage_logs.insert_one({
                    "user_id": current_user.get("user_id"),
                    "email": current_user.get("email"),
                    "feature": "trading_companion",
                    "symbol": request.symbol,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "credits_used": 1
                })
        except Exception:
            pass  # Don't fail if logging fails
        
        return CompanionResponse(response=response)
        
    except Exception as e:
        logger.error(f"Companion error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Nu am putut procesa cererea. Încearcă din nou."
        )


@router.get("/tips/{symbol}")
async def get_quick_tips(
    symbol: str,
    stock_type: str = "bvb",
    change_percent: float = 0
):
    """
    Get quick tips based on stock situation
    No auth required - available to everyone
    """
    tips = []
    
    # Tips based on price movement
    if change_percent <= -5:
        tips.append("📉 Acțiunea a scăzut semnificativ. Întreabă-te: e o oportunitate sau un semn de avertizare?")
        tips.append("⚠️ Nu cumpăra doar pentru că 'e ieftin'. Verifică DE CE a scăzut.")
    elif change_percent >= 5:
        tips.append("📈 Creștere mare! Atenție la FOMO - nu cumpăra doar pentru că vezi verde.")
        tips.append("🤔 Dacă a crescut mult, poate ai ratat momentul. Sau poate e doar începutul?")
    elif abs(change_percent) < 1:
        tips.append("➡️ Piață calmă pentru această acțiune. Moment bun pentru analiză, nu pentru decizii rapide.")
    
    # General tips
    tips.append("💡 Ai un plan de ieșire înainte să intri?")
    tips.append("📊 Diversificarea reduce riscul. Nu pune totul pe o singură acțiune.")
    
    return {
        "symbol": symbol,
        "tips": tips[:3],  # Return max 3 tips
        "cta": "Vrei să discutăm mai în detaliu? Întreabă-mă orice!"
    }
