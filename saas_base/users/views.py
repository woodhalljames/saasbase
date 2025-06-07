from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from saas_base.users.models import User


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None=None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        # Check if user has an active subscription
        if hasattr(self.request.user, 'subscription') and self.request.user.has_active_subscription():
            # User has subscription, go to dashboard
            return reverse("users:detail", kwargs={"username": self.request.user.username})
        
        # Check if there's a specific price_id from signup (user clicked a pricing link before signup)
        price_id = self.request.session.pop('subscription_price_id', None)
        if price_id:
            # Redirect to pricing page with auto-checkout parameter
            return f"{reverse('subscriptions:pricing')}?checkout={price_id}"
        
        # New user without subscription, go to pricing page
        return reverse("subscriptions:pricing")
