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

from utils.llm import LlmChat, UserMessage
HAS_AI = True


class AnalysisRequest(BaseModel):
    symbol: str
    period: str = "1m"  # 1w, 1m, 3m, 6m, 1y


def calculate_support_resistance(prices: List[float], window: int = 5) -> Dict:
    """Calculate support and resistance levels using local min/max"""
    if len(prices) < window * 2:
        return {"support": None, "resistance": None, "support_levels": [], "resistance_levels": []}
    
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


def analyze_volume(volumes: List[int], current_volume: int) -> Dict:
    """Analyze volume patterns - CRUCIAL for BVB"""
    if not volumes or len(volumes) < 5:
        return {"status": "insufficient_data"}
    
    avg_volume = np.mean(volumes)
    avg_volume_20 = np.mean(volumes[-20:]) if len(volumes) >= 20 else avg_volume
    
    # Volume ratio (current vs average)
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
    volume_ratio_20 = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
    
    # Detect volume spikes (days with 2x+ average volume)
    volume_spikes = sum(1 for v in volumes[-10:] if v > avg_volume * 2)
    
    # Volume trend (increasing or decreasing)
    if len(volumes) >= 10:
        recent_avg = np.mean(volumes[-5:])
        older_avg = np.mean(volumes[-10:-5])
        volume_trend = "crescător" if recent_avg > older_avg * 1.2 else "descrescător" if recent_avg < older_avg * 0.8 else "stabil"
    else:
        volume_trend = "stabil"
    
    # Determine volume status
    if volume_ratio >= 3:
        status = "FOARTE_MARE"
        alert = "⚠️ Volum excepțional! Verifică știrile!"
    elif volume_ratio >= 2:
        status = "MARE"
        alert = "📈 Volum semnificativ peste medie"
    elif volume_ratio >= 1.5:
        status = "PESTE_MEDIE"
        alert = "Volum ușor peste medie"
    elif volume_ratio <= 0.5:
        status = "FOARTE_MIC"
        alert = "⚠️ Volum foarte mic - lichiditate redusă!"
    elif volume_ratio <= 0.7:
        status = "MIC"
        alert = "Volum sub medie"
    else:
        status = "NORMAL"
        alert = "Volum în parametri normali"
    
    return {
        "current": int(current_volume),
        "average": int(round(avg_volume)),
        "average_20d": int(round(avg_volume_20)),
        "ratio": float(round(volume_ratio, 2)),
        "ratio_20d": float(round(volume_ratio_20, 2)),
        "status": status,
        "alert": alert,
        "trend": volume_trend,
        "spikes_10d": int(volume_spikes),
        "is_confirmation": bool(volume_ratio >= 1.2)  # Volume confirms price movement
    }


def calculate_liquidity_score(avg_volume: float, avg_value: float, spread_estimate: float = None) -> Dict:
    """Calculate liquidity score for BVB stocks"""
    # BVB liquidity tiers based on average daily volume
    if avg_volume >= 100000:
        tier = "FOARTE_LICHIDĂ"
        score = 5
        description = "Poți intra/ieși ușor cu sume mari"
    elif avg_volume >= 50000:
        tier = "LICHIDĂ"
        score = 4
        description = "Lichiditate bună pentru majoritatea investitorilor"
    elif avg_volume >= 20000:
        tier = "MEDIE"
        score = 3
        description = "OK pentru sume moderate, atenție la ordine mari"
    elif avg_volume >= 5000:
        tier = "SCĂZUTĂ"
        score = 2
        description = "⚠️ Lichiditate redusă, spread poate fi mare"
    else:
        tier = "FOARTE_SCĂZUTĂ"
        score = 1
        description = "⚠️ Foarte greu de tranzacționat, risc mare"
    
    return {
        "tier": tier,
        "score": score,
        "max_score": 5,
        "description": description,
        "avg_daily_volume": round(avg_volume),
        "recommendation": "OK" if score >= 3 else "ATENȚIE" if score == 2 else "EVITĂ"
    }


