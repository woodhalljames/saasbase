from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for SaaS Base.
    """
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view."""
        return reverse("users:detail", kwargs={"username": self.username})

    def has_active_subscription(self):
        """Check if user has an active subscription"""
        try:
            return self.subscription.subscription_active
        except:
            return False
    
    def get_stripe_customer_id(self):
        """Get Stripe customer ID for this user"""
        try:
            return self.subscription.stripe_customer_id
        except:
            return None
    
    def has_social_account(self):
        """Check if user has any connected social accounts"""
        try:
            from allauth.socialaccount.models import SocialAccount
            return SocialAccount.objects.filter(user=self).exists()
        except:
            return False
    
    def has_usable_password(self):
        """Check if user has set a password (not just social login)"""
        return super().has_usable_password()
    
    def needs_password_setup(self):
        """Check if social user needs to set up a password"""
        return self.has_social_account() and not self.has_usable_password()
    
    @property 
    def subscription(self):
        """Get or create subscription object for the user"""
        from subscriptions.models import CustomerSubscription
        
        try:
            return CustomerSubscription.objects.get(user=self)
        except CustomerSubscription.DoesNotExist:
            return CustomerSubscription.objects.create(
                user=self,
                subscription_active=False
            )