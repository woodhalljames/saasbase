from django.urls import path
from . import views

app_name = 'image_processing'

urlpatterns = [
    # Main Wedding Studio
    path('', views.wedding_studio, name='wedding_studio'),
    
    # AJAX Upload endpoint
    path('upload/', views.ajax_upload_image, name='ajax_upload'),
    
    # Single Image Processing
    path('image/<int:pk>/', views.image_detail, name='image_detail'),
    path('image/<int:pk>/process/', views.process_wedding_image, name='process_wedding_image'),
    # Gallery and History
    path('gallery/', views.image_gallery, name='image_gallery'),
    path('history/', views.processing_history, name='processing_history'),
    
    # Job Status
    path('job/<int:job_id>/status/', views.job_status, name='job_status'),
    
    # Processed Images - Save/Keep functionality
    path('processed/<int:pk>/', views.processed_image_detail, name='processed_image_detail'),
    path('processed/<int:pk>/save/', views.save_processed_image, name='save_processed_image'),
    path('processed/<int:pk>/discard/', views.discard_processed_image, name='discard_processed_image'),
    
    # Collections & Favorites
    path('collections/', views.collections_list, name='collections_list'),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/<int:collection_id>/', views.collection_detail, name='collection_detail'),
    path('collections/api/', views.get_user_collections, name='get_user_collections'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('favorite/', views.toggle_favorite, name='toggle_favorite'),
]