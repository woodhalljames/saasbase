# image_processing/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import UserImage, ImageProcessingJob, ProcessedImage, Collection, CollectionItem, Favorite, WEDDING_THEMES, SPACE_TYPES


@admin.register(UserImage)
class UserImageAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'image_preview', 'dimensions', 'file_size_display', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('original_filename', 'user__username', 'user__email')
    readonly_fields = ('user', 'original_filename', 'file_size', 'width', 'height', 'uploaded_at', 'image_preview')
    
    def image_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;">', obj.thumbnail.url)
        elif obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;">', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"
    
    def dimensions(self, obj):
        return f"{obj.width}x{obj.height}"
    dimensions.short_description = "Dimensions"
    
    def file_size_display(self, obj):
        return f"{obj.file_size / 1024 / 1024:.1f} MB" if obj.file_size > 1024*1024 else f"{obj.file_size / 1024:.1f} KB"
    file_size_display.short_description = "File Size"


class ProcessedImageInline(admin.TabularInline):
    model = ProcessedImage
    extra = 0
    readonly_fields = ('processed_image_preview', 'file_size', 'width', 'height', 'stability_seed', 'created_at', 'is_saved')
    fields = ('processed_image_preview', 'is_saved', 'file_size', 'width', 'height', 'stability_seed', 'created_at')
    
    def processed_image_preview(self, obj):
        if obj.processed_image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;">', obj.processed_image.url)
        return "No image"
    processed_image_preview.short_description = "Preview"
    
    def has_add_permission(self, request, obj):
        return False


@admin.register(ImageProcessingJob)
class ImageProcessingJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_image_name', 'user', 'status', 'wedding_style', 'created_at', 'completed_at')
    list_filter = ('status', 'wedding_theme', 'space_type', 'created_at')
    search_fields = ('user_image__original_filename', 'user_image__user__username')
    readonly_fields = ('user_image', 'created_at', 'started_at', 'completed_at', 'generated_prompt')
    inlines = [ProcessedImageInline]
    
    def user_image_name(self, obj):
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
    
    fieldsets = (
        (None, {
            'fields': ('user_image', 'status', 'error_message')
        }),
        ('Wedding Configuration', {
            'fields': ('wedding_theme', 'space_type', 'additional_details'),
        }),
        ('AI Parameters', {
            'fields': ('strength', 'cfg_scale', 'steps', 'seed', 'aspect_ratio', 'output_format'),
            'classes': ('collapse',)
        }),
        ('Generated Prompt', {
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
    list_display = ('processing_job', 'wedding_style', 'image_preview', 'dimensions', 'file_size_display', 'is_saved', 'created_at')
    list_filter = ('is_saved', 'processing_job__wedding_theme', 'processing_job__space_type', 'created_at')
    search_fields = ('processing_job__user_image__original_filename', 'processing_job__user_image__user__username')
    readonly_fields = ('processing_job', 'file_size', 'width', 'height', 'stability_seed', 'finish_reason', 'created_at', 'saved_at', 'image_preview')
    
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


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'item_count', 'is_public', 'is_default', 'updated_at')
    list_filter = ('is_public', 'is_default', 'created_at')
    search_fields = ('name', 'user__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Items"


class CollectionItemInline(admin.TabularInline):
    model = CollectionItem
    extra = 0
    readonly_fields = ('added_at',)


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ('collection', 'image_title', 'added_at')
    list_filter = ('added_at', 'collection__user')
    search_fields = ('collection__name', 'notes')
    readonly_fields = ('added_at',)
    
    def image_title(self, obj):
        return obj.image_title
    image_title.short_description = "Image"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'image_title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    
    def image_title(self, obj):
        job = obj.processed_image.processing_job
        theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, 'Unknown') if job.wedding_theme else 'Unknown'
        space_display = dict(SPACE_TYPES).get(job.space_type, 'Unknown') if job.space_type else 'Unknown'
        return f"Wedding: {theme_display} {space_display}"
    image_title.short_description = "Image"