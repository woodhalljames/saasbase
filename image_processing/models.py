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


# Comprehensive Wedding Theme Choices - 50+ Beautiful Wedding Styles
WEDDING_THEMES = [
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
    ('tropical_paradise', 'Tropical Paradise'),
    
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
    
    # Fantasy & Themed Celebrations
    ('enchanted_forest_fairy', 'Enchanted Forest Fairy'),
    ('princess_castle', 'Princess Castle'),
    ('mermaid_lagoon', 'Mermaid Lagoon'),
    ('dragon_castle', 'Dragon & Castle'),
    ('unicorn_dreams', 'Unicorn Dreams'),
    ('hollywood_glam', 'Hollywood Glam'),
    ('broadway_musical', 'Broadway Musical'),
    ('vintage_circus', 'Vintage Circus'),
    ('comic_book', 'Comic Book'),
    
    # Holiday & Celebration Themes
    ('christmas_magic', 'Christmas Magic'),
    ('halloween_gothic', 'Halloween Gothic'),
    ('valentine_romance', 'Valentine Romance'),
    ('new_year_eve', "New Year's Eve"),
    ('fourth_july', 'Fourth of July'),
    ('dia_muertos', 'Día de los Muertos'),
    ('chinese_new_year', 'Chinese New Year'),
    ('oktoberfest', 'Oktoberfest'),
    ('mardi_gras', 'Mardi Gras'),
    
    # Unique & Creative Themes
    ('book_lovers', 'Book Lovers'),
    ('music_festival', 'Music Festival'),
    ('travel_adventure', 'Travel Adventure'),
    ('wine_country', 'Wine Country'),
    ('coffee_house', 'Coffee House'),
    ('neon_cyberpunk', 'Neon Cyberpunk'),
    ('steampunk_victorian', 'Steampunk Victorian'),
    ('space_galaxy', 'Space Galaxy'),
    ('under_the_sea', 'Under the Sea'),
    ('secret_garden', 'Secret Garden'),
    
    # Classic Popular Themes (keeping originals for backward compatibility)
    ('rustic', 'Rustic Barn'),
    ('modern', 'Modern Elegant'),
    ('vintage', 'Vintage Romance'),
    ('bohemian', 'Bohemian Chic'),
    ('classic', 'Classic Traditional'),
    ('garden', 'Garden Party'),
    ('beach', 'Beach Paradise'),
    ('industrial', 'Industrial Chic'),
]

# STREAMLINED SPACE TYPES - Focus on 5 key wedding spaces
SPACE_TYPES = [
    ('wedding_ceremony', 'Wedding Ceremony'),
    ('dance_floor', 'Dance Floor'),
    ('dining_area', 'Dining Area'),
    ('cocktail_hour', 'Cocktail Hour'),
    ('lounge_area', 'Lounge Area'),
]

def generate_wedding_prompt(theme, space_type, additional_details=None):
    """Generate comprehensive AI prompt for wedding venue transformation using improved space-first system"""
    try:
        from .prompt_generator import WeddingPromptGenerator
        
        return WeddingPromptGenerator.generate_space_first_prompt(
            wedding_theme=theme, 
            space_type=space_type, 
            additional_details=additional_details
        )
    except ImportError as e:
        # Enhanced fallback prompt generation if import fails
        logger.warning(f"Could not import improved WeddingPromptGenerator: {e}")
        return generate_space_first_fallback_prompt(theme, space_type, additional_details)


def generate_wedding_prompt_with_dynamics(wedding_theme, space_type, guest_count=None, 
                                        budget_level=None, season=None, time_of_day=None,
                                        color_scheme=None, custom_colors=None, 
                                        religion_culture=None, user_negative_prompt=None,
                                        additional_details=None):
    """Generate comprehensive AI prompt with space-first approach for SD3.5 Large including religion/culture and user negative prompts"""
    try:
        from .prompt_generator import WeddingPromptGenerator
        
        return WeddingPromptGenerator.generate_space_first_prompt(
            wedding_theme=wedding_theme,
            space_type=space_type,
            guest_count=guest_count,
            budget_level=budget_level,
            season=season,
            time_of_day=time_of_day,
            color_scheme=color_scheme,
            custom_colors=custom_colors,
            religion_culture=religion_culture,
            user_negative_prompt=user_negative_prompt,
            additional_details=additional_details
        )
    except ImportError as e:
        logger.warning(f"Could not import improved WeddingPromptGenerator: {e}")
        return generate_space_first_fallback_prompt(wedding_theme, space_type, additional_details, guest_count)


