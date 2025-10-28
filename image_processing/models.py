# image_processing/models.py - FIXED: Remove auto prompt generation from save()

import os
import uuid
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


def user_image_upload_path(instance, filename):
    """Generate upload path for user images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"user_images/{instance.user.id}/{filename}"


def processed_image_upload_path(instance, filename):
    """Generate upload path for processed images - preserves human-readable filename"""
    import os
    import re
    
    base_filename = os.path.basename(filename)
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', base_filename)
    
    if '.' not in safe_filename:
        safe_filename += '.png'
    
    return f"processed_images/{instance.processing_job.user_image.user.id}/{safe_filename}"


# Wedding Theme Choices - ALIGNED WITH PROMPT_GENERATOR (80+ themes)
WEDDING_THEMES = [
    # Classic Traditional Themes
    ('rustic', 'Rustic Farmhouse'),
    ('modern', 'Modern Contemporary'),
    ('vintage', 'Vintage Romance'),
    ('classic', 'Classic Traditional'),
    ('garden', 'Garden Natural'),
    ('beach', 'Beach Coastal'),
    ('industrial', 'Industrial Urban'),
    ('bohemian', 'Bohemian Chic'),
    ('glamorous', 'Glamorous Luxury'),
    ('tropical', 'Tropical Paradise'),
    ('fairy_tale', 'Fairy Tale Enchanted'),
    ('minimalist', 'Minimalist Clean'),
    ('romantic', 'Romantic Dreamy'),
    ('elegant', 'Elegant Sophisticated'),
    ('chic', 'Chic Contemporary'),
    ('timeless', 'Timeless Classic'),
    
    # Popular Style Variations
    ('country_barn', 'Country Barn'),
    ('art_deco', 'Art Deco Glamour'),
    ('scandinavian', 'Scandinavian Hygge'),
    ('mediterranean', 'Mediterranean'),
    ('prairie_wildflower', 'Prairie Wildflower'),
    
    # Seasonal Specific
    ('winter_wonderland', 'Winter Wonderland'),
    ('spring_fresh', 'Spring Fresh'),
    ('harvest_festival', 'Harvest Festival'),
    
    # Approach-Based
    ('whimsical', 'Whimsical Playful'),
    ('monochrome', 'Monochrome B&W'),
    ('statement_bold', 'Bold Statement'),
    ('soft_dreamy', 'Soft Dreamy'),
    ('luxury', 'Premium Luxury'),
    
    # Cultural & Traditional Themes
    ('japanese_zen', 'Japanese Zen'),
    ('chinese_dynasty', 'Chinese Dynasty'),
    ('indian_palace', 'Indian Palace'),
    ('korean_hanbok', 'Korean Hanbok'),
    ('thai_temple', 'Thai Temple'),
    ('scottish_highland', 'Scottish Highland'),
    ('french_chateau', 'French Château'),
    ('greek_island', 'Greek Island'),
    ('italian_villa', 'Italian Villa'),
    ('english_garden', 'English Garden'),
    ('mexican_fiesta', 'Mexican Fiesta'),
    ('spanish_hacienda', 'Spanish Hacienda'),
    ('brazilian_carnival', 'Brazilian Carnival'),
    ('argentine_tango', 'Argentine Tango'),
    ('moroccan_nights', 'Moroccan Nights'),
    ('arabian_desert', 'Arabian Desert'),
    ('african_safari', 'African Safari'),
    ('egyptian_royal', 'Egyptian Royal'),
    
    # Nature & Seasonal Themes
    ('spring_awakening', 'Spring Awakening'),
    ('summer_solstice', 'Summer Solstice'),
    ('autumn_harvest', 'Autumn Harvest'),
    ('forest_enchanted', 'Enchanted Forest'),
    ('desert_bloom', 'Desert Bloom'),
    ('ocean_waves', 'Ocean Waves'),
    ('mountain_vista', 'Mountain Vista'),
    
    # Modern & Contemporary Themes
    ('metropolitan_chic', 'Metropolitan Chic'),
    ('brooklyn_loft', 'Brooklyn Loft'),
    ('rooftop_garden', 'Rooftop Garden'),
    ('art_deco_glam', 'Art Deco Glam'),
    ('concrete_jungle', 'Concrete Jungle'),
    ('glass_house', 'Glass House'),
    
    # Vintage & Retro Themes
    ('1950s_diner', '1950s Diner Retro'),
    ('1960s_mod', '1960s Mod'),
    ('1970s_disco', '1970s Disco'),
    ('1980s_neon', '1980s Neon'),
    ('1990s_grunge', '1990s Grunge'),
    ('victorian_romance', 'Victorian Romance'),
    ('art_nouveau', 'Art Nouveau'),
    ('great_gatsby', 'Great Gatsby'),
    
    # Special option
    ('use_pictured', 'Use Pictured Style'),
]

SPACE_TYPES = [
    ('wedding_ceremony', 'Wedding Ceremony'),
    ('dance_floor', 'Dance Floor / Party Area'),
    ('dining_area', 'Reception Dining'),
    ('cocktail_hour', 'Cocktail Reception'),
    ('bridal_suite', 'Bridal Suite / Getting Ready'),
    ('entrance_area', 'Entrance / Welcome Area'),
    ('use_pictured', 'Use Pictured Space'),
]

# Portrait Studio Themes - ALIGNED
PORTRAIT_THEMES = [
    ('classic_elegant', 'Classic Elegant'),
    ('modern_romantic', 'Modern Romantic'),
    ('outdoor_natural', 'Outdoor Natural'),
    ('vintage_timeless', 'Vintage Timeless'),
    ('destination_exotic', 'Destination Exotic'),
    ('bohemian_free', 'Bohemian Free-Spirited'),
    ('luxury_glamour', 'Luxury Glamour'),
    ('casual_lifestyle', 'Casual Lifestyle'),
    ('urban_chic', 'Urban Chic'),
    ('minimalist_modern', 'Minimalist Modern'),
    ('use_pictured', 'Use Pictured Style'),
]

PORTRAIT_SETTINGS = [
    ('studio', 'Studio / Indoor'),
    ('garden', 'Garden / Park'),
    ('beach', 'Beach / Waterfront'),
    ('urban', 'Urban / City'),
    ('countryside', 'Countryside / Rural'),
    ('venue_interior', 'Wedding Venue Interior'),
    ('mountain', 'Mountain / Vista'),
    ('forest', 'Forest / Woods'),
    ('home', 'Home / Cozy Indoor'),
    ('coffee_shop', 'Coffee Shop / Café'),
    ('use_pictured', 'Use Pictured Location'),
]

PORTRAIT_POSES = [
    # Standard Poses
    ('formal_portrait', 'Formal Portrait'),
    ('romantic_embrace', 'Romantic Embrace'),
    ('candid_laughing', 'Candid & Laughing'),
    ('walking_together', 'Walking Together'),
    ('sitting_intimate', 'Sitting Intimate'),
    ('dancing', 'Dancing'),
    ('playful_fun', 'Playful & Fun'),
    ('forehead_kiss', 'Forehead Kiss'),
    ('looking_at_each_other', 'Looking at Each Other'),
    
    # Activity & Hobby Poses (Mainly for Engagement)
    ('playing_board_game', 'Playing Board Game'),
    ('cooking_together', 'Cooking Together'),
    ('hiking', 'Hiking'),
    ('coffee_date', 'Coffee Date'),
    ('skiing_snowboarding', 'Skiing/Snowboarding'),
    ('reading_together', 'Reading Together'),
    ('picnic', 'Picnic'),
    ('biking', 'Biking'),
    
    ('use_pictured', 'Use Pictured Pose/Activity'),
]

PORTRAIT_ATTIRE = [
    # Wedding Attire
    ('traditional_formal', 'Traditional Wedding Attire'),
    ('modern_chic', 'Modern Chic'),
    ('casual_elegant', 'Casual Elegant'),
    ('bohemian', 'Bohemian Style'),
    ('vintage_inspired', 'Vintage Inspired'),
    ('cultural_traditional', 'Cultural Traditional'),
    
    # Engagement Attire
    ('formal_elegant', 'Formal Elegant'),
    ('cozy_casual', 'Cozy Casual'),
    ('activity_specific', 'Activity-Specific'),
    
    ('use_pictured', 'Use Pictured Attire'),
]

COLOR_SCHEMES = [
    # Primary Colors
    ('red', 'Red'),
    ('pink', 'Pink'),
    ('coral', 'Coral'),
    ('orange', 'Orange'),
    ('yellow', 'Yellow'),
    ('green', 'Green'),
    ('blue', 'Blue'),
    ('purple', 'Purple'),
    ('white', 'White'),
    ('black', 'Black'),
    
    # Pastels
    ('pastel_pink', 'Pastel Pink'),
    ('pastel_peach', 'Pastel Peach'),
    ('pastel_yellow', 'Pastel Yellow'),
    ('pastel_mint', 'Pastel Mint'),
    ('pastel_blue', 'Pastel Blue'),
    ('pastel_lavender', 'Pastel Lavender'),
    ('pastel_sage', 'Pastel Sage'),
    ('pastel_cream', 'Pastel Cream'),
    
    # Earth Tones
    ('earth_brown', 'Earth Brown'),
    ('earth_rust', 'Earth Rust'),
    ('earth_forest', 'Earth Forest'),
    ('earth_desert', 'Earth Desert'),
    ('earth_autumn', 'Earth Autumn'),
    ('earth_moss', 'Earth Moss'),
    
    # Popular Combinations
    ('black_white', 'Black & White'),
    ('pink_gold', 'Pink & Gold'),
    ('blue_white', 'Blue & White'),
    ('red_white', 'Red & White'),
    ('sage_cream', 'Sage & Cream'),
    ('blush_gold', 'Blush & Gold'),
    ('navy_gold', 'Navy & Gold'),
    ('burgundy_gold', 'Burgundy & Gold'),
    
    # Seasonal
    ('spring_fresh', 'Spring Fresh'),
    ('summer_bright', 'Summer Bright'),
    ('autumn_harvest', 'Autumn Harvest'),
    ('winter_elegant', 'Winter Elegant'),
    
    # Portrait-specific
    ('vibrant_bold', 'Vibrant Bold'),
    ('light_airy_pastels', 'Light Airy Pastels'),
    ('earth_tones_natural', 'Earth Tones Natural'),
    ('moody_dramatic', 'Moody Dramatic'),
    ('black_white_classic', 'Black & White Classic'),
    ('warm_tones', 'Warm Tones'),
    ('cool_tones', 'Cool Tones'),
    
    ('use_pictured', 'Use Pictured Colors'),
]

LIGHTING_MOODS = [
    # Time-based
    ('dawn', 'Dawn Morning Light'),
    ('morning', 'Morning Light'),
    ('midday', 'Midday Bright'),
    ('golden', 'Golden Hour'),
    ('dusk', 'Twilight Dusk'),
    ('evening', 'Evening'),
    ('night', 'Night'),
    
    # Mood-based
    ('romantic', 'Romantic Warm'),
    ('bright', 'Bright & Cheerful'),
    ('dim', 'Intimate & Cozy'),
    ('dramatic', 'Dramatic & Bold'),
    ('candlelit', 'Candlelit'),
    
    # Quality-based
    ('natural', 'Natural Daylight'),
    ('fluorescent', 'Fluorescent Bright'),
    ('rainy', 'Rainy/Overcast'),
    
    ('use_pictured', 'Use Pictured Lighting'),
]

SEASONS = [
    ('spring', 'Spring'),
    ('summer', 'Summer'),
    ('fall', 'Fall/Autumn'),
    ('winter', 'Winter'),
    ('use_pictured', 'Use Pictured Season'),
]


class UserImage(models.Model):
    """User uploaded images - for all studio modes"""
    
    IMAGE_TYPES = [
        ('venue', 'Venue Photo'),
        ('face', 'Face Photo'),
        ('reference', 'Reference Image'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images')
    original_filename = models.CharField(max_length=255)
    image = models.ImageField(upload_to=user_image_upload_path)
    thumbnail = models.ImageField(upload_to=user_image_upload_path, blank=True, null=True)
    
    # Image classification
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPES, default='venue',
                                  help_text="Type of image uploaded")
    
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Optional metadata
    venue_name = models.CharField(max_length=200, blank=True, help_text="Name or label")
    venue_description = models.TextField(blank=True, help_text="Description or notes")
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.original_filename}"
    
    def save(self, *args, **kwargs):
        if self.image and not self.width:
            img = Image.open(self.image)
            self.width, self.height = img.size
            self.file_size = self.image.size
            
        super().save(*args, **kwargs)
        
        if self.image and not self.thumbnail:
            self.create_thumbnail()
    
    def create_thumbnail(self):
        """Create a thumbnail for the image"""
        if not self.image:
            return
            
        try:
            from PIL import Image as PILImage
            import os
            from django.core.files.base import ContentFile
            import io
            
            img = PILImage.open(self.image.path)
            
            if img.mode in ('RGBA', 'LA', 'P'):
                background = PILImage.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            img.thumbnail((300, 300), PILImage.Resampling.LANCZOS)
            
            thumb_io = io.BytesIO()
            img.save(thumb_io, format='JPEG', quality=85)
            thumb_io.seek(0)
            
            name, ext = os.path.splitext(self.image.name)
            thumb_filename = f"{name}_thumb.jpg"
            
            self.thumbnail.save(
                os.path.basename(thumb_filename),
                ContentFile(thumb_io.read()),
                save=False
            )
            
            super().save(update_fields=['thumbnail'])
            logger.info(f"Created thumbnail for image: {self.original_filename}")
            
        except Exception as e:
            logger.error(f"Error creating thumbnail for {self.original_filename}: {str(e)}")


class FavoriteUpload(models.Model):
    """Favorites for uploaded images (star icon) - for quick access in studio"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_uploads')
    image = models.ForeignKey(UserImage, on_delete=models.CASCADE, related_name='favorited_by')
    
    # Usage tracking
    times_used = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'image']
        ordering = ['-last_used', '-created_at']
        verbose_name = 'Favorite Upload'
        verbose_name_plural = 'Favorite Uploads'
    
    def __str__(self):
        return f"{self.user.username} ⭐ {self.image.original_filename}"
    
    def increment_usage(self):
        """Increment usage counter and update last used timestamp"""
        self.times_used += 1
        self.last_used = timezone.now()
        self.save(update_fields=['times_used', 'last_used'])


