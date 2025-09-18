# usage_limits/tier_config.py - Updated for wedding venue processing

class TierLimits:
    """Define usage limits for wedding venue visualization"""
    TIERS = {
        'free': {
            'monthly_limit': 2,  # 1 images per month
            'stripe_price_ids': [],
        },
        'basic': {
            'monthly_limit': 15,  # 15 images per month
            'stripe_price_ids': [],
        },
        'pro': {
            'monthly_limit': 50,  # 50 images per month
            'stripe_price_ids': [],
        },
        'enterprise': {
            'monthly_limit': 200,  # 200 images per month
            'stripe_price_ids': [],
        }
    }

    @classmethod
    def get_limit_for_tier(cls, tier_name):
        """Get the monthly image processing limit for a tier"""
        return cls.TIERS.get(tier_name, cls.TIERS['free'])['monthly_limit']

    @classmethod
    def get_user_limit(cls, user):
        """Get the monthly image processing limit for a user"""
        if not user or not user.is_authenticated:
            return cls.TIERS['free']['monthly_limit']
        
        try:
            subscription = getattr(user, 'subscription', None)
            if not subscription or not subscription.subscription_active:
                return cls.TIERS['free']['monthly_limit']
            
            # Try to get limit from Product model first
            plan_id = subscription.plan_id
            if plan_id:
                try:
                    from subscriptions.models import Price
                    price = Price.objects.select_related('product').get(stripe_id=plan_id)
                    if price.product.tokens > 0:
                        return price.product.tokens
                except Price.DoesNotExist:
                    pass
            
            # Fallback to tier-based limits
            tier = cls.get_tier_from_price_id(plan_id)
            return cls.get_limit_for_tier(tier)
            
        except Exception:
            return cls.TIERS['free']['monthly_limit']

    @classmethod
    def get_tier_from_price_id(cls, price_id):
        """Get the tier name from a Stripe price ID"""
        if not price_id:
            return 'free'
            
        for tier, config in cls.TIERS.items():
            if price_id in config['stripe_price_ids']:
                return tier
                
        # If price_id not found, determine it on-the-fly
        try:
            from subscriptions.models import Price
            price = Price.objects.filter(stripe_id=price_id).first()
            if price:
                tier = cls.determine_tier(price)
                if tier in cls.TIERS and price_id not in cls.TIERS[tier]['stripe_price_ids']:
                    cls.TIERS[tier]['stripe_price_ids'].append(price_id)
                return tier
        except Exception:
            pass
            
        return 'free'

    @classmethod
    def determine_tier(cls, price):
        """Determine which tier a price belongs to based on product name or amount"""
        product_name = price.product.name.lower()
        
        if "basic" in product_name or "starter" in product_name or "happy couple" in product_name:
            return "basic"
        elif "pro" in product_name or "professional" in product_name:
            return "pro"
        elif "enterprise" in product_name or "business" in product_name:
            return "enterprise"
        
        # Fallback to price amount
        amount = price.amount / 100
        if amount <= 10:
            return "free"
        elif amount <= 60:
            return "basic"
        elif amount <= 120:
            return "pro"
        else:
            return "enterprise"

   