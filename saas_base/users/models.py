from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for SaaS Base.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
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
        
    