# image_processing/forms.py - Updated for wedding venue processing

from django import forms
from django.core.exceptions import ValidationError
from .models import UserImage, WEDDING_THEMES, SPACE_TYPES


class ImageUploadForm(forms.ModelForm):
    """Form for single image upload"""
    
    class Meta:
        model = UserImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
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


class WeddingVisualizationForm(forms.Form):
    """Form for wedding venue visualization settings"""
    
    wedding_theme = forms.ChoiceField(
        choices=WEDDING_THEMES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'wedding-theme-select'
        }),
        label="Wedding Theme",
        help_text="Choose the overall style and aesthetic for your venue"
    )
    
    space_type = forms.ChoiceField(
        choices=SPACE_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'space-type-select'
        }),
        label="Venue Space",
        help_text="Select the type of space you want to transform"
    )
    
    # Optional advanced settings (collapsed by default)
    cfg_scale = forms.FloatField(
        initial=7.0,
        min_value=1.0,
        max_value=20.0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5'
        }),
        label="Style Strength",
        help_text="How strongly to apply the wedding theme (1-20, default: 7)"
    )
    
    steps = forms.IntegerField(
        initial=50,
        min_value=10,
        max_value=150,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Processing Quality",
        help_text="Higher values = better quality but slower processing (10-150, default: 50)"
    )
    
    seed = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave empty for random'
        }),
        label="Random Seed",
        help_text="Use same number for consistent results (optional)"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add user context for potential tier-based modifications
        self.user = user


class QuickWeddingForm(forms.Form):
    """Simplified form for quick wedding visualization"""
    
    wedding_theme = forms.ChoiceField(
        choices=WEDDING_THEMES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
        }),
        label="Wedding Style"
    )
    
    space_type = forms.ChoiceField(
        choices=SPACE_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
        }),
        label="Venue Type"
    )


# Keep existing forms for compatibility
class BulkImageUploadForm(forms.Form):
    """Form for bulk image upload - kept for backward compatibility"""
    
    images = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'multiple': True
        }),
        help_text="Select multiple wedding venue photos (max 5MB each)"
    )
    
    def clean_images(self):
        files = self.files.getlist('images')
        
        if not files:
            raise ValidationError("Please select at least one image.")
        
        # Limit to reasonable number for MVP
        if len(files) > 5:
            raise ValidationError("You can upload a maximum of 5 images at once.")
        
        # Check each file
        for file in files:
            if file.size > 5 * 1024 * 1024:
                raise ValidationError(f"'{file.name}' is too large. Maximum size is 5MB per image.")
            
            if not file.content_type.startswith('image/'):
                raise ValidationError(f"'{file.name}' is not an image file.")
        
        return files