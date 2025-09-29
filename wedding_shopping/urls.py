from django.urls import path
from . import views

app_name = 'wedding_shopping'

urlpatterns = [
    # Management pages (login required)
    path('wedding/dashboard/', views.couple_dashboard, name='dashboard'),
    path('wedding/manage/', views.CoupleProfileManageView.as_view(), name='manage_wedding_page'),
    path('wedding/create/', views.CoupleProfileManageView.as_view(), name='couple_create'),
    
    # Discovery page 
    path('discover/', views.public_couples_list, name='public_couples_list'),
    
    # Link tracking
    path('link/<int:pk>/', views.wedding_link_redirect, name='wedding_link_redirect'),
    
    # Token-based URL (for sharing private pages)
    path('w/<uuid:share_token>/', views.PublicCoupleDetailView.as_view(), name='wedding_page_token'),
    
    # Note: Root-level slug URLs are handled in main urls.py
]
