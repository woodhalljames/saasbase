from django.urls import path
from . import views

app_name = 'image_processing'

urlpatterns = [
    # Main Studio (combined upload and processing)
    path('', views.upload_image, name='dashboard'),  # Main studio page
    path('upload/', views.upload_image, name='upload'),  # Alias for compatibility
    
    # Image management  
    path('gallery/', views.image_gallery, name='image_gallery'),
    path('image/<int:pk>/', views.image_detail, name='image_detail'),
    
    # Processing
    path('image/<int:pk>/process/', views.process_image, name='process_image'),
    path('job/<int:job_id>/status/', views.job_status, name='job_status'),
    path('history/', views.processing_history, name='processing_history'),
    
    # Processed images
    path('processed/<int:pk>/', views.processed_image_detail, name='processed_image_detail'),
    
    # Themes
    path('themes/', views.themes_list, name='themes_list'),
    
    # Collections
    path('collections/', views.collections_list, name='collections_list'),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/<int:collection_id>/', views.collection_detail, name='collection_detail'),
    path('collections/add/', views.add_to_collection, name='add_to_collection'),
    path('collections/remove/', views.remove_from_collection, name='remove_from_collection'),
    
    # Ratings & Favorites
    path('rate/', views.rate_image, name='rate_image'),
    path('favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    
    # Sharing
    path('share/<str:image_type>/<int:image_id>/', views.share_image, name='share_image'),
]