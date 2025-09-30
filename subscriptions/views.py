# saas_base/subscriptions/views.py
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.forms import SetPasswordForm
import stripe
import logging

from .stripe_utils import create_checkout_session, create_customer_portal_session
from .models import AccountSetupToken

logger = logging.getLogger(__name__)

def subscription_checkout(request):
    """
    Handle POST checkout requests - NO LOGIN REQUIRED
    Supports both authenticated and guest users
    WITH REWARDFUL TRACKING
    """
    if request.method == 'POST':
        price_id = request.POST.get('price_id')
        referral = request.POST.get('referral', '').strip()  # Get Rewardful referral ID
        
        if not price_id:
            return JsonResponse({'error': 'No price ID provided'}, status=400)
        
        # Log referral tracking
        if referral:
            logger.info(f"Checkout with Rewardful referral: {referral[:8]}...")
        else:
            logger.info("Checkout without referral")
        
        success_url = request.build_absolute_uri(
            reverse('subscriptions:checkout_success')
        )
        cancel_url = request.build_absolute_uri(
            reverse('subscriptions:checkout_cancel')
        )
        
        try:
            if request.user.is_authenticated:
                # Existing flow for logged-in users with referral tracking
                checkout_session = create_checkout_session(
                    request.user, 
                    price_id, 
                    success_url, 
                    cancel_url,
                    referral=referral  # Pass referral to Stripe
                )
            else:
                # Guest checkout with referral tracking
                checkout_session = create_guest_checkout_session(
                    price_id,
                    success_url,
                    cancel_url,
                    referral=referral  # Pass referral to Stripe
                )
            
            return JsonResponse({'sessionId': checkout_session.id})
        except Exception as e:
            logger.error(f"Checkout error: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=400)
    
    # Redirect GET requests to the pricing page
    return redirect('subscriptions:pricing')

def create_guest_checkout_session(price_id, success_url, cancel_url, referral=None):
    """Create a Stripe Checkout Session for guest users with optional referral tracking"""
    import stripe
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Build session parameters
    session_params = {
        'payment_method_types': ['card'],
        'line_items': [{
            'price': price_id,
            'quantity': 1,
        }],
        'mode': 'subscription',
        'success_url': success_url,
        'cancel_url': cancel_url,
        'customer_email': None,  # Allow Stripe to collect customer email
    }
    
    # Add client_reference_id for Rewardful tracking if referral exists
    # IMPORTANT: Only set if not empty, as Stripe will error on blank values
    if referral:
        session_params['client_reference_id'] = referral
        logger.info(f"Setting client_reference_id for guest checkout: {referral[:8]}...")
    
    checkout_session = stripe.checkout.Session.create(**session_params)
    
    return checkout_session

def checkout_success(request):
    """Handle successful checkout - works for both authenticated and guest users"""
    import stripe
    from django.conf import settings
    from .models import CustomerSubscription, Price, Product
    import time
    import logging
    
    logger = logging.getLogger(__name__)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    if request.user.is_authenticated:
        # Existing logic for authenticated users
        try:
            customer_subscription = CustomerSubscription.objects.get(user=request.user)
            
            if customer_subscription.subscription_active and customer_subscription.stripe_subscription_id:
                logger.info(f"User {request.user.username} already has active subscription")
                return render(request, 'subscriptions/checkout_success.html')
            
            # Wait and sync subscription
            if customer_subscription.stripe_customer_id:
                time.sleep(2)
                
                for attempt in range(3):
                    subscriptions = stripe.Subscription.list(
                        customer=customer_subscription.stripe_customer_id,
                        limit=5,
                        expand=['data.items.data.price.product']
                    )
                    
                    if subscriptions and subscriptions.data:
                        active_sub = None
                        for sub in subscriptions.data:
                            if sub.status in ['active', 'trialing']:
                                active_sub = sub
                                break
                        
                        if active_sub:
                            customer_subscription.stripe_subscription_id = active_sub.id
                            customer_subscription.status = active_sub.status
                            customer_subscription.subscription_active = True
                            
                            if active_sub.items and active_sub.items.data:
                                item = active_sub.items.data[0]
                                customer_subscription.plan_id = item.price.id
                            
                            customer_subscription.save()
                            logger.info(f"Successfully updated subscription for {request.user.username}")
                            break
                    
                    if attempt < 2:
                        time.sleep(1)
        
        except CustomerSubscription.DoesNotExist:
            logger.warning(f"No subscription record for {request.user.username}")
        except Exception as e:
            logger.error(f"Error syncing subscription: {str(e)}")
    else:
        # Guest user - generic message for both new and existing users
        # Template will handle both scenarios with dual options
        pass
    
    return render(request, 'subscriptions/checkout_success.html')

def account_setup(request, token):
    """Handle account setup completion - password setup only"""
    from django.contrib.auth import get_user_model
    from django.contrib.auth.forms import SetPasswordForm
    
    User = get_user_model()
    
    # Get the setup token
    setup_token = get_object_or_404(AccountSetupToken, token=token)
    
    # Check if token is still valid
    if not setup_token.is_valid():
        messages.error(request, 
            "This account setup link has expired or has already been used.")
        return redirect('account_login')
    
    user = setup_token.user
    
    # NEW: If user already has a password, redirect them to login
    if user.has_usable_password():
        setup_token.mark_used()
        messages.info(request,
            "Your account is already set up! Please login below.")
        return redirect('account_login')
    
    if request.method == 'POST':
        # Handle password setup form submission
        action = request.POST.get('action')
        
        if action == 'set_password':
            # User wants to set a password
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                setup_token.mark_used()
                # Log user in with explicit backend
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, 
                    "Password set successfully! Welcome to DreamWedAI!")
                
                # Redirect to user dashboard with success message about social accounts
                messages.info(request, 
                    "You can now connect your Google account from your profile settings for quick login.")
                return redirect('users:detail', username=user.username)
    
    else:
        # GET request - show the setup form
        form = SetPasswordForm(user)
    
    return render(request, 'subscriptions/account_setup.html', {
        'form': form,
        'user': user,
        'setup_token': setup_token,
    })

