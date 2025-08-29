# image_processing/forms.py - Simplified for core functionality
from django import forms
from django.core.exceptions import ValidationError
from .models import UserImage, ImageProcessingJob, WEDDING_THEMES, SPACE_TYPES, COLOR_SCHEMES

# Essential Choices - Simplified
SEASON_CHOICES = [
    ('', 'Any season'),
    ('spring', 'Spring'),
    ('summer', 'Summer'),
    ('fall', 'Fall'),
    ('winter', 'Winter'),
]

# Simplified lighting choices - more intuitive options
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


class ImageUploadForm(forms.ModelForm):
    """Simple, effective image upload with venue details"""
    
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
                'placeholder': 'Any special features we should know about? (optional)',
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
        self.fields['venue_description'].help_text = "Describe architectural features, views, or special elements"
    
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


class WeddingTransformForm(forms.ModelForm):
    """Simplified wedding transformation form - core functionality only"""
    
    # Override season and lighting with custom choices
    season = forms.ChoiceField(
        choices=SEASON_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'season',
        })
    )
    
    lighting = forms.ChoiceField(
        choices=LIGHTING_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'lighting',
        })
    )
    
    class Meta:
        model = ImageProcessingJob
        fields = [
            'wedding_theme', 'space_type', 'season', 'lighting',
            'color_scheme', 'special_features', 'avoid'
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
            'special_features': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'id': 'special-features',
                'rows': 2,
                'placeholder': 'e.g., cathedral ceilings, fireplace, historic details, outdoor views'
            }),
            'avoid': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'id': 'avoid',
                'rows': 2,
                'placeholder': 'e.g., dark colors, modern furniture, artificial flowers, minimalist style'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add empty choices for required fields
        self.fields['wedding_theme'].choices = [('', 'Choose your style...')] + list(WEDDING_THEMES)
        self.fields['space_type'].choices = [('', 'What will this space be?')] + list(SPACE_TYPES)
        self.fields['color_scheme'].choices = [('', 'Theme default')] + list(COLOR_SCHEMES)
        
        # Set required fields
        self.fields['wedding_theme'].required = True
        self.fields['space_type'].required = True
        
        # Make other fields optional
        for field_name in ['season', 'lighting', 'color_scheme', 'special_features', 'avoid']:
            self.fields[field_name].required = False
        
        # Add help text
        self.fields['wedding_theme'].help_text = 'Choose the overall style and feeling for your wedding'
        self.fields['space_type'].help_text = 'What type of wedding space is this?'
        self.fields['season'].help_text = 'Wedding season (optional)'
        self.fields['lighting'].help_text = 'Preferred lighting atmosphere (optional)'
        self.fields['color_scheme'].help_text = 'Preferred color palette (optional)'
        self.fields['special_features'].help_text = 'Highlight any special architectural features'
        self.fields['avoid'].help_text = 'Elements you definitely want to avoid'
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure we have the required fields
        if not cleaned_data.get('wedding_theme'):
            raise ValidationError("Wedding style is required.")
        
        if not cleaned_data.get('space_type'):
            raise ValidationError("Space type is required.")
        
        return cleaned_data


# Export simplified choices for use in other modules
__all__ = [
    'ImageUploadForm',
    'WeddingTransformForm',
    'SEASON_CHOICES',
    'LIGHTING_CHOICES',
]