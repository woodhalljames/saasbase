# wedding_shopping/admin.py
from django.contrib import admin
from .models import CoupleProfile, SocialMediaLink, WeddingLink


class SocialMediaLinkInline(admin.TabularInline):
    """Inline admin for social media links"""
    model = SocialMediaLink
    extra = 1
    fields = ['owner', 'url', 'display_name']
    readonly_fields = ['platform_info']
    
    def platform_info(self, obj):
        """Show detected platform info"""
        if obj.pk:
            return f"{obj.platform.title()} ({obj.platform_icon})"
        return "Will be detected from URL"
    platform_info.short_description = "Detected Platform"


class WeddingLinkInline(admin.TabularInline):
    """Inline admin for wedding links"""
    model = WeddingLink
    extra = 1
    fields = ['link_type', 'url', 'title', 'description', 'click_count']
    readonly_fields = ['service_info', 'click_count']
    
    def service_info(self, obj):
        """Show detected service info"""
        if obj.pk:
            return f"{obj.service_type.replace('_', ' ').title()} ({obj.service_icon})"
        return "Will be detected from URL"
    service_info.short_description = "Detected Service"


@admin.register(CoupleProfile)
class CoupleProfileAdmin(admin.ModelAdmin):
    """Admin interface for couple profiles"""
    list_display = [
        'couple_names', 'wedding_date', 'venue_name', 'is_public', 
        'social_count', 'wedding_links_count', 'created_at'
    ]
    list_filter = ['is_public', 'wedding_date', 'created_at']
    search_fields = ['partner_1_name', 'partner_2_name', 'venue_name', 'venue_location']
    readonly_fields = ['slug', 'share_token', 'wedding_url_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'partner_1_name', 'partner_2_name', 'wedding_date')
        }),
        ('Venue Details', {
            'fields': ('venue_name', 'venue_location'),
            'classes': ('collapse',)
        }),
        ('Photos', {
            'fields': ('couple_photo', 'venue_photo'),
            'classes': ('collapse',)
        }),
        ('Story', {
            'fields': ('couple_story',),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_public', 'slug', 'share_token', 'wedding_url_preview'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SocialMediaLinkInline, WeddingLinkInline]
    
    def social_count(self, obj):
        """Count of social media links"""
        return obj.social_links.count()
    social_count.short_description = "Social Links"
    
    def wedding_links_count(self, obj):
        """Count of wedding links"""
        return obj.wedding_links.count()
    wedding_links_count.short_description = "Wedding Links"
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('user').prefetch_related(
            'social_links', 'wedding_links'
        )


@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    """Admin interface for social media links"""
    list_display = ['couple_profile', 'owner', 'platform', 'display_name', 'url']
    list_filter = ['owner', 'couple_profile__is_public']
    search_fields = ['couple_profile__partner_1_name', 'couple_profile__partner_2_name', 'display_name', 'url']
    readonly_fields = ['platform', 'platform_icon', 'platform_color']
    
    fields = ['couple_profile', 'owner', 'url', 'display_name', 'platform', 'platform_icon', 'platform_color']
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('couple_profile')


@admin.register(WeddingLink)
class WeddingLinkAdmin(admin.ModelAdmin):
    """Admin interface for wedding links"""
    list_display = ['couple_profile', 'link_type', 'title', 'service_type', 'click_count', 'created_at']
    list_filter = ['link_type', 'couple_profile__is_public', 'created_at']
    search_fields = ['couple_profile__partner_1_name', 'couple_profile__partner_2_name', 'title', 'url']
    readonly_fields = ['service_type', 'service_icon', 'service_color', 'click_count', 'created_at']
    
    fields = [
        'couple_profile', 'link_type', 'url', 'title', 'description', 
        'service_type', 'service_icon', 'service_color',
        'click_count', 'created_at'
    ]
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('couple_profile')


# Note: RegistryLink is now just an alias for WeddingLink, so no separate registration needed