# wedding_shopping/models.py
import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse
from PIL import Image
import json


class ShoppingList(models.Model):
    """Wedding shopping list/registry"""
    PRIVACY_CHOICES = [
        ('private', 'Private'),
        ('shared', 'Shared with Link'),
        ('public', 'Public Registry'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shopping_lists')
    name = models.CharField(max_length=200, default="My Wedding Shopping List")
    description = models.TextField(blank=True, null=True)
    
    # Source image - the wedding transformation this list is based on
    source_image = models.ForeignKey('image_processing.ProcessedImage', on_delete=models.CASCADE, related_name='shopping_lists')
    
    # Sharing settings
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='private')
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Wedding details for public registry
    wedding_date = models.DateField(blank=True, null=True)
    bride_name = models.CharField(max_length=100, blank=True)
    groom_name = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def get_absolute_url(self):
        return reverse('wedding_shopping:shopping_list_detail', kwargs={'pk': self.pk})
    
    def get_public_url(self):
        """Get public sharing URL"""
        return reverse('wedding_shopping:public_shopping_list', kwargs={'share_token': self.share_token})
    
    @property
    def total_items(self):
        return self.items.count()
    
    @property
    def purchased_items(self):
        return self.items.filter(is_purchased=True).count()
    
    @property
    def total_price(self):
        return sum(item.price or 0 for item in self.items.all())


class ShoppingItem(models.Model):
    """Individual items identified in wedding photos"""
    CATEGORY_CHOICES = [
        ('ceremony', 'Ceremony'),
        ('reception', 'Reception'),
        ('lighting', 'Lighting'),
        ('furniture', 'Furniture'),
        ('textiles', 'Textiles & Linens'),
        ('tableware', 'Tableware'),
        ('flowers', 'Flowers & Decor'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Must Have'),
        (2, 'Important'),
        (3, 'Nice to Have'),
    ]
    
    RETAILER_CHOICES = [
        ('amazon', 'Amazon'),
        ('wayfair', 'Wayfair'),
        ('target', 'Target'),
        ('ikea', 'IKEA'),
        ('pottery_barn', 'Pottery Barn'),
        ('williams_sonoma', 'Williams Sonoma'),
        ('crate_barrel', 'Crate & Barrel'),
        ('etsy', 'Etsy'),
        ('other', 'Other'),
    ]
    
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items')
    
    # Item details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    
    # Pricing and purchase info
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    is_purchased = models.BooleanField(default=False)
    purchased_by = models.CharField(max_length=100, blank=True)
    purchased_at = models.DateTimeField(blank=True, null=True)
    
    # Image selection data
    selection_x = models.IntegerField(help_text="X coordinate of selection rectangle")
    selection_y = models.IntegerField(help_text="Y coordinate of selection rectangle")
    selection_width = models.IntegerField(help_text="Width of selection rectangle")
    selection_height = models.IntegerField(help_text="Height of selection rectangle")
    cropped_image = models.ImageField(upload_to='shopping/crops/', blank=True, null=True)
    
    # AI analysis results
    ai_description = models.TextField(blank=True, help_text="AI-generated item description")
    ai_confidence = models.FloatField(default=0.0, help_text="AI confidence score 0-1")
    ai_tags = models.JSONField(default=list, help_text="AI-generated tags")
    
    # Product links
    product_url = models.URLField(blank=True, null=True)
    affiliate_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    retailer = models.CharField(max_length=20, choices=RETAILER_CHOICES, default='other')
    
    # User notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.shopping_list.name}"
    
    def save(self, *args, **kwargs):
        # Create cropped image if selection coordinates are provided
        if (self.selection_x is not None and self.selection_y is not None and 
            self.selection_width and self.selection_height and 
            not self.cropped_image and self.shopping_list.source_image.processed_image):
            
            self.create_cropped_image()
        
        super().save(*args, **kwargs)
    
    def create_cropped_image(self):
        """Create cropped image from selection coordinates"""
        try:
            # Open the source image
            source_image_path = self.shopping_list.source_image.processed_image.path
            with Image.open(source_image_path) as img:
                # Crop the image based on selection coordinates
                box = (
                    self.selection_x,
                    self.selection_y,
                    self.selection_x + self.selection_width,
                    self.selection_y + self.selection_height
                )
                cropped = img.crop(box)
                
                # Save cropped image
                from django.core.files.base import ContentFile
                import io
                
                buffer = io.BytesIO()
                cropped.save(buffer, format='PNG')
                buffer.seek(0)
                
                filename = f"crop_{self.shopping_list.id}_{uuid.uuid4().hex[:8]}.png"
                self.cropped_image.save(filename, ContentFile(buffer.getvalue()), save=False)
                
        except Exception as e:
            print(f"Error creating cropped image: {e}")


class ShoppingSession(models.Model):
    """Track shopping sessions for analytics"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shopping_sessions')
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='sessions')
    
    # Session data
    items_selected = models.IntegerField(default=0)
    items_purchased = models.IntegerField(default=0)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Analytics
    time_spent = models.DurationField(blank=True, null=True)
    conversion_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Shopping session - {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"