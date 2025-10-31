# image_processing/admin.py - Updated for new model structure

import os
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    UserImage, ImageProcessingJob, ProcessedImage, 
    Collection, CollectionItem, Favorite, FavoriteUpload,
    WEDDING_THEMES, SPACE_TYPES, COLOR_SCHEMES,
    ENGAGEMENT_SETTINGS, ENGAGEMENT_ACTIVITIES,
    WEDDING_MOMENTS, WEDDING_SETTINGS, ATTIRE_STYLES,
    COMPOSITION_CHOICES, EMOTIONAL_TONE_CHOICES
)

User = get_user_model()


# Custom Admin Base Classes
class ImageDisplayMixin:
    """Mixin for displaying image thumbnails in admin"""
    
    def image_thumbnail(self, obj):
        """Display thumbnail with link to full image"""
        if hasattr(obj, 'image') and obj.image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 4px;" '
                'title="Click to view full size" />'
                '</a>',
                obj.image.url,
                obj.image.url
            )
        elif hasattr(obj, 'thumbnail') and obj.thumbnail:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 4px;" '
                'title="Click to view full size" />'
                '</a>',
                obj.thumbnail.url,
                obj.thumbnail.url
            )
        return "No image"
    image_thumbnail.short_description = "Preview"


# User Images Admin
@admin.register(UserImage)
class UserImageAdmin(admin.ModelAdmin, ImageDisplayMixin):
    list_display = ['image_thumbnail', 'original_filename', 'user_link', 'image_type', 'dimensions', 'file_size_kb', 'job_count', 'uploaded_at']
    list_filter = ['uploaded_at', 'image_type', 'width', 'height']
    search_fields = ['original_filename', 'user__username', 'user__email', 'venue_name']
    readonly_fields = ['image_thumbnail', 'full_image_link', 'file_size', 'width', 'height', 'processing_summary']
    ordering = ['-uploaded_at']
    list_per_page = 25
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Image Information', {
            'fields': ['image_thumbnail', 'full_image_link', 'original_filename', 'user', 'image_type']
        }),
        ('Details', {
            'fields': ['venue_name', 'venue_description'],
            'classes': ['collapse']
        }),
        ('Technical Details', {
            'fields': ['file_size', 'width', 'height'],
            'classes': ['collapse']
        }),
        ('Processing Summary', {
            'fields': ['processing_summary'],
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').annotate(
            jobs_count=Count('processing_jobs')
        ).prefetch_related('processing_jobs__processed_images')
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"
    
    def dimensions(self, obj):
        return f"{obj.width} × {obj.height}px"
    dimensions.short_description = "Size"
    
    def file_size_kb(self, obj):
        return f"{obj.file_size / 1024:.1f} KB"
    file_size_kb.short_description = "File Size"
    
    def job_count(self, obj):
        return obj.jobs_count if hasattr(obj, 'jobs_count') else obj.processing_jobs.count()
    job_count.short_description = "Jobs"
    job_count.admin_order_field = 'jobs_count'
    
    def full_image_link(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank" style="color: #0066cc;">View Full Image →</a>',
                obj.image.url
            )
        return "No image"
    full_image_link.short_description = "Full Size Image"
    
    def processing_summary(self, obj):
        """Show processing job summary for this image"""
        jobs = obj.processing_jobs.all()
        if not jobs:
            return "No processing jobs"
        
        html = '<div style="max-height: 300px; overflow-y: auto;">'
        for job in jobs:
            status_color = {
                'completed': '#28a745',
                'failed': '#dc3545', 
                'processing': '#ffc107',
                'pending': '#6c757d'
            }.get(job.status, '#6c757d')
            
            # Get description based on mode
            if job.custom_prompt:
                description = f"Custom: {job.custom_prompt[:50]}..."
            elif job.studio_mode == 'venue':
                theme = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme)
                space = dict(SPACE_TYPES).get(job.space_type, job.space_type) if job.space_type else 'N/A'
                description = f"Venue: {theme} - {space}"
            elif job.studio_mode == 'portrait_engagement':
                activity = dict(ENGAGEMENT_ACTIVITIES).get(job.engagement_activity, job.engagement_activity) if job.engagement_activity else 'N/A'
                description = f"Engagement: {activity}"
            else:  # portrait_wedding
                moment = dict(WEDDING_MOMENTS).get(job.wedding_moment, job.wedding_moment) if job.wedding_moment else 'N/A'
                description = f"Wedding: {moment}"
            
            processed_count = job.processed_images.count()
            
            html += format_html(
                '<div style="margin-bottom: 10px; padding: 8px; border: 1px solid #ddd; border-left: 4px solid {};">'
                '<strong>Job #{}</strong> <span style="color: {};">[{}]</span><br>'
                '<small>{}<br>'
                'Created: {}<br>'
                'Output: {}</small>'
                '</div>',
                status_color, job.id, status_color, job.status.title(),
                description,
                job.created_at.strftime('%Y-%m-%d %H:%M'),
                'Generated' if processed_count > 0 else 'None'
            )
        html += '</div>'
        return mark_safe(html)
    processing_summary.short_description = "Processing Jobs"


