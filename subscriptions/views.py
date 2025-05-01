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
    """Create a Stripe Checkout session for subscription"""
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
    
    # For GET requests, render the checkout page
    # In real app, you'd fetch available plans from Stripe
    # For MVP, we'll hard-code a few price IDs
    
    # Retrieve the plans from Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        prices = stripe.Price.list(
            active=True,
            expand=['data.product'],
            limit=10
        )
        return render(request, 'subscriptions/checkout.html', {
            'prices': prices.data,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY
        })
    except Exception as e:
        return render(request, 'subscriptions/checkout.html', {
            'error': str(e),
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY
        })

@login_required
def checkout_success(request):
    """Handle successful checkout"""
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
    
    try:
        # Get active products with prices
        products_with_prices = []
        
        for product in Product.objects.filter(active=True):
            # Get all prices for this product, organized by interval
            monthly_price = product.prices.filter(active=True, interval='month').first()
            yearly_price = product.prices.filter(active=True, interval='year').first()
            
            # Only include products that have at least one active price
            if monthly_price or yearly_price:
                products_with_prices.append({
                    'id': product.stripe_id,
                    'name': product.name,
                    'description': product.description,
                    'prices': {
                        'monthly': {
                            'id': monthly_price.stripe_id,
                            'amount': monthly_price.amount / 100,
                            'currency': monthly_price.currency.upper()
                        } if monthly_price else None,
                        'yearly': {
                            'id': yearly_price.stripe_id,
                            'amount': yearly_price.amount / 100,
                            'currency': yearly_price.currency.upper()
                        } if yearly_price else None
                    }
                })
        
        # Sort products by monthly price (ascending)
        products_with_prices.sort(
            key=lambda p: p['prices']['monthly']['amount'] 
            if p['prices']['monthly'] 
            else float('inf')
        )
        
        return render(request, 'subscriptions/pricing.html', {
            'products': products_with_prices,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'user_authenticated': request.user.is_authenticated
        })
    except Exception as e:
        return render(request, 'subscriptions/pricing.html', {
            'error': str(e),
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'user_authenticated': request.user.is_authenticated
        })