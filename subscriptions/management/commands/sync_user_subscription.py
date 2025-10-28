# subscriptions/management/commands/sync_subscription.py
"""
Simple subscription sync command for production use.
Syncs a user's subscription data from Stripe to local database.
"""

import stripe
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

from subscriptions.models import CustomerSubscription, Price, Product

User = get_user_model()


class Command(BaseCommand):
    help = 'Sync user subscription from Stripe (production-safe)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'identifier',
            type=str,
            help='Username or email address'
        )
        parser.add_argument(
            '--customer-id',
            type=str,
            help='Force specific Stripe customer ID',
            default=None
        )
    
    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        identifier = options['identifier']
        force_customer_id = options.get('customer_id')
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Syncing subscription for: {identifier}")
        self.stdout.write(f"{'='*60}\n")
        
        try:
            # Step 1: Find user
            user = self._find_user(identifier)
            if not user:
                self.stdout.write(self.style.ERROR(f"✗ User not found: {identifier}"))
                return
            
            self.stdout.write(self.style.SUCCESS(f"✓ Found user: {user.username} ({user.email})"))
            
            # Step 2: Get or create subscription record
            subscription_record, created = CustomerSubscription.objects.get_or_create(user=user)
            
            if created:
                self.stdout.write(self.style.WARNING("⚠ Created new subscription record"))
            
            # Step 3: Get Stripe customer ID
            if force_customer_id:
                self.stdout.write(f"Using forced customer ID: {force_customer_id}")
                customer_id = force_customer_id
                subscription_record.stripe_customer_id = customer_id
                subscription_record.save()
            elif subscription_record.stripe_customer_id:
                customer_id = subscription_record.stripe_customer_id
                self.stdout.write(f"Using existing customer ID: {customer_id}")
            else:
                self.stdout.write(self.style.ERROR("✗ No Stripe customer ID found"))
                self.stdout.write("\nTo fix, run with --customer-id flag:")
                self.stdout.write(f"  python manage.py sync_subscription {identifier} --customer-id=cus_XXX")
                return
            
            # Step 4: Fetch from Stripe
            self.stdout.write(f"\nFetching from Stripe...")
            
            try:
                # Get subscriptions for this customer
                subscriptions = stripe.Subscription.list(
                    customer=customer_id,
                    limit=10
                )
                
                if not subscriptions.data:
                    self.stdout.write(self.style.WARNING("⚠ No subscriptions found in Stripe"))
                    return
                
                self.stdout.write(self.style.SUCCESS(f"✓ Found {len(subscriptions.data)} subscription(s)"))
                
                # Find active subscription
                active_sub = None
                for sub in subscriptions.data:
                    if sub.status in ['active', 'trialing']:
                        active_sub = sub
                        break
                
                if not active_sub and subscriptions.data:
                    active_sub = subscriptions.data[0]  # Use most recent
                    self.stdout.write(self.style.WARNING(f"⚠ No active subscription, using: {active_sub.status}"))
                
                # Step 5: Get subscription items (price/product info)
                self.stdout.write(f"\nFetching subscription details...")
                
                subscription_items = stripe.SubscriptionItem.list(
                    subscription=active_sub.id,
                    expand=['data.price.product']
                )
                
                # Step 6: Update database
                subscription_record.stripe_subscription_id = active_sub.id
                subscription_record.status = active_sub.status
                subscription_record.subscription_active = active_sub.status in ['active', 'trialing']
                
                if subscription_items.data:
                    price_item = subscription_items.data[0]
                    subscription_record.plan_id = price_item.price.id
                    
                    # Sync product/price to local DB
                    self._sync_product_price(price_item.price)
                
                subscription_record.save()
                
                # Step 7: Display results
                self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
                self.stdout.write(self.style.SUCCESS("✓ SYNC COMPLETED"))
                self.stdout.write(self.style.SUCCESS(f"{'='*60}\n"))
                
                self.stdout.write("Updated subscription:")
                self.stdout.write(f"  - User: {user.username} ({user.email})")
                self.stdout.write(f"  - Customer ID: {subscription_record.stripe_customer_id}")
                self.stdout.write(f"  - Subscription ID: {subscription_record.stripe_subscription_id}")
                self.stdout.write(f"  - Status: {subscription_record.status}")
                self.stdout.write(f"  - Active: {subscription_record.subscription_active}")
                self.stdout.write(f"  - Plan ID: {subscription_record.plan_id}")
                
                # Get token info
                try:
                    from usage_limits.usage_tracker import UsageTracker
                    usage_data = UsageTracker.get_usage_data(user)
                    self.stdout.write(f"\nToken allocation:")
                    self.stdout.write(f"  - Current: {usage_data['current']}")
                    self.stdout.write(f"  - Limit: {usage_data['limit']}")
                    self.stdout.write(f"  - Remaining: {usage_data['remaining']}")
                except Exception as e:
                    self.stdout.write(f"\n⚠ Could not fetch token info: {e}")
                
                self.stdout.write("")
                
            except stripe.error.InvalidRequestError as e:
                self.stdout.write(self.style.ERROR(f"\n✗ Stripe API error: {e}"))
            except stripe.error.AuthenticationError as e:
                self.stdout.write(self.style.ERROR(f"\n✗ Stripe authentication error: {e}"))
                self.stdout.write("Check your STRIPE_SECRET_KEY setting")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error: {e}"))
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def _find_user(self, identifier):
        """Find user by username or email"""
        try:
            # Try username first
            return User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                # Try email
                return User.objects.get(email=identifier)
            except User.DoesNotExist:
                return None
    
    def _sync_product_price(self, stripe_price):
        """Sync Stripe price and product to local database"""
        try:
            # Get product data
            if isinstance(stripe_price.product, str):
                product_data = stripe.Product.retrieve(stripe_price.product)
            else:
                product_data = stripe_price.product
            
            # Create/update product
            product, _ = Product.objects.update_or_create(
                stripe_id=product_data.id,
                defaults={
                    'name': product_data.name,
                    'description': product_data.description or '',
                    'active': product_data.active,
                }
            )
            
            # Create/update price
            Price.objects.update_or_create(
                stripe_id=stripe_price.id,
                defaults={
                    'product': product,
                    'active': stripe_price.active,
                    'currency': stripe_price.currency,
                    'amount': stripe_price.unit_amount or 0,
                    'interval': stripe_price.recurring.interval if stripe_price.recurring else 'month',
                    'interval_count': stripe_price.recurring.interval_count if stripe_price.recurring else 1,
                }
            )
            
            self.stdout.write(f"  ✓ Synced: {product.name} - ${stripe_price.unit_amount/100:.2f}")
            
        except Exception as e:
            self.stdout.write(f"  ⚠ Could not sync product: {e}")