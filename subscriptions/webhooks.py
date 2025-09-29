import logging
from django.db import transaction
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
import stripe
import json

from .models import CustomerSubscription, Product, Price, AccountSetupToken

logger = logging.getLogger(__name__)
User = get_user_model()

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
        else:
            logger.info(f"Unhandled event type: {event.type}")
    except Exception as e:
        logger.error(f"Error processing {event.type}: {str(e)}", exc_info=True)
        # Still return 200 to prevent Stripe from retrying
    
    return HttpResponse(status=200)

def get_customer_subscription_by_stripe_id(customer_id):
    """Helper function to get CustomerSubscription by Stripe customer ID"""
    try:
        return CustomerSubscription.objects.get(stripe_customer_id=customer_id)
    except CustomerSubscription.DoesNotExist:
        logger.error(f"No CustomerSubscription found for stripe_customer_id: {customer_id}")
        
        # Try to find by customer metadata
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer = stripe.Customer.retrieve(customer_id)
            
            if customer.metadata and 'user_id' in customer.metadata:
                user = User.objects.get(id=customer.metadata['user_id'])
                
                # Create the missing CustomerSubscription
                customer_subscription = CustomerSubscription.objects.create(
                    user=user,
                    stripe_customer_id=customer_id,
                    subscription_active=False
                )
                logger.info(f"Created missing CustomerSubscription for user {user.id}")
                return customer_subscription
                
        except Exception as e:
            logger.error(f"Error creating CustomerSubscription from metadata: {str(e)}")
        
        return None

def handle_checkout_session(session):
    """Process checkout.session.completed event with simplified account setup"""
    customer_id = session.customer
    subscription_id = session.subscription
    customer_email = session.customer_details.email if session.customer_details else None
    
    if not customer_id:
        logger.warning("Checkout session has no customer ID")
        return
    
    logger.info(f"Processing checkout session for customer {customer_id}, subscription {subscription_id}, email {customer_email}")
    
    try:
        with transaction.atomic():
            # Check if customer already exists
            customer_subscription = None
            user_created = False
            
            try:
                customer_subscription = CustomerSubscription.objects.get(stripe_customer_id=customer_id)
                logger.info(f"Found existing CustomerSubscription for checkout")
            except CustomerSubscription.DoesNotExist:
                # This could be a guest checkout - create user account
                if customer_email:
                    user, user_created = create_or_get_user_from_email(customer_email)
                    customer_subscription = CustomerSubscription.objects.create(
                        user=user,
                        stripe_customer_id=customer_id,
                        subscription_active=False
                    )
                    logger.info(f"Created new user and subscription for {customer_email}")
                else:
                    logger.error(f"No email found for customer {customer_id}")
                    return
            
            # Update with subscription details if available
            if subscription_id and customer_subscription:
                customer_subscription.stripe_subscription_id = subscription_id
                customer_subscription.save()
                logger.info(f"Updated checkout session with subscription {subscription_id}")
            else:
                logger.warning(f"Checkout session {session.id} has no subscription_id - waiting for subscription.created")
            
            # Send welcome email with account setup link if new user
            if user_created and customer_subscription:
                send_welcome_email_with_setup_link(customer_subscription.user)
                
    except Exception as e:
        logger.error(f"Error processing checkout session: {str(e)}", exc_info=True)

def create_or_get_user_from_email(email):
    """Create or retrieve user account from email"""
    try:
        # Check if user already exists
        user = User.objects.get(email=email)
        logger.info(f"Found existing user for {email}")
        return user, False
    except User.DoesNotExist:
        # Create new user
        username = generate_username_from_email(email)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=None,  # No password initially
        )
        logger.info(f"Created new user {username} for {email}")
        return user, True

def generate_username_from_email(email):
    """Generate a unique username from email"""
    base_username = email.split('@')[0]
    # Clean username to meet Django requirements
    import re
    base_username = re.sub(r'[^a-zA-Z0-9._-]', '', base_username)
    
    # Ensure uniqueness
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    return username

def generate_account_setup_link(user):
    """Generate an account setup link for a user (30-day expiry)"""
    # Create setup token
    setup_token = AccountSetupToken.create_for_user(user)
    
    # Build the URL
    base_url = getattr(settings, 'SITE_URL', 'https://dreamwedai.com')
    setup_url = f"{base_url}/subscriptions/account-setup/{setup_token.token}/"
    
    return setup_url

def send_welcome_email_with_setup_link(user):
    """Send welcome email with account setup link only"""
    try:
        # Generate account setup link
        setup_url = generate_account_setup_link(user)
        
        subject = "Welcome to DreamWedAI - Complete Your Account Setup"
        
        context = {
            'user': user,
            'account_setup_url': setup_url,
            'login_url': f"{getattr(settings, 'SITE_URL', 'https://dreamwedai.com')}/accounts/login/",
            'support_email': 'hello@dreamwedai.com',
        }
        
        # Render email templates
        html_message = render_to_string('subscriptions/emails/welcome_guest.html', context)
        text_message = render_to_string('subscriptions/emails/welcome_guest.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        logger.info(f"Sent welcome email with setup link to {user.email}")
        
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}")

