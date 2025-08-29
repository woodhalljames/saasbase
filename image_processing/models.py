# image_processing/models.py - Streamlined for core venue + theme transformations
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
    filename = f"processed_{uuid.uuid4().hex}.{ext}"
    return f"processed_images/{instance.processing_job.user_image.user.id}/{filename}"


# Comprehensive Wedding Theme Choices
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
    
    # Seasonal & Nature Themes
    ('winter_wonderland', 'Winter Wonderland'),
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

# Color scheme options
COLOR_SCHEMES = [
    ('neutral', 'Neutral Elegance'),
    ('pastels', 'Soft Pastels'),
    ('jewel_tones', 'Rich Jewel Tones'),
    ('earth_tones', 'Warm Earth Tones'),
    ('monochrome', 'Black & White'),
    ('bold_colors', 'Vibrant Bold Colors'),
    ('blush_gold', 'Blush & Gold'),
    ('sage_cream', 'Sage & Cream'),
    ('navy_copper', 'Navy & Copper'),
    ('burgundy_ivory', 'Burgundy & Ivory'),
]

# Style intensity levels
STYLE_INTENSITY = [
    ('subtle', 'Subtle Enhancement'),
    ('moderate', 'Balanced Transformation'),
    ('dramatic', 'Bold Transformation'),
    ('complete', 'Complete Reimagining'),
]

# Lighting mood options
LIGHTING_MOODS = [
    ('romantic', 'Romantic & Intimate'),
    ('dramatic', 'Dramatic & Bold'),
    ('soft', 'Soft & Dreamy'),
    ('vibrant', 'Bright & Energetic'),
    ('moody', 'Atmospheric & Moody'),
    ('natural', 'Natural & Fresh'),
]


def generate_wedding_prompt(wedding_theme, space_type, season=None, lighting_mood=None,
                          color_scheme=None, special_features=None, user_negative_prompt=None, **kwargs):
    """Generate SIMPLIFIED wedding venue transformation prompt with FIXED parameters"""
    try:
        from .prompt_generator import WeddingPromptGenerator
        
        # Use simplified prompt generator with only the core parameters
        return WeddingPromptGenerator.generate_wedding_prompt(
            wedding_theme=wedding_theme,
            space_type=space_type,
            season=season,
            lighting_mood=lighting_mood,  # Simplified from multiple lighting options
            color_scheme=color_scheme,
            special_features=special_features,
            avoid=user_negative_prompt,
        )
    except ImportError as e:
        logger.warning(f"Could not import WeddingPromptGenerator: {e}")
        return generate_fallback_prompt(
            wedding_theme, space_type, season, lighting_mood,
            color_scheme, special_features, user_negative_prompt
        )

