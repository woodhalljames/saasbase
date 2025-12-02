# subscriptions/webhooks.py - UPDATED WITH FREE TIER RESET
# When subscriptions become inactive, users are reset to free tier (3 tokens)

import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime
import stripe
import json

from .models import CustomerSubscription, Product, Price, AccountSetupToken

logger = logging.getLogger(__name__)
User = get_user_model()

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    CRITICAL: Always return 200 for valid events to prevent retry storms
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    logger.info(f"📨 Webhook received - signature: {sig_header[:10] if sig_header else 'None'}")
    
    # Step 1: Verify webhook signature (ONLY time we return 400)
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"✓ Webhook verified: {event.type} (ID: {event.id})")
    except ValueError as e:
        logger.error(f"✗ Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"✗ Invalid signature: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"✗ Unexpected error verifying webhook: {str(e)}", exc_info=True)
        return HttpResponse(status=400)
    
    # Step 2: Process the event (ALWAYS return 200, even on errors)
    try:
        logger.info(f"Processing event: {event.type}")
        
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
        elif event.type == 'invoice.payment_failed':
            handle_invoice_payment_failed(event.data.object)
        elif event.type == 'invoice.payment_action_required':
            handle_invoice_payment_action_required(event.data.object)
        else:
            logger.info(f"ℹ️ Unhandled event type: {event.type}")
        
        logger.info(f"✓ Successfully processed {event.type} (ID: {event.id})")
        
    except Exception as e:
        logger.error(
            f"❌ ERROR processing {event.type} (ID: {event.id}): {str(e)}",
            exc_info=True,
            extra={
                'event_id': event.id,
                'event_type': event.type,
                'customer_id': getattr(event.data.object, 'customer', 'N/A')
            }
        )
    
    return HttpResponse(status=200)


def reset_user_to_free_tier(user):
    """
    Reset user to free tier (3 tokens) when subscription becomes inactive.
    This is called when:
    - Subscription is canceled
    - Payment fails and subscription becomes inactive
    - Subscription is deleted
    """
    try:
        from usage_limits.usage_tracker import UsageTracker
        
        if UsageTracker.reset_to_free_tier(user):
            logger.info(f"✓ Reset {user.email} to free tier (3 tokens)")
            return True
        else:
            logger.error(f"✗ Failed to reset {user.email} to free tier")
            return False
    except ImportError:
        logger.warning("UsageTracker not available - skipping free tier reset")
        return False
    except Exception as e:
        logger.error(f"Error resetting {user.email} to free tier: {str(e)}")
        return False


