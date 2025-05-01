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

    def __str__(self):
        return f"{self.user.username}'s subscription"
    


class Product(models.Model):
    """Store Stripe product information locally"""
    stripe_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.get_interval_display()} ({self.amount_display})"
    
    @property
    def amount_display(self):
        """Return the amount in dollars/euros/etc."""
        return f"{self.amount / 100:.2f} {self.currency.upper()}"