def generate_account_setup_link(user, request=None):
    """Generate an account setup link for a user (30-day expiry)"""
    # Create setup token
    setup_token = AccountSetupToken.create_for_user(user)
    
    # Build the URL
    if request:
        setup_url = request.build_absolute_uri(
            reverse('subscriptions:account_setup', kwargs={'token': setup_token.token})
        )
    else:
        # Fallback for webhook context
        base_url = getattr(settings, 'SITE_URL', 'https://dreamwedai.com')
        setup_url = f"{base_url}/subscriptions/account-setup/{setup_token.token}/"
    
    return setup_url

@login_required
def checkout_cancel(request):
    """Handle canceled checkout"""
    return render(request, 'subscriptions/checkout_cancel.html')

@login_required
def customer_portal(request):
    """Redirect to Stripe Customer Portal for subscription management"""
    return_url = request.build_absolute_uri(
        reverse('users:detail', kwargs={'username': request.user.username})
    )
    
    try:
        portal_session = create_customer_portal_session(request.user, return_url)
        return redirect(portal_session.url)
    except Exception as e:
        return render(request, 'subscriptions/error.html', {'error': str(e)})

def pricing_page(request):
    """Public pricing page showing available subscription plans"""
    from .models import Product, Price
    
    # Check if we should auto-redirect to checkout
    auto_checkout_price_id = request.GET.get('checkout')
    
    # Check if this is a new user (just signed up)
    is_new_user = (
        request.user.is_authenticated and 
        not request.user.has_active_subscription() and
        not request.session.get('pricing_visited', False)
    )
    
    # Mark that they've visited pricing
    if request.user.is_authenticated:
        request.session['pricing_visited'] = True

    try:
        # Get active products with prices - only those marked to show on site
        products_with_prices = []
        
        # Get products with their custom fields
        for product in Product.objects.filter(active=True, show_on_site=True).order_by('display_order', 'id'):
            # Get all prices for this product, organized by interval
            monthly_price = product.prices.filter(active=True, interval='month').first()
            yearly_price = product.prices.filter(active=True, interval='year').first()
            
            # Only include products that have at least one active price
            if monthly_price or yearly_price:
                product_data = {
                    'id': product.stripe_id,
                    'name': product.name,
                    'description': product.description,
                    'highlight': product.highlight,
                    'tokens': product.tokens,
                    'features_list': product.get_features_list(),
                    'prices': {
                        'monthly': {
                            'id': monthly_price.stripe_id,
                            'amount': monthly_price.amount / 100,
                            'currency': monthly_price.currency.upper(),
                            'display_name': monthly_price.display_name
                        } if monthly_price else None,
                        'yearly': {
                            'id': yearly_price.stripe_id,
                            'amount': yearly_price.amount / 100,
                            'currency': yearly_price.currency.upper(),
                            'display_name': yearly_price.display_name
                        } if yearly_price else None
                    }
                }
                products_with_prices.append(product_data)
        
        # Sort products by display_order first, then by monthly price
        products_with_prices.sort(
            key=lambda p: (
                0 if p.get('highlight') else 1,  # Highlighted products first
                p['prices']['monthly']['amount'] if p['prices']['monthly'] else float('inf')
            )
        )
        
        return render(request, 'subscriptions/pricing.html', {
            'products': products_with_prices,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'user_authenticated': request.user.is_authenticated,
            'auto_checkout_price_id': auto_checkout_price_id,
            'is_new_user': is_new_user,
        })
    except Exception as e:
        return render(request, 'subscriptions/pricing.html', {
            'error': str(e),
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'user_authenticated': request.user.is_authenticated,
            'is_new_user': False,
        })