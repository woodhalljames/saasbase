# wedding_shopping/views.py - Simplified for elegant frontend
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

from .models import CoupleProfile, WeddingLink
from .forms import CoupleProfileForm, WeddingLinkFormSet


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
            
            # Allow viewing private pages via direct slug if user owns it
            if not couple.is_public and self.request.user != couple.user:
                # Redirect to token-based URL for private pages
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
        
        # Get all wedding links
        context['wedding_links'] = couple.wedding_links.all().order_by('id')
        
        return context


class CoupleProfileManageView(LoginRequiredMixin, UpdateView):
    """Simplified view to create or update couple profile"""
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
        
        return context
    
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
            old_slug = self.object.slug if self.object.pk else None
            self.object = form.save()
            new_slug = self.object.slug
            
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
                f"Your wedding page has been created! Share this link: {self.request.build_absolute_uri(self.object.get_absolute_url())}"
            )
        elif old_slug != new_slug:
            messages.success(
                self.request, 
                f"Your wedding page has been updated! Your new URL is: {self.object.wedding_url_preview}"
            )
        else:
            messages.success(self.request, "Your wedding page has been updated successfully!")
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        if form.errors:
            messages.error(self.request, "Please correct the errors in your wedding details.")
        
        context = self.get_context_data()
        wedding_link_formset = context.get('wedding_link_formset')
        
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


def legacy_couple_redirect(request, slug=None, share_token=None):
    """Redirect old /couple/ URLs to new /wedding/ format"""
    if share_token:
        return redirect('wedding_shopping:wedding_page_token', share_token=share_token)
    elif slug:
        return redirect('wedding_shopping:wedding_page', slug=slug)
    else:
        return redirect('wedding_shopping:public_couples_list')


def public_couples_list(request):
    """Compact list of public couple profiles with pagination"""
    couples_list = CoupleProfile.objects.filter(is_public=True).order_by('-created_at')
    
    # Pagination: 42 couples per page (6 across, 7 down)
    paginator = Paginator(couples_list, 42)
    page_number = request.GET.get('page')
    couples = paginator.get_page(page_number)
    
    context = {
        'couples': couples,
        'title': 'Wedding Celebrations'
    }
    
    return render(request, 'wedding_shopping/public_couples_list.html', context)