# Processing Jobs Admin  
@admin.register(ImageProcessingJob)
class ImageProcessingJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'studio_mode', 'mode_details', 'status_badge', 'has_output', 'created_at']
    list_filter = ['status', 'studio_mode', 'created_at']
    search_fields = ['user_image__user__username', 'user_image__user__email', 'custom_prompt']
    readonly_fields = ['prompt_details', 'processing_timeline', 'generated_images_summary', 'full_prompt_display']
    ordering = ['-created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Job Information', {
            'fields': ['user_image', 'studio_mode', 'status', 'processing_timeline']
        }),
        ('Prompt Configuration', {
            'fields': ['prompt_details', 'full_prompt_display']
        }),
        ('Results', {
            'fields': ['generated_images_summary'],
        }),
        ('Error Information', {
            'fields': ['error_message'],
            'classes': ['collapse']
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user_image__user'
        ).annotate(
            processed_images_count=Count('processed_images')
        ).prefetch_related('processed_images', 'reference_images')
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user_image.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user_image.user.username)
    user_link.short_description = "User"
    
    def mode_details(self, obj):
        """Show mode-specific details"""
        if obj.custom_prompt:
            return format_html('<span title="Custom prompt">Custom 📝</span>')
        
        if obj.studio_mode == 'venue':
            theme = dict(WEDDING_THEMES).get(obj.wedding_theme, obj.wedding_theme or 'N/A')
            return format_html('<span title="{}">Venue</span>', theme)
        elif obj.studio_mode == 'portrait_engagement':
            activity = dict(ENGAGEMENT_ACTIVITIES).get(obj.engagement_activity, obj.engagement_activity or 'N/A')
            return format_html('<span title="{}">Activity</span>', activity)
        else:  # portrait_wedding
            moment = dict(WEDDING_MOMENTS).get(obj.wedding_moment, obj.wedding_moment or 'N/A')
            return format_html('<span title="{}">Moment</span>', moment)
    
    mode_details.short_description = "Details"
    
    def status_badge(self, obj):
        colors = {
            'completed': '#28a745',
            'failed': '#dc3545',
            'processing': '#ffc107',
            'pending': '#6c757d'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.status.upper()
        )
    status_badge.short_description = "Status"
    
    def has_output(self, obj):
        count = obj.processed_images_count if hasattr(obj, 'processed_images_count') else obj.processed_images.count()
        if count > 0:
            return format_html('✅ {} image(s)', count)
        return '❌ None'
    has_output.short_description = "Output"
    has_output.admin_order_field = 'processed_images_count'
    
    def prompt_details(self, obj):
        """Show prompt configuration details"""
        html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 4px;">'
        
        if obj.custom_prompt:
            html += '<div style="margin-bottom: 10px;"><strong>Custom Prompt:</strong></div>'
            html += f'<div style="background: white; padding: 10px; border-radius: 4px; font-family: monospace;">{obj.custom_prompt}</div>'
        else:
            if obj.studio_mode == 'venue':
                html += '<div style="margin-bottom: 10px;"><strong>Venue Mode:</strong></div>'
                html += f'<div><strong>Theme:</strong> {dict(WEDDING_THEMES).get(obj.wedding_theme, obj.wedding_theme or "N/A")}</div>'
                if obj.space_type:
                    html += f'<div><strong>Space:</strong> {dict(SPACE_TYPES).get(obj.space_type, obj.space_type)}</div>'
            
            elif obj.studio_mode == 'portrait_engagement':
                html += '<div style="margin-bottom: 10px;"><strong>Engagement Portrait Mode:</strong></div>'
                if obj.engagement_activity:
                    html += f'<div><strong>Activity:</strong> {dict(ENGAGEMENT_ACTIVITIES).get(obj.engagement_activity, obj.engagement_activity)}</div>'
                if obj.engagement_setting:
                    html += f'<div><strong>Setting:</strong> {dict(ENGAGEMENT_SETTINGS).get(obj.engagement_setting, obj.engagement_setting)}</div>'
                if obj.attire_style:
                    html += f'<div><strong>Attire:</strong> {dict(ATTIRE_STYLES).get(obj.attire_style, obj.attire_style)}</div>'
            
            else:  # portrait_wedding
                html += '<div style="margin-bottom: 10px;"><strong>Wedding Portrait Mode:</strong></div>'
                if obj.wedding_moment:
                    html += f'<div><strong>Moment:</strong> {dict(WEDDING_MOMENTS).get(obj.wedding_moment, obj.wedding_moment)}</div>'
                if obj.wedding_setting:
                    html += f'<div><strong>Setting:</strong> {dict(WEDDING_SETTINGS).get(obj.wedding_setting, obj.wedding_setting)}</div>'
                if obj.attire_style:
                    html += f'<div><strong>Attire:</strong> {dict(ATTIRE_STYLES).get(obj.attire_style, obj.attire_style)}</div>'
            
            # Shared fields
            html += '<div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #dee2e6;">'
            html += '<strong>Additional Options:</strong>'
            
            if obj.composition:
                html += f'<div><strong>Composition:</strong> {dict(COMPOSITION_CHOICES).get(obj.composition, obj.composition)}</div>'
            if obj.emotional_tone:
                html += f'<div><strong>Emotional Tone:</strong> {dict(EMOTIONAL_TONE_CHOICES).get(obj.emotional_tone, obj.emotional_tone)}</div>'
            if obj.season:
                html += f'<div><strong>Season:</strong> {obj.season.title()}</div>'
            if obj.lighting_mood:
                html += f'<div><strong>Lighting:</strong> {obj.lighting_mood.replace("_", " ").title()}</div>'
            if obj.color_scheme:
                html += f'<div><strong>Color Scheme:</strong> {dict(COLOR_SCHEMES).get(obj.color_scheme, obj.color_scheme)}</div>'
            html += '</div>'
        
        if obj.user_instructions:
            html += '<div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #dee2e6;">'
            html += '<div><strong>User Instructions:</strong></div>'
            html += f'<div style="background: white; padding: 10px; border-radius: 4px; margin-top: 5px;">{obj.user_instructions}</div>'
            html += '</div>'
        
        html += '</div>'
        
        return mark_safe(html)
    prompt_details.short_description = "Prompt Configuration"
    
    def full_prompt_display(self, obj):
        """Show the full generated prompt"""
        if obj.generated_prompt:
            return format_html(
                '<div style="background: #e9ecef; padding: 10px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; max-height: 300px; overflow-y: auto;">{}</div>',
                obj.generated_prompt
            )
        return "No generated prompt"
    full_prompt_display.short_description = "Generated Prompt"
    
    def processing_timeline(self, obj):
        """Show processing timeline"""
        html = f'<div><strong>Created:</strong> {obj.created_at.strftime("%Y-%m-%d %H:%M:%S")}</div>'
        if obj.started_at:
            html += f'<div><strong>Started:</strong> {obj.started_at.strftime("%Y-%m-%d %H:%M:%S")}</div>'
        if obj.completed_at:
            html += f'<div><strong>Completed:</strong> {obj.completed_at.strftime("%Y-%m-%d %H:%M:%S")}</div>'
            if obj.started_at:
                duration = obj.completed_at - obj.started_at
                html += f'<div><strong>Duration:</strong> {duration.total_seconds():.1f} seconds</div>'
        return mark_safe(html)
    processing_timeline.short_description = "Timeline"
    
    def generated_images_summary(self, obj):
        """Show generated images"""
        processed_images = obj.processed_images.all()
        if not processed_images:
            return "No output generated"
        
        html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
        for img in processed_images:
            html += format_html(
                '<div style="text-align: center;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 4px; border: 1px solid #ddd;" />'
                '</a><br>'
                '<small>{} × {}px</small>'
                '</div>',
                img.processed_image.url,
                img.processed_image.url,
                img.width, img.height
            )
        html += '</div>'
        return mark_safe(html)
    generated_images_summary.short_description = "Generated Output"