async def get_market_context(db) -> Dict:
    """Get overall BVB market context (BET index, sentiment)"""
    try:
        # Try to get BET index data first
        bet_data = await db.indices_bvb.find_one({"symbol": "BET"}, {"_id": 0})
        
        bet_change = None
        
        if bet_data and bet_data.get("change_percent") is not None:
            bet_change = bet_data.get("change_percent", 0)
        else:
            # Fallback: Calculate market sentiment from all BVB stocks average
            cursor = db.stocks_bvb.find({}, {"_id": 0, "change_percent": 1, "symbol": 1})
            stocks = await cursor.to_list(length=100)
            
            if stocks:
                changes = [s.get("change_percent", 0) for s in stocks if s.get("change_percent") is not None]
                if changes:
                    bet_change = sum(changes) / len(changes)
                    logger.info(f"Calculated market avg from {len(changes)} stocks: {bet_change:.2f}%")
        
        if bet_change is not None:
            bet_change = round(bet_change, 2)
            
            if bet_change >= 1.5:
                sentiment = "FOARTE_BULLISH"
                description = "Piața BVB e în creștere puternică"
            elif bet_change >= 0.5:
                sentiment = "BULLISH"
                description = "Piața BVB e pozitivă"
            elif bet_change <= -1.5:
                sentiment = "FOARTE_BEARISH"
                description = "Piața BVB e în scădere puternică"
            elif bet_change <= -0.5:
                sentiment = "BEARISH"
                description = "Piața BVB e negativă"
            else:
                sentiment = "NEUTRU"
                description = "Piața BVB e stabilă"
            
            return {
                "bet_value": bet_data.get("value") if bet_data else None,
                "bet_change": bet_change,
                "sentiment": sentiment,
                "description": description,
                "recommendation": "Contextul favorizează cumpărarea" if bet_change > 0.3 else "Contextul favorizează prudența" if bet_change < -0.3 else "Context neutru"
            }
    except Exception as e:
        logger.error(f"Error getting market context: {e}")
    
    return {
        "bet_change": 0,
        "sentiment": "NEUTRU",
        "description": "Date piață indisponibile momentan"
    }


def analyze_price_action(prices: List[float], volumes: List[int]) -> Dict:
    """Analyze price action patterns with volume confirmation"""
    if len(prices) < 5 or len(volumes) < 5:
        return {"pattern": "insufficient_data"}
    
    # Last 5 days analysis
    last_5_prices = prices[-5:]
    last_5_volumes = volumes[-5:]
    avg_volume = np.mean(volumes)
    
    # Detect patterns
    patterns = []
    
    # Higher highs and higher lows (uptrend)
    if all(last_5_prices[i] >= last_5_prices[i-1] * 0.99 for i in range(1, 5)):
        patterns.append("TREND_ASCENDENT")
    
    # Lower highs and lower lows (downtrend)
    if all(last_5_prices[i] <= last_5_prices[i-1] * 1.01 for i in range(1, 5)):
        patterns.append("TREND_DESCENDENT")
    
    # Volume spike with price increase (accumulation)
    if last_5_volumes[-1] > avg_volume * 1.5 and last_5_prices[-1] > last_5_prices[-2]:
        patterns.append("ACUMULARE")
    
    # Volume spike with price decrease (distribution)
    if last_5_volumes[-1] > avg_volume * 1.5 and last_5_prices[-1] < last_5_prices[-2]:
        patterns.append("DISTRIBUȚIE")
    
    # Breakout detection
    max_20 = max(prices[-20:]) if len(prices) >= 20 else max(prices)
    min_20 = min(prices[-20:]) if len(prices) >= 20 else min(prices)
    current = prices[-1]
    
    if current >= max_20 * 0.98:
        patterns.append("APROAPE_DE_MAXIM")
    if current <= min_20 * 1.02:
        patterns.append("APROAPE_DE_MINIM")
    
    # Volume-price divergence
    price_up = prices[-1] > prices[-3]
    volume_up = volumes[-1] > np.mean(volumes[-5:])
    
    if price_up and not volume_up:
        patterns.append("DIVERGENȚĂ_VOLUM")  # Price up but volume down = weak move
    
    return {
        "patterns": patterns,
        "last_5_trend": "UP" if last_5_prices[-1] > last_5_prices[0] else "DOWN",
        "volume_confirms": bool(volume_up if price_up else not volume_up),
        "near_high": bool(current >= max_20 * 0.95),
        "near_low": bool(current <= min_20 * 1.05)
    }


