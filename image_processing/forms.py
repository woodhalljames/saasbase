# image_processing/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import UserImage, PromptTemplate, Collection


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
            # Check file size (max 5MB for MVP)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large. Maximum size is 5MB.")
            
            # Check file type
            if not image.content_type.startswith('image/'):
                raise ValidationError("File must be an image.")
                
        return image


class BulkImageUploadForm(forms.Form):
    """Form for bulk image upload - MVP version"""
    
    images = forms.FileField(
        widget=forms.FileInput(attrs={  # Changed from ClearableFileInput to FileInput
            'class': 'form-control',
            'multiple': True,  # This enables multiple file selection
            'accept': 'image/*'
        }),
        help_text="Select multiple wedding photos (max 5MB each, up to 10 photos)"
    )
    
    def clean_images(self):
        files = self.files.getlist('images')
        
        if not files:
            raise ValidationError("Please select at least one image.")
        
        # MVP limits: 10 files max
        if len(files) > 10:
            raise ValidationError("You can upload a maximum of 10 images at once.")
        
        # Check each file
        for file in files:
            # MVP limit: 5MB per file (more reasonable for wedding photos)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError(f"'{file.name}' is too large. Maximum size is 5MB per image.")
            
            # Ensure it's an image
            if not file.content_type.startswith('image/'):
                raise ValidationError(f"'{file.name}' is not an image file.")
        
        return files


class ImageProcessingForm(forms.Form):
    """Form for configuring wedding space visualization"""
    
    prompts = forms.ModelMultipleChoiceField(
        queryset=PromptTemplate.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select wedding styles to visualize your space"
    )
    
    cfg_scale = forms.FloatField(
        initial=7.0,
        min_value=1.0,
        max_value=20.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5'
        }),
        help_text="Style strength (1-20, default: 7)"
    )
    
    steps = forms.IntegerField(
        initial=50,
        min_value=10,
        max_value=150,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Processing quality (10-150, default: 50)"
    )
    
    seed = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Leave empty for random'
        }),
        help_text="Random seed for consistent results (optional)"
    )


class PromptFilterForm(forms.Form):
    """Form for filtering wedding styles"""
    
    category = forms.ChoiceField(
        choices=[('', 'All Styles')] + PromptTemplate.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search wedding styles...'
        })
    )


class CollectionForm(forms.ModelForm):
    """Form for creating wedding inspiration collections"""
    
    class Meta:
        model = Collection
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. "Rustic Barn Wedding", "Garden Party"...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your wedding vision...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Collection Name',
            'description': 'Wedding Vision (Optional)',
            'is_public': 'Share with other couples'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.user:
            # Check for duplicate names for this user (excluding current instance)
            existing = Collection.objects.filter(
                user=self.user, 
                name__iexact=name
            )
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError("You already have a collection with this name.")
        
        return name