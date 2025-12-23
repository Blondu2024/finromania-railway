from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import services and database
from config.database import connect_to_mongodb, close_mongodb_connection, get_database
from services.stock_service import StockService
from services.news_service import NewsService
from services.currency_service import CurrencyService
from jobs.scheduler import start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
stock_service = StockService()
news_service = NewsService()
currency_service = CurrencyService()

# Lifespan for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting FinRomania API...")
    await connect_to_mongodb()
    start_scheduler()
    logger.info("✅ FinRomania API started successfully!")
    yield
    # Shutdown
    logger.info("🛑 Shutting down FinRomania API...")
    stop_scheduler()
    await close_mongodb_connection()
    logger.info("✅ FinRomania API shut down successfully!")

# Create the main app
app = FastAPI(
    title="FinRomania API",
    description="Platformă de știri financiare pentru România",
    version="1.0.0",
    lifespan=lifespan
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============================================
# PYDANTIC MODELS
# ============================================

class StockResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: Optional[int] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    currency: Optional[str] = None
    market: Optional[str] = None
    source: Optional[str] = None
    is_mock: Optional[bool] = False

class IndexResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    previous_close: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None
    source: Optional[str] = None

class ArticleResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    source: Dict[str, Any]
    author: Optional[str] = None
    published_at: Optional[str] = None
    language: str
    is_rewritten: Optional[bool] = False

class CurrencyRate(BaseModel):
    currency: str
    rate: float
    multiplier: int = 1

class CurrencyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    date: str
    rates: Dict[str, Dict[str, Any]]
    source: str

class MarketOverview(BaseModel):
    bvb_stocks: List[StockResponse]
    global_indices: List[IndexResponse]
    currencies: Optional[CurrencyResponse] = None
    last_updated: str

# ============================================
# API ENDPOINTS
# ============================================

@api_router.get("/")
async def root():
    return {
        "message": "FinRomania API",
        "version": "1.0.0",
        "endpoints": {
            "stocks_bvb": "/api/stocks/bvb",
            "stocks_global": "/api/stocks/global",
            "news": "/api/news",
            "currencies": "/api/currencies",
            "market_overview": "/api/market/overview"
        }
    }

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# ============================================
# STOCKS - BVB (Romania)
# ============================================

@api_router.get("/stocks/bvb", response_model=List[StockResponse])
async def get_bvb_stocks():
    """Obține toate acțiunile BVB"""
    try:
        db = await get_database()
        stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        
        if not stocks:
            # Dacă nu există date, forțează update
            await stock_service.update_bvb_stocks()
            stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        
        return stocks
    except Exception as e:
        logger.error(f"Error getting BVB stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/stocks/bvb/{symbol}", response_model=StockResponse)
async def get_bvb_stock(symbol: str):
    """Obține o acțiune BVB specifică"""
    try:
        db = await get_database()
        stock = await db.stocks_bvb.find_one({"symbol": symbol.upper()}, {"_id": 0})
        
        if not stock:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
        
        return stock
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting BVB stock {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# STOCKS - GLOBAL INDICES
# ============================================

@api_router.get("/stocks/global", response_model=List[IndexResponse])
async def get_global_indices():
    """Obține toți indicii globali"""
    try:
        db = await get_database()
        indices = await db.stocks_global.find({}, {"_id": 0}).to_list(100)
        
        if not indices:
            # Dacă nu există date, forțează update
            await stock_service.update_global_indices()
            indices = await db.stocks_global.find({}, {"_id": 0}).to_list(100)
        
        return indices
    except Exception as e:
        logger.error(f"Error getting global indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# NEWS
# ============================================

@api_router.get("/news", response_model=List[ArticleResponse])
async def get_news(
    limit: int = Query(default=20, ge=1, le=100),
    language: str = Query(default="en")
):
    """Obține ultimele știri"""
    try:
        db = await get_database()
        articles = await db.articles.find(
            {"language": language},
            {"_id": 0}
        ).sort("published_at", -1).limit(limit).to_list(limit)
        
        if not articles:
            # Dacă nu există date, forțează fetch
            await news_service.fetch_and_store_news()
            articles = await db.articles.find(
                {"language": language},
                {"_id": 0}
            ).sort("published_at", -1).limit(limit).to_list(limit)
        
        return articles
    except Exception as e:
        logger.error(f"Error getting news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# CURRENCIES
# ============================================

@api_router.get("/currencies", response_model=CurrencyResponse)
async def get_currencies():
    """Obține cursurile valutare BNR"""
    try:
        db = await get_database()
        rates = await db.currencies.find_one(
            {},
            {"_id": 0},
            sort=[("date", -1)]
        )
        
        if not rates:
            # Dacă nu există date, forțează update
            await currency_service.update_currency_rates()
            rates = await db.currencies.find_one(
                {},
                {"_id": 0},
                sort=[("date", -1)]
            )
        
        if not rates:
            raise HTTPException(status_code=404, detail="No currency rates available")
        
        return rates
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting currencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# MARKET OVERVIEW (Combined endpoint)
# ============================================

@api_router.get("/market/overview", response_model=MarketOverview)
async def get_market_overview():
    """Obține o vedere de ansamblu asupra pieței"""
    try:
        db = await get_database()
        
        # Get BVB stocks
        bvb_stocks = await db.stocks_bvb.find({}, {"_id": 0}).to_list(100)
        
        # Get global indices
        global_indices = await db.stocks_global.find({}, {"_id": 0}).to_list(100)
        
        # Get currencies
        currencies = await db.currencies.find_one(
            {},
            {"_id": 0},
            sort=[("date", -1)]
        )
        
        return MarketOverview(
            bvb_stocks=bvb_stocks or [],
            global_indices=global_indices or [],
            currencies=currencies,
            last_updated=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# MANUAL REFRESH ENDPOINTS (for testing)
# ============================================

@api_router.post("/refresh/bvb")
async def refresh_bvb_stocks():
    """Forțează refresh pentru BVB stocks"""
    try:
        count = await stock_service.update_bvb_stocks()
        return {"message": f"Updated {count} BVB stocks", "count": count}
    except Exception as e:
        logger.error(f"Error refreshing BVB stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/refresh/global")
async def refresh_global_indices():
    """Forțează refresh pentru global indices"""
    try:
        count = await stock_service.update_global_indices()
        return {"message": f"Updated {count} global indices", "count": count}
    except Exception as e:
        logger.error(f"Error refreshing global indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/refresh/news")
async def refresh_news():
    """Forțează refresh pentru news"""
    try:
        count = await news_service.fetch_and_store_news()
        return {"message": f"Fetched {count} new articles", "count": count}
    except Exception as e:
        logger.error(f"Error refreshing news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/refresh/currencies")
async def refresh_currencies():
    """Forțează refresh pentru currencies"""
    try:
        success = await currency_service.update_currency_rates()
        return {"message": "Currency rates updated" if success else "Failed to update", "success": success}
    except Exception as e:
        logger.error(f"Error refreshing currencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)