def generate_space_first_fallback_prompt(theme, space_type, additional_details=None, guest_count=None):
    """Space-first fallback prompt generation optimized for Stable Image Ultra"""
    
    # Space definitions (more concise for Ultra)
    space_definitions = {
        'wedding_ceremony': {
            'function': 'wedding ceremony venue with processional aisle and guest seating',
            'elements': 'ceremony altar or arch, guest seating rows, center processional aisle',
            'requirements': 'clear sightlines to altar, wedding party space'
        },
        'dance_floor': {
            'function': 'dance floor for wedding reception entertainment and dancing', 
            'elements': 'smooth dance floor surface, DJ setup area, perimeter lounge seating, dance lighting',
            'requirements': 'proper flooring for dancing, sound system positioning, adequate lighting'
        },
        'dining_area': {
            'function': 'dining area for wedding reception meal service',
            'elements': 'dining tables with seating, table place settings, centerpieces',
            'requirements': 'proper table spacing, comfortable seating, clear service access'
        },
        'cocktail_hour': {
            'function': 'cocktail area for guest mingling and appetizers',
            'elements': 'cocktail tables, bar setup, standing areas, appetizer stations',
            'requirements': 'bar service area, food stations, mingling space'
        },
        'lounge_area': {
            'function': 'lounge area for comfortable conversation and relaxation',
            'elements': 'comfortable sofas and chairs, coffee tables, ambient lighting', 
            'requirements': 'comfortable furniture, conversation lighting, relaxed atmosphere'
        }
    }
    
    # Theme styling (concise for Ultra)
    theme_styling = {
        'rustic': 'rustic wooden elements, burlap details, mason jar lighting, wildflowers, string lights',
        'modern': 'sleek geometric furniture, contemporary materials, minimalist decorations, modern lighting',
        'vintage': 'antique furniture, vintage lace details, classic roses, ornate chandeliers',
        'bohemian': 'macrame details, pampas grass, colorful textiles, natural materials',
        'classic': 'elegant formal furniture, crystal chandeliers, white linens, classic flowers',
        'garden': 'natural flowers, greenery, botanical elements, garden furniture',
        'beach': 'coastal elements, flowing fabrics, natural wood, seashell details',
        'industrial': 'metal fixtures, Edison bulb lighting, concrete elements, urban materials',
        'indian_palace': 'ornate gold furniture, rich silk draping, marigold flowers, intricate carved details',
        'japanese_zen': 'bamboo screens, cherry blossoms, minimalist wooden furniture, paper lanterns',
        'moroccan_nights': 'ornate metallic lanterns, rich tapestries, low cushioned seating',
    }
    
    # Get space and theme data
    space_data = space_definitions.get(space_type, space_definitions['wedding_ceremony'])
    theme_elements = theme_styling.get(theme, 'elegant wedding decorations')
    
    # Guest count specifications (concise)
    guest_specs = {
        'intimate': '15-50 guests',
        'medium': '75-100 guests', 
        'large': '150-200 guests',
        'grand': '250+ guests'
    }
    
    guest_spec = guest_specs.get(guest_count, '75-100 guests')
    
    # BUILD CONCISE PROMPT for Ultra
    prompt_parts = [
        f"Transform this space into {space_data['function']} for {guest_spec}.",
        f"{space_data['elements']}.",
        f"{space_data['requirements']}.", 
        f"{theme} wedding theme featuring {theme_elements}.",
        f"Output requirements: {theme} wedding setup ready for guests, no people visible, celebration-ready venue."
    ]
    
    # Add additional details if provided
    if additional_details:
        prompt_parts.insert(-1, f"{additional_details}.")
    
    # Assemble prompt
    main_prompt = " ".join(prompt_parts)
    
    # Concise negative prompt for Ultra
    negative_prompt = "people, faces, crowd, guests, blurry, low quality, dark, messy, text, watermark, cartoon, unrealistic"
    
    return {
        'prompt': main_prompt,
        'negative_prompt': negative_prompt,
        'recommended_params': {
            'strength': 0.4,
            'cfg_scale': 7.0,
            'steps': 40,
            'output_format': 'png',
        }
    }



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
        # Set image dimensions and file size before saving
        if self.image and not self.width:
            img = Image.open(self.image)
            self.width, self.height = img.size
            self.file_size = self.image.size
            
        super().save(*args, **kwargs)
        
        # Create thumbnail after saving (only if we don't have one)
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
            
            # Open the original image
            img = PILImage.open(self.image.path)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = PILImage.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Create thumbnail (300x300 max, keeping aspect ratio)
            img.thumbnail((300, 300), PILImage.Resampling.LANCZOS)
            
            # Save to bytes
            thumb_io = io.BytesIO()
            img.save(thumb_io, format='JPEG', quality=85)
            thumb_io.seek(0)
            
            # Generate thumbnail filename
            name, ext = os.path.splitext(self.image.name)
            thumb_filename = f"{name}_thumb.jpg"
            
            # Save the thumbnail
            self.thumbnail.save(
                os.path.basename(thumb_filename),
                ContentFile(thumb_io.read()),
                save=False
            )
            
            # Save the model instance (without triggering infinite recursion)
            super().save(update_fields=['thumbnail'])
            
            logger.info(f"Created thumbnail for image: {self.original_filename}")
            
        except Exception as e:
            # Log error but don't fail the save
            logger.error(f"Error creating thumbnail for {self.original_filename}: {str(e)}")
    
    def get_absolute_url(self):
        return reverse('image_processing:image_detail', kwargs={'pk': self.pk})


