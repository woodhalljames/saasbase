# image_processing/admin.py - Updated for streamlined models
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserImage, ImageProcessingJob, ProcessedImage, Collection, CollectionItem, Favorite, 
    WEDDING_THEMES, SPACE_TYPES, COLOR_SCHEMES, STYLE_INTENSITY, LIGHTING_MOODS
)


@admin.register(UserImage)
class UserImageAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'venue_info', 'image_preview', 'dimensions', 'file_size_display', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('original_filename', 'venue_name', 'user__username', 'user__email')
    readonly_fields = ('user', 'original_filename', 'file_size', 'width', 'height', 'uploaded_at', 'image_preview')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'original_filename', 'image', 'image_preview')
        }),
        ('Venue Details', {
            'fields': ('venue_name', 'venue_description'),
        }),
        ('Image Info', {
            'fields': ('file_size', 'width', 'height', 'uploaded_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;">', obj.thumbnail.url)
        elif obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;">', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"
    
    def venue_info(self, obj):
        if obj.venue_name:
            return f"{obj.venue_name}"
        return "No venue name"
    venue_info.short_description = "Venue"
    
    def dimensions(self, obj):
        return f"{obj.width}x{obj.height}"
    dimensions.short_description = "Dimensions"
    
    def file_size_display(self, obj):
        return f"{obj.file_size / 1024 / 1024:.1f} MB" if obj.file_size > 1024*1024 else f"{obj.file_size / 1024:.1f} KB"
    file_size_display.short_description = "File Size"


class ProcessedImageInline(admin.TabularInline):
    model = ProcessedImage
    extra = 0
    readonly_fields = ('processed_image_preview', 'file_size', 'width', 'height', 'stability_seed', 'created_at')
    fields = ('processed_image_preview', 'file_size', 'width', 'height', 'stability_seed', 'created_at')
    
    def processed_image_preview(self, obj):
        if obj.processed_image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;">', obj.processed_image.url)
        return "No image"
    processed_image_preview.short_description = "Preview"
    
    def has_add_permission(self, request, obj):
        return False


@admin.register(ImageProcessingJob)
class ImageProcessingJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_image_name', 'user', 'status', 'wedding_style', 'transformation_settings', 'created_at', 'completed_at')
    list_filter = ('status', 'wedding_theme', 'space_type', 'color_scheme', 'style_intensity', 'lighting_mood', 'strength', 'created_at')
    search_fields = ('user_image__original_filename', 'user_image__user__username', 'user_image__venue_name')
    readonly_fields = ('user_image', 'created_at', 'started_at', 'completed_at', 'generated_prompt', 'negative_prompt')
    inlines = [ProcessedImageInline]
    
    def user_image_name(self, obj):
        venue_name = obj.user_image.venue_name
        if venue_name:
            return f"{obj.user_image.original_filename} ({venue_name})"
        return obj.user_image.original_filename
    user_image_name.short_description = "Image"
    
    def user(self, obj):
        return obj.user_image.user.username
    user.short_description = "User"
    
    def wedding_style(self, obj):
        if obj.wedding_theme and obj.space_type:
            theme_display = dict(WEDDING_THEMES).get(obj.wedding_theme, obj.wedding_theme)
            space_display = dict(SPACE_TYPES).get(obj.space_type, obj.space_type)
            return f"{theme_display} - {space_display}"
        return "Not set"
    wedding_style.short_description = "Wedding Style"
    
    def transformation_settings(self, obj):
        settings = [f"Strength: {obj.strength:.0%}"]
        
        if obj.style_intensity:
            intensity_display = dict(STYLE_INTENSITY).get(obj.style_intensity, obj.style_intensity)
            settings.append(f"Intensity: {intensity_display}")
        
        if obj.color_scheme:
            color_display = dict(COLOR_SCHEMES).get(obj.color_scheme, obj.color_scheme)
            settings.append(f"Colors: {color_display}")
            
        if obj.lighting_mood:
            lighting_display = dict(LIGHTING_MOODS).get(obj.lighting_mood, obj.lighting_mood)
            settings.append(f"Lighting: {lighting_display}")
        
        return " | ".join(settings)
    transformation_settings.short_description = "Settings"
    
    fieldsets = (
        (None, {
            'fields': ('user_image', 'status', 'error_message')
        }),
        ('Wedding Configuration', {
            'fields': ('wedding_theme', 'space_type'),
        }),
        ('Style Customization', {
            'fields': ('season', 'time_of_day', 'color_scheme', 'style_intensity', 'lighting_mood'),
            'classes': ('collapse',)
        }),
        ('Additional Details', {
            'fields': ('special_features', 'avoid'),
            'classes': ('collapse',)
        }),
        ('AI Generation Parameters', {
            'fields': ('strength', 'cfg_scale', 'steps', 'seed', 'output_format'),
            'classes': ('collapse',)
        }),
        ('Generated Prompts', {
            'fields': ('generated_prompt', 'negative_prompt'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin):
    list_display = ('processing_job_id', 'wedding_style', 'transformation_info', 'image_preview', 'dimensions', 'file_size_display', 'created_at')
    list_filter = ('processing_job__wedding_theme', 'processing_job__space_type', 'processing_job__strength', 'created_at')
    search_fields = ('processing_job__user_image__original_filename', 'processing_job__user_image__user__username', 'processing_job__user_image__venue_name')
    readonly_fields = ('processing_job', 'file_size', 'width', 'height', 'stability_seed', 'finish_reason', 'created_at', 'image_preview')
    
    def processing_job_id(self, obj):
        return f"Job #{obj.processing_job.id}"
    processing_job_id.short_description = "Job"
    
    def image_preview(self, obj):
        if obj.processed_image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;">', obj.processed_image.url)
        return "No image"
    image_preview.short_description = "Preview"
    
    def dimensions(self, obj):
        return f"{obj.width}x{obj.height}"
    dimensions.short_description = "Dimensions"
    
    def file_size_display(self, obj):
        return f"{obj.file_size / 1024 / 1024:.1f} MB" if obj.file_size > 1024*1024 else f"{obj.file_size / 1024:.1f} KB"
    file_size_display.short_description = "File Size"
    
    def wedding_style(self, obj):
        job = obj.processing_job
        if job.wedding_theme and job.space_type:
            theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme)
            space_display = dict(SPACE_TYPES).get(job.space_type, job.space_type)
            return f"{theme_display} - {space_display}"
        return "Not set"
    wedding_style.short_description = "Wedding Style"
    
    def transformation_info(self, obj):
        job = obj.processing_job
        info = [f"Strength: {job.strength:.0%}", f"CFG: {job.cfg_scale}", f"Steps: {job.steps}"]
        
        if job.style_intensity:
            intensity_display = dict(STYLE_INTENSITY).get(job.style_intensity, job.style_intensity)
            info.append(f"Intensity: {intensity_display}")
        
        return " | ".join(info)
    transformation_info.short_description = "AI Settings"


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'item_count', 'is_public', 'is_default', 'updated_at')
    list_filter = ('is_public', 'is_default', 'created_at')
    search_fields = ('name', 'user__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Items"


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ('collection', 'image_title', 'item_type', 'added_at')
    list_filter = ('added_at', 'collection__user')
    search_fields = ('collection__name', 'notes')
    readonly_fields = ('added_at',)
    
    def image_title(self, obj):
        return obj.image_title
    image_title.short_description = "Image"
    
    def item_type(self, obj):
        if obj.processed_image:
            return "Wedding Transformation"
        else:
            return "Original Image"
    item_type.short_description = "Type"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'image_title', 'transformation_details', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    
    def image_title(self, obj):
        job = obj.processed_image.processing_job
        theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, 'Unknown') if job.wedding_theme else 'Unknown'
        space_display = dict(SPACE_TYPES).get(job.space_type, 'Unknown') if job.space_type else 'Unknown'
        return f"Wedding: {theme_display} {space_display}"
    image_title.short_description = "Image"
    
    def transformation_details(self, obj):
        job = obj.processed_image.processing_job
        details = [f"Strength: {job.strength:.0%}"]
        
        if job.color_scheme:
            color_display = dict(COLOR_SCHEMES).get(job.color_scheme, job.color_scheme)
            details.append(f"Colors: {color_display}")
            
        return " | ".join(details)
    transformation_details.short_description = "Transformation Info"


# Enhanced admin actions for bulk operations
@admin.action(description='Mark selected jobs as processing')
def mark_as_processing(modeladmin, request, queryset):
    updated = queryset.update(status='processing')
    modeladmin.message_user(request, f"Marked {updated} jobs as processing.")


@admin.action(description='Mark selected jobs as failed')
def mark_as_failed(modeladmin, request, queryset):
    updated = queryset.update(status='failed')
    modeladmin.message_user(request, f"Marked {updated} jobs as failed.")


@admin.action(description='Reset selected jobs to pending')
def reset_to_pending(modeladmin, request, queryset):
    updated = queryset.update(status='pending', started_at=None, completed_at=None, error_message=None)
    modeladmin.message_user(request, f"Reset {updated} jobs to pending.")


@admin.action(description='Update to high strength (85%) for major transformations')
def update_to_high_strength(modeladmin, request, queryset):
    updated = queryset.update(strength=0.85)
    modeladmin.message_user(request, f"Updated {updated} jobs to 85% strength for major transformations.")


@admin.action(description='Optimize parameters for current AI model')
def optimize_parameters(modeladmin, request, queryset):
    updated = queryset.update(cfg_scale=7.5, steps=40)
    modeladmin.message_user(request, f"Optimized parameters for {updated} jobs.")


@admin.action(description='Clear generated prompts (will regenerate on processing)')
def clear_prompts(modeladmin, request, queryset):
    updated = queryset.update(generated_prompt='', negative_prompt='')
    modeladmin.message_user(request, f"Cleared prompts for {updated} jobs - they will regenerate on processing.")


# Add the actions to the ImageProcessingJobAdmin
ImageProcessingJobAdmin.actions = [
    mark_as_processing, 
    mark_as_failed, 
    reset_to_pending,
    update_to_high_strength,
    optimize_parameters,
    clear_prompts
]


# Custom admin site configuration
admin.site.site_header = "Wedding Venue Transformation Admin"
admin.site.site_title = "Wedding Admin"
admin.site.index_title = "Wedding Venue Transformation Administration"


# Statistics and monitoring in admin
class ProcessingStatsAdmin(admin.ModelAdmin):
    """Custom admin view for processing statistics"""
    
    def changelist_view(self, request, extra_context=None):
        from django.db.models import Count, Q
        from datetime import timedelta
        from django.utils import timezone
        
        # Calculate statistics
        total_jobs = ImageProcessingJob.objects.count()
        completed_jobs = ImageProcessingJob.objects.filter(status='completed').count()
        failed_jobs = ImageProcessingJob.objects.filter(status='failed').count()
        
        # Recent statistics (last 24 hours)
        recent_cutoff = timezone.now() - timedelta(hours=24)
        recent_jobs = ImageProcessingJob.objects.filter(created_at__gte=recent_cutoff).count()
        
        # Popular themes and spaces
        popular_themes = ImageProcessingJob.objects.values('wedding_theme').annotate(
            count=Count('wedding_theme')
        ).order_by('-count')[:10]
        
        popular_spaces = ImageProcessingJob.objects.values('space_type').annotate(
            count=Count('space_type')
        ).order_by('-count')[:10]
        
        # User statistics
        active_users = ImageProcessingJob.objects.filter(
            created_at__gte=recent_cutoff
        ).values('user_image__user').distinct().count()
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'failed_jobs': failed_jobs,
            'success_rate': round((completed_jobs / total_jobs * 100) if total_jobs > 0 else 0, 1),
            'recent_jobs': recent_jobs,
            'active_users': active_users,
            'popular_themes': popular_themes,
            'popular_spaces': popular_spaces,
        })
        
        return super().changelist_view(request, extra_context=extra_context)


# Custom admin dashboard widgets (if you want to display stats)
def admin_dashboard_stats():
    """Helper function to get dashboard statistics"""
    from django.db.models import Count, Q
    from datetime import timedelta
    from django.utils import timezone
    
    recent_cutoff = timezone.now() - timedelta(hours=24)
    
    stats = {
        'total_images': UserImage.objects.count(),
        'total_jobs': ImageProcessingJob.objects.count(),
        'recent_jobs': ImageProcessingJob.objects.filter(created_at__gte=recent_cutoff).count(),
        'processing_jobs': ImageProcessingJob.objects.filter(status='processing').count(),
        'failed_jobs': ImageProcessingJob.objects.filter(status='failed').count(),
        'total_collections': Collection.objects.count(),
        'total_favorites': Favorite.objects.count(),
    }
    
    return stats