# Processed Images Admin
@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin, ImageDisplayMixin):
    list_display = ['image_thumbnail', 'job_mode', 'user_link', 'dimensions', 'file_size_kb', 'gemini_model', 'created_at']
    list_filter = ['created_at', 'gemini_model', 'processing_job__status', 'processing_job__studio_mode']
    search_fields = ['processing_job__user_image__user__username']
    readonly_fields = ['image_thumbnail', 'full_image_link', 'job_details', 'original_image_link']
    ordering = ['-created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'processing_job__user_image__user'
        )
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.processing_job.user_image.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.processing_job.user_image.user.username)
    user_link.short_description = "User"
    
    def job_mode(self, obj):
        return obj.processing_job.get_studio_mode_display()
    job_mode.short_description = "Mode"
    
    def image_thumbnail(self, obj):
        if obj.processed_image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 4px;" />'
                '</a>',
                obj.processed_image.url,
                obj.processed_image.url
            )
        return "No image"
    image_thumbnail.short_description = "Preview"
    
    def dimensions(self, obj):
        return f"{obj.width} × {obj.height}px"
    dimensions.short_description = "Size"
    
    def file_size_kb(self, obj):
        return f"{obj.file_size / 1024:.1f} KB"
    file_size_kb.short_description = "File Size"
    
    def full_image_link(self, obj):
        if obj.processed_image:
            return format_html(
                '<a href="{}" target="_blank" style="color: #0066cc; font-weight: bold;">View Full Image →</a>',
                obj.processed_image.url
            )
        return "No image"
    full_image_link.short_description = "Full Size"
    
    def original_image_link(self, obj):
        if obj.processing_job.user_image.image:
            return format_html(
                '<a href="{}" target="_blank" style="color: #28a745;">View Original →</a>',
                obj.processing_job.user_image.image.url
            )
        return "No original"
    original_image_link.short_description = "Original"
    
    def job_details(self, obj):
        """Show job details"""
        job = obj.processing_job
        html = f'<div><strong>Job ID:</strong> #{job.id}</div>'
        html += f'<div><strong>Mode:</strong> {job.get_studio_mode_display()}</div>'
        html += f'<div><strong>Status:</strong> {job.status.title()}</div>'
        return mark_safe(html)
    job_details.short_description = "Job Info"


