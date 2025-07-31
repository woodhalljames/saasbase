import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from .forms import NewsletterSignupForm


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@method_decorator(csrf_protect, name='dispatch')
class NewsletterSignupView(View):
    def post(self, request):
        # Handle AJAX form submission
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
        
        try:
            # Parse JSON data
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            # Create form with data
            form = NewsletterSignupForm(data={'email': email})
            
            if form.is_valid():
                subscription = form.save(commit=False)
                subscription.ip_address = get_client_ip(request)
                subscription.user_agent = request.META.get('HTTP_USER_AGENT', '')
                subscription.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you! You\'ve been subscribed to our newsletter.'
                })
            else:
                # Return form errors
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list[0]  # Get first error
                
                return JsonResponse({
                    'success': False,
                    'errors': errors,
                    'message': errors.get('email', 'Please check your email and try again.')
                })
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'Something went wrong. Please try again.'}, status=500)


newsletter_signup = NewsletterSignupView.as_view()
