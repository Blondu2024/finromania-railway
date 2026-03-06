"""CRON Jobs Scheduler pentru actualizare automată"""
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from services.stock_service import StockService
from services.news_service import NewsService
from services.currency_service import CurrencyService
from services.notification_service import notification_service
from config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
stock_service = StockService()
news_service = NewsService()
currency_service = CurrencyService()

# Create scheduler
scheduler = AsyncIOScheduler()

async def update_bvb_stocks_job():
    """Job: Update BVB stocks"""
    try:
        logger.info("🔄 [JOB] Starting BVB stocks update...")
        count = await stock_service.update_bvb_stocks()
        logger.info(f"✅ [JOB] BVB stocks updated: {count} stocks")
    except Exception as e:
        logger.error(f"❌ [JOB] Error updating BVB stocks: {e}")

async def update_global_indices_job():
    """Job: Update global indices"""
    try:
        logger.info("🔄 [JOB] Starting global indices update...")
        count = await stock_service.update_global_indices()
        logger.info(f"✅ [JOB] Global indices updated: {count} indices")
    except Exception as e:
        logger.error(f"❌ [JOB] Error updating global indices: {e}")

async def fetch_news_job():
    """Job: Fetch and store Romanian news"""
    try:
        logger.info("🔄 [JOB] Starting Romanian news fetch...")
        count = await news_service.fetch_and_store_news()
        logger.info(f"✅ [JOB] Romanian news fetched: {count} new articles")
    except Exception as e:
        logger.error(f"❌ [JOB] Error fetching Romanian news: {e}")

async def fetch_international_news_job():
    """Job: Fetch and store international news"""
    try:
        logger.info("🔄 [JOB] Starting international news fetch...")
        count = await news_service.fetch_and_store_international_news()
        logger.info(f"✅ [JOB] International news fetched: {count} new articles")
    except Exception as e:
        logger.error(f"❌ [JOB] Error fetching international news: {e}")

async def update_currency_rates_job():
    """Job: Update currency rates"""
    try:
        logger.info("🔄 [JOB] Starting currency rates update...")
        success = await currency_service.update_currency_rates()
        if success:
            logger.info("✅ [JOB] Currency rates updated")
        else:
            logger.warning("⚠️ [JOB] Currency rates update failed")
    except Exception as e:
        logger.error(f"❌ [JOB] Error updating currency rates: {e}")

async def check_subscription_expirations_job():
    """Job: Check Early Adopter subscriptions expiring and send notifications"""
    try:
        logger.info("🔄 [JOB] Checking subscription expirations...")
        results = await notification_service.check_expiring_subscriptions()
        logger.info(f"✅ [JOB] Expiration check complete: 7d={results['7_days']}, 3d={results['3_days']}, 1d={results['1_day']}, expired={results['expired']}")
    except Exception as e:
        logger.error(f"❌ [JOB] Error checking expirations: {e}")

def start_scheduler():
    """Start all scheduled jobs"""
    try:
        # Job 1: Update BVB stocks (every 5 minutes)
        scheduler.add_job(
            update_bvb_stocks_job,
            trigger=IntervalTrigger(minutes=settings.STOCK_UPDATE_INTERVAL_MINUTES),
            id='update_bvb_stocks',
            name='Update BVB Stocks',
            replace_existing=True
        )
        
        # Job 2: Update global indices (every 5 minutes)
        scheduler.add_job(
            update_global_indices_job,
            trigger=IntervalTrigger(minutes=settings.STOCK_UPDATE_INTERVAL_MINUTES),
            id='update_global_indices',
            name='Update Global Indices',
            replace_existing=True
        )
        
        # Job 3: Fetch Romanian news (every 15 minutes)
        scheduler.add_job(
            fetch_news_job,
            trigger=IntervalTrigger(minutes=settings.SCRAPING_INTERVAL_MINUTES),
            id='fetch_news',
            name='Fetch Romanian News',
            replace_existing=True
        )
        
        # Job 4: Fetch International news (every 15 minutes)
        scheduler.add_job(
            fetch_international_news_job,
            trigger=IntervalTrigger(minutes=settings.SCRAPING_INTERVAL_MINUTES),
            id='fetch_international_news',
            name='Fetch International News',
            replace_existing=True
        )
        
        # Job 5: Update currency rates (every 1 hour)
        scheduler.add_job(
            update_currency_rates_job,
            trigger=IntervalTrigger(hours=settings.CURRENCY_UPDATE_INTERVAL_HOURS),
            id='update_currency_rates',
            name='Update Currency Rates',
            replace_existing=True
        )
        
        # Job 6: Check subscription expirations (daily at 9 AM)
        scheduler.add_job(
            check_subscription_expirations_job,
            trigger=CronTrigger(hour=9, minute=0),  # Rulează zilnic la 9:00
            id='check_subscription_expirations',
            name='Check Subscription Expirations',
            replace_existing=True
        )
        
        # Start scheduler
        scheduler.start()
        logger.info("✅ Scheduler started with all jobs!")
        logger.info(f"   • BVB stocks: every {settings.STOCK_UPDATE_INTERVAL_MINUTES} min")
        logger.info(f"   • Global indices: every {settings.STOCK_UPDATE_INTERVAL_MINUTES} min")
        logger.info(f"   • Romanian news: every {settings.SCRAPING_INTERVAL_MINUTES} min")
        logger.info(f"   • International news: every {settings.SCRAPING_INTERVAL_MINUTES} min")
        logger.info(f"   • Currency rates: every {settings.CURRENCY_UPDATE_INTERVAL_HOURS} hour")
        logger.info(f"   • Subscription expirations: daily at 9:00 AM")
        
        # Run all jobs once immediately
        asyncio.create_task(update_bvb_stocks_job())
        asyncio.create_task(update_global_indices_job())
        asyncio.create_task(fetch_news_job())
        asyncio.create_task(fetch_international_news_job())
        asyncio.create_task(update_currency_rates_job())
        asyncio.create_task(check_subscription_expirations_job())  # Check on startup too
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise

def stop_scheduler():
    """Stop scheduler"""
    try:
        scheduler.shutdown()
        logger.info("✅ Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
