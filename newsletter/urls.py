from django.urls import path
from . import views
from .feeds import LatestPostsFeed, AtomSiteNewsFeed

app_name = 'newsletter'

urlpatterns = [
    # Newsletter
    path('newsletter/signup/', views.newsletter_signup, name='signup'),
    path('newsletter/unsubscribe/', views.general_unsubscribe, name='general_unsubscribe'),
    path('newsletter/unsubscribe/<str:email>/', views.unsubscribe, name='unsubscribe'),
    
    # Resources (blog)
    path('resources/', views.BlogListView.as_view(), name='resources_list'),
    path('resources/feed/rss/', LatestPostsFeed(), name='resources_rss'),
    path('resources/feed/atom/', AtomSiteNewsFeed(), name='resources_atom'),
    
    # Tags
    path('resources/tag/<slug:slug>/', views.TagPostsView.as_view(), name='tag_posts'),
    
    # Individual posts (must be last to avoid conflicts)
    path('resources/<slug:slug>/', views.BlogDetailView.as_view(), name='resource_detail'),
    path('resources/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    
    # Backwards compatibility (redirect old blog URLs)
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_post_detail'),
]