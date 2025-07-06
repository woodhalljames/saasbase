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
