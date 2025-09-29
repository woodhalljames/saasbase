from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_summernote.admin import SummernoteModelAdmin
from .models import NewsletterSubscription, BlogPost, BlogComment


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active', 'ip_address']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at', 'ip_address', 'user_agent']
    ordering = ['-subscribed_at']
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriptions activated.')
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriptions deactivated.')
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"


@admin.register(BlogPost)
class BlogPostAdmin(SummernoteModelAdmin):
    """Blog post admin with Summernote WYSIWYG editor"""
    
    # Summernote configuration
    summernote_fields = ('content',)
    
    list_display = [
        'title', 'status', 'author', 'published_at', 
        'view_count', 'comment_count', 'tag_list'
    ]
    list_filter = ['status', 'published_at', 'created_at', 'tags']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'created_at', 'updated_at', 'reading_time']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'excerpt')
        }),
        ('Content', {
            'fields': ('content',),
            'description': 'Use the rich text editor below to write your post. You can drag & drop images directly into the editor.'
        }),
        ('Featured Image', {
            'fields': ('featured_image', 'featured_image_alt'),
            'description': 'Upload a hero image for the top of your post. Recommended size: 1920x1080px'
        }),
        ('SEO & Metadata', {
            'fields': ('meta_description', 'meta_keywords', 'tags'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('status', 'published_at', 'allow_comments')
        }),
        ('Statistics', {
            'fields': ('view_count', 'reading_time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Email', {
            'fields': ('email_sent', 'email_sent_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['publish_posts', 'draft_posts', 'send_newsletter']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
    
    def tag_list(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()]) if obj.tags.exists() else '-'
    tag_list.short_description = 'Tags'
    
    def comment_count(self, obj):
        count = obj.comments.count()
        if count > 0:
            url = reverse('admin:newsletter_blogcomment_changelist') + f'?post__id__exact={obj.id}'
            return format_html('<a href="{}">{} comments</a>', url, count)
        return '0 comments'
    comment_count.short_description = 'Comments'
    
    def reading_time(self, obj):
        return f"{obj.reading_time} min"
    reading_time.short_description = 'Reading Time'
    
    def publish_posts(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} posts published.')
    publish_posts.short_description = "Publish selected posts"
    
    def draft_posts(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} posts moved to draft.')
    draft_posts.short_description = "Move to draft"
    
    def send_newsletter(self, request, queryset):
        """Manually trigger newsletter sending for selected posts"""
        from .tasks import send_blog_post_email
        count = 0
        for post in queryset.filter(status='published'):
            if not post.email_sent:
                send_blog_post_email.delay(post.pk)
                count += 1
        
        if count > 0:
            self.message_user(request, f'Newsletter emails queued for {count} posts.')
        else:
            self.message_user(request, 'No eligible posts found (must be published and not already sent).')
    send_newsletter.short_description = "Send newsletter for selected posts"


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'content_preview', 'created_at', 'is_approved', 'is_featured']
    list_filter = ['is_approved', 'is_featured', 'created_at', 'post']
    search_fields = ['content', 'author__email', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('post', 'author', 'content', 'parent')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_comments', 'unapprove_comments', 'feature_comments']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = "Approve selected comments"
    
    def unapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments unapproved.')
    unapprove_comments.short_description = "Unapprove selected comments"
    
    def feature_comments(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} comments featured.')
    feature_comments.short_description = "Feature selected comments"