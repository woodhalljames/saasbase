# image_processing/admin.py - Enhanced admin for tracking images, prompts, and users

import os
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    UserImage, ImageProcessingJob, ProcessedImage, 
    Collection, CollectionItem, Favorite,
    WEDDING_THEMES, SPACE_TYPES, COLOR_SCHEMES
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
    

class PromptDisplayMixin:
    """Mixin for displaying prompt information"""
    
    def prompt_preview(self, obj):
        """Show prompt preview with full prompt in tooltip"""
        if hasattr(obj, 'custom_prompt') and obj.custom_prompt:
            preview = obj.custom_prompt[:100]
            if len(obj.custom_prompt) > 100:
                preview += "..."
            return format_html(
                '<div title="{}" style="max-width: 300px; cursor: help;">'
                '<strong>Custom:</strong> {}'
                '</div>',
                obj.custom_prompt,
                preview
            )
        elif hasattr(obj, 'generated_prompt') and obj.generated_prompt:
            preview = obj.generated_prompt[:100]
            if len(obj.generated_prompt) > 100:
                preview += "..."
            return format_html(
                '<div title="{}" style="max-width: 300px; cursor: help;">'
                '<strong>Generated:</strong> {}'
                '</div>',
                obj.generated_prompt,
                preview
            )
        return "No prompt"
    prompt_preview.short_description = "Prompt Preview"
    
    def prompt_type_display(self, obj):
        """Show whether custom or guided mode was used"""
        if hasattr(obj, 'custom_prompt') and obj.custom_prompt:
            return format_html('<span style="color: #0066cc;">Custom</span>')
        else:
            return format_html('<span style="color: #009900;">Guided</span>')
    prompt_type_display.short_description = "Mode"


# User admin is handled by users app - focus on image processing models only


