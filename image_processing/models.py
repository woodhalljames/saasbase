# image_processing/models.py - Complete Wedding Implementation
import os
import uuid
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
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
    return f"processed_images/{instance.processing_job.user_image.user.id}/{filename}"


# Wedding Theme and Space Type Choices
WEDDING_THEMES = [
    ('rustic', 'Rustic Barn'),
    ('modern', 'Modern Elegant'),
    ('vintage', 'Vintage Romance'),
    ('bohemian', 'Bohemian Chic'),
    ('classic', 'Classic Traditional'),
    ('garden', 'Garden Party'),
    ('beach', 'Beach Paradise'),
    ('industrial', 'Industrial Chic'),
]

SPACE_TYPES = [
    ('indoor_ceremony', 'Indoor Ceremony'),
    ('outdoor_ceremony', 'Outdoor Ceremony'),
    ('reception_hall', 'Reception Hall'),
    ('garden', 'Garden/Outdoor'),
    ('beach', 'Beach'),
    ('barn', 'Barn'),
    ('ballroom', 'Ballroom'),
    ('rooftop', 'Rooftop'),
]


def generate_wedding_prompt(theme, space_type):
    """Generate AI prompt for wedding venue transformation"""
    theme_descriptions = {
        'rustic': 'rustic wooden decorations, burlap and lace details, mason jar centerpieces, warm string lights, wooden signs, vintage furniture',
        'modern': 'sleek contemporary decorations, minimalist floral arrangements, geometric shapes, clean lines, modern lighting, elegant simplicity',
        'vintage': 'antique decorations, vintage lace, old-fashioned flowers, retro furniture, classic chandeliers, nostalgic romantic details',
        'bohemian': 'colorful tapestries, macrame details, wildflower arrangements, eclectic furniture, dreamcatchers, free-spirited decorations',
        'classic': 'traditional white decorations, elegant floral arrangements, classic drapery, formal table settings, timeless romantic details',
        'garden': 'abundant flowers, natural greenery, botanical arrangements, outdoor garden elements, natural lighting, organic decorations',
        'beach': 'coastal decorations, seashells, driftwood, ocean-inspired colors, nautical elements, breezy natural lighting',
        'industrial': 'exposed brick, metal fixtures, Edison bulb lighting, urban elements, concrete accents, modern industrial decorations',
    }
    
    space_descriptions = {
        'indoor_ceremony': 'indoor wedding ceremony space with aisle and altar area',
        'outdoor_ceremony': 'outdoor wedding ceremony space with natural backdrop',
        'reception_hall': 'wedding reception dining and dancing area',
        'garden': 'outdoor garden wedding space with natural elements',
        'beach': 'beachside wedding venue with ocean views',
        'barn': 'rustic barn wedding venue with wooden elements',
        'ballroom': 'elegant ballroom wedding space',
        'rooftop': 'rooftop wedding venue with city or landscape views',
    }
    
    theme_desc = theme_descriptions.get(theme, 'beautiful wedding decorations')
    space_desc = space_descriptions.get(space_type, 'wedding venue')
    
    prompt = f"""Transform this {space_desc} into a stunning {theme} style wedding venue. 
    Add {theme_desc}. Create a romantic, inviting atmosphere perfect for a wedding celebration. 
    Maintain the original architecture but enhance it with appropriate wedding decorations, 
    lighting, and styling. The result should look realistic and professionally decorated."""
    
    return prompt


def get_wedding_choices():
    """Get wedding theme and space type choices for forms"""
    return {
        'themes': WEDDING_THEMES,
        'spaces': SPACE_TYPES,
    }


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
            
        try:
            img = Image.open(self.image.path)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumb_path = self.image.path.replace('.', '_thumb.')
            img.save(thumb_path)
            
            # Update thumbnail field
            rel_path = os.path.relpath(thumb_path, settings.MEDIA_ROOT)
            self.thumbnail.name = rel_path
            self.save(update_fields=['thumbnail'])
        except Exception as e:
            # Log error but don't fail the save
            import logging
            logging.error(f"Error creating thumbnail: {str(e)}")
    
    def get_absolute_url(self):
        return reverse('image_processing:image_detail', kwargs={'pk': self.pk})


