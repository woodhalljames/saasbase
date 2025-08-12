# image_processing/forms.py - Updated to ensure all options are available

from django import forms
from django.core.exceptions import ValidationError
from .models import UserImage, WEDDING_THEMES, SPACE_TYPES

# Enhanced Guest Count Options - More descriptive
GUEST_COUNT_CHOICES = [
    ('', 'Select expected guests'),
    ('intimate', 'Intimate (1-50 guests) - Close family & friends'),
    ('medium', 'Medium (51-150 guests) - Traditional size'),
    ('large', 'Large (151-300 guests) - Extended celebration'),
    ('grand', 'Grand (300+ guests) - Spectacular gala'),
]

# Enhanced Budget Options - Clearer descriptions
BUDGET_CHOICES = [
    ('', 'Select budget level'),
    ('budget', 'Budget-Friendly - Creative DIY elegance'),
    ('moderate', 'Moderate - Professional quality'),
    ('luxury', 'Luxury - Premium everything'),
    ('ultra_luxury', 'Ultra Luxury - No limits spectacular'),
]

# Season Options
SEASON_CHOICES = [
    ('', 'Select season'),
    ('spring', 'Spring - Fresh blooms & renewal'),
    ('summer', 'Summer - Bright & vibrant'),
    ('fall', 'Fall/Autumn - Rich harvest colors'),
    ('winter', 'Winter - Elegant & cozy'),
]

# Time of Day Options
TIME_OF_DAY_CHOICES = [
    ('', 'Select time of day'),
    ('morning', 'Morning - Sunrise to noon'),
    ('afternoon', 'Afternoon - Golden daylight'),
    ('evening', 'Evening - Sunset magic hour'),
    ('night', 'Night - Stars & candlelight'),
]

# Enhanced Color Schemes
COLOR_SCHEME_CHOICES = [
    ('', 'Use theme default colors'),
    ('neutral', 'Neutral Elegance - Whites, creams, beiges'),
    ('pastels', 'Soft Pastels - Romantic & dreamy'),
    ('jewel_tones', 'Jewel Tones - Rich & luxurious'),
    ('earth_tones', 'Earth Tones - Natural & organic'),
    ('monochrome', 'Black & White - Classic contrast'),
    ('bold_colors', 'Bold & Vibrant - Energetic celebration'),
    ('custom', 'My Custom Palette - Specify below'),
]


class ImageUploadForm(forms.ModelForm):
    """Enhanced image upload with better validation"""
    
    class Meta:
        model = UserImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control form-control-lg',
                'accept': 'image/jpeg,image/jpg,image/png,image/webp',
                'id': 'id_image',
            })
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if image:
            # 10MB max for high quality
            if image.size > 10 * 1024 * 1024:
                raise ValidationError("Image too large. Maximum size is 10MB for best quality.")
            
            # Check content type
            if not image.content_type.startswith('image/'):
                raise ValidationError("File must be an image.")
            
            # Support modern formats
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if image.content_type.lower() not in allowed_formats:
                raise ValidationError("Supported formats: JPEG, PNG, WebP")
                
        return image


