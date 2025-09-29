# newsletter/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BlogPost
from .tasks import send_blog_post_email
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BlogPost)
def trigger_newsletter_email(sender, instance, created, **kwargs):
    """
    Automatically send newsletter email when a blog post is published
    """
    # Check if post is being published for the first time
    if instance.status == 'published' and instance.published_at and not instance.email_sent:
        # Check if this is a real publish (not draft save)
        if not created:  # Only for updates, not initial creation
            try:
                old_instance = BlogPost.objects.get(pk=instance.pk)
                # Check if status changed from draft/archived to published
                was_published = old_instance.status == 'published'
                is_published = instance.status == 'published'
                
                if not was_published and is_published:
                    # Schedule email task
                    logger.info(f"Scheduling newsletter email for post: {instance.title}")
                    send_blog_post_email.delay(instance.pk)
            except BlogPost.DoesNotExist:
                pass