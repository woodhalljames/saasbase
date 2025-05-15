# usage_limits/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class UsageLimitsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usage_limits'
    
    def ready(self):
        # Test Redis connection on startup
        from .redis_client import RedisClient
        try:
            redis_client = RedisClient.get_client()
            redis_client.ping()
            logger.info("Redis connection for rate limiting is working")
        except Exception as e:
            logger.warning(f"Redis connection for rate limiting failed: {str(e)}")
            
        # Initialize tier configuration with price IDs from the database
        try:
            # Import here to avoid circular imports
            from .tier_config import TierLimits
            
            # Only run in main process (not in management commands etc.)
            import sys
            if not any(cmd in sys.argv for cmd in ['makemigrations', 'migrate', 'collectstatic']):
                TierLimits.initialize_from_db()
                logger.info("Tier configuration initialized with price IDs from database")
        except Exception as e:
            logger.warning(f"Failed to initialize tier configuration: {str(e)}")