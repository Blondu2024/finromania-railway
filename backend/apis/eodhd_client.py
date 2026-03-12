"""EODHD API Client pentru date BVB reale"""
import httpx
import logging
import os
from typing import Optional, List, Dict
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

class EODHDClient:
    """Client pentru EODHD API - date bursiere reale"""
    
    BASE_URL = "https://eodhd.com/api"
    
    # BVB Stock symbols with their EODHD codes
    BVB_STOCKS = {
        "TLV": {"name": "Banca Transilvania", "sector": "Financiar"},
        "H2O": {"name": "Hidroelectrica", "sector": "Energie"},
        "SNP": {"name": "OMV Petrom", "sector": "Energie"},
        "FP": {"name": "Fondul Proprietatea", "sector": "Financiar"},
        "BRD": {"name": "BRD - Groupe Société Générale", "sector": "Financiar"},
        "SNG": {"name": "Romgaz", "sector": "Energie"},
        "SNN": {"name": "Nuclearelectrica", "sector": "Energie"},
        "TGN": {"name": "Transgaz", "sector": "Energie"},
        "DIGI": {"name": "Digi Communications", "sector": "Telecom"},
        "M": {"name": "MedLife", "sector": "Sănătate"},
        "ONE": {"name": "One United Properties", "sector": "Imobiliare"},
        "TRP": {"name": "Teraplast", "sector": "Construcții"},
        "EL": {"name": "Electrica", "sector": "Energie"},
        "TEL": {"name": "Transelectrica", "sector": "Energie"},
        "WINE": {"name": "Purcari Wineries", "sector": "Consum"},
        "AQ": {"name": "Aquila Part Prod Com", "sector": "Distribuție"},
        "BVB": {"name": "Bursa de Valori București", "sector": "Financiar"},
        "COTE": {"name": "Conpet", "sector": "Energie"},
        "SFG": {"name": "Sphera Franchise Group", "sector": "Consum"},
        "ALR": {"name": "Alro", "sector": "Industrie"},
    }
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("EODHD_API_KEY")
        if not self.api_key:
            logger.warning("EODHD API key not configured")
    
    async def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time quote for a BVB stock"""
        if not self.api_key:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                # EODHD format: SYMBOL.RO for Romanian stocks
                url = f"{self.BASE_URL}/real-time/{symbol}.RO"
                params = {
                    "api_token": self.api_key,
                    "fmt": "json"
                }
                
                response = await client.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    stock_info = self.BVB_STOCKS.get(symbol, {"name": symbol, "sector": "N/A"})
                    
                    return {
                        "symbol": symbol,
                        "name": stock_info["name"],
                        "sector": stock_info["sector"],
                        "price": float(data.get("close", 0)),
                        "open": float(data.get("open", 0)),
                        "high": float(data.get("high", 0)),
                        "low": float(data.get("low", 0)),
                        "volume": int(data.get("volume", 0)),
                        "change": float(data.get("change", 0)),
                        "change_percent": float(data.get("change_p", 0)),
                        "previous_close": float(data.get("previousClose", 0)),
                        "timestamp": data.get("timestamp"),
                        "exchange": "BVB",
                        "currency": "RON",
                        "is_mock": False
                    }
                else:
                    logger.error(f"EODHD API error for {symbol}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    async def get_all_bvb_quotes(self) -> List[Dict]:
        """Get quotes for all BVB stocks"""
        if not self.api_key:
            logger.warning("EODHD API key not available, returning empty list")
            return []
        
        stocks = []
        for symbol in self.BVB_STOCKS.keys():
            quote = await self.get_stock_quote(symbol)
            if quote:
                stocks.append(quote)
        
        return stocks
    
    async def get_historical_data(self, symbol: str, period: str = "m", days: int = None) -> List[Dict]:
        """Get historical data for a stock
        period: d=day, w=week, m=month, 3m=3months, 6m=6months, 1y=1year, 5y=5years
        days: optional - exact number of days to fetch
        Note: EODHD only provides end-of-day data, so minimum is ~7 days to get meaningful data
        """
        if not self.api_key:
            return []
            
        try:
            async with httpx.AsyncClient() as client:
                # Calculate date range
                end_date = datetime.now()
                
                # Minimum 10 days to ensure we have data (accounting for weekends/holidays)
                if days:
                    actual_days = max(days, 10)
                    start_date = end_date - timedelta(days=actual_days)
                elif period == "1d" or period == "d":
                    # For "1 day" view, show last 10 calendar days (about 5-7 trading days)
                    start_date = end_date - timedelta(days=10)
                elif period == "1w" or period == "w":
                    # For 1 week, get 14 days to ensure we have ~7 trading days
                    start_date = end_date - timedelta(days=14)
                elif period == "1m" or period == "m":
                    start_date = end_date - timedelta(days=35)
                elif period == "3m":
                    start_date = end_date - timedelta(days=100)
                elif period == "6m":
                    start_date = end_date - timedelta(days=190)
                elif period == "1y":
                    start_date = end_date - timedelta(days=380)
                elif period == "5y":
                    start_date = end_date - timedelta(days=1900)
                else:
                    start_date = end_date - timedelta(days=35)
                
                url = f"{self.BASE_URL}/eod/{symbol}.RO"
                params = {
                    "api_token": self.api_key,
                    "fmt": "json",
                    "from": start_date.strftime("%Y-%m-%d"),
                    "to": end_date.strftime("%Y-%m-%d")
                }
                
                response = await client.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    return [
                        {
                            "date": item.get("date"),
                            "open": float(item.get("open", 0)),
                            "high": float(item.get("high", 0)),
                            "low": float(item.get("low", 0)),
                            "close": float(item.get("close", 0)),
                            "volume": int(item.get("volume", 0))
                        }
                        for item in data
                    ]
                else:
                    logger.error(f"EODHD historical API error: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []
    
    async def get_intraday_data(self, symbol: str, interval: str = "1h") -> List[Dict]:
        """Get intraday data for a stock
        interval: 1m, 5m, 1h
        """
        if not self.api_key:
            return []
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.BASE_URL}/intraday/{symbol}.RO"
                params = {
                    "api_token": self.api_key,
                    "fmt": "json",
                    "interval": interval
                }
                
                response = await client.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    return [
                        {
                            "datetime": item.get("datetime"),
                            "timestamp": item.get("timestamp"),
                            "open": float(item.get("open", 0)),
                            "high": float(item.get("high", 0)),
                            "low": float(item.get("low", 0)),
                            "close": float(item.get("close", 0)),
                            "volume": int(item.get("volume", 0))
                        }
                        for item in data
                    ]
                else:
                    logger.error(f"EODHD intraday API error: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            return []
    
    async def search_stocks(self, query: str) -> List[Dict]:
        """Search for stocks by name or symbol"""
        if not self.api_key:
            return []
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.BASE_URL}/search/{query}"
                params = {
                    "api_token": self.api_key,
                    "exchange": "RO"  # Only Romanian stocks
                }
                
                response = await client.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return []
    
    async def get_fundamentals(self, symbol: str) -> Optional[Dict]:
        """Get fundamental data for a stock (P/E, ROE, EPS, etc.)"""
        if not self.api_key:
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.BASE_URL}/fundamentals/{symbol}.RO"
                params = {
                    "api_token": self.api_key,
                    "fmt": "json"
                }
                
                response = await client.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract key fundamental metrics
                    highlights = data.get("Highlights", {})
                    valuation = data.get("Valuation", {})
                    financials = data.get("Financials", {})
                    balance_sheet = financials.get("Balance_Sheet", {}).get("yearly", {})
                    
                    # Get most recent balance sheet data
                    latest_bs = {}
                    if balance_sheet:
                        latest_year = sorted(balance_sheet.keys())[-1] if balance_sheet else None
                        if latest_year:
                            latest_bs = balance_sheet.get(latest_year, {})
                    
                    # Calculate debt/equity if data available
                    total_debt = float(latest_bs.get("totalDebt", 0) or 0)
                    total_equity = float(latest_bs.get("totalStockholderEquity", 0) or 0)
                    debt_equity = round(total_debt / total_equity, 2) if total_equity > 0 else None
                    
                    return {
                        "symbol": symbol,
                        "pe_ratio": highlights.get("PERatio"),
                        "pb_ratio": valuation.get("PriceBookMRQ"),
                        "ps_ratio": valuation.get("PriceSalesTTM"),
                        "roe": highlights.get("ReturnOnEquityTTM"),
                        "roi": highlights.get("ReturnOnAssetsTTM"),
                        "eps": highlights.get("EarningsShare"),
                        "eps_growth": highlights.get("QuarterlyEarningsGrowthYOY"),
                        "revenue_growth": highlights.get("QuarterlyRevenueGrowthYOY"),
                        "dividend_yield": highlights.get("DividendYield"),
                        "dividend_share": highlights.get("DividendShare"),
                        "profit_margin": highlights.get("ProfitMargin"),
                        "operating_margin": highlights.get("OperatingMarginTTM"),
                        "debt_equity": debt_equity,
                        "market_cap": highlights.get("MarketCapitalization"),
                        "ev": valuation.get("EnterpriseValue"),
                        "beta": highlights.get("Beta"),
                        "52_week_high": highlights.get("52WeekHigh"),
                        "52_week_low": highlights.get("52WeekLow"),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    logger.error(f"EODHD fundamentals API error for {symbol}: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")
            return None
    
    async def get_all_bvb_fundamentals(self) -> List[Dict]:
        """Get fundamental data for all BVB stocks"""
        if not self.api_key:
            return []
        
        fundamentals = []
        for symbol in self.BVB_STOCKS.keys():
            data = await self.get_fundamentals(symbol)
            if data:
                # Add stock info
                stock_info = self.BVB_STOCKS.get(symbol, {})
                data["name"] = stock_info.get("name", symbol)
                data["sector"] = stock_info.get("sector", "N/A")
                fundamentals.append(data)
        
        return fundamentals
    
    async def test_connection(self) -> bool:
        """Test if the API key is valid"""
        if not self.api_key:
            return False
            
        try:
            # Test with a simple request
            quote = await self.get_stock_quote("TLV")
            return quote is not None
        except Exception:
            return False


# Singleton instance
_eodhd_client = None

def get_eodhd_client() -> EODHDClient:
    """Get or create EODHD client instance"""
    global _eodhd_client
    if _eodhd_client is None:
        _eodhd_client = EODHDClient()
    return _eodhd_client
