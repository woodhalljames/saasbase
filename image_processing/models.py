# image_processing/models.py - Simplified for Gemini 2.5 real-time processing with single user_instructions

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
    """Generate upload path for processed images"""
    ext = filename.split('.')[-1]
    filename = f"gemini_{uuid.uuid4().hex}.{ext}"
    return f"processed_images/{instance.processing_job.user_image.user.id}/{filename}"


# Wedding Theme Choices - Same as before with enhanced descriptions
WEDDING_THEMES = [
    # Core Popular Themes
    ('rustic', 'Rustic Farmhouse'),
    ('modern', 'Modern Contemporary'),
    ('vintage', 'Vintage Romance'),
    ('bohemian', 'Bohemian Chic'),
    ('classic', 'Classic Traditional'),
    ('garden', 'Garden Natural'),
    ('beach', 'Beach Coastal'),
    ('industrial', 'Industrial Urban'),
    ('glamorous', 'Glamorous Luxury'),
    ('tropical', 'Tropical Paradise'),
    ('fairy_tale', 'Fairy Tale Enchanted'),
    ('cultural_fusion', 'Cultural Fusion'),
    
    # Core Basic Styles
    ('minimalist', 'Minimalist Clean'),
    ('romantic', 'Romantic Dreamy'),
    ('elegant', 'Elegant Sophisticated'),
    ('chic', 'Chic Contemporary'),
    ('timeless', 'Timeless Classic'),
    
    # Popular Style Variations
    ('country_barn', 'Country Barn'),
    ('art_deco', 'Art Deco Glamour'),
    ('scandinavian', 'Scandinavian Hygge'),
    ('mediterranean', 'Mediterranean Warmth'),
    ('prairie_wildflower', 'Prairie Wildflower'),
    
    # Seasonal Specific
    ('winter_wonderland', 'Winter Wonderland'),
    ('spring_fresh', 'Spring Fresh'),
    ('harvest_festival', 'Harvest Festival'),
    
    # Approach-Based
    ('whimsical', 'Whimsical Playful'),
    ('monochrome', 'Monochrome Sophisticated'),
    ('statement_bold', 'Statement Bold'),
    ('soft_dreamy', 'Soft Dreamy'),
    ('luxury', 'Luxury Premium'),
    
    # Cultural & Traditional Themes - Enhanced with authentic details
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
    ('scandinavian_simple', 'Scandinavian Simple'),
    ('modern_monochrome', 'Modern Monochrome'),
    ('concrete_jungle', 'Concrete Jungle'),
    ('glass_house', 'Glass House'),
    
    # Vintage & Retro Themes
    ('1950s_diner', '1950s Diner'),
    ('1960s_mod', '1960s Mod'),
    ('1970s_disco', '1970s Disco'),
    ('1980s_neon', '1980s Neon'),
    ('1990s_grunge', '1990s Grunge'),
    ('victorian_romance', 'Victorian Romance'),
    ('art_nouveau', 'Art Nouveau'),
    ('great_gatsby', 'Great Gatsby'),
]


# Space Types for wedding venues
SPACE_TYPES = [
    ('wedding_ceremony', 'Wedding Ceremony'),
    ('dance_floor', 'Dance Floor / Party Area'),
    ('dining_area', 'Reception Dining'),
    ('cocktail_hour', 'Cocktail Reception'),
    ('bridal_suite', 'Bridal Suite / Getting Ready'),
    ('entrance_area', 'Entrance / Welcome Area'),
]

# Color scheme options - Comprehensive palette
COLOR_SCHEMES = [
    # Solid Colors - Single color focus
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
    
    # Pastels - Soft, light colors
    ('pastel_pink', 'Pastel Pink'),
    ('pastel_peach', 'Pastel Peach'),
    ('pastel_yellow', 'Pastel Yellow'),
    ('pastel_mint', 'Pastel Mint'),
    ('pastel_blue', 'Pastel Blue'),
    ('pastel_lavender', 'Pastel Lavender'),
    ('pastel_sage', 'Pastel Sage'),
    ('pastel_cream', 'Pastel Cream'),
    
    # Earth Tones - Natural, warm colors
    ('earth_brown', 'Brown & Tan'),
    ('earth_rust', 'Rust & Terracotta'),
    ('earth_forest', 'Forest Green & Brown'),
    ('earth_desert', 'Sand & Copper'),
    ('earth_autumn', 'Autumn Orange & Brown'),
    ('earth_moss', 'Moss Green & Stone'),
    
    # Popular Combinations - Most requested pairs
    ('black_white', 'Black & White'),
    ('pink_gold', 'Pink & Gold'),
    ('blue_white', 'Blue & White'),
    ('red_white', 'Red & White'),
    ('sage_cream', 'Sage Green & Cream'),
    ('blush_gold', 'Blush Pink & Gold'),
    ('navy_gold', 'Navy Blue & Gold'),
    ('burgundy_gold', 'Burgundy & Gold'),
    
    # Seasonal - Classic seasonal palettes
    ('spring_fresh', 'Spring (Pink, Green, Yellow)'),
    ('summer_bright', 'Summer (Coral, Turquoise, Yellow)'),
    ('autumn_harvest', 'Autumn (Orange, Burgundy, Gold)'),
    ('winter_elegant', 'Winter (Navy, Silver, White)'),
]

