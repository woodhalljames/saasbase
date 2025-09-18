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
            

      