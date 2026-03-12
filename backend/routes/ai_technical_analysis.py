"""AI Technical Analysis pentru FinRomania PRO"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
import os
import logging
import numpy as np

from config.database import get_database
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai-analysis", tags=["AI Analysis"])

# Try to import emergent integrations for AI
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    HAS_AI = True
except ImportError:
    HAS_AI = False
    logger.warning("AI integration not available for technical analysis")


class AnalysisRequest(BaseModel):
    symbol: str
    period: str = "1m"  # 1w, 1m, 3m, 6m, 1y


def calculate_support_resistance(prices: List[float], window: int = 5) -> Dict:
    """Calculate support and resistance levels using local min/max"""
    if len(prices) < window * 2:
        return {"support": None, "resistance": None}
    
    supports = []
    resistances = []
    
    for i in range(window, len(prices) - window):
        # Local minimum = support
        if prices[i] == min(prices[i-window:i+window+1]):
            supports.append(prices[i])
        # Local maximum = resistance
        if prices[i] == max(prices[i-window:i+window+1]):
            resistances.append(prices[i])
    
    # Get most recent/relevant levels
    support = round(np.mean(supports[-3:]), 2) if supports else min(prices)
    resistance = round(np.mean(resistances[-3:]), 2) if resistances else max(prices)
    
    return {
        "support": support,
        "resistance": resistance,
        "support_levels": sorted(set([round(s, 2) for s in supports[-5:]]))[:3],
        "resistance_levels": sorted(set([round(r, 2) for r in resistances[-5:]]), reverse=True)[:3]
    }


def calculate_moving_averages(prices: List[float]) -> Dict:
    """Calculate common moving averages"""
    result = {}
    
    if len(prices) >= 20:
        result["ma20"] = round(np.mean(prices[-20:]), 2)
    if len(prices) >= 50:
        result["ma50"] = round(np.mean(prices[-50:]), 2)
    if len(prices) >= 200:
        result["ma200"] = round(np.mean(prices[-200:]), 2)
    
    return result


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """Calculate RSI (Relative Strength Index)"""
    if len(prices) < period + 1:
        return None
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 1)


def determine_trend(prices: List[float], ma20: float = None, ma50: float = None) -> Dict:
    """Determine trend direction and strength"""
    if len(prices) < 5:
        return {"direction": "neutral", "strength": 0}
    
    current_price = prices[-1]
    
    # Short-term trend (last 5 days)
    short_trend = (prices[-1] - prices[-5]) / prices[-5] * 100 if len(prices) >= 5 else 0
    
    # Medium-term trend (last 20 days)
    medium_trend = (prices[-1] - prices[-20]) / prices[-20] * 100 if len(prices) >= 20 else short_trend
    
    # Determine direction
    if short_trend > 1 and medium_trend > 2:
        direction = "bullish"
        strength = min(abs(medium_trend) / 5, 1)  # 0-1 scale
    elif short_trend < -1 and medium_trend < -2:
        direction = "bearish"
        strength = min(abs(medium_trend) / 5, 1)
    else:
        direction = "neutral"
        strength = 0.3
    
    # MA confirmation
    if ma20 and ma50:
        if current_price > ma20 > ma50:
            if direction == "bullish":
                strength = min(strength + 0.2, 1)
        elif current_price < ma20 < ma50:
            if direction == "bearish":
                strength = min(strength + 0.2, 1)
    
    return {
        "direction": direction,
        "strength": round(strength, 2),
        "short_term_change": round(short_trend, 2),
        "medium_term_change": round(medium_trend, 2)
    }


def generate_signal(rsi: float, trend: Dict, current_price: float, support: float, resistance: float) -> Dict:
    """Generate trading signal based on technical indicators"""
    score = 50  # Neutral starting point
    reasons = []
    
    # RSI analysis
    if rsi:
        if rsi < 30:
            score += 20
            reasons.append(f"RSI supravândut ({rsi})")
        elif rsi > 70:
            score -= 20
            reasons.append(f"RSI supracumpărat ({rsi})")
        elif rsi < 45:
            score += 10
            reasons.append(f"RSI favorabil ({rsi})")
        elif rsi > 55:
            score -= 10
            reasons.append(f"RSI ridicat ({rsi})")
    
    # Trend analysis
    if trend["direction"] == "bullish":
        score += int(trend["strength"] * 20)
        reasons.append(f"Trend ascendent ({trend['strength']*100:.0f}% putere)")
    elif trend["direction"] == "bearish":
        score -= int(trend["strength"] * 20)
        reasons.append(f"Trend descendent ({trend['strength']*100:.0f}% putere)")
    
    # Support/Resistance proximity
    if support and resistance:
        range_size = resistance - support
        if range_size > 0:
            position = (current_price - support) / range_size
            if position < 0.2:  # Near support
                score += 15
                reasons.append("Aproape de suport")
            elif position > 0.8:  # Near resistance
                score -= 15
                reasons.append("Aproape de rezistență")
    
    # Determine signal
    if score >= 70:
        signal = "CUMPĂRĂ"
        signal_color = "green"
    elif score >= 55:
        signal = "CUMPĂRĂ MODERAT"
        signal_color = "lightgreen"
    elif score <= 30:
        signal = "VINDE"
        signal_color = "red"
    elif score <= 45:
        signal = "VINDE MODERAT"
        signal_color = "orange"
    else:
        signal = "PĂSTREAZĂ"
        signal_color = "gray"
    
    return {
        "signal": signal,
        "signal_color": signal_color,
        "confidence": min(abs(score - 50) * 2, 100),
        "score": score,
        "reasons": reasons
    }


AI_ANALYSIS_PROMPT = """Tu ești un analist tehnic profesionist pentru piața de capital din România (BVB).
Analizează următoarele date tehnice și oferă o interpretare CONCISĂ și UTILĂ pentru investitori.