def handle_subscription_updated(subscription):
    """
    Process customer.subscription.updated event
    UPDATED: Immediately deactivates subscription on payment failure (past_due, unpaid, canceled)
    User is downgraded to free tier until payment succeeds
    """
    customer_id = subscription.customer

    try:
        customer_subscription = get_customer_subscription_by_stripe_id(customer_id)
        if not customer_subscription:
            logger.error(f"Could not find CustomerSubscription for {customer_id}")
            return

        logger.info(f"Updating subscription for customer {customer_id}, user {customer_subscription.user.email}")

        # Track old state
        old_status = customer_subscription.status
        old_active = customer_subscription.subscription_active

        # Update subscription details
        customer_subscription.status = subscription.status
        # Subscription only active when 'active' or 'trialing'
        # past_due, unpaid, canceled = immediate loss of access
        customer_subscription.subscription_active = subscription.status in ['active', 'trialing']

        # Log status transitions
        if old_status != subscription.status:
            logger.info(
                f"📊 Subscription status transition for {customer_subscription.user.email}: "
                f"{old_status} → {subscription.status} "
                f"(active: {old_active} → {customer_subscription.subscription_active})"
            )

            # CRITICAL: Subscription becoming inactive
            if subscription.status in ['past_due', 'unpaid', 'canceled', 'incomplete_expired']:
                logger.warning(
                    f"🚫 Subscription {subscription.id} moved to {subscription.status} - "
                    f"User {customer_subscription.user.email} losing access immediately."
                )

                # Reset to free tier immediately when losing access
                if old_active and not customer_subscription.subscription_active:
                    reset_user_to_free_tier(customer_subscription.user)

            # Subscription reactivating (payment succeeded)
            elif old_status in ['past_due', 'unpaid'] and subscription.status == 'active':
                logger.info(
                    f"✅ Subscription {subscription.id} reactivated - "
                    f"payment succeeded for {customer_subscription.user.email}"
                )

        # Update plan_id
        plan_id_set = False
        old_plan_id = customer_subscription.plan_id
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            subscription_items = stripe.SubscriptionItem.list(
                subscription=subscription.id,
                expand=['data.price.product']
            )

            if subscription_items.data:
                price_item = subscription_items.data[0]
                customer_subscription.plan_id = price_item.price.id
                plan_id_set = True
                sync_product_and_price(price_item.price)
                logger.info(f"✓ Updated plan_id to {price_item.price.id}")

        except Exception as e:
            logger.error(f"Error retrieving subscription items: {str(e)}", exc_info=True)

        # Fallback
        if not plan_id_set:
            try:
                if hasattr(subscription, 'items') and subscription.items and subscription.items.data:
                    price_id = subscription.items.data[0].price.id
                    customer_subscription.plan_id = price_id
                    plan_id_set = True
                    logger.info(f"✓ Updated plan_id to {price_id} using fallback")
            except Exception as e:
                logger.error(f"Fallback plan_id retrieval failed: {str(e)}")

        customer_subscription.save()
        logger.info(
            f"✓ Subscription updated: {subscription.id} for {customer_subscription.user.email} "
            f"(status: {old_status} → {subscription.status}, active: {customer_subscription.subscription_active})"
        )

    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}", exc_info=True)


def handle_subscription_deleted(subscription):
    """
    Process customer.subscription.deleted event
    UPDATED: Resets to free tier when subscription is deleted
    """
    customer_id = subscription.customer
    
    try:
        customer_subscription = get_customer_subscription_by_stripe_id(customer_id)
        if not customer_subscription:
            logger.warning(f"CustomerSubscription not found for deleted subscription {customer_id}")
            return
        
        # Mark as inactive
        was_active = customer_subscription.subscription_active
        customer_subscription.subscription_active = False
        customer_subscription.status = subscription.status
        customer_subscription.save()
        
        logger.warning(f"🗑️ Subscription {subscription.id} deleted for {customer_subscription.user.email}")
        
        # NEW: Reset to free tier
        if was_active:
            reset_user_to_free_tier(customer_subscription.user)
            
    except Exception as e:
        logger.error(f"Error deleting subscription: {str(e)}", exc_info=True)


def handle_invoice_payment_failed(invoice):
    """
    Process invoice.payment_failed event
    UPDATED: Immediately deactivates subscription and downgrades to free tier on payment failure
    Sends email notification to user so they can update payment method
    Subscription will be restored automatically when payment succeeds (invoice.paid event)
    """
    customer_id = invoice.customer

    try:
        customer_subscription = get_customer_subscription_by_stripe_id(customer_id)
        if not customer_subscription:
            logger.warning(f"⚠️ CustomerSubscription not found for failed payment {customer_id}")
            return

        attempt_count = invoice.get('attempt_count', 0)
        amount_due = invoice.amount_due / 100

        logger.warning(
            f"💳 Payment failed for {customer_subscription.user.email} - "
            f"Invoice: {invoice.id}, Amount: ${amount_due:.2f}, Attempt: {attempt_count}"
        )

        # Sync with Stripe to get current subscription status
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = stripe.Subscription.retrieve(customer_subscription.stripe_subscription_id)

        # Update local database
        old_active = customer_subscription.subscription_active
        customer_subscription.status = subscription.status
        # Immediately deactivate on payment failure
        customer_subscription.subscription_active = subscription.status in ['active', 'trialing']
        customer_subscription.save()

        # Downgrade to free tier immediately when losing access
        if old_active and not customer_subscription.subscription_active:
            logger.warning(
                f"🚫 Payment failed - Downgrading {customer_subscription.user.email} to free tier immediately. "
                f"Subscription status: {subscription.status}. Stripe will retry automatically."
            )
            reset_user_to_free_tier(customer_subscription.user)

        # Send email notification so user can update payment method
        try:
            send_payment_failure_email(customer_subscription.user, invoice)
            logger.info(f"📧 Sent payment failure notification to {customer_subscription.user.email}")
        except Exception as email_error:
            logger.error(f"Failed to send payment failure email: {str(email_error)}")

    except Exception as e:
        logger.error(f"Error processing payment failure: {str(e)}", exc_info=True)


