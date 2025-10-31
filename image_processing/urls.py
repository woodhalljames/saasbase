# image_processing/urls.py - COMPLETE UPDATED VERSION

from django.urls import path
from . import views

app_name = 'image_processing'

urlpatterns = [
    # Main Studio
    path('', views.wedding_studio, name='wedding_studio'),
    
    # AJAX Upload
    path('upload/', views.ajax_upload_image, name='ajax_upload'),
    
    # Favorite Uploads (⭐ star for uploaded images)
    path('favorite-upload/toggle/', views.toggle_favorite_upload, name='toggle_favorite_upload'),
    path('favorite-uploads/', views.get_favorite_uploads, name='get_favorite_uploads'),
   
    # Image Processing
    path('image/<int:pk>/', views.image_detail, name='image_detail'),
    path('image/<int:pk>/process/', views.process_wedding_image, name='process_wedding_image'),
    
    # Gallery and History
    path('history/', views.image_gallery, name='image_gallery'),
    path('visualizations/', views.processing_history, name='processing_history'),
    
    # Job Status
    path('job/<int:job_id>/status/', views.job_status, name='job_status'),
    
    # Processed Images
    path('processed/<int:pk>/', views.processed_image_detail, name='processed_image_detail'),
    path('processed/<int:pk>/delete/', views.delete_processed_image, name='delete_processed_image'),
    path('processed/<int:processed_image_id>/collections/', views.get_processed_image_collections, name='get_processed_image_collections'),
    
    # Redo transformation
    path('redo-transformation/<int:job_id>/', views.redo_transformation_with_job, name='redo_transformation_with_job'),
    
    # Get job details API
    path('job/<int:job_id>/details/', views.get_job_details, name='get_job_details'),
    
    # Collections
    path('collections/', views.collections_list, name='collections_list'),
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/<int:collection_id>/', views.collection_detail, name='collection_detail'),
    path('collections/<int:collection_id>/edit/', views.edit_collection, name='edit_collection'),
    path('collections/<int:collection_id>/delete/', views.delete_collection, name='delete_collection'),
    path('collections/<int:collection_id>/remove/<int:item_id>/', views.remove_from_collection, name='remove_from_collection'),
    path('collections/<int:collection_id>/remove-image/', views.remove_image_from_collection, name='remove_image_from_collection'),
    
    # Collection APIs
    path('collections/api/', views.get_user_collections, name='get_user_collections'),
    path('collections/add/', views.add_to_collection, name='add_to_collection'),
    path('collections/add-multiple/', views.add_to_multiple_collections, name='add_to_multiple_collections'),
    path('collections/create-ajax/', views.create_collection_ajax, name='create_collection_ajax'),
    
    # Favorites (♥ heart for processed images)
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # Images
    path('images/', views.image_gallery, name='image_gallery'),
    
    # API Endpoints
    path('api/usage-data/', views.get_usage_data, name='get_usage_data'),
    path('api/test-gemini/', views.test_gemini_api, name='test_gemini_api'),
]