DATELE TEHNICE:
- Simbol: {symbol}
- Preț curent: {current_price} RON
- Perioadă analizată: {period}

INDICATORI:
- Suport: {support} RON
- Rezistență: {resistance} RON
- RSI (14): {rsi}
- MA20: {ma20} RON
- MA50: {ma50} RON
- Trend: {trend_direction} (putere: {trend_strength}%)
- Variație pe termen scurt: {short_change}%
- Variație pe termen mediu: {medium_change}%

SEMNAL GENERAT: {signal} (încredere: {confidence}%)
Motive: {reasons}

INSTRUCȚIUNI:
1. Scrie în română, maxim 150 cuvinte
2. Explică în termeni simpli ce indică datele
3. Menționează nivelurile cheie de urmărit
4. Oferă un sfat practic (dar nu garantat)
5. Adaugă un disclaimer scurt că nu e sfat financiar

Răspunde DIRECT, fără introduceri."""


async def generate_ai_interpretation(analysis_data: Dict) -> str:
    """Generate AI interpretation of technical analysis"""
    if not HAS_AI:
        return "Interpretarea AI nu este disponibilă momentan."
    
    api_key = os.environ.get("EMERGENT_UNIVERSAL_KEY")
    if not api_key:
        return "Configurare AI lipsă."
    
    try:
        import uuid
        session_id = f"analysis_{uuid.uuid4().hex[:8]}"
        
        prompt = AI_ANALYSIS_PROMPT.format(
            symbol=analysis_data.get("symbol", "N/A"),
            current_price=analysis_data.get("current_price", "N/A"),
            period=analysis_data.get("period", "1 lună"),
            support=analysis_data.get("support", "N/A"),
            resistance=analysis_data.get("resistance", "N/A"),
            rsi=analysis_data.get("rsi", "N/A"),
            ma20=analysis_data.get("ma20", "N/A"),
            ma50=analysis_data.get("ma50", "N/A"),
            trend_direction=analysis_data.get("trend_direction", "neutru"),
            trend_strength=analysis_data.get("trend_strength", 0),
            short_change=analysis_data.get("short_change", 0),
            medium_change=analysis_data.get("medium_change", 0),
            signal=analysis_data.get("signal", "PĂSTREAZĂ"),
            confidence=analysis_data.get("confidence", 50),
            reasons=", ".join(analysis_data.get("reasons", []))
        )
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message="Ești un analist tehnic pentru BVB. Răspunzi concis în română."
        )
        
        response = await chat.send_message(UserMessage(text=prompt))
        return response
        
    except Exception as e:
        logger.error(f"AI interpretation error: {e}")
        return "Nu am putut genera interpretarea AI. Te rog încearcă din nou."


@router.post("/analyze")
async def analyze_stock(request: AnalysisRequest, user: dict = Depends(require_auth)):
    """
    PRO Feature: AI Technical Analysis for BVB stocks
    Calculates technical indicators and generates AI interpretation
    """
    # Check PRO subscription
    if user.get("subscription_level") not in ["pro", "premium"]:
        raise HTTPException(
            status_code=403,
            detail="Analiza AI necesită abonament PRO. Upgrade pentru acces."
        )
    
    try:
        db = await get_database()
        
        # Get historical data
        period_days = {
            "1w": 7, "1m": 30, "3m": 90, "6m": 180, "1y": 365
        }
        days = period_days.get(request.period, 30)
        
        # Fetch from stocks_history or use EODHD
        from apis.eodhd_client import get_eodhd_client
        eodhd = get_eodhd_client()
        
        history = await eodhd.get_stock_history(request.symbol, days=days)
        
        if not history or len(history) < 5:
            raise HTTPException(status_code=404, detail=f"Nu sunt suficiente date pentru {request.symbol}")
        
        # Extract closing prices
        prices = [h["close"] for h in history if h.get("close")]
        current_price = prices[-1] if prices else 0
        
        # Calculate indicators
        sr_levels = calculate_support_resistance(prices)
        mas = calculate_moving_averages(prices)
        rsi = calculate_rsi(prices)
        trend = determine_trend(prices, mas.get("ma20"), mas.get("ma50"))
        signal = generate_signal(
            rsi, trend, current_price,
            sr_levels["support"], sr_levels["resistance"]
        )
        
        # Prepare analysis data
        analysis_data = {
            "symbol": request.symbol,
            "current_price": current_price,
            "period": f"{days} zile",
            "support": sr_levels["support"],
            "resistance": sr_levels["resistance"],
            "support_levels": sr_levels["support_levels"],
            "resistance_levels": sr_levels["resistance_levels"],
            "rsi": rsi,
            "ma20": mas.get("ma20"),
            "ma50": mas.get("ma50"),
            "ma200": mas.get("ma200"),
            "trend_direction": trend["direction"],
            "trend_strength": round(trend["strength"] * 100),
            "short_change": trend["short_term_change"],
            "medium_change": trend["medium_term_change"],
            "signal": signal["signal"],
            "signal_color": signal["signal_color"],
            "confidence": signal["confidence"],
            "reasons": signal["reasons"]
        }
        
        # Generate AI interpretation
        ai_interpretation = await generate_ai_interpretation(analysis_data)
        
        # Log usage
        await db.ai_analysis_logs.insert_one({
            "user_id": user.get("user_id"),
            "symbol": request.symbol,
            "period": request.period,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "success": True,
            "symbol": request.symbol,
            "analysis": analysis_data,
            "ai_interpretation": ai_interpretation,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error for {request.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage")
async def get_analysis_usage(user: dict = Depends(require_auth)):
    """Get user's AI analysis usage stats"""
    db = await get_database()
    
    # Count today's analyses
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = await db.ai_analysis_logs.count_documents({
        "user_id": user.get("user_id"),
        "timestamp": {"$gte": today.isoformat()}
    })
    
    # Total analyses
    total_count = await db.ai_analysis_logs.count_documents({
        "user_id": user.get("user_id")
    })
    
    return {
        "today": today_count,
        "total": total_count,
        "is_pro": user.get("subscription_level") in ["pro", "premium"]
    }