# Enhanced lighting mood options for more detailed prompts
LIGHTING_MOODS = [
    ('romantic', 'Romantic Candlelit'),
    ('bright', 'Bright & Cheerful'),
    ('dim', 'Intimate & Cozy'),
    ('dramatic', 'Dramatic & Bold'),
    ('natural', 'Natural Daylight'),
    ('golden', 'Golden Hour'),
    ('dusk', 'Twilight Dusk'),
    ('dawn', 'Dawn Morning Light'),
]

# Season options for seasonal decorations
SEASONS = [
    ('spring', 'Spring'),
    ('summer', 'Summer'),
    ('fall', 'Fall/Autumn'),
    ('winter', 'Winter'),
]


def generate_wedding_venue_prompt(wedding_theme, space_type, season=None, lighting_mood=None,
                                 color_scheme=None, custom_prompt=None, user_instructions=None):
    """Generate enhanced narrative text prompt for Gemini 2.5 venue transformation"""
    try:
        from .prompt_generator import WeddingVenuePromptGenerator
        
        return WeddingVenuePromptGenerator.generate_prompt(
            wedding_theme=wedding_theme,
            space_type=space_type,
            season=season,
            lighting_mood=lighting_mood,
            color_scheme=color_scheme,
            custom_prompt=custom_prompt,
            user_instructions=user_instructions
        )
    except ImportError as e:
        logger.error(f"Could not import WeddingVenuePromptGenerator: {e}")
        # Simple fallback if prompt generator is not available
        if custom_prompt and custom_prompt.strip():
            prompt = custom_prompt.strip()
            if user_instructions and user_instructions.strip():
                prompt += f" {user_instructions.strip()}"
            return prompt
        
        # Basic fallback for guided mode
        theme_name = dict(WEDDING_THEMES).get(wedding_theme, wedding_theme) if wedding_theme else "elegant"
        space_name = dict(SPACE_TYPES).get(space_type, space_type) if space_type else "wedding space"
        prompt = f"Transform this venue into a beautiful {space_name.lower()} with {theme_name.lower()} wedding styling and decorations."
        
        if user_instructions and user_instructions.strip():
            prompt += f" {user_instructions.strip()}"
        
        prompt += " Show the space without any people visible."
        return prompt


