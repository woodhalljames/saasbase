from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def tag_url(tag):
    """Generate URL for a tag"""
    return reverse('newsletter:tag_posts', kwargs={'slug': tag.slug})