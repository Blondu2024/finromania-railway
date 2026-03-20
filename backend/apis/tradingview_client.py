"""
TradingView API Client pentru indicii BVB
API gratuit care returnează date în timp real pentru toți indicii BVB
"""
import httpx
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Mapare simboluri TradingView -> nume afișat
BVB_INDEX_MAPPING = {
    "BVB:BET": {"id": "BET", "name": "BET Index", "description": "Blue-chip companies"},
    "BVB:BETTR": {"id": "BETTR", "name": "BET-TR Index", "description": "Total Return"},
    "BVB:BETFI": {"id": "BETFI", "name": "BET-FI Index", "description": "Financial sector"},
    "BVB:BETNG": {"id": "BETNG", "name": "BET-NG Index", "description": "Energy sector"},
    "BVB:BETXT": {"id": "BETXT", "name": "BET-XT Index", "description": "Extended index"},
}

class TradingViewClient:
    """Client pentru TradingView Scanner API"""
    
    BASE_URL = "https://scanner.tradingview.com/romania/scan"
    
    async def get_bvb_indices(self) -> List[Dict]:
        """
        Obține toți indicii BVB cu date în timp real de la TradingView.
        Returnează date exacte ca pe bvb.ro!
        """
        try:
            symbols = list(BVB_INDEX_MAPPING.keys())
            
            payload = {
                "symbols": {"tickers": symbols},
                "columns": ["close", "change", "change_abs", "high", "low", "open"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.BASE_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.error(f"TradingView API error: {response.status_code}")
                    return []
                
                data = response.json()
                indices = []
                
                for item in data.get("data", []):
                    symbol = item["s"]
                    values = item["d"]
                    
                    if symbol not in BVB_INDEX_MAPPING:
                        continue
                    
                    info = BVB_INDEX_MAPPING[symbol]
                    
                    # values: [close, change%, change_abs, high, low, open]
                    close = values[0] if len(values) > 0 else None
                    change_percent = values[1] if len(values) > 1 else 0
                    change_abs = values[2] if len(values) > 2 else 0
                    high = values[3] if len(values) > 3 else None
                    low = values[4] if len(values) > 4 else None
                    open_val = values[5] if len(values) > 5 else None
                    
                    if close is not None:
                        indices.append({
                            "id": info["id"],
                            "symbol": symbol,
                            "name": info["name"],
                            "description": info["description"],
                            "value": round(close, 2),
                            "change": round(change_abs, 2),
                            "change_percent": round(change_percent, 2),
                            "high": round(high, 2) if high else None,
                            "low": round(low, 2) if low else None,
                            "open": round(open_val, 2) if open_val else None,
                            "is_live": True,
                            "source": "TradingView"
                        })
                
                logger.info(f"TradingView: fetched {len(indices)} BVB indices")
                return indices
                
        except Exception as e:
            logger.error(f"Error fetching BVB indices from TradingView: {e}")
            return []
    
    async def get_index(self, index_id: str) -> Optional[Dict]:
        """Obține un singur indice BVB"""
        indices = await self.get_bvb_indices()
        for idx in indices:
            if idx["id"] == index_id:
                return idx
        return None


# Singleton instance
_tradingview_client = None

def get_tradingview_client() -> TradingViewClient:
    global _tradingview_client
    if _tradingview_client is None:
        _tradingview_client = TradingViewClient()
    return _tradingview_client
