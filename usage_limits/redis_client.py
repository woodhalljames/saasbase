# usage_limits/redis_client.py
import redis
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Singleton pattern for Redis connection
class RedisClient:
    _instance = None
    
    @classmethod
    def get_client(cls):
        if cls._instance is None:
            try:
                redis_kwargs = {
                    'decode_responses': True,  # Return strings instead of bytes
                }
                
                # Add SSL if needed
                if settings.REDIS_RATE_LIMIT_SSL:
                    redis_kwargs['ssl'] = True
                    redis_kwargs['ssl_cert_reqs'] = None
                
                cls._instance = redis.from_url(
                    settings.REDIS_RATE_LIMIT_URL, 
                    **redis_kwargs
                )
                logger.info("Redis client for rate limiting initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Redis client: {str(e)}")
                # Fallback to dummy client that won't block the application
                cls._instance = DummyRedisClient()
                
        return cls._instance


# Dummy client that doesn't do anything but doesn't break the app if Redis is down
class DummyRedisClient:
    """Dummy Redis client that doesn't break the app if Redis is unavailable"""
    
    def incr(self, *args, **kwargs):
        return 0
        
    def get(self, *args, **kwargs):
        return 0
    
    def set(self, *args, **kwargs):
        pass
        
    def expire(self, *args, **kwargs):
        pass

    def ttl(self, *args, **kwargs):
        return 0