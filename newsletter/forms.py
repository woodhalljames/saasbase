from django import forms
from .models import NewsletterSubscription


class NewsletterSignupForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control bg-transparent border-light-subtle text-white newsletter-email-input',
                'placeholder': 'Enter your email',
                'aria-label': 'Email address',
                'required': True,
                'style': 'backdrop-filter: blur(10px);'
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        
        if NewsletterSubscription.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError("You're already subscribed to our newsletter!")
        
        return email
