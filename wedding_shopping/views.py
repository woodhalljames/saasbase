# wedding_shopping/views.py - Updated for enhanced social media and wedding links
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, Http404
from django.db import transaction
from django.utils import timezone
from datetime import datetime
import re
from urllib.parse import urlparse

from .models import CoupleProfile, WeddingLink, SocialMediaLink
from .forms import (
    CoupleProfileForm, SocialMediaFormSet, WeddingLinkFormSet
)


def detect_wedding_link_branding(url, link_type=None):
    """Enhanced detection for wedding links including registries, RSVP, livestreams, etc."""
    if not url:
        return {
            'detected': False,
            'service': 'other',
            'name': 'Custom Link',
            'icon': 'bi-link-45deg',
            'color': '#6c757d',
            'suggestions': {}
        }
    
    url_lower = url.lower()
    domain = urlparse(url).netloc.lower()
    
    # Comprehensive service patterns
    service_patterns = {
        # Wedding Registries
        'amazon': {
            'patterns': ['amazon.com', 'amzn.com'],
            'name': 'Amazon',
            'icon': 'bi-amazon',
            'color': '#FF9900',
            'suggestions': {'title': 'Amazon Registry'}
        },
        'target': {
            'patterns': ['target.com'],
            'name': 'Target',
            'icon': 'bi-bullseye',
            'color': '#CC0000',
            'suggestions': {'title': 'Target Registry'}
        },
        'bed_bath_beyond': {
            'patterns': ['bedbathandbeyond.com', 'buybuybaby.com'],
            'name': 'Bed Bath & Beyond',
            'icon': 'bi-house-fill',
            'color': '#003087',
            'suggestions': {'title': 'Bed Bath & Beyond Registry'}
        },
        'williams_sonoma': {
            'patterns': ['williams-sonoma.com', 'williamssonoma.com'],
            'name': 'Williams Sonoma',
            'icon': 'bi-cup-hot-fill',
            'color': '#8B4513',
            'suggestions': {'title': 'Williams Sonoma Registry'}
        },
        'crate_barrel': {
            'patterns': ['crateandbarrel.com', 'cb2.com'],
            'name': 'Crate & Barrel',
            'icon': 'bi-house-door-fill',
            'color': '#000000',
            'suggestions': {'title': 'Crate & Barrel Registry'}
        },
        'pottery_barn': {
            'patterns': ['potterybarn.com', 'pbteen.com', 'pbkids.com'],
            'name': 'Pottery Barn',
            'icon': 'bi-home-fill',
            'color': '#8B4513',
            'suggestions': {'title': 'Pottery Barn Registry'}
        },
        'macy': {
            'patterns': ['macys.com'],
            'name': "Macy's",
            'icon': 'bi-bag-fill',
            'color': '#E21937',
            'suggestions': {'title': "Macy's Registry"}
        },
        'zola': {
            'patterns': ['zola.com'],
            'name': 'Zola',
            'icon': 'bi-heart-fill',
            'color': '#FF6B6B',
            'suggestions': {'title': 'Zola Registry'}
        },
        'the_knot': {
            'patterns': ['theknot.com'],
            'name': 'The Knot',
            'icon': 'bi-heart',
            'color': '#FF69B4',
            'suggestions': {'title': 'The Knot Registry'}
        },
        'wayfair': {
            'patterns': ['wayfair.com'],
            'name': 'Wayfair',
            'icon': 'bi-house-fill',
            'color': '#663399',
            'suggestions': {'title': 'Wayfair Registry'}
        },
        'honeyfund': {
            'patterns': ['honeyfund.com'],
            'name': 'Honeyfund',
            'icon': 'bi-airplane-fill',
            'color': '#FFA500',
            'suggestions': {'title': 'Honeymoon Fund'}
        },
        
        # RSVP Services
        'rsvpify': {
            'patterns': ['rsvpify.com'],
            'name': 'RSVPify',
            'icon': 'bi-envelope-check',
            'color': '#007bff',
            'suggestions': {'title': 'Wedding RSVP'}
        },
        'wedding_wire': {
            'patterns': ['rsvp.weddingwire.com', 'weddingwire.com'],
            'name': 'WeddingWire',
            'icon': 'bi-envelope-check',
            'color': '#28a745',
            'suggestions': {'title': 'RSVP Page'}
        },
        'anrsvp': {
            'patterns': ['anrsvp.com'],
            'name': 'anRSVP',
            'icon': 'bi-envelope-check',
            'color': '#6f42c1',
            'suggestions': {'title': 'Wedding RSVP'}
        },
        'withjoy': {
            'patterns': ['withjoy.com'],
            'name': 'WithJoy',
            'icon': 'bi-envelope-heart',
            'color': '#fd7e14',
            'suggestions': {'title': 'Wedding Website & RSVP'}
        },
        
        # Livestream Services
        'zoom': {
            'patterns': ['zoom.us', 'zoom.com'],
            'name': 'Zoom',
            'icon': 'bi-camera-video',
            'color': '#2D8CFF',
            'suggestions': {'title': 'Wedding Livestream'}
        },
        'youtube': {
            'patterns': ['youtube.com', 'youtu.be'],
            'name': 'YouTube',
            'icon': 'bi-youtube',
            'color': '#FF0000',
            'suggestions': {'title': 'Wedding Livestream'}
        },
        'facebook': {
            'patterns': ['facebook.com', 'fb.com'],
            'name': 'Facebook',
            'icon': 'bi-facebook',
            'color': '#1877F2',
            'suggestions': {'title': 'Facebook Live Stream'}
        },
        'instagram': {
            'patterns': ['instagram.com'],
            'name': 'Instagram',
            'icon': 'bi-instagram',
            'color': '#E4405F',
            'suggestions': {'title': 'Instagram Live'}
        },
        
        # Photo Sharing
        'google_photos': {
            'patterns': ['photos.google.com', 'photos.app.goo.gl'],
            'name': 'Google Photos',
            'icon': 'bi-google',
            'color': '#4285F4',
            'suggestions': {'title': 'Wedding Photos'}
        },
        'dropbox': {
            'patterns': ['dropbox.com'],
            'name': 'Dropbox',
            'icon': 'bi-dropbox',
            'color': '#0061FF',
            'suggestions': {'title': 'Photo Gallery'}
        },
        'shutterfly': {
            'patterns': ['shutterfly.com'],
            'name': 'Shutterfly',
            'icon': 'bi-camera',
            'color': '#00A651',
            'suggestions': {'title': 'Wedding Photos'}
        },
        'smugmug': {
            'patterns': ['smugmug.com'],
            'name': 'SmugMug',
            'icon': 'bi-camera-fill',
            'color': '#6DB33F',
            'suggestions': {'title': 'Photo Gallery'}
        },
    }
    
    for service_type, config in service_patterns.items():
        if any(pattern in domain for pattern in config['patterns']):
            return {
                'detected': True,
                'service': service_type,
                'name': config['name'],
                'icon': config['icon'],
                'color': config.get('color', '#007bff'),
                'suggestions': config.get('suggestions', {})
            }
    
    return {
        'detected': False,
        'service': 'custom',
        'name': 'Custom Link',
        'icon': 'bi-link-45deg',
        'color': '#6c757d',
        'suggestions': {}
    }


