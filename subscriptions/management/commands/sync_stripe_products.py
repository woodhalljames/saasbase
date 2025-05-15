# subscriptions/management/commands/sync_stripe_products.py
import stripe
from django.core.management.base import BaseCommand
from django.conf import settings
from subscriptions.models import Product, Price

class Command(BaseCommand):
    help = 'Sync products and prices from Stripe while preserving custom fields'

    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Sync products
        products = stripe.Product.list(active=True)
        self.stdout.write(f"Found {len(products.data)} active products")
        
        for stripe_product in products.data:
            # Check if product already exists
            try:
                product = Product.objects.get(stripe_id=stripe_product.id)
                # Update only the fields that come from Stripe
                product.name = stripe_product.name
                product.description = stripe_product.description
                product.active = stripe_product.active
                product.save()
                self.stdout.write(f"Updated product: {product.name}")
            except Product.DoesNotExist:
                # Create new product
                product = Product.objects.create(
                    stripe_id=stripe_product.id,
                    name=stripe_product.name,
                    description=stripe_product.description,
                    active=stripe_product.active,
                    # Set default tokens based on metadata if available
                    tokens=stripe_product.metadata.get('tokens', 5) if hasattr(stripe_product, 'metadata') else 5
                )
                self.stdout.write(f"Created product: {product.name}")
        
        # Sync prices
        prices = stripe.Price.list(active=True, limit=100)
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
                
                # Check if price already exists
                try:
                    price = Price.objects.get(stripe_id=stripe_price.id)
                    # Update only fields that come from Stripe
                    price.active = True
                    price.currency = stripe_price.currency
                    price.amount = stripe_price.unit_amount
                    price.interval = recurring_interval
                    price.interval_count = recurring_interval_count
                    price.save()
                    self.stdout.write(f"Updated price: {price}")
                except Price.DoesNotExist:
                    # Create new price
                    price = Price.objects.create(
                        stripe_id=stripe_price.id,
                        product=product,
                        active=True,
                        currency=stripe_price.currency,
                        amount=stripe_price.unit_amount,
                        interval=recurring_interval,
                        interval_count=recurring_interval_count
                    )
                    self.stdout.write(f"Created price: {price}")
                
            except Product.DoesNotExist:
                self.stdout.write(f"Product not found for price: {stripe_price.id}")
        
        # Update tier mappings manually
        try:
            # Manually update price IDs for specific tiers
            from usage_limits.tier_config import TierLimits
            
            # Clear existing mappings
            for tier in TierLimits.TIERS:
                TierLimits.TIERS[tier]['stripe_price_ids'] = []
                
            # Add price IDs to tiers based on product name
            for price in Price.objects.filter(active=True).select_related('product'):
                tier = TierLimits.determine_tier(price)
                if price.stripe_id not in TierLimits.TIERS[tier]['stripe_price_ids']:
                    TierLimits.TIERS[tier]['stripe_price_ids'].append(price.stripe_id)
                    
            self.stdout.write("Updated tier mappings with new product information")
        except Exception as e:
            self.stdout.write(f"Error updating tier mappings: {str(e)}")
        
        self.stdout.write(self.style.SUCCESS('Successfully synced products and prices from Stripe'))