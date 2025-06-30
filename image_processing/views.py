# image_processing/views.py - Updated views for wedding venue processing

import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.urls import reverse

from usage_limits.decorators import usage_limit_required
from usage_limits.tier_config import TierLimits
from .models import (
    UserImage, ImageProcessingJob, ProcessedImage, Collection, CollectionItem,
    ImageRating, RatingTag, Favorite,
    generate_wedding_prompt, get_wedding_choices,
    WEDDING_THEMES, SPACE_TYPES
)
from .forms import ImageUploadForm, WeddingVisualizationForm, QuickWeddingForm
from .tasks import process_image_async

logger = logging.getLogger(__name__)


@login_required
def wedding_studio(request):
    """Main wedding venue visualization studio"""
    if request.method == 'POST':
        # Handle image upload
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user_image = form.save(commit=False)
                user_image.user = request.user
                user_image.original_filename = form.cleaned_data['image'].name
                user_image.save()
                messages.success(request, f'"{user_image.original_filename}" uploaded successfully!')
                return redirect('image_processing:wedding_studio')
            except Exception as e:
                messages.error(request, f'Failed to upload image: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    
    # Get user's recent images
    recent_images = UserImage.objects.filter(user=request.user).order_by('-uploaded_at')[:12]
    
    # Get user's usage data
    from usage_limits.usage_tracker import UsageTracker
    usage_data = UsageTracker.get_usage_data(request.user)
    
    # Get recent processing jobs
    recent_jobs = ImageProcessingJob.objects.filter(
        user_image__user=request.user
    ).order_by('-created_at')[:5]
    
    # Wedding choices
    wedding_choices = get_wedding_choices()
    
    context = {
        'recent_images': recent_images,
        'usage_data': usage_data,
        'recent_jobs': recent_jobs,
        'wedding_themes': WEDDING_THEMES,
        'space_types': SPACE_TYPES,
        'upload_form': ImageUploadForm(),
        'wedding_form': QuickWeddingForm(),
    }
    
    return render(request, 'image_processing/wedding_studio.html', context)


@login_required
def image_detail(request, pk):
    """Display single image with wedding processing options"""
    user_image = get_object_or_404(UserImage, pk=pk, user=request.user)
    
    # Get user's usage data
    from usage_limits.usage_tracker import UsageTracker
    usage_data = UsageTracker.get_usage_data(request.user)
    
    # Get processing history for this image
    processing_jobs = ImageProcessingJob.objects.filter(
        user_image=user_image
    ).order_by('-created_at')
    
    context = {
        'user_image': user_image,
        'usage_data': usage_data,
        'processing_jobs': processing_jobs,
        'wedding_form': WeddingVisualizationForm(user=request.user),
        'wedding_themes': WEDDING_THEMES,
        'space_types': SPACE_TYPES,
    }
    
    return render(request, 'image_processing/wedding_image_detail.html', context)


@login_required
@require_POST
@usage_limit_required(tokens=1)  # 1 token per image processed
def process_wedding_image(request, pk):
    """Process a single image with wedding theme and space type"""
    user_image = get_object_or_404(UserImage, pk=pk, user=request.user)
    
    try:
        data = json.loads(request.body)
        wedding_theme = data.get('wedding_theme')
        space_type = data.get('space_type')
        
        # Validate required fields
        if not wedding_theme or not space_type:
            return JsonResponse({
                'error': 'Both wedding theme and space type are required'
            }, status=400)
        
        # Validate choices
        valid_themes = [choice[0] for choice in WEDDING_THEMES]
        valid_spaces = [choice[0] for choice in SPACE_TYPES]
        
        if wedding_theme not in valid_themes:
            return JsonResponse({'error': 'Invalid wedding theme'}, status=400)
        
        if space_type not in valid_spaces:
            return JsonResponse({'error': 'Invalid space type'}, status=400)
        
        # Generate prompt from theme + space
        generated_prompt = generate_wedding_prompt(wedding_theme, space_type)
        
        # Create processing job
        with transaction.atomic():
            job = ImageProcessingJob.objects.create(
                user_image=user_image,
                wedding_theme=wedding_theme,
                space_type=space_type,
                generated_prompt=generated_prompt,
                cfg_scale=data.get('cfg_scale', 7.0),
                steps=data.get('steps', 50),
                seed=data.get('seed') if data.get('seed') else None
            )
        
        # Process asynchronously
        process_image_async.delay(job.id)
        
        # Get theme and space display names
        theme_display = dict(WEDDING_THEMES)[wedding_theme]
        space_display = dict(SPACE_TYPES)[space_type]
        
        return JsonResponse({
            'success': True,
            'job_id': job.id,
            'message': f'Transforming your {space_display} into {theme_display} style...',
            'redirect_url': reverse('image_processing:processing_history')
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error processing wedding image: {str(e)}")
        return JsonResponse({'error': 'Processing failed'}, status=500)


@login_required
def job_status(request, job_id):
    """Get status of a processing job with wedding context"""
    job = get_object_or_404(ImageProcessingJob, id=job_id, user_image__user=request.user)
    
    data = {
        'job_id': job.id,
        'status': job.status,
        'created_at': job.created_at.isoformat(),
        'wedding_theme': job.wedding_theme,
        'space_type': job.space_type,
    }
    
    # Add display names
    if job.wedding_theme:
        data['theme_display'] = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme)
    if job.space_type:
        data['space_display'] = dict(SPACE_TYPES).get(job.space_type, job.space_type)
    
    if job.status == 'completed':
        data['completed_at'] = job.completed_at.isoformat()
        # Note: For wedding processing, we expect only one result per job
        processed_images = job.processed_images.all()
        if processed_images:
            processed_img = processed_images.first()
            data['result'] = {
                'id': processed_img.id,
                'image_url': processed_img.processed_image.url,
                'seed': processed_img.stability_seed,
            }
    elif job.status == 'failed':
        data['error_message'] = job.error_message
    
    return JsonResponse(data)


@login_required
def processing_history(request):
    """View all wedding processing jobs for the user"""
    jobs = ImageProcessingJob.objects.filter(
        user_image__user=request.user
    ).order_by('-created_at')
    
    # Add display names to jobs
    for job in jobs:
        if job.wedding_theme:
            job.theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme)
        if job.space_type:
            job.space_display = dict(SPACE_TYPES).get(job.space_type, job.space_type)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'image_processing/wedding_processing_history.html', context)


