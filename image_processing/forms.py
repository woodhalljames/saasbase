from django import forms
from django.core.exceptions import ValidationError
from .models import UserImage, WEDDING_THEMES, SPACE_TYPES


class ImageUploadForm(forms.ModelForm):
    """Simple form for single image upload"""
    
    class Meta:
        model = UserImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'imageUpload'
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
    """Simple form for wedding venue transformation"""
    
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
    
    # Optional advanced settings (collapsed by default)
    cfg_scale = forms.FloatField(
        initial=7.0,
        min_value=1.0,
        max_value=20.0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'style': 'display: none;'  # Hidden by default
        }),
        label="Style Strength",
        help_text="How strongly to apply the wedding theme (1-20, default: 7)"
    )
    
    steps = forms.IntegerField(
        initial=50,
        min_value=10,
        max_value=150,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'display: none;'  # Hidden by default
        }),
        label="Processing Quality",
        help_text="Higher values = better quality but slower processing (10-150, default: 50)"
    )
    
    seed = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave empty for random',
            'style': 'display: none;'  # Hidden by default
        }),
        label="Random Seed",
        help_text="Use same number for consistent results (optional)"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user