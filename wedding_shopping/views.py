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
    model = CoupleProfile
    template_name = 'wedding_shopping/public_couple_detail.html'
    context_object_name = 'couple'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        # Only show public profiles
        return CoupleProfile.objects.filter(is_public=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        couple = self.object
        
        # Get wedding links
        wedding_links = couple.wedding_links.all().order_by('order', 'created_at')
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
    
    def get_enhanced_seo_data(self, couple):
        """Generate comprehensive SEO meta tags dynamically"""
        # Build dynamic title
        title_parts = [f"{couple.partner_1_name} & {couple.partner_2_name}"]
        if couple.wedding_date:
            title_parts.append("Wedding")
        else:
            title_parts.append("Wedding Page")
        
        # Generate comprehensive meta description
        meta_description_parts = [
            f"Join {couple.partner_1_name} & {couple.partner_2_name} as they celebrate their love"
        ]
        
        if couple.wedding_date:
            formatted_date = couple.wedding_date.strftime('%B %d, %Y')
            if couple.wedding_date > timezone.now().date():
                meta_description_parts.append(f"on {formatted_date}")
            else:
                meta_description_parts.append(f"- married {formatted_date}")
        
        if couple.venue_name:
            meta_description_parts.append(f"at {couple.venue_name}")
        
        if couple.venue_location:
            if couple.display_city:
                meta_description_parts.append(f"in {couple.display_city}")
            else:
                meta_description_parts.append(f"in {couple.venue_location}")
        
        # Add story preview if available
        if couple.couple_story:
            story_preview = couple.couple_story.strip()[:80]
            if len(couple.couple_story) > 80:
                story_preview = story_preview.rsplit(' ', 1)[0] + "..."
            meta_description_parts.append(f"- {story_preview}")
        
        meta_description = ". ".join(meta_description_parts)[:160]
        
        # Choose the best image for Open Graph
        og_image = None
        if couple.couple_photo:
            og_image = self.request.build_absolute_uri(couple.couple_photo.url)
        elif couple.venue_photo:
            og_image = self.request.build_absolute_uri(couple.venue_photo.url)
        
        # Build keywords
        keywords = [
            couple.partner_1_name,
            couple.partner_2_name,
            "wedding",
            "love story",
            "wedding page"
        ]
        
        if couple.venue_name:
            keywords.append(couple.venue_name)
        
        if couple.display_city:
            keywords.extend([couple.display_city, f"{couple.display_city} wedding"])
        
        if couple.wedding_date:
            keywords.extend([
                couple.wedding_date.strftime('%Y'),
                couple.wedding_date.strftime('%B %Y'),
                f"{couple.wedding_date.strftime('%B %Y')} wedding"
            ])
        
        # Build canonical URL
        canonical_url = self.request.build_absolute_uri(couple.get_absolute_url())
        
        return {
            'title': " - ".join(title_parts),
            'description': meta_description,
            'keywords': ", ".join(keywords),
            'og_image': og_image,
            'canonical_url': canonical_url,
            'wedding_date': couple.wedding_date,
            'venue_name': couple.venue_name,
            'venue_location': couple.venue_location,
            'couple_names': couple.couple_names,
            
            # Structured data components
            'schema_org': {
                'type': 'Event',
                'name': f"{couple.couple_names} Wedding",
                'description': meta_description,
                'url': canonical_url,
                'image': og_image,
                'startDate': couple.wedding_date.isoformat() if couple.wedding_date else None,
                'location': {
                    'name': couple.venue_name or couple.venue_location,
                    'address': couple.venue_location
                } if couple.venue_name or couple.venue_location else None,
                'organizer': {
                    'name': couple.couple_names,
                    'type': 'Person'
                }
            },
            
            # Social sharing optimized URLs
            'social_share': {
                'facebook': f"https://www.facebook.com/sharer/sharer.php?u={canonical_url}",
                'twitter': f"https://twitter.com/intent/tweet?url={canonical_url}&text={couple.couple_names} Wedding",
                'pinterest': f"https://pinterest.com/pin/create/button/?url={canonical_url}&description={meta_description}&media={og_image or ''}",
                'whatsapp': f"https://wa.me/?text={couple.couple_names} Wedding - {canonical_url}",
                'email': f"mailto:?subject={couple.couple_names} Wedding&body=Check out {couple.couple_names}'s wedding page: {canonical_url}"
            }
        }


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
        
        # Add SEO preview data for the form
        if not is_new:
            context['seo_preview'] = {
                'url_preview': self.object.wedding_url_preview,
                'share_url': self.request.build_absolute_uri(self.object.get_share_url()),
                'public_url': self.request.build_absolute_uri(self.object.get_absolute_url()) if self.object.is_public else None
            }
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        is_new = context['is_new']
        
        wedding_link_formset = context.get('wedding_link_formset')
        
        # Validate formset
        if wedding_link_formset and not wedding_link_formset.is_valid():
            return self.form_invalid(form)
        
        with transaction.atomic():
            # Save the main profile (images will be auto-optimized)
            form.instance.user = self.request.user
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
        
        # Enhanced success messages with sharing info
        if is_new:
            public_url = self.request.build_absolute_uri(self.object.get_absolute_url())
            share_url = self.request.build_absolute_uri(self.object.get_share_url())
            
            messages.success(
                self.request, 
                f"Your wedding page has been created! "
                f"{'Public URL: ' + public_url if self.object.is_public else 'Private sharing URL: ' + share_url}"
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


def public_couples_list(request):
    """Enhanced list of public couple profiles with SEO"""
    couples_list = CoupleProfile.objects.filter(is_public=True).order_by('-created_at')
    
    # Pagination: 42 couples per page (6 across, 7 down)
    paginator = Paginator(couples_list, 42)
    page_number = request.GET.get('page')
    couples = paginator.get_page(page_number)
    
    # Enhanced SEO data
    page_title = 'Wedding Celebrations'
    if page_number and page_number != '1':
        page_title += f' - Page {page_number}'
    
    context = {
        'couples': couples,
        'title': 'Wedding Celebrations',
        'seo_data': {
            'title': f'Discover {page_title} | DreamWedAI',
            'description': 'Browse beautiful wedding pages and love stories from couples around the world. Get inspired for your own wedding celebration.',
            'keywords': 'wedding pages, wedding stories, couple profiles, wedding inspiration, real weddings',
            'canonical_url': request.build_absolute_uri(),
            'schema_org': {
                'type': 'CollectionPage',
                'name': page_title,
                'description': 'A collection of beautiful wedding celebrations and love stories',
                'url': request.build_absolute_uri(),
                'numberOfItems': couples_list.count()
            }
        }
    }
    
    return render(request, 'wedding_shopping/public_couples_list.html', context)