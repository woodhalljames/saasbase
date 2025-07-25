from django.urls import path
from . import views

app_name = 'wedding_shopping'

urlpatterns = [
    # Management pages (login required)
    path('', views.couple_dashboard, name='dashboard'),
    path('manage/', views.CoupleProfileManageView.as_view(), name='manage_wedding_page'),
    path('create/', views.CoupleProfileManageView.as_view(), name='couple_create'),
    
    # Discovery page (must come before slug pattern)
    path('discover/', views.public_couples_list, name='public_couples_list'),
    
    # Tracking and redirects
    path('registry/<int:pk>/', views.registry_redirect, name='registry_redirect'),
    
    # API endpoints
    path('api/detect-branding/', views.detect_url_branding_api, name='api_detect_branding'),
    
    # Fallback token-based URL (for sharing before custom URL is set)
    path('token/<uuid:share_token>/', views.PublicCoupleDetailView.as_view(), name='wedding_page_token'),
    
    # Legacy URLs for backwards compatibility
    path('couple/<slug:slug>/', views.legacy_couple_redirect, name='legacy_couple_redirect'),
    path('couple/<uuid:share_token>/', views.legacy_couple_redirect, name='legacy_couple_token_redirect'),
    
    # Custom wedding pages - FORMAT: /wedding/name1name2MMDDYY/ (must be last due to slug pattern)
    path('<slug:slug>/', views.PublicCoupleDetailView.as_view(), name='wedding_page'),
]