"""Curated indices pentru învățare simplificată"""
from fastapi import APIRouter
from typing import List, Dict
import logging

router = APIRouter(prefix="/curated", tags=["curated"])
logger = logging.getLogger(__name__)

# 5-10 indici selectați pentru învățare
CURATED_INDICES = [
    {
        "id": "oil_wti",
        "symbol": "CL=F",  # WTI Crude Oil
        "name": "Oil (WTI)",
        "emoji": "🛢️",
        "category": "commodities",
        "category_ro": "Materii Prime",
        "description_ro": "Petrol - toată lumea știe ce e",
        "volatility": "high",
        "volatility_ro": "Volatil",
        "good_for_learning": True,
        "learning_tip": "Oil e perfect pentru învățare! E volatil (se mișcă mult) deci vei vedea rapid profit/pierdere.",
        "risk_level": "medium",
        "market_type": "global"
    },
    {
        "id": "gold",
        "symbol": "GC=F",  # Gold Futures
        "name": "Gold",
        "emoji": "🥇",
        "category": "commodities",
        "category_ro": "Materii Prime",
        "description_ro": "Aur - investiție clasică și sigură",
        "volatility": "low",
        "volatility_ro": "Stabil",
        "good_for_learning": True,
        "learning_tip": "Gold e mai stabil decât Oil. Perfect pentru a învăța trading fără stres mare.",
        "risk_level": "low",
        "market_type": "global"
    },
    {
        "id": "sp500",
        "symbol": "^GSPC",  # S&P 500
        "name": "S&P 500",
        "emoji": "📈",
        "category": "indices",
        "category_ro": "Indici",
        "description_ro": "Top 500 companii americane",
        "volatility": "medium",
        "volatility_ro": "Moderat",
        "good_for_learning": True,
        "learning_tip": "S&P 500 reprezintă economia SUA. Bun pentru strategii pe termen lung.",
        "risk_level": "low",
        "market_type": "global"
    },
    {
        "id": "eurusd",
        "symbol": "EURUSD=X",  # EUR/USD
        "name": "EUR/USD",
        "emoji": "💵",
        "category": "forex",
        "category_ro": "Forex",
        "description_ro": "Euro vs Dolar American",
        "volatility": "medium",
        "volatility_ro": "Moderat",
        "good_for_learning": True,
        "learning_tip": "EUR/USD e cea mai tranzacționată pereche forex. Lichiditate mare = execuție rapidă.",
        "risk_level": "medium",
        "market_type": "global"
    },
    {
        "id": "tlv",
        "symbol": "TLV",
        "name": "Banca Transilvania",
        "emoji": "🏦",
        "category": "stocks_ro",
        "category_ro": "Acțiuni Românești",
        "description_ro": "Cea mai mare bancă privată din România",
        "volatility": "medium",
        "volatility_ro": "Moderat",
        "good_for_learning": True,
        "learning_tip": "Banca Transilvania e blue-chip românesc. Date reale de pe BVB!",
        "risk_level": "medium",
        "market_type": "bvb"
    },
    {
        "id": "h2o",
        "symbol": "H2O",
        "name": "Hidroelectrica",
        "emoji": "⚡",
        "category": "stocks_ro",
        "category_ro": "Acțiuni Românești",
        "description_ro": "Cel mai mare producător de energie din România",
        "volatility": "medium",
        "volatility_ro": "Moderat",
        "good_for_learning": True,
        "learning_tip": "Hidroelectrica e gigant energetic. Stabilitate + creștere = good pentru învățare!",
        "risk_level": "low",
        "market_type": "bvb"
    },
    {
        "id": "snp",
        "symbol": "SNP",
        "name": "OMV Petrom",
        "emoji": "🛢️",
        "category": "stocks_ro",
        "category_ro": "Acțiuni Românești",
        "description_ro": "Cea mai mare companie petrolieră din România",
        "volatility": "medium",
        "volatility_ro": "Moderat",
        "good_for_learning": True,
        "learning_tip": "OMV Petrom e legat de prețul petrolului. Învață corelații între piețe!",
        "risk_level": "medium",
        "market_type": "bvb"
    },
]

@router.get("/indices")
async def get_curated_indices():
    """Get all curated indices for learning"""
    return {
        "indices": CURATED_INDICES,
        "total": len(CURATED_INDICES),
        "categories": ["commodities", "indices", "forex", "stocks_ro"]
    }

@router.get("/indices/{index_id}")
async def get_index_details(index_id: str):
    """Get details for a specific curated index"""
    for idx in CURATED_INDICES:
        if idx["id"] == index_id:
            return idx
    
    return {"error": "Index not found"}

@router.get("/beginner")
async def get_beginner_indices():
    """Get recommended indices for beginners"""
    beginner_friendly = [idx for idx in CURATED_INDICES if idx["good_for_learning"]]
    
    return {
        "indices": beginner_friendly[:5],  # Top 5 for beginners
        "message": "Aceștia sunt cei mai buni indici pentru a începe învățarea!"
    }

@router.get("/by-category/{category}")
async def get_indices_by_category(category: str):
    """Get indices by category"""
    filtered = [idx for idx in CURATED_INDICES if idx["category"] == category]
    
    return {
        "category": category,
        "indices": filtered,
        "total": len(filtered)
    }
