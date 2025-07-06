# usage_limits/decorators.py
import functools
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from .usage_tracker import UsageTracker

def usage_limit_required(tokens=1, redirect_url=None):
    """
    Decorator to check if a user has enough tokens before executing the view
    
    Args:
        tokens: Number of tokens to consume
        redirect_url: URL to redirect to if limits are exceeded
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            
            # Try to increment usage
            if UsageTracker.increment_usage(request.user, tokens):
                # User has enough tokens, proceed with the view
                return view_func(request, *args, **kwargs)
            
            # User has reached their limit
            usage_data = UsageTracker.get_usage_data(request.user)
            
            # Handle different response types based on the request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # AJAX request, return JSON response
                return JsonResponse({
                    'error': 'Usage limit exceeded',
                    'limit': usage_data['limit'],
                    'usage': usage_data['current'],
                    'remaining': usage_data['remaining']
                }, status=429)
            
            # Add message for user
            messages.error(
                request, 
                f"You've reached your usage limit ({usage_data['limit']} per month). "
                "Please upgrade your subscription to continue."
            )
            
            # Redirect to specified URL or default
            redirect_to = redirect_url
            if not redirect_to:
                redirect_to = reverse('subscriptions:pricing')
            
            return HttpResponseRedirect(redirect_to)
            
        return wrapped_view
    return decorator