"""Fear & Greed Index pentru piața BVB"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import logging
from config.database import get_database
from apis.eodhd_client import get_eodhd_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/market", tags=["market-sentiment"])

# BET Index components (cele mai lichide acțiuni BVB)
BET_COMPONENTS = ["TLV", "H2O", "SNP", "FP", "BRD", "SNG", "SNN", "TGN", "DIGI", "ONE", "EL", "M"]


async def calculate_rsi_component(eodhd_client) -> Dict:
    """
    RSI Component (0-100 points)
    RSI < 30 = Extreme Fear (0-20 points)
    RSI 30-40 = Fear (20-40 points)
    RSI 40-60 = Neutral (40-60 points)
    RSI 60-70 = Greed (60-80 points)
    RSI > 70 = Extreme Greed (80-100 points)
    """
    try:
        import httpx
        import os
        
        api_key = os.environ.get("EODHD_API_KEY")
        if not api_key:
            return {"score": 50, "label": "Neutru", "details": "API key missing"}
        
        rsi_values = []
        async with httpx.AsyncClient() as client:
            for symbol in BET_COMPONENTS[:5]:  # Top 5 for speed
                try:
                    url = f"https://eodhd.com/api/technical/{symbol}.RO"
                    params = {
                        "api_token": api_key,
                        "fmt": "json",
                        "function": "rsi",
                        "period": 14
                    }
                    response = await client.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            # Get latest RSI
                            latest_rsi = data[-1].get("rsi", 50)
                            rsi_values.append(latest_rsi)
                except Exception as e:
                    logger.warning(f"Error fetching RSI for {symbol}: {e}")
                    continue
        
        if not rsi_values:
            return {"score": 50, "label": "Neutru", "details": "No RSI data"}
        
        avg_rsi = sum(rsi_values) / len(rsi_values)
        
        # Convert RSI to Fear & Greed score
        if avg_rsi < 30:
            score = int((avg_rsi / 30) * 20)
            label = "Frică Extremă"
        elif avg_rsi < 40:
            score = int(20 + ((avg_rsi - 30) / 10) * 20)
            label = "Frică"
        elif avg_rsi < 60:
            score = int(40 + ((avg_rsi - 40) / 20) * 20)
            label = "Neutru"
        elif avg_rsi < 70:
            score = int(60 + ((avg_rsi - 60) / 10) * 20)
            label = "Lăcomie"
        else:
            score = int(80 + ((avg_rsi - 70) / 30) * 20)
            label = "Lăcomie Extremă"
        
        return {
            "score": min(100, max(0, score)),
            "label": label,
            "avg_rsi": round(avg_rsi, 2),
            "details": f"RSI mediu BET: {avg_rsi:.1f}"
        }
    except Exception as e:
        logger.error(f"Error calculating RSI component: {e}")
        return {"score": 50, "label": "Neutru", "details": str(e)}


async def calculate_momentum_component(db) -> Dict:
    """
    Market Momentum (Gainers vs Losers)
    Score based on ratio of stocks going up vs down
    """
    try:
        stocks = await db.stocks_bvb.find({}, {"_id": 0, "change_percent": 1}).to_list(100)
        
        if not stocks:
            return {"score": 50, "label": "Neutru", "details": "No stock data"}
        
        gainers = sum(1 for s in stocks if s.get("change_percent", 0) > 0)
        losers = sum(1 for s in stocks if s.get("change_percent", 0) < 0)
        total = gainers + losers
        
        if total == 0:
            return {"score": 50, "label": "Neutru", "details": "No movement data"}
        
        ratio = gainers / total
        score = int(ratio * 100)
        
        if score < 25:
            label = "Frică Extremă"
        elif score < 40:
            label = "Frică"
        elif score < 60:
            label = "Neutru"
        elif score < 75:
            label = "Lăcomie"
        else:
            label = "Lăcomie Extremă"
        
        return {
            "score": score,
            "label": label,
            "gainers": gainers,
            "losers": losers,
            "details": f"{gainers} cresc, {losers} scad"
        }
    except Exception as e:
        logger.error(f"Error calculating momentum: {e}")
        return {"score": 50, "label": "Neutru", "details": str(e)}


async def calculate_volatility_component(eodhd_client) -> Dict:
    """
    Volatility Component
    High volatility = Fear, Low volatility = Greed
    """
    try:
        import httpx
        import os
        
        api_key = os.environ.get("EODHD_API_KEY")
        if not api_key:
            return {"score": 50, "label": "Neutru", "details": "API key missing"}
        
        volatilities = []
        async with httpx.AsyncClient() as client:
            for symbol in BET_COMPONENTS[:5]:
                try:
                    # Get last 20 days of data
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
                    
                    url = f"https://eodhd.com/api/eod/{symbol}.RO"
                    params = {
                        "api_token": api_key,
                        "fmt": "json",
                        "from": start_date.strftime("%Y-%m-%d"),
                        "to": end_date.strftime("%Y-%m-%d")
                    }
                    response = await client.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if len(data) >= 5:
                            # Calculate daily returns volatility
                            closes = [d["close"] for d in data[-20:]]
                            returns = [(closes[i] - closes[i-1]) / closes[i-1] * 100 
                                      for i in range(1, len(closes))]
                            if returns:
                                import statistics
                                vol = statistics.stdev(returns) if len(returns) > 1 else 0
                                volatilities.append(vol)
                except Exception as e:
                    logger.warning(f"Error fetching volatility for {symbol}: {e}")
                    continue
        
        if not volatilities:
            return {"score": 50, "label": "Neutru", "details": "No volatility data"}
        
        avg_vol = sum(volatilities) / len(volatilities)
        
        # Inverse scoring: high volatility = fear (low score)
        # Normal BVB volatility ~1-2%, high >3%
        if avg_vol > 3:
            score = 15
            label = "Frică Extremă"
        elif avg_vol > 2:
            score = 30
            label = "Frică"
        elif avg_vol > 1.5:
            score = 50
            label = "Neutru"
        elif avg_vol > 1:
            score = 70
            label = "Lăcomie"
        else:
            score = 85
            label = "Lăcomie Extremă"
        
        return {
            "score": score,
            "label": label,
            "volatility": round(avg_vol, 2),
            "details": f"Volatilitate medie: {avg_vol:.2f}%"
        }
    except Exception as e:
        logger.error(f"Error calculating volatility: {e}")
        return {"score": 50, "label": "Neutru", "details": str(e)}


async def calculate_volume_component(db) -> Dict:
    """
    Volume Component
    High volume = more conviction (can be either direction)
    """
    try:
        # Get recent volume data
        stocks = await db.stocks_bvb.find(
            {"volume": {"$exists": True}}, 
            {"_id": 0, "symbol": 1, "volume": 1, "change_percent": 1}
        ).to_list(50)
        
        if not stocks:
            return {"score": 50, "label": "Neutru", "details": "No volume data"}
        
        # Calculate volume-weighted sentiment
        total_volume = sum(s.get("volume", 0) for s in stocks)
        if total_volume == 0:
            return {"score": 50, "label": "Neutru", "details": "Zero volume"}
        
        weighted_sentiment = sum(
            s.get("volume", 0) * (1 if s.get("change_percent", 0) > 0 else -1 if s.get("change_percent", 0) < 0 else 0)
            for s in stocks
        ) / total_volume
        
        # Convert to 0-100 score
        score = int(50 + weighted_sentiment * 50)
        score = min(100, max(0, score))
        
        if score < 25:
            label = "Frică Extremă"
        elif score < 40:
            label = "Frică"
        elif score < 60:
            label = "Neutru"
        elif score < 75:
            label = "Lăcomie"
        else:
            label = "Lăcomie Extremă"
        
        return {
            "score": score,
            "label": label,
            "total_volume": total_volume,
            "details": f"Volum total: {total_volume:,}"
        }
    except Exception as e:
        logger.error(f"Error calculating volume component: {e}")
        return {"score": 50, "label": "Neutru", "details": str(e)}


@router.get("/fear-greed")
async def get_fear_greed_index():
    """
    Calculate comprehensive Fear & Greed Index for BVB
    
    Components:
    1. RSI (30% weight) - Technical momentum
    2. Market Momentum (25% weight) - Gainers vs Losers
    3. Volatility (25% weight) - Price swings
    4. Volume (20% weight) - Trading conviction
    """
    try:
        db = await get_database()
        eodhd_client = get_eodhd_client()
        
        # Calculate all components
        rsi_component = await calculate_rsi_component(eodhd_client)
        momentum_component = await calculate_momentum_component(db)
        volatility_component = await calculate_volatility_component(eodhd_client)
        volume_component = await calculate_volume_component(db)
        
        # Weighted average
        weights = {
            "rsi": 0.30,
            "momentum": 0.25,
            "volatility": 0.25,
            "volume": 0.20
        }
        
        total_score = (
            rsi_component["score"] * weights["rsi"] +
            momentum_component["score"] * weights["momentum"] +
            volatility_component["score"] * weights["volatility"] +
            volume_component["score"] * weights["volume"]
        )
        
        total_score = int(round(total_score))
        
        # Determine overall label
        if total_score < 20:
            label = "Frică Extremă"
            description = "Piața este în panică. Investitorii vând agresiv."
            color = "#dc2626"  # red-600
        elif total_score < 40:
            label = "Frică"
            description = "Predomină pesimismul. Oportunități potențiale pentru cumpărare."
            color = "#ea580c"  # orange-600
        elif total_score < 60:
            label = "Neutru"
            description = "Piața este echilibrată. Fără tendințe clare."
            color = "#ca8a04"  # yellow-600
        elif total_score < 80:
            label = "Lăcomie"
            description = "Optimism crescut. Atenție la supraevaluare."
            color = "#65a30d"  # lime-600
        else:
            label = "Lăcomie Extremă"
            description = "Euforie pe piață. Risc ridicat de corecție."
            color = "#16a34a"  # green-600
        
        # Historical data (store in DB for trends)
        await db.fear_greed_history.insert_one({
            "score": total_score,
            "label": label,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {
                "rsi": rsi_component,
                "momentum": momentum_component,
                "volatility": volatility_component,
                "volume": volume_component
            }
        })
        
        # Get 7-day history for trend
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        history = await db.fear_greed_history.find(
            {"timestamp": {"$gte": seven_days_ago.isoformat()}},
            {"_id": 0, "score": 1, "timestamp": 1}
        ).sort("timestamp", -1).limit(7).to_list(7)
        
        # Calculate trend
        if len(history) >= 2:
            recent_avg = sum(h["score"] for h in history[:3]) / min(3, len(history))
            older_avg = sum(h["score"] for h in history[3:]) / max(1, len(history) - 3) if len(history) > 3 else recent_avg
            trend = "up" if recent_avg > older_avg + 5 else "down" if recent_avg < older_avg - 5 else "stable"
        else:
            trend = "stable"
        
        return {
            "score": total_score,
            "label": label,
            "description": description,
            "color": color,
            "trend": trend,
            "components": {
                "rsi": {
                    "score": rsi_component["score"],
                    "weight": "30%",
                    "details": rsi_component["details"]
                },
                "momentum": {
                    "score": momentum_component["score"],
                    "weight": "25%",
                    "details": momentum_component["details"]
                },
                "volatility": {
                    "score": volatility_component["score"],
                    "weight": "25%",
                    "details": volatility_component["details"]
                },
                "volume": {
                    "score": volume_component["score"],
                    "weight": "20%",
                    "details": volume_component["details"]
                }
            },
            "history": history[:7],
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "market": "BVB"
        }
        
    except Exception as e:
        logger.error(f"Error calculating Fear & Greed Index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fear-greed/history")
async def get_fear_greed_history(days: int = 30):
    """Get historical Fear & Greed data"""
    try:
        db = await get_database()
        
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        history = await db.fear_greed_history.find(
            {"timestamp": {"$gte": start_date.isoformat()}},
            {"_id": 0}
        ).sort("timestamp", -1).to_list(days * 24)  # Hourly data
        
        return {
            "period_days": days,
            "data_points": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
