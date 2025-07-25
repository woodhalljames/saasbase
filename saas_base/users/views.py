# Update saas_base/users/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db.models import QuerySet
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from django.views import View

from saas_base.users.models import User
from .forms import UserUpdateForm, PasswordSetupForm


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "users/user_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add wedding page information
        try:
            from wedding_shopping.models import CoupleProfile
            context['user_couple_profile'] = CoupleProfile.objects.get(user=self.object)
        except (ImportError, CoupleProfile.DoesNotExist):
            context['user_couple_profile'] = None
        
        # Add recent transformations
        try:
            from image_processing.models import ProcessedImage
            context['recent_transformations'] = ProcessedImage.objects.filter(
                processing_job__user_image__user=self.object,
                is_saved=True
            ).order_by('-created_at')[:4]
        except (ImportError, AttributeError):
            context['recent_transformations'] = []
        
        return context


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_message = _("Profile updated successfully")
    template_name = "users/user_update_form.html"

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None=None) -> User:
        assert self.request.user.is_authenticated
        return self.request.user


class PasswordSetupView(LoginRequiredMixin, View):
    """View for social users to set up a password"""
    template_name = "users/password_setup.html"
    
    def get(self, request):
        if not request.user.needs_password_setup():
            messages.info(request, "You already have a password set up.")
            return redirect('users:detail', username=request.user.username)
        
        form = PasswordSetupForm(request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = PasswordSetupForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password set up successfully! You can now login with username/email and password.")
            return redirect('users:detail', username=user.username)
        return render(request, self.template_name, {'form': form})


user_update_view = UserUpdateView.as_view()
password_setup_view = PasswordSetupView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        # Check if user has an active subscription
        if hasattr(self.request.user, 'subscription') and self.request.user.has_active_subscription():
            return reverse("users:detail", kwargs={"username": self.request.user.username})
        
        # Check if there's a specific price_id from signup
        price_id = self.request.session.pop('subscription_price_id', None)
        if price_id:
            return f"{reverse('subscriptions:pricing')}?checkout={price_id}"
        
        return reverse("subscriptions:pricing")


user_redirect_view = UserRedirectView.as_view()

