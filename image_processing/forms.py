from django import forms
from django.core.exceptions import ValidationError
from .models import UserImage, WEDDING_THEMES, SPACE_TYPES

# Core Essential Choices - Most Impact
ESSENTIAL_GUEST_COUNT_CHOICES = [
    ('', 'Any size'),
    ('intimate', 'Intimate (1-50)'),
    ('medium', 'Medium (51-150)'),
    ('large', 'Large (151-300)'),
    ('grand', 'Grand (300+)'),
]

ESSENTIAL_BUDGET_CHOICES = [
    ('', 'Any budget'),
    ('budget', 'Budget-Friendly'),
    ('moderate', 'Moderate'),
    ('luxury', 'Luxury'),
    ('ultra_luxury', 'Ultra Luxury'),
]

# Contextual Choices - Shown Based on Theme/Space
CONTEXTUAL_SEASON_CHOICES = [
    ('', 'Any season'),
    ('spring', 'Spring'),
    ('summer', 'Summer'),
    ('fall', 'Fall'),
    ('winter', 'Winter'),
]

CONTEXTUAL_TIME_CHOICES = [
    ('', 'Any time'),
    ('morning', 'Morning'),
    ('afternoon', 'Afternoon'),
    ('evening', 'Evening'),
    ('night', 'Night'),
]

STREAMLINED_COLOR_CHOICES = [
    ('', 'Theme default'),
    ('neutral', 'Neutral (whites, creams)'),
    ('pastels', 'Soft Pastels'),
    ('jewel_tones', 'Rich Jewel Tones'),
    ('earth_tones', 'Earth Tones'),
    ('monochrome', 'Black & White'),
    ('bold_colors', 'Bold & Vibrant'),
    ('custom', 'My Custom Colors'),
]


class ImageUploadForm(forms.ModelForm):
    """Simple, effective image upload"""
    
    class Meta:
        model = UserImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control form-control-lg',
                'accept': 'image/*',
                'id': 'id_image',
            })
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if image:
            # 10MB max for better quality
            if image.size > 10 * 1024 * 1024:
                raise ValidationError("Image too large. Maximum size is 10MB.")
            
            if not image.content_type.startswith('image/'):
                raise ValidationError("File must be an image.")
            
            # Support modern formats
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if image.content_type.lower() not in allowed_formats:
                raise ValidationError("Supported formats: JPEG, PNG, WebP")
                
        return image


class WeddingTransformForm(forms.Form):
    """Streamlined wedding transformation form following UX best practices"""
    
    # ESSENTIAL - Always visible, biggest impact
    wedding_theme = forms.ChoiceField(
        choices=[('', 'Choose your style...')] + WEDDING_THEMES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'wedding-theme',
        })
    )
    
    space_type = forms.ChoiceField(
        choices=[('', 'What will this space be?')] + SPACE_TYPES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'space-type',
        })
    )
    
    # SECONDARY - Hidden by default, high impact when specified
    guest_count = forms.ChoiceField(
        choices=ESSENTIAL_GUEST_COUNT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'guest-count',
        })
    )
    
    budget_level = forms.ChoiceField(
        choices=ESSENTIAL_BUDGET_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'budget-level',
        })
    )
    
    color_scheme = forms.ChoiceField(
        choices=STREAMLINED_COLOR_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'color-scheme',
        })
    )
    
    custom_colors = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'id': 'custom-colors',
            'placeholder': 'e.g., blush pink, sage green, gold accents',
        })
    )
    
    # CONTEXTUAL - Only shown when relevant based on theme/space
    season = forms.ChoiceField(
        choices=CONTEXTUAL_SEASON_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'season',
        })
    )
    
    time_of_day = forms.ChoiceField(
        choices=CONTEXTUAL_TIME_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'time-of-day',
        })
    )
    
    # PERSONALIZATION - Optional details
    additional_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-sm',
            'id': 'additional-details',
            'rows': 2,
            'placeholder': 'Any specific elements you want to include?'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        color_scheme = cleaned_data.get('color_scheme')
        custom_colors = cleaned_data.get('custom_colors')
        
        # Validate custom colors
        if color_scheme == 'custom' and not custom_colors:
            raise ValidationError("Please specify your custom colors when 'My Custom Colors' is selected.")
        
        return cleaned_data
    
    def get_contextual_fields(self, theme, space_type):
        """Return which contextual fields should be shown based on theme/space"""
        show_season = False
        show_time = False
        
        # Show season for outdoor/natural themes
        outdoor_themes = ['garden', 'beach', 'rustic', 'bohemian']
        outdoor_spaces = ['garden', 'rooftop', 'beach', 'vineyard']
        
        if theme in outdoor_themes or space_type in outdoor_spaces:
            show_season = True
        
        # Show time for ceremonies and outdoor spaces
        ceremony_spaces = ['wedding_ceremony', 'garden', 'beach', 'rooftop']
        if space_type in ceremony_spaces or theme in outdoor_themes:
            show_time = True
        
        return {
            'show_season': show_season,
            'show_time': show_time
        }
    
    def get_smart_suggestions(self, theme, space_type):
        """Get AI-powered suggestions based on theme/space combination"""
        suggestions = {
            'rustic_reception_area': {
                'guest_count': 'medium',
                'budget_level': 'moderate',
                'season': 'fall',
                'color_scheme': 'earth_tones',
                'description': 'Medium guest count, moderate budget, fall season, earth tones'
            },
            'modern_ballroom': {
                'guest_count': 'large',
                'budget_level': 'luxury',
                'time_of_day': 'night',
                'color_scheme': 'monochrome',
                'description': 'Large guest count, luxury budget, evening time, monochrome colors'
            },
            'garden_wedding_ceremony': {
                'guest_count': 'medium',
                'budget_level': 'moderate',
                'season': 'spring',
                'time_of_day': 'afternoon',
                'color_scheme': 'pastels',
                'description': 'Medium size, spring afternoon, pastel colors'
            },
            'beach_wedding_ceremony': {
                'guest_count': 'medium',
                'season': 'summer',
                'time_of_day': 'evening',
                'color_scheme': 'neutral',
                'description': 'Summer sunset ceremony, neutral coastal colors'
            },
            'vintage_reception_area': {
                'guest_count': 'medium',
                'budget_level': 'moderate',
                'color_scheme': 'pastels',
                'description': 'Medium size, moderate budget, soft pastels'
            },
        }
        
        key = f"{theme}_{space_type}"
        return suggestions.get(key, {})


