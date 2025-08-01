# wedding_shopping/models.py - Enhanced with partner-specific social media and expanded link types
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid
from django.utils.text import slugify
import re
from urllib.parse import urlparse

User = get_user_model()


class CoupleProfile(models.Model):
    """Main model for a couple's wedding profile"""
    
    # Basic Info
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='couple_profile')
    partner_1_name = models.CharField(max_length=100, help_text="First partner's name")
    partner_2_name = models.CharField(max_length=100, help_text="Second partner's name")
    
    # Wedding Details
    wedding_date = models.DateField(null=True, blank=True)
    venue_name = models.CharField(max_length=200, blank=True)
    venue_location = models.CharField(max_length=200, blank=True, help_text="City, State")
    
    # Images
    couple_photo = models.ImageField(upload_to='couple_photos/', null=True, blank=True)
    venue_photo = models.ImageField(upload_to='venue_photos/', null=True, blank=True)
    
    # Story
    couple_story = models.TextField(blank=True, help_text="Tell your love story")
    
    # Sharing & Privacy
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_public = models.BooleanField(default=False, help_text="Make this profile publicly accessible")
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Couple Profile"
        verbose_name_plural = "Couple Profiles"
    
    def __str__(self):
        return f"{self.partner_1_name} & {self.partner_2_name}"
    
    def _clean_name(self, name):
        """Clean name for URL: remove spaces, special chars, keep only alphanumeric"""
        if not name:
            return ""
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        return cleaned[:15]
    
    def _generate_wedding_slug(self):
        """Generate slug in format: name1name2MMDDYY"""
        name1 = self._clean_name(self.partner_1_name)
        name2 = self._clean_name(self.partner_2_name)
        
        if self.wedding_date:
            date_str = self.wedding_date.strftime('%m%d%y')
        else:
            date_str = 'tbd'
        
        base_slug = f"{name1}{name2}{date_str}"
        
        if not base_slug or len(base_slug) < 3:
            base_slug = f"wedding{self.pk or 'new'}"
        
        return base_slug
    
    def save(self, *args, **kwargs):
        if not self.slug or self._should_regenerate_slug():
            base_slug = self._generate_wedding_slug()
            counter = 1
            self.slug = base_slug
            
            while CoupleProfile.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}{counter}"
                counter += 1
                if counter > 999:
                    self.slug = f"{base_slug}{uuid.uuid4().hex[:4]}"
                    break
        
        super().save(*args, **kwargs)
    
    def _should_regenerate_slug(self):
        if not self.pk:
            return True
        
        try:
            original = CoupleProfile.objects.get(pk=self.pk)
            return (
                original.partner_1_name != self.partner_1_name or
                original.partner_2_name != self.partner_2_name or
                original.wedding_date != self.wedding_date
            )
        except CoupleProfile.DoesNotExist:
            return True
    
    def get_absolute_url(self):
        return reverse('wedding_shopping:wedding_page', kwargs={'slug': self.slug})
    
    def get_public_url(self):
        return self.get_absolute_url()
    
    def get_share_url(self):
        return reverse('wedding_shopping:wedding_page_token', kwargs={'share_token': str(self.share_token)})
    
    @property
    def couple_names(self):
        return f"{self.partner_1_name} & {self.partner_2_name}"
    
    @property
    def wedding_url_preview(self):
        return f"/wedding/{self.slug}/" if self.slug else "/wedding/[will-be-generated]/"
    
    # Helper methods for social media organization
    @property
    def partner_1_social_links(self):
        return self.social_links.filter(owner='partner_1')
    
    @property
    def partner_2_social_links(self):
        return self.social_links.filter(owner='partner_2')
    
    @property
    def shared_social_links(self):
        return self.social_links.filter(owner='shared')
    
    # Helper methods for wedding links by category
    @property
    def registry_links(self):
        return self.wedding_links.filter(link_type='registry')
    
    @property
    def rsvp_links(self):
        return self.wedding_links.filter(link_type='rsvp')
    
    @property
    def livestream_links(self):
        return self.wedding_links.filter(link_type='livestream')
    
    @property
    def photo_links(self):
        return self.wedding_links.filter(link_type='photos')
    
    @property
    def other_links(self):
        return self.wedding_links.filter(link_type='other')


