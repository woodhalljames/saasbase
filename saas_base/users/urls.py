from django.urls import path
from .views import user_detail_view, user_redirect_view, user_update_view, password_setup_view
app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("~password-setup/", view=password_setup_view, name="password_setup"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
