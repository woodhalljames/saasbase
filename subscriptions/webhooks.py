# subscriptions/webhooks.py - REPLACE the entire webhooks.py file with this
import logging
from django.db import transaction
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
import json

from .models import CustomerSubscription, Product, Price

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
        logger.error(f"Error processing {event.type}: {str(e)}", exc_info=True)
    
    return HttpResponse(status=200)

def handle_checkout_session(session):
    """Process checkout.session.completed event with improved plan_id handling"""
    customer_id = session.customer
    subscription_id = session.subscription
    
    if not customer_id:
        logger.warning("Checkout session has no customer ID")
        return
    
    logger.info(f"Processing checkout session for customer {customer_id}")
    
    try:
        with transaction.atomic():
            # Set Stripe API key
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Get or create customer subscription
            customer_subscription, created = CustomerSubscription.objects.get_or_create(
                stripe_customer_id=customer_id,
                defaults={
                    'subscription_active': False
                }
            )
            
            if subscription_id:
                # Fetch full subscription details from Stripe
                stripe_sub = stripe.Subscription.retrieve(
                    subscription_id,
                    expand=['items.data.price.product']
                )
                
                # Update subscription details
                customer_subscription.stripe_subscription_id = subscription_id
                customer_subscription.subscription_active = True
                customer_subscription.status = stripe_sub.status
                
                # Extract and save plan_id
                if stripe_sub.items and stripe_sub.items.data:
                    price_item = stripe_sub.items.data[0]
                    customer_subscription.plan_id = price_item.price.id
                    
                    # Also sync the product and price data locally
                    sync_product_and_price(price_item.price)
                    
                    logger.info(f"Set plan_id to {price_item.price.id} for subscription {subscription_id}")
                
                customer_subscription.save()
                logger.info(f"Successfully processed checkout for customer {customer_id}")
                
    except Exception as e:
        logger.error(f"Error processing checkout session: {str(e)}", exc_info=True)

def sync_product_and_price(stripe_price):
    """Sync a Stripe price and its product to local database"""
    try:
        # Sync product
        product_data = stripe_price.product
        product, created = Product.objects.update_or_create(
            stripe_id=product_data.id,
            defaults={
                'name': product_data.name,
                'description': product_data.description or '',
                'active': product_data.active,
            }
        )
        if created:
            logger.info(f"Created new product: {product.name}")
        
        # Sync price
        price, created = Price.objects.update_or_create(
            stripe_id=stripe_price.id,
            defaults={
                'product': product,
                'active': stripe_price.active,
                'currency': stripe_price.currency,
                'amount': stripe_price.unit_amount,
                'interval': stripe_price.recurring.interval,
                'interval_count': stripe_price.recurring.interval_count,
            }
        )
        if created:
            logger.info(f"Created new price: {price}")
            
    except Exception as e:
        logger.error(f"Error syncing product/price: {str(e)}")

def handle_subscription_created(subscription):
    """Process customer.subscription.created event"""
    customer_id = subscription.customer
    
    try:
        with transaction.atomic():
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Get or create customer subscription
            customer_subscription, created = CustomerSubscription.objects.get_or_create(
                stripe_customer_id=customer_id,
                defaults={
                    'subscription_active': False
                }
            )
            
            # Update subscription details
            customer_subscription.stripe_subscription_id = subscription.id
            customer_subscription.status = subscription.status
            customer_subscription.subscription_active = subscription.status in ['active', 'trialing']
            
            # Extract plan_id from subscription items
            if subscription.items and subscription.items.data:
                price_item = subscription.items.data[0]
                customer_subscription.plan_id = price_item.price.id
                
                # Fetch and sync product details
                stripe_price = stripe.Price.retrieve(
                    price_item.price.id,
                    expand=['product']
                )
                sync_product_and_price(stripe_price)
                
                logger.info(f"Set plan_id to {price_item.price.id} for new subscription {subscription.id}")
            
            customer_subscription.save()
            logger.info(f"Created subscription {subscription.id} for customer {customer_id}")
            
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}", exc_info=True)

def handle_subscription_updated(subscription):
    """Process customer.subscription.updated event"""
    customer_id = subscription.customer
    
    try:
        with transaction.atomic():
            customer_subscription = CustomerSubscription.objects.get(
                stripe_customer_id=customer_id
            )
            
            # Update subscription details
            customer_subscription.status = subscription.status
            customer_subscription.subscription_active = subscription.status in ['active', 'trialing']
            
            # Update plan_id if items exist
            if subscription.items and subscription.items.data:
                price_item = subscription.items.data[0]
                customer_subscription.plan_id = price_item.price.id
                logger.info(f"Updated plan_id to {price_item.price.id} for subscription {subscription.id}")
            
            customer_subscription.save()
            logger.info(f"Updated subscription {subscription.id} for customer {customer_id}")
            
    except CustomerSubscription.DoesNotExist:
        logger.warning(f"Subscription updated for unknown customer: {customer_id}")
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}", exc_info=True)

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
        logger.error(f"Error deleting subscription: {str(e)}", exc_info=True)

def handle_invoice_paid(invoice):
    """Process invoice.paid event"""
    customer_id = invoice.customer
    
    try:
        customer_subscription = CustomerSubscription.objects.get(
            stripe_customer_id=customer_id
        )
        
        # Update status if this was a late payment
        if customer_subscription.status in ['past_due', 'unpaid', 'incomplete']:
            customer_subscription.status = 'active'
            customer_subscription.subscription_active = True
            customer_subscription.save()
            logger.info(f"Reactivated subscription for customer {customer_id}")
            
    except CustomerSubscription.DoesNotExist:
        logger.warning(f"Payment received for unknown customer: {customer_id}")
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}", exc_info=True)