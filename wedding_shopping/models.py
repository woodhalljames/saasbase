# wedding_shopping/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid

User = get_user_model()

class ShoppingList(models.Model):
    PRIVACY_CHOICES = [
        ('private', 'Private'),
        ('shared', 'Shared with Link'),
        ('public', 'Public Registry'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_lists')
    source_image = models.ForeignKey(
        'image_processing.ProcessedImage', 
        on_delete=models.CASCADE, 
        related_name='shopping_lists'
    )
    name = models.CharField(max_length=200, default='My Wedding Shopping List')
    description = models.TextField(blank=True, null=True)
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='private')
    share_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Public registry fields
    wedding_date = models.DateField(blank=True, null=True)
    bride_name = models.CharField(max_length=100, blank=True)
    groom_name = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    @property
    def total_items(self):
        return self.items.count()
    
    @property
    def purchased_items(self):
        return self.items.filter(is_purchased=True).count()
    
    @property
    def total_price(self):
        return sum(item.price or 0 for item in self.items.all())
    
    def get_public_url(self):
        return reverse('wedding_shopping:public_shopping_list', kwargs={'share_token': self.share_token})


class ShoppingItem(models.Model):
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
    
    # Basic item info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    
    # Purchase info
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    is_purchased = models.BooleanField(default=False)
    purchased_by = models.CharField(max_length=100, blank=True)
    purchased_at = models.DateTimeField(blank=True, null=True)
    
    # Selection coordinates (relative to source image)
    selection_x = models.IntegerField(help_text='X coordinate of selection rectangle')
    selection_y = models.IntegerField(help_text='Y coordinate of selection rectangle')
    selection_width = models.IntegerField(help_text='Width of selection rectangle')
    selection_height = models.IntegerField(help_text='Height of selection rectangle')
    
    # Image data
    cropped_image = models.ImageField(upload_to='shopping/crops/', blank=True, null=True)
    
    # AI analysis results
    ai_description = models.TextField(blank=True, help_text='AI-generated item description')
    ai_confidence = models.FloatField(default=0.0, help_text='AI confidence score 0-1')
    ai_tags = models.JSONField(default=list, help_text='AI-generated tags')
    
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
    
    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
    
    def get_retailer_display(self):
        return dict(self.RETAILER_CHOICES).get(self.retailer, self.retailer)


class ShoppingSession(models.Model):
    """Track shopping sessions for analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_sessions')
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='sessions')
    
    # Session stats
    items_selected = models.IntegerField(default=0)
    items_purchased = models.IntegerField(default=0)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    time_spent = models.DurationField(blank=True, null=True)
    conversion_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Session {self.id} - {self.user.username}"