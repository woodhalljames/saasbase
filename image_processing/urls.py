# image_processing/urls.py - Updated for wedding venue processing

from django.urls import path
from . import views

app_name = 'image_processing'

urlpatterns = [
    # Main Wedding Studio
    path('', views.wedding_studio, name='wedding_studio'),
    path('studio/', views.wedding_studio, name='dashboard'),  # Alias for compatibility
    
    # Wedding-specific processing
    path('image/<int:pk>/process/', views.process_wedding_image, name='process_wedding_image'),
    path('image/<int:pk>/', views.image_detail, name='image_detail'),
    
    # Gallery and history
    path('gallery/', views.image_gallery, name='image_gallery'),
    path('history/', views.processing_history, name='processing_history'),
    
    # Job status
    path('job/<int:job_id>/status/', views.job_status, name='job_status'),
    
    # Processed images
    path('processed/<int:pk>/', views.processed_image_detail, name='processed_image_detail'),
    
    # Wedding Collections (keep this feature!)
    path('collections/', views.collections_list, name='collections_list'),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/<int:collection_id>/', views.collection_detail, name='collection_detail'),
    path('collections/add/', views.add_to_collection, name='add_to_collection'),
    path('collections/remove/', views.remove_from_collection, name='remove_from_collection'),
    
    # Ratings & Favorites (keep these too!)
    path('rate/', views.rate_image, name='rate_image'),
    path('favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    
    # Sharing
    path('share/<str:image_type>/<int:image_id>/', views.share_image, name='share_image'),
    
    # Legacy redirects for backward compatibility
    path('upload/', views.wedding_studio, name='upload'),
    path('themes/', views.wedding_studio, name='themes_list'),
]