def generate_fallback_prompt(wedding_theme, space_type, season=None, lighting_mood=None,
                           color_scheme=None, special_features=None, user_negative_prompt=None):
    """SIMPLIFIED fallback prompt generation with FIXED parameters"""
    
    # Get display names
    theme_display = dict(WEDDING_THEMES).get(wedding_theme, wedding_theme.replace('_', ' '))
    space_display = dict(SPACE_TYPES).get(space_type, space_type.replace('_', ' '))
    
    # Simplified theme details - core themes only
    theme_details = {
        'rustic': 'rustic farmhouse style with wooden elements, mason jars, string lights, wildflower arrangements',
        'modern': 'modern contemporary style with clean lines, minimalist decor, geometric elements',
        'vintage': 'vintage romantic style with antique furniture, lace details, garden roses, crystal chandeliers',
        'bohemian': 'bohemian chic style with macrame hangings, pampas grass, natural textures, eclectic patterns',
        'classic': 'classic traditional style with white roses, gold accents, elegant furniture, sophisticated linens',
        'garden': 'garden natural style with seasonal blooms, wrought iron details, natural lighting, greenery',
        'beach': 'beach coastal style with driftwood accents, seashells, hurricane lanterns, tropical florals',
        'industrial': 'industrial urban style with exposed brick, steel beams, Edison bulbs, metal fixtures',
        'glamorous': 'glamorous luxury style with crystal chandeliers, gold accents, premium roses, dramatic lighting',
        'tropical': 'tropical paradise style with palm fronds, exotic flowers, bamboo elements, vibrant colors'
    }.get(wedding_theme, f'{theme_display} style decorations')
    
    # Build main prompt
    main_parts = [
        f'elegant {space_display.lower()} wedding venue',
        f'decorated in {theme_details}'
    ]
    
    # Add SIMPLIFIED optional elements
    if color_scheme:
        color_map = {
            'neutral': 'with sophisticated neutral palette of whites, creams, and beiges',
            'pastels': 'with soft pastel colors including blush pinks and sage greens',
            'jewel_tones': 'with rich jewel tones of emerald, sapphire, and gold',
            'earth_tones': 'with warm earth tones of terracotta, sage, and bronze',
            'monochrome': 'with elegant black, white, and gray palette',
            'bold_colors': 'with vibrant bold colors and striking contrasts'
        }
        if color_scheme in color_map:
            main_parts.append(color_map[color_scheme])
    
    # Add lighting mood (simplified from multiple lighting options)
    if lighting_mood:
        lighting_map = {
            'romantic': 'with romantic warm lighting and intimate ambiance',
            'bright': 'with bright cheerful lighting and energetic atmosphere',
            'dim': 'with intimate dim lighting and cozy atmosphere',
            'dramatic': 'with dramatic bold lighting and theatrical mood',
            'natural': 'with beautiful natural lighting and fresh brightness',
            'golden': 'with golden hour lighting and warm glow',
            'dusk': 'with twilight dusk atmosphere and evening ambiance',
            'dawn': 'with soft morning light and fresh beginning feel'
        }
        if lighting_mood in lighting_map:
            main_parts.append(lighting_map[lighting_mood])
    
    # Add seasonal context
    if season:
        seasonal_map = {
            'spring': 'with spring blooms and fresh greenery',
            'summer': 'with lush summer elements and light colors',
            'fall': 'with autumn colors and warm golden tones',
            'winter': 'with winter elegance and rich textures'
        }
        if season in seasonal_map:
            main_parts.append(seasonal_map[season])
    
    # Add special features
    if special_features and special_features.strip():
        main_parts.append(f'incorporating {special_features.strip()}')
    
    main_prompt = " ".join(main_parts)
    
    # Quality descriptors (simplified)
    quality_parts = [
        "professional wedding photography",
        "elegant design execution",
        "beautiful lighting setup", 
        "high quality details",
        "sophisticated styling"
    ]
    
    final_prompt = f"{main_prompt}, {', '.join(quality_parts)}"
    
    # Negative prompt (simplified)
    negative_elements = [
        "people, person, humans, guests, bride, groom, wedding party",
        "blurry, poorly lit, overexposed",
        "tables and chairs with multiple legs, multiple utilities in the same space",
        "text, watermark, logos"
    ]
    
    if user_negative_prompt and user_negative_prompt.strip():
        negative_elements.append(user_negative_prompt.strip())
    
    negative_prompt = ", ".join(negative_elements)
    
    # FIXED parameters - no more customization
    return {
        'prompt': final_prompt,
        'negative_prompt': negative_prompt,
        'recommended_params': {
            'strength': 0.70,      # FIXED at 70%
            'cfg_scale': 7.5,      # FIXED standard CFG  
            'steps': 30,           # FIXED at 30 steps
            'output_format': 'png'
        }
    }


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
    """Wedding venue transformation jobs - streamlined version"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, related_name='processing_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Core transformation parameters
    wedding_theme = models.CharField(max_length=50, choices=WEDDING_THEMES)
    space_type = models.CharField(max_length=20, choices=SPACE_TYPES)
    
    # Style customization
    season = models.CharField(max_length=20, blank=True, help_text="Wedding season")
    time_of_day = models.CharField(max_length=20, blank=True, help_text="Time of day")
    color_scheme = models.CharField(max_length=30, choices=COLOR_SCHEMES, blank=True)
    style_intensity = models.CharField(max_length=20, choices=STYLE_INTENSITY, blank=True)
    lighting_mood = models.CharField(max_length=20, choices=LIGHTING_MOODS, blank=True)
    
    # Additional customization
    special_features = models.TextField(blank=True, null=True, 
                                      help_text="Special features to highlight or incorporate")
    avoid = models.TextField(blank=True, null=True, 
                           help_text="Elements to avoid in the transformation")
    
    # Generated prompts
    generated_prompt = models.TextField(blank=True, null=True)
    negative_prompt = models.TextField(blank=True, null=True)
    
    # Generation parameters
    cfg_scale = models.FloatField(default=7.5, help_text="CFG scale (1.0-20.0)")
    steps = models.IntegerField(default=40, help_text="Generation steps (10-100)")
    seed = models.BigIntegerField(blank=True, null=True, help_text="Random seed")
    strength = models.FloatField(default=0.85, help_text="Transformation strength (0.0-1.0)")
    output_format = models.CharField(max_length=10, default='png')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        theme_display = dict(WEDDING_THEMES).get(self.wedding_theme, 'Unknown')
        space_display = dict(SPACE_TYPES).get(self.space_type, 'Unknown')
        return f"Job {self.id} - {theme_display} {space_display} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Generate prompt if needed"""
        if self.wedding_theme and self.space_type and not self.generated_prompt:
            try:
                prompt_data = generate_wedding_prompt(
                    wedding_theme=self.wedding_theme,
                    space_type=self.space_type,
                    season=self.season or None,
                    time_of_day=self.time_of_day or None,
                    color_scheme=self.color_scheme or None,
                    style_intensity=self.style_intensity or None,
                    lighting_mood=self.lighting_mood or None,
                    special_features=self.special_features or None,
                    avoid=self.avoid or None
                )
                
                self.generated_prompt = prompt_data['prompt']
                self.negative_prompt = prompt_data['negative_prompt']
                
                # Update parameters with recommendations
                recommended = prompt_data['recommended_params']
                self.strength = recommended.get('strength', self.strength)
                self.cfg_scale = recommended.get('cfg_scale', self.cfg_scale)
                self.steps = recommended.get('steps', self.steps)
                self.output_format = recommended.get('output_format', self.output_format)
                
                logger.info(f"Generated prompt for job {self.id}")
                
            except Exception as e:
                logger.error(f"Error generating prompt for job {self.id}: {str(e)}")
                # Fallback prompt
                theme_name = dict(WEDDING_THEMES).get(self.wedding_theme, self.wedding_theme)
                space_name = dict(SPACE_TYPES).get(self.space_type, self.space_type)
                self.generated_prompt = f"elegant wedding {space_name.lower()} with {theme_name.lower()} style, professional wedding photography"
                self.negative_prompt = "people, faces, crowd, guests, blurry, low quality"
        
        super().save(*args, **kwargs)
    
    def get_stability_ai_params(self):
        """Get parameters for Stability AI API"""
        return {
            'prompt': self.generated_prompt,
            'negative_prompt': self.negative_prompt,
            'strength': self.strength,
            'cfg_scale': self.cfg_scale,
            'steps': self.steps,
            'seed': self.seed,
            'output_format': self.output_format,
        }
    
    @property
    def theme_display_name(self):
        return dict(WEDDING_THEMES).get(self.wedding_theme, self.wedding_theme)
    
    @property
    def space_display_name(self):
        return dict(SPACE_TYPES).get(self.space_type, self.space_type)


class ProcessedImage(models.Model):
    """Processed wedding venue images"""
    processing_job = models.ForeignKey(ImageProcessingJob, on_delete=models.CASCADE, related_name='processed_images')
    processed_image = models.ImageField(upload_to=processed_image_upload_path)
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    
    # AI generation metadata
    stability_seed = models.BigIntegerField(blank=True, null=True)
    finish_reason = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.processed_image:
            img = Image.open(self.processed_image)
            self.width, self.height = img.size
            self.file_size = self.processed_image.size
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Wedding Design - {self.processing_job.theme_display_name}"
    
    @property
    def transformation_title(self):
        return f"{self.processing_job.theme_display_name} {self.processing_job.space_display_name}"


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
    """Get choices for forms"""
    return {
        'themes': WEDDING_THEMES,
        'spaces': SPACE_TYPES,
        'color_schemes': COLOR_SCHEMES,
        'style_intensity': STYLE_INTENSITY,
        'lighting_moods': LIGHTING_MOODS,
    }