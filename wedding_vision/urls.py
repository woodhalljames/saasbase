# wedding_vision/urls.py
from django.urls import path
from . import views

app_name = 'wedding_vision'

urlpatterns = [
    path('', views.venue_list, name='index'),
    path('venues/', views.venue_list, name='venue_list'),
    path('venues/upload/', views.venue_upload, name='venue_upload'),
    path('venues/<int:venue_id>/', views.venue_detail, name='venue_detail'),
    path('venues/<int:venue_id>/themes/', views.theme_selection, name='theme_selection'),
    path('venues/<int:venue_id>/generate/<int:theme_id>/', views.generate_image, name='generate_image'),
    path('generations/<int:generation_id>/', views.preview_image, name='preview_image'),
    path('generations/<int:generation_id>/save/', views.save_image, name='save_image'),
    path('generations/<int:generation_id>/feedback/', views.image_feedback, name='image_feedback'),
    path('gallery/', views.gallery, name='gallery'),
]