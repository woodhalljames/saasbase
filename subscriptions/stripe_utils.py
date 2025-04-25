# saas_base/subscriptions/stripe_utils.py
import stripe
from django.conf import settings

# Configure Stripe API key
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
stripe.api_version = '2023-10-16'  # Use a specific API version for stability

def get_or_create_customer(user):
    """Create or retrieve a Stripe customer for the user"""
    from .models import CustomerSubscription
    
    try:
        # Check if we already have a customer record
        customer_subscription = CustomerSubscription.objects.get(user=user)
        
        if customer_subscription.stripe_customer_id:
            # Return existing customer
            return stripe.Customer.retrieve(customer_subscription.stripe_customer_id)
    except CustomerSubscription.DoesNotExist:
        # First time customer
        customer_subscription = CustomerSubscription(user=user)
    
    # Create a new Stripe customer
    customer = stripe.Customer.create(
        email=user.email,
        name=user.name or user.username,
        metadata={"user_id": str(user.id)}
    )
    
    # Update the local record
    customer_subscription.stripe_customer_id = customer.id
    customer_subscription.save()
    
    return customer

def create_checkout_session(user, price_id, success_url, cancel_url):
    """Create a Stripe Checkout Session for subscription"""
    customer = get_or_create_customer(user)
    
    checkout_session = stripe.checkout.Session.create(
        customer=customer.id,
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    
    return checkout_session

def create_customer_portal_session(user, return_url):
    """Create a Customer Portal session for managing subscriptions"""
    from .models import CustomerSubscription
    
    try:
        customer_subscription = CustomerSubscription.objects.get(user=user)
        if not customer_subscription.stripe_customer_id:
            # Create customer if needed
            get_or_create_customer(user)
            customer_subscription.refresh_from_db()
        
        # Create portal session
        session = stripe.billing_portal.Session.create(
            customer=customer_subscription.stripe_customer_id,
            return_url=return_url
        )
        
        return session
    except CustomerSubscription.DoesNotExist:
        # No customer subscription record yet
        customer = get_or_create_customer(user)
        
        session = stripe.billing_portal.Session.create(
            customer=customer.id,
            return_url=return_url
        )
        
        return session