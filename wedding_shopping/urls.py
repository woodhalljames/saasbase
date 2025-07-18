from django.urls import path
from . import views

app_name = 'wedding_shopping'

urlpatterns = [
    # Single dashboard/management page (create or edit)
    path('', views.couple_dashboard, name='dashboard'),
    path('manage/', views.CoupleProfileManageView.as_view(), name='manage_wedding_page'),
    
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