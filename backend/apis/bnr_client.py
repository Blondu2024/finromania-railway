"""BNR API client for currency rates"""
import requests
from xml.etree import ElementTree
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BNRClient:
    """Client pentru BNR - cursuri valutare"""
    
    BASE_URL = "https://www.bnr.ro/nbrfxrates.xml"
    
    def get_exchange_rates(self) -> Optional[Dict]:
        """Obține toate cursurile valutare de la BNR"""
        try:
            response = requests.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            
            root = ElementTree.fromstring(response.content)
            
            # Extract date
            date_str = root.attrib.get('Date')
            
            # Extract rates
            rates = {}
            for currency in root.findall('.//Rate'):
                code = currency.attrib.get('currency')
                value = float(currency.text)
                multiplier = int(currency.attrib.get('multiplier', 1))
                
                rates[code] = {
                    'rate': value / multiplier,
                    'multiplier': multiplier
                }
            
            return {
                'date': date_str,
                'rates': rates,
                'source': 'BNR',
                'last_updated': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error fetching BNR rates: {e}")
            return None
    
    def get_specific_rate(self, currency: str) -> Optional[float]:
        """Obține rata pentru o monedă specifică"""
        data = self.get_exchange_rates()
        
        if data and currency in data['rates']:
            return data['rates'][currency]['rate']
        
        return None
