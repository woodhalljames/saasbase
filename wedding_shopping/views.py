# wedding_shopping/views.py
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
    """Detect registry type and branding from URL"""
    if not url:
        return {'type': 'other', 'name': '', 'icon': 'bi-gift'}
    
    url_lower = url.lower()
    domain = urlparse(url).netloc.lower()
    
    registry_patterns = {
        'amazon': {
            'patterns': ['amazon.com', 'amzn.com'],
            'name': 'Amazon',
            'icon': 'bi-amazon',
            'color': '#FF9900'
        },
        'target': {
            'patterns': ['target.com'],
            'name': 'Target',
            'icon': 'bi-bullseye',
            'color': '#CC0000'
        },
        'bed_bath_beyond': {
            'patterns': ['bedbathandbeyond.com', 'buybuybaby.com'],
            'name': 'Bed Bath & Beyond',
            'icon': 'bi-house-fill',
            'color': '#003087'
        },
        'williams_sonoma': {
            'patterns': ['williams-sonoma.com', 'williamssonoma.com'],
            'name': 'Williams Sonoma',
            'icon': 'bi-cup-hot-fill',
            'color': '#8B4513'
        },
        'crate_barrel': {
            'patterns': ['crateandbarrel.com', 'cb2.com'],
            'name': 'Crate & Barrel',
            'icon': 'bi-house-door-fill',
            'color': '#000000'
        },
        'pottery_barn': {
            'patterns': ['potterybarn.com', 'pbteen.com', 'pbkids.com'],
            'name': 'Pottery Barn',
            'icon': 'bi-home-fill',
            'color': '#8B4513'
        },
        'macy': {
            'patterns': ['macys.com'],
            'name': "Macy's",
            'icon': 'bi-bag-fill',
            'color': '#E21937'
        },
        'zola': {
            'patterns': ['zola.com'],
            'name': 'Zola',
            'icon': 'bi-heart-fill',
            'color': '#FF6B6B'
        },
        'the_knot': {
            'patterns': ['theknot.com'],
            'name': 'The Knot',
            'icon': 'bi-heart',
            'color': '#FF69B4'
        },
        'wayfair': {
            'patterns': ['wayfair.com'],
            'name': 'Wayfair',
            'icon': 'bi-house-fill',
            'color': '#663399'
        }
    }
    
    for registry_type, config in registry_patterns.items():
        if any(pattern in domain for pattern in config['patterns']):
            return {
                'type': registry_type,
                'name': config['name'],
                'icon': config['icon'],
                'color': config.get('color', '#007bff')
            }
    
    return {'type': 'other', 'name': '', 'icon': 'bi-gift', 'color': '#6c757d'}


def detect_social_platform(url):
    """Detect social media platform from URL"""
    if not url:
        return {'platform': 'other', 'icon': 'bi-link-45deg'}
    
    url_lower = url.lower()
    domain = urlparse(url).netloc.lower()
    
    platform_patterns = {
        'instagram': {
            'patterns': ['instagram.com', 'instagr.am'],
            'icon': 'bi-instagram'
        },
        'facebook': {
            'patterns': ['facebook.com', 'fb.com'],
            'icon': 'bi-facebook'
        },
        'twitter': {
            'patterns': ['twitter.com', 'x.com'],
            'icon': 'bi-twitter'
        },
        'tiktok': {
            'patterns': ['tiktok.com'],
            'icon': 'bi-tiktok'
        },
        'website': {
            'patterns': ['www.', '.com', '.org', '.net'],
            'icon': 'bi-globe'
        }
    }
    
    for platform, config in platform_patterns.items():
        if any(pattern in domain for pattern in config['patterns']):
            return {
                'platform': platform,
                'icon': config['icon']
            }
    
    return {'platform': 'other', 'icon': 'bi-link-45deg'}


def get_user_wedding_context(user):
    """Helper function to get wedding-related context for user dashboard"""
    context = {
        'has_couple_profile': False,
        'couple_profile': None,
        'wedding_stats': None,
    }
    
    try:
        couple_profile = CoupleProfile.objects.get(user=user)
        context['has_couple_profile'] = True
        context['couple_profile'] = couple_profile
        
        # Calculate wedding stats
        stats = {
            'registries_count': couple_profile.registry_links.count(),
            'social_links_count': couple_profile.social_links.count(),
            'total_clicks': sum(r.click_count for r in couple_profile.registry_links.all()),
        }
        
        # Days until wedding
        if couple_profile.wedding_date:
            today = timezone.now().date()
            if couple_profile.wedding_date > today:
                stats['days_until_wedding'] = (couple_profile.wedding_date - today).days
            elif couple_profile.wedding_date == today:
                stats['is_wedding_day'] = True
            else:
                stats['wedding_passed'] = True
                stats['days_since_wedding'] = (today - couple_profile.wedding_date).days
        
        context['wedding_stats'] = stats
        
    except CoupleProfile.DoesNotExist:
        pass
    
    return context


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
        
        # Get photo collections for wedding venue transformations
        context['collections_with_images'] = []
        try:
            photo_collections = couple.photo_collections.filter(is_featured=True)
            for collection in photo_collections:
                collection_data = {
                    'collection': collection,
                    'sample_items': [],  # You can populate this if you have image processing integration
                    'studio_collection': None  # You can populate this if you have studio integration
                }
                context['collections_with_images'].append(collection_data)
        except AttributeError:
            # photo_collections relationship doesn't exist yet
            pass
        
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
        
        # Configure formsets with proper minimum forms
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
            # For new profiles, ensure we have at least 2 empty forms for each
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
                    social.save()
                # Handle deletions
                for obj in social_formset.deleted_objects:
                    obj.delete()
            
            if registry_formset:
                registry_formset.instance = self.object
                registry_instances = registry_formset.save(commit=False)
                for registry in registry_instances:
                    registry.couple_profile = self.object
                    
                    # Auto-detect registry type if not set
                    if not registry.registry_type or registry.registry_type == 'other':
                        branding = detect_registry_branding(registry.original_url)
                        if branding['type'] != 'other':
                            registry.registry_type = branding['type']
                            if not registry.display_name:
                                registry.display_name = branding['name']
                    
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
    return redirect(registry.original_url)


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
        
        return JsonResponse(branding)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def public_couples_list(request):
    """List all public couple profiles"""
    couples = CoupleProfile.objects.filter(is_public=True).order_by('-created_at')
    
    context = {
        'couples': couples,
        'title': 'Wedding Celebrations'
    }
    
    return render(request, 'wedding_shopping/public_couples_list.html', context)