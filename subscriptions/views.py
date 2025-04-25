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
    
    # Initialize Stripe API
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        # Fetch active prices with their products
        prices = stripe.Price.list(
            active=True,
            expand=['data.product'],
            limit=20  # Increase limit to ensure we get all prices
        )
        
        # Group prices by product and interval (monthly/yearly)
        products = {}
        for price in prices.data:
            # Skip prices without recurring component or inactive products
            if not price.recurring or not price.product.active:
                continue
                
            product_id = price.product.id
            
            if product_id not in products:
                products[product_id] = {
                    'id': product_id,
                    'name': price.product.name,
                    'description': price.product.description,
                    'prices': {'monthly': None, 'yearly': None}
                }
            
            # Categorize as monthly or yearly
            interval = price.recurring.interval
            if interval == 'month':
                products[product_id]['prices']['monthly'] = {
                    'id': price.id,
                    'amount': price.unit_amount / 100,  # Convert from cents to dollars
                    'currency': price.currency.upper()
                }
            elif interval == 'year':
                products[product_id]['prices']['yearly'] = {
                    'id': price.id,
                    'amount': price.unit_amount / 100,  # Convert from cents to dollars
                    'currency': price.currency.upper()
                }
        
        # Convert to list for easier templating
        product_list = list(products.values())
        
        # Sort products by price (ascending)
        product_list.sort(key=lambda p: p['prices']['monthly']['amount'] if p['prices']['monthly'] else float('inf'))
        
        return render(request, 'subscriptions/pricing.html', {
            'products': product_list,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'user_authenticated': request.user.is_authenticated
        })
    except Exception as e:
        return render(request, 'subscriptions/pricing.html', {
            'error': str(e),
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'user_authenticated': request.user.is_authenticated
        })