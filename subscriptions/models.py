from django.db import models

# Create your models here.
# saas_base/subscriptions/models.py
from django.db import models
from django.conf import settings

class CustomerSubscription(models.Model):
    """Store minimal subscription data - Stripe is the source of truth"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    plan_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_usage_data(self):
        """Get the usage data for this subscription's user"""
        from usage_limits.usage_tracker import UsageTracker
        if not self.user:
            return None
        return UsageTracker.get_usage_data(self.user)

    def get_subscription_details(self):
        """Get detailed information about the current subscription"""
        if not self.subscription_active or not self.plan_id:
            return None
            
        try:
            # Get price and associated product information
            price = Price.objects.select_related('product').get(stripe_id=self.plan_id)
            return {
                'name': price.product.name,
                'description': price.product.description,
                'amount': price.amount_display,
                'interval': price.get_interval_display(),
                'status': self.status,
                'tokens': price.product.tokens,  # Include tokens in details
            }
        except Price.DoesNotExist:
            return {
                'name': 'Unknown Plan',
                'description': None,
                'amount': None, 
                'interval': None,
                'status': self.status,
                'tokens': 0,
            }

    def get_stripe_subscription(self):
        """Get subscription details directly from Stripe"""
        if not self.stripe_subscription_id:
            return None
            
        import stripe
        from django.conf import settings
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            return stripe.Subscription.retrieve(
                self.stripe_subscription_id,
                expand=['items.data.price.product']
            )
        except Exception:
            return None
        


        # Add to subscriptions/models.py
    def get_tier_name(self):
        """Get the subscription tier name based on the plan_id"""
        from usage_limits.tier_config import TierLimits
        if not self.plan_id or not self.subscription_active:
            return 'free'
        return TierLimits.get_tier_from_price_id(self.plan_id)

    def get_monthly_limit(self):
        """Get the monthly usage limit based on the subscription tier"""
        from usage_limits.tier_config import TierLimits
        return TierLimits.get_limit_for_tier(self.get_tier_name())

   
    

    

    def __str__(self):
        return f"{self.user.username}'s subscription"
    


class Product(models.Model):
    """Store Stripe product information locally with additional customization fields"""
    stripe_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    
    # Additional fields for customization
    features = models.TextField(blank=True, null=True, 
                               help_text="Feature list in JSON format. Example: ['Feature 1', 'Feature 2']")
    display_order = models.IntegerField(default=0, 
                                       help_text="Order to display products (lower numbers first)")
    highlight = models.BooleanField(default=False, 
                                   help_text="Highlight this product on the pricing page")
    tokens = models.IntegerField(default=5, 
                                help_text="Number of tokens/actions included with this product")
    show_on_site = models.BooleanField(default=True,
                                      help_text="Show this product on the pricing page")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_features_list(self):
        """Returns the features as a Python list"""
        if not self.features:
            return []
        
        import json
        try:
            return json.loads(self.features)
        except json.JSONDecodeError:
            # If not valid JSON, assume it's a comma-separated list
            return [f.strip() for f in self.features.split(',')]

    class Meta:
        ordering = ['display_order', 'name']

class Price(models.Model):
    """Store Stripe price information locally"""
    INTERVAL_CHOICES = (
        ('month', 'Monthly'),
        ('year', 'Yearly'),
        ('week', 'Weekly'),
        ('day', 'Daily'),
    )
    
    stripe_id = models.CharField(max_length=255, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    active = models.BooleanField(default=True)
    currency = models.CharField(max_length=3, default='usd')
    amount = models.IntegerField()  # Amount in cents
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)
    interval_count = models.IntegerField(default=1)
    display_name = models.CharField(max_length=100, blank=True, null=True,
                                  help_text="Optional name to display instead of the default")
    is_featured = models.BooleanField(default=False,
                                     help_text="Feature this pricing option on the pricing page")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.get_interval_display()} ({self.amount_display})"
    
    @property
    def amount_display(self):
        """Return the amount in dollars/euros/etc."""
        return f"{self.amount / 100:.2f} {self.currency.upper()}"
    
    class Meta:
        ordering = ['product__display_order', 'interval', 'amount']
    
