from django.contrib import admin
from django.utils.html import format_html
from .models import PromptTemplate, UserImage, ImageProcessingJob, ProcessedImage


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'prompt_text')
    list_editable = ('is_active',)
    ordering = ('category', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'description', 'is_active')
        }),
        ('Prompt Configuration', {
            'fields': ('prompt_text',),
            'classes': ('wide',)
        }),
    )


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
    readonly_fields = ('prompt_template', 'processed_image', 'file_size', 'width', 'height', 'stability_seed', 'created_at')
    
    def has_add_permission(self, request, obj):
        return False


@admin.register(ImageProcessingJob)
class ImageProcessingJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_image_name', 'user', 'status', 'prompt_count', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user_image__original_filename', 'user_image__user__username')
    readonly_fields = ('user_image', 'created_at', 'started_at', 'completed_at')
    inlines = [ProcessedImageInline]
    
    def user_image_name(self, obj):
        return obj.user_image.original_filename
    user_image_name.short_description = "Image"
    
    def user(self, obj):
        return obj.user_image.user.username
    user.short_description = "User"
    
    fieldsets = (
        (None, {
            'fields': ('user_image', 'status', 'error_message')
        }),
        ('AI Parameters', {
            'fields': ('cfg_scale', 'steps', 'seed'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin):
    list_display = ('processing_job', 'prompt_template', 'image_preview', 'dimensions', 'file_size_display', 'created_at')
    list_filter = ('prompt_template__category', 'created_at')
    search_fields = ('processing_job__user_image__original_filename', 'prompt_template__name')
    readonly_fields = ('processing_job', 'prompt_template', 'file_size', 'width', 'height', 'stability_seed', 'finish_reason', 'created_at', 'image_preview')
    
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