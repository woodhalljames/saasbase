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
from .models import (
    UserImage, ImageProcessingJob, ProcessedImage, Collection, CollectionItem, Favorite,
    WEDDING_THEMES, SPACE_TYPES
)
from .forms import ImageUploadForm, WeddingTransformForm
from .tasks import process_image_async

logger = logging.getLogger(__name__)


@login_required
def wedding_studio(request):
    """Main wedding venue visualization studio - matches wireframe"""
    
    # Handle image upload
    if request.method == 'POST':
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
    
    # Get user's recent images (for image selection grid)
    recent_images = UserImage.objects.filter(user=request.user).order_by('-uploaded_at')[:20]
    
    # Get user's usage data
    from usage_limits.usage_tracker import UsageTracker
    usage_data = UsageTracker.get_usage_data(request.user)
    
    # Get recent processing jobs for status display
    recent_jobs = ImageProcessingJob.objects.filter(
        user_image__user=request.user
    ).select_related('user_image').order_by('-created_at')[:5]
    
    context = {
        'recent_images': recent_images,
        'usage_data': usage_data,
        'recent_jobs': recent_jobs,
        'wedding_themes': WEDDING_THEMES,
        'space_types': SPACE_TYPES,
        'upload_form': ImageUploadForm(),
        'transform_form': WeddingTransformForm(),
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
        'transform_form': WeddingTransformForm(),
        'wedding_themes': WEDDING_THEMES,
        'space_types': SPACE_TYPES,
    }
    
    return render(request, 'image_processing/image_detail.html', context)


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
        
        # Create processing job
        with transaction.atomic():
            job = ImageProcessingJob.objects.create(
                user_image=user_image,
                wedding_theme=wedding_theme,
                space_type=space_type,
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
    ).select_related('user_image').order_by('-created_at')
    
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
    
    return render(request, 'image_processing/processing_history.html', context)


@login_required 
def image_gallery(request):
    """Display user's uploaded images and saved transformations"""
    # Original uploaded images
    uploaded_images = UserImage.objects.filter(user=request.user).order_by('-uploaded_at')
    
    # Saved processed images
    saved_transformations = ProcessedImage.objects.filter(
        processing_job__user_image__user=request.user,
        is_saved=True
    ).select_related('processing_job__user_image').order_by('-saved_at')
    
    # Get usage data
    from usage_limits.usage_tracker import UsageTracker
    usage_data = UsageTracker.get_usage_data(request.user)
    
    # Combine and paginate all images
    from itertools import chain
    from django.core.paginator import Paginator
    
    # Create a combined list with type indicators
    all_images = []
    for img in uploaded_images:
        all_images.append({
            'type': 'original',
            'object': img,
            'date': img.uploaded_at,
            'title': img.original_filename,
            'url': img.thumbnail.url if img.thumbnail else img.image.url
        })
    
    for transformation in saved_transformations:
        job = transformation.processing_job
        theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, 'Unknown')
        space_display = dict(SPACE_TYPES).get(job.space_type, 'Unknown')
        all_images.append({
            'type': 'transformation',
            'object': transformation,
            'date': transformation.saved_at,
            'title': f"{theme_display} {space_display}",
            'url': transformation.processed_image.url
        })
    
    # Sort by date (newest first)
    all_images.sort(key=lambda x: x['date'], reverse=True)
    
    # Pagination
    paginator = Paginator(all_images, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_images': len(all_images),
        'uploaded_count': uploaded_images.count(),
        'saved_count': saved_transformations.count(),
        'usage_data': usage_data,
        'wedding_themes': WEDDING_THEMES,
        'space_types': SPACE_TYPES,
    }
    
    return render(request, 'image_processing/image_gallery.html', context)


@login_required
def processed_image_detail(request, pk):
    """View details of a processed wedding image with save/discard options"""
    processed_image = get_object_or_404(
        ProcessedImage, 
        pk=pk, 
        processing_job__user_image__user=request.user
    )
    
    # Add display names
    job = processed_image.processing_job
    theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, 'Unknown')
    space_display = dict(SPACE_TYPES).get(job.space_type, 'Unknown')
    
    context = {
        'processed_image': processed_image,
        'theme_display': theme_display,
        'space_display': space_display,
    }
    
    return render(request, 'image_processing/processed_image_detail.html', context)


