from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from wedding_shopping.views import PublicCoupleDetailView

# Import sitemaps from config.sitemaps
from config.sitemaps import (
    StaticViewSitemap, WeddingPageSitemap, 
    BlogPostSitemap, DiscoverySitemap
)
from config.views import robots_txt

# Configure sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'weddings': WeddingPageSitemap,
    'blog': BlogPostSitemap,
    'discovery': DiscoverySitemap,
}

urlpatterns = [
    # Home and static pages
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    
    # SEO files
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    
    # Django Admin
    path(settings.ADMIN_URL, admin.site.urls),
    
    # User management
    path("users/", include("saas_base.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    
    # Apps
    path("subscriptions/", include("subscriptions.urls", namespace="subscriptions")),
    path("studio/", include("image_processing.urls", namespace="image_processing")),
    
    # Newsletter and Blog
    path("", include("newsletter.urls", namespace="newsletter")),
    
    # Wedding pages (includes management pages under /wedding/)
    path("", include("wedding_shopping.urls", namespace="wedding_shopping")),
    
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

# Debug mode URLs
if settings.DEBUG:
    urlpatterns += [
        path("400/", default_views.bad_request, kwargs={"exception": Exception("Bad Request!")}),
        path("403/", default_views.permission_denied, kwargs={"exception": Exception("Permission Denied")}),
        path("404/", default_views.page_not_found, kwargs={"exception": Exception("Page not Found")}),
        path("500/", default_views.server_error),
    ]
    
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

# IMPORTANT: Root-level wedding page slugs - MUST be last
urlpatterns += [
    path('<slug:slug>/', PublicCoupleDetailView.as_view(), name='wedding_page'),
]