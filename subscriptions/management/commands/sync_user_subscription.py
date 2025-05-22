import stripe
from django.core.management.base import BaseCommand
from django.conf import settings
from saas_base.users.models import User
from subscriptions.models import CustomerSubscription

class Command(BaseCommand):
    help = 'Sync user subscription from Stripe'
    
    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
    
    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            sub, created = CustomerSubscription.objects.get_or_create(user=user)
            
            if not sub.stripe_customer_id:
                self.stdout.write("No Stripe customer ID found")
                return
            
            subscriptions = stripe.Subscription.list(
                customer=sub.stripe_customer_id,
                expand=['data.items.data.price.product']
            )
            
            if not subscriptions.data:
                self.stdout.write("No subscriptions found")
                return
                
            subscription = subscriptions.data[0]
            sub.stripe_subscription_id = subscription.id
            sub.status = subscription.status
            sub.subscription_active = subscription.status in ['active', 'trialing']
            
            # Fix: Properly access the price ID from the subscription items
            if subscription.items and subscription.items.data:
                sub.plan_id = subscription.items.data[0].price.id
                
            sub.save()
            self.stdout.write(f"Subscription updated: {sub.status}, plan_id: {sub.plan_id}")
        except User.DoesNotExist:
            self.stdout.write(f"User {username} not found")