class ImageProcessingJob(models.Model):
    """Processing jobs - supports venue, wedding portrait, and engagement portrait modes"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    STUDIO_MODES = [
        ('venue', 'Venue Design'),
        ('portrait_wedding', 'Wedding Portrait'),
        ('portrait_engagement', 'Engagement Portrait'),
    ]
    
    # Primary image (main input)
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, related_name='processing_jobs')
    
    # Studio mode selection
    studio_mode = models.CharField(max_length=20, choices=STUDIO_MODES, default='venue')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # VENUE MODE FIELDS
    wedding_theme = models.CharField(max_length=50, choices=WEDDING_THEMES, blank=True)
    space_type = models.CharField(max_length=20, choices=SPACE_TYPES, blank=True)
    
    # PORTRAIT MODE FIELDS
    photo_theme = models.CharField(max_length=50, choices=PORTRAIT_THEMES, blank=True)
    setting_type = models.CharField(max_length=30, choices=PORTRAIT_SETTINGS, blank=True)
    pose_style = models.CharField(max_length=30, choices=PORTRAIT_POSES, blank=True)
    attire_style = models.CharField(max_length=30, choices=PORTRAIT_ATTIRE, blank=True)
    
    # SHARED OPTIONAL FIELDS
    season = models.CharField(max_length=20, choices=SEASONS, blank=True)
    lighting_mood = models.CharField(max_length=20, choices=LIGHTING_MOODS, blank=True)
    color_scheme = models.CharField(max_length=30, choices=COLOR_SCHEMES, blank=True)
    
    # Custom prompt (overrides guided mode)
    custom_prompt = models.TextField(blank=True, null=True)
    
    # User instructions (appended to all prompts)
    user_instructions = models.TextField(blank=True, null=True)
    
    # Generated final prompt (cached) - NO LONGER AUTO-GENERATED IN SAVE
    generated_prompt = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        mode_display = dict(self.STUDIO_MODES).get(self.studio_mode, self.studio_mode)
        return f"Job {self.id} - {mode_display} ({self.status})"
    
    # REMOVED: Auto prompt generation from save() method
    # Prompt is now generated in views.py BEFORE job creation
    
    @property
    def is_venue_mode(self):
        return self.studio_mode == 'venue'
    
    @property
    def is_portrait_mode(self):
        return self.studio_mode.startswith('portrait_')
    
    @property
    def mode_display(self):
        return dict(self.STUDIO_MODES).get(self.studio_mode, self.studio_mode)


class JobReferenceImage(models.Model):
    """Links multiple reference images to a single processing job (up to 5 images)"""
    job = models.ForeignKey(
        ImageProcessingJob, 
        on_delete=models.CASCADE,
        related_name='reference_images'
    )
    reference_image = models.ForeignKey(
        UserImage,
        on_delete=models.CASCADE
    )
    order = models.IntegerField(default=0, help_text="Order of reference images")
    
    class Meta:
        ordering = ['order']
        unique_together = ['job', 'reference_image']
    
    def __str__(self):
        return f"Job {self.job.id} - Reference {self.order + 1}"


class ProcessedImage(models.Model):
    """Processed images from Gemini - single output only"""
    processing_job = models.ForeignKey(ImageProcessingJob, on_delete=models.CASCADE, related_name='processed_images')
    processed_image = models.ImageField(upload_to=processed_image_upload_path)
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    
    # Gemini generation metadata
    gemini_model = models.CharField(max_length=50, default='gemini-2.5-flash-image-preview')
    finish_reason = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.processed_image and not self.width:
            try:
                img = Image.open(self.processed_image)
                self.width, self.height = img.size
                self.file_size = self.processed_image.size
            except Exception as e:
                logger.error(f"Error getting image dimensions: {str(e)}")
                self.width = 512
                self.height = 512
                self.file_size = getattr(self.processed_image, 'size', 0) or 0
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.processing_job.mode_display} - Output"


# Collections and Favorites for Processed Images
class Collection(models.Model):
    """User collections for organizing designs"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    @classmethod
    def get_or_create_default(cls, user):
        collection, created = cls.objects.get_or_create(
            user=user,
            is_default=True,
            defaults={
                'name': 'My Designs',
                'description': 'Your saved designs',
            }
        )
        return collection
    
    @property
    def item_count(self):
        return self.items.count()
    
    @property
    def thumbnail(self):
        first_item = self.items.first()
        if first_item:
            if first_item.processed_image:
                return first_item.processed_image.processed_image
            else:
                return first_item.user_image.thumbnail or first_item.user_image.image
        return None


class CollectionItem(models.Model):
    """Items within a collection"""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='items')
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, null=True, blank=True)
    processed_image = models.ForeignKey('ProcessedImage', on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True, null=True, help_text="Personal notes about this design")
    order = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-added_at']
        unique_together = [
            ['collection', 'user_image'],
            ['collection', 'processed_image']
        ]
    
    def __str__(self):
        if self.processed_image:
            return f"{self.collection.name} - {self.processed_image}"
        else:
            return f"{self.collection.name} - {self.user_image.original_filename}"


class Favorite(models.Model):
    """Favorites for processed images (heart icon)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    processed_image = models.ForeignKey('ProcessedImage', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'processed_image']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} ♥ {self.processed_image}"