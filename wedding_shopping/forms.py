# wedding_shopping/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import CoupleProfile, SocialMediaLink, RegistryLink, WeddingPhotoCollection


class CoupleProfileForm(forms.ModelForm):
    """Form for creating/editing couple profiles"""
    
    class Meta:
        model = CoupleProfile
        fields = [
            'partner_1_name', 'partner_2_name', 'wedding_date', 
            'venue_name', 'venue_location', 'couple_photo', 
            'venue_photo', 'couple_story', 'is_public'
        ]
        widgets = {
            'partner_1_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First partner\'s name'
            }),
            'partner_2_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Second partner\'s name'
            }),
            'wedding_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'venue_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Wedding venue name'
            }),
            'venue_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, State'
            }),
            'couple_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'venue_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'couple_story': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Tell your love story... How did you meet? When did you get engaged? What are you most excited about for your wedding day?'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'couple_photo': 'Upload a photo of you as a couple',
            'venue_photo': 'Upload a photo of your wedding venue',
            'is_public': 'Allow others to find your page publicly',
        }


class SocialMediaLinkForm(forms.ModelForm):
    """Form for adding social media links"""
    
    class Meta:
        model = SocialMediaLink
        fields = ['platform', 'platform_name', 'url', 'display_name']
        widgets = {
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'platform_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Platform name (if Other selected)'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://...'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@username or display name'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        platform = cleaned_data.get('platform')
        platform_name = cleaned_data.get('platform_name')
        
        if platform == 'other' and not platform_name:
            raise ValidationError("Platform name is required when 'Other' is selected.")
        
        return cleaned_data


class RegistryLinkForm(forms.ModelForm):
    """Form for adding registry links"""
    
    class Meta:
        model = RegistryLink
        fields = ['registry_type', 'registry_name', 'original_url', 'display_name', 'description']
        widgets = {
            'registry_type': forms.Select(attrs={'class': 'form-select'}),
            'registry_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Registry name (if Other selected)'
            }),
            'original_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://registry-url...'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Display name for this registry'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What types of items are on this registry?'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        registry_type = cleaned_data.get('registry_type')
        registry_name = cleaned_data.get('registry_name')
        
        if registry_type == 'other' and not registry_name:
            raise ValidationError("Registry name is required when 'Other' is selected.")
        
        return cleaned_data


class WeddingPhotoCollectionForm(forms.ModelForm):
    """Form for linking to wedding photo collections"""
    
    class Meta:
        model = WeddingPhotoCollection
        fields = ['collection_name', 'description', 'studio_collection_id', 'is_featured']
        widgets = {
            'collection_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Our Wedding Venue Transformations'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your wedding venue transformation collection'
            }),
            'studio_collection_id': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Collection ID from Wedding Studio'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'studio_collection_id': 'The ID of your collection from the Wedding Studio (found in the collection URL)',
            'is_featured': 'Display this collection prominently on your wedding page'
        }


# Formsets for managing multiple links
SocialMediaFormSet = forms.inlineformset_factory(
    CoupleProfile, 
    SocialMediaLink, 
    form=SocialMediaLinkForm,
    extra=1, 
    can_delete=True,
    min_num=0,
    max_num=10
)

RegistryFormSet = forms.inlineformset_factory(
    CoupleProfile, 
    RegistryLink, 
    form=RegistryLinkForm,
    extra=1, 
    can_delete=True,
    min_num=0,
    max_num=10
)

PhotoCollectionFormSet = forms.inlineformset_factory(
    CoupleProfile, 
    WeddingPhotoCollection, 
    form=WeddingPhotoCollectionForm,
    extra=1, 
    can_delete=True,
    min_num=0,
    max_num=5
)