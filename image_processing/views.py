# image_processing/views.py - Updated with enhanced form handling

import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.db import transaction
from django.urls import reverse

from usage_limits.decorators import usage_limit_required
from .models import (
    UserImage, ImageProcessingJob, ProcessedImage, Collection, CollectionItem, Favorite,
    WEDDING_THEMES, SPACE_TYPES
)
from .forms import ImageUploadForm, WeddingTransformForm, GUEST_COUNT_CHOICES, BUDGET_CHOICES, SEASON_CHOICES, TIME_OF_DAY_CHOICES, COLOR_SCHEME_CHOICES
from .tasks import process_image_async

logger = logging.getLogger(__name__)


@login_required
def wedding_studio(request):
    """Main wedding venue visualization studio with dynamic options"""
    
    # Handle image upload
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user_image = form.save(commit=False)
                user_image.user = request.user
                user_image.original_filename = form.cleaned_data['image'].name
                user_image.save()
                
                # Handle AJAX requests
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'"{user_image.original_filename}" uploaded successfully!',
                        'image': {
                            'id': user_image.id,
                            'original_filename': user_image.original_filename,
                            'image_url': user_image.image.url,
                            'thumbnail_url': user_image.thumbnail.url if user_image.thumbnail else user_image.image.url,
                            'width': user_image.width,
                            'height': user_image.height,
                            'file_size': user_image.file_size,
                        }
                    })
                
                messages.success(request, f'"{user_image.original_filename}" uploaded successfully!')
                return redirect('image_processing:wedding_studio')
                
            except Exception as e:
                logger.error(f"Error uploading image: {str(e)}")
                error_msg = f'Failed to upload image: {str(e)}'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                messages.error(request, error_msg)
        else:
            # Handle form errors
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(str(error))
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': '; '.join(error_messages)}, status=400)
            
            for error in error_messages:
                messages.error(request, error)
    
    # GET request - display the studio
    recent_images = UserImage.objects.filter(user=request.user).order_by('-uploaded_at')[:20]
    
    # Get specific image if image_id is provided (for preselection from gallery)
    preselected_image = None
    image_id = request.GET.get('image_id')
    if image_id:
        try:
            preselected_image = UserImage.objects.get(id=image_id, user=request.user)
        except UserImage.DoesNotExist:
            pass
    
    # Get user's usage data
    from usage_limits.usage_tracker import UsageTracker
    usage_data = UsageTracker.get_usage_data(request.user)
    
    # Get recent processing jobs
    recent_jobs = ImageProcessingJob.objects.filter(
        user_image__user=request.user
    ).select_related('user_image').order_by('-created_at')[:5]
    
    context = {
        'recent_images': recent_images,
        'preselected_image': preselected_image,
        'usage_data': usage_data,
        'recent_jobs': recent_jobs,
        'wedding_themes': WEDDING_THEMES,
        'space_types': SPACE_TYPES,
        'guest_count_choices': GUEST_COUNT_CHOICES,
        'budget_choices': BUDGET_CHOICES,
        'season_choices': SEASON_CHOICES,
        'time_choices': TIME_OF_DAY_CHOICES,
        'color_choices': COLOR_SCHEME_CHOICES,
        'upload_form': ImageUploadForm(),
    }
    
    return render(request, 'image_processing/wedding_studio.html', context)

