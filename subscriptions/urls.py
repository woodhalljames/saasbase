# saas_base/subscriptions/urls.py
from django.urls import path
from . import views, webhooks

app_name = "subscriptions"

urlpatterns = [
    path("checkout/", views.subscription_checkout, name="checkout"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),
    path("portal/", views.customer_portal, name="customer_portal"),
    path("", views.pricing_page, name="pricing"),
    path("webhook/", webhooks.stripe_webhook, name="webhook"),

]