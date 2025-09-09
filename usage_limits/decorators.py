# usage_limits/decorators.py - Simplified for individual processing only

import functools
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from .usage_tracker import UsageTracker

def usage_limit_required(tokens=1, redirect_url=None):
    """
    Simple decorator to check if a user has enough tokens before executing the view.
    Usage is NOT consumed by this decorator - it only checks availability.
    Actual usage increment happens in the view logic after successful processing.
    
    Args:
        tokens: Number of tokens to check for availability
        redirect_url: URL to redirect to if limits are exceeded
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            
            if not request.user.is_authenticated:
                # Unauthenticated users can't use resources
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Authentication required',
                        'needs_login': True
                    }, status=401)
                return HttpResponseRedirect(reverse('account_login'))
            
            # Get current usage data
            usage_data = UsageTracker.get_usage_data(request.user)
            
            # Check if user has enough remaining capacity
            if usage_data['remaining'] < tokens:
                error_message = f"You've reached your usage limit ({usage_data['limit']} per month). Please upgrade your subscription to continue."
                
                # Handle different response types
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': error_message,
                        'usage_data': usage_data,
                        'needs_upgrade': True
                    }, status=429)
                
                # Add message for regular requests
                messages.error(request, error_message)
                
                # Redirect to pricing or specified URL
                redirect_to = redirect_url or reverse('subscriptions:pricing')
                return HttpResponseRedirect(redirect_to)
            
            # User has enough tokens available, proceed with the view
            # Note: Actual usage increment happens in the view after successful processing
            return view_func(request, *args, **kwargs)
            
        return wrapped_view
    return decorator

def usage_info_required(view_func):
    """
    Simple decorator that adds usage information to the request context.
    Doesn't check or consume usage, just provides data for display.
    """
    @functools.wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        
        if request.user.is_authenticated:
            request.usage_data = UsageTracker.get_usage_data(request.user)
        else:
            request.usage_data = {
                'current': 0,
                'limit': 3,
                'remaining': 3,
                'percentage': 0,
                'subscription_type': 'free'
            }
        
        return view_func(request, *args, **kwargs)
        
    return wrapped_view

# Legacy compatibility wrapper
def usage_limit_decorator(*args, **kwargs):
    """Legacy wrapper for backward compatibility"""
    return usage_limit_required(*args, **kwargs)