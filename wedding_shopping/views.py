from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
from PIL import Image
import io
import base64

from .models import ShoppingSession, ItemSelection, ProductSearchResult, ShoppingList, ShoppingListItem, UserProfile
from .services import AIAnalysisService, ProductSearchService

@login_required
def shopping_home(request, session_id=None):
    """Main shopping interface"""
    session = None
    if session_id:
        session = get_object_or_404(ShoppingSession, id=session_id, user=request.user)
    
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'session': session,
        'user_tokens': user_profile.shopping_tokens,
        'shopping_lists': ShoppingList.objects.filter(user=request.user)
    }
    return render(request, 'wedding_shopping/shopping_interface.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class CreateShoppingSession(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Handle uploaded image or existing venue image
        image_file = request.FILES.get('venue_image')
        if not image_file:
            return JsonResponse({'error': 'No image provided'}, status=400)
            
        session = ShoppingSession.objects.create(
            user=request.user,
            venue_image=image_file
        )
        
        return JsonResponse({
            'session_id': str(session.id),
            'image_url': session.venue_image.url,
            'success': True
        })

@method_decorator(csrf_exempt, name='dispatch') 
class AnalyzeSelection(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        # Check user tokens
        user_profile = get_object_or_404(UserProfile, user=request.user)
        if user_profile.shopping_tokens <= 0:
            return JsonResponse({'error': 'No tokens remaining'}, status=402)
        
        data = json.loads(request.body)
        session = get_object_or_404(ShoppingSession, id=data['session_id'], user=request.user)
        
        # Create selection record
        selection = ItemSelection.objects.create(
            session=session,
            selection_number=data['selection_number'],
            x_position=data['x_position'],
            y_position=data['y_position'], 
            width=data['width'],
            height=data['height']
        )
        
        # Crop image for AI analysis
        cropped_image = self.crop_image(session.venue_image.path, data)
        
        # AI Analysis (implement your YOLO + CLIP here)
        ai_service = AIAnalysisService()
        analysis_result = ai_service.analyze_cropped_image(cropped_image)
        
        # Update selection with AI results
        selection.ai_detected_item = analysis_result['item_type']
        selection.ai_description = analysis_result['description']
        selection.save()
        
        # Search products across retailers
        search_service = ProductSearchService()
        products = search_service.search_all_retailers(
            query=analysis_result['search_query'],
            context='wedding'
        )
        
        # Save search results
        for product_data in products:
            ProductSearchResult.objects.create(
                selection=selection,
                retailer=product_data['retailer'],
                product_title=product_data['title'],
                product_price=product_data['price'],
                product_image_url=product_data['image_url'],
                affiliate_link=product_data['affiliate_link']
            )
        
        # Deduct token
        user_profile.shopping_tokens -= 1
        user_profile.save()
        
        return JsonResponse({
            'selection_id': selection.id,
            'ai_analysis': {
                'item_type': selection.ai_detected_item,
                'description': selection.ai_description
            },
            'products': [
                {
                    'retailer': p.retailer,
                    'title': p.product_title,
                    'price': str(p.product_price),
                    'image_url': p.product_image_url,
                    'affiliate_link': p.affiliate_link,
                    'product_id': p.id
                } for p in selection.products.all()
            ],
            'remaining_tokens': user_profile.shopping_tokens
        })
    
    def crop_image(self, image_path, selection_data):
        """Crop image based on selection coordinates"""
        with Image.open(image_path) as img:
            box = (
                selection_data['x_position'],
                selection_data['y_position'],
                selection_data['x_position'] + selection_data['width'],
                selection_data['y_position'] + selection_data['height']
            )
            cropped = img.crop(box)
            
            # Convert to bytes for AI processing
            buffer = io.BytesIO()
            cropped.save(buffer, format='PNG')
            return buffer.getvalue()

@require_http_methods(["POST"])
@csrf_exempt
def add_to_shopping_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    data = json.loads(request.body)
    
    # Get or create shopping list
    shopping_list, created = ShoppingList.objects.get_or_create(
        user=request.user,
        name=data.get('list_name', 'My Wedding Registry')
    )
    
    # Add product to list
    product = get_object_or_404(ProductSearchResult, id=data['product_id'])
    
    item, created = ShoppingListItem.objects.get_or_create(
        shopping_list=shopping_list,
        product=product,
        defaults={'notes': data.get('notes', '')}
    )
    
    return JsonResponse({
        'success': True,
        'list_id': str(shopping_list.id),
        'item_added': created
    })

def public_registry(request, share_url):
    """Public view of shared wedding registry"""
    shopping_list = get_object_or_404(ShoppingList, share_url=share_url, is_public=True)
    
    context = {
        'shopping_list': shopping_list,
        'items': shopping_list.items.all(),
        'total_estimated_cost': sum(item.product.product_price for item in shopping_list.items.all())
    }
    return render(request, 'wedding_shopping/public_registry.html', context)
