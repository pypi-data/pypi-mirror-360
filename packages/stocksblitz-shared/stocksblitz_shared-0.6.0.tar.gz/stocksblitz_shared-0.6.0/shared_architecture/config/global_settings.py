from shared_architecture.config.config_loader import config_loader
import os

DEFAULT_CURRENCY = config_loader.get("DEFAULT_CURRENCY", "INR")
DEFAULT_TIMEZONE = config_loader.get("DEFAULT_TIMEZONE", "Asia/Kolkata")
DEFAULT_LOCALE = config_loader.get("DEFAULT_LOCALE", "en_IN")

class Settings:
    """Global settings for RBAC system."""
    
    def __init__(self):
        self.USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.TRADE_SERVICE_URL = os.getenv("TRADE_SERVICE_URL", "http://localhost:8004")
        self.TICKER_SERVICE_URL = os.getenv("TICKER_SERVICE_URL", "http://localhost:8001")

def get_settings():
    """Get global settings instance."""
    return Settings()
