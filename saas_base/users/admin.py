from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django import forms

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


class UserAdminForm(UserAdminChangeForm):
    """Custom form with token usage field"""
    set_remaining_tokens = forms.IntegerField(
        required=False,
        min_value=0,
        label="Set Remaining Tokens",
        help_text="Set how many tokens the user has available. This overrides their subscription limit.",
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set initial value from Redis if editing existing user
        if self.instance and self.instance.pk:
            from usage_limits.usage_tracker import UsageTracker
            usage_data = UsageTracker.get_usage_data(self.instance)
            remaining = usage_data['remaining']
            
            self.fields['set_remaining_tokens'].initial = remaining
            self.fields['set_remaining_tokens'].widget.attrs.update({
                'style': 'width: 150px; font-size: 16px; font-weight: bold;',
                'placeholder': f'{remaining} tokens'
            })


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminForm
    add_form = UserAdminCreationForm
    
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (
            _("Token Management"),
            {
                "fields": ("display_token_info", "set_remaining_tokens"),
                "description": "View and directly set user's available tokens"
            }
        ),
    )
    
    readonly_fields = ["display_token_info"]
    
    list_display = ["username", "name", "email", "token_usage_display", "is_superuser"]
    search_fields = ["name", "username", "email"]
    
    actions = ["reset_to_full", "add_50_tokens", "add_100_tokens", "set_to_zero"]
    
    def display_token_info(self, obj):
        """Display current token usage information"""
        from usage_limits.usage_tracker import UsageTracker
        
        usage_data = UsageTracker.get_usage_data(obj)
        
        html = f"""
        <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #0d6efd;">
            <h4 style="margin: 0 0 10px 0; color: #0d6efd;">📊 Current Token Status</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 8px 0; font-weight: 600;">Tokens Used:</td>
                    <td style="padding: 8px 0; text-align: right;">{usage_data['current']}</td>
                </tr>
                <tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 8px 0; font-weight: 600;">Subscription Limit:</td>
                    <td style="padding: 8px 0; text-align: right;">{usage_data['limit']}</td>
                </tr>
                <tr style="background: #e7f3ff;">
                    <td style="padding: 8px 0; font-weight: 700; color: #0d6efd;">✨ Available Now:</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: 700; font-size: 18px; color: #0d6efd;">{usage_data['remaining']}</td>
                </tr>
                <tr style="border-bottom: 1px solid #dee2e6;">
                    <td style="padding: 8px 0;">Usage Percentage:</td>
                    <td style="padding: 8px 0; text-align: right;">{usage_data['percentage']}%</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;">Subscription Type:</td>
                    <td style="padding: 8px 0; text-align: right; text-transform: capitalize;">{usage_data['subscription_type']}</td>
                </tr>
            </table>
        </div>
        
        <div style="margin-top: 15px; padding: 12px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
            <strong>💡 How to edit tokens:</strong>
            <ul style="margin: 8px 0 0 0; padding-left: 20px;">
                <li>Enter <strong>50</strong> → User gets 50 tokens to use</li>
                <li>Enter <strong>700</strong> → User gets 700 tokens (even beyond subscription limit!)</li>
                <li>Enter <strong>0</strong> → User has no tokens left (blocked)</li>
                <li>You can give MORE than their subscription limit if needed</li>
                <li>Example: User on 100-token plan can be given 1000 bonus tokens</li>
            </ul>
        </div>
        """
        return format_html(html)
    
    display_token_info.short_description = "Token Overview"
    
    def token_usage_display(self, obj):
        """Compact display for list view"""
        from usage_limits.usage_tracker import UsageTracker
        
        usage_data = UsageTracker.get_usage_data(obj)
        
        # Color code based on remaining tokens
        if usage_data['remaining'] == 0:
            color = '#dc3545'  # red
        elif usage_data['remaining'] <= 5:
            color = '#ffc107'  # yellow
        else:
            color = '#28a745'  # green
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} left</span> <span style="color: #6c757d;">(limit: {})</span>',
            color,
            usage_data['remaining'],
            usage_data['limit']
        )
    
    token_usage_display.short_description = "Tokens Available"
    
    def save_model(self, request, obj, form, change):
        """Save user and update token availability if changed"""
        super().save_model(request, obj, form, change)
        
        # Check if remaining tokens were set
        if change and 'set_remaining_tokens' in form.cleaned_data:
            new_remaining = form.cleaned_data['set_remaining_tokens']
            
            if new_remaining is not None:
                from usage_limits.usage_tracker import UsageTracker
                from usage_limits.redis_client import RedisClient
                
                redis_client = RedisClient.get_client()
                usage_key = f"usage:{obj.id}"  # FIXED: Use new key pattern
                
                # Get current data
                old_usage_data = UsageTracker.get_usage_data(obj)
                old_remaining = old_usage_data['remaining']
                limit = old_usage_data['limit']
                
                # FIXED: Allow negative usage for bonus tokens beyond limit
                # Formula: remaining = limit - used
                # Therefore: used = limit - remaining
                # 
                # Examples:
                # - User has 3 left, set to 50: used = limit - 50 (works perfectly)
                # - User has 100 limit, set to 700: used = 100 - 700 = -600 (negative = bonus)
                # - Set to 0: used = limit - 0 = limit (no tokens left)
                new_used = limit - new_remaining
                
                try:
                    redis_client.set(usage_key, new_used)
                    # No expiry - tokens persist until payment reset
                    
                    # Show appropriate message based on whether we're giving bonus tokens
                    if new_remaining > limit:
                        bonus = new_remaining - limit
                        messages.success(
                            request,
                            f"✅ Tokens updated: {old_remaining} → {new_remaining} available "
                            f"(+{bonus} bonus tokens beyond {limit} subscription limit)"
                        )
                    else:
                        messages.success(
                            request,
                            f"✅ Tokens updated: {old_remaining} → {new_remaining} available "
                            f"(Usage set to {new_used}/{limit})"
                        )
                except Exception as e:
                    messages.error(
                        request,
                        f"❌ Failed to update tokens: {str(e)}"
                    )
    
    # Admin actions
    def reset_to_full(self, request, queryset):
        """Give users their full subscription limit"""
        from usage_limits.redis_client import RedisClient
        
        redis_client = RedisClient.get_client()
        count = 0
        
        for user in queryset:
            usage_key = f"usage:{user.id}"  # FIXED: Use new key pattern
            try:
                redis_client.set(usage_key, 0)  # Set used to 0 = full limit available
                count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Failed to reset {user.username}: {str(e)}",
                    level=messages.ERROR
                )
        
        self.message_user(
            request,
            f"✅ Reset {count} user(s) to full subscription limit",
            level=messages.SUCCESS
        )
    
    reset_to_full.short_description = "✨ Reset to full limit"
    
    def add_50_tokens(self, request, queryset):
        """Add 50 tokens to selected users"""
        self._add_tokens(request, queryset, 50)
    
    add_50_tokens.short_description = "➕ Add 50 tokens"
    
    def add_100_tokens(self, request, queryset):
        """Add 100 tokens to selected users"""
        self._add_tokens(request, queryset, 100)
    
    add_100_tokens.short_description = "➕ Add 100 tokens"
    
    def set_to_zero(self, request, queryset):
        """Set users to 0 remaining tokens"""
        from usage_limits.usage_tracker import UsageTracker
        from usage_limits.redis_client import RedisClient
        
        redis_client = RedisClient.get_client()
        count = 0
        
        for user in queryset:
            usage_key = f"usage:{user.id}"  # FIXED: Use new key pattern
            try:
                limit = UsageTracker.get_user_limit(user)
                redis_client.set(usage_key, limit)  # Set used = limit, so remaining = 0
                count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Failed to set {user.username} to zero: {str(e)}",
                    level=messages.ERROR
                )
        
        self.message_user(
            request,
            f"✅ Set {count} user(s) to 0 tokens",
            level=messages.SUCCESS
        )
    
    set_to_zero.short_description = "🚫 Set to 0 tokens (block)"
    
    def _add_tokens(self, request, queryset, amount):
        """Helper method to add tokens to users"""
        from usage_limits.usage_tracker import UsageTracker
        from usage_limits.redis_client import RedisClient
        
        redis_client = RedisClient.get_client()
        count = 0
        
        for user in queryset:
            usage_key = f"usage:{user.id}"  # FIXED: Use new key pattern
            try:
                usage_data = UsageTracker.get_usage_data(user)
                current_used = usage_data['current']
                
                # FIXED: To add tokens, we reduce the "used" count
                # Allow negative values for bonus tokens beyond subscription limit
                # Example: used=97, add 50 tokens → new_used=47 (gives 53 more tokens if limit=100)
                # Example: used=10, add 50 tokens → new_used=-40 (40 bonus beyond limit)
                new_used = current_used - amount
                
                redis_client.set(usage_key, new_used)
                count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Failed to add tokens for {user.username}: {str(e)}",
                    level=messages.ERROR
                )
        
        self.message_user(
            request,
            f"✅ Added {amount} tokens to {count} user(s)",
            level=messages.SUCCESS
        )