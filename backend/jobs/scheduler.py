"""CRON Jobs Scheduler pentru actualizare automata"""
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz

BUCHAREST_TZ = pytz.timezone('Europe/Bucharest')

def _is_market_day() -> bool:
    """Verifică dacă e zi de bursă (Luni-Vineri)"""
    return datetime.now(BUCHAREST_TZ).weekday() < 5

from services.stock_service import StockService
from services.news_service import NewsService
from services.currency_service import CurrencyService
from services.notification_service import notification_service
from services.daily_summary_service import daily_summary_service
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
    """Job: Update BVB stocks from EODHD API (paid plan)"""
    try:
        logger.info("🔄 [JOB] Updating BVB stocks from EODHD API...")
        count = await stock_service.update_bvb_stocks()
        logger.info(f"✅ [JOB] BVB stocks updated from EODHD: {count} stocks")
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

async def check_price_alerts_job():
    """Job: Check price alerts and send notifications (doar in zilele de bursa)"""
    if not _is_market_day():
        return
    try:
        logger.info("🔄 [JOB] Checking price alerts...")
        results = await notification_service.check_price_alerts()
        logger.info(f"✅ [JOB] Price alerts check complete: checked={results['alerts_checked']}, sent={results['notifications_sent']}")
    except Exception as e:
        logger.error(f"❌ [JOB] Error checking price alerts: {e}")

async def check_watchlist_big_moves_job():
    """Job: Verifică mișcările mari (>5%) din watchlist-uri (doar in zilele de bursa)"""
    if not _is_market_day():
        return
    try:
        logger.info("🔄 [JOB] Checking watchlist big moves...")
        results = await notification_service.check_watchlist_big_moves()
        logger.info(f"✅ [JOB] Watchlist big moves: checked={results['checked']}, emails={results['emails_sent']}")
    except Exception as e:
        logger.error(f"❌ [JOB] Error checking watchlist big moves: {e}")


async def send_daily_summary_job():
    """
    Job: Generează rezumatul zilnic și îl trimite abonaților.
    
    FLOW:
    1. Generează și salvează rezumatul în MongoDB (o singură dată)
    2. Trimite emailurile către abonați folosind rezumatul salvat
    
    Rulează la 18:10 Bucharest time (după închiderea BVB la 18:00)
    """
    try:
        logger.info("📧 [JOB] Starting daily summary generation...")
        
        # Pas 1: Generează și salvează rezumatul în DB
        summary = await daily_summary_service.generate_and_save_daily_summary()
        if not summary:
            logger.error("❌ [JOB] Failed to generate daily summary")
            return
        
        logger.info("✅ [JOB] Daily summary generated and saved to DB")
        
        # Pas 2: Trimite emailurile către abonați
        results = await daily_summary_service.send_to_all_subscribers()
        logger.info(f"✅ [JOB] Daily summary emails: sent={results['sent']}, failed={results['failed']}, skipped={results['skipped']}")
        
    except Exception as e:
        logger.error(f"❌ [JOB] Error in daily summary job: {e}")

async def update_screener_cache_job():
    """Job: Actualizează cache-ul Screener PRO (rulează în fundal la fiecare 45 min)"""
    try:
        from routes.screener_pro import run_scan_and_cache
        logger.info("🔄 [JOB] Updating Screener PRO cache...")
        await run_scan_and_cache()
        logger.info("✅ [JOB] Screener PRO cache updated")
    except Exception as e:
        logger.error(f"❌ [JOB] Error updating screener cache: {e}")

async def scrape_bvb_dividends_job():
    """Job: Scrape dividende de pe BVB.ro (1x/zi dimineața)"""
    try:
        from scrapers.bvb_dividend_scraper import run_full_scrape
        logger.info("🔄 [JOB] Scraping BVB.ro dividends & calendar...")
        result = await run_full_scrape()
        logger.info(f"✅ [JOB] BVB scrape done: {result['dividends']} dividends, {result['calendar']} events")
    except Exception as e:
        logger.error(f"❌ [JOB] Error scraping BVB.ro: {e}")


async def refresh_fundamentals_cache_job():
    """
    Job: Actualizează cache-ul zilnic de fundamentale (P/E, ROE, EPS, D/E din EODHD).
    Date reale, fără estimări. Se rulează o dată pe zi la 8:00 AM.
    """
    try:
        from routes.screener_pro import refresh_fundamentals_daily_cache
        logger.info("🔄 [JOB] Refreshing daily fundamentals cache (P/E, ROE, EPS, D/E)...")
        await refresh_fundamentals_daily_cache()
        logger.info("✅ [JOB] Daily fundamentals cache refreshed")
    except Exception as e:
        logger.error(f"❌ [JOB] Error refreshing fundamentals cache: {e}")