class SocialMediaLink(models.Model):
    """Enhanced social media links with partner ownership"""
    
    OWNER_CHOICES = [
        ('partner_1', 'Partner 1'),
        ('partner_2', 'Partner 2'),  
        ('shared', 'Both/Shared'),
    ]
    
    couple_profile = models.ForeignKey(CoupleProfile, on_delete=models.CASCADE, related_name='social_links')
    owner = models.CharField(max_length=20, choices=OWNER_CHOICES, default='shared')
    url = models.URLField()
    display_name = models.CharField(max_length=100, blank=True, help_text="Display name (e.g., @username)")
    
    class Meta:
        unique_together = ['couple_profile', 'url']
        ordering = ['owner', 'id']
    
    def __str__(self):
        owner_display = dict(self.OWNER_CHOICES).get(self.owner, self.owner)
        return f"{self.couple_profile} - {owner_display} - {self.display_name or self.url}"
    
    def _detect_platform_from_url(self):
        """Auto-detect platform from URL"""
        if not self.url:
            return 'other'
        
        domain = urlparse(self.url).netloc.lower()
        
        platform_patterns = {
            'instagram': ['instagram.com', 'instagr.am'],
            'facebook': ['facebook.com', 'fb.com'],
            'twitter': ['twitter.com', 'x.com'],
            'tiktok': ['tiktok.com'],
            'youtube': ['youtube.com', 'youtu.be'],
            'pinterest': ['pinterest.com'],
            'linkedin': ['linkedin.com'],
        }
        
        for platform, patterns in platform_patterns.items():
            if any(pattern in domain for pattern in patterns):
                return platform
        
        return 'website' if any(tld in domain for tld in ['.com', '.org', '.net']) else 'other'
    
    @property
    def platform(self):
        """Returns detected platform"""
        return self._detect_platform_from_url()
    
    @property
    def platform_icon(self):
        """Returns Bootstrap icon class for the platform"""
        icons = {
            'instagram': 'bi-instagram',
            'facebook': 'bi-facebook',
            'twitter': 'bi-twitter-x',
            'tiktok': 'bi-tiktok',
            'youtube': 'bi-youtube',
            'pinterest': 'bi-pinterest',
            'linkedin': 'bi-linkedin',
            'website': 'bi-globe',
            'other': 'bi-link-45deg',
        }
        return icons.get(self.platform, 'bi-link-45deg')

    @property
    def platform_color(self):
        """Returns brand color for the platform"""
        colors = {
            'instagram': '#E4405F',
            'facebook': '#1877F2',
            'twitter': '#000000',
            'tiktok': '#FF0050',
            'youtube': '#FF0000',
            'pinterest': '#BD081C',
            'linkedin': '#0A66C2',
            'website': '#007bff',
            'other': '#6c757d',
        }
        return colors.get(self.platform, '#6c757d')
    
    @property
    def platform_display_name(self):
        """Returns the display name to show on the wedding page"""
        return self.display_name or self.url
    
    @property
    def owner_display_name(self):
        """Return the display name for the owner"""
        if self.owner == 'partner_1':
            return self.couple_profile.partner_1_name
        elif self.owner == 'partner_2':
            return self.couple_profile.partner_2_name
        else:
            return "Both"