# User Images Admin
@admin.register(UserImage)
class UserImageAdmin(admin.ModelAdmin, ImageDisplayMixin):
    list_display = ['image_thumbnail', 'original_filename', 'user_link', 'dimensions', 'file_size_kb', 'job_count', 'uploaded_at']
    list_filter = ['uploaded_at', 'width', 'height']
    search_fields = ['original_filename', 'user__username', 'user__email', 'venue_name']
    readonly_fields = ['image_thumbnail', 'full_image_link', 'file_size', 'width', 'height', 'processing_summary']
    ordering = ['-uploaded_at']
    list_per_page = 25
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Image Information', {
            'fields': ['image_thumbnail', 'full_image_link', 'original_filename', 'user']
        }),
        ('Venue Details', {
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
            
            # Get theme/space display
            if job.custom_prompt:
                description = f"Custom: {job.custom_prompt[:50]}..."
            else:
                theme = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme)
                space = dict(SPACE_TYPES).get(job.space_type, job.space_type)
                description = f"{theme} - {space}"
            
            processed_count = job.processed_images.count()
            
            html += format_html(
                '<div style="margin-bottom: 10px; padding: 8px; border: 1px solid #ddd; border-left: 4px solid {};">'
                '<strong>Job #{}</strong> <span style="color: {};">[{}]</span><br>'
                '<small>{}<br>'
                'Created: {}<br>'
                'Generated Images: {}</small>'
                '</div>',
                status_color, job.id, status_color, job.status.title(),
                description,
                job.created_at.strftime('%Y-%m-%d %H:%M'),
                processed_count
            )
        html += '</div>'
        return mark_safe(html)
    processing_summary.short_description = "Processing Jobs"


# Processing Jobs Admin  
@admin.register(ImageProcessingJob)
class ImageProcessingJobAdmin(admin.ModelAdmin, PromptDisplayMixin):
    list_display = ['id', 'user_link', 'prompt_type_display', 'theme_space_display', 'status_badge', 'processed_count', 'created_at']
    list_filter = ['status', 'wedding_theme', 'space_type', 'created_at']
    search_fields = ['user_image__user__username', 'user_image__user__email', 'custom_prompt', 'wedding_theme', 'space_type']
    readonly_fields = ['prompt_details', 'processing_timeline', 'generated_images_summary', 'full_prompt_display']
    ordering = ['-created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Job Information', {
            'fields': ['user_image', 'status', 'prompt_type_display', 'processing_timeline']
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
        ).prefetch_related('processed_images')
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user_image.user.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user_image.user.username
        )
    user_link.short_description = "User"
    
    def theme_space_display(self, obj):
        """Show theme and space type in a compact format"""
        if obj.custom_prompt:
            return format_html(
                '<span style="color: #0066cc; font-style: italic;">Custom Prompt</span>'
            )
        
        theme = dict(WEDDING_THEMES).get(obj.wedding_theme, obj.wedding_theme)
        space = dict(SPACE_TYPES).get(obj.space_type, obj.space_type)
        
        return format_html(
            '<div style="max-width: 200px;">'
            '<strong>{}</strong><br>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            theme, space
        )
    theme_space_display.short_description = "Theme & Space"
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'completed': '#28a745',
            'failed': '#dc3545',
            'processing': '#ffc107',
            'pending': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = "Status"
    
    def processed_count(self, obj):
        return obj.processed_images_count if hasattr(obj, 'processed_images_count') else obj.processed_images.count()
    processed_count.short_description = "Generated"
    processed_count.admin_order_field = 'processed_images_count'
    
    def prompt_details(self, obj):
        """Show detailed prompt information"""
        if obj.custom_prompt:
            html = f'<div style="margin-bottom: 15px;"><strong>Mode:</strong> Custom Prompt</div>'
            html += f'<div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 15px;"><strong>Custom Prompt:</strong><br>{obj.custom_prompt}</div>'
        else:
            html = f'<div style="margin-bottom: 15px;"><strong>Mode:</strong> Guided Design</div>'
            html += '<div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 15px;">'
            html += f'<strong>Wedding Theme:</strong> {dict(WEDDING_THEMES).get(obj.wedding_theme, obj.wedding_theme)}<br>'
            html += f'<strong>Space Type:</strong> {dict(SPACE_TYPES).get(obj.space_type, obj.space_type)}<br>'
            
            if obj.season:
                html += f'<strong>Season:</strong> {obj.season.title()}<br>'
            if obj.lighting_mood:
                html += f'<strong>Lighting:</strong> {obj.lighting_mood.title()}<br>'
            if obj.color_scheme:
                html += f'<strong>Color Scheme:</strong> {dict(COLOR_SCHEMES).get(obj.color_scheme, obj.color_scheme)}<br>'
            html += '</div>'
        
        if obj.user_instructions:
            html += f'<div style="background: #fff3cd; padding: 10px; border-radius: 4px; margin-bottom: 15px;"><strong>User Instructions:</strong><br>{obj.user_instructions}</div>'
        
        return mark_safe(html)
    prompt_details.short_description = "Prompt Configuration"
    
    def full_prompt_display(self, obj):
        """Show the full generated prompt sent to Gemini"""
        if obj.generated_prompt:
            return format_html(
                '<div style="background: #e9ecef; padding: 10px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; max-height: 300px; overflow-y: auto;">{}</div>',
                obj.generated_prompt
            )
        return "No generated prompt available"
    full_prompt_display.short_description = "Generated Prompt (Sent to Gemini)"
    
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
        """Show generated images with thumbnails"""
        processed_images = obj.processed_images.all()
        if not processed_images:
            return "No generated images"
        
        html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
        for img in processed_images:
            html += format_html(
                '<div style="text-align: center;">'
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 4px; border: 1px solid #ddd;" />'
                '</a><br>'
                '<small>{} × {}px</small>'
                '</div>',
                img.processed_image.url,
                img.processed_image.url,
                img.width, img.height
            )
        html += '</div>'
        return mark_safe(html)
    generated_images_summary.short_description = "Generated Images"


# Processed Images Admin
@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin, ImageDisplayMixin):
    list_display = ['image_thumbnail', 'transformation_title', 'user_link', 'dimensions', 'file_size_kb', 'gemini_model', 'created_at']
    list_filter = ['created_at', 'gemini_model', 'processing_job__status']
    search_fields = ['processing_job__user_image__user__username', 'processing_job__user_image__user__email']
    readonly_fields = ['image_thumbnail', 'full_image_link', 'job_details', 'original_image_link']
    ordering = ['-created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Generated Image', {
            'fields': ['image_thumbnail', 'full_image_link', 'original_image_link']
        }),
        ('Processing Information', {
            'fields': ['job_details', 'gemini_model', 'finish_reason']
        }),
        ('Technical Details', {
            'fields': ['width', 'height', 'file_size'],
            'classes': ['collapse']
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'processing_job__user_image__user'
        ).prefetch_related('processing_job')
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.processing_job.user_image.user.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.processing_job.user_image.user.username
        )
    user_link.short_description = "User"
    
    def image_thumbnail(self, obj):
        """Override to use processed_image field"""
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
                '<a href="{}" target="_blank" style="color: #0066cc; font-weight: bold;">View Full Generated Image →</a>',
                obj.processed_image.url
            )
        return "No image"
    full_image_link.short_description = "Full Size Image"
    
    def original_image_link(self, obj):
        if obj.processing_job.user_image.image:
            return format_html(
                '<a href="{}" target="_blank" style="color: #28a745;">View Original Image →</a>',
                obj.processing_job.user_image.image.url
            )
        return "No original"
    original_image_link.short_description = "Original Image"
    
    def job_details(self, obj):
        """Show details about the processing job"""
        job = obj.processing_job
        
        html = f'<div><strong>Job ID:</strong> #{job.id}</div>'
        html += f'<div><strong>Status:</strong> {job.status.title()}</div>'
        
        if job.custom_prompt:
            html += '<div><strong>Mode:</strong> Custom Prompt</div>'
            html += f'<div style="background: #f8f9fa; padding: 8px; margin: 8px 0; border-radius: 4px; max-height: 100px; overflow-y: auto;"><strong>Prompt:</strong><br>{job.custom_prompt}</div>'
        else:
            html += '<div><strong>Mode:</strong> Guided Design</div>'
            theme = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme)
            space = dict(SPACE_TYPES).get(job.space_type, job.space_type)
            html += f'<div><strong>Theme:</strong> {theme}</div>'
            html += f'<div><strong>Space:</strong> {space}</div>'
        
        if job.user_instructions:
            html += f'<div style="background: #fff3cd; padding: 8px; margin: 8px 0; border-radius: 4px;"><strong>User Instructions:</strong><br>{job.user_instructions}</div>'
        
        html += f'<div><strong>Original File:</strong> {job.user_image.original_filename}</div>'
        
        return mark_safe(html)
    job_details.short_description = "Processing Job Details"


# Collection Admin (for completeness)
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


# Register remaining models with basic admin
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user_link', 'image_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"
    
    def image_preview(self, obj):
        if obj.processed_image.processed_image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-width: 50px; max-height: 50px;" />'
                '</a>',
                obj.processed_image.processed_image.url,
                obj.processed_image.processed_image.url
            )
        return "No image"
    image_preview.short_description = "Image"


# Admin site customization
admin.site.site_header = "Wedding Venue AI - Admin"
admin.site.site_title = "Wedding Venue AI Admin" 
admin.site.index_title = "Content Management & Analytics"