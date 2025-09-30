# saas_base/utils/social_sharing.py
"""
Social sharing URL generator utility
"""
from urllib.parse import urlencode, quote_plus
from django.conf import settings


def generate_social_share_urls(request, title, description, image_url=None):
    """
    Generate social sharing URLs for various platforms
    
    Args:
        request: Django request object
        title: Title to share
        description: Description to share
        image_url: Optional image URL (for Pinterest)
    
    Returns:
        Dictionary of social share URLs
    """
    current_url = request.build_absolute_uri()
    
    # Encode parameters
    encoded_url = quote_plus(current_url)
    encoded_title = quote_plus(title)
    encoded_description = quote_plus(description)
    share_text = quote_plus(f"{title} - {description}")
    
    social_urls = {
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        'twitter': f"https://twitter.com/intent/tweet?url={encoded_url}&text={share_text}",
        'whatsapp': f"https://wa.me/?text={share_text}%20{encoded_url}",
        'email': f"mailto:?subject={encoded_title}&body={encoded_description}%20{encoded_url}",
        'copy_link': current_url,
    }
    
    # Add Pinterest with image if provided
    if image_url:
        encoded_image = quote_plus(image_url)
        social_urls['pinterest'] = (
            f"https://pinterest.com/pin/create/button/"
            f"?url={encoded_url}&media={encoded_image}&description={encoded_description}"
        )
    else:
        social_urls['pinterest'] = (
            f"https://pinterest.com/pin/create/button/"
            f"?url={encoded_url}&description={encoded_description}"
        )
    
    return social_urls


def get_default_og_image(request):
    """
    Get the default OG image URL for social sharing
    
    Returns absolute URL to default OG image
    """
    # Use the static og-image.jpg from your static files
    from django.templatetags.static import static
    
    default_image_path = static('images/og-image.jpg')
    return request.build_absolute_uri(default_image_path)