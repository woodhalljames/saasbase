# image_processing/models.py - Updated with comprehensive 50+ themes and enhanced prompt generation

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
    ('new_year_eve', 'New Year\'s Eve'),
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

SPACE_TYPES = [
    ('wedding_ceremony', 'Wedding Ceremony'),
    ('reception_area', 'Reception Area'),
    ('dance_floor', 'Dance Floor'),
    ('dinner_party', 'Dinner Party'),
    ('cocktail_hour', 'Cocktail Hour'),
    ('bridal_suite', 'Bridal Suite'),
    ('photo_backdrop', 'Photo Backdrop'),
    ('lounge_area', 'Lounge Area'),
]

def generate_wedding_prompt(theme, space_type, additional_details=None):
    """Generate comprehensive AI prompt for wedding venue transformation using advanced system"""
    try:
        from .prompt_generator import WeddingPromptGenerator
        
        return WeddingPromptGenerator.generate_dynamic_prompt(
            wedding_theme=theme, 
            space_type=space_type, 
            additional_details=additional_details
        )
    except ImportError as e:
        # Enhanced fallback prompt generation if import fails
        logger.warning(f"Could not import comprehensive WeddingPromptGenerator: {e}")
        return generate_comprehensive_fallback_prompt(theme, space_type, additional_details)


def generate_wedding_prompt_with_dynamics(wedding_theme, space_type, guest_count=None, 
                                        budget_level=None, season=None, time_of_day=None,
                                        color_scheme=None, custom_colors=None, additional_details=None):
    """Generate comprehensive AI prompt with dynamic parameters for SD3 Turbo"""
    try:
        from .prompt_generator import WeddingPromptGenerator
        
        return WeddingPromptGenerator.generate_dynamic_prompt(
            wedding_theme=wedding_theme,
            space_type=space_type,
            guest_count=guest_count,
            budget_level=budget_level,
            season=season,
            time_of_day=time_of_day,
            color_scheme=color_scheme,
            custom_colors=custom_colors,
            additional_details=additional_details
        )
    except ImportError as e:
        logger.warning(f"Could not import comprehensive WeddingPromptGenerator: {e}")
        return generate_comprehensive_fallback_prompt(wedding_theme, space_type, additional_details, guest_count)


