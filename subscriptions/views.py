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
    """Handle successful checkout with direct Stripe API check"""
    import stripe
    from django.conf import settings
    from .models import CustomerSubscription
    import time
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Try to get customer subscription
    try:
        customer_subscription = CustomerSubscription.objects.get(user=request.user)
        
        # If we don't have a subscription ID yet (webhook hasn't processed), 
        # try to find it directly from Stripe
        if not customer_subscription.stripe_subscription_id and customer_subscription.stripe_customer_id:
            # Wait a moment for Stripe to process
            time.sleep(1.5)
            
            # Query Stripe for subscriptions
            subscriptions = stripe.Subscription.list(
                customer=customer_subscription.stripe_customer_id,
                limit=1,
                status='active'
            )
            
            # If found, update our local record
            if subscriptions and subscriptions.data:
                subscription = subscriptions.data[0]
                customer_subscription.stripe_subscription_id = subscription.id
                customer_subscription.status = subscription.status
                customer_subscription.subscription_active = subscription.status in ['active', 'trialing']
                
                # Set plan ID from the first item
                if subscription.items and len(subscription.items.data) > 0:
                    item = subscription.items.data[0]
                    customer_subscription.plan_id = item.price.id
                
                customer_subscription.save()
    except (CustomerSubscription.DoesNotExist, stripe.error.StripeError) as e:
        # Log the error but don't show to user
        import logging
        logging.error(f"Error syncing subscription: {str(e)}")
    
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
            'auto_checkout_price_id': auto_checkout_price_id
        })
    except Exception as e:
        return render(request, 'subscriptions/pricing.html', {
            'error': str(e),
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'user_authenticated': request.user.is_authenticated
        })