class ImageProcessingJob(models.Model):
    """Track wedding venue transformation jobs with SD3.5 Large parameters"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, related_name='processing_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Wedding-specific fields - updated to support 50+ themes and 5 core spaces
    wedding_theme = models.CharField(max_length=50, choices=WEDDING_THEMES, null=True, blank=True)
    space_type = models.CharField(max_length=20, choices=SPACE_TYPES, null=True, blank=True)
    
    # Dynamic wedding parameters
    guest_count = models.CharField(max_length=20, blank=True, help_text="Guest count category")
    budget_level = models.CharField(max_length=20, blank=True, help_text="Budget level")
    season = models.CharField(max_length=20, blank=True, help_text="Wedding season")
    time_of_day = models.CharField(max_length=20, blank=True, help_text="Time of day")
    color_scheme = models.CharField(max_length=30, blank=True, help_text="Color scheme")
    custom_colors = models.CharField(max_length=200, blank=True, help_text="Custom colors")
    
    # NEW: Religion/Culture for culturally-relevant elements
    religion_culture = models.CharField(max_length=30, blank=True, help_text="Religion or cultural background for appropriate elements")
    
    additional_details = models.TextField(blank=True, null=True, help_text="Additional user-specified details")
    
    # NEW: User-defined negative prompt (things to avoid/remove)
    user_negative_prompt = models.TextField(blank=True, null=True, help_text="User-specified things to avoid or remove from the transformation")
    
    # Generated prompts
    generated_prompt = models.TextField(blank=True, null=True, help_text="Generated AI prompt for this job")
    negative_prompt = models.TextField(blank=True, null=True, help_text="Final negative prompt combining system and user preferences")
    
    # SD3.5 Large parameters
    cfg_scale = models.FloatField(default=7.0, help_text="How strictly the diffusion process adheres to the prompt text (1.0-20.0)")
    steps = models.IntegerField(default=50, help_text="Number of diffusion steps to run (10-150)")
    seed = models.BigIntegerField(blank=True, null=True, help_text="Random noise seed for generation")
    aspect_ratio = models.CharField(max_length=10, default='1:1', help_text="Aspect ratio (not used in image-to-image mode - maintains original dimensions)")
    strength = models.FloatField(default=0.4, help_text="How much the input image influences the output (0.0-1.0)")
    output_format = models.CharField(max_length=10, default='png', help_text="Output image format")
    
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
        """Override save to generate prompt if needed"""
        # Generate space-first prompt if wedding theme and space type are provided
        if self.wedding_theme and self.space_type and not self.generated_prompt:
            try:
                # Pass all the optional parameters to the prompt generator
                prompt_data = generate_wedding_prompt_with_dynamics(
                    wedding_theme=self.wedding_theme,
                    space_type=self.space_type,
                    guest_count=self.guest_count or None,  # Convert empty string to None
                    budget_level=self.budget_level or None,
                    season=self.season or None,
                    time_of_day=self.time_of_day or None,
                    color_scheme=self.color_scheme or None,
                    custom_colors=self.custom_colors or None,
                    additional_details=self.additional_details or None
                )
                
                self.generated_prompt = prompt_data['prompt']
                self.negative_prompt = prompt_data['negative_prompt']
                
                # Update parameters with recommendations for SD3.5 Large
                recommended_params = prompt_data['recommended_params']
                self.strength = recommended_params.get('strength', self.strength)
                self.cfg_scale = recommended_params.get('cfg_scale', self.cfg_scale)
                self.steps = recommended_params.get('steps', self.steps)
                self.output_format = recommended_params.get('output_format', self.output_format)
                
                logger.info(f"Generated space-first prompt for job {self.id}: {self.generated_prompt[:100]}...")
                
            except Exception as e:
                logger.error(f"Error generating space-first prompt for job {self.id}: {str(e)}")
                # Set a basic prompt as fallback
                theme_name = dict(WEDDING_THEMES).get(self.wedding_theme, self.wedding_theme)
                space_name = dict(SPACE_TYPES).get(self.space_type, self.space_type)
                self.generated_prompt = f"Transform this space into a beautiful {space_name} for a {theme_name} wedding, professional wedding photography, high quality, elegant decoration"
                self.negative_prompt = "people, faces, crowd, guests, blurry, low quality, dark, messy"
        
        # Call the parent save method
        super().save(*args, **kwargs)
    
    def get_stability_ai_params(self):
        """Get all parameters formatted for Stability AI Stable Image Ultra API call"""
        params = {
            'prompt': self.generated_prompt,
            'negative_prompt': self.negative_prompt,
            'strength': self.strength,
            'output_format': self.output_format,
        }
        
        # Add optional parameters for Ultra
        if self.cfg_scale:
            params['cfg_scale'] = self.cfg_scale
        if self.steps:
            params['steps'] = self.steps
        if self.seed:
            params['seed'] = self.seed
            
        return params


class ProcessedImage(models.Model):
    """Store processed wedding venue images - permanently saved"""
    processing_job = models.ForeignKey(ImageProcessingJob, on_delete=models.CASCADE, related_name='processed_images')
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
        return f"Wedding Transformation - Job {self.processing_job.id}"


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
    """User favorites for wedding transformations - processed images only"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    processed_image = models.ForeignKey('ProcessedImage', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'processed_image']
        ordering = ['-created_at']
    
    def __str__(self):
        job = self.processed_image.processing_job
        theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, 'Unknown') if job.wedding_theme else 'Unknown'
        space_display = dict(SPACE_TYPES).get(job.space_type, 'Unknown') if job.space_type else 'Unknown'
        return f"{self.user.username} ❤️ {theme_display} {space_display}"
    
    @property
    def image_url(self):
        """Get the processed image URL"""
        return self.processed_image.processed_image.url
    
    @property
    def image_title(self):
        """Get a display title for the transformation"""
        job = self.processed_image.processing_job
        theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, 'Unknown')
        space_display = dict(SPACE_TYPES).get(job.space_type, 'Unknown')
        return f"{theme_display} {space_display}"


