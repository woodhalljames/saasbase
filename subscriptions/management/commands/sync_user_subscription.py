import stripe
from django.core.management.base import BaseCommand
from django.conf import settings
from saas_base.users.models import User
from subscriptions.models import CustomerSubscription, Price, Product

class Command(BaseCommand):
    help = 'Sync user subscription from Stripe - improved version'
    
    def add_arguments(self, parser):
        parser.add_argument('identifier', type=str, help='Username or email')
        parser.add_argument('--customer-id', type=str, help='Stripe customer ID (if known)', default=None)
    
    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        identifier = options['identifier']
        customer_id_override = options.get('customer_id')
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Syncing subscription for: {identifier}")
        self.stdout.write(f"{'='*60}\n")
        
        try:
            # Find user by username or email
            try:
                user = User.objects.get(username=identifier)
                self.stdout.write(self.style.SUCCESS(f"✓ Found user by username: {user.username}"))
            except User.DoesNotExist:
                user = User.objects.get(email=identifier)
                self.stdout.write(self.style.SUCCESS(f"✓ Found user by email: {user.email}"))
            
            # Get or create subscription record
            sub, created = CustomerSubscription.objects.get_or_create(user=user)
            
            if created:
                self.stdout.write(self.style.WARNING("⚠ Created new CustomerSubscription record"))
            
            # Display current state
            self.stdout.write(f"\nCurrent DB state:")
            self.stdout.write(f"  - stripe_customer_id: {sub.stripe_customer_id or 'NOT SET'}")
            self.stdout.write(f"  - stripe_subscription_id: {sub.stripe_subscription_id or 'NOT SET'}")
            self.stdout.write(f"  - subscription_active: {sub.subscription_active}")
            self.stdout.write(f"  - plan_id: {sub.plan_id or 'NOT SET'}")
            self.stdout.write(f"  - status: {sub.status or 'NOT SET'}")
            
            # Use override customer ID if provided
            if customer_id_override:
                self.stdout.write(f"\n⚠ Using override customer ID: {customer_id_override}")
                sub.stripe_customer_id = customer_id_override
                sub.save()
            
            # Check if we have a customer ID
            if not sub.stripe_customer_id:
                self.stdout.write(self.style.ERROR("\n✗ No Stripe customer ID found!"))
                self.stdout.write(f"\nTo fix, run with customer ID:")
                self.stdout.write(f"  python manage.py sync_user_subscription {identifier} --customer-id=cus_XXX")
                return
            
            # Fetch subscriptions from Stripe
            self.stdout.write(f"\nFetching subscriptions from Stripe...")
            subscriptions = stripe.Subscription.list(
                customer=sub.stripe_customer_id,
                limit=10,
                expand=['data.items.data.price.product']
            )
            
            if not subscriptions.data:
                self.stdout.write(self.style.ERROR("✗ No subscriptions found in Stripe"))
                return
            
            self.stdout.write(self.style.SUCCESS(f"✓ Found {len(subscriptions.data)} subscription(s) in Stripe\n"))
            
            # Show all subscriptions
            for idx, s in enumerate(subscriptions.data):
                self.stdout.write(f"Subscription {idx + 1}:")
                self.stdout.write(f"  - ID: {s.id}")
                self.stdout.write(f"  - Status: {s.status}")
                self.stdout.write(f"  - Created: {s.created}")
                if s.items and s.items.data:
                    price = s.items.data[0].price
                    self.stdout.write(f"  - Price ID: {price.id}")
                    self.stdout.write(f"  - Amount: ${price.unit_amount/100:.2f}/{price.recurring.interval}")
                self.stdout.write("")
            
            # Use the first active subscription
            subscription = None
            for s in subscriptions.data:
                if s.status in ['active', 'trialing']:
                    subscription = s
                    break
            
            if not subscription:
                subscription = subscriptions.data[0]
                self.stdout.write(self.style.WARNING(f"⚠ No active subscription, using most recent: {subscription.status}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✓ Using active subscription: {subscription.id}"))
            
            # Update the database
            self.stdout.write(f"\nUpdating database...")
            
            sub.stripe_subscription_id = subscription.id
            sub.status = subscription.status
            sub.subscription_active = subscription.status in ['active', 'trialing']
            
            # Get plan_id from subscription items
            if subscription.items and subscription.items.data:
                price_item = subscription.items.data[0]
                sub.plan_id = price_item.price.id
                
                # Sync product/price to local DB
                self._sync_product_and_price(price_item.price)
            
            sub.save()
            
            # Display final state
            self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
            self.stdout.write(self.style.SUCCESS(f"✓ SYNC COMPLETED"))
            self.stdout.write(self.style.SUCCESS(f"{'='*60}\n"))
            
            self.stdout.write(f"Updated DB state:")
            self.stdout.write(f"  - stripe_customer_id: {sub.stripe_customer_id}")
            self.stdout.write(f"  - stripe_subscription_id: {sub.stripe_subscription_id}")
            self.stdout.write(f"  - subscription_active: {sub.subscription_active}")
            self.stdout.write(f"  - plan_id: {sub.plan_id}")
            self.stdout.write(f"  - status: {sub.status}")
            
            # Get token limit
            try:
                price = Price.objects.select_related('product').get(stripe_id=sub.plan_id)
                self.stdout.write(f"  - token_limit: {price.product.tokens}")
            except Price.DoesNotExist:
                self.stdout.write(f"  - token_limit: (price not synced)")
            
            self.stdout.write("")
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"✗ User not found: {identifier}"))
            self.stdout.write("Available users with subscriptions:")
            for cs in CustomerSubscription.objects.all()[:10]:
                self.stdout.write(f"  - {cs.user.username} ({cs.user.email})")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def _sync_product_and_price(self, stripe_price):
        """Sync product and price to local database"""
        try:
            # Ensure we have the full product data
            if isinstance(stripe_price.product, str):
                product_data = stripe.Product.retrieve(stripe_price.product)
            else:
                product_data = stripe_price.product
            
            # Sync product
            product, created = Product.objects.update_or_create(
                stripe_id=product_data.id,
                defaults={
                    'name': product_data.name,
                    'description': product_data.description or '',
                    'active': product_data.active,
                }
            )
            
            # Sync price
            price, created = Price.objects.update_or_create(
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
            
            self.stdout.write(f"  ✓ Synced product: {product.name} ({product.tokens} tokens)")
            
        except Exception as e:
            self.stdout.write(f"  ⚠ Warning: Could not sync product/price: {str(e)}")