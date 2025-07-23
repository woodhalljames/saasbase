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

from .models import CoupleProfile, RegistryLink, SocialMediaLink, WeddingPhotoCollection
from .forms import (
    CoupleProfileForm, SocialMediaFormSet, RegistryFormSet, 
    PhotoCollectionFormSet
)


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
            'collections_count': couple_profile.photo_collections.count(),
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
            # Token-based lookup (fallback method)
            return get_object_or_404(CoupleProfile, share_token=share_token)
        elif slug:
            # Custom slug lookup (primary method)
            couple = get_object_or_404(CoupleProfile, slug=slug)
            
            # If this is a private page accessed without token, check if it should be public
            if not couple.is_public and not self.request.user == couple.user:
                # Redirect to token-based URL for private sharing
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
        
        # Get related data
        context['social_links'] = couple.social_links.all()
        context['registry_links'] = couple.registry_links.all()
        context['photo_collections'] = couple.photo_collections.filter(is_featured=True)
        
        # Try to get actual collection data from image_processing app
        collections_with_images = []
        for collection in context['photo_collections']:
            if collection.studio_collection_id:
                try:
                    # Try to import and get collection data
                    from image_processing.models import Collection, CollectionItem
                    studio_collection = Collection.objects.get(
                        id=collection.studio_collection_id,
                        user=couple.user
                    )
                    # Get sample images from the collection
                    sample_items = CollectionItem.objects.filter(
                        collection=studio_collection
                    )[:6]  # Show up to 6 images
                    
                    collections_with_images.append({
                        'collection': collection,
                        'studio_collection': studio_collection,
                        'sample_items': sample_items
                    })
                except:
                    # If collection doesn't exist or import fails, just add the collection info
                    collections_with_images.append({
                        'collection': collection,
                        'studio_collection': None,
                        'sample_items': []
                    })
            else:
                collections_with_images.append({
                    'collection': collection,
                    'studio_collection': None,
                    'sample_items': []
                })
        
        context['collections_with_images'] = collections_with_images
        
        return context


class CoupleProfileManageView(LoginRequiredMixin, UpdateView):
    """Single view to create or update couple profile"""
    model = CoupleProfile
    form_class = CoupleProfileForm
    template_name = 'wedding_shopping/couple_manage.html'
    
    def get_object(self, queryset=None):
        """Get existing profile or create a new one"""
        try:
            return CoupleProfile.objects.get(user=self.request.user)
        except CoupleProfile.DoesNotExist:
            # Return a new unsaved instance
            return CoupleProfile(user=self.request.user)
    
    def get_success_url(self):
        return reverse('wedding_shopping:manage_wedding_page')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Determine if this is create or update mode
        is_new = not self.object.pk
        context['is_new'] = is_new
        context['title'] = "Create Your Wedding Page" if is_new else "Manage Your Wedding Page"
        
        if self.request.POST:
            # Only show formsets if we have an existing object
            if not is_new:
                context['social_formset'] = SocialMediaFormSet(
                    self.request.POST, instance=self.object
                )
                context['registry_formset'] = RegistryFormSet(
                    self.request.POST, instance=self.object
                )
                context['photo_formset'] = PhotoCollectionFormSet(
                    self.request.POST, instance=self.object
                )
        else:
            if not is_new:
                context['social_formset'] = SocialMediaFormSet(instance=self.object)
                context['registry_formset'] = RegistryFormSet(instance=self.object)
                context['photo_formset'] = PhotoCollectionFormSet(instance=self.object)
        
        # Get user's collections from image_processing app for easier selection
        try:
            from image_processing.models import Collection
            context['user_collections'] = Collection.objects.filter(
                user=self.request.user
            ).exclude(is_default=True)
        except:
            context['user_collections'] = []
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        is_new = context['is_new']
        
        # For new profiles, just save the basic form first
        if is_new:
            form.instance.user = self.request.user
            self.object = form.save()
            
            # Show success message with custom URL preview
            messages.success(
                self.request, 
                f"Your wedding page has been created! Your custom URL is: {self.object.wedding_url_preview}"
            )
            return redirect(self.get_success_url())
        
        # For existing profiles, handle all formsets
        social_formset = context.get('social_formset')
        registry_formset = context.get('registry_formset')
        photo_formset = context.get('photo_formset')
        
        with transaction.atomic():
            # Check if URL-affecting fields changed
            old_slug = self.object.slug if self.object.pk else None
            self.object = form.save()
            new_slug = self.object.slug
            
            if social_formset and social_formset.is_valid():
                social_formset.instance = self.object
                social_formset.save()
            
            if registry_formset and registry_formset.is_valid():
                registry_formset.instance = self.object
                # Process affiliate URLs here if needed
                for registry_form in registry_formset:
                    if registry_form.cleaned_data and not registry_form.cleaned_data.get('DELETE'):
                        registry = registry_form.save(commit=False)
                        registry.couple_profile = self.object
                        # TODO: Add affiliate URL processing here
                        registry.save()
                registry_formset.save()
            
            if photo_formset and photo_formset.is_valid():
                photo_formset.instance = self.object
                photo_formset.save()
        
        # Show different message if URL changed
        if old_slug != new_slug:
            messages.success(
                self.request, 
                f"Your wedding page has been updated! Your custom URL is now: {self.object.wedding_url_preview}"
            )
        else:
            messages.success(self.request, "Your wedding page has been updated!")
        
        return super().form_valid(form)


@login_required
def couple_dashboard(request):
    """Dashboard redirects to the single manage page"""
    return redirect('wedding_shopping:manage_wedding_page')


def registry_redirect(request, pk):
    """Simple click tracking and redirect to registry"""
    registry = get_object_or_404(RegistryLink, pk=pk)
    
    # Track the click
    registry.increment_clicks()
    
    # Redirect directly to original URL (no affiliate logic for now)
    return redirect(registry.original_url)


def legacy_couple_redirect(request, slug=None, share_token=None):
    """Redirect old /couple/ URLs to new /wedding/ format"""
    if share_token:
        # Redirect token-based legacy URL
        return redirect('wedding_shopping:wedding_page_token', share_token=share_token)
    elif slug:
        # Redirect slug-based legacy URL
        return redirect('wedding_shopping:wedding_page', slug=slug)
    else:
        # Fallback to discovery page
        return redirect('wedding_shopping:public_couples_list')


# API views for AJAX functionality
def get_collections_api(request):
    """API endpoint to get user's collections for selection"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        from image_processing.models import Collection
        collections = Collection.objects.filter(
            user=request.user
        ).exclude(is_default=True).values('id', 'name', 'item_count')
        
        return JsonResponse({
            'collections': list(collections)
        })
    except ImportError:
        return JsonResponse({'collections': []})


# Simple view to list all public couples (optional discovery page)
def public_couples_list(request):
    """Optional: List all public couple profiles"""
    couples = CoupleProfile.objects.filter(is_public=True).order_by('-created_at')
    
    context = {
        'couples': couples,
        'title': 'Wedding Celebrations'
    }
    
    return render(request, 'wedding_shopping/public_couples_list.html', context)