class WeddingTransformForm(forms.Form):
    """Complete wedding transformation form with all options"""
    
    # ESSENTIAL - Always visible
    wedding_theme = forms.ChoiceField(
        choices=[('', 'Choose your wedding style...')] + WEDDING_THEMES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'wedding-theme',
        }),
        help_text='Select the overall aesthetic and style for your wedding'
    )
    
    space_type = forms.ChoiceField(
        choices=[('', 'What will this space become?')] + SPACE_TYPES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'space-type',
        }),
        help_text='Choose the function this space will serve at your wedding'
    )
    
    # DYNAMIC OPTIONS - All available
    guest_count = forms.ChoiceField(
        choices=GUEST_COUNT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'guest-count',
        }),
        help_text='Expected number of guests affects space layout and scale'
    )
    
    budget_level = forms.ChoiceField(
        choices=BUDGET_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'budget-level',
        }),
        help_text='Budget level influences decoration complexity and materials'
    )
    
    season = forms.ChoiceField(
        choices=SEASON_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'season',
        }),
        help_text='Season affects flowers, colors, and atmosphere'
    )
    
    time_of_day = forms.ChoiceField(
        choices=TIME_OF_DAY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'time-of-day',
        }),
        help_text='Time of day influences lighting and ambiance'
    )
    
    color_scheme = forms.ChoiceField(
        choices=COLOR_SCHEME_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'color-scheme',
        }),
        help_text='Override theme colors with your preference'
    )
    
    custom_colors = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'id': 'custom-colors',
            'placeholder': 'e.g., dusty rose, sage green, gold accents, ivory',
        }),
        help_text='Describe your custom color palette'
    )
    
    additional_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-sm',
            'id': 'additional-details',
            'rows': 3,
            'placeholder': 'Any specific elements? (e.g., "include fairy lights", "add photo display area", "space for live band")'
        }),
        help_text='Special requests or specific elements you want included'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        color_scheme = cleaned_data.get('color_scheme')
        custom_colors = cleaned_data.get('custom_colors')
        
        # Validate custom colors
        if color_scheme == 'custom' and not custom_colors:
            raise ValidationError({
                'custom_colors': "Please specify your custom colors when 'My Custom Palette' is selected."
            })
        
        return cleaned_data
    
    def get_theme_description(self, theme):
        """Get a rich description of the selected theme"""
        theme_descriptions = {
            'rustic': 'Warm farmhouse charm with mason jars, burlap, and wildflowers',
            'modern': 'Sleek contemporary elegance with clean lines and minimalist beauty',
            'vintage': 'Timeless romance with antique details and old-world charm',
            'bohemian': 'Free-spirited artistic celebration with eclectic natural elements',
            'classic': 'Traditional ballroom elegance with formal sophistication',
            'garden': 'Natural floral paradise with botanical beauty',
            'beach': 'Coastal paradise with ocean breeze romance',
            'industrial': 'Urban warehouse chic with raw architectural beauty',
            'japanese_zen': 'Serene minimalist harmony with cherry blossoms',
            'indian_palace': 'Opulent maharaja celebration with vibrant colors',
            'moroccan_nights': 'Exotic Arabian fantasy with rich patterns',
            'french_chateau': 'Versailles-inspired grandeur and romance',
            'italian_villa': 'Tuscan warmth with Mediterranean abundance',
            'scottish_highland': 'Celtic traditions with dramatic Highland beauty',
            'mexican_fiesta': 'Vibrant celebration with colorful papel picado',
            'chinese_dynasty': 'Imperial elegance with red and gold prosperity',
            'winter_wonderland': 'Magical ice palace with sparkling beauty',
            'autumn_harvest': 'Rich fall colors with cozy abundance',
            'spring_awakening': 'Fresh blooms and renewal energy',
            'summer_solstice': 'Sun-drenched celebration with vibrant energy',
            'fairy_tale': 'Enchanted castle with storybook magic',
            'great_gatsby': 'Art Deco glamour with champagne and jazz',
        }
        return theme_descriptions.get(theme, 'Beautiful wedding celebration')
    
    def get_space_description(self, space):
        """Get a rich description of the selected space"""
        space_descriptions = {
            'wedding_ceremony': 'Sacred ceremony space with processional aisle and guest seating',
            'dance_floor': 'Entertainment area with professional dance floor and party lighting',
            'dining_area': 'Elegant dining hall for wedding feast and toasts',
            'cocktail_hour': 'Social mingling space with bars and appetizers',
            'lounge_area': 'Comfortable relaxation area for intimate conversations',
        }
        return space_descriptions.get(space, 'Wedding celebration space')


class SmartSuggestionForm(forms.Form):
    """Form for AI-powered smart suggestions based on selections"""
    
    def get_smart_suggestions(self, theme, space_type):
        """Get intelligent suggestions based on theme and space combination"""
        
        suggestions = {
            # Rustic combinations
            'rustic_wedding_ceremony': {
                'guest_count': 'medium',
                'budget_level': 'moderate',
                'season': 'fall',
                'time_of_day': 'afternoon',
                'color_scheme': 'earth_tones',
                'suggestion': 'Barn ceremony with hay bale seating, wildflower aisle, mason jar lighting'
            },
            'rustic_dining_area': {
                'guest_count': 'medium',
                'budget_level': 'moderate',
                'season': 'fall',
                'color_scheme': 'earth_tones',
                'suggestion': 'Farm tables with burlap runners, mason jar centerpieces, string lights overhead'
            },
            
            # Modern combinations
            'modern_wedding_ceremony': {
                'guest_count': 'large',
                'budget_level': 'luxury',
                'time_of_day': 'evening',
                'color_scheme': 'monochrome',
                'suggestion': 'Minimalist altar with geometric backdrop, lucite chairs, architectural lighting'
            },
            'modern_dance_floor': {
                'guest_count': 'large',
                'budget_level': 'luxury',
                'time_of_day': 'night',
                'color_scheme': 'monochrome',
                'suggestion': 'LED dance floor, intelligent lighting, minimalist lounge areas'
            },
            
            # Beach combinations
            'beach_wedding_ceremony': {
                'guest_count': 'medium',
                'season': 'summer',
                'time_of_day': 'evening',
                'color_scheme': 'neutral',
                'suggestion': 'Sunset ceremony with driftwood arbor, flowing fabrics, tiki torches'
            },
            
            # Garden combinations
            'garden_wedding_ceremony': {
                'guest_count': 'medium',
                'season': 'spring',
                'time_of_day': 'afternoon',
                'color_scheme': 'pastels',
                'suggestion': 'Garden bower with cascading flowers, butterfly release, natural beauty'
            },
            
            # Add more combinations as needed
        }
        
        key = f"{theme}_{space_type}"
        return suggestions.get(key, {
            'suggestion': 'Create your perfect wedding vision with this beautiful combination'
        })