def generate_comprehensive_fallback_prompt(theme, space_type, additional_details=None, guest_count=None):
    """Comprehensive fallback prompt generation with support for all 50+ themes"""
    
    # Comprehensive theme descriptions for all 50+ themes
    theme_descriptions = {
        # Cultural & Traditional Themes
        'japanese_zen': 'serene Japanese zen wedding with cherry blossom ceremony arch, bamboo elements, paper lanterns, minimalist wooden seating, zen garden details',
        'chinese_dynasty': 'elegant Chinese dynasty wedding with red silk draping, golden dragon decorations, traditional round tables, Chinese lanterns, jade accents',
        'indian_palace': 'magnificent Indian palace wedding with marigold garlands, intricate mandap, silk cushions, golden elephant statues, jewel-toned fabrics',
        'korean_hanbok': 'traditional Korean hanbok wedding with colorful silk ceremony arch, low wooden tables, hanbok-inspired decorations, lotus flowers',
        'thai_temple': 'exotic Thai temple wedding with golden Buddha statues, tropical flowers, ornate Thai decorations, silk draping, incense holders',
        'scottish_highland': 'rustic Scottish highland wedding with tartan details, bagpipe area, wooden ceremony arch, heather arrangements, clan banners',
        'french_chateau': 'elegant French château wedding with ornate gold details, crystal chandeliers, French provincial furniture, rose arrangements',
        'greek_island': 'stunning Greek island wedding with white and blue decorations, olive branch details, Mediterranean seating, Greek columns',
        'italian_villa': 'romantic Italian villa wedding with vineyard elements, rustic wooden details, Italian cypress arrangements, wine barrel accents',
        'english_garden': 'classic English garden wedding with rose arbors, cottage garden flowers, vintage tea service, English garden seating',
        'mexican_fiesta': 'vibrant Mexican fiesta wedding with colorful papel picado, piñata decorations, mariachi area, bright flower arrangements',
        'spanish_hacienda': 'elegant Spanish hacienda wedding with wrought iron details, terracotta elements, Spanish tile accents, fountain centerpieces',
        'brazilian_carnival': 'festive Brazilian carnival wedding with bright feathers, samba decorations, tropical flowers, carnival masks',
        'argentine_tango': 'passionate Argentine tango wedding with rose decorations, dance floor centerpiece, tango band area, elegant Argentine elements',
        'moroccan_nights': 'exotic Moroccan nights wedding with ornate lanterns, rich tapestries, low lounge seating, intricate patterns, Middle Eastern decorations',
        'arabian_desert': 'luxurious Arabian desert wedding with tent decorations, camel details, desert flowers, sand-colored elements',
        'african_safari': 'adventurous African safari wedding with animal print details, acacia tree decorations, safari elements, earth-toned flowers',
        'egyptian_royal': 'regal Egyptian royal wedding with golden pyramids, hieroglyphic details, Egyptian columns, royal blue accents',
        
        # Seasonal & Nature Themes
        'winter_wonderland': 'magical winter wonderland wedding with snow-white decorations, ice crystal elements, evergreen arrangements, winter berries',
        'spring_awakening': 'fresh spring awakening wedding with blooming flowers, pastel decorations, butterfly elements, garden growth theme',
        'summer_solstice': 'vibrant summer solstice wedding with sun decorations, bright summer flowers, solar elements, longest day theme',
        'autumn_harvest': 'cozy autumn harvest wedding with pumpkin decorations, fall leaves, harvest elements, apple details',
        'forest_enchanted': 'mystical enchanted forest wedding with tree branches, fairy lights, moss details, woodland creatures',
        'desert_bloom': 'stunning desert bloom wedding with cactus flowers, succulent arrangements, desert sunset theme, southwestern elements',
        'ocean_waves': 'flowing ocean waves wedding with wave decorations, seashell details, ocean blue theme, coastal elements',
        'mountain_vista': 'majestic mountain vista wedding with peak decorations, alpine flowers, mountain stone elements, vista views',
        'tropical_paradise': 'lush tropical paradise wedding with palm leaves, tropical flowers, paradise birds, island elements',
        
        # Modern & Contemporary Themes
        'metropolitan_chic': 'sophisticated metropolitan wedding with city skyline backdrop, urban furniture, glass elements, steel accents',
        'brooklyn_loft': 'trendy Brooklyn loft wedding with exposed brick, industrial windows, loft furniture, urban art',
        'rooftop_garden': 'elevated rooftop garden wedding with city views, container gardens, rooftop furniture, urban greenery',
        'art_deco_glam': 'glamorous art deco wedding with geometric patterns, gold accents, deco furniture, vintage glam elements',
        'scandinavian_simple': 'clean Scandinavian wedding with minimal furniture, white wood elements, simple flowers, hygge details',
        'modern_monochrome': 'striking modern monochrome wedding with black and white elements, geometric shapes, minimal furniture',
        'concrete_jungle': 'urban concrete jungle wedding with raw concrete, industrial plants, urban furniture, jungle plants',
        'glass_house': 'transparent glass house wedding with glass elements, modern transparency, clean lines, light refraction',
        
        # Fantasy & Themed Celebrations
        'enchanted_forest_fairy': 'magical enchanted fairy wedding with fairy lights, mushroom seating, woodland creatures, fairy wings',
        'princess_castle': 'royal princess castle wedding with castle towers, princess decorations, royal throne seating, crown details',
        'mermaid_lagoon': 'underwater mermaid wedding with seashell decorations, ocean plants, mermaid tail elements, underwater theme',
        'dragon_castle': 'medieval dragon castle wedding with dragon decorations, castle stones, medieval banners, knight elements',
        'unicorn_dreams': 'dreamy unicorn wedding with rainbow colors, unicorn horn details, magical flowers, dream elements',
        'hollywood_glam': 'glamorous Hollywood wedding with red carpet, movie star elements, golden statues, spotlight details',
        'broadway_musical': 'theatrical Broadway wedding with stage elements, musical decorations, theater seating, spotlight areas',
        'vintage_circus': 'whimsical vintage circus wedding with carnival decorations, circus tents, popcorn details, carnival games',
        'comic_book': 'superhero comic book wedding with comic elements, superhero decorations, pop art details, comic speech bubbles',
        
        # Holiday & Celebration Themes
        'christmas_magic': 'magical Christmas wedding with evergreen decorations, red ribbon details, Christmas lights, ornament centerpieces',
        'halloween_gothic': 'gothic Halloween wedding with dark decorations, pumpkin elements, autumn leaves, spooky details',
        'valentine_romance': 'romantic Valentine wedding with heart decorations, rose petals, romantic red elements, love details',
        'new_year_eve': 'glamorous New Year\'s Eve wedding with countdown elements, champagne details, midnight theme, celebration decorations',
        'fourth_july': 'patriotic Fourth of July wedding with American flag elements, red white blue decorations, firework details',
        'dia_muertos': 'colorful Día de los Muertos wedding with sugar skull decorations, marigold flowers, papel picado',
        'chinese_new_year': 'festive Chinese New Year wedding with dragon decorations, red lanterns, lucky elements, prosperity theme',
        'oktoberfest': 'traditional Oktoberfest wedding with beer hall decorations, pretzel details, German elements, lederhosen theme',
        'mardi_gras': 'festive Mardi Gras wedding with mask decorations, purple gold green colors, bead details, New Orleans theme',
        
        # Unique & Creative Themes
        'book_lovers': 'literary book lovers wedding with book decorations, library elements, vintage books, reading nooks',
        'music_festival': 'energetic music festival wedding with stage elements, band setup, festival decorations, music notes',
        'travel_adventure': 'adventurous travel wedding with map decorations, luggage elements, passport details, world theme',
        'wine_country': 'elegant wine country wedding with vineyard decorations, wine barrel elements, grape details, winery theme',
        'coffee_house': 'cozy coffee house wedding with coffee bean decorations, café elements, espresso details, barista theme',
        'neon_cyberpunk': 'futuristic neon cyberpunk wedding with LED decorations, cyber elements, tech details, futuristic theme',
        'steampunk_victorian': 'vintage steampunk wedding with gear decorations, Victorian elements, brass details, mechanical theme',
        'space_galaxy': 'cosmic space galaxy wedding with star decorations, planet elements, cosmic details, astronaut theme',
        'under_the_sea': 'underwater sea wedding with ocean decorations, fish elements, coral details, submarine theme',
        'secret_garden': 'mysterious secret garden wedding with hidden pathways, secret doors, garden mysteries, enchanted plants',
        
        # Vintage decades
        '1950s_diner': '1950s diner wedding with retro booths, jukebox elements, checkered floors, vintage diner decorations',
        '1960s_mod': '1960s mod wedding with geometric patterns, mod furniture, go-go decorations, psychedelic elements',
        '1970s_disco': '1970s disco wedding with mirror balls, dance floor lights, disco decorations, groovy elements',
        '1980s_neon': '1980s neon wedding with bright neon colors, synthesizer elements, new wave decorations, geometric shapes',
        '1990s_grunge': '1990s grunge wedding with flannel decorations, alternative elements, Seattle theme, indie details',
        'victorian_romance': 'elegant Victorian romance wedding with ornate furniture, lace details, romantic Victorian elements',
        'art_nouveau': 'artistic Art Nouveau wedding with flowing lines, natural motifs, artistic elements, nouveau decorations',
        'great_gatsby': 'glamorous Great Gatsby wedding with art deco elements, jazz age decorations, 1920s luxury',
        
        # Classic Popular Themes (enhanced)
        'rustic': 'rustic farmhouse wedding with wooden ceremony arch, mason jar centerpieces, burlap details, string lights, wildflowers',
        'modern': 'contemporary minimalist wedding with sleek geometric ceremony backdrop, modern acrylic chairs, clean white linens',
        'vintage': 'romantic vintage wedding with ornate ceremony backdrop, vintage lace details, antique chairs, classic rose arrangements',
        'bohemian': 'bohemian wedding with macrame ceremony backdrop, pampas grass arrangements, colorful textiles, floor cushions',
        'classic': 'timeless traditional wedding with elegant ceremony arch, formal chiavari chairs, crystal chandeliers, classic white flowers',
        'garden': 'natural garden wedding with floral ceremony arch, garden party seating, botanical centerpieces, abundant greenery',
        'beach': 'coastal beach wedding with driftwood ceremony arch, beach chairs, flowing white fabrics, seashell accents',
        'industrial': 'urban industrial wedding with metal pipe ceremony backdrop, Edison bulb lighting, exposed brick walls',
    }
    
    # Specific space setups - what the space should BECOME
    space_setups = {
        'wedding_ceremony': 'complete wedding ceremony setup with processional aisle, rows of chairs for guests, ceremonial altar or arch, unity candle area',
        'reception_area': 'elegant wedding reception with dining tables, dance floor area, head table, centerpieces, celebration lighting',
        'dance_floor': 'dedicated dance floor area with proper flooring, ambient lighting, DJ or band area, surrounding lounge seating',
        'dinner_party': 'intimate dinner party setup with elegant dining table, formal place settings, ambient lighting',
        'cocktail_hour': 'cocktail hour setup with standing tables, bar area, lounge seating, mingling space',
        'bridal_suite': 'luxurious bridal preparation suite with vanity area, mirrors, seating for bridal party',
        'photo_backdrop': 'stunning photo backdrop area with dramatic visual elements, perfect lighting',
        'lounge_area': 'comfortable lounge area with seating groups, ambient lighting, relaxation space'
    }
    
    # Guest count specifications
    guest_specs = {
        'intimate': 'seating for 15-30 guests with cozy intimate arrangement',
        'medium': 'seating for 75-100 guests with balanced arrangement',
        'large': 'seating for 150-200 guests with grand arrangement',
        'grand': 'seating for 250+ guests with spectacular arrangement'
    }
    
    # Build comprehensive prompt
    prompt_parts = [
        "professional wedding staging, photorealistic, detailed, high resolution",
        f"Transform this space into a {space_setups.get(space_type, 'beautiful wedding venue')}",
        f"beautiful {theme_descriptions.get(theme, 'elegant wedding')} style",
    ]
    
    # Add guest count if specified
    if guest_count and guest_count in guest_specs:
        prompt_parts.append(guest_specs[guest_count])
    else:
        prompt_parts.append("appropriate seating arrangement for wedding guests")
    
    # Add specific elements
    prompt_parts.extend([
        "elegant wedding setup, celebration ready",
        "complete transformation of space",
        "no people visible, empty chairs and tables ready for guests"
    ])
    
    if additional_details:
        prompt_parts.append(additional_details)
    
    main_prompt = " ".join(prompt_parts)
    
    # Enhanced negative prompt
    negative_prompt = "people, faces, crowd, guests, bride, groom, wedding party, humans, blurry, low quality, pixelated, distorted, dark, dim, messy, cluttered, text, watermark, signature, cartoon, unrealistic, artificial"
    
    return {
        'prompt': main_prompt,
        'negative_prompt': negative_prompt,
        'recommended_params': {
            'aspect_ratio': '16:9' if space_type in ['reception_area', 'dance_floor'] else '1:1',
            'strength': 0.4,  # Increased for more dramatic transformation
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
    """Track wedding venue transformation jobs with SD3 Turbo parameters"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, related_name='processing_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Wedding-specific fields - updated to support 50+ themes
    wedding_theme = models.CharField(max_length=50, choices=WEDDING_THEMES, null=True, blank=True)
    space_type = models.CharField(max_length=20, choices=SPACE_TYPES, null=True, blank=True)
    
    # Dynamic wedding parameters
    guest_count = models.CharField(max_length=20, blank=True, help_text="Guest count category")
    budget_level = models.CharField(max_length=20, blank=True, help_text="Budget level")
    season = models.CharField(max_length=20, blank=True, help_text="Wedding season")
    time_of_day = models.CharField(max_length=20, blank=True, help_text="Time of day")
    color_scheme = models.CharField(max_length=30, blank=True, help_text="Color scheme")
    custom_colors = models.CharField(max_length=200, blank=True, help_text="Custom colors")
    additional_details = models.TextField(blank=True, null=True, help_text="Additional user-specified details")
    
    # Generated prompts
    generated_prompt = models.TextField(blank=True, null=True, help_text="Generated AI prompt for this job")
    negative_prompt = models.TextField(blank=True, null=True, help_text="Negative prompt to avoid unwanted elements")
    
    # SD3 Turbo parameters (NO cfg_scale or steps)
    seed = models.BigIntegerField(blank=True, null=True, help_text="Random noise seed for generation")
    aspect_ratio = models.CharField(max_length=10, default='1:1', help_text="Aspect ratio for output image")
    strength = models.FloatField(default=0.35, help_text="How much the input image influences the output (0.0-1.0)")
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
        # Generate comprehensive prompt if wedding theme and space type are provided
        if self.wedding_theme and self.space_type and not self.generated_prompt:
            try:
                prompt_data = generate_wedding_prompt_with_dynamics(
                    wedding_theme=self.wedding_theme,
                    space_type=self.space_type,
                    guest_count=self.guest_count,
                    budget_level=self.budget_level,
                    season=self.season,
                    time_of_day=self.time_of_day,
                    color_scheme=self.color_scheme,
                    custom_colors=self.custom_colors,
                    additional_details=self.additional_details
                )
                
                self.generated_prompt = prompt_data['prompt']
                self.negative_prompt = prompt_data['negative_prompt']
                
                # Update parameters with recommendations
                recommended_params = prompt_data['recommended_params']
                self.aspect_ratio = recommended_params.get('aspect_ratio', self.aspect_ratio)
                self.strength = recommended_params.get('strength', self.strength)
                self.output_format = recommended_params.get('output_format', self.output_format)
                
                logger.info(f"Generated comprehensive prompt for job {self.id}: {self.generated_prompt[:100]}...")
                
            except Exception as e:
                logger.error(f"Error generating comprehensive prompt for job {self.id}: {str(e)}")
                # Set a basic prompt as fallback
                theme_name = dict(WEDDING_THEMES).get(self.wedding_theme, self.wedding_theme)
                self.generated_prompt = f"Transform this {self.space_type} into a beautiful {theme_name} wedding venue, professional wedding photography, high quality, elegant decoration"
                self.negative_prompt = "people, faces, crowd, guests, blurry, low quality, dark, messy"
        
        super().save(*args, **kwargs)
    
    def get_stability_ai_params(self):
        """Get all parameters formatted for Stability AI SD3 Turbo API call"""
        return {
            'prompt': self.generated_prompt,
            'negative_prompt': self.negative_prompt,
            'strength': self.strength,
            'seed': self.seed,
            'output_format': self.output_format,
        }


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
        ('base_prompt', 'Base Prompt Template'),
        ('negative_prompt', 'Negative Prompt Template'),
    ]
    
    name = models.CharField(max_length=100, help_text="Descriptive name for this template")
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    identifier = models.CharField(max_length=50, help_text="Unique identifier (e.g., 'rustic', 'budget', 'spring')")
    
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
    
    # Parameters for SD3 Turbo optimization
    recommended_strength = models.FloatField(default=0.35, help_text="Recommended transformation strength for this template")
    recommended_aspect_ratio = models.CharField(max_length=10, default='1:1', help_text="Recommended aspect ratio")
    
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
    
    # Default parameters
    default_strength = models.FloatField(default=0.35)
    default_aspect_ratio = models.CharField(max_length=10, default='1:1')
    
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
    budget_level = models.CharField(max_length=20, blank=True, help_text="budget, moderate, luxury, ultra_luxury")
    season = models.CharField(max_length=20, blank=True, help_text="spring, summer, fall, winter")
    time_of_day = models.CharField(max_length=20, blank=True, help_text="morning, afternoon, evening, night")
    color_scheme = models.CharField(max_length=30, blank=True, help_text="Color scheme choice")
    custom_colors = models.CharField(max_length=200, blank=True, help_text="Custom color specification")
    
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
            'wedding_theme': self.base_job.wedding_theme,
            'space_type': self.base_job.space_type,
            'additional_details': self.base_job.additional_details,
        }