def calculate_moving_averages(prices: List[float]) -> Dict:
    """Calculate common moving averages"""
    result = {}
    
    if len(prices) >= 20:
        result["ma20"] = float(round(np.mean(prices[-20:]), 2))
    if len(prices) >= 50:
        result["ma50"] = float(round(np.mean(prices[-50:]), 2))
    if len(prices) >= 200:
        result["ma200"] = float(round(np.mean(prices[-200:]), 2))
    
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
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return float(round(rsi, 1))


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
        "strength": float(round(strength, 2)),
        "short_term_change": float(round(short_trend, 2)),
        "medium_term_change": float(round(medium_trend, 2))
    }


def generate_signal(rsi: float, trend: Dict, current_price: float, support: float, resistance: float, volume_data: Dict = None, market_context: Dict = None) -> Dict:
    """Generate trading signal based on ALL technical indicators"""
    score = 50  # Neutral starting point
    reasons = []
    warnings = []
    
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
    
    # VOLUME analysis - CRUCIAL for BVB!
    if volume_data:
        vol_ratio = volume_data.get("ratio", 1)
        vol_status = volume_data.get("status", "NORMAL")
        
        # Volume confirms trend
        if volume_data.get("is_confirmation"):
            if trend["direction"] == "bullish":
                score += 10
                reasons.append("Volum confirmă creșterea")
            elif trend["direction"] == "bearish":
                score -= 10
                reasons.append("Volum confirmă scăderea")
        else:
            # Volume divergence warning
            if trend["direction"] != "neutral":
                warnings.append("⚠️ Volumul NU confirmă mișcarea de preț")
        
        # Volume spike alerts
        if vol_status == "FOARTE_MARE":
            warnings.append("🔔 Volum excepțional - verifică știrile!")
        elif vol_status == "FOARTE_MIC":
            score -= 5
            warnings.append("⚠️ Lichiditate foarte scăzută")
    
    # MARKET CONTEXT - BET index sentiment
    if market_context:
        sentiment = market_context.get("sentiment", "NEUTRU")
        bet_change = market_context.get("bet_change", 0)
        
        if sentiment in ["FOARTE_BULLISH", "BULLISH"]:
            score += 5
            reasons.append(f"Piață pozitivă (BET {bet_change:+.1f}%)")
        elif sentiment in ["FOARTE_BEARISH", "BEARISH"]:
            score -= 5
            reasons.append(f"Piață negativă (BET {bet_change:+.1f}%)")
    
    # Determine signal - NEUTRAL terminology (not investment advice)
    if score >= 70:
        signal = "FOARTE FAVORABIL"
        signal_color = "green"
    elif score >= 55:
        signal = "FAVORABIL"
        signal_color = "lightgreen"
    elif score <= 30:
        signal = "FOARTE RISCANT"
        signal_color = "red"
    elif score <= 45:
        signal = "RISCANT"
        signal_color = "orange"
    else:
        signal = "NEUTRU"
        signal_color = "gray"
    
    return {
        "signal": signal,
        "signal_color": signal_color,
        "confidence": int(min(abs(score - 50) * 2, 100)),
        "score": int(score),
        "reasons": reasons,
        "warnings": warnings
    }


