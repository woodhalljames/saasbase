# image_processing/forms.py - Aligned with models.py and prompt_generator.py

from django import forms
from django.core.exceptions import ValidationError
from .models import (
    UserImage, ImageProcessingJob, 
    WEDDING_THEMES, SPACE_TYPES, COLOR_SCHEMES,
    PORTRAIT_THEMES, PORTRAIT_SETTINGS, PORTRAIT_POSES, PORTRAIT_ATTIRE,
    SEASONS, LIGHTING_MOODS
)

# Essential Choices
SEASON_CHOICES = [('', 'Any season')] + list(SEASONS)

LIGHTING_CHOICES = [('', 'Automatic')] + list(LIGHTING_MOODS)

STUDIO_MODE_CHOICES = [
    ('venue', 'Venue Design'),
    ('portrait_wedding', 'Wedding Portrait'),
    ('portrait_engagement', 'Engagement Portrait'),
]

OUTPUT_COUNT_CHOICES = [
    (1, '1 Photo (1 Credit)'),
    (3, '3 Photos (3 Credits)'),
    (5, '5 Photos (5 Credits)'),
]


class ImageUploadForm(forms.ModelForm):
    """Image upload form with image type classification"""
    
    IMAGE_TYPE_CHOICES = [
        ('venue', 'Venue/Space Photo'),
        ('face', 'Face Photo'),
        ('reference', 'Reference (Clothing, Pet, etc.)'),
    ]
    
    image_type = forms.ChoiceField(
        choices=IMAGE_TYPE_CHOICES,
        initial='venue',
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm mb-2',
            'id': 'image_type_select'
        }),
        help_text='What type of image is this?'
    )
    
    class Meta:
        model = UserImage
        fields = ['image', 'image_type', 'venue_name', 'venue_description']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control form-control-lg',
                'accept': 'image/*',
                'id': 'id_image',
                'capture': 'environment',
            }),
            'venue_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional: Name or label for this image',
                'id': 'venue_name'
            }),
            'venue_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional: Any notes about this image',
                'id': 'venue_description'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['venue_name'].required = False
        self.fields['venue_description'].required = False
        self.fields['venue_name'].label = 'Label (Optional)'
        self.fields['venue_description'].label = 'Notes (Optional)'
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if image:
            if image.size > 15 * 1024 * 1024:
                raise ValidationError("Image too large. Maximum size is 15MB.")
            
            if not image.content_type.startswith('image/'):
                raise ValidationError("File must be an image.")
            
            allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if image.content_type.lower() not in allowed_formats:
                raise ValidationError("Supported formats: JPEG, PNG, WebP")
                
        return image


