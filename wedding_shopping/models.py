# wedding_shopping/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shopping_tokens = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

class ShoppingSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    venue_image = models.ImageField(upload_to='shopping_sessions/')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class ItemSelection(models.Model):
    session = models.ForeignKey(ShoppingSession, on_delete=models.CASCADE, related_name='selections')
    selection_number = models.IntegerField()
    x_position = models.IntegerField()
    y_position = models.IntegerField() 
    width = models.IntegerField()
    height = models.IntegerField()
    ai_detected_item = models.CharField(max_length=200, blank=True)
    ai_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductSearchResult(models.Model):
    RETAILER_CHOICES = [
        ('amazon', 'Amazon'),
        ('wayfair', 'Wayfair'), 
        ('overstock', 'Overstock'),
    ]
    
    selection = models.ForeignKey(ItemSelection, on_delete=models.CASCADE, related_name='products')
    retailer = models.CharField(max_length=20, choices=RETAILER_CHOICES)
    product_title = models.CharField(max_length=300)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image_url = models.URLField()
    affiliate_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

class ShoppingList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default="My Wedding Registry")
    is_public = models.BooleanField(default=False)
    share_url = models.CharField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.share_url:
            self.share_url = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

class ShoppingListItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductSearchResult, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
