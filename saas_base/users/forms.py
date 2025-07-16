from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import SetPasswordForm

from .models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):  # type: ignore[name-defined]
        model = User


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):  # type: ignore[name-defined]  # django-stubs is missing the class, thats why the error is thrown: typeddjango/django-stubs#2555
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):  # type: ignore[name-defined]
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


# saas_base/users/forms.py
# saas_base/users/forms.py
# Update the UserSignupForm class

class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get price_id from request if it exists
        if hasattr(self, 'request') and self.request and 'price_id' in self.request.GET:
            self.price_id = self.request.GET.get('price_id')
        else:
            self.price_id = None
    
    def save(self, request):
        # Save the user as normal
        user = super().save(request)
        
        # Store the price_id in session if exists
        if hasattr(self, 'price_id') and self.price_id:
            request.session['subscription_price_id'] = self.price_id
        
        return user

# In saas_base/users/forms.py
class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Ensures username is set even for social signups.
    """
    username = forms.CharField(
        max_length=150,
        help_text="Choose a unique username for your account"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username required for social signups
        self.fields['username'].required = True
        
    def save(self, request):
        user = super().save(request)
        # Username will be saved automatically by the parent class
        return user
    
class UserUpdateForm(forms.ModelForm):
    """Enhanced form for updating user profile"""
    
    class Meta:
        model = User
        fields = ['username', 'name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'help_text': 'Letters, digits and @/./+/-/_ only.'
            }),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data['username']
        # Check if username is taken by another user
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


class PasswordSetupForm(SetPasswordForm):
    """Form for social users to set up a password"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
