# wedding_shopping/urls.py
from django.urls import path
from . import views

app_name = 'wedding_shopping'

urlpatterns = [
    # Shopping mode and item selection
    path('shop/<int:processed_image_id>/', views.shopping_mode, name='shopping_mode'),
    path('create-list/<int:processed_image_id>/', views.create_shopping_list, name='create_shopping_list'),
    
    # AI Analysis and item management
    path('analyze/', views.analyze_selection, name='analyze_selection'),
    path('search-retailers/<int:item_id>/', views.search_item_retailers, name='search_item_retailers'),
    
    # Shopping list management
    path('lists/', views.shopping_lists, name='shopping_lists'),
    path('lists/<int:pk>/', views.shopping_list_detail, name='shopping_list_detail'),
    path('lists/<int:pk>/delete/', views.delete_shopping_list, name='delete_shopping_list'),
    
    # Public registry (shareable wedding lists)
    path('registry/<uuid:share_token>/', views.public_shopping_list, name='public_shopping_list'),
    path('registry/<uuid:share_token>/purchase/<int:item_id>/', views.purchase_item, name='purchase_item'),
]