class WeddingLink(models.Model):
    """Enhanced link model for registries, RSVP, livestreams, and other wedding content"""
    
    LINK_TYPE_CHOICES = [
        ('registry', 'Wedding Registry'),
        ('rsvp', 'RSVP Site'),
        ('livestream', 'Live Stream'),
        ('photos', 'Wedding Photos'),
        ('website', 'Wedding Website'),
        ('other', 'Other'),
    ]
    
    couple_profile = models.ForeignKey(CoupleProfile, on_delete=models.CASCADE, related_name='wedding_links')
    link_type = models.CharField(max_length=20, choices=LINK_TYPE_CHOICES, default='registry')
    url = models.URLField(help_text="Link URL")
    title = models.CharField(max_length=100, help_text="Title for this link")
    description = models.TextField(blank=True, help_text="Description of this link")
    
    # Tracking
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['link_type', 'created_at']
    
    def __str__(self):
        return f"{self.couple_profile} - {self.get_link_type_display()} - {self.title}"
    
    def _detect_service_from_url(self):
        """Auto-detect service type from URL"""
        if not self.url:
            return 'other'
        
        domain = urlparse(self.url).netloc.lower()
        
        service_patterns = {
            # Registries
            'amazon': ['amazon.com', 'amzn.com'],
            'target': ['target.com'],
            'bed_bath_beyond': ['bedbathandbeyond.com', 'buybuybaby.com'],
            'williams_sonoma': ['williams-sonoma.com', 'williamssonoma.com'],
            'crate_barrel': ['crateandbarrel.com', 'cb2.com'],
            'pottery_barn': ['potterybarn.com', 'pbteen.com', 'pbkids.com'],
            'macy': ['macys.com'],
            'zola': ['zola.com'],
            'the_knot': ['theknot.com'],
            'wayfair': ['wayfair.com'],
            'honeyfund': ['honeyfund.com'],
            
            # RSVP Sites
            'rsvpify': ['rsvpify.com'],
            'wedding_wire': ['rsvp.weddingwire.com'],
            'anrsvp': ['anrsvp.com'],
            'withjoy': ['withjoy.com'],
            
            # Livestream
            'zoom': ['zoom.us', 'zoom.com'],
            'youtube_live': ['youtube.com/watch', 'youtu.be'],
            'facebook_live': ['facebook.com'],
            'instagram_live': ['instagram.com'],
            
            # Photo sharing
            'google_photos': ['photos.google.com', 'photos.app.goo.gl'],
            'dropbox': ['dropbox.com'],
            'shutterfly': ['shutterfly.com'],
            'smugmug': ['smugmug.com'],
        }
        
        for service_type, patterns in service_patterns.items():
            if any(pattern in domain for pattern in patterns):
                return service_type
        
        return 'custom'
    
    @property
    def service_type(self):
        """Returns detected service type"""
        return self._detect_service_from_url()
    
    @property
    def service_icon(self):
        """Returns appropriate Bootstrap icon based on link type and detected service"""
        link_type_icons = {
            'registry': 'bi-gift',
            'rsvp': 'bi-envelope-check',
            'livestream': 'bi-camera-video',
            'photos': 'bi-camera',
            'website': 'bi-globe',
            'other': 'bi-link-45deg',
        }
        
        # Service-specific icons
        service_icons = {
            'amazon': 'bi-amazon',
            'target': 'bi-bullseye',
            'zoom': 'bi-camera-video',
            'youtube_live': 'bi-youtube',
            'facebook_live': 'bi-facebook',
            'google_photos': 'bi-google',
            'dropbox': 'bi-dropbox',
        }
        
        # Try service-specific icon first, then link type icon
        return service_icons.get(self.service_type, link_type_icons.get(self.link_type, 'bi-link-45deg'))

    @property
    def service_color(self):
        """Returns brand color based on detected service"""
        colors = {
            # Registries
            'amazon': '#FF9900',
            'target': '#CC0000',
            'bed_bath_beyond': '#003087',
            'williams_sonoma': '#8B4513',
            'crate_barrel': '#000000',
            'pottery_barn': '#8B4513',
            'macy': '#E21937',
            'zola': '#FF6B6B',
            'the_knot': '#FF69B4',
            'wayfair': '#663399',
            'honeyfund': '#FFA500',
            
            # RSVP
            'rsvpify': '#007bff',
            'wedding_wire': '#28a745',
            'anrsvp': '#6f42c1',
            'withjoy': '#fd7e14',
            
            # Livestream
            'zoom': '#2D8CFF',
            'youtube_live': '#FF0000',
            'facebook_live': '#1877F2',
            'instagram_live': '#E4405F',
            
            # Photos
            'google_photos': '#4285F4',
            'dropbox': '#0061FF',
            'shutterfly': '#00A651',
            'smugmug': '#6DB33F',
        }
        
        link_type_colors = {
            'registry': '#007bff',
            'rsvp': '#28a745', 
            'livestream': '#dc3545',
            'photos': '#6f42c1',
            'website': '#17a2b8',
            'other': '#6c757d',
        }
        
        return colors.get(self.service_type, link_type_colors.get(self.link_type, '#6c757d'))
    
    @property
    def display_title(self):
        """Returns the title to display on the wedding page"""
        return self.title
    
    def increment_clicks(self):
        """Increment click count"""
        self.click_count += 1
        self.save(update_fields=['click_count'])
    
    @property
    def final_url(self):
        """Returns the URL to redirect to"""
        return self.url


# For backwards compatibility, keep RegistryLink as an alias
RegistryLink = WeddingLink