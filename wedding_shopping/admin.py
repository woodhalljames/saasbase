# wedding_shopping/admin.py
from django.contrib import admin
from .models import CoupleProfile, SocialMediaLink, RegistryLink


class SocialMediaLinkInline(admin.TabularInline):
    """Inline admin for social media links"""
    model = SocialMediaLink
    extra = 1
    fields = ['url', 'display_name']
    readonly_fields = ['platform_info']
    
    def platform_info(self, obj):
        """Show detected platform info"""
        if obj.pk:
            return f"{obj.platform.title()} ({obj.platform_icon})"
        return "Will be detected from URL"
    platform_info.short_description = "Detected Platform"


class RegistryLinkInline(admin.TabularInline):
    """Inline admin for registry links"""
    model = RegistryLink
    extra = 1
    fields = ['url', 'registry_name', 'description', 'click_count']
    readonly_fields = ['registry_info', 'click_count']
    
    def registry_info(self, obj):
        """Show detected registry info"""
        if obj.pk:
            return f"{obj.registry_type.replace('_', ' ').title()} ({obj.registry_icon})"
        return "Will be detected from URL"
    registry_info.short_description = "Detected Registry"


@admin.register(CoupleProfile)
class CoupleProfileAdmin(admin.ModelAdmin):
    """Admin interface for couple profiles"""
    list_display = [
        'couple_names', 'wedding_date', 'venue_name', 'is_public', 
        'social_count', 'registry_count', 'created_at'
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
    
    inlines = [SocialMediaLinkInline, RegistryLinkInline]
    
    def social_count(self, obj):
        """Count of social media links"""
        return obj.social_links.count()
    social_count.short_description = "Social Links"
    
    def registry_count(self, obj):
        """Count of registry links"""
        return obj.registry_links.count()
    registry_count.short_description = "Registries"
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('user').prefetch_related(
            'social_links', 'registry_links'
        )


@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    """Admin interface for social media links"""
    list_display = ['couple_profile', 'platform', 'display_name', 'url']
    list_filter = ['couple_profile__is_public']
    search_fields = ['couple_profile__partner_1_name', 'couple_profile__partner_2_name', 'display_name', 'url']
    readonly_fields = ['platform', 'platform_icon', 'platform_color']
    
    fields = ['couple_profile', 'url', 'display_name', 'platform', 'platform_icon', 'platform_color']
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('couple_profile')


@admin.register(RegistryLink)
class RegistryLinkAdmin(admin.ModelAdmin):
    """Admin interface for registry links"""
    list_display = ['couple_profile', 'registry_type', 'registry_name', 'click_count', 'created_at']
    list_filter = ['couple_profile__is_public', 'created_at']
    search_fields = ['couple_profile__partner_1_name', 'couple_profile__partner_2_name', 'registry_name', 'url']
    readonly_fields = ['registry_type', 'registry_icon', 'registry_color', 'click_count', 'created_at']
    
    fields = [
        'couple_profile', 'url', 'registry_name', 'description', 
        'registry_type', 'registry_icon', 'registry_color',
        'click_count', 'created_at'
    ]
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('couple_profile')