def detect_social_platform(url):
    """Detect social media platform from URL"""
    if not url:
        return {
            'detected': False,
            'platform': 'other',
            'name': 'Unknown Platform',
            'icon': 'bi-link-45deg',
            'color': '#6c757d',
            'suggestions': {}
        }
    
    url_lower = url.lower()
    domain = urlparse(url).netloc.lower()
    
    platform_patterns = {
        'instagram': {
            'patterns': ['instagram.com', 'instagr.am'],
            'name': 'Instagram',
            'icon': 'bi-instagram',
            'color': '#E4405F',
            'suggestions': {'display_name': '@username'}
        },
        'facebook': {
            'patterns': ['facebook.com', 'fb.com'],
            'name': 'Facebook',
            'icon': 'bi-facebook',
            'color': '#1877F2',
            'suggestions': {'display_name': 'Facebook Page'}
        },
        'twitter': {
            'patterns': ['twitter.com', 'x.com'],
            'name': 'X (Twitter)',
            'icon': 'bi-twitter-x',
            'color': '#000000',
            'suggestions': {'display_name': '@username'}
        },
        'tiktok': {
            'patterns': ['tiktok.com'],
            'name': 'TikTok',
            'icon': 'bi-tiktok',
            'color': '#FF0050',
            'suggestions': {'display_name': '@username'}
        },
        'youtube': {
            'patterns': ['youtube.com', 'youtu.be'],
            'name': 'YouTube',
            'icon': 'bi-youtube',
            'color': '#FF0000',
            'suggestions': {'display_name': 'YouTube Channel'}
        },
        'pinterest': {
            'patterns': ['pinterest.com'],
            'name': 'Pinterest',
            'icon': 'bi-pinterest',
            'color': '#BD081C',
            'suggestions': {'display_name': 'Pinterest'}
        },
        'linkedin': {
            'patterns': ['linkedin.com'],
            'name': 'LinkedIn',
            'icon': 'bi-linkedin',
            'color': '#0A66C2',
            'suggestions': {'display_name': 'LinkedIn'}
        }
    }
    
    for platform, config in platform_patterns.items():
        if any(pattern in domain for pattern in config['patterns']):
            return {
                'detected': True,
                'platform': platform,
                'name': config['name'],
                'icon': config['icon'],
                'color': config.get('color', '#007bff'),
                'suggestions': config.get('suggestions', {})
            }
    
    # Check if it's a website
    if any(tld in domain for tld in ['.com', '.org', '.net', '.co', '.io']):
        return {
            'detected': True,
            'platform': 'website',
            'name': 'Website',
            'icon': 'bi-globe',
            'color': '#007bff',
            'suggestions': {'display_name': 'Our Website'}
        }
    
    return {
        'detected': False,
        'platform': 'other',
        'name': 'Custom Link',
        'icon': 'bi-link-45deg',
        'color': '#6c757d',
        'suggestions': {}
    }