@login_required
@require_http_methods(["POST"])
def process_wedding_image(request, pk):
    """Process wedding venue image with AI transformation - enhanced with all form fields"""
    try:
        # Get the user's image
        user_image = get_object_or_404(UserImage, id=pk, user=request.user)
        
        # Check usage limits before processing
        from usage_limits.usage_tracker import UsageTracker
        usage_data = UsageTracker.get_usage_data(request.user)
        
        if usage_data['remaining'] <= 0:
            return JsonResponse({
                'success': False,
                'error': 'You have reached your monthly transformation limit. Please upgrade your subscription to continue.',
                'usage_data': usage_data,
                'needs_upgrade': True
            }, status=429)
        
        # Try to increment usage (this will fail if no tokens available)
        if not UsageTracker.increment_usage(request.user, 1):
            return JsonResponse({
                'success': False, 
                'error': 'Unable to process - monthly limit reached. Please upgrade your subscription.',
                'usage_data': UsageTracker.get_usage_data(request.user),
                'needs_upgrade': True
            }, status=429)
        
        # Parse request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid request data'
            }, status=400)
        
        # Validate required fields
        wedding_theme = data.get('wedding_theme')
        space_type = data.get('space_type')
        
        if not wedding_theme or not space_type:
            return JsonResponse({
                'success': False,
                'error': 'Wedding theme and space type are required'
            }, status=400)
        
        # Create processing job with all form fields
        job_data = {
            'user_image': user_image,
            'wedding_theme': wedding_theme,
            'space_type': space_type,
            
            # Optional fields - only save if they have values
            'guest_count': data.get('guest_count', ''),
            'budget_level': data.get('budget_level', ''),
            'season': data.get('season', ''),
            'time_of_day': data.get('time_of_day', ''),
            'color_scheme': data.get('color_scheme', ''),
            'custom_colors': data.get('custom_colors', ''),
            'additional_details': data.get('additional_details', ''),
        }
        
        # Clean empty strings to None for database
        for key, value in job_data.items():
            if isinstance(value, str) and value.strip() == '':
                job_data[key] = None
        
        job = ImageProcessingJob.objects.create(**job_data)
        
        # Queue the processing task
        process_image_async.delay(job.id)
        
        logger.info(f"Created processing job {job.id} with enhanced parameters: theme={wedding_theme}, space={space_type}, guest_count={job_data.get('guest_count')}, budget={job_data.get('budget_level')}")
        
        return JsonResponse({
            'success': True,
            'job_id': job.id,
            'redirect_url': reverse('image_processing:processing_history'),
            'message': 'Your wedding transformation has been queued for processing!'
        })
        
    except Exception as e:
        logger.error(f"Error in process_wedding_image: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }, status=500)


@login_required
def image_detail(request, pk):
    """Display single image with enhanced wedding processing options"""
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
        'guest_count_choices': GUEST_COUNT_CHOICES,
        'budget_choices': BUDGET_CHOICES,
        'season_choices': SEASON_CHOICES,
        'time_choices': TIME_OF_DAY_CHOICES,
        'color_choices': COLOR_SCHEME_CHOICES,
    }
    
    return render(request, 'image_processing/image_detail.html', context)

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
        
        # Include enhanced parameters in status response
        'guest_count': job.guest_count,
        'budget_level': job.budget_level,
        'season': job.season,
        'time_of_day': job.time_of_day,
        'color_scheme': job.color_scheme,
        'custom_colors': job.custom_colors,
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
    """Display user's uploaded images and processed transformations"""
    # Original uploaded images
    uploaded_images = UserImage.objects.filter(user=request.user).order_by('-uploaded_at')
    
    # All processed images with favorite status
    all_transformations = ProcessedImage.objects.filter(
        processing_job__user_image__user=request.user
    ).select_related('processing_job__user_image').order_by('-created_at')
    
    # Add favorite status to processed images
    all_transformations = add_favorite_status_to_processed_images(request.user, all_transformations)
    
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
    
    for transformation in all_transformations:
        job = transformation.processing_job
        theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, 'Unknown')
        space_display = dict(SPACE_TYPES).get(job.space_type, 'Unknown')
        all_images.append({
            'type': 'transformation',
            'object': transformation,
            'date': transformation.created_at,
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
        'transformation_count': all_transformations.count(),
        'usage_data': usage_data,
        'wedding_themes': WEDDING_THEMES,
        'space_types': SPACE_TYPES,
    }
    
    return render(request, 'image_processing/image_gallery.html', context)


@login_required
def processed_image_detail(request, pk):
    """View details of a processed wedding image"""
    processed_image = get_object_or_404(
        ProcessedImage, 
        pk=pk, 
        processing_job__user_image__user=request.user
    )
    
    # Add favorite status
    processed_image.is_favorited = Favorite.objects.filter(
        user=request.user,
        processed_image=processed_image
    ).exists()
    
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
def add_to_collection(request):
    """Add an image to a collection"""
    from django.utils import timezone
    
    collection_id = request.POST.get('collection_id')
    processed_image_id = request.POST.get('processed_image_id')
    user_image_id = request.POST.get('user_image_id')
    use_default = request.POST.get('use_default') == 'true'
    
    try:
        # Determine which collection to use
        if use_default or not collection_id:
            collection = Collection.get_or_create_default(request.user)
        else:
            collection = get_object_or_404(Collection, id=collection_id, user=request.user)
        
        if processed_image_id:
            processed_image = get_object_or_404(
                ProcessedImage,
                id=processed_image_id,
                processing_job__user_image__user=request.user
            )
            
            collection_item, created = CollectionItem.objects.get_or_create(
                collection=collection,
                processed_image=processed_image,
                defaults={'notes': f'Added on {timezone.now().strftime("%B %d, %Y")}'}
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': f'Added to "{collection.name}"!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Image already in this collection'
                })
                
        elif user_image_id:
            user_image = get_object_or_404(UserImage, id=user_image_id, user=request.user)
            
            collection_item, created = CollectionItem.objects.get_or_create(
                collection=collection,
                user_image=user_image,
                defaults={'notes': f'Added on {timezone.now().strftime("%B %d, %Y")}'}
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': f'Added to "{collection.name}"!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Image already in this collection'
                })
        else:
            return JsonResponse({'success': False, 'message': 'No image specified'})
            
    except Exception as e:
        logger.error(f"Error adding to collection: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Error adding to collection'})


@login_required
@require_POST
def toggle_favorite(request):
    """Toggle favorite status for wedding transformations (processed images only)"""
    processed_image_id = request.POST.get('processed_image_id')
    
    if not processed_image_id:
        return JsonResponse({'success': False, 'error': 'No image specified'})
    
    try:
        processed_image = get_object_or_404(
            ProcessedImage,
            id=processed_image_id,
            processing_job__user_image__user=request.user
        )
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            processed_image=processed_image
        )
        
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
        logger.error(f"Error toggling favorite: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Error updating favorite'})


@login_required
def favorites_list(request):
    """Display user's favorite wedding transformations"""
    from django.core.paginator import Paginator
    
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'processed_image__processing_job__user_image'
    ).order_by('-created_at')
    
    # Add favorite status to processed images (they're all favorited here)
    for favorite in favorites:
        favorite.processed_image.is_favorited = True
    
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
            # Add favorite status
            item.processed_image.is_favorited = Favorite.objects.filter(
                user=request.user,
                processed_image=item.processed_image
            ).exists()
    
    context = {
        'collection': collection,
        'items': items,
    }
    
    return render(request, 'image_processing/collection_detail.html', context)


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
def ajax_upload_image(request):
    """Handle AJAX image uploads without page reload"""
    try:
        upload_form = ImageUploadForm(request.POST, request.FILES)
        
        if upload_form.is_valid():
            user_image = upload_form.save(commit=False)
            user_image.user = request.user
            user_image.original_filename = request.FILES['image'].name
            user_image.save()
            
            # Force thumbnail creation
            if not user_image.thumbnail:
                user_image.create_thumbnail()
                user_image.refresh_from_db()
            
            return JsonResponse({
                'success': True,
                'image_id': user_image.id,
                'image_url': user_image.image.url,  # Full resolution image
                'thumbnail_url': user_image.thumbnail.url if user_image.thumbnail else user_image.image.url,  # Thumbnail for sidebar
                'image_name': user_image.original_filename,
                'width': user_image.width,
                'height': user_image.height,
                'file_size': user_image.file_size,
                'message': f'"{user_image.original_filename}" uploaded successfully!'
            })
            
        else:
            errors = []
            for field, field_errors in upload_form.errors.items():
                errors.extend(field_errors)
            
            return JsonResponse({
                'success': False,
                'error': ' '.join(errors)
            }, status=400)
    
    except Exception as e:
        logger.error(f"Error in upload: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }, status=500)


@login_required
def delete_processed_image(request, pk):
    """Delete a processed image (user's own images only)"""
    if request.method == 'POST':
        processed_image = get_object_or_404(
            ProcessedImage, 
            pk=pk, 
            processing_job__user_image__user=request.user
        )
        
        try:
            import os
            # Delete the image file
            if processed_image.processed_image and os.path.exists(processed_image.processed_image.path):
                os.remove(processed_image.processed_image.path)
            
            # Delete from database
            processed_image.delete()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Image deleted successfully',
                    'redirect_url': reverse('image_processing:processing_history')
                })
            
            messages.success(request, 'Wedding transformation deleted successfully')
            return redirect('image_processing:processing_history')
            
        except Exception as e:
            logger.error(f"Error deleting processed image: {str(e)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Error deleting image'
                })
            messages.error(request, 'Error deleting image')
            return redirect('image_processing:processed_image_detail', pk=pk)
    
    # GET request - show confirmation page
    processed_image = get_object_or_404(
        ProcessedImage, 
        pk=pk, 
        processing_job__user_image__user=request.user
    )
    
    return render(request, 'image_processing/confirm_delete.html', {
        'processed_image': processed_image
    })


