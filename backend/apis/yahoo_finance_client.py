"""Yahoo Finance API client for global markets"""
import yfinance as yf
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class YahooFinanceClient:
    """Client pentru Yahoo Finance - indici globali"""
    
    GLOBAL_INDICES = {
        '^GSPC': 'S&P 500',
        '^IXIC': 'NASDAQ',
        '^DJI': 'Dow Jones',
        '^GDAXI': 'DAX',
        '^FTSE': 'FTSE 100',
        '^N225': 'Nikkei 225',
    }
    
    def get_global_indices(self) -> List[Dict]:
        """Obține toți indicii globali"""
        results = []
        
        for symbol, name in self.GLOBAL_INDICES.items():
            try:
                data = self.get_index(symbol)
                if data:
                    data['name'] = name
                    results.append(data)
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
        
        return results
    
    def get_index(self, symbol: str) -> Optional[Dict]:
        """Obține date pentru un index specific"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            price = info.get('regularMarketPrice')
            if not price:
                return None
            
            return {
                'symbol': symbol,
                'price': price,
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'previous_close': info.get('regularMarketPreviousClose'),
                'open': info.get('regularMarketOpen'),
                'high': info.get('regularMarketDayHigh'),
                'low': info.get('regularMarketDayLow'),
                'volume': info.get('regularMarketVolume'),
                'last_updated': datetime.utcnow(),
                'source': 'yahoo_finance'
            }
        except Exception as e:
            logger.error(f"Error fetching index {symbol}: {e}")
            return None
