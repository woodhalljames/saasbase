import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.urls import reverse
from taggit.models import Tag

from .forms import NewsletterSignupForm
from .models import (
    NewsletterSubscription, BlogPost, BlogComment
)

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@method_decorator(csrf_protect, name='dispatch')
class NewsletterSignupView(View):
    def post(self, request):
        # Handle AJAX form submission
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
        
        try:
            # Parse JSON data
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter your email address.'
                })
            
            # Check if already subscribed first (for better UX)
            existing_subscription = NewsletterSubscription.objects.filter(email=email).first()
            
            if existing_subscription and existing_subscription.is_active:
                return JsonResponse({
                    'success': False,
                    'message': 'You\'re already subscribed to our newsletter! Check your inbox for updates.'
                })
            
            # Create form with data
            form = NewsletterSignupForm(data={'email': email})
            
            if form.is_valid():
                try:
                    # Handle both new subscriptions and reactivations
                    if existing_subscription and not existing_subscription.is_active:
                        # Reactivate existing subscription
                        existing_subscription.is_active = True
                        existing_subscription.ip_address = get_client_ip(request)
                        existing_subscription.user_agent = request.META.get('HTTP_USER_AGENT', '')
                        existing_subscription.save()
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'Welcome back! Your subscription has been reactivated.'
                        })
                    else:
                        # Create new subscription
                        subscription = form.save(commit=False)
                        subscription.ip_address = get_client_ip(request)
                        subscription.user_agent = request.META.get('HTTP_USER_AGENT', '')
                        subscription.save()
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'Thank you! You\'ve been subscribed to our newsletter.'
                        })
                        
                except Exception as save_error:
                    logger.error(f"Error saving newsletter subscription: {save_error}")
                    return JsonResponse({
                        'success': False,
                        'message': 'Something went wrong while subscribing. Please try again.'
                    })
            else:
                # Return form errors
                error_message = 'Please check your email and try again.'
                
                if 'email' in form.errors:
                    error_message = form.errors['email'][0]
                
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid request data.'
            }, status=400)
        except Exception as e:
            logger.error(f"Newsletter signup error: {e}")
            return JsonResponse({
                'success': False, 
                'message': 'Something went wrong. Please try again later.'
            }, status=500)


newsletter_signup = NewsletterSignupView.as_view()


def unsubscribe(request, email):
    """Unsubscribe from newsletter"""
    try:
        subscription = NewsletterSubscription.objects.get(email=email)
        subscription.is_active = False
        subscription.save()
        
        messages.success(
            request, 
            f"You've been unsubscribed from our newsletter. "
            f"We're sorry to see you go! You can resubscribe anytime."
        )
    except NewsletterSubscription.DoesNotExist:
        messages.info(request, "This email is not in our newsletter list.")
    
    return render(request, 'newsletter/unsubscribe.html', {'email': email})


