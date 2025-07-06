# image_processing/forms.py - Enhanced with dynamic inputs
from django import forms
from django.core.exceptions import ValidationError
from .models import UserImage, WEDDING_THEMES, SPACE_TYPES

# New choices for enhanced features
GUEST_COUNT_CHOICES = [
    ('intimate', 'Intimate (1-50 guests)'),
    ('medium', 'Medium (51-150 guests)'),
    ('large', 'Large (151-300 guests)'),
    ('grand', 'Grand (300+ guests)'),
]

BUDGET_CHOICES = [
    ('budget', 'Budget-Friendly'),
    ('moderate', 'Moderate'),
    ('luxury', 'Luxury'),
    ('ultra_luxury', 'Ultra Luxury'),
]

SEASON_CHOICES = [
    ('spring', 'Spring'),
    ('summer', 'Summer'),
    ('fall', 'Fall'),
    ('winter', 'Winter'),
]

TIME_OF_DAY_CHOICES = [
    ('morning', 'Morning Ceremony'),
    ('afternoon', 'Afternoon'),
    ('evening', 'Evening/Sunset'),
    ('night', 'Night'),
]

COLOR_SCHEME_CHOICES = [
    ('neutral', 'Neutral (Whites, Creams, Beiges)'),
    ('pastels', 'Soft Pastels'),
    ('jewel_tones', 'Rich Jewel Tones'),
    ('earth_tones', 'Earth Tones'),
    ('monochrome', 'Black & White'),
    ('bold_colors', 'Bold & Vibrant'),
    ('custom', 'Custom Colors'),
]


class ImageUploadForm(forms.ModelForm):
    """Simplified form for single image upload"""
    
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
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large. Maximum size is 5MB.")
            
            # Check file type
            if not image.content_type.startswith('image/'):
                raise ValidationError("File must be an image.")
                
        return image


