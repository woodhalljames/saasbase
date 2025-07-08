from django.urls import path
from . import views

app_name = 'wedding_shopping'

urlpatterns = [
    path('', views.shopping_home, name='home'),
    path('shop/<uuid:session_id>/', views.shopping_home, name='session'),
    path('shop/create-session/', views.CreateShoppingSession.as_view(), name='create_session'),
    path('shop/analyze-selection/', views.AnalyzeSelection.as_view(), name='analyze_selection'),
    path('shop/add-to-list/', views.add_to_shopping_list, name='add_to_list'),
    path('registry/<str:share_url>/', views.public_registry, name='public_registry'),
]
