# image_processing/models.py
import os
import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse
from PIL import Image


def user_image_upload_path(instance, filename):
    """Generate upload path for user images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"user_images/{instance.user.id}/{filename}"


def processed_image_upload_path(instance, filename):
    """Generate upload path for processed images"""
    ext = filename.split('.')[-1]
    filename = f"processed_{uuid.uuid4().hex}.{ext}"
    return f"processed_images/{instance.user_image.user.id}/{filename}"


class PromptTemplate(models.Model):
    """Predefined prompts/themes for image processing"""
    CATEGORY_CHOICES = [
        ('art', 'Artistic'),
        ('photo', 'Photography'),
        ('fantasy', 'Fantasy'),
        ('nature', 'Nature'),
        ('portrait', 'Portrait'),
        ('abstract', 'Abstract'),
        ('vintage', 'Vintage'),
        ('modern', 'Modern'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(help_text="Description of what this prompt does")
    prompt_text = models.TextField(help_text="The actual prompt to send to Stability AI")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class UserImage(models.Model):
    """User uploaded images"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images')
    original_filename = models.CharField(max_length=255)
    image = models.ImageField(upload_to=user_image_upload_path)
    thumbnail = models.ImageField(upload_to=user_image_upload_path, blank=True, null=True)
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.original_filename}"
    
    def save(self, *args, **kwargs):
        # Set image dimensions and file size
        if self.image:
            img = Image.open(self.image)
            self.width, self.height = img.size
            self.file_size = self.image.size
            
        super().save(*args, **kwargs)
        
        # Create thumbnail after saving
        if self.image and not self.thumbnail:
            self.create_thumbnail()
    
    def create_thumbnail(self):
        """Create a thumbnail for the image"""
        if not self.image:
            return
            
        img = Image.open(self.image.path)
        img.thumbnail((300, 300), Image.Resampling.LANCZOS)
        
        # Save thumbnail
        thumb_path = self.image.path.replace('.', '_thumb.')
        img.save(thumb_path)
        
        # Update thumbnail field
        rel_path = os.path.relpath(thumb_path, settings.MEDIA_ROOT)
        self.thumbnail.name = rel_path
        self.save(update_fields=['thumbnail'])
    
    def get_absolute_url(self):
        return reverse('image_processing:image_detail', kwargs={'pk': self.pk})


class ImageProcessingJob(models.Model):
    """Track image processing jobs with Stability AI"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, related_name='processing_jobs')
    prompts = models.ManyToManyField(PromptTemplate, related_name='processing_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Stability AI parameters
    cfg_scale = models.FloatField(default=7.0, help_text="How strictly the diffusion process adheres to the prompt text")
    steps = models.IntegerField(default=50, help_text="Number of diffusion steps to run")
    seed = models.BigIntegerField(blank=True, null=True, help_text="Random noise seed for generation")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Job {self.id} - {self.user_image.original_filename} ({self.status})"
    
    @property
    def prompt_count(self):
        return self.prompts.count()


class ProcessedImage(models.Model):
    """Store processed images from Stability AI"""
    processing_job = models.ForeignKey(ImageProcessingJob, on_delete=models.CASCADE, related_name='processed_images')
    prompt_template = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE)
    processed_image = models.ImageField(upload_to=processed_image_upload_path)
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    
    # Metadata from Stability AI
    stability_seed = models.BigIntegerField(blank=True, null=True)
    finish_reason = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Set image dimensions and file size
        if self.processed_image:
            img = Image.open(self.processed_image)
            self.width, self.height = img.size
            self.file_size = self.processed_image.size
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Processed: {self.prompt_template.name} - Job {self.processing_job.id}"


class Collection(models.Model):
    """User collections/albums for organizing images"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False, help_text="Allow public viewing of this collection")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user', 'name']  # Unique collection names per user
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    @property
    def item_count(self):
        return self.items.count()
    
    @property
    def thumbnail(self):
        """Get the first image as thumbnail"""
        first_item = self.items.first()
        if first_item:
            if first_item.processed_image:
                return first_item.processed_image.processed_image
            else:
                return first_item.user_image.thumbnail or first_item.user_image.image
        return None


class CollectionItem(models.Model):
    """Items within a collection (can be original or processed images)"""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='items')
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, null=True, blank=True)
    processed_image = models.ForeignKey('ProcessedImage', on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True, null=True, help_text="Personal notes about this image")
    order = models.PositiveIntegerField(default=0, help_text="Order within collection")
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-added_at']
        unique_together = [
            ['collection', 'user_image'],
            ['collection', 'processed_image']
        ]  # Prevent duplicates
    
    def __str__(self):
        if self.processed_image:
            return f"{self.collection.name} - {self.processed_image.prompt_template.name}"
        else:
            return f"{self.collection.name} - {self.user_image.original_filename}"
    
    @property
    def image_url(self):
        """Get the image URL regardless of type"""
        if self.processed_image:
            return self.processed_image.processed_image.url
        else:
            return self.user_image.thumbnail.url if self.user_image.thumbnail else self.user_image.image.url
    
    @property
    def image_title(self):
        """Get a display title for the image"""
        if self.processed_image:
            return f"{self.processed_image.prompt_template.name}"
        else:
            return self.user_image.original_filename


class ImageRating(models.Model):
    """Simple thumbs up/down rating system"""
    RATING_CHOICES = [
        ('up', 'Thumbs Up'),
        ('down', 'Thumbs Down'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    processed_image = models.ForeignKey('ProcessedImage', on_delete=models.CASCADE, related_name='ratings')
    rating = models.CharField(max_length=10, choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'processed_image']  # One rating per user per image
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.rating} - {self.processed_image.prompt_template.name}"


class RatingTag(models.Model):
    """Tags for thumbs down ratings to understand why users didn't like it"""
    TAG_CHOICES = [
        ('too_dark', 'Too Dark'),
        ('too_bright', 'Too Bright'),
        ('wrong_style', 'Wrong Style'),
        ('poor_quality', 'Poor Quality'),
        ('unrealistic', 'Unrealistic'),
        ('missing_details', 'Missing Details'),
        ('color_issues', 'Color Issues'),
        ('composition', 'Poor Composition'),
        ('artifacts', 'Visual Artifacts'),
        ('other', 'Other'),
    ]
    
    rating = models.ForeignKey(ImageRating, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=20, choices=TAG_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['rating', 'tag']  # Prevent duplicate tags per rating
    
    def __str__(self):
        return f"{self.rating.processed_image.prompt_template.name} - {self.get_tag_display()}"


class Favorite(models.Model):
    """User favorites for quick access"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, null=True, blank=True)
    processed_image = models.ForeignKey('ProcessedImage', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ['user', 'user_image'],
            ['user', 'processed_image']
        ]  # Prevent duplicate favorites
        ordering = ['-created_at']
    
    def __str__(self):
        if self.processed_image:
            return f"{self.user.username} ❤️ {self.processed_image.prompt_template.name}"
        else:
            return f"{self.user.username} ❤️ {self.user_image.original_filename}"
    
    @property
    def image_url(self):
        """Get the image URL regardless of type"""
        if self.processed_image:
            return self.processed_image.processed_image.url
        else:
            return self.user_image.thumbnail.url if self.user_image.thumbnail else self.user_image.image.url