"""BVB Mock Data Client pentru MVP"""
import random
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class BVBMockClient:
    """Client pentru BVB cu date MOCK pentru MVP"""
    
    # Top 10 companii BVB pentru demo
    MOCK_STOCKS = [
        {'symbol': 'H2O', 'name': 'Hidroelectrica', 'base_price': 152.50},
        {'symbol': 'TLV', 'name': 'Banca Transilvania', 'base_price': 28.40},
        {'symbol': 'SNP', 'name': 'OMV Petrom', 'base_price': 0.62},
        {'symbol': 'BRD', 'name': 'BRD Groupe Societe Generale', 'base_price': 18.20},
        {'symbol': 'SNG', 'name': 'SN Nuclearelectrica', 'base_price': 45.60},
        {'symbol': 'TRP', 'name': 'Teraplast', 'base_price': 0.89},
        {'symbol': 'EL', 'name': 'Electrica', 'base_price': 12.34},
        {'symbol': 'SNN', 'name': 'SN Nuclearelectrica', 'base_price': 45.60},
        {'symbol': 'FP', 'name': 'Fondul Proprietatea', 'base_price': 1.45},
        {'symbol': 'ONE', 'name': 'One United Properties', 'base_price': 0.52},
    ]
    
    def __init__(self):
        self.last_prices = {stock['symbol']: stock['base_price'] for stock in self.MOCK_STOCKS}
    
    def get_all_stocks(self) -> List[Dict]:
        """Obține toate stocks BVB (MOCK)"""
        results = []
        
        for stock in self.MOCK_STOCKS:
            symbol = stock['symbol']
            name = stock['name']
            base_price = stock['base_price']
            
            # Simulate price change (±2% random)
            last_price = self.last_prices[symbol]
            change_percent = random.uniform(-2, 2)
            new_price = last_price * (1 + change_percent / 100)
            
            # Update last price pentru next call
            self.last_prices[symbol] = new_price
            
            change = new_price - last_price
            
            results.append({
                'symbol': symbol,
                'name': name,
                'price': round(new_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': random.randint(50000, 500000),
                'open': round(last_price, 2),
                'high': round(max(last_price, new_price) * 1.01, 2),
                'low': round(min(last_price, new_price) * 0.99, 2),
                'currency': 'RON',
                'market': 'BVB',
                'last_updated': datetime.utcnow(),
                'source': 'mock_data',
                'is_mock': True  # Flag pentru să știm că e mock
            })
        
        return results
    
    def get_stock(self, symbol: str) -> Dict:
        """Obține un stock specific"""
        all_stocks = self.get_all_stocks()
        
        for stock in all_stocks:
            if stock['symbol'] == symbol:
                return stock
        
        return None