# Helper function to check if a processed image is favorited
def get_favorite_status(user, processed_image_id):
    """Check if a processed image is favorited by the user"""
    if not user.is_authenticated:
        return False
    
    return Favorite.objects.filter(
        user=user,
        processed_image_id=processed_image_id
    ).exists()


# Add this helper function for template context
def add_favorite_status_to_processed_images(user, processed_images):
    """Add is_favorited attribute to processed images"""
    if not user.is_authenticated:
        for img in processed_images:
            img.is_favorited = False
        return processed_images
    
    # Get all favorite IDs for this user
    favorite_ids = set(
        Favorite.objects.filter(user=user)
        .values_list('processed_image_id', flat=True)
    )
    
    # Add is_favorited attribute to each image
    for img in processed_images:
        img.is_favorited = img.id in favorite_ids
    
    return processed_images


# Additional views to add to image_processing/views.py

@login_required
@require_POST  
def edit_collection(request, collection_id):
    """Edit an existing collection"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    
    if collection.is_default:
        messages.error(request, 'Cannot edit the default collection')
        return redirect('image_processing:collections_list')
    
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    is_public = request.POST.get('is_public') == 'on'
    
    if not name:
        messages.error(request, 'Collection name is required')
        return redirect('image_processing:collection_detail', collection_id=collection_id)
    
    try:
        collection.name = name
        collection.description = description
        collection.is_public = is_public
        collection.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Collection "{name}" updated successfully!'
            })
        
        messages.success(request, f'Collection "{name}" updated successfully!')
    except Exception as e:
        logger.error(f"Error updating collection: {str(e)}")
        error_msg = 'Error updating collection'
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        
        messages.error(request, error_msg)
    
    return redirect('image_processing:collection_detail', collection_id=collection_id)


@login_required
@require_POST
def delete_collection(request, collection_id):
    """Delete a collection"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    
    if collection.is_default:
        return JsonResponse({
            'success': False,
            'error': 'Cannot delete the default collection'
        })
    
    try:
        collection_name = collection.name
        collection.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Collection "{collection_name}" deleted successfully',
                'redirect_url': reverse('image_processing:collections_list')
            })
        
        messages.success(request, f'Collection "{collection_name}" deleted successfully')
        return redirect('image_processing:collections_list')
        
    except Exception as e:
        logger.error(f"Error deleting collection: {str(e)}")
        error_msg = 'Error deleting collection'
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        
        messages.error(request, error_msg)
        return redirect('image_processing:collection_detail', collection_id=collection_id)


@login_required
@require_POST
def remove_from_collection(request, collection_id, item_id):
    """Remove an item from a collection"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    collection_item = get_object_or_404(CollectionItem, id=item_id, collection=collection)
    
    try:
        item_title = collection_item.image_title
        collection_item.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'"{item_title}" removed from collection'
            })
        
        messages.success(request, f'"{item_title}" removed from collection')
        
    except Exception as e:
        logger.error(f"Error removing item from collection: {str(e)}")
        error_msg = 'Error removing item from collection'
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})
        
        messages.error(request, error_msg)
    
    return redirect('image_processing:collection_detail', collection_id=collection_id)


@login_required
def get_usage_data(request):
    """API endpoint to get user's usage data"""
    try:
        from usage_limits.usage_tracker import UsageTracker
        usage_data = UsageTracker.get_usage_data(request.user)
        
        return JsonResponse({
            'success': True,
            'remaining': usage_data.get('remaining', 0),
            'limit': usage_data.get('limit', 0),
            'used': usage_data.get('used', 0),
            'reset_date': usage_data.get('reset_date', ''),
        })
    except Exception as e:
        logger.error(f"Error getting usage data: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to load usage data'
        }, status=500)