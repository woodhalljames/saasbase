# image_processing/forms.py - Updated to remove batch processing
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
    """Simplified form for wedding venue transformation with advanced options"""
    
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
    
    # Additional details
    additional_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any specific details you want to include? (e.g., "add more flowers", "brighter lighting", "vintage furniture")'
        }),
        label="Additional Details (Optional)",
        help_text="Describe any specific elements you want to emphasize"
    )
    
    # Advanced Stability AI Parameters
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
    
    cfg_scale = forms.FloatField(
        initial=7.0,
        min_value=1.0,
        max_value=20.0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'type': 'range'
        }),
        label="Style Precision",
        help_text="How precisely to follow the style description (1-20, default: 7)"
    )
    
    steps = forms.IntegerField(
        initial=50,
        min_value=20,
        max_value=100,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'type': 'range'
        }),
        label="Processing Quality",
        help_text="Higher values = better quality but slower processing (20-100, default: 50)"
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
        
        self.fields['cfg_scale'].widget.attrs.update({
            'data-display-target': 'cfgValue',
            'oninput': 'updateRangeDisplay(this)'
        })
        
        self.fields['steps'].widget.attrs.update({
            'data-display-target': 'stepsValue',
            'oninput': 'updateRangeDisplay(this)'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that required basic fields are provided
        wedding_theme = cleaned_data.get('wedding_theme')
        space_type = cleaned_data.get('space_type')
        
        if not wedding_theme:
            raise ValidationError("Please select a wedding theme.")
        
        if not space_type:
            raise ValidationError("Please select a venue space type.")
        
        # Validate advanced parameters
        strength = cleaned_data.get('strength', 0.35)
        if strength < 0.1 or strength > 0.9:
            raise ValidationError("Transformation strength must be between 0.1 and 0.9")
        
        cfg_scale = cleaned_data.get('cfg_scale', 7.0)
        if cfg_scale < 1.0 or cfg_scale > 20.0:
            raise ValidationError("Style precision must be between 1.0 and 20.0")
        
        return cleaned_data
    
    def get_processing_parameters(self):
        """Get all parameters formatted for processing job creation"""
        if not self.is_valid():
            return None
        
        return {
            'wedding_theme': self.cleaned_data['wedding_theme'],
            'space_type': self.cleaned_data['space_type'],
            'additional_details': self.cleaned_data.get('additional_details', ''),
            'strength': self.cleaned_data.get('strength', 0.35),
            'cfg_scale': self.cleaned_data.get('cfg_scale', 7.0),
            'steps': self.cleaned_data.get('steps', 50),
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
    
    # Quality preset
    QUALITY_PRESETS = [
        ('fast', 'Fast (Good quality, 30 seconds)'),
        ('balanced', 'Balanced (High quality, 60 seconds)'),
        ('premium', 'Premium (Best quality, 2 minutes)'),
    ]
    
    quality_preset = forms.ChoiceField(
        choices=QUALITY_PRESETS,
        initial='balanced',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label="Processing Quality"
    )
    
    def get_preset_parameters(self, preset):
        """Get parameters based on quality preset"""
        presets = {
            'fast': {
                'steps': 25,
                'cfg_scale': 6.0,
                'strength': 0.3,
            },
            'balanced': {
                'steps': 50,
                'cfg_scale': 7.0,
                'strength': 0.35,
            },
            'premium': {
                'steps': 75,
                'cfg_scale': 8.0,
                'strength': 0.4,
            }
        }
        return presets.get(preset, presets['balanced'])
    
    def get_processing_parameters(self):
        """Get parameters with preset applied"""
        if not self.is_valid():
            return None
        
        preset_params = self.get_preset_parameters(
            self.cleaned_data.get('quality_preset', 'balanced')
        )
        
        return {
            'wedding_theme': self.cleaned_data['wedding_theme'],
            'space_type': self.cleaned_data['space_type'],
            'additional_details': '',
            **preset_params
        }