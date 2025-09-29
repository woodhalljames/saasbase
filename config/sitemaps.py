from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from wedding_shopping.models import CoupleProfile
from newsletter.models import BlogPost


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 1.0
    changefreq = 'monthly'
    
    def items(self):
        return ['home', 'about', 'subscriptions:pricing']
    
    def location(self, item):
        return reverse(item)


class WeddingPageSitemap(Sitemap):
    """Sitemap for public wedding pages"""
    changefreq = 'weekly'
    priority = 0.9
    
    def items(self):
        return CoupleProfile.objects.filter(is_public=True).order_by('-updated_at')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class BlogPostSitemap(Sitemap):
    """Sitemap for blog posts"""
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
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
        return ['wedding_shopping:public_couples_list', 'newsletter:blog_list']
    
    def location(self, item):
        return reverse(item)