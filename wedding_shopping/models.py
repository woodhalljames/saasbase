# wedding_shopping/models.py
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
    """Social media profiles for the couple"""
    
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('tiktok', 'TikTok'),
        ('website', 'Website'),
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
        """Returns Bootstrap icon class for the platform"""
        icons = {
            'instagram': 'bi-instagram',
            'facebook': 'bi-facebook',
            'twitter': 'bi-twitter',
            'tiktok': 'bi-tiktok',
            'website': 'bi-globe',
            'other': 'bi-link-45deg',
        }
        return icons.get(self.platform, 'bi-link-45deg')


class RegistryLink(models.Model):
    """Wedding registry links with affiliate tracking"""
    
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
        """Returns appropriate icon for the registry"""
        icons = {
            'amazon': 'bi-amazon',
            'target': 'bi-bullseye',
            'zola': 'bi-heart-fill',
            'the_knot': 'bi-heart',
            'other': 'bi-gift',
        }
        return icons.get(self.registry_type, 'bi-gift')
    
    def increment_clicks(self):
        """Increment click count"""
        self.click_count += 1
        self.save(update_fields=['click_count'])


class WeddingPhotoCollection(models.Model):
    """Link to showcase wedding venue transformations"""
    
    couple_profile = models.ForeignKey(CoupleProfile, on_delete=models.CASCADE, related_name='photo_collections')
    collection_name = models.CharField(max_length=100, default="Our Wedding Venue Transformations")
    description = models.TextField(blank=True, help_text="Description of the photo collection")
    
    # Link to image_processing collection or individual images
    # We'll reference by collection name/id since it's in a different app
    studio_collection_id = models.IntegerField(null=True, blank=True, 
                                             help_text="ID of the studio collection to display")
    
    is_featured = models.BooleanField(default=True, help_text="Show this collection prominently")
    display_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order', '-created_at']
    
    def __str__(self):
        return f"{self.couple_profile} - {self.collection_name}"