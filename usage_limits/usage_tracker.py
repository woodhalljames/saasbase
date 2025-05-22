import time
import logging
from datetime import datetime, timedelta
from django.utils import timezone

from .redis_client import RedisClient

logger = logging.getLogger(__name__)

class UsageTracker:
    """Track usage per user with Redis backend"""
    
    @classmethod
    def _get_monthly_key(cls, user_id):
        """Get Redis key for user's monthly usage - resets each month"""
        now = datetime.now()
        return f"usage:monthly:{user_id}:{now.year}:{now.month}"
    
    @classmethod
    def increment_usage(cls, user, count=1):
        """Increment usage for a user by the specified count"""
        if not user or not user.is_authenticated:
            return False
        
        redis_client = RedisClient.get_client()
        usage_key = cls._get_monthly_key(user.id)
        
        # Get current usage
        current_usage = cls.get_current_usage(user)
        
        # Get user's limit based on subscription
        limit = cls.get_user_limit(user)
        
        # Check if incrementing would exceed the limit
        if current_usage + count > limit:
            return False
        
        # Increment usage counter
        try:
            redis_client.incrby(usage_key, count)
            
            # Set expiry if this is a new key
            ttl = redis_client.ttl(usage_key)
            if ttl < 0:
                # Set expiry to the end of the current month
                now = datetime.now()
                next_month = now.replace(day=28) + timedelta(days=4)  # Guarantees next month
                end_of_month = next_month.replace(day=1) - timedelta(days=1)
                seconds_until_month_end = int((end_of_month - now).total_seconds())
                # Add a buffer of one day to ensure it doesn't expire too early
                redis_client.expire(usage_key, seconds_until_month_end + 86400)
                
            return True
        except Exception as e:
            logger.error(f"Error incrementing usage for user {user.id}: {str(e)}")
            return False
    
    @classmethod
    def get_current_usage(cls, user):
        """Get current usage for a user in the current month"""
        if not user or not user.is_authenticated:
            return 0
        
        redis_client = RedisClient.get_client()
        usage_key = cls._get_monthly_key(user.id)
        
        try:
            usage = redis_client.get(usage_key)
            return int(usage) if usage else 0
        except Exception as e:
            logger.error(f"Error getting usage for user {user.id}: {str(e)}")
            return 0
    
    @classmethod
    def get_user_limit(cls, user):
        """Get the monthly usage limit for a user based on their subscription"""
        if not user or not user.is_authenticated:
            return 3  # Default free tier limit
        
        try:
            # Try to get subscription
            subscription = getattr(user, 'subscription', None)
            if not subscription or not subscription.subscription_active:
                return 3  # Free tier limit
            
            # Try to get the limit from the Product model first
            plan_id = subscription.plan_id
            if plan_id:
                try:
                    from subscriptions.models import Price
                    price = Price.objects.select_related('product').get(stripe_id=plan_id)
                    product_tokens = price.product.tokens
                    if product_tokens > 0:
                        logger.debug(f"Using product tokens limit: {product_tokens} for user {user.id}")
                        return product_tokens
                except Price.DoesNotExist:
                    logger.warning(f"Price not found for plan_id: {plan_id}")
                except Exception as e:
                    logger.error(f"Error getting product tokens: {str(e)}")
            
            # Fallback to tier-based limits
            from .tier_config import TierLimits
            tier = TierLimits.get_tier_from_price_id(plan_id)
            limit = TierLimits.get_limit_for_tier(tier)
            logger.debug(f"Using tier-based limit: {limit} for tier {tier}, user {user.id}")
            return limit
            
        except Exception as e:
            logger.error(f"Error determining limit for user {user.id}: {str(e)}")
            return 3  # Free tier fallback
    
    @classmethod
    def get_usage_data(cls, user):
        """Get complete usage data for a user"""
        if not user or not user.is_authenticated:
            return {
                'current': 0,
                'limit': 3,
                'remaining': 3,
                'percentage': 0
            }
        
        current = cls.get_current_usage(user)
        limit = cls.get_user_limit(user)
        remaining = max(0, limit - current)
        percentage = int((current / limit) * 100) if limit > 0 else 100
        
        return {
            'current': current,
            'limit': limit,
            'remaining': remaining,
            'percentage': percentage
        }
    
    @classmethod
    def reset_usage(cls, user):
        """Reset usage counter for a user"""
        if not user or not user.is_authenticated:
            return False
        
        redis_client = RedisClient.get_client()
        usage_key = cls._get_monthly_key(user.id)
        
        try:
            redis_client.set(usage_key, 0)
            return True
        except Exception as e:
            logger.error(f"Error resetting usage for user {user.id}: {str(e)}")
            return False