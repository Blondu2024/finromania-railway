"""Service pentru gestionarea datelor de stocks"""
from typing import List, Dict, Optional
import logging
from datetime import datetime
from apis.yahoo_finance_client import YahooFinanceClient
from apis.bvb_mock_client import BVBMockClient
from config.database import get_database
from config.settings import settings

logger = logging.getLogger(__name__)

class StockService:
    """Service pentru stocks (BVB + Global)"""
    
    def __init__(self):
        self.yahoo_client = YahooFinanceClient()
        self.bvb_client = BVBMockClient()
    
    async def update_global_indices(self) -> int:
        """Update indici globali"""
        try:
            logger.info("🔄 Updating global indices...")
            
            indices = self.yahoo_client.get_global_indices()
            
            if not indices:
                logger.warning("No global indices fetched")
                return 0
            
            db = await get_database()
            count = 0
            
            for index in indices:
                await db.stocks_global.update_one(
                    {'symbol': index['symbol']},
                    {'$set': index},
                    upsert=True
                )
                count += 1
            
            logger.info(f"✅ Updated {count} global indices")
            return count
            
        except Exception as e:
            logger.error(f"Error updating global indices: {e}")
            return 0
    
    async def update_bvb_stocks(self) -> int:
        """Update BVB stocks (MOCK pentru MVP)"""
        try:
            logger.info("🔄 Updating BVB stocks...")
            
            stocks = self.bvb_client.get_all_stocks()
            
            if not stocks:
                logger.warning("No BVB stocks fetched")
                return 0
            
            db = await get_database()
            count = 0
            
            for stock in stocks:
                await db.stocks_bvb.update_one(
                    {'symbol': stock['symbol']},
                    {'$set': stock},
                    upsert=True
                )
                count += 1
            
            logger.info(f"✅ Updated {count} BVB stocks (MOCK)")
            return count
            
        except Exception as e:
            logger.error(f"Error updating BVB stocks: {e}")
            return 0
    
    async def get_all_bvb_stocks(self) -> List[Dict]:
        """Obține toate stocks BVB din DB"""
        db = await get_database()
        cursor = db.stocks_bvb.find()
        return await cursor.to_list(length=None)
    
    async def get_all_global_indices(self) -> List[Dict]:
        """Obține toți indicii globali din DB"""
        db = await get_database()
        cursor = db.stocks_global.find()
        return await cursor.to_list(length=None)
