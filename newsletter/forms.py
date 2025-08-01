from django import forms
from django.core.exceptions import ValidationError
from .models import NewsletterSubscription


class NewsletterSignupForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control newsletter-email-input',
                'placeholder': 'Enter your email',
                'aria-label': 'Email address',
                'required': True,
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        
        if not email:
            raise ValidationError("Please enter your email address.")
        
        # Check if email is already subscribed and active
        existing_subscription = NewsletterSubscription.objects.filter(email=email).first()
        
        if existing_subscription:
            if existing_subscription.is_active:
                raise ValidationError("You're already subscribed to our newsletter! Check your inbox for updates.")
            else:
                # Reactivate inactive subscription
                existing_subscription.is_active = True
                existing_subscription.save()
                raise ValidationError("Welcome back! Your subscription has been reactivated.")
        
        return email
    
    def save(self, commit=True):
        # Handle reactivation case
        email = self.cleaned_data.get('email')
        existing_subscription = NewsletterSubscription.objects.filter(email=email).first()
        
        if existing_subscription and not existing_subscription.is_active:
            # This case is handled in clean_email, but just in case
            existing_subscription.is_active = True
            if commit:
                existing_subscription.save()
            return existing_subscription
        
        # Create new subscription
        return super().save(commit=commit)