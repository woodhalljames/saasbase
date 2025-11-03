# config/sitemaps.py
# OPTIMIZED VERSION with all features covered

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from wedding_shopping.models import CoupleProfile
from newsletter.models import BlogPost
from datetime import datetime


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages - High priority pages"""
    priority = 1.0
    changefreq = 'weekly'  # Changed from monthly - these pages update more often with new features
    
    def items(self):
        return [
            'home',
            'about', 
            'subscriptions:pricing',
        ]
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, obj):
        # Return current date for static pages
        return datetime.now()


class WeddingPageSitemap(Sitemap):
    """Sitemap for public wedding pages"""
    changefreq = 'weekly'
    priority = 0.9
    
    def items(self):
        # Only include public wedding pages, ordered by most recently updated
        return CoupleProfile.objects.filter(is_public=True).order_by('-updated_at')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class BlogPostSitemap(Sitemap):
    """Sitemap for blog posts/resources"""
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        # Only published blog posts, ordered by most recent
        return BlogPost.published_posts().order_by('-published_at')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class DiscoverySitemap(Sitemap):
    """Sitemap for discovery/list pages"""
    changefreq = 'daily'
    priority = 0.7
    
    def items(self):
        return [
            'wedding_shopping:public_couples_list',
            'newsletter:blog_list',
            'newsletter:resources_list',
        ]
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, obj):
        return datetime.now()


# OPTIONAL: If you create feature landing pages, add this:
class FeatureLandingSitemap(Sitemap):
    """Sitemap for feature-specific landing pages"""
    changefreq = 'monthly'
    priority = 0.85  # High priority - these are key conversion pages
    
    def items(self):
        # These URLs would need to be created
        # Return as list of URL names or paths
        return [
            # 'engagement_photos',      # /engagement-photos/
            # 'venue_design',           # /venue-design/
            # 'photo_touchup',          # /photo-touchup/
            # 'wedding_website',        # /wedding-website/
            # 'for_planners',           # /for-planners/
        ]
    
    def location(self, item):
        # If using named URLs:
        return reverse(item)
        # OR if using static paths:
        # return f'/{item}/'
    
    def lastmod(self, obj):
        return datetime.now()


# RECOMMENDED: Add a catch-all for important app pages
class AppPagesSitemap(Sitemap):
    """Sitemap for important authenticated app pages (public-facing only)"""
    changefreq = 'monthly'
    priority = 0.6
    
    def items(self):
        return [
            # Only public pages, not auth-required pages
            'account_login',
            'account_signup',
        ]
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, obj):
        return datetime.now()