class ImageProcessingJob(models.Model):
    """Track wedding venue transformation jobs"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, related_name='processing_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Wedding-specific fields
    wedding_theme = models.CharField(max_length=20, choices=WEDDING_THEMES, null=True, blank=True)
    space_type = models.CharField(max_length=20, choices=SPACE_TYPES, null=True, blank=True)
    generated_prompt = models.TextField(blank=True, null=True, help_text="Generated AI prompt for this job")
    
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
        theme_display = dict(WEDDING_THEMES).get(self.wedding_theme, 'Unknown')
        space_display = dict(SPACE_TYPES).get(self.space_type, 'Unknown')
        return f"Wedding Job {self.id} - {theme_display} {space_display} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Generate prompt if wedding theme and space type are provided
        if self.wedding_theme and self.space_type and not self.generated_prompt:
            self.generated_prompt = generate_wedding_prompt(self.wedding_theme, self.space_type)
        super().save(*args, **kwargs)


class ProcessedImage(models.Model):
    """Store processed wedding venue images with save/discard functionality"""
    processing_job = models.ForeignKey(ImageProcessingJob, on_delete=models.CASCADE, related_name='processed_images')
    processed_image = models.ImageField(upload_to=processed_image_upload_path)
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    
    # Save/Keep functionality
    is_saved = models.BooleanField(default=False, help_text="Whether user has chosen to save this image")
    saved_at = models.DateTimeField(blank=True, null=True, help_text="When the user saved this image")
    
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
    
    def mark_as_saved(self, collection=None):
        """Mark this image as saved by the user, optionally to a specific collection"""
        from django.utils import timezone
        self.is_saved = True
        self.saved_at = timezone.now()
        self.save(update_fields=['is_saved', 'saved_at'])
        
        # Add to collection if specified
        if collection:
            CollectionItem.objects.get_or_create(
                collection=collection,
                processed_image=self,
                defaults={'notes': f"Saved on {self.saved_at.strftime('%B %d, %Y')}"}
            )
    
    @property
    def is_temporary(self):
        """Check if this is a temporary (unsaved) image"""
        return not self.is_saved
    
    @property
    def expires_at(self):
        """When this temporary image will be deleted (48 hours after creation)"""
        if self.is_saved:
            return None
        return self.created_at + timedelta(hours=48)
    
    @property
    def time_until_deletion(self):
        """Human readable time until deletion for temporary images"""
        if self.is_saved:
            return None
        expires = self.expires_at
        if expires and expires > timezone.now():
            diff = expires - timezone.now()
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''}"
            else:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''}"
        return "Expired"
    
    def __str__(self):
        status = "Saved" if self.is_saved else "Temporary"
        return f"Wedding Transformation - Job {self.processing_job.id} ({status})"


# Keep these models for favorites and collections
class Collection(models.Model):
    """User collections/albums for organizing wedding inspiration"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False, help_text="Allow public viewing of this collection")
    is_default = models.BooleanField(default=False, help_text="Default collection for saved images")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    @classmethod
    def get_or_create_default(cls, user):
        """Get or create the default 'Saved Images' collection for a user"""
        collection, created = cls.objects.get_or_create(
            user=user,
            is_default=True,
            defaults={
                'name': 'Saved Transformations',
                'description': 'Your saved wedding venue transformations',
            }
        )
        return collection
    
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
    """Items within a wedding inspiration collection"""
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
        ]
    
    def __str__(self):
        if self.processed_image:
            return f"{self.collection.name} - Wedding Transformation"
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
            job = self.processed_image.processing_job
            theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, 'Unknown')
            space_display = dict(SPACE_TYPES).get(job.space_type, 'Unknown')
            return f"{theme_display} {space_display}"
        else:
            return self.user_image.original_filename


class Favorite(models.Model):
    """User favorites for quick access to wedding inspiration"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, null=True, blank=True)
    processed_image = models.ForeignKey('ProcessedImage', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ['user', 'user_image'],
            ['user', 'processed_image']
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        if self.processed_image:
            return f"{self.user.username} ❤️ Wedding Transformation"
        else:
            return f"{self.user.username} ❤️ {self.user_image.original_filename}"
    
    @property
    def image_url(self):
        """Get the image URL regardless of type"""
        if self.processed_image:
            return self.processed_image.processed_image.url
        else:
            return self.user_image.thumbnail.url if self.user_image.thumbnail else self.user_image.image.url