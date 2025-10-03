from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import DetailView, UpdateView
from django.urls import reverse
from django.http import Http404
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
import urllib.parse

from .models import CoupleProfile, WeddingLink
from .forms import CoupleProfileForm, WeddingLinkFormSet


def generate_social_share_urls(request, title, description, image_url=None):
    """Helper function to generate social share URLs"""
    current_url = request.build_absolute_uri()
    encoded_url = urllib.parse.quote(current_url)
    encoded_title = urllib.parse.quote(title)
    encoded_desc = urllib.parse.quote(description)
    
    return {
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        'twitter': f"https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}",
        'pinterest': f"https://pinterest.com/pin/create/button/?url={encoded_url}&description={encoded_desc}&media={image_url or ''}",
        'whatsapp': f"https://wa.me/?text={encoded_title} - {encoded_url}",
        'email': f"mailto:?subject={title}&body={description} - {current_url}",
        'copy_link': current_url
    }


class PublicCoupleDetailView(DetailView):
    """View for displaying wedding pages - allows owners to preview even if not public"""
    model = CoupleProfile
    template_name = 'wedding_shopping/public_couple_detail.html'
    context_object_name = 'couple'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Return all profiles - we'll check permissions in get_object"""
        return CoupleProfile.objects.all()
    
    def get_object(self, queryset=None):
        """Get the couple profile, checking if user can view it"""
        if queryset is None:
            queryset = self.get_queryset()
        
        # Try to get by slug
        slug = self.kwargs.get(self.slug_url_kwarg)
        if slug:
            try:
                obj = queryset.get(slug=slug)
            except CoupleProfile.DoesNotExist:
                raise Http404("Wedding page not found")
        else:
            # Try to get by share_token
            share_token = self.kwargs.get('share_token')
            if share_token:
                try:
                    obj = queryset.get(share_token=share_token)
                except CoupleProfile.DoesNotExist:
                    raise Http404("Wedding page not found")
            else:
                raise Http404("Wedding page not found")
        
        # Check permissions
        is_owner = self.request.user.is_authenticated and obj.user == self.request.user
        
        # Allow access if:
        # 1. Page is public, OR
        # 2. User is the owner
        if not obj.is_public and not is_owner:
            raise Http404("This wedding page is not public yet")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        couple = self.object
        
        # Check if user is the owner
        is_owner = self.request.user.is_authenticated and couple.user == self.request.user
        context['is_owner'] = is_owner
        context['is_preview'] = is_owner and not couple.is_public
        
        # Get wedding links
        wedding_links = couple.wedding_links.all().order_by('created_at')
        context['wedding_links'] = wedding_links
        
        # Calculate countdown
        if couple.wedding_date:
            from datetime import date
            today = date.today()
            days_until = (couple.wedding_date - today).days
            
            context['days_until_wedding'] = days_until
            context['is_wedding_day'] = days_until == 0
            context['wedding_passed'] = days_until < 0
        
        # Generate social share URLs
        image_url = None
        if couple.couple_photo:
            image_url = self.request.build_absolute_uri(couple.couple_photo.url)
        
        description = f"Join {couple.couple_names} as they celebrate their wedding"
        if couple.wedding_date:
            description += f" on {couple.wedding_date.strftime('%B %d, %Y')}"
        if couple.venue_location:
            description += f" in {couple.venue_location}"
        description += "."
        
        context['social_share'] = generate_social_share_urls(
            request=self.request,
            title=f"{couple.couple_names} - Wedding Celebration",
            description=description,
            image_url=image_url
        )
        
        return context


class CoupleProfileManageView(LoginRequiredMixin, UpdateView):
    """Simplified view to create or update couple profile"""
    model = CoupleProfile
    form_class = CoupleProfileForm
    template_name = 'wedding_shopping/manage_couple_site.html'
    
    def get_object(self, queryset=None):
        """Get existing profile or return None for creation"""
        try:
            return CoupleProfile.objects.get(user=self.request.user)
        except CoupleProfile.DoesNotExist:
            return None
    
    def get_success_url(self):
        return reverse('wedding_shopping:manage_wedding_page')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        is_new = self.object is None or not self.object.pk
        context['is_new'] = is_new
        context['title'] = "Create Your Wedding Page" if is_new else "Manage Your Wedding Page"
        
        # Configure wedding links formset
        if self.request.POST:
            context['wedding_link_formset'] = WeddingLinkFormSet(
                self.request.POST, 
                instance=self.object if not is_new else None,
                prefix='weddinglink'
            )
        else:
            context['wedding_link_formset'] = WeddingLinkFormSet(
                instance=self.object if not is_new else None,
                prefix='weddinglink'
            )
        
        # Add preview/publish context
        if not is_new and self.object:
            context['page_url'] = self.request.build_absolute_uri(self.object.get_absolute_url())
            context['share_token_url'] = self.request.build_absolute_uri(self.object.get_share_url())
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission including publish action"""
        self.object = self.get_object()
        
        # Check if this is a publish action
        if 'publish_page' in request.POST:
            if self.object and self.object.pk:
                self.object.is_public = True
                self.object.save(update_fields=['is_public'])
                messages.success(request, "🎉 Your wedding page is now live and public!")
                return redirect(self.get_success_url())
            else:
                messages.error(request, "Please save your wedding page first before publishing.")
                return redirect(self.get_success_url())
        
        # Check if this is an unpublish action
        if 'unpublish_page' in request.POST:
            if self.object and self.object.pk:
                self.object.is_public = False
                self.object.save(update_fields=['is_public'])
                messages.info(request, "Your wedding page is now private.")
                return redirect(self.get_success_url())
        
        # Handle delete request
        if 'delete_wedding_page' in request.POST:
            if self.object and self.object.pk:
                self.object.delete()
                messages.success(request, "Your wedding page has been deleted.")
                return redirect('users:detail', username=request.user.username)
        
        # Handle photo deletions
        if self.object and self.object.pk:
            if 'delete_couple_photo' in request.POST:
                if self.object.couple_photo:
                    self.object.couple_photo.delete()
                    self.object.save(update_fields=['couple_photo'])
            
            if 'delete_venue_photo' in request.POST:
                if self.object.venue_photo:
                    self.object.venue_photo.delete()
                    self.object.save(update_fields=['venue_photo'])
        
        # Normal form submission
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        context = self.get_context_data()
        is_new = context['is_new']
        
        wedding_link_formset = context.get('wedding_link_formset')
        
        # Validate formset
        if wedding_link_formset and not wedding_link_formset.is_valid():
            return self.form_invalid(form)
        
        with transaction.atomic():
            # Save the main profile
            form.instance.user = self.request.user
            
            # For new profiles, keep them private by default
            if is_new:
                form.instance.is_public = False
            
            self.object = form.save()
            
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
                "✅ Your wedding page has been created! Review it below, then click 'Publish' to make it live."
            )
        else:
            messages.success(self.request, "✅ Your wedding page has been updated successfully!")
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        messages.error(self.request, "❌ Please correct the errors below.")
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


def public_couples_list(request):
    """List of public couple profiles - ONLY shows published pages"""
    couples_list = CoupleProfile.objects.filter(is_public=True).order_by('-created_at')
    
    # Pagination: 42 couples per page
    paginator = Paginator(couples_list, 42)
    page_number = request.GET.get('page')
    couples = paginator.get_page(page_number)
    
    context = {
        'couples': couples,
        'title': 'Wedding Celebrations',
    }
    
    return render(request, 'wedding_shopping/public_couples_list.html', context)