async def scrape_bvb_fundamentals_job():
    """
    Job: Scrape fundamentale BVB.ro (PER, dividend, market cap, 52w) pentru toate acțiunile.
    Date oficiale BVB.ro — nu se schimbă la minut, scraping 2x/zi e suficient.
    """
    try:
        from scrapers.bvb_fundamentals_scraper import run_fundamentals_scrape
        logger.info("🔄 [JOB] Scraping BVB.ro fundamentals (PER, dividend, market cap, 52w)...")
        result = await run_fundamentals_scrape()
        logger.info(f"✅ [JOB] BVB fundamentals done: {result['count']} stocks")
    except Exception as e:
        logger.error(f"❌ [JOB] Error scraping BVB fundamentals: {e}")


def start_scheduler():
    """Start all scheduled jobs"""
    try:
        # Job 1: Update BVB stocks from EODHD API (every 15 minutes - real data)
        scheduler.add_job(
            update_bvb_stocks_job,
            trigger=IntervalTrigger(minutes=15),
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
        
        # Job 7: Check price alerts (every 5 minutes - after stock update)
        scheduler.add_job(
            check_price_alerts_job,
            trigger=IntervalTrigger(minutes=5),  # Verifică alertele la fiecare 5 minute
            id='check_price_alerts',
            name='Check Price Alerts',
            replace_existing=True
        )

        # Job 7b: Check watchlist big moves (every 30 min during market hours)
        scheduler.add_job(
            check_watchlist_big_moves_job,
            trigger=IntervalTrigger(minutes=30),
            id='check_watchlist_big_moves',
            name='Check Watchlist Big Moves (>5%)',
            replace_existing=True
        )
        
        # Job 8: Send daily summary email (Mon-Fri at 18:05 Bucharest time - after BVB close)
        scheduler.add_job(
            send_daily_summary_job,
            trigger=CronTrigger(hour=18, minute=5, day_of_week='mon-fri', timezone='Europe/Bucharest'),
            id='send_daily_summary',
            name='Send Daily Market Summary',
            replace_existing=True
        )
        
        # Job 9: Update Screener PRO cache (every 45 minutes - background scan)
        scheduler.add_job(
            update_screener_cache_job,
            trigger=IntervalTrigger(minutes=45),
            id='update_screener_cache',
            name='Update Screener PRO Cache',
            replace_existing=True
        )
        
        # Job 10: Scrape BVB.ro dividends (daily at 7:00 AM Bucharest time)
        scheduler.add_job(
            scrape_bvb_dividends_job,
            trigger=CronTrigger(hour=7, minute=0, timezone='Europe/Bucharest'),
            id='scrape_bvb_dividends',
            name='Scrape BVB.ro Dividends',
            replace_existing=True
        )

        # Job 11: Refresh daily fundamentals cache (daily at 8:00 AM Bucharest time)
        # Salvează P/E, ROE, EPS, D/E pentru toate acțiunile BVB (date reale, fără estimări)
        scheduler.add_job(
            refresh_fundamentals_cache_job,
            trigger=CronTrigger(hour=8, minute=0, timezone='Europe/Bucharest'),
            id='refresh_fundamentals_cache',
            name='Refresh Daily Fundamentals Cache',
            replace_existing=True
        )

        # Job 12: Scrape BVB.ro fundamentals (2x/zi: 07:30 + 18:30 Bucharest)
        # PER, dividend, market cap, 52w — date oficiale BVB.ro
        scheduler.add_job(
            scrape_bvb_fundamentals_job,
            trigger=CronTrigger(hour=7, minute=30, timezone='Europe/Bucharest'),
            id='scrape_bvb_fundamentals_morning',
            name='Scrape BVB.ro Fundamentals (Morning)',
            replace_existing=True
        )
        scheduler.add_job(
            scrape_bvb_fundamentals_job,
            trigger=CronTrigger(hour=18, minute=30, timezone='Europe/Bucharest'),
            id='scrape_bvb_fundamentals_evening',
            name='Scrape BVB.ro Fundamentals (Evening)',
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
        logger.info("   • Subscription expirations: daily at 9:00 AM")
        logger.info("   • Price alerts: every 5 min")
        logger.info("   • Daily summary email: daily at 18:05 (Europe/Bucharest)")
        logger.info("   • BVB.ro dividends scrape: daily at 7:00 AM (Europe/Bucharest)")
        logger.info("   • Fundamentals cache refresh: daily at 8:00 AM (Europe/Bucharest)")
        logger.info("   • BVB.ro fundamentals scrape: daily at 7:30 + 18:30 (Europe/Bucharest)")
        
        # DON'T run jobs immediately at startup - let the scheduler handle them
        # This prevents blocking the application startup
        # Jobs will run at their scheduled intervals starting from next trigger
        logger.info("✅ Jobs will start running at their scheduled intervals")
        
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