class PublicCoupleDetailView(DetailView):
    """Public view of a couple's wedding page - no login required"""
    model = CoupleProfile
    template_name = 'wedding_shopping/public_couple_detail.html'
    context_object_name = 'couple'
    
    def get_object(self):
        """Get couple by custom slug or share_token"""
        share_token = self.kwargs.get('share_token')
        slug = self.kwargs.get('slug')
        
        if share_token:
            return get_object_or_404(CoupleProfile, share_token=share_token)
        elif slug:
            couple = get_object_or_404(CoupleProfile, slug=slug)
            
            if not couple.is_public and not self.request.user == couple.user:
                return redirect('wedding_shopping:wedding_page_token', 
                              share_token=couple.share_token)
            
            return couple
        else:
            raise Http404("Wedding page not found")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        couple = self.object
        
        # Calculate days until wedding
        if couple.wedding_date:
            today = timezone.now().date()
            if couple.wedding_date > today:
                context['days_until_wedding'] = (couple.wedding_date - today).days
            elif couple.wedding_date == today:
                context['is_wedding_day'] = True
            else:
                context['wedding_passed'] = True
                context['days_since_wedding'] = (today - couple.wedding_date).days
        
        # Get organized social media links
        context['partner_1_social_links'] = couple.partner_1_social_links.filter(pk__isnull=False)
        context['partner_2_social_links'] = couple.partner_2_social_links.filter(pk__isnull=False)
        context['shared_social_links'] = couple.shared_social_links.filter(pk__isnull=False)
        
        # Get wedding links by category
        context['registry_links'] = couple.registry_links.filter(pk__isnull=False)
        context['rsvp_links'] = couple.rsvp_links.filter(pk__isnull=False)
        context['livestream_links'] = couple.livestream_links.filter(pk__isnull=False)
        context['photo_links'] = couple.photo_links.filter(pk__isnull=False)
        context['other_links'] = couple.other_links.filter(pk__isnull=False)
        
        # All wedding links for backwards compatibility
        context['wedding_links'] = couple.wedding_links.filter(pk__isnull=False)
        
        return context