@login_required
@require_POST
def save_processed_image(request, pk):
    """Save a processed image to user's permanent collection"""
    processed_image = get_object_or_404(
        ProcessedImage, 
        pk=pk, 
        processing_job__user_image__user=request.user
    )
    
    if processed_image.is_saved:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Image is already saved'
            })
        messages.info(request, 'This transformation is already saved')
        return redirect('image_processing:processed_image_detail', pk=pk)
    
    # Get collection choice from request
    collection_choice = request.POST.get('collection_choice')  # 'default', 'existing', or 'new'
    collection_id = request.POST.get('collection_id')  # for existing collection
    new_collection_name = request.POST.get('new_collection_name')  # for new collection
    
    try:
        # Determine which collection to use
        if collection_choice == 'new' and new_collection_name:
            # Create new collection
            collection, created = Collection.objects.get_or_create(
                user=request.user,
                name=new_collection_name.strip(),
                defaults={'description': f'Created when saving wedding transformation'}
            )
            if not created:
                # Collection name already exists
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': f'Collection "{new_collection_name}" already exists'
                    })
                messages.error(request, f'Collection "{new_collection_name}" already exists')
                return redirect('image_processing:processed_image_detail', pk=pk)
                
        elif collection_choice == 'existing' and collection_id:
            # Use existing collection
            collection = get_object_or_404(Collection, id=collection_id, user=request.user)
        else:
            # Use default collection
            collection = Collection.get_or_create_default(request.user)
        
        # Save the image to the collection
        processed_image.mark_as_saved(collection=collection)
        
        # Handle AJAX requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Saved to "{collection.name}"!',
                'is_saved': True,
                'collection_name': collection.name,
                'saved_at': processed_image.saved_at.isoformat()
            })
        
        messages.success(request, f'Wedding transformation saved to "{collection.name}"!')
        
    except Exception as e:
        logger.error(f"Error saving image to collection: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error saving transformation'
            })
        messages.error(request, 'Error saving transformation')
    
    # Redirect back to the image detail page
    return redirect('image_processing:processed_image_detail', pk=pk)


@login_required
@require_POST
def discard_processed_image(request, pk):
    """Discard a processed image (delete immediately)"""
    processed_image = get_object_or_404(
        ProcessedImage, 
        pk=pk, 
        processing_job__user_image__user=request.user
    )
    
    if processed_image.is_saved:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Cannot discard a saved image'
            })
        messages.error(request, 'Cannot discard a saved transformation')
        return redirect('image_processing:processed_image_detail', pk=pk)
    
    # Delete the image file and record
    try:
        import os
        if processed_image.processed_image and os.path.exists(processed_image.processed_image.path):
            os.remove(processed_image.processed_image.path)
        processed_image.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Transformation discarded',
                'redirect_url': reverse('image_processing:processing_history')
            })
        
        messages.success(request, 'Wedding transformation discarded')
        return redirect('image_processing:processing_history')
        
    except Exception as e:
        logger.error(f"Error discarding image: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error discarding transformation'
            })
        messages.error(request, 'Error discarding transformation')
        return redirect('image_processing:processed_image_detail', pk=pk)


# Collection and favorites views remain the same but simplified
@login_required
def collections_list(request):
    """Display user's wedding inspiration collections"""
    # Get default collection separately
    default_collection = Collection.objects.filter(user=request.user, is_default=True).first()
    
    # Get custom collections (non-default)
    collections = Collection.objects.filter(user=request.user, is_default=False).order_by('-updated_at')
    
    # Get recent favorites
    recent_favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')[:6]
    
    context = {
        'default_collection': default_collection,
        'collections': collections,
        'recent_favorites': recent_favorites,
    }
    
    return render(request, 'image_processing/collections_list.html', context)

@login_required
@require_POST
def toggle_favorite(request):
    """Toggle favorite status for wedding images"""
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
@require_POST
def create_collection(request):
    """Create a new collection"""
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    is_public = request.POST.get('is_public') == 'on'
    
    if not name:
        messages.error(request, 'Collection name is required')
        return redirect('image_processing:collections_list')
    
    try:
        collection = Collection.objects.create(
            user=request.user,
            name=name,
            description=description,
            is_public=is_public
        )
        messages.success(request, f'Collection "{name}" created successfully!')
    except Exception as e:
        logger.error(f"Error creating collection: {str(e)}")
        messages.error(request, 'Error creating collection')
    
    return redirect('image_processing:collections_list')


@login_required
def get_user_collections(request):
    """API endpoint to get user's collections as JSON"""
    collections = Collection.objects.filter(user=request.user).order_by('-updated_at')
    
    collections_data = []
    for collection in collections:
        collections_data.append({
            'id': collection.id,
            'name': collection.name,
            'count': collection.item_count,
            'is_default': collection.is_default
        })
    
    return JsonResponse({
        'collections': collections_data
    })


@login_required
def collection_detail(request, collection_id):
    """Display a specific collection"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    
    # Get all items in the collection
    items = collection.items.select_related(
        'user_image', 
        'processed_image__processing_job'
    ).order_by('order', '-added_at')
    
    # Add display information to each item
    for item in items:
        if item.processed_image:
            job = item.processed_image.processing_job
            item.theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, 'Unknown') if job.wedding_theme else 'Unknown'
            item.space_display = dict(SPACE_TYPES).get(job.space_type, 'Unknown') if job.space_type else 'Unknown'
    
    context = {
        'collection': collection,
        'items': items,
    }
    
    return render(request, 'image_processing/collection_detail.html', context)