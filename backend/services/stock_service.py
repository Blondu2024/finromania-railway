"""Service pentru gestionarea datelor de stocks"""
from typing import List, Dict, Optional
import logging
import os
from datetime import datetime, timezone, timedelta
from apis.yahoo_finance_client import YahooFinanceClient
from apis.eodhd_client import get_eodhd_client, EODHDClient
from config.database import get_database
from config.settings import settings
import yfinance as yf

logger = logging.getLogger(__name__)

class StockService:
    """Service pentru stocks (BVB + Global)"""
    
    def __init__(self):
        self.yahoo_client = YahooFinanceClient()
        self.eodhd_client = get_eodhd_client()
        self._use_real_bvb = bool(os.environ.get("EODHD_API_KEY"))
    
    # EODHD symbols for global indices (batch real-time)
    # symbol_display maps to legacy yfinance symbols stored in DB
    EODHD_INDICES = {
        "GSPC.INDX": {"name": "S&P 500", "symbol_display": "^GSPC"},
        "NDX.INDX": {"name": "NASDAQ 100", "symbol_display": "^IXIC"},  # replace old NASDAQ Composite
        "DJI.INDX": {"name": "Dow Jones", "symbol_display": "^DJI"},
        "GDAXI.INDX": {"name": "DAX", "symbol_display": "^GDAXI"},
        "FTSE.INDX": {"name": "FTSE 100", "symbol_display": "^FTSE"},
        "N225.INDX": {"name": "Nikkei 225", "symbol_display": "^N225"},
        "HSI.INDX": {"name": "Hang Seng", "symbol_display": "^HSI"},
    }

    async def update_global_indices(self) -> int:
        """Update indici globali - 100% EODHD (no yfinance)"""
        import httpx
        import os

        def safe_float(val, default=0.0):
            if val is None or val in ('NA', 'N/A', ''):
                return default
            try:
                return float(val)
            except (ValueError, TypeError):
                return default

        def safe_int(val, default=0):
            if val is None or val in ('NA', 'N/A', ''):
                return default
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return default

        try:
            logger.info("🔄 Updating global indices (EODHD)...")
            api_key = os.environ.get("EODHD_API_KEY")
            if not api_key:
                logger.warning("EODHD_API_KEY not set, skipping global indices update")
                return 0

            symbols_str = ",".join(self.EODHD_INDICES.keys())
            url = f"https://eodhd.com/api/real-time/{symbols_str}"

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, params={"api_token": api_key, "fmt": "json"})

            if resp.status_code != 200:
                logger.error(f"EODHD indices update failed: {resp.status_code}")
                return 0

            rt_data = resp.json()
            rt_items = rt_data if isinstance(rt_data, list) else [rt_data]

            db = await get_database()
            count = 0
            now = datetime.now(timezone.utc)

            for item in rt_items:
                code = item.get("code", "")
                if code not in self.EODHD_INDICES:
                    continue

                info = self.EODHD_INDICES[code]
                price = safe_float(item.get("close"))
                if price == 0:
                    continue

                prev_close = safe_float(item.get("previousClose"), price)
                change = safe_float(item.get("change"))
                change_p = safe_float(item.get("change_p"))

                index_doc = {
                    "symbol": info["symbol_display"],
                    "eodhd_symbol": code,
                    "name": info["name"],
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_p, 2),
                    "previous_close": round(prev_close, 2),
                    "high": round(safe_float(item.get("high"), price), 2),
                    "low": round(safe_float(item.get("low"), price), 2),
                    "volume": safe_int(item.get("volume")),
                    "last_updated": now,
                    "source": "eodhd_realtime",
                    "is_live": True,
                }

                await db.stocks_global.update_one(
                    {"symbol": info["symbol_display"]},
                    {"$set": index_doc},
                    upsert=True,
                )
                count += 1

            logger.info(f"✅ Updated {count} global indices (EODHD)")
            return count

        except Exception as e:
            logger.error(f"Error updating global indices: {e}")
            return 0
    
    async def update_bvb_stocks(self) -> int:
        """Update BVB stocks - REAL data from EODHD if available"""
        try:
            logger.info("🔄 Updating BVB stocks...")
            
            if self._use_real_bvb:
                # Use REAL data from EODHD
                stocks = await self.eodhd_client.get_all_bvb_quotes()
                data_source = "EODHD (REAL)"
            else:
                # Fallback to mock data
                from apis.bvb_mock_client import BVBMockClient
                bvb_mock = BVBMockClient()
                stocks = bvb_mock.get_all_stocks()
                data_source = "MOCK"
            
            if not stocks:
                logger.warning("No BVB stocks fetched")
                return 0
            
            db = await get_database()
            count = 0

            # Pre-load logo_url from fundamentals cache (avoid N+1 at query time)
            logo_cache = {}
            fund_docs = await db.fundamentals_daily_cache.find({}, {"_id": 0, "symbol": 1, "logo_url": 1}).to_list(200)
            for doc in fund_docs:
                if doc.get("logo_url"):
                    logo_cache[doc["symbol"]] = doc["logo_url"]

            for stock in stocks:
                if stock.get("symbol") in logo_cache:
                    stock["logo_url"] = logo_cache[stock["symbol"]]
                await db.stocks_bvb.update_one(
                    {'symbol': stock['symbol']},
                    {'$set': stock},
                    upsert=True
                )
                count += 1

            logger.info(f"✅ Updated {count} BVB stocks ({data_source})")
            return count
            
        except Exception as e:
            logger.error(f"Error updating BVB stocks: {e}")
            return 0
    
    async def get_bvb_stock_realtime(self, symbol: str) -> Optional[Dict]:
        """Get real-time data for a specific BVB stock"""
        if self._use_real_bvb:
            return await self.eodhd_client.get_stock_quote(symbol)
        else:
            from apis.bvb_mock_client import BVBMockClient
            bvb_mock = BVBMockClient()
            return bvb_mock.get_stock(symbol)
    
    async def get_all_bvb_stocks(self) -> List[Dict]:
        """Obține toate stocks BVB din DB, cu fundamentale de pe BVB.ro"""
        db = await get_database()
        stocks = await db.stocks_bvb.find({}, {"_id": 0}).limit(100).to_list(length=100)

        # Merge fundamentale BVB.ro (PER, dividend, market_cap, 52w)
        fundamentals = await db.bvb_fundamentals.find({}, {"_id": 0}).to_list(200)
        fund_map = {f["symbol"]: f for f in fundamentals}

        for stock in stocks:
            sym = stock.get("symbol", "")
            fund = fund_map.get(sym)
            if fund:
                stock["pe_ratio"] = fund.get("per")
                stock["dividend_yield"] = fund.get("dividend_yield")
                stock["dividend_per_share"] = fund.get("dividend")
                stock["dividend_year"] = fund.get("dividend_year")
                stock["market_cap"] = fund.get("market_cap")
                stock["high_52w"] = fund.get("high_52w")
                stock["low_52w"] = fund.get("low_52w")
                stock["total_shares"] = fund.get("total_shares")
                stock["fundamentals_source"] = "BVB.ro"
                stock["fundamentals_updated"] = fund.get("scraped_at")

        return stocks
    
    async def get_all_global_indices(self) -> List[Dict]:
        """Obține toți indicii globali din DB"""
        db = await get_database()
        cursor = db.stocks_global.find({}, {"_id": 0}).limit(100)
        return await cursor.to_list(length=100)
    
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
            
            # Get current price from latest history or info
            current_price = history_data[-1]['close'] if history_data else 0
            prev_close = history_data[0]['close'] if len(history_data) > 1 else current_price
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close else 0
            
            return {
                'symbol': symbol,
                'name': info.get('shortName', symbol),
                'description': info.get('longBusinessSummary', ''),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', ''),
                'price': current_price,
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'history': history_data,
                'period': period,
                'is_mock': False,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting history for {symbol}: {e}")
            return None
    
    async def get_bvb_stock_history(self, symbol: str, period: str = "1m", days: int = None) -> Optional[Dict]:
        """Obține istoricul pentru o acțiune BVB"""
        try:
            if self._use_real_bvb:
                # Get REAL historical data from EODHD
                history_data = await self.eodhd_client.get_historical_data(symbol, period, days)
                
                if history_data:
                    stock_info = EODHDClient.BVB_STOCKS.get(symbol, {"name": symbol, "sector": "N/A"})
                    return {
                        'symbol': symbol,
                        'name': stock_info["name"],
                        'description': f"Acțiune listată la Bursa de Valori București (BVB).",
                        'currency': 'RON',
                        'exchange': 'BVB',
                        'history': history_data,
                        'period': period,
                        'is_mock': False,
                        'last_updated': datetime.now(timezone.utc).isoformat()
                    }
                else:
                    logger.warning(f"No EODHD historical data for {symbol}, falling back to DB data")
            
            # Fallback: get stock from DB and generate mock history
            db = await get_database()
            stock = await db.stocks_bvb.find_one({"symbol": symbol.upper()}, {"_id": 0})
            
            if stock:
                return self._generate_fallback_history(stock, period)
            
            # Last resort: try mock data
            return self._get_bvb_mock_history(symbol)
            
        except Exception as e:
            logger.error(f"Error getting BVB history for {symbol}: {e}")
            # Try DB fallback even on exception
            try:
                db = await get_database()
                stock = await db.stocks_bvb.find_one({"symbol": symbol.upper()}, {"_id": 0})
                if stock:
                    return self._generate_fallback_history(stock, period)
            except:
                pass
            return None
    
    def _generate_fallback_history(self, stock: Dict, period: str = "1m") -> Dict:
        """Generate fallback history from DB stock data"""
        import random
        base_price = stock.get('price', 1.0)
        symbol = stock.get('symbol', '')
        
        days_map = {"1d": 5, "1w": 7, "1m": 30, "3m": 90, "6m": 180, "1y": 365, "5y": 1825}
        num_days = days_map.get(period, 30)
        
        history_data = []
        for i in range(num_days, 0, -1):
            date = datetime.now() - timedelta(days=i)
            if date.weekday() >= 5:
                continue
            variation = random.uniform(-0.03, 0.03)
            day_price = base_price * (1 + variation * (num_days - i) / num_days)
            history_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(day_price * 0.995, 4),
                'high': round(day_price * 1.01, 4),
                'low': round(day_price * 0.99, 4),
                'close': round(day_price, 4),
                'volume': random.randint(50000, 500000)
            })
        
        return {
            'symbol': symbol,
            'name': stock.get('name', symbol),
            'description': f"Acțiune listată la BVB.",
            'currency': 'RON',
            'exchange': 'BVB',
            'history': history_data,
            'period': period,
            'is_mock': True,
            'data_notice': 'Grafic ilustrativ. Datele istorice reale sunt temporar indisponibile.',
            'price': base_price,
            'change_percent': stock.get('change_percent', 0),
            'volume': stock.get('volume', 0),
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_bvb_mock_history(self, symbol: str) -> Optional[Dict]:
        """Generate mock history for BVB stock"""
        from apis.bvb_mock_client import BVBMockClient
        import random
        
        bvb_mock = BVBMockClient()
        stock = bvb_mock.get_stock(symbol)
        
        if not stock:
            return None
        
        base_price = stock['price']
        history_data = []
        
        for i in range(30, 0, -1):
            date = datetime.now() - timedelta(days=i)
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
            'description': f"Acțiune listată la BVB. Date simulate pentru MVP.",
            'currency': 'RON',
            'exchange': 'BVB',
            'history': history_data,
            'period': '1mo',
            'is_mock': True,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    async def is_using_real_data(self) -> Dict:
        """Check if using real BVB data"""
        if self._use_real_bvb:
            # Test connection
            test_ok = await self.eodhd_client.test_connection()
            return {
                "bvb_source": "EODHD (REAL)" if test_ok else "MOCK (EODHD failed)",
                "global_source": "Yahoo Finance (REAL)",
                "eodhd_connected": test_ok
            }
        return {
            "bvb_source": "MOCK",
            "global_source": "Yahoo Finance (REAL)",
            "eodhd_connected": False
        }
