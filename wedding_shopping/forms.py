from django import forms
from django.core.exceptions import ValidationError
from .models import CoupleProfile, WeddingLink


class CoupleProfileForm(forms.ModelForm):
    """Simplified form for creating/editing couple profiles"""
    
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
                'required': True
            }),
            'partner_2_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Second partner\'s name',
                'required': True
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
                'placeholder': '123 Wedding Lane, Austin, TX 78701 or Austin, Texas'
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
                'rows': 5,
                'placeholder': 'Tell your love story... How did you meet? When did you get engaged? What are you most excited about for your wedding day?'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_partner_1_name(self):
        name = self.cleaned_data.get('partner_1_name', '')
        if not name or len(name.strip()) < 1:
            raise ValidationError("First partner's name is required.")
        return name.strip()
    
    def clean_partner_2_name(self):
        name = self.cleaned_data.get('partner_2_name', '')
        if not name or len(name.strip()) < 1:
            raise ValidationError("Second partner's name is required.")
        return name.strip()
    
    def clean_couple_story(self):
        story = self.cleaned_data.get('couple_story', '')
        if not story or len(story.strip()) < 10:
            raise ValidationError("Please tell us a bit about your love story (at least 10 characters).")
        return story.strip()


class WeddingLinkForm(forms.ModelForm):
    """Simplified form for wedding links"""
    
    class Meta:
        model = WeddingLink
        fields = ['title', 'url', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Site or link title'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/your-link'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Brief description of this link'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['description'].required = False
    
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


WeddingLinkFormSet = forms.inlineformset_factory(
    CoupleProfile, 
    WeddingLink, 
    form=WeddingLinkForm,
    extra=0,
    can_delete=True,
    min_num=0,
    max_num=10,
    validate_min=False,
    validate_max=True
)