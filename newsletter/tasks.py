from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
import logging

from .models import NewsletterSubscription, BlogPost

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_blog_post_email(self, post_id):
    """Send blog post notification to all active subscribers"""
    try:
        post = BlogPost.objects.get(pk=post_id)
        
        # Skip if already sent
        if post.email_sent:
            logger.info(f"Email already sent for post {post.title}")
            return f"Email already sent for post {post.title}"
        
        # Get active subscribers
        subscribers = NewsletterSubscription.objects.filter(is_active=True)
        total = subscribers.count()
        
        if total == 0:
            logger.info("No active subscribers to notify")
            return "No active subscribers"
        
        # Get site domain
        try:
            site = Site.objects.get_current()
            domain = site.domain
        except:
            domain = settings.SITE_DOMAIN if hasattr(settings, 'SITE_DOMAIN') else 'dreamwedai.com'
        
        # Prepare email context
        context = {
            'post': post,
            'domain': domain,
            'post_url': f"https://{domain}{post.get_absolute_url()}",
            'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'DreamWedAI',
            'excerpt_words': 50,  # Number of words to show in preview
            'current_year': timezone.now().year,
        }
        
        # Generate email content
        html_content = render_to_string('newsletter/emails/blog_post_notification.html', context)
        text_content = strip_tags(render_to_string('newsletter/emails/blog_post_notification.txt', context))
        
        # Email subject
        subject = f"New Post: {post.title}"
        from_email = settings.DEFAULT_FROM_EMAIL
        
        # Batch send to subscribers
        batch_size = 50  # Send in batches to avoid overwhelming the mail server
        sent_count = 0
        failed_count = 0
        
        for i in range(0, total, batch_size):
            batch = subscribers[i:i+batch_size]
            
            for subscriber in batch:
                try:
                    # Add unsubscribe link for this subscriber
                    subscriber_context = context.copy()
                    subscriber_context['unsubscribe_url'] = f"https://{domain}/newsletter/unsubscribe/{subscriber.email}/"
                    
                    # Re-render with subscriber-specific context
                    html_with_unsubscribe = render_to_string(
                        'newsletter/emails/blog_post_notification.html', 
                        subscriber_context
                    )
                    text_with_unsubscribe = strip_tags(
                        render_to_string(
                            'newsletter/emails/blog_post_notification.txt', 
                            subscriber_context
                        )
                    )
                    
                    # Create email
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_with_unsubscribe,
                        from_email=from_email,
                        to=[subscriber.email],
                        headers={
                            'List-Unsubscribe': f'<https://{domain}/newsletter/unsubscribe/{subscriber.email}/>',
                            'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click'
                        }
                    )
                    msg.attach_alternative(html_with_unsubscribe, "text/html")
                    msg.send(fail_silently=False)
                    sent_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to send email to {subscriber.email}: {e}")
                    failed_count += 1
        
        # Mark post as sent
        post.email_sent = True
        post.email_sent_at = timezone.now()
        post.save(update_fields=['email_sent', 'email_sent_at'])
        
        result_msg = f"Newsletter sent: {sent_count} successful, {failed_count} failed out of {total} subscribers"
        logger.info(result_msg)
        return result_msg
        
    except BlogPost.DoesNotExist:
        logger.error(f"BlogPost with id {post_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error sending blog post email: {e}")
        # Retry the task
        raise self.retry(exc=e, countdown=60)  # Retry after 1 minute


@shared_task
def send_test_blog_email(post_id, test_email):
    """Send a test email for a blog post to a specific address"""
    try:
        post = BlogPost.objects.get(pk=post_id)
        
        # Get site domain
        try:
            site = Site.objects.get_current()
            domain = site.domain
        except:
            domain = settings.SITE_DOMAIN if hasattr(settings, 'SITE_DOMAIN') else 'dreamwedai.com'
        
        context = {
            'post': post,
            'domain': domain,
            'post_url': f"https://{domain}{post.get_absolute_url()}",
            'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'DreamWedAI',
            'excerpt_words': 50,
            'unsubscribe_url': '#',  # Dummy for test
            'is_test': True,
            'current_year': timezone.now().year,
        }
        
        html_content = render_to_string('newsletter/emails/blog_post_notification.html', context)
        text_content = strip_tags(render_to_string('newsletter/emails/blog_post_notification.txt', context))
        
        subject = f"[TEST] New Post: {post.title}"
        
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[test_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return f"Test email sent to {test_email}"
        
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise