# Add this to usage_limits/tier_config.py (update the existing TIERS dict)

class TierLimits:
    """Define usage limits for each subscription tier"""
    TIERS = {
        'basic': {
            'monthly_limit': 5,  # Updated to match the 5 actions seen in the dashboard
            'max_prompts_per_image': 2,  # Can use 2 prompts per image
            'stripe_price_ids': [],  # We'll populate this dynamically from the database
        },
        'pro': {
            'monthly_limit': 50,
            'max_prompts_per_image': 5,  # Can use 5 prompts per image
            'stripe_price_ids': [],
        },
        'enterprise': {
            'monthly_limit': 200,
            'max_prompts_per_image': 10,  # Can use 10 prompts per image
            'stripe_price_ids': [],
        },
        'free': {
            'monthly_limit': 3,  # Default for users without a subscription
            'max_prompts_per_image': 1,  # Can only use 1 prompt per image
            'stripe_price_ids': [],
        }
    }

    @classmethod
    def get_max_prompts_for_tier(cls, tier_name):
        """Get the maximum prompts per image for a tier"""
        return cls.TIERS.get(tier_name, cls.TIERS['free'])['max_prompts_per_image']
    
    @classmethod
    def get_user_max_prompts(cls, user):
        """Get the maximum prompts per image for a user based on their subscription"""
        if not user or not user.is_authenticated:
            return cls.TIERS['free']['max_prompts_per_image']
        
        try:
            subscription = getattr(user, 'subscription', None)
            if not subscription or not subscription.subscription_active:
                return cls.TIERS['free']['max_prompts_per_image']
            
            tier = cls.get_tier_from_price_id(subscription.plan_id)
            return cls.get_max_prompts_for_tier(tier)
            
        except Exception:
            return cls.TIERS['free']['max_prompts_per_image']

    # ... (keep all existing methods)
    
    @classmethod
    def initialize_from_db(cls):
        """Initialize price IDs from the database when the app starts"""
        try:
            from subscriptions.models import Price
            
            # Get all active prices from the database
            prices = Price.objects.filter(active=True).select_related('product')
            
            # Map prices to tiers based on amount or product name
            for price in prices:
                # Determine tier by price or product name
                tier_name = cls.determine_tier(price)
                
                # Add price ID to the appropriate tier
                if tier_name in cls.TIERS:
                    if price.stripe_id not in cls.TIERS[tier_name]['stripe_price_ids']:
                        cls.TIERS[tier_name]['stripe_price_ids'].append(price.stripe_id)
        except Exception as e:
            # Log the error but don't crash the application
            import logging
            logging.error(f"Error initializing tier config: {str(e)}")

    @classmethod
    def determine_tier(cls, price):
        """Determine which tier a price belongs to based on product name or amount"""
        # Check product name first
        product_name = price.product.name.lower()
        
        if "basic" in product_name or "starter" in product_name or "happy couple" in product_name:
            return "basic"
        elif "pro" in product_name or "professional" in product_name:
            return "pro"
        elif "enterprise" in product_name or "business" in product_name:
            return "enterprise"
        
        # If no match by name, check by price amount
        amount = price.amount / 100  # Convert from cents to dollars
        
        if amount <= 10:
            return "free"
        elif amount <= 60:  # Your Happy Couple plan is 54.99
            return "basic"
        elif amount <= 120:
            return "pro"
        else:
            return "enterprise"

    @classmethod
    def get_tier_from_price_id(cls, price_id):
        """Get the tier name from a Stripe price ID"""
        if not price_id:
            return 'free'
            
        for tier, config in cls.TIERS.items():
            if price_id in config['stripe_price_ids']:
                return tier
                
        # If price_id not found in our mapping, determine it on-the-fly
        try:
            from subscriptions.models import Price
            price = Price.objects.filter(stripe_id=price_id).first()
            if price:
                tier = cls.determine_tier(price)
                # Add to our mapping for future use
                if tier in cls.TIERS and price_id not in cls.TIERS[tier]['stripe_price_ids']:
                    cls.TIERS[tier]['stripe_price_ids'].append(price_id)
                return tier
        except Exception:
            pass
            
        return 'free'  # Default tier if price ID not found

    @classmethod
    def get_limit_for_tier(cls, tier_name):
        """Get the monthly usage limit for a tier"""
        return cls.TIERS.get(tier_name, cls.TIERS['free'])['monthly_limit']