# Keep all other handlers from the previous version...
# (I'll include them below for completeness)

def get_customer_subscription_by_stripe_id(customer_id):
    """Helper function to get CustomerSubscription by Stripe customer ID with email fallback"""
    try:
        return CustomerSubscription.objects.get(stripe_customer_id=customer_id)
    except CustomerSubscription.DoesNotExist:
        logger.warning(f"No CustomerSubscription found for stripe_customer_id: {customer_id}")

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer = stripe.Customer.retrieve(customer_id)

            if customer.metadata and 'user_id' in customer.metadata:
                try:
                    user = User.objects.get(id=customer.metadata['user_id'])
                    customer_subscription, created = CustomerSubscription.objects.get_or_create(
                        user=user,
                        defaults={'stripe_customer_id': customer_id, 'subscription_active': False}
                    )
                    if not created:
                        customer_subscription.stripe_customer_id = customer_id
                        customer_subscription.save()
                    return customer_subscription
                except User.DoesNotExist:
                    pass

            if customer.email:
                try:
                    user = User.objects.get(email=customer.email)
                    customer_subscription, created = CustomerSubscription.objects.get_or_create(
                        user=user,
                        defaults={'stripe_customer_id': customer_id, 'subscription_active': False}
                    )
                    if not created:
                        customer_subscription.stripe_customer_id = customer_id
                        customer_subscription.save()
                    return customer_subscription
                except User.DoesNotExist:
                    pass

        except Exception as e:
            logger.error(f"Error in fallback lookup: {str(e)}", exc_info=True)

        return None


def handle_checkout_session(session):
    """Process checkout.session.completed event"""
    customer_id = session.customer
    subscription_id = session.subscription
    customer_email = session.customer_details.email if session.customer_details else None
    
    if not customer_id:
        return
    
    try:
        if not customer_email:
            return
        
        user, user_created = create_or_get_user_from_email(customer_email)
        customer_subscription, sub_created = CustomerSubscription.objects.get_or_create(
            user=user,
            defaults={'stripe_customer_id': customer_id}
        )
        
        customer_subscription.stripe_customer_id = customer_id
        if subscription_id:
            customer_subscription.stripe_subscription_id = subscription_id
        customer_subscription.save()
        
        if user_created:
            try:
                send_welcome_email_with_setup_link(user)
            except Exception as e:
                logger.error(f"Failed to send welcome email: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error processing checkout session: {str(e)}", exc_info=True)


def create_or_get_user_from_email(email):
    """Create or retrieve user account from email"""
    try:
        user = User.objects.get(email=email)
        return user, False
    except User.DoesNotExist:
        username = generate_username_from_email(email)
        user = User.objects.create_user(username=username, email=email, password=None)
        return user, True


def generate_username_from_email(email):
    """Generate a unique username from email"""
    import re
    base_username = re.sub(r'[^a-zA-Z0-9._-]', '', email.split('@')[0])
    if len(base_username) < 3:
        base_username = 'user_' + base_username
    
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username


def generate_account_setup_link(user):
    """Generate account setup link"""
    setup_token = AccountSetupToken.create_for_user(user)
    base_url = getattr(settings, 'SITE_URL', 'https://dreamwedai.com')
    return f"{base_url}/subscriptions/account-setup/{setup_token.token}/"


