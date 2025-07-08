from django.shortcuts import render

# Create your views here.
# wedding_shopping/views.py
import json
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from PIL import Image
import io
import base64

from image_processing.models import ProcessedImage
from .models import ShoppingList, ShoppingItem, ShoppingSession
from .ai_analysis import analyze_item_selection  # We'll create this
from .retailer_search import search_retailers  # We'll create this


@login_required
def shopping_mode(request, processed_image_id):
    """Shopping mode for a processed wedding image"""
    processed_image = get_object_or_404(
        ProcessedImage, 
        id=processed_image_id,
        processing_job__user_image__user=request.user
    )
    
    # Get or create shopping list for this image
    shopping_list, created = ShoppingList.objects.get_or_create(
        user=request.user,
        source_image=processed_image,
        defaults={
            'name': f"Shopping List for {processed_image.processing_job.user_image.original_filename}",
            'description': f"Items from {processed_image.processing_job.wedding_theme} {processed_image.processing_job.space_type} transformation"
        }
    )
    
    # Start shopping session
    session, session_created = ShoppingSession.objects.get_or_create(
        user=request.user,
        shopping_list=shopping_list,
        completed_at__isnull=True,
        defaults={'items_selected': 0}
    )
    
    context = {
        'processed_image': processed_image,
        'shopping_list': shopping_list,
        'session': session,
        'existing_items': shopping_list.items.all(),
    }
    
    return render(request, 'wedding_shopping/shopping_mode.html', context)


