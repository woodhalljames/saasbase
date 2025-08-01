import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
from .forms import NewsletterSignupForm
from .models import NewsletterSubscription

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@method_decorator(csrf_protect, name='dispatch')
class NewsletterSignupView(View):
    def post(self, request):
        # Handle AJAX form submission
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
        
        try:
            # Parse JSON data
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter your email address.'
                })
            
            # Check if already subscribed first (for better UX)
            existing_subscription = NewsletterSubscription.objects.filter(email=email).first()
            
            if existing_subscription and existing_subscription.is_active:
                return JsonResponse({
                    'success': False,
                    'message': 'You\'re already subscribed to our newsletter! Check your inbox for updates.'
                })
            
            # Create form with data
            form = NewsletterSignupForm(data={'email': email})
            
            if form.is_valid():
                try:
                    # Handle both new subscriptions and reactivations
                    if existing_subscription and not existing_subscription.is_active:
                        # Reactivate existing subscription
                        existing_subscription.is_active = True
                        existing_subscription.ip_address = get_client_ip(request)
                        existing_subscription.user_agent = request.META.get('HTTP_USER_AGENT', '')
                        existing_subscription.save()
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'Welcome back! Your subscription has been reactivated.'
                        })
                    else:
                        # Create new subscription
                        subscription = form.save(commit=False)
                        subscription.ip_address = get_client_ip(request)
                        subscription.user_agent = request.META.get('HTTP_USER_AGENT', '')
                        subscription.save()
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'Thank you! You\'ve been subscribed to our newsletter.'
                        })
                        
                except Exception as save_error:
                    logger.error(f"Error saving newsletter subscription: {save_error}")
                    return JsonResponse({
                        'success': False,
                        'message': 'Something went wrong while subscribing. Please try again.'
                    })
            else:
                # Return form errors
                error_message = 'Please check your email and try again.'
                
                if 'email' in form.errors:
                    error_message = form.errors['email'][0]
                
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid request data.'
            }, status=400)
        except Exception as e:
            logger.error(f"Newsletter signup error: {e}")
            return JsonResponse({
                'success': False, 
                'message': 'Something went wrong. Please try again later.'
            }, status=500)


newsletter_signup = NewsletterSignupView.as_view()