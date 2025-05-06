# usage_limits/tier_config.py
class TierLimits:
    """Define usage limits for each subscription tier"""
    TIERS = {
        'basic': {
            'monthly_limit': 300,
            'stripe_price_ids': ['price_basic_monthly', 'price_basic_yearly'],  # Replace with your actual price IDs
        },
        'pro': {
            'monthly_limit': 900,
            'stripe_price_ids': ['price_pro_monthly', 'price_pro_yearly'],  # Replace with your actual price IDs
        },
        'enterprise': {
            'monthly_limit': 2000,
            'stripe_price_ids': ['price_enterprise_monthly', 'price_enterprise_yearly'],  # Replace with your actual price IDs
        },
        'free': {
            'monthly_limit': 5,  # Default for users without a subscription
            'stripe_price_ids': [],
        }
    }

    @classmethod
    def get_tier_from_price_id(cls, price_id):
        """Get the tier name from a Stripe price ID"""
        if not price_id:
            return 'free'
            
        for tier, config in cls.TIERS.items():
            if price_id in config['stripe_price_ids']:
                return tier
        return 'free'  # Default tier if price ID not found

    @classmethod
    def get_limit_for_tier(cls, tier_name):
        """Get the monthly usage limit for a tier"""
        return cls.TIERS.get(tier_name, cls.TIERS['free'])['monthly_limit']