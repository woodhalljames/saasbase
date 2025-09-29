import os
from django.utils.text import slugify


def get_blog_post_upload_path(instance, filename):
    """
    Custom upload path for blog post content images.
    Organizes images by post: blog/content/{post-slug}/{filename}
    """
    # Get the post from the instance
    # Summernote passes the attachment instance, we need to get the post
    if hasattr(instance, 'object_id') and hasattr(instance, 'name'):
        # This is a summernote attachment
        from .models import BlogPost
        try:
            post = BlogPost.objects.get(pk=instance.object_id)
            post_slug = post.slug if post.slug else 'draft'
        except BlogPost.DoesNotExist:
            post_slug = 'draft'
    else:
        post_slug = 'draft'
    
    # Clean the filename
    name, ext = os.path.splitext(filename)
    clean_name = slugify(name)
    
    return f'blog/content/{post_slug}/{clean_name}{ext}'