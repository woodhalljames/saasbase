# wedding_shopping/admin.py - Simple admin for basic moderation
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import CoupleProfile, WeddingLink


class WeddingLinkInline(admin.TabularInline):
    """Inline admin for wedding links"""
    model = WeddingLink
    extra = 0
    fields = ['title', 'url', 'description', 'click_count']
    readonly_fields = ['click_count']


@admin.register(CoupleProfile)
class CoupleProfileAdmin(admin.ModelAdmin):
    """Simple admin for wedding page moderation"""
    list_display = [
        'couple_names', 'user_email', 'wedding_date', 'venue_display', 'is_public', 
        'link_count', 'created_at', 'view_page_link'
    ]
    list_filter = ['is_public', 'created_at', 'wedding_date']
    search_fields = [
        'partner_1_name', 'partner_2_name', 'venue_name', 'venue_location',
        'user__email', 'user__username', 'user__first_name', 'user__last_name'
    ]
    readonly_fields = ['slug', 'share_token', 'created_at', 'updated_at', 'view_page_link']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'partner_1_name', 'partner_2_name', 'wedding_date')
        }),
        ('Venue Details', {
            'fields': ('venue_name', 'venue_location'),
        }),
        ('Photos', {
            'fields': ('couple_photo', 'venue_photo'),
        }),
        ('Story', {
            'fields': ('couple_story',),
        }),
        ('Settings', {
            'fields': ('is_public', 'slug', 'share_token', 'view_page_link'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    inlines = [WeddingLinkInline]
    
    def user_email(self, obj):
        """Show user email with link to user admin"""
        user_url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', user_url, obj.user.email)
    user_email.short_description = "User Email"
    user_email.admin_order_field = 'user__email'
    
    def venue_display(self, obj):
        """Show venue info compactly"""
        parts = []
        if obj.venue_name:
            parts.append(obj.venue_name)
        if obj.venue_location:
            # Show just city if it's a full address
            if obj.display_city:
                parts.append(obj.display_city)
            else:
                parts.append(obj.venue_location)
        return ' - '.join(parts) if parts else '-'
    venue_display.short_description = "Venue"
    
    def link_count(self, obj):
        """Count wedding links"""
        return obj.wedding_links.count()
    link_count.short_description = "Links"
    
    def view_page_link(self, obj):
        """Link to view the public wedding page"""
        if obj.slug:
            url = obj.get_absolute_url()
            return format_html(
                '<a href="{}" target="_blank" class="viewlink">View Page</a>', 
                url
            )
        return "No page"
    view_page_link.short_description = "Wedding Page"
    
    # Simple actions for moderation
    actions = ['make_private', 'make_public', 'delete_selected']
    
    def make_private(self, request, queryset):
        """Make selected pages private (hide from public)"""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} wedding page(s) made private.')
    make_private.short_description = "Hide selected pages from public"
    
    def make_public(self, request, queryset):
        """Make selected pages public"""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} wedding page(s) made public.')
    make_public.short_description = "Make selected pages public"
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('user').prefetch_related('wedding_links')


@admin.register(WeddingLink)
class WeddingLinkAdmin(admin.ModelAdmin):
    """Simple admin for wedding links"""
    list_display = ['couple_profile', 'title', 'url_display', 'click_count', 'created_at']
    list_filter = ['created_at']
    search_fields = [
        'couple_profile__partner_1_name', 'couple_profile__partner_2_name', 
        'title', 'url', 'description'
    ]
    readonly_fields = ['click_count', 'created_at']
    ordering = ['-created_at']
    
    fields = [
        'couple_profile', 'title', 'url', 'description', 
        'click_count', 'created_at'
    ]
    
    def url_display(self, obj):
        """Show truncated URL"""
        if len(obj.url) > 50:
            return obj.url[:47] + "..."
        return obj.url
    url_display.short_description = "URL"
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('couple_profile')


# Custom admin site titles
admin.site.site_header = "DreamWedAI Administration"
admin.site.site_title = "DreamWedAI Admin"
admin.site.index_title = "Wedding Pages Management"