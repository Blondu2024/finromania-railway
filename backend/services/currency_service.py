"""Service pentru cursuri valutare"""
from typing import Dict, Optional
import logging
from ..apis.bnr_client import BNRClient
from ..config.database import get_database

logger = logging.getLogger(__name__)

class CurrencyService:
    """Service pentru cursuri valutare"""
    
    def __init__(self):
        self.bnr_client = BNRClient()
    
    async def update_currency_rates(self) -> bool:
        """Update cursuri valutare de la BNR"""
        try:
            logger.info("🔄 Updating currency rates...")
            
            rates_data = self.bnr_client.get_exchange_rates()
            
            if not rates_data:
                logger.warning("No currency rates fetched")
                return False
            
            db = await get_database()
            
            await db.currencies.update_one(
                {'date': rates_data['date']},
                {'$set': rates_data},
                upsert=True
            )
            
            logger.info(f"✅ Updated {len(rates_data['rates'])} currency rates")
            return True
            
        except Exception as e:
            logger.error(f"Error updating currency rates: {e}")
            return False
    
    async def get_latest_rates(self) -> Optional[Dict]:
        """Obține ultimele cursuri din DB"""
        db = await get_database()
        return await db.currencies.find_one(sort=[('date', -1)])