class PromptTemplate(models.Model):
    """Admin-manageable prompt templates for wedding transformations"""
    
    TEMPLATE_TYPES = [
        ('theme', 'Wedding Theme Template'),
        ('space', 'Space Type Template'),
        ('guest_modifier', 'Guest Count Modifier'),
        ('budget_modifier', 'Budget Level Modifier'),
        ('season_modifier', 'Season Modifier'),
        ('time_modifier', 'Time of Day Modifier'),
        ('color_modifier', 'Color Scheme Modifier'),
        ('religion_modifier', 'Religion/Culture Modifier'),
        ('base_prompt', 'Base Prompt Template'),
        ('negative_prompt', 'Negative Prompt Template'),
    ]
    
    name = models.CharField(max_length=100, help_text="Descriptive name for this template")
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    identifier = models.CharField(max_length=50, help_text="Unique identifier (e.g., 'rustic', 'budget', 'spring', 'hindu')")
    
    # Prompt content
    prompt_text = models.TextField(help_text="The actual prompt text. Use {variables} for dynamic content.")
    description = models.TextField(blank=True, help_text="Description of what this template does")
    
    # Settings
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher priority templates are used first")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Parameters for SD3.5 Large optimization
    recommended_strength = models.FloatField(default=0.4, help_text="Recommended transformation strength for this template")
    recommended_cfg_scale = models.FloatField(default=7.0, help_text="Recommended CFG scale for this template")
    recommended_steps = models.IntegerField(default=50, help_text="Recommended steps for this template")
    
    class Meta:
        ordering = ['-priority', 'name']
        unique_together = ['template_type', 'identifier']
    
    def __str__(self):
        return f"{self.get_template_type_display()}: {self.name}"


