# config/views.py
# OPTIMIZED robots.txt

from django.http import HttpResponse
from django.conf import settings


def robots_txt(request):
    """
    Generate robots.txt dynamically
    Optimized for SEO with clear Allow/Disallow rules
    """
    lines = [
        "# DreamWedAI Robots.txt",
        "# Generated dynamically for optimal SEO",
        "",
        "User-agent: *",
        "",
        "# ALLOW - Public pages we want indexed",
    ]
    
    # Allow indexing of main content
    lines.extend([
        "Allow: /",
        "Allow: /about/",
        "Allow: /subscriptions/pricing/",
        "",
        "# Resources & Discovery",
        "Allow: /resources/",
        "Allow: /discover/",
        "",
        "# Authentication pages (important for conversions)",
        "Allow: /accounts/login/",
        "Allow: /accounts/signup/",
        "",
        "# Future feature landing pages (uncomment when created)",
        "# Allow: /engagement-photos/",
        "# Allow: /venue-design/",
        "# Allow: /photo-touchup/",
        "# Allow: /wedding-website/",
        "# Allow: /for-planners/",
    ])
    
    lines.extend([
        "",
        "# DISALLOW - Private/Admin areas",
    ])
    
    # Disallow admin and internal paths
    lines.extend([
        "Disallow: /admin/",
        "Disallow: /studio/",          # Authenticated area
        "Disallow: /users/",           # User profiles (private)
        "Disallow: /accounts/logout/", # No need to index logout
        "Disallow: /accounts/password/", # Password reset pages
        "Disallow: /wedding/",         # Wedding management (private)
        "Disallow: /link/",            # Internal links
        "Disallow: /newsletter/",      # Newsletter management
        "Disallow: /w/",               # Token-based wedding URLs (use canonical instead)
        "",
        "# Media & Static files that shouldn't be indexed",
        "Disallow: /media/private/",
        "Disallow: /static/admin/",
        "Disallow: /static/debug_toolbar/",
    ])
    
    # Add sitemap reference
    domain = request.get_host()
    protocol = request.scheme
    lines.extend([
        "",
        "# SITEMAP",
        f"Sitemap: {protocol}://{domain}/sitemap.xml",
    ])
    
    # Crawl delay for politeness (not too high, not too low)
    lines.extend([
        "",
        "# CRAWL RATE",
        "Crawl-delay: 1",
        "",
        "# Google-specific (no delay for Google)",
        "User-agent: Googlebot",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /studio/",
        "Disallow: /users/",
        "",
        "# Bing-specific",
        "User-agent: Bingbot",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /studio/",
        "Disallow: /users/",
        "Crawl-delay: 1",
    ])
    
    return HttpResponse('\n'.join(lines), content_type='text/plain')