AI_ANALYSIS_PROMPT = """Ești un analist tehnic profesionist pentru BVB (Bursa de Valori București). 
Analizează TOATE datele de mai jos și oferă o SINTEZĂ completă, profesionistă.

IMPORTANT: NU da recomandări de CUMPĂRARE sau VÂNZARE! Folosește doar termeni neutri precum:
- "Favorabil" sau "Accesibil" pentru situații pozitive
- "Riscant" sau "Prudență recomandată" pentru situații negative
- "Neutru" pentru situații echilibrate

═══════════════════════════════════════════
📊 ACȚIUNE: {symbol}
═══════════════════════════════════════════
• Preț curent: {current_price} RON
• Perioadă analizată: {period}

📈 INDICATORI TEHNICI:
• Suport: {support} RON | Rezistență: {resistance} RON
• RSI (14): {rsi} {rsi_status}
• MA20: {ma20} RON | MA50: {ma50} RON
• Trend: {trend_direction} (putere {trend_strength}%)
• Variație 5 zile: {short_change}% | Variație 20 zile: {medium_change}%

📊 ANALIZA VOLUMULUI (CRUCIAL!):
• Volum curent: {volume_current} acțiuni
• Media zilnică: {volume_avg} acțiuni
• Raport: {volume_ratio}x față de medie
• Status: {volume_status}
• Trend volum: {volume_trend}
• {volume_alert}

🏛️ CONTEXT PIAȚĂ BVB:
• Indicele BET: {bet_change}%
• Sentiment: {market_sentiment}
• {market_description}

📉 PRICE ACTION:
• Pattern-uri detectate: {patterns}
• Aproape de maxim 20 zile: {near_high}
• Aproape de minim 20 zile: {near_low}
• Volumul confirmă prețul: {volume_confirms}

💧 LICHIDITATE:
• Scor: {liquidity_score}/5
• Clasificare: {liquidity_tier}
• {liquidity_description}

⚡ EVALUARE ALGORITMICĂ: {signal} (încredere {confidence}%)
Factori pozitivi/negativi: {reasons}
Avertismente: {warnings}

═══════════════════════════════════════════
INSTRUCȚIUNI DE RĂSPUNS:
═══════════════════════════════════════════
1. Analizează TOȚI indicatorii ÎMPREUNĂ (RSI + MA + Trend + Volum + Context)
2. VOLUMUL e crucial pe BVB! O mișcare fără volum = slabă/falsă
3. Identifică CONFLUENȚA: când mai mulți indicatori arată același lucru
4. Menționează:
   - Ce face situația favorabilă sau riscantă
   - Ce trebuie urmărit/monitorizat
   - RISCURI specifice (lichiditate, divergențe)
5. Oferă NIVELURI de interes: "Nivel favorabil sub X RON, zonă de rezistență la Y RON"
6. Concluzie clară în 2-3 propoziții despre evaluarea riscului
7. Disclaimer: "Aceasta este o analiză tehnică educativă, NU o recomandare de investiții."

Scrie în română, maxim 250 cuvinte, stil direct și profesionist.
NU folosi cuvintele "cumpără", "vinde", "recomand"!"""


