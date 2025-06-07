from django.shortcuts import render

# Create your views here.
# saas_base/subscriptions/views.py
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe

from .stripe_utils import create_checkout_session, create_customer_portal_session

@login_required
def subscription_checkout(request):
    """
    Handle POST checkout requests from the pricing page
    Redirect GET requests to the pricing page
    """
    if request.method == 'POST':
        price_id = request.POST.get('price_id')
        
        if not price_id:
            return JsonResponse({'error': 'No price ID provided'}, status=400)
        
        success_url = request.build_absolute_uri(
            reverse('subscriptions:checkout_success')
        )
        cancel_url = request.build_absolute_uri(
            reverse('subscriptions:checkout_cancel')
        )
        
        try:
            checkout_session = create_checkout_session(
                request.user, 
                price_id, 
                success_url, 
                cancel_url
            )
            return JsonResponse({'sessionId': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # Redirect GET requests to the pricing page
    return redirect('subscriptions:pricing')


@login_required
def checkout_success(request):
    """Handle successful checkout with improved subscription detection"""
    import stripe
    from django.conf import settings
    from .models import CustomerSubscription, Price, Product
    import time
    import logging
    
    logger = logging.getLogger(__name__)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Try to get customer subscription
    try:
        customer_subscription = CustomerSubscription.objects.get(user=request.user)
        
        # If we already have an active subscription, we're good
        if customer_subscription.subscription_active and customer_subscription.stripe_subscription_id:
            logger.info(f"User {request.user.username} already has active subscription")
            return render(request, 'subscriptions/checkout_success.html')
        
        # If we have a customer ID but no active subscription, check Stripe directly
        if customer_subscription.stripe_customer_id:
            # Wait for Stripe to process
            time.sleep(2)
            
            # Try multiple times to find the subscription
            for attempt in range(3):
                logger.info(f"Attempt {attempt+1} to find subscription for {request.user.username}")
                
                # Query Stripe for subscriptions
                subscriptions = stripe.Subscription.list(
                    customer=customer_subscription.stripe_customer_id,
                    limit=5,
                    expand=['data.items.data.price.product']
                )
                
                # Find the most recent active subscription
                if subscriptions and subscriptions.data:
                    active_sub = None
                    for sub in subscriptions.data:
                        if sub.status in ['active', 'trialing']:
                            active_sub = sub
                            break
                    
                    if active_sub:
                        # Update subscription record
                        customer_subscription.stripe_subscription_id = active_sub.id
                        customer_subscription.status = active_sub.status
                        customer_subscription.subscription_active = True
                        
                        # Set plan ID from the first item
                        if active_sub.items and active_sub.items.data:
                            item = active_sub.items.data[0]
                            customer_subscription.plan_id = item.price.id
                        
                        customer_subscription.save()
                        logger.info(f"Successfully updated subscription for {request.user.username}")
                        break
                
                # Wait before next attempt
                if attempt < 2:
                    time.sleep(1)
    
    except CustomerSubscription.DoesNotExist:
        logger.warning(f"No subscription record for {request.user.username}")
    except Exception as e:
        logger.error(f"Error syncing subscription: {str(e)}")
    
    return render(request, 'subscriptions/checkout_success.html')

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
            'is_new_user': is_new_user,  # Add this flag
        })
    except Exception as e:
        return render(request, 'subscriptions/pricing.html', {
            'error': str(e),
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'user_authenticated': request.user.is_authenticated,
            'is_new_user': False,
        })