@login_required 
def image_gallery(request):
    """Display user's uploaded images with wedding context"""
    images = UserImage.objects.filter(user=request.user).order_by('-uploaded_at')
    
    # Get usage data
    from usage_limits.usage_tracker import UsageTracker
    usage_data = UsageTracker.get_usage_data(request.user)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(images, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_images': images.count(),
        'usage_data': usage_data,
    }
    
    return render(request, 'image_processing/wedding_gallery.html', context)


# Collections, Favorites, and Ratings - Keep these features for wedding context!

@login_required
def collections_list(request):
    """Display user's wedding inspiration collections"""
    collections = Collection.objects.filter(user=request.user)
    recent_favorites = Favorite.objects.filter(user=request.user)[:6]
    
    context = {
        'collections': collections,
        'recent_favorites': recent_favorites,
    }
    
    return render(request, 'image_processing/collections_list.html', context)


@login_required
@require_POST
def create_collection(request):
    """Create a new wedding collection"""
    from .forms import CollectionForm
    form = CollectionForm(request.POST, user=request.user)
    if form.is_valid():
        collection = form.save(commit=False)
        collection.user = request.user
        collection.save()
        messages.success(request, f'Wedding collection "{collection.name}" created successfully!')
        return redirect('image_processing:collections_list')
    else:
        messages.error(request, 'Error creating collection. Please check your input.')
        return redirect('image_processing:collections_list')


@login_required
def collection_detail(request, collection_id):
    """View wedding collection details"""
    from .models import Collection
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    items = collection.items.all().order_by('order', '-added_at')
    
    context = {
        'collection': collection,
        'items': items,
    }
    
    return render(request, 'image_processing/collection_detail.html', context)


