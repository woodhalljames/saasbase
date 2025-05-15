# subscriptions/admin.py
from django.contrib import admin
from .models import Product, Price, CustomerSubscription

class PriceInline(admin.TabularInline):
    model = Price
    extra = 0
    fields = ('stripe_id', 'active', 'amount', 'currency', 'interval', 
              'interval_count', 'display_name', 'is_featured')
    readonly_fields = ('stripe_id', 'amount', 'currency', 'interval', 'interval_count')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'show_on_site', 'tokens', 'display_order', 'highlight')
    list_filter = ('active', 'show_on_site', 'highlight')
    search_fields = ('name', 'description')
    readonly_fields = ('stripe_id', 'created_at', 'updated_at')
    list_editable = ('show_on_site', 'active', 'highlight')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'active', 'show_on_site', 'stripe_id')
        }),
        ('Display Options', {
            'fields': ('display_order', 'highlight', 'tokens', 'features'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    inlines = [PriceInline]
    
    def get_readonly_fields(self, request, obj=None):
        # Make more fields readonly if this is an existing object
        if obj:
            return self.readonly_fields
        return ('created_at', 'updated_at')

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'product', 'active', 'amount_display', 
                    'interval', 'is_featured')
    list_filter = ('active', 'is_featured', 'interval', 'product')
    search_fields = ('stripe_id', 'product__name')
    readonly_fields = ('stripe_id', 'product', 'amount', 'currency', 
                      'interval', 'interval_count', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('product', 'stripe_id', 'active')
        }),
        ('Price Details', {
            'fields': ('amount', 'currency', 'interval', 'interval_count'),
        }),
        ('Display Options', {
            'fields': ('display_name', 'is_featured'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

@admin.register(CustomerSubscription)
class CustomerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stripe_customer_id', 'status', 'subscription_active')
    list_filter = ('subscription_active', 'status')
    search_fields = ('user__username', 'user__email', 'stripe_customer_id', 
                    'stripe_subscription_id')
    readonly_fields = ('user', 'stripe_customer_id', 'stripe_subscription_id', 
                      'status', 'plan_id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'subscription_active')
        }),
        ('Stripe Details', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id', 'status', 'plan_id'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )