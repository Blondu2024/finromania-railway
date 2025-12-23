"""Service pentru gestionarea datelor de stocks"""
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
from apis.yahoo_finance_client import YahooFinanceClient
from apis.bvb_mock_client import BVBMockClient
from config.database import get_database
from config.settings import settings
import yfinance as yf

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
        cursor = db.stocks_bvb.find({}, {"_id": 0})
        return await cursor.to_list(length=None)
    
    async def get_all_global_indices(self) -> List[Dict]:
        """Obține toți indicii globali din DB"""
        db = await get_database()
        cursor = db.stocks_global.find({}, {"_id": 0})
        return await cursor.to_list(length=None)
    
    def get_index_history(self, symbol: str, period: str = "1mo") -> Optional[Dict]:
        """Obține istoricul unui indice (date reale de la Yahoo Finance)"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Convert to list of dicts for JSON serialization
            history_data = []
            for date, row in hist.iterrows():
                history_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(float(row['Open']), 2),
                    'high': round(float(row['High']), 2),
                    'low': round(float(row['Low']), 2),
                    'close': round(float(row['Close']), 2),
                    'volume': int(row['Volume']) if row['Volume'] else 0
                })
            
            # Get basic info
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('shortName', symbol),
                'description': info.get('longBusinessSummary', ''),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', ''),
                'history': history_data,
                'period': period,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting history for {symbol}: {e}")
            return None
    
    def get_bvb_stock_history(self, symbol: str) -> Optional[Dict]:
        """Obține istoricul mock pentru o acțiune BVB"""
        try:
            stock = self.bvb_client.get_stock(symbol)
            if not stock:
                return None
            
            # Generate mock history for last 30 days
            import random
            base_price = stock['price']
            history_data = []
            
            for i in range(30, 0, -1):
                date = datetime.now() - timedelta(days=i)
                # Random variation ±5%
                variation = random.uniform(-0.05, 0.05)
                day_price = base_price * (1 + variation * (30-i)/30)
                
                history_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(day_price * 0.99, 2),
                    'high': round(day_price * 1.02, 2),
                    'low': round(day_price * 0.98, 2),
                    'close': round(day_price, 2),
                    'volume': random.randint(50000, 500000)
                })
            
            return {
                'symbol': symbol,
                'name': stock['name'],
                'description': f"Acțiune listată la Bursa de Valori București (BVB). Date simulate pentru MVP.",
                'currency': 'RON',
                'exchange': 'BVB',
                'history': history_data,
                'period': '1mo',
                'is_mock': True,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting BVB history for {symbol}: {e}")
            return None
