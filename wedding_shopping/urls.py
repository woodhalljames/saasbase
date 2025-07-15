# wedding_shopping/urls.py
from django.urls import path
from . import views

app_name = 'wedding_shopping'

urlpatterns = [
    # Dashboard and management
    path('', views.couple_dashboard, name='dashboard'),
    path('create/', views.CoupleProfileCreateView.as_view(), name='couple_create'),
    path('manage/<int:pk>/', views.CoupleProfileUpdateView.as_view(), name='couple_manage'),
    
    # Public couple pages
    path('couple/<uuid:share_token>/', views.PublicCoupleDetailView.as_view(), name='public_couple'),
    path('couple/<slug:slug>/', views.PublicCoupleDetailView.as_view(), name='public_couple_slug'),
    
    # Simple redirects and tracking
    path('registry/<int:pk>/', views.registry_redirect, name='registry_redirect'),
    path('couple/<int:pk>/view/', views.couple_detail_redirect, name='couple_redirect'),
    
    # API endpoints
    path('api/collections/', views.get_collections_api, name='api_collections'),
    
    # Optional discovery page
    path('discover/', views.public_couples_list, name='public_couples_list'),
]