class UnifiedStudioForm(forms.ModelForm):
    """Unified form for venue and portrait studio modes - ALIGNED"""
    
    # Studio mode selection
    studio_mode = forms.ChoiceField(
        choices=STUDIO_MODE_CHOICES,
        initial='venue',
        widget=forms.RadioSelect(attrs={
            'class': 'studio-mode-radio',
        }),
        help_text='Select studio type'
    )
    
    # Output count selection
    output_count = forms.ChoiceField(
        choices=OUTPUT_COUNT_CHOICES,
        initial=1,
        widget=forms.RadioSelect(attrs={
            'class': 'output-count-radio',
            'id': 'output-count',
        }),
        help_text='More outputs = more variations but uses more credits'
    )
    
    # Shared optional fields
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
    
    color_scheme = forms.ChoiceField(
        choices=[('', 'Theme default')] + list(COLOR_SCHEMES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'color-scheme',
        })
    )
    
    user_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'user-instructions',
            'rows': 3,
            'placeholder': 'Any additional instructions or preferences...'
        })
    )
    
    custom_prompt = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'custom-prompt',
            'rows': 5,
            'placeholder': 'Write your own custom prompt for advanced control...',
            'style': 'display: none;'
        })
    )
    
    class Meta:
        model = ImageProcessingJob
        fields = [
            'studio_mode', 'output_count',
            # Venue fields
            'wedding_theme', 'space_type',
            # Portrait fields
            'photo_theme', 'setting_type', 'pose_style', 'attire_style',
            # Shared fields
            'season', 'lighting_mood', 'color_scheme',
            'user_instructions', 'custom_prompt'
        ]
        
        widgets = {
            # Venue mode widgets
            'wedding_theme': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'wedding-theme',
            }),
            'space_type': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'space-type',
            }),
            # Portrait mode widgets
            'photo_theme': forms.Select(attrs={
                'class': 'form-select form-select-sm',
                'id': 'photo-theme',
            }),
            'setting_type': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'setting-type',
            }),
            'pose_style': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'pose-style',
            }),
            'attire_style': forms.Select(attrs={
                'class': 'form-select form-select-sm',
                'id': 'attire-style',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Sort choices alphabetically (except 'use_pictured' which stays at end)
        def sort_with_use_pictured(choices):
            """Sort choices but keep 'use_pictured' at the end"""
            regular = [(k, v) for k, v in choices if k != 'use_pictured']
            use_pictured = [(k, v) for k, v in choices if k == 'use_pictured']
            return sorted(regular, key=lambda x: x[1]) + use_pictured
        
        sorted_wedding_themes = sort_with_use_pictured(WEDDING_THEMES)
        sorted_portrait_themes = sort_with_use_pictured(PORTRAIT_THEMES)
        sorted_portrait_settings = sort_with_use_pictured(PORTRAIT_SETTINGS)
        sorted_portrait_poses = sort_with_use_pictured(PORTRAIT_POSES)
        sorted_portrait_attire = sort_with_use_pictured(PORTRAIT_ATTIRE)
        sorted_color_schemes = sort_with_use_pictured(COLOR_SCHEMES)
        
        # Setup venue mode choices
        self.fields['wedding_theme'].choices = [('', 'Choose your wedding style...')] + list(sorted_wedding_themes)
        self.fields['space_type'].choices = [('', 'What will this space be?')] + list(SPACE_TYPES)
        
        # Setup portrait mode choices
        self.fields['photo_theme'].choices = [('', 'Choose theme (optional)...')] + list(sorted_portrait_themes)
        self.fields['setting_type'].choices = [('', 'Choose setting...')] + list(sorted_portrait_settings)
        self.fields['pose_style'].choices = [('', 'Choose pose/action...')] + list(sorted_portrait_poses)
        self.fields['attire_style'].choices = [('', 'Choose attire (optional)...')] + list(sorted_portrait_attire)
        
        # Setup shared choices
        self.fields['color_scheme'].choices = [('', 'Theme default')] + list(sorted_color_schemes)
        
        # Make all theme/style fields optional (validated conditionally in clean())
        for field_name in ['wedding_theme', 'space_type', 'photo_theme', 'setting_type', 
                          'pose_style', 'attire_style']:
            self.fields[field_name].required = False
        
        # Help text
        self.fields['wedding_theme'].help_text = 'Overall venue style (includes 80+ themes + "Use Pictured")'
        self.fields['space_type'].help_text = 'What type of space? ("Use Pictured" available)'
        self.fields['photo_theme'].help_text = 'Portrait style (optional, includes "Use Pictured")'
        self.fields['setting_type'].help_text = 'Where should the photo be taken? ("Use Pictured" available)'
        self.fields['pose_style'].help_text = 'How should subjects be posed? ("Use Pictured" available)'
        self.fields['attire_style'].help_text = 'Clothing style (optional, includes "Use Pictured")'
        self.fields['season'].help_text = 'Season preference ("Use Pictured" available)'
        self.fields['lighting_mood'].help_text = 'Lighting mood ("Use Pictured" available)'
        self.fields['color_scheme'].help_text = 'Color palette ("Use Pictured" available)'
        self.fields['output_count'].help_text = 'Generate multiple variations for more options'
    
    def clean(self):
        cleaned_data = super().clean()
        studio_mode = cleaned_data.get('studio_mode', 'venue')
        custom_prompt = cleaned_data.get('custom_prompt', '').strip()
        
        # If custom prompt provided, skip other validation
        if custom_prompt:
            if len(custom_prompt) < 20:
                self.add_error('custom_prompt', 'Custom prompt too short. Please provide more detail.')
            return cleaned_data
        
        # Validate based on studio mode - UPDATED: Only one field required per mode
        if studio_mode == 'venue':
            # Venue mode: require ONLY wedding style
            if not cleaned_data.get('wedding_theme'):
                self.add_error('wedding_theme', 'Wedding style is required for venue design.')
            # space_type is now optional
        
        elif studio_mode in ['portrait_wedding', 'portrait_engagement']:
            # Portrait mode: require ONLY pose/action
            if not cleaned_data.get('pose_style'):
                self.add_error('pose_style', 'Pose/action is required for portrait studio.')
            # setting_type is now optional
            # photo_theme and attire_style remain optional
        
        # Validate output count
        output_count = cleaned_data.get('output_count', 1)
        if output_count:
            try:
                output_count = int(output_count)
                if output_count < 1 or output_count > 5:
                    self.add_error('output_count', 'Output count must be between 1 and 5.')
            except (ValueError, TypeError):
                self.add_error('output_count', 'Invalid output count.')
        
        return cleaned_data

class FavoriteFaceForm(forms.Form):
    """Form for saving a face image to favorites"""
    image_id = forms.IntegerField(widget=forms.HiddenInput())
    label = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Bride, Groom, Mom, Dad',
        }),
        help_text='Optional label to identify this person'
    )


# Export choices for use in other modules
__all__ = [
    'ImageUploadForm',
    'UnifiedStudioForm',
    'FavoriteFaceForm',
    'SEASON_CHOICES',
    'LIGHTING_CHOICES',
    'STUDIO_MODE_CHOICES',
    'OUTPUT_COUNT_CHOICES',
]