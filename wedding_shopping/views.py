# wedding_shopping/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse
import json
import logging

# Import the usage limit decorator
from usage_limits.decorators import usage_limit_required
from usage_limits.usage_tracker import UsageTracker

from image_processing.models import ProcessedImage
from .models import ShoppingList, ShoppingItem, ShoppingSession

logger = logging.getLogger(__name__)


@login_required
@usage_limit_required(tokens=1, redirect_url='subscriptions:pricing')
def shopping_mode(request, processed_image_id):
    """
    Main shopping interface - requires 1 token to access.
    """
    processed_image = get_object_or_404(ProcessedImage, id=processed_image_id)
    
    # Check if user owns this image
    if processed_image.processing_job.user_image.user != request.user:
        messages.error(request, "You don't have permission to shop this image.")
        return redirect('image_processing:processing_history')
    
    # Get or create shopping list for this image
    shopping_list, created = ShoppingList.objects.get_or_create(
        user=request.user,
        source_image=processed_image,
        defaults={
            'name': f'Shopping for {processed_image.processing_job.user_image.original_filename}',
            'description': f'Items from wedding transformation'
        }
    )
    
    # Get existing items
    existing_items = shopping_list.items.all()
    
    # Get user's usage data
    usage_data = UsageTracker.get_usage_data(request.user)
    
    context = {
        'processed_image': processed_image,
        'shopping_list': shopping_list,
        'existing_items': existing_items,
        'usage_data': usage_data,
    }
    
    return render(request, 'wedding_shopping/shopping_mode.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def analyze_selection(request):
    """
    Analyze a user's selection and create shopping item.
    """
    try:
        data = json.loads(request.body)
        shopping_list_id = data.get('shopping_list_id')
        selection = data.get('selection', {})
        
        shopping_list = get_object_or_404(ShoppingList, id=shopping_list_id, user=request.user)
        
        # Create the shopping item with mock AI analysis
        item = ShoppingItem.objects.create(
            shopping_list=shopping_list,
            name="Wedding Item",  # Mock name
            description="AI-generated description",
            ai_description="Mock AI description",
            ai_confidence=0.85,
            ai_tags=["wedding", "elegant"],
            category='other',
            selection_x=selection.get('x', 0),
            selection_y=selection.get('y', 0),
            selection_width=selection.get('width', 0),
            selection_height=selection.get('height', 0),
        )
        
        return JsonResponse({
            'success': True,
            'item_id': item.id,
            'item': {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'category': item.get_category_display(),
                'confidence': item.ai_confidence,
                'tags': item.ai_tags,
            }
        })
        
    except Exception as e:
        logger.error(f"Error analyzing selection: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def search_retailers(request, item_id):
    """
    Search for products from retailers.
    """
    try:
        item = get_object_or_404(ShoppingItem, id=item_id, shopping_list__user=request.user)
        
        # Mock product results
        results = [
            {
                'name': f'Premium {item.name}',
                'description': f'High-quality {item.name.lower()}',
                'price': 89.99,
                'image_url': 'https://images.unsplash.com/photo-1606800052052-a08af7148866?w=200&h=200&fit=crop',
                'product_url': 'https://example.com/product1',
                'affiliate_url': 'https://example.com/affiliate1',
                'retailer': 'amazon',
                'rating': 4.5
            }
        ]
        
        return JsonResponse({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error searching retailers: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def shopping_lists_view(request):
    """View all shopping lists for the user"""
    shopping_lists = ShoppingList.objects.filter(user=request.user)
    
    context = {
        'shopping_lists': shopping_lists,
    }
    
    return render(request, 'wedding_shopping/shopping_lists.html', context)


@login_required
def shopping_list_detail(request, list_id):
    """View details of a specific shopping list"""
    shopping_list = get_object_or_404(ShoppingList, id=list_id, user=request.user)
    
    # Handle POST requests for list updates
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_list':
            shopping_list.name = request.POST.get('name', shopping_list.name)
            shopping_list.description = request.POST.get('description', shopping_list.description)
            shopping_list.privacy = request.POST.get('privacy', shopping_list.privacy)
            shopping_list.save()
            messages.success(request, 'Shopping list updated successfully!')
            
        elif action == 'delete_item':
            item_id = request.POST.get('item_id')
            if item_id:
                ShoppingItem.objects.filter(id=item_id, shopping_list=shopping_list).delete()
                messages.success(request, 'Item removed from shopping list!')
        
        return redirect('wedding_shopping:shopping_list_detail', list_id=list_id)
    
    # Group items by category
    items_by_category = {}
    for item in shopping_list.items.all():
        category = item.category
        if category not in items_by_category:
            items_by_category[category] = {
                'name': item.get_category_display(),
                'items': []
            }
        items_by_category[category]['items'].append(item)
    
    context = {
        'shopping_list': shopping_list,
        'items_by_category': items_by_category,
    }
    
    return render(request, 'wedding_shopping/shopping_list_detail.html', context)


@login_required
def delete_shopping_list(request, list_id):
    """Delete a shopping list"""
    shopping_list = get_object_or_404(ShoppingList, id=list_id, user=request.user)
    
    if request.method == 'POST':
        shopping_list.delete()
        messages.success(request, 'Shopping list deleted successfully!')
        return redirect('wedding_shopping:shopping_lists')
    
    return redirect('wedding_shopping:shopping_list_detail', list_id=list_id)


def public_shopping_list(request, share_token):
    """Public view of shared wedding shopping list"""
    shopping_list = get_object_or_404(
        ShoppingList, 
        share_token=share_token, 
        privacy__in=['shared', 'public']
    )
    
    # Group items by category
    items_by_category = {}
    for item in shopping_list.items.all():
        category = item.category
        if category not in items_by_category:
            items_by_category[category] = {
                'name': item.get_category_display(),
                'items': []
            }
        items_by_category[category]['items'].append(item)
    
    context = {
        'shopping_list': shopping_list,
        'items_by_category': items_by_category,
        'is_public_view': True,
    }
    
    return render(request, 'wedding_shopping/public_shopping_list.html', context)