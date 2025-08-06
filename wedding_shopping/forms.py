from django import forms
from django.core.exceptions import ValidationError
from .models import CoupleProfile, SocialMediaLink, WeddingLink
import re


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
                'placeholder': 'First partner\'s name',
                'oninput': 'updateUrlPreview()'
            }),
            'partner_2_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Second partner\'s name',
                'oninput': 'updateUrlPreview()'
            }),
            'wedding_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'onchange': 'updateUrlPreview()'
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
            'partner_1_name': 'This will be used in your custom wedding URL',
            'partner_2_name': 'This will be used in your custom wedding URL',
            'wedding_date': 'This will be used in your custom wedding URL',
            'couple_photo': 'Upload a photo of you as a couple',
            'venue_photo': 'Upload a photo of your wedding venue',
            'is_public': 'Allow others to find your page publicly',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add URL preview field (read-only)
        self.fields['url_preview'] = forms.CharField(
            label='Your Wedding URL Preview',
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'id': 'url-preview',
                'placeholder': 'Your custom URL will appear here...'
            }),
            help_text='This is how your wedding page URL will look'
        )
        
        # If this is an existing object, show current URL
        if self.instance and self.instance.pk:
            self.fields['url_preview'].initial = f"yoursite.com{self.instance.wedding_url_preview}"
    
    def clean_partner_1_name(self):
        name = self.cleaned_data.get('partner_1_name', '')
        if not name or len(name.strip()) < 1:
            raise ValidationError("Partner 1 name is required.")
        return name.strip()
    
    def clean_partner_2_name(self):
        name = self.cleaned_data.get('partner_2_name', '')
        if not name or len(name.strip()) < 1:
            raise ValidationError("Partner 2 name is required.")
        return name.strip()
    
    def clean(self):
        cleaned_data = super().clean()
        name1 = cleaned_data.get('partner_1_name', '')
        name2 = cleaned_data.get('partner_2_name', '')
        
        # Check if names will create a valid URL
        if name1 and name2:
            clean1 = re.sub(r'[^a-zA-Z0-9]', '', name1.lower())[:15]
            clean2 = re.sub(r'[^a-zA-Z0-9]', '', name2.lower())[:15]
            
            if len(clean1) < 1 or len(clean2) < 1:
                raise ValidationError(
                    "Names must contain at least some letters or numbers to create a valid URL. "
                    "Special characters and spaces will be removed automatically."
                )
        
        return cleaned_data


class SocialMediaLinkForm(forms.ModelForm):
    """Simplified form for social media links - just URL and display name"""
    
    class Meta:
        model = SocialMediaLink
        fields = ['url', 'display_name']
        widgets = {
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/yourusername',
                'onblur': 'detectBrandingFromUrl(this)'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@yourusername or Handle'
            })
        }
        labels = {
            'url': 'Social Media URL',
            'display_name': 'Handle/Username'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url'].help_text = "We'll automatically detect the platform"
        self.fields['display_name'].help_text = "How this should appear (e.g., @username)"
    
    def clean_url(self):
        url = self.cleaned_data.get('url')
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url


class WeddingLinkForm(forms.ModelForm):
    """Enhanced form for all wedding-related links (registries, RSVP, livestreams, etc.)"""
    
    class Meta:
        model = WeddingLink
        fields = ['link_type', 'url', 'title', 'description']
        widgets = {
            'link_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/your-link',
                'onblur': 'detectBrandingFromUrl(this)'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Link Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description of this link (optional)'
            })
        }
        labels = {
            'link_type': 'Type',
            'url': 'URL',
            'title': 'Title',
            'description': 'Description'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['url'].help_text = "We'll automatically detect the service"
        self.fields['title'].help_text = "A friendly name for this link"
        self.fields['description'].help_text = "Additional details (optional)"
        
        # Make title required
        self.fields['title'].required = True
        
        # Add placeholder text based on link type
        self.fields['link_type'].widget.attrs.update({
            'onchange': 'updateLinkPlaceholders(this)'
        })
    
    def clean_url(self):
        url = self.cleaned_data.get('url')
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if not title or len(title.strip()) < 1:
            raise ValidationError("Title is required.")
        return title.strip()


SocialMediaFormSet = forms.inlineformset_factory(
    CoupleProfile, 
    SocialMediaLink, 
    form=SocialMediaLinkForm,
    extra=2,  # Start with 2 empty forms
    can_delete=True,
    min_num=0,
    max_num=10,  # Allow up to 10 social media links
    validate_min=False,
    validate_max=True,
    can_order=False
)

WeddingLinkFormSet = forms.inlineformset_factory(
    CoupleProfile, 
    WeddingLink, 
    form=WeddingLinkForm,
    extra=2,  # Start with 2 empty forms
    can_delete=True,
    min_num=0,
    max_num=20,  # Allow up to 20 wedding links
    validate_min=False,
    validate_max=True,
    can_order=False
)

# Backwards compatibility alias
RegistryFormSet = WeddingLinkFormSet