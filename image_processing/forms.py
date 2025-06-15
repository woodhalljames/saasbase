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
            # Check file size (max 10MB)
            if image.size > 10 * 1024 * 1024:
                raise ValidationError("Image file too large. Maximum size is 10MB.")
            
            # Check file type
            if not image.content_type.startswith('image/'):
                raise ValidationError("File must be an image.")
                
        return image


class BulkImageUploadForm(forms.Form):
    """Form for bulk image upload"""
    
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'multiple': True,
            'accept': 'image/*'
        }),
        help_text="Select multiple images (max 10MB each)"
    )
    
    def clean_images(self):
        files = self.files.getlist('images')
        
        if len(files) > 20:  # Limit to 20 files at once
            raise ValidationError("You can upload a maximum of 20 images at once.")
        
        for file in files:
            if file.size > 10 * 1024 * 1024:
                raise ValidationError(f"File {file.name} is too large. Maximum size is 10MB.")
            
            if not file.content_type.startswith('image/'):
                raise ValidationError(f"File {file.name} is not an image.")
        
        return files


class ImageProcessingForm(forms.Form):
    """Form for configuring image processing"""
    
    prompts = forms.ModelMultipleChoiceField(
        queryset=PromptTemplate.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text="Select up to your tier's limit of prompts"
    )
    
    cfg_scale = forms.FloatField(
        initial=7.0,
        min_value=1.0,
        max_value=20.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5'
        }),
        help_text="How strictly the AI follows the prompt (1-20, default: 7)"
    )
    
    steps = forms.IntegerField(
        initial=50,
        min_value=10,
        max_value=150,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Number of steps for generation (10-150, default: 50)"
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
    """Form for filtering prompts"""
    
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + PromptTemplate.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search prompts...'
        })
    )


class CollectionForm(forms.ModelForm):
    """Form for creating and editing collections"""
    
    class Meta:
        model = Collection
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Collection name...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
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