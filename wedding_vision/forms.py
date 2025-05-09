# wedding_vision/forms.py
from django import forms
from .models import VenueImage, GeneratedImage, ThemeTemplate

class VenueImageForm(forms.ModelForm):
    class Meta:
        model = VenueImage
        fields = ['title', 'description', 'image']
        
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check file type
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                raise forms.ValidationError("Only JPG, PNG and WEBP files are allowed")
            
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image size must be under 5MB")
        return image

class ThemeSelectionForm(forms.Form):
    theme = forms.ModelChoiceField(
        queryset=ThemeTemplate.objects.filter(active=True),
        empty_label=None,
        widget=forms.RadioSelect
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['theme'].label_from_instance = lambda obj: f"{obj.name} ({obj.token_cost} tokens)"