class EnhancedWeddingTransformForm(forms.Form):
    """Enhanced form with dynamic inputs for comprehensive wedding venue transformation"""
    
    # Basic wedding configuration
    wedding_theme = forms.ChoiceField(
        choices=WEDDING_THEMES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'wedding-theme'
        }),
        label="Wedding Style",
        help_text="Choose the overall style and aesthetic for your venue"
    )
    
    space_type = forms.ChoiceField(
        choices=SPACE_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'space-type'
        }),
        label="Venue Space",
        help_text="Select the type of space you want to transform"
    )
    
    # NEW: Dynamic inputs
    guest_count = forms.ChoiceField(
        choices=GUEST_COUNT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'guest-count'
        }),
        label="Expected Guest Count",
        help_text="This affects table arrangements and space layout"
    )
    
    budget_level = forms.ChoiceField(
        choices=BUDGET_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'budget-level'
        }),
        label="Budget Level",
        help_text="Influences decoration quality and style complexity"
    )
    
    season = forms.ChoiceField(
        choices=SEASON_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'season'
        }),
        label="Wedding Season",
        help_text="Affects flower choices and decoration elements",
        required=False
    )
    
    time_of_day = forms.ChoiceField(
        choices=TIME_OF_DAY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'time-of-day'
        }),
        label="Time of Day",
        help_text="Influences lighting and atmosphere",
        required=False
    )
    
    color_scheme = forms.ChoiceField(
        choices=COLOR_SCHEME_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'color-scheme'
        }),
        label="Preferred Color Scheme",
        help_text="Choose your preferred color palette",
        required=False
    )
    
    custom_colors = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., blush pink, gold, sage green',
            'id': 'custom-colors'
        }),
        label="Custom Colors",
        help_text="Specify custom colors if 'Custom Colors' is selected above"
    )
    
    # Additional details
    additional_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any specific requirements? (e.g., "wheelchair accessible", "outdoor cocktail area", "live band space")'
        }),
        label="Special Requirements (Optional)",
        help_text="Describe any specific needs or preferences"
    )
    
    # Generation options
    generate_variations = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'generate-variations'
        }),
        label="Generate Multiple Variations",
        help_text="Create 3 different style variations (uses 3 credits)"
    )
    
    # Advanced Stability AI Parameters (collapsed by default)
    strength = forms.FloatField(
        initial=0.35,
        min_value=0.1,
        max_value=0.9,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.05',
            'type': 'range'
        }),
        label="Transformation Strength",
        help_text="How much to change the original image (0.1=subtle, 0.9=dramatic)"
    )
    
    aspect_ratio = forms.ChoiceField(
        choices=[
            ('1:1', 'Square (1:1)'),
            ('16:9', 'Widescreen (16:9)'),
            ('4:3', 'Standard (4:3)'),
            ('3:2', 'Photo (3:2)'),
        ],
        initial='1:1',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label="Aspect Ratio",
        help_text="Choose the image dimensions"
    )
    
    seed = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave empty for random results',
        }),
        label="Random Seed (Optional)",
        help_text="Use same number for reproducible results"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Set up field attributes for better UX
        self._setup_field_attributes()
    
    def _setup_field_attributes(self):
        """Setup additional field attributes for better user experience"""
        
        # Add data attributes for JavaScript interactions
        self.fields['strength'].widget.attrs.update({
            'data-display-target': 'strengthValue',
            'oninput': 'updateRangeDisplay(this)'
        })
        
        # Hide custom colors initially
        self.fields['custom_colors'].widget.attrs.update({
            'style': 'display: none;'
        })

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that required basic fields are provided
        wedding_theme = cleaned_data.get('wedding_theme')
        space_type = cleaned_data.get('space_type')
        guest_count = cleaned_data.get('guest_count')
        budget_level = cleaned_data.get('budget_level')
        
        if not wedding_theme:
            raise ValidationError("Please select a wedding theme.")
        
        if not space_type:
            raise ValidationError("Please select a venue space type.")
        
        if not guest_count:
            raise ValidationError("Please select expected guest count.")
        
        if not budget_level:
            raise ValidationError("Please select a budget level.")
        
        # Validate custom colors if custom color scheme is selected
        color_scheme = cleaned_data.get('color_scheme')
        custom_colors = cleaned_data.get('custom_colors')
        
        if color_scheme == 'custom' and not custom_colors:
            raise ValidationError("Please specify custom colors when 'Custom Colors' is selected.")
        
        # Validate strength parameter
        strength = cleaned_data.get('strength', 0.35)
        if strength < 0.1 or strength > 0.9:
            raise ValidationError("Transformation strength must be between 0.1 and 0.9")
        
        return cleaned_data
    
    def get_processing_parameters(self):
        """Get all parameters formatted for processing job creation"""
        if not self.is_valid():
            return None
        
        return {
            # Basic parameters
            'wedding_theme': self.cleaned_data['wedding_theme'],
            'space_type': self.cleaned_data['space_type'],
            
            # Dynamic parameters
            'guest_count': self.cleaned_data['guest_count'],
            'budget_level': self.cleaned_data['budget_level'],
            'season': self.cleaned_data.get('season', ''),
            'time_of_day': self.cleaned_data.get('time_of_day', ''),
            'color_scheme': self.cleaned_data.get('color_scheme', ''),
            'custom_colors': self.cleaned_data.get('custom_colors', ''),
            
            # Details
            'additional_details': self.cleaned_data.get('additional_details', ''),
            'generate_variations': self.cleaned_data.get('generate_variations', False),
            
            # Technical parameters
            'strength': self.cleaned_data.get('strength', 0.35),
            'aspect_ratio': self.cleaned_data.get('aspect_ratio', '1:1'),
            'seed': self.cleaned_data.get('seed'),
        }


class QuickTransformForm(forms.Form):
    """Simplified form for quick transformations with preset parameters"""
    
    wedding_theme = forms.ChoiceField(
        choices=WEDDING_THEMES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg'
        }),
        label="Wedding Style"
    )
    
    space_type = forms.ChoiceField(
        choices=SPACE_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg'
        }),
        label="Venue Space"
    )
    
    guest_count = forms.ChoiceField(
        choices=GUEST_COUNT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Guest Count"
    )
    
    budget_level = forms.ChoiceField(
        choices=BUDGET_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Budget Level"
    )
    
    def get_processing_parameters(self):
        """Get parameters with preset optimizations"""
        if not self.is_valid():
            return None
        
        return {
            'wedding_theme': self.cleaned_data['wedding_theme'],
            'space_type': self.cleaned_data['space_type'],
            'guest_count': self.cleaned_data['guest_count'],
            'budget_level': self.cleaned_data['budget_level'],
            'additional_details': '',
            'strength': 0.35,
            'aspect_ratio': '1:1',
            'generate_variations': False,
        }