@login_required
@require_POST
def analyze_selection(request):
    """Analyze a selected area of the image using AI"""
    try:
        data = json.loads(request.body)
        shopping_list_id = data.get('shopping_list_id')
        selection = data.get('selection')  # {x, y, width, height}
        
        shopping_list = get_object_or_404(ShoppingList, id=shopping_list_id, user=request.user)
        
        # Perform AI analysis on the selection
        analysis_result = analyze_item_selection(
            shopping_list.source_image.processed_image.path,
            selection
        )
        
        if analysis_result['success']:
            # Create shopping item
            item = ShoppingItem.objects.create(
                shopping_list=shopping_list,
                name=analysis_result['name'],
                description=analysis_result['description'],
                category=analysis_result['category'],
                selection_x=selection['x'],
                selection_y=selection['y'],
                selection_width=selection['width'],
                selection_height=selection['height'],
                ai_description=analysis_result['ai_description'],
                ai_confidence=analysis_result['confidence'],
                ai_tags=analysis_result['tags']
            )
            
            # Update session
            session = ShoppingSession.objects.filter(
                user=request.user,
                shopping_list=shopping_list,
                completed_at__isnull=True
            ).first()
            if session:
                session.items_selected += 1
                session.save()
            
            return JsonResponse({
                'success': True,
                'item_id': item.id,
                'item': {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'category': item.category,
                    'confidence': item.ai_confidence,
                    'tags': item.ai_tags
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': analysis_result['error']
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_POST
def search_item_retailers(request, item_id):
    """Search retailers for a specific item"""
    item = get_object_or_404(ShoppingItem, id=item_id, shopping_list__user=request.user)
    
    try:
        # Search retailers using AI description and tags
        search_results = search_retailers(
            query=item.ai_description or item.name,
            category=item.category,
            tags=item.ai_tags
        )
        
        if search_results['success'] and search_results['results']:
            # Update item with best match
            best_match = search_results['results'][0]
            item.product_url = best_match.get('product_url')
            item.affiliate_url = best_match.get('affiliate_url')
            item.image_url = best_match.get('image_url')
            item.price = best_match.get('price')
            item.retailer = best_match.get('retailer', 'other')
            item.save()
            
            return JsonResponse({
                'success': True,
                'results': search_results['results'][:5]  # Return top 5 results
            })
        else:
            return JsonResponse({
                'success': False,
                'error': search_results.get('error', 'No products found')
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def shopping_list_detail(request, pk):
    """View and manage a shopping list"""
    shopping_list = get_object_or_404(ShoppingList, pk=pk, user=request.user)
    
    # Handle POST requests for updates
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_list':
            shopping_list.name = request.POST.get('name', shopping_list.name)
            shopping_list.description = request.POST.get('description', shopping_list.description)
            shopping_list.privacy = request.POST.get('privacy', shopping_list.privacy)
            shopping_list.wedding_date = request.POST.get('wedding_date') or None
            shopping_list.bride_name = request.POST.get('bride_name', shopping_list.bride_name)
            shopping_list.groom_name = request.POST.get('groom_name', shopping_list.groom_name)
            shopping_list.save()
            messages.success(request, 'Shopping list updated successfully!')
        
        elif action == 'update_item':
            item_id = request.POST.get('item_id')
            item = get_object_or_404(ShoppingItem, id=item_id, shopping_list=shopping_list)
            item.name = request.POST.get('name', item.name)
            item.description = request.POST.get('description', item.description)
            item.category = request.POST.get('category', item.category)
            item.priority = int(request.POST.get('priority', item.priority))
            item.price = request.POST.get('price') or None
            item.quantity = int(request.POST.get('quantity', item.quantity))
            item.notes = request.POST.get('notes', item.notes)
            item.save()
            messages.success(request, 'Item updated successfully!')
        
        elif action == 'delete_item':
            item_id = request.POST.get('item_id')
            item = get_object_or_404(ShoppingItem, id=item_id, shopping_list=shopping_list)
            item.delete()
            messages.success(request, 'Item deleted successfully!')
        
        return redirect('wedding_shopping:shopping_list_detail', pk=pk)
    
    # Group items by category
    items_by_category = {}
    for category_code, category_name in ShoppingItem.CATEGORY_CHOICES:
        items = shopping_list.items.filter(category=category_code)
        if items.exists():
            items_by_category[category_code] = {
                'name': category_name,
                'items': items
            }
    
    context = {
        'shopping_list': shopping_list,
        'items_by_category': items_by_category,
        'category_choices': ShoppingItem.CATEGORY_CHOICES,
        'priority_choices': ShoppingItem.PRIORITY_CHOICES,
        'retailer_choices': ShoppingItem.RETAILER_CHOICES,
    }
    
    return render(request, 'wedding_shopping/shopping_list_detail.html', context)


@login_required
def shopping_lists(request):
    """List all shopping lists for the user"""
    lists = ShoppingList.objects.filter(user=request.user).annotate(
        item_count=Count('items')
    )
    
    # Pagination
    paginator = Paginator(lists, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'wedding_shopping/shopping_lists.html', context)


def public_shopping_list(request, share_token):
    """Public view of a shared shopping list (wedding registry)"""
    shopping_list = get_object_or_404(
        ShoppingList, 
        share_token=share_token,
        privacy__in=['shared', 'public']
    )
    
    # Group items by category
    items_by_category = {}
    for category_code, category_name in ShoppingItem.CATEGORY_CHOICES:
        items = shopping_list.items.filter(category=category_code)
        if items.exists():
            items_by_category[category_code] = items
    
    context = {
        'shopping_list': shopping_list,
        'items_by_category': items_by_category,
    }
    
    return render(request, 'wedding_shopping/public_shopping_list.html', context)


@require_POST
@csrf_exempt
def purchase_item(request, share_token, item_id):
    """Mark an item as purchased (for public registries)"""
    shopping_list = get_object_or_404(
        ShoppingList, 
        share_token=share_token,
        privacy__in=['shared', 'public']
    )
    
    item = get_object_or_404(ShoppingItem, id=item_id, shopping_list=shopping_list)
    
    try:
        data = json.loads(request.body)
        purchaser_name = data.get('purchaser_name', '').strip()
        
        if not purchaser_name:
            return JsonResponse({'success': False, 'error': 'Purchaser name is required'})
        
        if item.is_purchased:
            return JsonResponse({'success': False, 'error': 'Item is already purchased'})
        
        # Mark as purchased
        from django.utils import timezone
        item.is_purchased = True
        item.purchased_by = purchaser_name
        item.purchased_at = timezone.now()
        item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Thank you! "{item.name}" has been marked as purchased.'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def create_shopping_list(request, processed_image_id):
    """Create a new shopping list from a processed image"""
    processed_image = get_object_or_404(
        ProcessedImage, 
        id=processed_image_id,
        processing_job__user_image__user=request.user
    )
    
    # Check if shopping list already exists
    existing_list = ShoppingList.objects.filter(
        user=request.user,
        source_image=processed_image
    ).first()
    
    if existing_list:
        return redirect('wedding_shopping:shopping_mode', processed_image_id=processed_image_id)
    
    # Create new shopping list
    shopping_list = ShoppingList.objects.create(
        user=request.user,
        source_image=processed_image,
        name=f"Wedding Shopping - {processed_image.processing_job.user_image.original_filename}",
        description=f"Items from {processed_image.processing_job.wedding_theme} {processed_image.processing_job.space_type} transformation"
    )
    
    messages.success(request, 'Shopping list created! Start selecting items from your wedding photo.')
    return redirect('wedding_shopping:shopping_mode', processed_image_id=processed_image_id)


@login_required
@require_POST
def delete_shopping_list(request, pk):
    """Delete a shopping list"""
    shopping_list = get_object_or_404(ShoppingList, pk=pk, user=request.user)
    shopping_list.delete()
    messages.success(request, 'Shopping list deleted successfully!')
    return redirect('wedding_shopping:shopping_lists')