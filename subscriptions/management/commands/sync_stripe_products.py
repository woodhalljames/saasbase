# subscriptions/management/commands/sync_stripe_products.py
import stripe
from django.core.management.base import BaseCommand
from django.conf import settings
from subscriptions.models import Product, Price

class Command(BaseCommand):
    help = 'Sync products and prices from Stripe'

    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Sync products
        products = stripe.Product.list(active=True)
        self.stdout.write(f"Found {len(products.data)} active products")
        
        for stripe_product in products.data:
            product, created = Product.objects.update_or_create(
                stripe_id=stripe_product.id,
                defaults={
                    'name': stripe_product.name,
                    'description': stripe_product.description,
                    'active': stripe_product.active,
                }
            )
            
            if created:
                self.stdout.write(f"Created product: {product.name}")
            else:
                self.stdout.write(f"Updated product: {product.name}")
        
        # Sync prices
        prices = stripe.Price.list(active=True)
        self.stdout.write(f"Found {len(prices.data)} active prices")
        
        for stripe_price in prices.data:
            # Skip if no product or no recurring component
            if not stripe_price.product:
                continue
                
            # Check if recurring exists and has interval
            recurring_interval = None
            recurring_interval_count = 1
            
            if hasattr(stripe_price, 'recurring') and stripe_price.recurring:
                recurring_interval = stripe_price.recurring.get('interval', None)
                recurring_interval_count = stripe_price.recurring.get('interval_count', 1)
            
            # Only process subscription prices with intervals
            if not recurring_interval:
                continue
                
            try:
                product = Product.objects.get(stripe_id=stripe_price.product)
                
                price, created = Price.objects.update_or_create(
                    stripe_id=stripe_price.id,
                    defaults={
                        'product': product,
                        'active': True,
                        'currency': stripe_price.currency,
                        'amount': stripe_price.unit_amount,
                        'interval': recurring_interval,
                        'interval_count': recurring_interval_count,
                    }
                )
                
                if created:
                    self.stdout.write(f"Created price: {price}")
                else:
                    self.stdout.write(f"Updated price: {price}")
            except Product.DoesNotExist:
                self.stdout.write(f"Product not found for price: {stripe_price.id}")
        
        self.stdout.write(self.style.SUCCESS('Successfully synced products and prices from Stripe'))