class UserImage(models.Model):
    """User uploaded venue images"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images')
    original_filename = models.CharField(max_length=255)
    image = models.ImageField(upload_to=user_image_upload_path)
    thumbnail = models.ImageField(upload_to=user_image_upload_path, blank=True, null=True)
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Optional venue details
    venue_name = models.CharField(max_length=200, blank=True, help_text="Name of the venue")
    venue_description = models.TextField(blank=True, help_text="Description of the venue space")
    
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


class ImageProcessingJob(models.Model):
    """Wedding venue transformation jobs - simplified for real-time processing"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, related_name='processing_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Core transformation parameters (guided mode)
    wedding_theme = models.CharField(max_length=50, choices=WEDDING_THEMES, blank=True)
    space_type = models.CharField(max_length=20, choices=SPACE_TYPES, blank=True)
    
    # Optional customization (guided mode) - Enhanced options
    season = models.CharField(max_length=20, choices=SEASONS, blank=True, help_text="Wedding season")
    lighting_mood = models.CharField(max_length=20, choices=LIGHTING_MOODS, blank=True, help_text="Lighting atmosphere")
    color_scheme = models.CharField(max_length=30, choices=COLOR_SCHEMES, blank=True)
    
    # Custom prompt for advanced users (custom mode)
    custom_prompt = models.TextField(blank=True, null=True,
                                   help_text="Custom prompt (overrides theme/style settings)")
    
    # Single user instructions field - appended to ALL prompts
    user_instructions = models.TextField(blank=True, null=True,
                                       help_text="Additional instructions for the transformation")
    
    # Generated final prompt (cached)
    generated_prompt = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.custom_prompt:
            return f"Job {self.id} - Custom Prompt ({self.status})"
        theme_display = dict(WEDDING_THEMES).get(self.wedding_theme, 'Unknown')
        space_display = dict(SPACE_TYPES).get(self.space_type, 'Unknown')
        return f"Job {self.id} - {theme_display} {space_display} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Generate enhanced narrative prompt if needed"""
        if not self.generated_prompt and (self.custom_prompt or (self.wedding_theme and self.space_type)):
            try:
                self.generated_prompt = generate_wedding_venue_prompt(
                    wedding_theme=self.wedding_theme,
                    space_type=self.space_type,
                    season=self.season or None,
                    lighting_mood=self.lighting_mood or None,
                    color_scheme=self.color_scheme or None,
                    custom_prompt=self.custom_prompt or None,
                    user_instructions=self.user_instructions or None
                )
                
                logger.info(f"Generated enhanced Gemini prompt for job {self.id}")
                
            except Exception as e:
                logger.error(f"Error generating prompt for job {self.id}: {str(e)}")
                # Enhanced fallback with more detail
                if self.custom_prompt:
                    self.generated_prompt = f"{self.custom_prompt}. Transform and decorate this space beautifully without any people visible."
                else:
                    theme_name = dict(WEDDING_THEMES).get(self.wedding_theme, self.wedding_theme) if self.wedding_theme else "elegant"
                    space_name = dict(SPACE_TYPES).get(self.space_type, self.space_type) if self.space_type else "wedding space"
                    self.generated_prompt = f"Transform this venue into a breathtaking {space_name.lower()} with beautiful {theme_name.lower()} wedding styling, featuring appropriate decorations, floral arrangements, and lighting. The space should be elegantly decorated and empty with no people visible."
                
                if self.user_instructions:
                    self.generated_prompt += f" {self.user_instructions}"
        
        super().save(*args, **kwargs)
    
    @property
    def theme_display_name(self):
        if self.custom_prompt:
            return "Custom Design"
        return dict(WEDDING_THEMES).get(self.wedding_theme, self.wedding_theme) if self.wedding_theme else "Custom"
    
    @property
    def space_display_name(self):
        if self.custom_prompt:
            return "Custom Space"
        return dict(SPACE_TYPES).get(self.space_type, self.space_type) if self.space_type else "Space"
    
    @property
    def is_custom_mode(self):
        """Check if this job uses custom prompt mode"""
        return bool(self.custom_prompt and self.custom_prompt.strip())


class ProcessedImage(models.Model):
    """Processed wedding venue images from Gemini 2.5"""
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
                # Set default values if image can't be opened
                self.width = 512
                self.height = 512
                self.file_size = getattr(self.processed_image, 'size', 0) or 0
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Gemini Wedding Design - {self.processing_job.theme_display_name}"
    
    @property
    def transformation_title(self):
        return f"{self.processing_job.theme_display_name} {self.processing_job.space_display_name}"


# Collection and Favorite models remain the same
class Collection(models.Model):
    """User collections for organizing wedding designs"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
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
        """Get or create the default collection for a user"""
        collection, created = cls.objects.get_or_create(
            user=user,
            is_default=True,
            defaults={
                'name': 'My Wedding Designs',
                'description': 'Your saved wedding venue designs',
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
            return f"{self.collection.name} - {self.processed_image.transformation_title}"
        else:
            return f"{self.collection.name} - {self.user_image.original_filename}"
    
    @property
    def image_url(self):
        if self.processed_image:
            return self.processed_image.processed_image.url
        else:
            return self.user_image.thumbnail.url if self.user_image.thumbnail else self.user_image.image.url
    
    @property
    def image_title(self):
        if self.processed_image:
            return self.processed_image.transformation_title
        else:
            return self.user_image.original_filename


class Favorite(models.Model):
    """User favorites for wedding designs"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    processed_image = models.ForeignKey('ProcessedImage', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'processed_image']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} ❤️ {self.processed_image.transformation_title}"
    
    @property
    def image_url(self):
        return self.processed_image.processed_image.url
    
    @property
    def image_title(self):
        return self.processed_image.transformation_title


# Helper functions
def get_wedding_choices():
    """Get choices for forms with enhanced options"""
    return {
        'themes': WEDDING_THEMES,
        'spaces': SPACE_TYPES,
        'color_schemes': COLOR_SCHEMES,
        'lighting_moods': LIGHTING_MOODS,
        'seasons': SEASONS,
    }