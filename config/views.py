from django.http import HttpResponse
from django.conf import settings


def robots_txt(request):
    """Generate robots.txt dynamically"""
    lines = [
        "User-agent: *",
    ]
    
    # Allow indexing of main content
    lines.extend([
        "Allow: /",
        "Allow: /resources/",
        "Allow: /discover/",
        "Allow: /about/",
        "Allow: /subscriptions/pricing/",
    ])
    
    # Disallow admin and internal paths
    lines.extend([
        "Disallow: /admin/",
        "Disallow: /studio/",
        "Disallow: /users/",
        "Disallow: /accounts/",
        "Disallow: /wedding/",
        "Disallow: /link/",
        "Disallow: /newsletter/",
        "Disallow: /w/",  # Token-based wedding URLs
    ])
    
    # Disallow media/static that shouldn't be indexed
    lines.extend([
        "Disallow: /media/private/",
        "Disallow: /static/admin/",
    ])
    
    # Add sitemap reference - FIXED to use request.get_host()
    domain = request.get_host()
    protocol = request.scheme
    lines.extend([
        "",
        f"Sitemap: {protocol}://{domain}/sitemap.xml"
    ])
    
    # Crawl delay for politeness
    lines.extend([
        "",
        "Crawl-delay: 1"
    ])
    
    return HttpResponse('\n'.join(lines), content_type='text/plain')