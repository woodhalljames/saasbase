import logging
from django.db import transaction
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe

from .models import CustomerSubscription

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    logger.info(f"Received webhook - signature: {sig_header[:10] if sig_header else 'None'}")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"Webhook verified: {event.type}")
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)
    
    # Handle the event
    try:
        if event.type == 'checkout.session.completed':
            handle_checkout_session(event.data.object)
        elif event.type == 'customer.subscription.created':
            handle_subscription_created(event.data.object)
        elif event.type == 'customer.subscription.updated':
            handle_subscription_updated(event.data.object)
        elif event.type == 'customer.subscription.deleted':
            handle_subscription_deleted(event.data.object)
        elif event.type == 'invoice.paid':
            handle_invoice_paid(event.data.object)
    except Exception as e:
        logger.error(f"Error processing {event.type}: {str(e)}")
        # We still return 200 so Stripe doesn't retry
    
    return HttpResponse(status=200)

def handle_checkout_session(session):
    """Process checkout.session.completed event"""
    customer_id = session.customer
    
    if not customer_id:
        logger.warning("Checkout session has no customer ID")
        return
    
    try:
        with transaction.atomic():
            customer_subscription = CustomerSubscription.objects.get(
                stripe_customer_id=customer_id
            )
            
            if session.subscription:
                customer_subscription.stripe_subscription_id = session.subscription
                customer_subscription.save()
                logger.info(f"Updated subscription ID to {session.subscription} for customer {customer_id}")
    except CustomerSubscription.DoesNotExist:
        logger.warning(f"No customer subscription found for customer {customer_id}")
    except Exception as e:
        logger.error(f"Error processing checkout session: {str(e)}")

def handle_subscription_created(subscription):
    """Process customer.subscription.created event"""
    customer_id = subscription.customer
    
    try:
        with transaction.atomic():
            customer_subscription = CustomerSubscription.objects.get(
                stripe_customer_id=customer_id
            )
            
            customer_subscription.stripe_subscription_id = subscription.id
            customer_subscription.status = subscription.status
            
            # Set plan ID from the first item
            if subscription.items and len(subscription.items.data) > 0:
                item = subscription.items.data[0]
                customer_subscription.plan_id = item.price.id
            
            # Check if subscription is active
            customer_subscription.subscription_active = subscription.status in ['active', 'trialing']
            customer_subscription.save()
            
            logger.info(f"Created subscription {subscription.id} for customer {customer_id}")
    except CustomerSubscription.DoesNotExist:
        logger.warning(f"Subscription created for unknown customer: {customer_id}")
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")

def handle_subscription_updated(subscription):
    """Process customer.subscription.updated event"""
    customer_id = subscription.customer
    
    try:
        with transaction.atomic():
            customer_subscription = CustomerSubscription.objects.get(
                stripe_customer_id=customer_id
            )
            
            # Store the old plan ID to check for tier changes
            old_plan_id = customer_subscription.plan_id
            
            customer_subscription.status = subscription.status
            
            # Update plan ID if items exist
            if subscription.items and len(subscription.items.data) > 0:
                item = subscription.items.data[0]
                customer_subscription.plan_id = item.price.id
            
            customer_subscription.subscription_active = subscription.status in ['active', 'trialing']
            customer_subscription.save()
            
            # Check for tier change
            if old_plan_id != customer_subscription.plan_id:
                logger.info(f"Subscription plan changed from {old_plan_id} to {customer_subscription.plan_id}")
                
                # Get the new tier's limit from TierLimits
                from usage_limits.tier_config import TierLimits
                old_tier = TierLimits.get_tier_from_price_id(old_plan_id)
                new_tier = TierLimits.get_tier_from_price_id(customer_subscription.plan_id)
                
                if old_tier != new_tier:
                    logger.info(f"User tier changed from {old_tier} to {new_tier}")
            
            logger.info(f"Updated subscription {subscription.id} for customer {customer_id}")
    except CustomerSubscription.DoesNotExist:
        logger.warning(f"Subscription updated for unknown customer: {customer_id}")
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}")

def handle_subscription_deleted(subscription):
    """Process customer.subscription.deleted event"""
    customer_id = subscription.customer
    
    try:
        with transaction.atomic():
            customer_subscription = CustomerSubscription.objects.get(
                stripe_customer_id=customer_id
            )
            
            customer_subscription.subscription_active = False
            customer_subscription.status = subscription.status
            customer_subscription.save()
            
            logger.info(f"Marked subscription {subscription.id} as inactive")
    except CustomerSubscription.DoesNotExist:
        logger.warning(f"Subscription deleted for unknown customer: {customer_id}")
    except Exception as e:
        logger.error(f"Error deleting subscription: {str(e)}")


# Add to subscriptions/webhooks.py
def handle_invoice_paid(invoice):
    """Process invoice.paid event to reset usage counters if payment was overdue"""
    customer_id = invoice.customer
    
    try:
        # Get customer subscription
        customer_subscription = CustomerSubscription.objects.get(
            stripe_customer_id=customer_id
        )
        
        # Only reset if this was a late payment (subscription was inactive)
        if customer_subscription.status in ['past_due', 'unpaid', 'incomplete']:
            from usage_limits.usage_tracker import UsageTracker
            UsageTracker.reset_usage(customer_subscription.user)
            logger.info(f"Reset usage for customer {customer_id} after late payment")
    except CustomerSubscription.DoesNotExist:
        logger.warning(f"Payment received for unknown customer: {customer_id}")
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")


