# usage_limits/usage_tracker.py - Simplified without batch processing or reservations

import logging
from datetime import datetime, timedelta
from django.utils import timezone

from .redis_client import RedisClient

logger = logging.getLogger(__name__)

class UsageTracker:
    """Simple usage tracker for individual processing"""
    
    @classmethod
    def _get_usage_key(cls, user_id):
        """Get Redis key for user's usage - no auto-reset"""
        return f"usage:{user_id}"
    
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
        usage_key = cls._get_usage_key(user.id)
        
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
                        # No expiry - tokens don't auto-reset
                        
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
    def get_current_usage(cls, user):
        """Get current monthly usage"""
        if not user or not user.is_authenticated:
            return 0
        
        redis_client = RedisClient.get_client()
        usage_key = cls._get_usage_key(user.id)
        
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
            return 3  # Free tier default - UPDATED from 2 to 3
        
        try:
            subscription = cls._get_user_subscription(user.id)
            
            if not subscription or not subscription.subscription_active:
                return 3  # Free tier - UPDATED from 2 to 3
            
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
            return 3  # UPDATED from 2 to 3
    
    @classmethod
    def get_usage_data(cls, user):
        """Get simplified usage data without Stripe API calls"""
        if not user or not user.is_authenticated:
            return {
                'current': 0,
                'limit': 3,  # UPDATED from 2 to 3
                'remaining': 3,  # UPDATED from 2 to 3
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
        usage_key = cls._get_usage_key(user.id)
        
        try:
            redis_client.set(usage_key, 0)
            # No expiry - tokens persist until payment resets them
            
            logger.info(f"Usage reset for user {user.id}")
            return True
        except Exception as e:
            logger.error(f"Error resetting usage for user {user.id}: {str(e)}")
            return False
    
    @classmethod
    def check_yearly_reset_eligible(cls, user):
        """FIXED: Check if yearly subscriber is eligible for reset"""
        try:
            subscription = cls._get_user_subscription(user.id)
            if not subscription or not subscription.subscription_active:
                return False, "No active subscription"
            
            if not subscription.stripe_subscription_id:
                return False, "No Stripe subscription ID"
            
            import stripe
            from django.conf import settings
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Use the FIXED method to check if subscription is yearly
            is_yearly = cls._check_subscription_yearly_safe(subscription.stripe_subscription_id)
            
            if not is_yearly:
                return False, "Not a yearly subscription"
            
            # Get subscription start date
            stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            
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
    def _check_subscription_yearly_safe(cls, stripe_subscription_id):
        """FIXED: Safely check if subscription is yearly"""
        try:
            import stripe
            from django.conf import settings
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Method 1: Use separate SubscriptionItem.list call (most reliable)
            try:
                items = stripe.SubscriptionItem.list(
                    subscription=stripe_subscription_id,
                    expand=['data.price']
                )
                
                if items.data:
                    item = items.data[0]
                    if hasattr(item.price, 'recurring') and item.price.recurring:
                        return item.price.recurring.interval == 'year'
                
            except Exception as e:
                logger.debug(f"SubscriptionItem.list failed for {stripe_subscription_id}: {str(e)}")
            
            # Method 2: Use bracket notation to avoid items() method conflict
            try:
                stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
                items_data = stripe_sub['items']['data']  # FIXED: bracket notation
                
                if items_data:
                    item = items_data[0]
                    if 'price' in item and 'recurring' in item['price']:
                        return item['price']['recurring']['interval'] == 'year'
                
            except Exception as e:
                logger.debug(f"Bracket notation failed for {stripe_subscription_id}: {str(e)}")
            
            return False
            
        except Exception as e:
            logger.error(f"All methods failed for subscription {stripe_subscription_id}: {str(e)}")
            return False


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
    
    @classmethod
    def reset_usage_on_payment(cls, user):
        """
        Reset usage when invoice.paid webhook fires.
        This gives users a fresh token allocation for their billing period.
        """
        if not user or not user.is_authenticated:
            logger.warning("Cannot reset usage: invalid user")
            return False
        
        redis_client = RedisClient.get_client()
        usage_key = cls._get_usage_key(user.id)
        
        try:
            # Get current state for logging
            old_usage = int(redis_client.get(usage_key) or 0)
            user_limit = cls.get_user_limit(user)
            
            # Reset to 0
            redis_client.set(usage_key, 0)
            
            logger.info(
                f"Payment received - reset usage for user {user.id} "
                f"(was: {old_usage}/{user_limit}, now: 0/{user_limit})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error resetting usage on payment for user {user.id}: {str(e)}")
            return False
        
    @classmethod
    def reset_to_free_tier(cls, user):
        """
        Reset user to free tier when subscription becomes inactive.
        Sets usage to 0 and limits them to free tier (3 tokens).
        
        Called when:
        - Subscription is canceled (subscription.deleted)
        - Payment fails and subscription becomes past_due/unpaid
        - Subscription status changes to inactive
        
        This ensures users who stop paying only have free tier access.
        """
        if not user or not user.is_authenticated:
            logger.warning("Cannot reset to free tier: invalid user")
            return False
        
        redis_client = RedisClient.get_client()
        usage_key = cls._get_usage_key(user.id)
        
        try:
            # Get current state for logging
            old_usage = int(redis_client.get(usage_key) or 0)
            old_limit = cls.get_user_limit(user)
            free_tier_limit = 3  # Free tier limit
            
            # Reset usage to 0 (giving them a fresh start with free tier)
            redis_client.set(usage_key, 0)
            # No expiry - tokens don't auto-reset
            
            logger.warning(
                f"🔓 Subscription inactive - reset {user.email} to free tier "
                f"(was: {old_usage}/{old_limit} on paid plan, now: 0/{free_tier_limit} on free tier)"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error resetting user {user.id} to free tier: {str(e)}")
            return False
