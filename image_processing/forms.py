# image_processing/forms.py - Updated with alphabetical wedding theme sorting

from django import forms
from django.core.exceptions import ValidationError
from .models import UserImage, ImageProcessingJob, WEDDING_THEMES, SPACE_TYPES, COLOR_SCHEMES

# Essential Choices - Simplified for better UX
SEASON_CHOICES = [
    ('', 'Any season'),
    ('spring', 'Spring'),
    ('summer', 'Summer'),
    ('fall', 'Fall'),
    ('winter', 'Winter'),
]

# Simplified lighting choices for better prompts
LIGHTING_CHOICES = [
    ('', 'Automatic'),
    ('romantic', 'Romantic & Warm'),
    ('bright', 'Bright & Cheerful'),
    ('dim', 'Dim & Intimate'),
    ('dramatic', 'Dramatic & Moody'),
    ('natural', 'Natural Daylight'),
    ('golden', 'Golden Hour'),
    ('dusk', 'Dusk & Twilight'),
    ('dawn', 'Dawn & Morning'),
]

# Prompt mode choices
PROMPT_MODE_CHOICES = [
    ('guided', 'Guided Design (Recommended)'),
    ('custom', 'Custom Prompt (Advanced)'),
]


class ImageUploadForm(forms.ModelForm):
    """Image upload form with venue details"""
    
    class Meta:
        model = UserImage
        fields = ['image', 'venue_name', 'venue_description']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control form-control-lg',
                'accept': 'image/*',
                'id': 'id_image',
            }),
            'venue_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Garden Pavilion, Main Ballroom (optional)',
                'id': 'venue_name'
            }),
            'venue_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Describe special features, views, or architectural elements (optional)',
                'id': 'venue_description'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make venue fields optional
        self.fields['venue_name'].required = False
        self.fields['venue_description'].required = False
        
        # Add help text
        self.fields['venue_name'].help_text = "What do you call this space?"
        self.fields['venue_description'].help_text = "Help Gemini understand your venue better"
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if image:
            # 15MB max for high-quality Gemini processing
            if image.size > 15 * 1024 * 1024:
                raise ValidationError("Image too large. Maximum size is 15MB for best Gemini results.")
            
            if not image.content_type.startswith('image/'):
                raise ValidationError("File must be an image.")
            
            # Support modern formats that Gemini handles well
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if image.content_type.lower() not in allowed_formats:
                raise ValidationError("Supported formats: JPEG, PNG, WebP (best results with high-resolution images)")
                
        return image