# Favorite Uploads Admin (star icon)
@admin.register(FavoriteUpload)
class FavoriteUploadAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'image_preview', 'image_filename', 'label', 'times_used', 'last_used', 'created_at']
    list_filter = ['created_at', 'last_used']
    search_fields = ['user__username', 'image__original_filename', 'label']
    readonly_fields = ['times_used', 'last_used', 'created_at']
    ordering = ['-last_used', '-created_at']
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"
    
    def image_preview(self, obj):
        if obj.image.thumbnail:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px;" />',
                obj.image.thumbnail.url
            )
        elif obj.image.image:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px;" />',
                obj.image.image.url
            )
        return "No preview"
    image_preview.short_description = "Preview"
    
    def image_filename(self, obj):
        return obj.image.original_filename
    image_filename.short_description = "Filename"


# Favorites Admin (heart icon for processed images)
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'image_preview', 'job_mode', 'created_at']
    list_filter = ['created_at', 'processed_image__processing_job__studio_mode']
    search_fields = ['user__username']
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"
    
    def image_preview(self, obj):
        if obj.processed_image.processed_image:
            return format_html(
                '<img src="{}" style="max-width: 50px; max-height: 50px;" />',
                obj.processed_image.processed_image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    def job_mode(self, obj):
        return obj.processed_image.processing_job.get_studio_mode_display()
    job_mode.short_description = "Mode"


# Collections Admin
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_link', 'item_count', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'user__username', 'description']
    readonly_fields = ['item_count']
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"


# Admin site customization
admin.site.site_header = "Wedding Studio AI - Admin"
admin.site.site_title = "Wedding Studio Admin" 
admin.site.index_title = "Content Management & Analytics"