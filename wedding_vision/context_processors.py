# wedding_vision/context_processors.py
from usage_limits.usage_tracker import UsageTracker

def token_usage(request):
    """Add token usage data to all templates"""
    if request.user.is_authenticated:
        return {
            'token_usage': UsageTracker.get_usage_data(request.user)
        }
    return {'token_usage': None}