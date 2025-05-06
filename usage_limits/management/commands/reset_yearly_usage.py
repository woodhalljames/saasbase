# usage_limits/management/commands/reset_yearly_usage.py
from django.core.management.base import BaseCommand
import stripe
from django.conf import settings
from subscriptions.models import CustomerSubscription
from usage_limits.usage_tracker import UsageTracker

class Command(BaseCommand):
    help = 'Reset usage for yearly subscribers'
    
    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get all active subscriptions
        subscriptions = CustomerSubscription.objects.filter(subscription_active=True)
        yearly_count = 0
        
        for sub in subscriptions:
            if not sub.stripe_subscription_id or not sub.user:
                continue
                
            try:
                # Get subscription details from Stripe
                stripe_sub = stripe.Subscription.retrieve(sub.stripe_subscription_id)
                
                # Check if this is a yearly subscription
                if stripe_sub.items.data and stripe_sub.items.data[0].plan.interval == 'year':
                    # Reset usage for yearly subscribers
                    UsageTracker.reset_usage(sub.user)
                    yearly_count += 1
                    
            except Exception as e:
                self.stderr.write(f"Error processing subscription {sub.id}: {str(e)}")
        
        self.stdout.write(f"Reset usage for {yearly_count} yearly subscribers")