class CoupleProfileManageView(LoginRequiredMixin, UpdateView):
    """Single view to create or update couple profile with enhanced formsets"""
    model = CoupleProfile
    form_class = CoupleProfileForm
    template_name = 'wedding_shopping/manage_couple_site.html'
    
    def get_object(self, queryset=None):
        """Get existing profile or create a new one"""
        try:
            return CoupleProfile.objects.get(user=self.request.user)
        except CoupleProfile.DoesNotExist:
            return CoupleProfile(user=self.request.user)
    
    def get_success_url(self):
        return reverse('wedding_shopping:manage_wedding_page')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        is_new = not self.object.pk
        context['is_new'] = is_new
        context['title'] = "Create Your Wedding Page" if is_new else "Manage Your Wedding Page"
        
        # Configure formsets
        if self.request.POST:
            context['social_formset'] = SocialMediaFormSet(
                self.request.POST, 
                instance=self.object if not is_new else None,
                prefix='social',
                form_kwargs={'couple_profile': self.object if not is_new else None}
            )
            context['wedding_link_formset'] = WeddingLinkFormSet(
                self.request.POST, 
                instance=self.object if not is_new else None,
                prefix='weddinglink'
            )
        else:
            context['social_formset'] = SocialMediaFormSet(
                instance=self.object if not is_new else None,
                prefix='social',
                form_kwargs={'couple_profile': self.object if not is_new else None}
            )
            context['wedding_link_formset'] = WeddingLinkFormSet(
                instance=self.object if not is_new else None,
                prefix='weddinglink'
            )
        
        # Backwards compatibility
        context['registry_formset'] = context['wedding_link_formset']
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        is_new = context['is_new']
        
        social_formset = context.get('social_formset')
        wedding_link_formset = context.get('wedding_link_formset')
        
        # Validate all formsets
        formsets_valid = all([
            social_formset.is_valid() if social_formset else True,
            wedding_link_formset.is_valid() if wedding_link_formset else True
        ])
        
        if not formsets_valid:
            return self.form_invalid(form)
        
        with transaction.atomic():
            # Save the main profile
            form.instance.user = self.request.user
            old_slug = self.object.slug if self.object.pk else None
            self.object = form.save()
            new_slug = self.object.slug
            
            # Save social media formset
            if social_formset:
                social_formset.instance = self.object
                social_instances = social_formset.save(commit=False)
                for social in social_instances:
                    social.couple_profile = self.object
                    # Clean URL
                    if social.url and not social.url.startswith(('http://', 'https://')):
                        social.url = 'https://' + social.url
                    social.save()
                # Handle deletions
                for obj in social_formset.deleted_objects:
                    obj.delete()
            
            # Save wedding links formset
            if wedding_link_formset:
                wedding_link_formset.instance = self.object
                wedding_link_instances = wedding_link_formset.save(commit=False)
                for wedding_link in wedding_link_instances:
                    wedding_link.couple_profile = self.object
                    # Clean URL
                    if wedding_link.url and not wedding_link.url.startswith(('http://', 'https://')):
                        wedding_link.url = 'https://' + wedding_link.url
                    wedding_link.save()
                # Handle deletions
                for obj in wedding_link_formset.deleted_objects:
                    obj.delete()
        
        # Success messages
        if is_new:
            messages.success(
                self.request, 
                f"Your wedding page has been created successfully! Your custom URL is: {self.object.wedding_url_preview}. "
                f"Share this page with friends and family to let them find your registries and wedding information."
            )
        elif old_slug != new_slug:
            messages.success(
                self.request, 
                f"Your wedding page has been updated! Your custom URL is now: {self.object.wedding_url_preview}"
            )
        else:
            messages.success(self.request, "Your wedding page has been updated successfully!")
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        context = self.get_context_data()
        
        if form.errors:
            messages.error(self.request, "Please correct the errors in your wedding details.")
        
        social_formset = context.get('social_formset')
        wedding_link_formset = context.get('wedding_link_formset')
        
        if social_formset and not social_formset.is_valid():
            messages.error(self.request, "Please correct the errors in your social media links.")
        
        if wedding_link_formset and not wedding_link_formset.is_valid():
            messages.error(self.request, "Please correct the errors in your wedding links.")
        
        return super().form_invalid(form)


@login_required
def couple_dashboard(request):
    """Dashboard redirects to the single manage page"""
    return redirect('wedding_shopping:manage_wedding_page')


def wedding_link_redirect(request, pk):
    """Click tracking and redirect to wedding link"""
    wedding_link = get_object_or_404(WeddingLink, pk=pk)
    wedding_link.increment_clicks()
    return redirect(wedding_link.url)


# Backwards compatibility for registry redirects
def registry_redirect(request, pk):
    """Backwards compatibility - redirect to wedding link redirect"""
    return wedding_link_redirect(request, pk)


def legacy_couple_redirect(request, slug=None, share_token=None):
    """Redirect old /couple/ URLs to new /wedding/ format"""
    if share_token:
        return redirect('wedding_shopping:wedding_page_token', share_token=share_token)
    elif slug:
        return redirect('wedding_shopping:wedding_page', slug=slug)
    else:
        return redirect('wedding_shopping:public_couples_list')


# API endpoints
def detect_url_branding_api(request):
    """API endpoint to detect branding from URL"""
    if request.method == 'GET':
        url = request.GET.get('url', '')
        url_type = request.GET.get('type', 'wedding_link')  # 'wedding_link' or 'social'
        link_type = request.GET.get('link_type', None)  # For wedding links
        
        if url_type == 'social':
            branding = detect_social_platform(url)
        else:
            branding = detect_wedding_link_branding(url, link_type)
        
        return JsonResponse({
            'success': True,
            'branding': branding
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def public_couples_list(request):
    """List all public couple profiles"""
    couples = CoupleProfile.objects.filter(is_public=True).order_by('-created_at')
    
    context = {
        'couples': couples,
        'title': 'Wedding Celebrations'
    }
    
    return render(request, 'wedding_shopping/public_couples_list.html', context)