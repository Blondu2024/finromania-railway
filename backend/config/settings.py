"""Global settings and configuration"""
import os
from dotenv import load_dotenv

load_dotenv(override=False)

class Settings:
    """Application settings"""
    
    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Database
    MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'stock_news_romania')
    
    # API Keys
    API_KEY_FMP = os.getenv('API_KEY_FMP')
    API_KEY_TWELVEDATA = os.getenv('API_KEY_TWELVEDATA')
    API_KEY_NEWSAPI = os.getenv('API_KEY_NEWSAPI')
    EMERGENT_UNIVERSAL_KEY = os.getenv('EMERGENT_UNIVERSAL_KEY')  # Legacy - use OPENAI_API_KEY instead
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # AI Settings
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-4o-mini')
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', '2000'))
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', '0.7'))
    
    # BVB Settings
    BVB_MODE = os.getenv('BVB_MODE', 'mock')  # 'mock' or 'real'
    
    # CRON Settings
    SCRAPING_INTERVAL_MINUTES = int(os.getenv('SCRAPING_INTERVAL_MINUTES', '15'))
    STOCK_UPDATE_INTERVAL_MINUTES = int(os.getenv('STOCK_UPDATE_INTERVAL_MINUTES', '5'))
    CURRENCY_UPDATE_INTERVAL_HOURS = int(os.getenv('CURRENCY_UPDATE_INTERVAL_HOURS', '1'))
    
    # Feature Flags
    ENABLE_BVB = os.getenv('ENABLE_BVB', 'true').lower() == 'true'
    ENABLE_GLOBAL_MARKETS = os.getenv('ENABLE_GLOBAL_MARKETS', 'true').lower() == 'true'
    ENABLE_NEWS = os.getenv('ENABLE_NEWS', 'true').lower() == 'true'
    ENABLE_AI_REWRITING = os.getenv('ENABLE_AI_REWRITING', 'true').lower() == 'true'

settings = Settings()
