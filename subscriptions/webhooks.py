# saas_base/subscriptions/webhooks.py
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import CustomerSubscription

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)
    
    # Handle the event
    if event.type == 'checkout.session.completed':
        handle_checkout_session(event.data.object)
    elif event.type == 'customer.subscription.created':
        handle_subscription_created(event.data.object)
    elif event.type == 'customer.subscription.updated':
        handle_subscription_updated(event.data.object)
    elif event.type == 'customer.subscription.deleted':
        handle_subscription_deleted(event.data.object)
    
    return HttpResponse(status=200)

def handle_checkout_session(session):
    """Process checkout.session.completed event"""
    customer_id = session.get('customer')
    
    if not customer_id:
        return
    
    # Update customer record with checkout information
    try:
        customer_subscription = CustomerSubscription.objects.get(
            stripe_customer_id=customer_id
        )
        
        # If subscription was created via checkout, it will be in the session
        if session.get('subscription'):
            customer_subscription.stripe_subscription_id = session.get('subscription')
            customer_subscription.save()
    except CustomerSubscription.DoesNotExist:
        # This is an edge case, but we might want to handle it
        pass

def handle_subscription_created(subscription):
    """Process customer.subscription.created event"""
    customer_id = subscription.get('customer')
    
    try:
        customer_subscription = CustomerSubscription.objects.get(
            stripe_customer_id=customer_id
        )
        
        customer_subscription.stripe_subscription_id = subscription.get('id')
        customer_subscription.status = subscription.get('status')
        
        # Set plan ID from the first item
        if subscription.get('items') and subscription.get('items').get('data'):
            item = subscription.get('items').get('data')[0]
            customer_subscription.plan_id = item.get('price').get('id')
        
        # Check if subscription is active
        customer_subscription.subscription_active = subscription.get('status') in ['active', 'trialing']
        customer_subscription.save()
    except CustomerSubscription.DoesNotExist:
        # Subscription created for unknown customer
        pass

def handle_subscription_updated(subscription):
    """Process customer.subscription.updated event"""
    customer_id = subscription.get('customer')
    
    try:
        customer_subscription = CustomerSubscription.objects.get(
            stripe_customer_id=customer_id
        )
        
        customer_subscription.status = subscription.get('status')
        
        # Update plan ID if it has changed
        if subscription.get('items') and subscription.get('items').get('data'):
            item = subscription.get('items').get('data')[0]
            customer_subscription.plan_id = item.get('price').get('id')
        
        # Update active status
        customer_subscription.subscription_active = subscription.get('status') in ['active', 'trialing']
        customer_subscription.save()
    except CustomerSubscription.DoesNotExist:
        # Subscription update for unknown customer
        pass

def handle_subscription_deleted(subscription):
    """Process customer.subscription.deleted event"""
    customer_id = subscription.get('customer')
    
    try:
        customer_subscription = CustomerSubscription.objects.get(
            stripe_customer_id=customer_id
        )
        
        # Mark subscription as inactive
        customer_subscription.subscription_active = False
        customer_subscription.status = subscription.get('status')
        customer_subscription.save()
    except CustomerSubscription.DoesNotExist:
        # Subscription deleted for unknown customer
        pass