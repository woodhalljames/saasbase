from __future__ import annotations
import typing
import re
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib import messages
from django.urls import reverse

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest
    from saas_base.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
    
    def get_login_redirect_url(self, request):
        """Redirect after login based on subscription status"""
        user = request.user
        
        # Check if user has an active subscription
        if hasattr(user, 'subscription') and user.has_active_subscription():
            return reverse("users:detail", kwargs={"username": user.username})
        
    
        
        # New user without subscription, go to dashboard
        return reverse("users:detail", kwargs={"username": user.username})



class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest, sociallogin: SocialLogin) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(self, request: HttpRequest, sociallogin: SocialLogin, data: dict[str, typing.Any]) -> User:
        """
        Auto-generate username from social data and populate user info
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Set name from social data
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        
        # Auto-generate username if not set
        if not user.username:
            user.username = self.generate_unique_username(data)
            
        return user
    
    def generate_unique_username(self, social_data):
        """Generate a unique username from social account data"""
        from saas_base.users.models import User
        
        # Try different strategies to generate username
        candidates = []
        
        # Strategy 1: From email (before @)
        if 'email' in social_data and social_data['email']:
            email_part = social_data['email'].split('@')[0]
            email_clean = re.sub(r'[^a-zA-Z0-9_]', '', email_part)
            if len(email_clean) >= 3:
                candidates.append(email_clean)
        
        # Strategy 2: From name (remove spaces, special chars)
        if 'name' in social_data and social_data['name']:
            name_clean = re.sub(r'[^a-zA-Z0-9_]', '', social_data['name'].lower())
            if len(name_clean) >= 3:
                candidates.append(name_clean)
        
        # Strategy 3: From first + last name
        if 'first_name' in social_data and social_data['first_name']:
            first = re.sub(r'[^a-zA-Z0-9_]', '', social_data['first_name'].lower())
            if 'last_name' in social_data and social_data['last_name']:
                last = re.sub(r'[^a-zA-Z0-9_]', '', social_data['last_name'].lower())
                combined = f"{first}{last}"
                if len(combined) >= 3:
                    candidates.append(combined)
                # Also try first.last format
                dotted = f"{first}.{last}"
                if len(dotted) >= 3:
                    candidates.append(dotted)
            if len(first) >= 3:
                candidates.append(first)
        
        # Find the first available username
        for base_candidate in candidates:
            if len(base_candidate) >= 3:
                # Try the base candidate first
                if not User.objects.filter(username=base_candidate).exists():
                    return base_candidate
                
                # Try with numbers if base is taken
                for i in range(1, 1000):
                    numbered_candidate = f"{base_candidate}{i}"
                    if not User.objects.filter(username=numbered_candidate).exists():
                        return numbered_candidate
        
        # Ultimate fallback
        import random
        return f"user{random.randint(1000, 9999)}"
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save user and add welcome message
        """
        user = super().save_user(request, sociallogin, form)
        
        # Add welcome message
        provider_name = sociallogin.account.provider.title()
        messages.success(
            request, 
            f"Welcome! Your account has been created using {provider_name}. "
            f"Your username is '{user.username}' and you can change it anytime in your profile."
        )
        
        return user
    
    def get_signup_redirect_url(self, request):
        """Redirect after social signup"""
        # Check if there's a price_id in session
        price_id = request.session.get('subscription_price_id')
        if price_id:
            return f"{reverse('subscriptions:pricing')}?checkout={price_id}"
        
        return reverse("subscriptions:pricing")
    
    def pre_social_login(self, request, sociallogin):
    """
    Auto-connect social accounts to existing users by email.
    Fixes: "An account already exists with this email address" error.
    """
    # If user is already logged in or social account already exists, skip
    if request.user.is_authenticated or sociallogin.is_existing:
        return
    
    # Try to find existing user by email
    try:
        email = sociallogin.account.extra_data.get('email', '').lower()
        if not email:
            return
        
        from saas_base.users.models import User
        user = User.objects.get(email__iexact=email)
        
        # Auto-connect this social account to the existing user
        sociallogin.connect(request, user)
        
        # Show friendly message
        provider_name = sociallogin.account.provider.title()
        messages.success(
            request,
            f"Welcome back! Your {provider_name} account has been connected."
        )
        
    except User.DoesNotExist:
        # No existing user, proceed with normal signup
        pass
    except Exception as e:
        # Log but don't break the flow
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in pre_social_login: {e}")
    

