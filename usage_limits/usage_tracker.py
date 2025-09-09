# usage_limits/usage_tracker.py - Simplified without batch processing or reservations

import logging
from datetime import datetime, timedelta
from django.utils import timezone

from .redis_client import RedisClient

logger = logging.getLogger(__name__)

class UsageTracker:
    """Simple usage tracker for individual processing"""
    
    @classmethod
    def _get_monthly_key(cls, user_id):
        """Get Redis key for user's monthly usage"""
        now = datetime.now()
        return f"usage:monthly:{user_id}:{now.year}:{now.month}"
    
    @classmethod
    def _get_yearly_reset_key(cls, user_id, period):
        """Get Redis key for yearly reset tracking"""
        return f"yearly_reset:{user_id}:{period}"
    
    @classmethod
    def _get_user_subscription(cls, user_id):
        """Get user subscription safely"""
        try:
            from django.contrib.auth import get_user_model
            from subscriptions.models import CustomerSubscription
            User = get_user_model()
            
            user = User.objects.get(id=user_id)
            return CustomerSubscription.objects.filter(
                user=user, 
                subscription_active=True
            ).first()
        except Exception:
            return None
    
    @classmethod
    def increment_usage(cls, user, count=1):
        """Simple atomic increment for individual processing"""
        if not user or not user.is_authenticated:
            return False
        
        redis_client = RedisClient.get_client()
        usage_key = cls._get_monthly_key(user.id)
        
        try:
            # Atomic check-and-increment
            with redis_client.pipeline() as pipe:
                while True:
                    try:
                        pipe.watch(usage_key)
                        
                        # Get current values
                        current_usage = int(pipe.get(usage_key) or 0)
                        user_limit = cls.get_user_limit(user)
                        
                        # Check if increment would exceed limit
                        if current_usage + count > user_limit:
                            pipe.unwatch()
                            logger.warning(f"Usage limit exceeded for user {user.id}: {current_usage + count} > {user_limit}")
                            return False
                        
                        # Execute atomic increment
                        pipe.multi()
                        pipe.incrby(usage_key, count)
                        
                        # Set expiry if needed
                        ttl = redis_client.ttl(usage_key)
                        if ttl < 0:
                            cls._set_monthly_expiry(pipe, usage_key)
                        
                        pipe.execute()
                        
                        logger.info(f"Usage incremented for user {user.id}: +{count} (total: {current_usage + count}/{user_limit})")
                        return True
                        
                    except redis_client.WatchError:
                        # Key was modified during transaction, retry
                        logger.debug(f"Redis watch error for user {user.id}, retrying")
                        continue
                        
        except Exception as e:
            logger.error(f"Error incrementing usage for user {user.id}: {str(e)}")
            return False
    
    @classmethod
    def _set_monthly_expiry(cls, pipe, usage_key):
        """Set expiry to end of month with buffer"""
        now = datetime.now()
        # Calculate end of current month
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        
        end_of_month = next_month - timedelta(days=1)
        seconds_until_end = int((end_of_month - now).total_seconds())
        
        # Add 24 hour buffer to avoid early expiration
        pipe.expire(usage_key, seconds_until_end + 86400)
    
    @classmethod
    def get_current_usage(cls, user):
        """Get current monthly usage"""
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
        """Get user's monthly limit based on subscription"""
        if not user or not user.is_authenticated:
            return 3  # Free tier default
        
        try:
            subscription = cls._get_user_subscription(user.id)
            
            if not subscription or not subscription.subscription_active:
                return 3  # Free tier
            
            # Try to get limit from Product model first
            plan_id = subscription.plan_id
            if plan_id:
                try:
                    from subscriptions.models import Price
                    price = Price.objects.select_related('product').get(stripe_id=plan_id)
                    if price.product.tokens > 0:
                        return price.product.tokens
                except:
                    pass
            
            # Fallback to tier-based limits
            from .tier_config import TierLimits
            tier = TierLimits.get_tier_from_price_id(plan_id)
            limit = TierLimits.get_limit_for_tier(tier)
            
            return limit
            
        except Exception as e:
            logger.error(f"Error determining limit for user {user.id}: {str(e)}")
            return 3
    
    @classmethod
    def get_usage_data(cls, user):
        """Get simplified usage data without Stripe API calls"""
        if not user or not user.is_authenticated:
            return {
                'current': 0,
                'limit': 3,
                'remaining': 3,
                'percentage': 0,
                'subscription_type': 'free'
            }
        
        current = cls.get_current_usage(user)
        limit = cls.get_user_limit(user)
        remaining = max(0, limit - current)
        percentage = int((current / limit) * 100) if limit > 0 else 100
        
        # Simplified subscription type - no Stripe API call needed
        subscription_type = 'free'
        
        try:
            subscription = cls._get_user_subscription(user.id)
            if subscription and subscription.subscription_active:
                subscription_type = 'active'
        except Exception:
            pass
        
        return {
            'current': current,
            'limit': limit,
            'remaining': remaining,
            'percentage': percentage,
            'subscription_type': subscription_type
        }
    
    @classmethod
    def reset_usage(cls, user):
        """Reset usage for a user (used for yearly subscribers)"""
        if not user or not user.is_authenticated:
            return False
        
        redis_client = RedisClient.get_client()
        usage_key = cls._get_monthly_key(user.id)
        
        try:
            redis_client.set(usage_key, 0)
            cls._set_monthly_expiry(redis_client, usage_key)
            
            logger.info(f"Usage reset for user {user.id}")
            return True
        except Exception as e:
            logger.error(f"Error resetting usage for user {user.id}: {str(e)}")
            return False
    
    @classmethod
    def check_yearly_reset_eligible(cls, user):
        """Check if yearly subscriber is eligible for reset"""
        try:
            subscription = cls._get_user_subscription(user.id)
            if not subscription or not subscription.subscription_active:
                return False, "No active subscription"
            
            if not subscription.stripe_subscription_id:
                return False, "No Stripe subscription ID"
            
            import stripe
            from django.conf import settings
            stripe.api_key = settings.STRIPE_SECRET_KEY
            stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            
            if not (stripe_sub.items.data and stripe_sub.items.data[0].plan.interval == 'year'):
                return False, "Not a yearly subscription"
            
            # Calculate subscription periods (11 resets after initial)
            start_date = datetime.fromtimestamp(stripe_sub.created)
            start_date = timezone.make_aware(start_date)
            now = timezone.now()
            days_since_start = (now - start_date).days
            
            if days_since_start < 30:
                return False, f"Too early - only {days_since_start} days since start"
            
            # Period 1-11 (11 resets after initial purchase)
            period = min(days_since_start // 30, 11)
            
            if period > 11:
                return False, "All yearly resets completed (11 resets)"
            
            # Check if already reset this period
            reset_key = cls._get_yearly_reset_key(user.id, period)
            redis_client = RedisClient.get_client()
            if redis_client.get(reset_key):
                return False, f"Already reset for period {period}"
            
            return True, f"Eligible for period {period} reset"
            
        except Exception as e:
            logger.error(f"Error checking yearly reset eligibility for user {user.id}: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @classmethod
    def mark_yearly_reset_complete(cls, user, period):
        """Mark yearly reset as completed for a period"""
        try:
            reset_key = cls._get_yearly_reset_key(user.id, period)
            redis_client = RedisClient.get_client()
            # Mark for 35 days to prevent duplicate resets
            redis_client.setex(reset_key, 35 * 24 * 60 * 60, timezone.now().isoformat())
            logger.info(f"Marked yearly reset complete for user {user.id}, period {period}")
            return True
        except Exception as e:
            logger.error(f"Error marking yearly reset complete for user {user.id}: {str(e)}")
        return False