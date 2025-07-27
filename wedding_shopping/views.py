# wedding_shopping/views.py - Simplified version
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

from .models import CoupleProfile, RegistryLink, SocialMediaLink
from .forms import (
    CoupleProfileForm, SocialMediaFormSet, RegistryFormSet
)


def detect_registry_branding(url):
    """Detect registry type and branding from URL - simplified"""
    if not url:
        return {
            'detected': False,
            'type': 'other',
            'name': 'Unknown Registry',
            'icon': 'bi-gift',
            'color': '#6c757d',
            'suggestions': {}
        }
    
    url_lower = url.lower()
    domain = urlparse(url).netloc.lower()
    
    registry_patterns = {
        'amazon': {
            'patterns': ['amazon.com', 'amzn.com'],
            'name': 'Amazon',
            'icon': 'bi-amazon',
            'color': '#FF9900',
            'suggestions': {'display_name': 'Amazon Registry'}
        },
        'target': {
            'patterns': ['target.com'],
            'name': 'Target',
            'icon': 'bi-bullseye',
            'color': '#CC0000',
            'suggestions': {'display_name': 'Target Registry'}
        },
        'bed_bath_beyond': {
            'patterns': ['bedbathandbeyond.com', 'buybuybaby.com'],
            'name': 'Bed Bath & Beyond',
            'icon': 'bi-house-fill',
            'color': '#003087',
            'suggestions': {'display_name': 'Bed Bath & Beyond Registry'}
        },
        'williams_sonoma': {
            'patterns': ['williams-sonoma.com', 'williamssonoma.com'],
            'name': 'Williams Sonoma',
            'icon': 'bi-cup-hot-fill',
            'color': '#8B4513',
            'suggestions': {'display_name': 'Williams Sonoma Registry'}
        },
        'crate_barrel': {
            'patterns': ['crateandbarrel.com', 'cb2.com'],
            'name': 'Crate & Barrel',
            'icon': 'bi-house-door-fill',
            'color': '#000000',
            'suggestions': {'display_name': 'Crate & Barrel Registry'}
        },
        'pottery_barn': {
            'patterns': ['potterybarn.com', 'pbteen.com', 'pbkids.com'],
            'name': 'Pottery Barn',
            'icon': 'bi-home-fill',
            'color': '#8B4513',
            'suggestions': {'display_name': 'Pottery Barn Registry'}
        },
        'macy': {
            'patterns': ['macys.com'],
            'name': "Macy's",
            'icon': 'bi-bag-fill',
            'color': '#E21937',
            'suggestions': {'display_name': "Macy's Registry"}
        },
        'zola': {
            'patterns': ['zola.com'],
            'name': 'Zola',
            'icon': 'bi-heart-fill',
            'color': '#FF6B6B',
            'suggestions': {'display_name': 'Zola Registry'}
        },
        'the_knot': {
            'patterns': ['theknot.com'],
            'name': 'The Knot',
            'icon': 'bi-heart',
            'color': '#FF69B4',
            'suggestions': {'display_name': 'The Knot Registry'}
        },
        'wayfair': {
            'patterns': ['wayfair.com'],
            'name': 'Wayfair',
            'icon': 'bi-house-fill',
            'color': '#663399',
            'suggestions': {'display_name': 'Wayfair Registry'}
        },
        'honeyfund': {
            'patterns': ['honeyfund.com'],
            'name': 'Honeyfund',
            'icon': 'bi-airplane-fill',
            'color': '#FFA500',
            'suggestions': {'display_name': 'Honeymoon Fund'}
        }
    }
    
    for registry_type, config in registry_patterns.items():
        if any(pattern in domain for pattern in config['patterns']):
            return {
                'detected': True,
                'type': registry_type,
                'name': config['name'],
                'icon': config['icon'],
                'color': config.get('color', '#007bff'),
                'suggestions': config.get('suggestions', {})
            }
    
    return {
        'detected': False,
        'type': 'other',
        'name': 'Custom Registry',
        'icon': 'bi-gift',
        'color': '#6c757d',
        'suggestions': {}
    }


def detect_social_platform(url):
    """Detect social media platform from URL - simplified"""
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
        
        # Get related data - only include saved objects with valid PKs
        context['social_links'] = couple.social_links.filter(pk__isnull=False)
        context['registry_links'] = couple.registry_links.filter(pk__isnull=False)
        
        return context


class CoupleProfileManageView(LoginRequiredMixin, UpdateView):
    """Single view to create or update couple profile with social and registry formsets"""
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
                prefix='social'
            )
            context['registry_formset'] = RegistryFormSet(
                self.request.POST, 
                instance=self.object if not is_new else None,
                prefix='registry'
            )
        else:
            context['social_formset'] = SocialMediaFormSet(
                instance=self.object if not is_new else None,
                prefix='social'
            )
            context['registry_formset'] = RegistryFormSet(
                instance=self.object if not is_new else None,
                prefix='registry'
            )
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        is_new = context['is_new']
        
        social_formset = context.get('social_formset')
        registry_formset = context.get('registry_formset')
        
        # Validate all formsets
        formsets_valid = all([
            social_formset.is_valid() if social_formset else True,
            registry_formset.is_valid() if registry_formset else True
        ])
        
        if not formsets_valid:
            return self.form_invalid(form)
        
        with transaction.atomic():
            # Save the main profile
            form.instance.user = self.request.user
            old_slug = self.object.slug if self.object.pk else None
            self.object = form.save()
            new_slug = self.object.slug
            
            # Save formsets
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
            
            if registry_formset:
                registry_formset.instance = self.object
                registry_instances = registry_formset.save(commit=False)
                for registry in registry_instances:
                    registry.couple_profile = self.object
                    # Clean URL
                    if registry.url and not registry.url.startswith(('http://', 'https://')):
                        registry.url = 'https://' + registry.url
                    registry.save()
                # Handle deletions
                for obj in registry_formset.deleted_objects:
                    obj.delete()
        
        # Success messages
        if is_new:
            messages.success(
                self.request, 
                f"Your wedding page has been created successfully! Your custom URL is: {self.object.wedding_url_preview}. "
                f"Share this page with friends and family to let them find your registries and social media."
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
        registry_formset = context.get('registry_formset')
        
        if social_formset and not social_formset.is_valid():
            messages.error(self.request, "Please correct the errors in your social media links.")
        
        if registry_formset and not registry_formset.is_valid():
            messages.error(self.request, "Please correct the errors in your wedding registries.")
        
        return super().form_invalid(form)


@login_required
def couple_dashboard(request):
    """Dashboard redirects to the single manage page"""
    return redirect('wedding_shopping:manage_wedding_page')


def registry_redirect(request, pk):
    """Click tracking and redirect to registry"""
    registry = get_object_or_404(RegistryLink, pk=pk)
    registry.increment_clicks()
    return redirect(registry.url)


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
        url_type = request.GET.get('type', 'registry')  # 'registry' or 'social'
        
        if url_type == 'registry':
            branding = detect_registry_branding(url)
        else:
            branding = detect_social_platform(url)
        
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