@login_required
@require_POST
def add_to_collection(request):
    """Add wedding image to collection via AJAX"""
    from .models import Collection, CollectionItem
    collection_id = request.POST.get('collection_id')
    user_image_id = request.POST.get('user_image_id')
    processed_image_id = request.POST.get('processed_image_id')
    
    try:
        collection = get_object_or_404(Collection, id=collection_id, user=request.user)
        
        if user_image_id:
            user_image = get_object_or_404(UserImage, id=user_image_id, user=request.user)
            item, created = CollectionItem.objects.get_or_create(
                collection=collection,
                user_image=user_image
            )
        elif processed_image_id:
            processed_image = get_object_or_404(
                ProcessedImage, 
                id=processed_image_id,
                processing_job__user_image__user=request.user
            )
            item, created = CollectionItem.objects.get_or_create(
                collection=collection,
                processed_image=processed_image
            )
        else:
            return JsonResponse({'success': False, 'message': 'No image specified'})
        
        if created:
            return JsonResponse({'success': True, 'message': f'Added to "{collection.name}"'})
        else:
            return JsonResponse({'success': False, 'message': 'Already in collection'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def remove_from_collection(request):
    """Remove image from wedding collection"""
    from .models import Collection, CollectionItem
    collection_id = request.POST.get('collection_id')
    item_id = request.POST.get('item_id')
    
    try:
        collection = get_object_or_404(Collection, id=collection_id, user=request.user)
        item = get_object_or_404(CollectionItem, id=item_id, collection=collection)
        item.delete()
        
        return JsonResponse({'success': True, 'message': 'Removed from collection'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def rate_image(request):
    """Rate a wedding venue transformation"""
    from .models import ImageRating, RatingTag
    processed_image_id = request.POST.get('processed_image_id')
    rating = request.POST.get('rating')
    tags = request.POST.getlist('tags[]')
    
    try:
        processed_image = get_object_or_404(
            ProcessedImage,
            id=processed_image_id,
            processing_job__user_image__user=request.user
        )
        
        # Create or update rating
        image_rating, created = ImageRating.objects.update_or_create(
            user=request.user,
            processed_image=processed_image,
            defaults={'rating': rating}
        )
        
        # Add tags for thumbs down ratings
        if rating == 'down' and tags:
            image_rating.tags.all().delete()
            for tag in tags:
                RatingTag.objects.create(rating=image_rating, tag=tag)
        
        # Get updated counts
        thumbs_up_count = processed_image.ratings.filter(rating='up').count()
        thumbs_down_count = processed_image.ratings.filter(rating='down').count()
        
        return JsonResponse({
            'success': True,
            'message': 'Rating submitted',
            'thumbs_up_count': thumbs_up_count,
            'thumbs_down_count': thumbs_down_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def toggle_favorite(request):
    """Toggle favorite status for wedding images"""
    from .models import Favorite
    user_image_id = request.POST.get('user_image_id')
    processed_image_id = request.POST.get('processed_image_id')
    
    try:
        if user_image_id:
            user_image = get_object_or_404(UserImage, id=user_image_id, user=request.user)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                user_image=user_image
            )
        elif processed_image_id:
            processed_image = get_object_or_404(
                ProcessedImage,
                id=processed_image_id,
                processing_job__user_image__user=request.user
            )
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                processed_image=processed_image
            )
        else:
            return JsonResponse({'success': False, 'error': 'No image specified'})
        
        if not created:
            favorite.delete()
            is_favorited = False
            message = 'Removed from favorites'
        else:
            is_favorited = True
            message = 'Added to favorites'
        
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def favorites_list(request):
    """Display user's favorite wedding images"""
    from .models import Favorite
    from django.core.paginator import Paginator
    
    favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(favorites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'image_processing/favorites_list.html', context)


@login_required
def processed_image_detail(request, pk):
    """View details of a processed wedding image"""
    processed_image = get_object_or_404(
        ProcessedImage, 
        pk=pk, 
        processing_job__user_image__user=request.user
    )
    
    context = {
        'processed_image': processed_image,
    }
    
    return render(request, 'image_processing/processed_image_detail.html', context)


@login_required
def share_image(request, image_type, image_id):
    """Generate sharing URL for a wedding image"""
    from urllib.parse import quote
    
    if image_type == 'user':
        image = get_object_or_404(UserImage, id=image_id, user=request.user)
        image_url = request.build_absolute_uri(image.image.url)
    elif image_type == 'processed':
        image = get_object_or_404(
            ProcessedImage,
            id=image_id,
            processing_job__user_image__user=request.user
        )
        image_url = request.build_absolute_uri(image.processed_image.url)
    else:
        messages.error(request, 'Invalid image type')
        return redirect('image_processing:wedding_studio')
    
    context = {
        'image': image,
        'image_url': image_url,
        'image_type': image_type,
    }
    
    return render(request, 'image_processing/share_image.html', context)


# Keep existing views for compatibility
@login_required
def dashboard(request):
    """Redirect to wedding studio for now"""
    return redirect('image_processing:wedding_studio')


@login_required
def upload_image(request):
    """Redirect to wedding studio for now"""
    return redirect('image_processing:wedding_studio')