def send_welcome_email_with_setup_link(user):
    """Send welcome email"""
    try:
        setup_url = generate_account_setup_link(user)
        subject = "Welcome to DreamWedAI - Complete Your Account Setup"
        context = {
            'user': user,
            'account_setup_url': setup_url,
            'login_url': f"{getattr(settings, 'SITE_URL', 'https://dreamwedai.com')}/accounts/login/",
            'support_email': 'hello@dreamwedai.com',
        }
        html_message = render_to_string('subscriptions/emails/welcome_guest.html', context)
        text_message = render_to_string('subscriptions/emails/welcome_guest.txt', context)
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}")


def sync_product_and_price(stripe_price):
    """Sync product and price to local database"""
    try:
        if isinstance(stripe_price.product, str):
            stripe.api_key = settings.STRIPE_SECRET_KEY
            product_data = stripe.Product.retrieve(stripe_price.product)
        else:
            product_data = stripe_price.product
            
        product, created = Product.objects.update_or_create(
            stripe_id=product_data.id,
            defaults={
                'name': product_data.name,
                'description': product_data.description or '',
                'active': product_data.active,
            }
        )
        
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
    except Exception as e:
        logger.error(f"Error syncing product/price: {str(e)}")


def handle_subscription_created(subscription):
    """Process subscription.created event"""
    customer_id = subscription.customer

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer_subscription = get_customer_subscription_by_stripe_id(customer_id)
        if not customer_subscription:
            return

        customer_subscription.stripe_subscription_id = subscription.id
        customer_subscription.status = subscription.status
        customer_subscription.subscription_active = subscription.status in ['active', 'trialing']

        try:
            subscription_items = stripe.SubscriptionItem.list(
                subscription=subscription.id,
                expand=['data.price.product']
            )
            if subscription_items.data:
                price_item = subscription_items.data[0]
                customer_subscription.plan_id = price_item.price.id
                sync_product_and_price(price_item.price)
        except Exception as e:
            logger.error(f"Error retrieving subscription items: {str(e)}")

        customer_subscription.save()
        logger.info(f"✓ Subscription created: {subscription.id}")

    except Exception as e:
        logger.error(f"Error processing subscription.created: {str(e)}", exc_info=True)


def handle_invoice_paid(invoice):
    """Process invoice.paid event"""
    customer_id = invoice.customer

    try:
        customer_subscription = get_customer_subscription_by_stripe_id(customer_id)
        if not customer_subscription:
            return

        if customer_subscription.status in ['past_due', 'unpaid', 'incomplete']:
            customer_subscription.status = 'active'
            customer_subscription.subscription_active = True
            customer_subscription.save()

        from usage_limits.usage_tracker import UsageTracker
        if UsageTracker.reset_usage_on_payment(customer_subscription.user):
            logger.info(f"✓ Payment successful - tokens reset for {customer_subscription.user.email}")

    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}", exc_info=True)


def handle_invoice_payment_action_required(invoice):
    """Process invoice.payment_action_required event"""
    customer_id = invoice.customer
    try:
        customer_subscription = get_customer_subscription_by_stripe_id(customer_id)
        if customer_subscription:
            try:
                send_payment_action_required_email(customer_subscription.user, invoice)
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Error processing payment action required: {str(e)}", exc_info=True)


def send_payment_failure_email(user, invoice):
    """Send payment failure email"""
    try:
        subject = "Subscription Payment Issue - DreamWedAI"
        context = {
            'user': user,
            'amount': invoice.amount_due / 100,
            'portal_url': f"{getattr(settings, 'SITE_URL', 'https://dreamwedai.com')}/subscriptions/portal/",
        }
        html_message = render_to_string('subscriptions/emails/payment_failed.html', context)
        text_message = render_to_string('subscriptions/emails/payment_failed.txt', context)
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending payment failure email: {str(e)}")
        raise


def send_payment_action_required_email(user, invoice):
    """Send payment action required email"""
    try:
        subject = "Action Required - Complete Payment Authentication"
        context = {
            'user': user,
            'invoice_url': invoice.hosted_invoice_url if hasattr(invoice, 'hosted_invoice_url') else None,
            'amount': invoice.amount_due / 100,
        }
        html_message = render_to_string('subscriptions/emails/payment_action_required.html', context)
        text_message = render_to_string('subscriptions/emails/payment_action_required.txt', context)
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error sending payment action email: {str(e)}")
        raise