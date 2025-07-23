from django.urls import path
from . import views

app_name = 'wedding_shopping'

urlpatterns = [
    # Management pages (login required)
    path('', views.couple_dashboard, name='dashboard'),
    path('manage/', views.CoupleProfileManageView.as_view(), name='manage_wedding_page'),
    path('create/', views.CoupleProfileManageView.as_view(), name='couple_create'),
    
    # Custom wedding pages - NEW FORMAT: /wedding/name1name2MMDDYY/
    path('<slug:slug>/', views.PublicCoupleDetailView.as_view(), name='wedding_page'),
    
    # Fallback token-based URL (for sharing before custom URL is set)
    path('token/<uuid:share_token>/', views.PublicCoupleDetailView.as_view(), name='wedding_page_token'),
    
    # Tracking and redirects
    path('registry/<int:pk>/', views.registry_redirect, name='registry_redirect'),
    
    # API endpoints
    path('api/collections/', views.get_collections_api, name='api_collections'),
    
    # Discovery page
    path('discover/', views.public_couples_list, name='public_couples_list'),
    
    # Legacy URLs for backwards compatibility (optional)
    path('couple/<slug:slug>/', views.legacy_couple_redirect, name='legacy_couple_redirect'),
    path('couple/<uuid:share_token>/', views.legacy_couple_redirect, name='legacy_couple_token_redirect'),
]