async def generate_ai_interpretation(analysis_data: Dict) -> str:
    """Generate AI interpretation of technical analysis"""
    if not HAS_AI:
        return "Interpretarea AI nu este disponibilă momentan."
    
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_UNIVERSAL_KEY")
    if not api_key:
        return "Configurare AI lipsă."
    
    try:
        import uuid
        session_id = f"analysis_{uuid.uuid4().hex[:8]}"
        
        # Determine RSI status
        rsi = analysis_data.get("rsi")
        if rsi:
            if rsi < 30:
                rsi_status = "(SUPRAVÂNDUT - potențial de creștere)"
            elif rsi > 70:
                rsi_status = "(SUPRACUMPĂRAT - risc de corecție)"
            elif rsi < 40:
                rsi_status = "(zona de cumpărare)"
            elif rsi > 60:
                rsi_status = "(zona de vânzare)"
            else:
                rsi_status = "(neutru)"
        else:
            rsi_status = ""
        
        prompt = AI_ANALYSIS_PROMPT.format(
            symbol=analysis_data.get("symbol", "N/A"),
            current_price=analysis_data.get("current_price", "N/A"),
            period=analysis_data.get("period", "1 lună"),
            support=analysis_data.get("support", "N/A"),
            resistance=analysis_data.get("resistance", "N/A"),
            rsi=analysis_data.get("rsi", "N/A"),
            rsi_status=rsi_status,
            ma20=analysis_data.get("ma20", "N/A"),
            ma50=analysis_data.get("ma50", "N/A"),
            trend_direction=analysis_data.get("trend_direction", "neutru"),
            trend_strength=analysis_data.get("trend_strength", 0),
            short_change=analysis_data.get("short_change", 0),
            medium_change=analysis_data.get("medium_change", 0),
            # Volume data
            volume_current=analysis_data.get("volume_current", "N/A"),
            volume_avg=analysis_data.get("volume_avg", "N/A"),
            volume_ratio=analysis_data.get("volume_ratio", "N/A"),
            volume_status=analysis_data.get("volume_status", "N/A"),
            volume_trend=analysis_data.get("volume_trend", "N/A"),
            volume_alert=analysis_data.get("volume_alert", ""),
            # Market context
            bet_change=analysis_data.get("bet_change", "N/A"),
            market_sentiment=analysis_data.get("market_sentiment", "N/A"),
            market_description=analysis_data.get("market_description", ""),
            # Price action
            patterns=", ".join(analysis_data.get("patterns", [])) or "Niciun pattern clar",
            near_high="DA" if analysis_data.get("near_high") else "NU",
            near_low="DA" if analysis_data.get("near_low") else "NU",
            volume_confirms="DA ✓" if analysis_data.get("volume_confirms") else "NU ⚠️",
            # Liquidity
            liquidity_score=analysis_data.get("liquidity_score", "N/A"),
            liquidity_tier=analysis_data.get("liquidity_tier", "N/A"),
            liquidity_description=analysis_data.get("liquidity_description", ""),
            # Signal
            signal=analysis_data.get("signal", "PĂSTREAZĂ"),
            confidence=analysis_data.get("confidence", 50),
            reasons=", ".join(analysis_data.get("reasons", [])),
            warnings=", ".join(analysis_data.get("warnings", [])) or "Niciun avertisment"
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
            "1w": 10, "1m": 35, "3m": 100, "6m": 200, "1y": 400
        }
        days = period_days.get(request.period, 35)
        
        # Fetch from EODHD
        from apis.eodhd_client import get_eodhd_client
        eodhd = get_eodhd_client()
        
        history = await eodhd.get_historical_data(request.symbol, days=days)
        
        if not history or len(history) < 5:
            raise HTTPException(status_code=404, detail=f"Nu sunt suficiente date pentru {request.symbol}")
        
        # Extract closing prices and volumes
        prices = [h["close"] for h in history if h.get("close")]
        volumes = [h.get("volume", 0) for h in history]
        current_price = prices[-1] if prices else 0
        current_volume = volumes[-1] if volumes else 0
        
        # Calculate ALL indicators
        sr_levels = calculate_support_resistance(prices)
        mas = calculate_moving_averages(prices)
        rsi = calculate_rsi(prices)
        trend = determine_trend(prices, mas.get("ma20"), mas.get("ma50"))
        
        # NEW: Volume analysis
        volume_data = analyze_volume(volumes, current_volume)
        
        # NEW: Liquidity score
        avg_volume = np.mean(volumes) if volumes else 0
        avg_value = avg_volume * current_price if current_price else 0
        liquidity = calculate_liquidity_score(avg_volume, avg_value)
        
        # NEW: Market context (BET index)
        market_context = await get_market_context(db)
        
        # NEW: Price action patterns
        price_action = analyze_price_action(prices, volumes)
        
        # Generate signal with ALL data
        signal = generate_signal(
            rsi, trend, current_price,
            sr_levels["support"], sr_levels["resistance"],
            volume_data, market_context
        )
        
        # Prepare comprehensive analysis data
        analysis_data = {
            "symbol": request.symbol,
            "current_price": current_price,
            "period": f"{days} zile",
            # Technical indicators
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
            # Volume analysis
            "volume_current": volume_data.get("current"),
            "volume_avg": volume_data.get("average"),
            "volume_ratio": volume_data.get("ratio"),
            "volume_status": volume_data.get("status"),
            "volume_trend": volume_data.get("trend"),
            "volume_alert": volume_data.get("alert"),
            "volume_confirms": price_action.get("volume_confirms"),
            # Market context
            "bet_change": market_context.get("bet_change"),
            "market_sentiment": market_context.get("sentiment"),
            "market_description": market_context.get("description"),
            # Price action
            "patterns": price_action.get("patterns", []),
            "near_high": price_action.get("near_high"),
            "near_low": price_action.get("near_low"),
            # Liquidity
            "liquidity_score": liquidity.get("score"),
            "liquidity_tier": liquidity.get("tier"),
            "liquidity_description": liquidity.get("description"),
            # Signal
            "signal": signal["signal"],
            "signal_color": signal["signal_color"],
            "confidence": signal["confidence"],
            "reasons": signal["reasons"],
            "warnings": signal.get("warnings", [])
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
