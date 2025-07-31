from django.db import models
from django.utils import timezone


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    subscribed_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
    
    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
    
    @classmethod
    def get_active_count(cls):
        return cls.objects.filter(is_active=True).count()