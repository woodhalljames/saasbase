# usage_limits/tasks.py - Automated yearly reset system

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from datetime import datetime
import stripe
import logging

from subscriptions.models import CustomerSubscription
from .usage_tracker import UsageTracker

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task(bind=True)
def process_automatic_yearly_resets(self):
    """
    Automatic daily task to check and reset yearly subscribers who are eligible.
    This replaces manual commands with full automation.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        # Get all active yearly subscriptions
        yearly_subscribers = get_yearly_subscribers()
        
        eligible_users = []
        reset_count = 0
        error_count = 0
        
        logger.info(f"Checking {len(yearly_subscribers)} yearly subscribers for resets")
        
        for user_data in yearly_subscribers:
            user = user_data['user']
            
            try:
                # Check if eligible for reset
                eligible, reason = UsageTracker.check_yearly_reset_eligible(user)
                
                if eligible:
                    eligible_users.append(user_data)
                    
                    # Perform the reset
                    if UsageTracker.reset_usage(user):
                        # Mark reset as completed
                        period = user_data['period']
                        UsageTracker.mark_yearly_reset_complete(user, period)
                        
                        reset_count += 1
                        logger.info(
                            f"Auto-reset successful: {user.username} "
                            f"(period {period}/11, was: {user_data['current_usage']}/{user_data['limit']})"
                        )
                    else:
                        error_count += 1
                        logger.error(f"Failed to reset usage for {user.username}")
                else:
                    logger.debug(f"User {user.username} not eligible: {reason}")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing yearly reset for {user.username}: {str(e)}")
        
        # Log summary
        logger.info(
            f"Yearly reset automation completed: "
            f"{reset_count} resets performed, {error_count} errors, "
            f"{len(eligible_users)} eligible users found"
        )
        
        return {
            'success': True,
            'reset_count': reset_count,
            'eligible_count': len(eligible_users),
            'error_count': error_count,
            'total_yearly_subscribers': len(yearly_subscribers)
        }
        
    except Exception as e:
        logger.error(f"Error in automatic yearly reset task: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@shared_task(bind=True)
def reset_single_user(self, user_id):
    """
    Reset a single user's usage (for support/admin use)
    """
    try:
        user = User.objects.get(id=user_id)
        
        if UsageTracker.reset_usage(user):
            logger.info(f"Manual reset successful for user {user.username}")
            return {
                'success': True,
                'user': user.username,
                'message': f'Usage reset for {user.username}'
            }
        else:
            logger.error(f"Manual reset failed for user {user.username}")
            return {
                'success': False,
                'error': f'Failed to reset usage for {user.username}'
            }
            
    except User.DoesNotExist:
        return {
            'success': False,
            'error': f'User with ID {user_id} not found'
        }
    except Exception as e:
        logger.error(f"Error in manual user reset: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def get_yearly_subscribers():
    """
    FIXED: Get all active yearly subscribers without the items() method conflict.
    """
    subscriptions = CustomerSubscription.objects.filter(
        subscription_active=True,
        stripe_subscription_id__isnull=False
    ).select_related('user')
    
    yearly_subscribers = []
    
    for subscription in subscriptions:
        if not subscription.user:
            continue
        
        try:
            # FIXED: Use safe method to check if subscription is yearly
            is_yearly = check_subscription_yearly_safe(subscription.stripe_subscription_id)
            
            if not is_yearly:
                logger.debug(f"User {subscription.user.username} not yearly")
                continue
            
            # Get subscription start date
            stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            
            # Calculate subscription periods
            start_date = datetime.fromtimestamp(stripe_sub.created)
            start_date = timezone.make_aware(start_date)
            now = timezone.now()
            days_since_start = (now - start_date).days
            
            # Period 1-11 (11 resets after initial purchase)
            period = min(days_since_start // 30, 11)
            
            # Get current usage data
            usage_data = UsageTracker.get_usage_data(subscription.user)
            
            yearly_subscribers.append({
                'user': subscription.user,
                'subscription': subscription,
                'start_date': start_date,
                'days_since_start': days_since_start,
                'period': period,
                'current_usage': usage_data['current'],
                'limit': usage_data['limit'],
                'stripe_sub_id': subscription.stripe_subscription_id
            })
            
            logger.info(f"Found yearly subscriber: {subscription.user.username} (period {period})")
            
        except Exception as e:
            logger.error(f"Error processing subscription for {subscription.user.username}: {str(e)}")
            continue
    
    return yearly_subscribers

def check_subscription_yearly_safe(stripe_subscription_id):
    """
    FIXED: Safely check if a subscription is yearly without the items() method conflict.
    """
    try:
        # Method 1: Use separate SubscriptionItem.list call (most reliable)
        try:
            items = stripe.SubscriptionItem.list(
                subscription=stripe_subscription_id,
                expand=['data.price']
            )
            
            if items.data:
                item = items.data[0]
                if hasattr(item.price, 'recurring') and item.price.recurring:
                    interval = item.price.recurring.interval
                    logger.debug(f"Subscription {stripe_subscription_id} interval: {interval}")
                    return interval == 'year'
            
        except Exception as e:
            logger.debug(f"SubscriptionItem.list failed for {stripe_subscription_id}: {str(e)}")
        
        # Method 2: Use bracket notation to avoid items() method conflict
        try:
            stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
            items_data = stripe_sub['items']['data']  # FIXED: Use bracket notation instead of .items.data
            
            if items_data:
                item = items_data[0]
                if 'price' in item and 'recurring' in item['price']:
                    interval = item['price']['recurring']['interval']
                    logger.debug(f"Subscription {stripe_subscription_id} interval (bracket): {interval}")
                    return interval == 'year'
            
        except Exception as e:
            logger.debug(f"Bracket notation failed for {stripe_subscription_id}: {str(e)}")
        
        # All methods failed
        return False
        
    except Exception as e:
        logger.error(f"All methods failed for subscription {stripe_subscription_id}: {str(e)}")
        return False


@shared_task(bind=True)
def cleanup_usage_system(self):
    """
    Daily cleanup task to maintain Redis health and clear old data.
    """
    try:
        from .redis_client import RedisClient
        redis_client = RedisClient.get_client()
        
        # Clean up expired yearly reset keys (older than 40 days)
        pattern = "yearly_reset:*"
        keys = redis_client.keys(pattern)
        
        cleaned_keys = 0
        for key in keys:
            ttl = redis_client.ttl(key)
            if ttl < 0:  # No expiry set
                # Set expiry for 40 days
                redis_client.expire(key, 40 * 24 * 60 * 60)
            elif ttl > 40 * 24 * 60 * 60:  # More than 40 days
                redis_client.expire(key, 40 * 24 * 60 * 60)
                cleaned_keys += 1
        
        logger.info(f"Usage cleanup completed: processed {len(keys)} keys, cleaned {cleaned_keys}")
        
        return {
            'success': True,
            'keys_processed': len(keys),
            'keys_cleaned': cleaned_keys
        }
        
    except Exception as e:
        logger.error(f"Error in usage cleanup task: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }