from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid
from django.utils.text import slugify
import re
import urllib.parse

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
    venue_location = models.CharField(max_length=200, blank=True, help_text="Full address or City, State")
    
    # Images - Keep existing field names for compatibility
    couple_photo = models.ImageField(
        upload_to='couple_photos/', 
        null=True, 
        blank=True,
        help_text='Main photo of the couple'
    )
    venue_photo = models.ImageField(
        upload_to='venue_photos/', 
        null=True, 
        blank=True,
        help_text='Venue photo or additional couple photo'
    )
    
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
        # Generate slug if needed
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
        
        # Check if images are new or changed
        if self.pk:
            try:
                old_instance = CoupleProfile.objects.get(pk=self.pk)
                couple_photo_changed = old_instance.couple_photo != self.couple_photo
                venue_photo_changed = old_instance.venue_photo != self.venue_photo
            except CoupleProfile.DoesNotExist:
                couple_photo_changed = bool(self.couple_photo)
                venue_photo_changed = bool(self.venue_photo)
        else:
            couple_photo_changed = bool(self.couple_photo)
            venue_photo_changed = bool(self.venue_photo)
        
        # Automatically optimize images on upload
        if self.couple_photo and couple_photo_changed:
            self.optimize_image('couple_photo')
        
        if self.venue_photo and venue_photo_changed:
            self.optimize_image('venue_photo')
        
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
        """Return the root-level URL for this wedding page"""
        return f"/{self.slug}/"
    
    def get_public_url(self):
        return self.get_absolute_url()
    
    def get_share_url(self):
        return reverse('wedding_shopping:wedding_page_token', kwargs={'share_token': str(self.share_token)})
    
    @property
    def couple_names(self):
        return f"{self.partner_1_name} & {self.partner_2_name}"
    
    @property
    def wedding_url_preview(self):
        """Updated for new URL structure"""
        return f"/{self.slug}/" if self.slug else "/[will-be-generated]/"
    
    @property
    def address_map_url(self):
        """Generate Google Maps URL from venue_location"""
        if not self.venue_location:
            return None
        encoded_address = urllib.parse.quote(self.venue_location)
        return f"https://maps.google.com/maps?q={encoded_address}"
    
    @property
    def display_city(self):
        """Extract city for discovery cards - works with both full addresses and city/state"""
        if not self.venue_location:
            return ""
        
        # If it looks like a full address (contains numbers), try to extract city
        if any(char.isdigit() for char in self.venue_location):
            # Split by comma and take the second-to-last part as likely city
            parts = [part.strip() for part in self.venue_location.split(',')]
            if len(parts) >= 2:
                return parts[-2]  # Usually the city part
            return parts[0] if parts else ""
        
        # If no numbers, assume it's already in "City, State" format
        return self.venue_location


class WeddingLink(models.Model):
    """Simplified link model for wedding-related links"""
    
    couple_profile = models.ForeignKey(CoupleProfile, on_delete=models.CASCADE, related_name='wedding_links')
    title = models.CharField(max_length=100, help_text="Site or link title")
    description = models.TextField(blank=True, help_text="Description of this link")
    url = models.URLField(help_text="Link URL")
    
    # Tracking
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']  # Order by creation order
    
    def __str__(self):
        return f"{self.couple_profile} - {self.title}"
    
    def increment_clicks(self):
        """Increment click count"""
        self.click_count += 1
        self.save(update_fields=['click_count'])
    
    @property
    def final_url(self):
        """Returns the URL to redirect to"""
        return self.url


# Keep backwards compatibility
RegistryLink = WeddingLink