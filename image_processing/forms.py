# image_processing/forms.py - UPDATED with Composition, Emotional Tone, Activities, and Wedding Moments

from django import forms
from django.core.exceptions import ValidationError
from .models import (
    UserImage, ImageProcessingJob,
    WEDDING_THEMES, SPACE_TYPES, COLOR_SCHEMES,
    ENGAGEMENT_SETTINGS, ENGAGEMENT_ACTIVITIES,
    WEDDING_MOMENTS, WEDDING_SETTINGS, ATTIRE_STYLES,
    COMPOSITION_CHOICES, EMOTIONAL_TONE_CHOICES,
    SEASONS, LIGHTING_MOODS
)

# Essential Choices
SEASON_CHOICES = [('', 'Automatic')] + list(SEASONS)

LIGHTING_CHOICES = [('', 'Automatic')] + list(LIGHTING_MOODS)

COMPOSITION_FORM_CHOICES = [('', 'Automatic')] + list(COMPOSITION_CHOICES)

EMOTIONAL_TONE_FORM_CHOICES = [('', 'Automatic')] + list(EMOTIONAL_TONE_CHOICES)

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
    """Unified form for venue and portrait studio modes - UPDATED"""
    
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
    
    # NEW: Shared composition field
    composition = forms.ChoiceField(
        choices=COMPOSITION_FORM_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'composition',
        })
    )
    
    # NEW: Shared emotional tone field
    emotional_tone = forms.ChoiceField(
        choices=EMOTIONAL_TONE_FORM_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'emotional-tone',
        })
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
            # Engagement fields
            'engagement_setting', 'engagement_activity',
            # Wedding portrait fields
            'wedding_moment', 'wedding_setting',
            # Shared portrait fields
            'attire_style', 'composition', 'emotional_tone',
            # Other shared fields
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
            
            # Engagement portrait widgets
            'engagement_setting': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'engagement-setting',
            }),
            'engagement_activity': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'engagement-activity',
            }),
            
            # Wedding portrait widgets
            'wedding_moment': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'wedding-moment',
            }),
            'wedding_setting': forms.Select(attrs={
                'class': 'form-select form-select-lg',
                'id': 'wedding-setting',
            }),
            
            # Shared portrait widget
            'attire_style': forms.Select(attrs={
                'class': 'form-select form-select-sm',
                'id': 'attire-style',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Sort choices alphabetically (except 'na' which stays at end)
        def sort_with_na(choices):
            """Sort choices but keep 'na' at the end"""
            regular = [(k, v) for k, v in choices if k != 'na']
            na_option = [(k, v) for k, v in choices if k == 'na']
            return sorted(regular, key=lambda x: x[1]) + na_option
        
        sorted_wedding_themes = sort_with_na(WEDDING_THEMES)
        sorted_engagement_settings = sort_with_na(ENGAGEMENT_SETTINGS)
        sorted_wedding_moments = sort_with_na(WEDDING_MOMENTS)
        sorted_wedding_settings = sort_with_na(WEDDING_SETTINGS)
        sorted_attire = sort_with_na(ATTIRE_STYLES)
        sorted_color_schemes = sort_with_na(COLOR_SCHEMES)
        
        # Setup venue mode choices
        self.fields['wedding_theme'].choices = [('', 'Choose your wedding style...')] + list(sorted_wedding_themes)
        self.fields['space_type'].choices = [('', 'What will this space be? (Optional)')] + list(SPACE_TYPES)
        
        # Setup engagement portrait choices
        self.fields['engagement_setting'].choices = [('', 'Choose setting (optional)...')] + list(sorted_engagement_settings)
        self.fields['engagement_activity'].choices = [('', 'Choose activity/pose...')] + list(ENGAGEMENT_ACTIVITIES)
        
        # Setup wedding portrait choices
        self.fields['wedding_moment'].choices = [('', 'Choose moment/scene...')] + list(sorted_wedding_moments)
        self.fields['wedding_setting'].choices = [('', 'Choose location (optional)...')] + list(sorted_wedding_settings)
        
        # Setup shared portrait choices
        self.fields['attire_style'].choices = [('', 'Attire style (optional)...')] + list(sorted_attire)
        
        # Setup shared choices
        self.fields['color_scheme'].choices = [('', 'Theme default')] + list(sorted_color_schemes)
        
        # Make all fields optional (validated conditionally in clean())
        for field_name in ['wedding_theme', 'space_type', 
                          'engagement_setting', 'engagement_activity',
                          'wedding_moment', 'wedding_setting',
                          'attire_style', 'composition', 'emotional_tone']:
            self.fields[field_name].required = False
        
        # Help text
        self.fields['wedding_theme'].help_text = 'Overall venue style (80+ themes available)'
        self.fields['space_type'].help_text = 'What type of space? (Optional)'
        
        self.fields['engagement_setting'].help_text = 'Where should the photo be taken? (Optional)'
        self.fields['engagement_activity'].help_text = 'What are they doing? (150+ activities)'
        
        self.fields['wedding_moment'].help_text = 'What moment/scene to capture? (100+ moments)'
        self.fields['wedding_setting'].help_text = 'Location for the moment (Optional)'
        
        self.fields['attire_style'].help_text = 'Clothing style (Optional)'
        self.fields['composition'].help_text = 'Camera angle & framing (Optional)'
        self.fields['emotional_tone'].help_text = 'Mood & feeling of the photo (Optional)'
        self.fields['season'].help_text = 'Season preference (Optional)'
        self.fields['lighting_mood'].help_text = 'Lighting mood (Optional)'
        self.fields['color_scheme'].help_text = 'Color palette (Optional)'
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
        
        # Validate based on studio mode - only required fields per mode
        if studio_mode == 'venue':
            # Venue mode: require ONLY wedding theme
            if not cleaned_data.get('wedding_theme'):
                self.add_error('wedding_theme', 'Wedding style is required for venue design.')
        
        elif studio_mode == 'portrait_engagement':
            # Engagement mode: require ONLY activity
            if not cleaned_data.get('engagement_activity'):
                self.add_error('engagement_activity', 'Activity/pose is required for engagement portraits.')
        
        elif studio_mode == 'portrait_wedding':
            # Wedding mode: require ONLY moment/scene
            if not cleaned_data.get('wedding_moment'):
                self.add_error('wedding_moment', 'Moment/scene is required for wedding portraits.')
        
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
    'COMPOSITION_FORM_CHOICES',
    'EMOTIONAL_TONE_FORM_CHOICES',
    'STUDIO_MODE_CHOICES',
    'OUTPUT_COUNT_CHOICES',
]