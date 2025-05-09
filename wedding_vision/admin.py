# wedding_vision/admin.py
from django.contrib import admin
from .models import VenueImage, ThemeTemplate, GeneratedImage, ImageFeedback

@admin.register(ThemeTemplate)
class ThemeTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'token_cost', 'active', 'created_at')
    list_filter = ('active', 'token_cost')
    search_fields = ('name', 'description')

@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'user__username')

@admin.register(GeneratedImage)
class GeneratedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'theme', 'tokens_used', 'is_saved', 'status', 'created_at')
    list_filter = ('status', 'is_saved', 'tokens_used', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('tokens_used', 'created_at')

@admin.register(ImageFeedback)
class ImageFeedbackAdmin(admin.ModelAdmin):
    list_display = ('generated_image', 'feedback_type', 'created_at')
    list_filter = ('feedback_type', 'created_at')
    search_fields = ('comment', 'generated_image__user__username')