def sync_product_and_price(stripe_price):
    """Sync a Stripe price and its product to local database"""
    try:
        # Ensure we have the full product data
        if isinstance(stripe_price.product, str):
            stripe.api_key = settings.STRIPE_SECRET_KEY
            product_data = stripe.Product.retrieve(stripe_price.product)
        else:
            product_data = stripe_price.product
            
        # Sync product
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
                'amount': stripe_price.unit_amount or 0,
                'interval': stripe_price.recurring.interval if stripe_price.recurring else 'month',
                'interval_count': stripe_price.recurring.interval_count if stripe_price.recurring else 1,
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
            
            # Get existing CustomerSubscription (should exist from checkout)
            try:
                customer_subscription = CustomerSubscription.objects.get(stripe_customer_id=customer_id)
                logger.info(f"Found existing CustomerSubscription for {customer_id}")
            except CustomerSubscription.DoesNotExist:
                logger.error(f"No CustomerSubscription found for {customer_id} - this shouldn't happen")
                return
            
            # Update subscription details
            customer_subscription.stripe_subscription_id = subscription.id
            customer_subscription.status = subscription.status
            customer_subscription.subscription_active = subscription.status in ['active', 'trialing']
            
            # Get plan_id using safe API call
            try:
                subscription_items = stripe.SubscriptionItem.list(
                    subscription=subscription.id,
                    expand=['data.price.product']
                )
                
                if subscription_items.data:
                    price_item = subscription_items.data[0]
                    customer_subscription.plan_id = price_item.price.id
                    
                    # Sync product details
                    sync_product_and_price(price_item.price)
                    logger.info(f"Set plan_id to {price_item.price.id} for subscription {subscription.id}")
                else:
                    logger.warning(f"No subscription items found for {subscription.id}")
                    
            except Exception as e:
                logger.error(f"Error retrieving subscription items: {str(e)}", exc_info=True)
            
            customer_subscription.save()
            logger.info(f"Updated subscription details: {subscription.id} ({subscription.status})")
            
    except Exception as e:
        logger.error(f"Error processing subscription.created: {str(e)}", exc_info=True)

def handle_subscription_updated(subscription):
    """Process customer.subscription.updated event"""
    customer_id = subscription.customer
    
    try:
        with transaction.atomic():
            customer_subscription = get_customer_subscription_by_stripe_id(customer_id)
            if not customer_subscription:
                logger.error(f"Could not find CustomerSubscription for {customer_id}")
                return
            
            # Update subscription details
            customer_subscription.status = subscription.status
            customer_subscription.subscription_active = subscription.status in ['active', 'trialing']
            
            # Get plan_id using safe API call
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                subscription_items = stripe.SubscriptionItem.list(
                    subscription=subscription.id,
                    expand=['data.price.product']
                )
                
                if subscription_items.data:
                    price_item = subscription_items.data[0]
                    customer_subscription.plan_id = price_item.price.id
                    logger.info(f"Updated plan_id to {price_item.price.id} for subscription {subscription.id}")
                    
            except Exception as e:
                logger.error(f"Error retrieving subscription items: {str(e)}")
            
            customer_subscription.save()
            logger.info(f"Updated subscription {subscription.id} for customer {customer_id}")
            
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}", exc_info=True)

def handle_subscription_deleted(subscription):
    """Process customer.subscription.deleted event"""
    customer_id = subscription.customer
    
    try:
        with transaction.atomic():
            customer_subscription = get_customer_subscription_by_stripe_id(customer_id)
            if not customer_subscription:
                logger.warning(f"CustomerSubscription not found for deleted subscription {customer_id}")
                return
            
            customer_subscription.subscription_active = False
            customer_subscription.status = subscription.status
            # Keep the plan_id for reference
            customer_subscription.save()
            
            logger.info(f"Marked subscription {subscription.id} as inactive")
    except Exception as e:
        logger.error(f"Error deleting subscription: {str(e)}", exc_info=True)

def handle_invoice_paid(invoice):
    """Process invoice.paid event"""
    customer_id = invoice.customer
    
    try:
        customer_subscription = get_customer_subscription_by_stripe_id(customer_id)
        if not customer_subscription:
            logger.warning(f"CustomerSubscription not found for invoice payment {customer_id}")
            return
        
        # Update status if this was a late payment
        if customer_subscription.status in ['past_due', 'unpaid', 'incomplete']:
            customer_subscription.status = 'active'
            customer_subscription.subscription_active = True
            customer_subscription.save()
            logger.info(f"Reactivated subscription for customer {customer_id}")
            
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}", exc_info=True)