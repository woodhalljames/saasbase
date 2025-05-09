# wedding_vision/models.py
from django.db import models
from django.conf import settings
import uuid
import os

def venue_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('venues', filename)

def generated_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('generated', filename)

class ThemeTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    prompt_template = models.TextField(help_text="Template for AI generation")
    example_image = models.ImageField(upload_to='theme_examples', blank=True, null=True)
    token_cost = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class VenueImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='venue_images')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=venue_image_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class GeneratedImage(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='generated_images')
    venue_image = models.ForeignKey(VenueImage, on_delete=models.CASCADE, related_name='generations')
    theme = models.ForeignKey(ThemeTemplate, on_delete=models.SET_NULL, null=True, related_name='generations')
    image = models.ImageField(upload_to=generated_image_path, blank=True, null=True)
    image_data = models.BinaryField(null=True)  # Store image temporarily
    prompt = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    tokens_used = models.PositiveIntegerField(default=0)
    seed = models.BigIntegerField(null=True)
    is_saved = models.BooleanField(default=False)
    is_wishlisted = models.BooleanField(default=False)
    is_upscaled = models.BooleanField(default=False)
    parent_image = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='variations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.venue_image.title} - {self.theme.name if self.theme else 'No theme'} - {self.status}"

class ImageFeedback(models.Model):
    FEEDBACK_CHOICES = (
        ('positive', 'Positive'),
        ('negative', 'Negative'),
    )
    
    generated_image = models.OneToOneField(GeneratedImage, on_delete=models.CASCADE, related_name='feedback')
    feedback_type = models.CharField(max_length=10, choices=FEEDBACK_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.feedback_type} - {self.generated_image}"
