# wedding_shopping/models.py - Enhanced with better branding support
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid
from django.utils.text import slugify
import re
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
        # Remove spaces and special characters, keep only letters and numbers
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        # Limit length to prevent super long URLs
        return cleaned[:15]
    
    def _generate_wedding_slug(self):
        """Generate slug in format: name1name2MMDDYY"""
        # Clean the names
        name1 = self._clean_name(self.partner_1_name)
        name2 = self._clean_name(self.partner_2_name)
        
        # If no wedding date, use a placeholder
        if self.wedding_date:
            date_str = self.wedding_date.strftime('%m%d%y')
        else:
            date_str = 'tbd'  # "to be determined"
        
        # Combine into base slug
        base_slug = f"{name1}{name2}{date_str}"
        
        # Ensure we have something
        if not base_slug or len(base_slug) < 3:
            base_slug = f"wedding{self.pk or 'new'}"
        
        return base_slug
    
    def save(self, *args, **kwargs):
        # Generate custom slug if not exists or if names/date changed
        if not self.slug or self._should_regenerate_slug():
            base_slug = self._generate_wedding_slug()
            
            # Ensure uniqueness by adding number suffix if needed
            counter = 1
            self.slug = base_slug
            
            # Check for existing slugs and increment if needed
            while CoupleProfile.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}{counter}"
                counter += 1
                # Prevent infinite loop
                if counter > 999:
                    self.slug = f"{base_slug}{uuid.uuid4().hex[:4]}"
                    break
        
        super().save(*args, **kwargs)
    
    def _should_regenerate_slug(self):
        """Check if slug should be regenerated based on changed fields"""
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
        """Return the custom wedding URL"""
        return reverse('wedding_shopping:wedding_page', kwargs={'slug': self.slug})
    
    def get_public_url(self):
        """Return the public URL (same as absolute for now)"""
        return self.get_absolute_url()
    
    def get_share_url(self):
        """Return shareable URL using token (fallback)"""
        return reverse('wedding_shopping:wedding_page_token', kwargs={'share_token': str(self.share_token)})
    
    @property
    def couple_names(self):
        return f"{self.partner_1_name} & {self.partner_2_name}"
    
    @property
    def wedding_url_preview(self):
        """Show what the URL will look like"""
        return f"/wedding/{self.slug}/" if self.slug else "/wedding/[will-be-generated]/"


class SocialMediaLink(models.Model):
    """Social media profiles for the couple with enhanced branding"""
    
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('twitter', 'X (Twitter)'),
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube'),
        ('pinterest', 'Pinterest'),
        ('linkedin', 'LinkedIn'),
        ('other', 'Other'),
    ]
    
    couple_profile = models.ForeignKey(CoupleProfile, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    platform_name = models.CharField(max_length=50, blank=True, help_text="Custom platform name if 'Other'")
    url = models.URLField()
    display_name = models.CharField(max_length=100, blank=True, help_text="Display name (e.g., @username)")
    
    class Meta:
        unique_together = ['couple_profile', 'platform', 'url']
    
    def __str__(self):
        return f"{self.couple_profile} - {self.get_platform_display()}"
    
    @property
    def platform_icon(self):
        """Returns Bootstrap icon class for the platform with fallback"""
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
        return icons.get(self.platform, 'bi-link-45deg')  # Always returns something

    @property
    def platform_color(self):
        """Returns brand color for the platform with fallback"""
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
        return colors.get(self.platform, '#6c757d')  # Always returns something
    
    @property
    def platform_display_name(self):
        """Returns the display name to show on the wedding page"""
        if self.display_name:
            return self.display_name
        elif self.platform_name:
            return self.platform_name
        else:
            return self.get_platform_display()


class RegistryLink(models.Model):
    """Wedding registry links with enhanced branding and tracking"""
    
    REGISTRY_TYPES = [
        ('amazon', 'Amazon'),
        ('target', 'Target'),
        ('bed_bath_beyond', 'Bed Bath & Beyond'),
        ('williams_sonoma', 'Williams Sonoma'),
        ('crate_barrel', 'Crate & Barrel'),
        ('pottery_barn', 'Pottery Barn'),
        ('macy', 'Macy\'s'),
        ('zola', 'Zola'),
        ('the_knot', 'The Knot'),
        ('wayfair', 'Wayfair'),
        ('registry_finder', 'Registry Finder'),
        ('honeyfund', 'Honeyfund'),
        ('other', 'Other'),
    ]
    
    couple_profile = models.ForeignKey(CoupleProfile, on_delete=models.CASCADE, related_name='registry_links')
    registry_type = models.CharField(max_length=30, choices=REGISTRY_TYPES)
    registry_name = models.CharField(max_length=100, blank=True, help_text="Custom registry name if 'Other'")
    original_url = models.URLField(help_text="Original registry URL")
    affiliate_url = models.URLField(blank=True, help_text="Our affiliate URL (auto-generated if possible)")
    display_name = models.CharField(max_length=100, blank=True, help_text="Display name for the registry")
    description = models.TextField(blank=True, help_text="Description of what's on this registry")
    
    # Tracking
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['registry_type', 'created_at']
    
    def __str__(self):
        return f"{self.couple_profile} - {self.get_registry_type_display()}"
    
    @property
    def final_url(self):
        """Returns the original URL for now (affiliate logic removed)"""
        return self.original_url
    
    @property
    def registry_icon(self):
        """Returns appropriate Bootstrap icon for the registry with fallback"""
        icons = {
            'amazon': 'bi-amazon',
            'target': 'bi-bullseye',
            'bed_bath_beyond': 'bi-house-fill',
            'williams_sonoma': 'bi-cup-hot-fill',
            'crate_barrel': 'bi-house-door-fill',
            'pottery_barn': 'bi-home-fill',
            'macy': 'bi-bag-fill',
            'zola': 'bi-heart-fill',
            'the_knot': 'bi-heart',
            'wayfair': 'bi-house-fill',
            'registry_finder': 'bi-search-heart',
            'honeyfund': 'bi-airplane-fill',
            'other': 'bi-gift',
        }
        return icons.get(self.registry_type, 'bi-gift')  # Always returns something

    @property
    def registry_color(self):
        """Returns brand color for the registry with fallback"""
        colors = {
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
            'registry_finder': '#28a745',
            'honeyfund': '#FFA500',
            'other': '#6c757d',
        }
        return colors.get(self.registry_type, '#6c757d')  # Always returns something

    @property
    def registry_display_name(self):
        """Returns the display name to show on the wedding page with fallback"""
        if self.display_name:
            return self.display_name
        elif self.registry_name:
            return self.registry_name
        else:
            return f"{self.get_registry_type_display()}"
    
    def increment_clicks(self):
        """Increment click count"""
        self.click_count += 1
        self.save(update_fields=['click_count'])
