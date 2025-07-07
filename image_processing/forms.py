# image_processing/forms.py - Enhanced with dynamic inputs
from django import forms
from django.core.exceptions import ValidationError
from .models import UserImage, WEDDING_THEMES, SPACE_TYPES

# Enhanced choices for dynamic features
GUEST_COUNT_CHOICES = [
    ('', 'Select guest count...'),
    ('intimate', 'Intimate (1-50 guests)'),
    ('medium', 'Medium (51-150 guests)'),
    ('large', 'Large (151-300 guests)'),
    ('grand', 'Grand (300+ guests)'),
]

BUDGET_CHOICES = [
    ('', 'Select budget level...'),
    ('budget', 'Budget-Friendly'),
    ('moderate', 'Moderate'),
    ('luxury', 'Luxury'),
    ('ultra_luxury', 'Ultra Luxury'),
]

SEASON_CHOICES = [
    ('', 'Select season...'),
    ('spring', 'Spring'),
    ('summer', 'Summer'),
    ('fall', 'Fall'),
    ('winter', 'Winter'),
]

TIME_OF_DAY_CHOICES = [
    ('', 'Select time...'),
    ('morning', 'Morning Ceremony'),
    ('afternoon', 'Afternoon'),
    ('evening', 'Evening/Sunset'),
    ('night', 'Night'),
]

COLOR_SCHEME_CHOICES = [
    ('', 'Select color scheme...'),
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


class WeddingTransformForm(forms.Form):
    """Enhanced form for wedding venue transformation with dynamic options"""
    
    # Core wedding options
    wedding_theme = forms.ChoiceField(
        choices=[('', 'Choose wedding style...')] + WEDDING_THEMES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'wedding-theme'
        })
    )
    
    space_type = forms.ChoiceField(
        choices=[('', 'Choose space type...')] + SPACE_TYPES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'space-type'
        })
    )
    
    # Dynamic options
    guest_count = forms.ChoiceField(
        choices=GUEST_COUNT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'guest-count'
        })
    )
    
    budget_level = forms.ChoiceField(
        choices=BUDGET_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'budget-level'
        })
    )
    
    season = forms.ChoiceField(
        choices=SEASON_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'season'
        })
    )
    
    time_of_day = forms.ChoiceField(
        choices=TIME_OF_DAY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'time-of-day'
        })
    )
    
    color_scheme = forms.ChoiceField(
        choices=COLOR_SCHEME_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'color-scheme'
        })
    )
    
    custom_colors = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'custom-colors',
            'placeholder': 'e.g., blush pink, sage green, gold accents',
            'style': 'display: none;'  # Hidden by default, shown when custom is selected
        })
    )
    
    additional_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'additional-details',
            'rows': 3,
            'placeholder': 'Any specific details you want to include? (e.g., outdoor ceremony, string lights, rustic tables)'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        color_scheme = cleaned_data.get('color_scheme')
        custom_colors = cleaned_data.get('custom_colors')
        
        # If custom color scheme is selected, custom_colors should be provided
        if color_scheme == 'custom' and not custom_colors:
            raise ValidationError("Please specify your custom colors when 'Custom Colors' is selected.")
        
        return cleaned_data