class QuickPresetForm(forms.Form):
    """Quick preset selections for common combinations"""
    
    PRESET_CHOICES = [
        ('', 'Choose a quick preset...'),
        ('rustic_reception', '🌾 Rustic Reception - Cozy barn vibes'),
        ('modern_ballroom', '✨ Modern Ballroom - Sleek elegance'),
        ('garden_ceremony', '🌸 Garden Ceremony - Natural beauty'),
        ('beach_sunset', '🌅 Beach Sunset - Coastal romance'),
        ('vintage_tea_party', '🫖 Vintage Tea Party - Timeless charm'),
        ('glamorous_night', '💎 Glamorous Night - Ultra luxury'),
    ]
    
    preset = forms.ChoiceField(
        choices=PRESET_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'preset-selection'
        })
    )
    
    def get_preset_parameters(self, preset_value):
        """Convert preset to full parameters"""
        presets = {
            'rustic_reception': {
                'wedding_theme': 'rustic',
                'space_type': 'reception_area',
                'guest_count': 'medium',
                'budget_level': 'moderate',
                'season': 'fall',
                'time_of_day': 'evening',
                'color_scheme': 'earth_tones'
            },
            'modern_ballroom': {
                'wedding_theme': 'modern',
                'space_type': 'ballroom',
                'guest_count': 'large',
                'budget_level': 'luxury',
                'time_of_day': 'night',
                'color_scheme': 'monochrome'
            },
            'garden_ceremony': {
                'wedding_theme': 'garden',
                'space_type': 'wedding_ceremony',
                'guest_count': 'medium',
                'budget_level': 'moderate',
                'season': 'spring',
                'time_of_day': 'afternoon',
                'color_scheme': 'pastels'
            },
            'beach_sunset': {
                'wedding_theme': 'beach',
                'space_type': 'wedding_ceremony',
                'guest_count': 'medium',
                'budget_level': 'moderate',
                'season': 'summer',
                'time_of_day': 'evening',
                'color_scheme': 'neutral'
            },
            'vintage_tea_party': {
                'wedding_theme': 'vintage',
                'space_type': 'reception_area',
                'guest_count': 'intimate',
                'budget_level': 'moderate',
                'color_scheme': 'pastels'
            },
            'glamorous_night': {
                'wedding_theme': 'glamorous',
                'space_type': 'ballroom',
                'guest_count': 'large',
                'budget_level': 'ultra_luxury',
                'time_of_day': 'night',
                'color_scheme': 'jewel_tones'
            },
        }
        
        return presets.get(preset_value, {})


GUEST_COUNT_CHOICES = ESSENTIAL_GUEST_COUNT_CHOICES
BUDGET_CHOICES = ESSENTIAL_BUDGET_CHOICES
SEASON_CHOICES = CONTEXTUAL_SEASON_CHOICES
TIME_OF_DAY_CHOICES = CONTEXTUAL_TIME_CHOICES
COLOR_SCHEME_CHOICES = STREAMLINED_COLOR_CHOICES