class PromptVariation(models.Model):
    """Different variations of the same prompt for A/B testing"""
    
    template = models.ForeignKey(PromptTemplate, related_name='variations', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    prompt_text = models.TextField(help_text="Alternative prompt text")
    
    # Performance tracking
    usage_count = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(default=0.0, help_text="Success rate based on user ratings")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-success_rate', '-usage_count']
    
    def __str__(self):
        return f"{self.template.name} - {self.name}"


class GenerationPreset(models.Model):
    """Pre-configured settings for different types of generations"""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Default parameters for SD3.5 Large
    default_strength = models.FloatField(default=0.4)
    default_cfg_scale = models.FloatField(default=7.0)
    default_steps = models.IntegerField(default=50)
    
    # Theme and space combinations this preset works well with
    compatible_themes = models.JSONField(default=list, help_text="List of wedding themes this preset works well with")
    compatible_spaces = models.JSONField(default=list, help_text="List of space types this preset works well with")
    
    # Usage context
    recommended_for_guest_counts = models.JSONField(default=list, help_text="Guest count categories this works well for")
    recommended_for_budgets = models.JSONField(default=list, help_text="Budget levels this works well for")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class ProcessingJobEnhanced(models.Model):
    """Enhanced processing job with dynamic parameters"""
    
    # Link to existing job
    base_job = models.OneToOneField('ImageProcessingJob', on_delete=models.CASCADE, related_name='enhanced_data')
    
    # Dynamic parameters
    guest_count = models.CharField(max_length=20, blank=True, help_text="intimate, medium, large, grand")
    budget_level = models.CharField(max_length=20, blank=True, help_text="budget, moderate, luxury")
    season = models.CharField(max_length=20, blank=True, help_text="spring, summer, fall, winter")
    time_of_day = models.CharField(max_length=20, blank=True, help_text="morning, afternoon, evening, night")
    color_scheme = models.CharField(max_length=30, blank=True, help_text="Color scheme choice")
    custom_colors = models.CharField(max_length=200, blank=True, help_text="Custom color specification")
    religion_culture = models.CharField(max_length=30, blank=True, help_text="Religion or cultural background")
    
    # Generation options
    generate_variations = models.BooleanField(default=False)
    used_preset = models.ForeignKey(GenerationPreset, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Prompt tracking
    used_prompt_templates = models.ManyToManyField(PromptTemplate, blank=True)
    final_compiled_prompt = models.TextField(blank=True, help_text="The final prompt sent to AI")
    
    def get_dynamic_context(self):
        """Get all dynamic parameters as a context dictionary"""
        return {
            'guest_count': self.guest_count,
            'budget_level': self.budget_level,
            'season': self.season,
            'time_of_day': self.time_of_day,
            'color_scheme': self.color_scheme,
            'custom_colors': self.custom_colors,
            'religion_culture': self.religion_culture,
            'wedding_theme': self.base_job.wedding_theme,
            'space_type': self.base_job.space_type,
            'additional_details': self.base_job.additional_details,
            'user_negative_prompt': self.base_job.user_negative_prompt,
        }