def general_unsubscribe(request):
    """General unsubscribe page where users enter their email"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, 'newsletter/general_unsubscribe.html')
        
        try:
            subscription = NewsletterSubscription.objects.get(email=email)
            if subscription.is_active:
                subscription.is_active = False
                subscription.save()
                messages.success(
                    request, 
                    f"You've been unsubscribed from our newsletter. "
                    f"We're sorry to see you go! You can resubscribe anytime."
                )
            else:
                messages.info(request, "This email is already unsubscribed from our newsletter.")
        except NewsletterSubscription.DoesNotExist:
            messages.info(request, "This email is not in our newsletter list.")
        
        return render(request, 'newsletter/general_unsubscribe.html')
    
    return render(request, 'newsletter/general_unsubscribe.html')


# Blog Views
class BlogListView(ListView):
    """Main blog listing page with django-taggit tags"""
    model = BlogPost
    template_name = 'newsletter/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = BlogPost.published_posts().select_related('author').prefetch_related('tags')
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get popular tags using django-taggit
        context['popular_tags'] = Tag.objects.filter(
            taggit_taggeditem_items__content_type__app_label='newsletter',
            taggit_taggeditem_items__content_type__model='blogpost',
            taggit_taggeditem_items__object_id__in=BlogPost.published_posts().values_list('id', flat=True)
        ).annotate(
            post_count=Count('taggit_taggeditem_items')
        ).filter(post_count__gt=0).order_by('-post_count')[:15]
        
        # Recent posts for sidebar/recommendations
        context['recent_posts'] = BlogPost.published_posts()[:5]
        context['search_query'] = self.request.GET.get('q', '')
        
        return context


class BlogDetailView(DetailView):
    """Individual blog post page with enhanced SEO"""
    model = BlogPost
    template_name = 'newsletter/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.select_related('author').prefetch_related('tags', 'comments')
    
    def get_object(self):
        obj = super().get_object()
        # Only show published posts to non-staff
        if not obj.is_published and not self.request.user.is_staff:
            from django.http import Http404
            raise Http404("Blog post not found")
        
        # Increment view count
        obj.increment_views()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Get approved comments
        comments = post.comments.filter(
            is_approved=True,
            parent=None
        ).select_related('author').prefetch_related('replies')
        
        context['comments'] = comments
        context['comment_count'] = post.comments.filter(is_approved=True).count()
        
        # Related posts by tags using django-taggit
        related_posts = BlogPost.published_posts().exclude(pk=post.pk)
        
        if post.tags.exists():
            # Get posts that share tags with this post
            related_posts = related_posts.filter(
                tags__in=post.tags.all()
            ).distinct().order_by('-published_at')[:3]
        else:
            # Fallback to recent posts
            related_posts = related_posts.order_by('-published_at')[:3]
        
        context['related_posts'] = related_posts
        
        # Social sharing URLs
        from urllib.parse import quote
        share_url = self.request.build_absolute_uri()
        context['social_share'] = {
            'facebook': f"https://www.facebook.com/sharer/sharer.php?u={quote(share_url)}",
            'twitter': f"https://twitter.com/intent/tweet?url={quote(share_url)}&text={quote(post.title)}",
            'pinterest': f"https://pinterest.com/pin/create/button/?url={quote(share_url)}&description={quote(post.title)}",
            'linkedin': f"https://www.linkedin.com/shareArticle?url={quote(share_url)}&title={quote(post.title)}",
        }
        
        return context


class TagPostsView(ListView):
    """Posts filtered by tag using django-taggit"""
    model = BlogPost
    template_name = 'newsletter/tag_posts.html'
    context_object_name = 'posts'
    paginate_by = 12
    
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return BlogPost.published_posts().filter(
            tags=self.tag
        ).select_related('author').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        
        # Get other popular tags for discovery
        context['popular_tags'] = Tag.objects.filter(
            taggit_taggeditem_items__content_type__app_label='newsletter',
            taggit_taggeditem_items__content_type__model='blogpost',
            taggit_taggeditem_items__object_id__in=BlogPost.published_posts().values_list('id', flat=True)
        ).annotate(
            post_count=Count('taggit_taggeditem_items')
        ).filter(post_count__gt=0).order_by('-post_count')[:10]
        
        return context


@login_required
def add_comment(request, slug):
    """Add a comment to a blog post"""
    post = get_object_or_404(BlogPost, slug=slug)
    
    if not post.allow_comments:
        messages.error(request, "Comments are disabled for this post.")
        return redirect(post.get_absolute_url())
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if content:
            comment = BlogComment(
                post=post,
                author=request.user,
                content=content
            )
            
            # Handle reply
            if parent_id:
                try:
                    parent = BlogComment.objects.get(pk=parent_id, post=post)
                    comment.parent = parent
                except BlogComment.DoesNotExist:
                    pass
            
            comment.save()
            messages.success(request, "Your comment has been posted!")
        else:
            messages.error(request, "Please enter a comment.")
    
    return redirect(post.get_absolute_url() + '#comments')