class WeddingTransformForm(forms.ModelForm):
    """Updated wedding venue transformation form with single user_instructions field and alphabetical theme sorting"""
    
    # Prompt mode selection
    prompt_mode = forms.ChoiceField(
        choices=PROMPT_MODE_CHOICES,
        initial='guided',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg mb-3',
            'id': 'prompt-mode',
            'onchange': 'togglePromptMode()',
        }),
        help_text='Guided mode uses wedding themes, custom mode lets you write your own prompt'
    )
    
    # Override season and lighting with custom choices
    season = forms.ChoiceField(
        choices=SEASON_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'season',
        })
    )
    
    lighting_mood = forms.ChoiceField(
        choices=LIGHTING_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'lighting',
        })
    )
    
    # Processing preference
    realtime_processing = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'realtime-processing',
        }),
        help_text='Get results immediately (may take 30-60 seconds) instead of background processing'
    )
    
    class Meta:
        model = ImageProcessingJob
        fields = [
            'prompt_mode', 'custom_prompt',  # Prompt selection
            'wedding_theme', 'space_type', 'season', 'lighting_mood', 'color_scheme',  # Guided options
            'user_instructions',  # Single user instructions field
            'realtime_processing'  # Processing preference
        ]
        
        widgets = {
            'wedding_theme': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'wedding-theme',
            }),
            'space_type': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'space-type',
            }),
            'color_scheme': forms.Select(attrs={
                'class': 'form-select form-select-sm',
                'id': 'color-scheme',
            }),
            # Custom prompt widget
            'custom_prompt': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'custom-prompt',
                'rows': 5,
                'placeholder': 'Describe your ideal wedding venue transformation in detail. Example: "Transform this space into a romantic garden ceremony with soft pink roses, flowing white drapes, and warm golden lighting. Add vintage wooden chairs and a floral arch..."',
                'style': 'display: none;'  # Hidden by default
            }),
            # Single user instructions field with helpful placeholder
            'user_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'user-instructions',
                'rows': 3,
                'placeholder': 'Additional instructions for your transformation... For example: "Include lots of white roses and avoid dark colors" or "Add fairy lights everywhere but no artificial flowers" or "Make it very romantic with candles"'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Sort wedding themes alphabetically by display name (second element of tuple)
        sorted_wedding_themes = sorted(WEDDING_THEMES, key=lambda x: x[1])
        
        # Add empty choices for required fields (guided mode) with alphabetically sorted themes
        self.fields['wedding_theme'].choices = [('', 'Choose your wedding style...')] + list(sorted_wedding_themes)
        self.fields['space_type'].choices = [('', 'What will this space be?')] + list(SPACE_TYPES)
        
        # Sort color schemes alphabetically as well for consistency
        sorted_color_schemes = sorted(COLOR_SCHEMES, key=lambda x: x[1])
        self.fields['color_scheme'].choices = [('', 'Theme default')] + list(sorted_color_schemes)
        
        # Set field requirements (validated conditionally)
        self.fields['wedding_theme'].required = False
        self.fields['space_type'].required = False
        self.fields['custom_prompt'].required = False
        self.fields['user_instructions'].required = False
        
        # Make other fields optional
        for field_name in ['season', 'lighting_mood', 'color_scheme']:
            self.fields[field_name].required = False
        
        # Add enhanced help text for Gemini
        self.fields['wedding_theme'].help_text = 'Choose the overall style - Gemini will create detailed wedding decor (themes sorted A-Z)'
        self.fields['space_type'].help_text = 'What type of wedding area should this become?'
        self.fields['season'].help_text = 'Seasonal flowers and elements (optional)'
        self.fields['lighting_mood'].help_text = 'Lighting atmosphere (optional)'
        self.fields['color_scheme'].help_text = 'Color palette preference (optional, sorted A-Z)'
        self.fields['custom_prompt'].help_text = 'Write a detailed description of your ideal venue transformation. Gemini works best with specific, descriptive prompts.'
        
        # Enhanced help text for single user instructions field
        self.fields['user_instructions'].help_text = 'Add any specific requests, things to include or avoid. This will be added to your transformation prompt. Examples: "lots of fairy lights", "no artificial flowers", "make it very romantic", "include some greenery but avoid red colors"'
    
    def clean(self):
        cleaned_data = super().clean()
        prompt_mode = cleaned_data.get('prompt_mode', 'guided')
        
        if prompt_mode == 'guided':
            # Guided mode: require theme and space
            if not cleaned_data.get('wedding_theme'):
                self.add_error('wedding_theme', 'Wedding style is required for guided design.')
            
            if not cleaned_data.get('space_type'):
                self.add_error('space_type', 'Space type is required for guided design.')
            
            # Clear custom prompt if in guided mode
            cleaned_data['custom_prompt'] = ''
            
        elif prompt_mode == 'custom':
            # Custom mode: require custom prompt with minimum length
            custom_prompt = cleaned_data.get('custom_prompt', '').strip()
            if not custom_prompt:
                self.add_error('custom_prompt', 'Custom prompt is required for custom design mode.')
            elif len(custom_prompt) < 20:
                self.add_error('custom_prompt', 'Custom prompt is too short. Please provide more detail for better Gemini results.')
        
        # Validate user instructions length if provided
        user_instructions = cleaned_data.get('user_instructions', '').strip()
        if user_instructions:
            if len(user_instructions) > 1000:
                self.add_error('user_instructions', 'Instructions are too long (max 1000 characters).')
        
        return cleaned_data



# Export choices for use in other modules
__all__ = [
    'ImageUploadForm',
    'WeddingTransformForm', 
    'QuickTransformForm',
    'SimpleInstructionsForm',
    'SEASON_CHOICES',
    'LIGHTING_CHOICES',
    'PROMPT_MODE_CHOICES',
]