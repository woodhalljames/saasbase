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
        """Get couple by share_token or slug"""
        share_token = self.kwargs.get('share_token')
        slug = self.kwargs.get('slug')
        
        if share_token:
            return get_object_or_404(CoupleProfile, share_token=share_token)
        elif slug:
            return get_object_or_404(CoupleProfile, slug=slug, is_public=True)
        else:
            raise Http404("Couple profile not found")
    
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


class CoupleProfileCreateView(LoginRequiredMixin, CreateView):
    """Create a new couple profile"""
    model = CoupleProfile
    form_class = CoupleProfileForm
    template_name = 'wedding_shopping/couple_form.html'
    
    def get_success_url(self):
        return reverse('wedding_shopping:couple_manage', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Create Your Wedding Page"
        return context


class CoupleProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update couple profile with all related data"""
    model = CoupleProfile
    form_class = CoupleProfileForm
    template_name = 'wedding_shopping/couple_manage.html'
    
    def get_queryset(self):
        return CoupleProfile.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse('wedding_shopping:couple_manage', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
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
        
        context['title'] = "Manage Your Wedding Page"
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        social_formset = context['social_formset']
        registry_formset = context['registry_formset']
        photo_formset = context['photo_formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if social_formset.is_valid():
                social_formset.instance = self.object
                social_formset.save()
            
            if registry_formset.is_valid():
                registry_formset.instance = self.object
                # Process affiliate URLs here if needed
                for registry_form in registry_formset:
                    if registry_form.cleaned_data and not registry_form.cleaned_data.get('DELETE'):
                        registry = registry_form.save(commit=False)
                        registry.couple_profile = self.object
                        # TODO: Add affiliate URL processing here
                        registry.save()
                registry_formset.save()
            
            if photo_formset.is_valid():
                photo_formset.instance = self.object
                photo_formset.save()
        
        messages.success(self.request, "Your wedding page has been updated!")
        return super().form_valid(form)


@login_required
def couple_dashboard(request):
    """Dashboard for managing couple profile"""
    try:
        couple_profile = CoupleProfile.objects.get(user=request.user)
        return redirect('wedding_shopping:couple_manage', pk=couple_profile.pk)
    except CoupleProfile.DoesNotExist:
        return redirect('wedding_shopping:couple_create')


def registry_redirect(request, pk):
    """Simple click tracking and redirect to registry"""
    registry = get_object_or_404(RegistryLink, pk=pk)
    
    # Track the click
    registry.increment_clicks()
    
    # Redirect directly to original URL (no affiliate logic for now)
    return redirect(registry.original_url)


def couple_detail_redirect(request, pk):
    """Redirect to public couple page"""
    couple = get_object_or_404(CoupleProfile, pk=pk, user=request.user)
    return redirect(couple.get_public_url())


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