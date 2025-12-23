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
    NAMESPACE = {'bnr': 'http://www.bnr.ro/xsd'}
    
    def get_exchange_rates(self) -> Optional[Dict]:
        """Obține toate cursurile valutare de la BNR"""
        try:
            response = requests.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            
            root = ElementTree.fromstring(response.content)
            
            # Extract date from Cube element
            cube = root.find('.//bnr:Cube', self.NAMESPACE)
            date_str = cube.attrib.get('date') if cube is not None else None
            
            # Extract rates
            rates = {}
            for rate_elem in root.findall('.//bnr:Rate', self.NAMESPACE):
                code = rate_elem.attrib.get('currency')
                value = float(rate_elem.text)
                multiplier = int(rate_elem.attrib.get('multiplier', 1))
                
                rates[code] = {
                    'rate': round(value / multiplier, 4),
                    'multiplier': multiplier,
                    'original_value': value
                }
            
            logger.info(f"Fetched {len(rates)} currency rates from BNR")
            
            return {
                'date': date_str,
                'rates': rates,
                'source': 'BNR',
                'last_updated': datetime.utcnow().isoformat()
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
