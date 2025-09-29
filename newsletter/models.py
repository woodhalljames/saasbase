from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.urls import reverse
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from taggit.managers import TaggableManager
import uuid

User = get_user_model()


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


class BlogPost(models.Model):
    """Blog posts with SEO optimization and django-taggit tags"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    
    # Content
    excerpt = models.TextField(max_length=500, help_text="Brief description for listings and SEO")
    content = models.TextField(help_text="Main content with rich text editor (Summernote)")
    
    # Images
    featured_image = models.ImageField(upload_to='blog/featured/', blank=True, null=True)
    featured_image_alt = models.CharField(max_length=200, blank=True, help_text="Alt text for featured image (SEO)")
    
    # Tags using django-taggit
    tags = TaggableManager(blank=True, help_text="Add tags separated by commas")
    
    # SEO fields
    meta_description = models.TextField(max_length=160, blank=True, help_text="SEO meta description (160 chars)")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords")
    
    # Publishing
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Engagement
    view_count = models.PositiveIntegerField(default=0)
    allow_comments = models.BooleanField(default=True)
    
    # Email tracking
    email_sent = models.BooleanField(default=False, help_text="Newsletter email has been sent for this post")
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Generate slug
        if not self.slug:
            base_slug = slugify(self.title)
            counter = 1
            self.slug = base_slug
            
            while BlogPost.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        # Track if we're publishing for the first time
        is_newly_published = False
        if self.pk:
            try:
                old_instance = BlogPost.objects.get(pk=self.pk)
                # Check if status changed to published
                if old_instance.status != 'published' and self.status == 'published':
                    is_newly_published = True
            except BlogPost.DoesNotExist:
                if self.status == 'published':
                    is_newly_published = True
        else:
            if self.status == 'published':
                is_newly_published = True
        
        # Set published date
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        # Generate meta description if empty
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
        
        # Optimize featured image if changed
        if self.pk:
            try:
                old_instance = BlogPost.objects.get(pk=self.pk)
                image_changed = old_instance.featured_image != self.featured_image
            except BlogPost.DoesNotExist:
                image_changed = True
        else:
            image_changed = bool(self.featured_image)
        
        if self.featured_image and image_changed:
            self.optimize_featured_image()
        
        super().save(*args, **kwargs)
        
        # Trigger newsletter email if newly published
        if is_newly_published and not self.email_sent:
            from .tasks import send_blog_post_email
            send_blog_post_email.delay(self.pk)
    
    def optimize_featured_image(self):
        """Automatically optimize the featured image on upload"""
        try:
            from PIL import Image
            from io import BytesIO
            from django.core.files.base import ContentFile
            
            # Open the image
            img = Image.open(self.featured_image)
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Resize if too large (max 1920px wide)
            if img.width > 1920:
                ratio = 1920 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((1920, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized version back to featured_image
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # Update the featured_image field without triggering another save
            self.featured_image.save(
                self.featured_image.name,
                ContentFile(output.getvalue()),
                save=False
            )
            
        except Exception as e:
            print(f"Error optimizing featured image: {e}")
    
    def get_absolute_url(self):
        return reverse('newsletter:resource_detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        return self.status == 'published' and self.published_at and self.published_at <= timezone.now()
    
    @property
    def reading_time(self):
        """Estimate reading time in minutes"""
        word_count = len(self.content.split())
        return max(1, word_count // 200)
    
    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    @classmethod
    def published_posts(cls):
        """Get all published posts"""
        return cls.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        )
    
    def get_seo_data(self, request=None):
        """Generate SEO data for templates"""
        # Use custom meta description or fallback to excerpt
        description = self.meta_description or self.excerpt[:160]
        
        # Build absolute URL
        absolute_url = None
        if request:
            absolute_url = request.build_absolute_uri(self.get_absolute_url())
        
        # Choose best image for social sharing
        social_image = None
        if self.featured_image:
            social_image = self.featured_image.url
        
        # Get author name safely
        author_name = 'DreamWedAI'
        if self.author:
            if hasattr(self.author, 'get_display_name'):
                author_name = self.author.get_display_name()
            else:
                author_name = self.author.username or self.author.email
        
        return {
            'title': self.title,
            'description': description,
            'keywords': self.meta_keywords or ', '.join([tag.name for tag in self.tags.all()]),
            'og_image': social_image,
            'canonical_url': absolute_url,
            'published_time': self.published_at,
            'modified_time': self.updated_at,
            'author': author_name,
            'reading_time': self.reading_time,
            'article_tags': [tag.name for tag in self.tags.all()],
        }


class BlogComment(models.Model):
    """Comments on blog posts (authenticated users only)"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comments')
    content = models.TextField(max_length=1000)
    
    # Moderation
    is_approved = models.BooleanField(default=True)  # Auto-approve for authenticated users
    is_featured = models.BooleanField(default=False)  # Highlight great comments
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Threading (optional simple implementation)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]
    
    def __str__(self):
        # Safely get author name - check if get_display_name exists, otherwise use username
        author_name = getattr(self.author, 'get_display_name', lambda: self.author.username)()
        return f"Comment by {author_name} on {self.post.title}"
    
    @property
    def is_reply(self):
        return self.parent is not None