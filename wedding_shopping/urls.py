# wedding_shopping/urls.py
from django.urls import path
from . import views

app_name = 'wedding_shopping'

urlpatterns = [
    # Shopping mode for a processed image (main entry point - requires token)
    path('shopping-mode/<int:processed_image_id>/', views.shopping_mode, name='shopping_mode'),
    
    # Shopping list management
    path('shopping-lists/', views.shopping_lists_view, name='shopping_lists'),
    path('shopping-list/<int:list_id>/', views.shopping_list_detail, name='shopping_list_detail'),
    path('shopping-list/<int:list_id>/delete/', views.delete_shopping_list, name='delete_shopping_list'),
    
    # AJAX endpoints for shopping functionality (no additional tokens required)
    path('analyze-selection/', views.analyze_selection, name='analyze_selection'),
    path('search-retailers/<int:item_id>/', views.search_retailers, name='search_retailers'),
    
    # Public registry
    path('registry/<uuid:share_token>/', views.public_shopping_list, name='public_shopping_list'),
]