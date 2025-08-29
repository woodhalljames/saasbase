# image_processing/views.py - CLEANED VERSION with consistent favorites and redo functionality
import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.db import transaction
from django.urls import reverse
from urllib.parse import urlencode

from usage_limits.decorators import usage_limit_required
from .models import (
    UserImage, ImageProcessingJob, ProcessedImage, Collection, CollectionItem, Favorite,
    WEDDING_THEMES, SPACE_TYPES, COLOR_SCHEMES
)
from .forms import (
    ImageUploadForm, WeddingTransformForm, SEASON_CHOICES, LIGHTING_CHOICES
)
from .tasks import process_image_async

logger = logging.getLogger(__name__)


# HELPER FUNCTION - Used consistently across all views
def add_favorite_status_to_processed_images(user, processed_images):
    """Add is_favorited attribute to processed images efficiently"""
    if not user.is_authenticated:
        for img in processed_images:
            img.is_favorited = False
        return processed_images
    
    # Get all favorite IDs for this user in one query
    favorite_ids = set(
        Favorite.objects.filter(user=user)
        .values_list('processed_image_id', flat=True)
    )
    
    # Add is_favorited attribute to each image
    for img in processed_images:
        img.is_favorited = img.id in favorite_ids
    
    return processed_images


@login_required
def wedding_studio(request):
    """Main wedding venue transformation studio - simplified"""
    
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
                        'image_id': user_image.id,
                        'image_url': user_image.image.url,
                        'thumbnail_url': user_image.thumbnail.url if user_image.thumbnail else user_image.image.url,
                        'image_name': user_image.original_filename,
                        'venue_name': user_image.venue_name or '',
                        'venue_description': user_image.venue_description or '',
                        'width': user_image.width,
                        'height': user_image.height,
                        'file_size': user_image.file_size,
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
    
    # Get specific image if image_id is provided
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
    
    # Get recent processing jobs with favorite status
    recent_jobs = ImageProcessingJob.objects.filter(
        user_image__user=request.user
    ).select_related('user_image').prefetch_related('processed_images').order_by('-created_at')[:5]
    
    # Add favorite status to recent jobs
    favorite_ids = set(
        Favorite.objects.filter(user=request.user)
        .values_list('processed_image_id', flat=True)
    )
    
    for job in recent_jobs:
        for processed_image in job.processed_images.all():
            processed_image.is_favorited = processed_image.id in favorite_ids
    
    context = {
        'recent_images': recent_images,
        'preselected_image': preselected_image,
        'usage_data': usage_data,
        'recent_jobs': recent_jobs,
        # Core choices only
        'wedding_themes': WEDDING_THEMES,
        'space_types': SPACE_TYPES,
        'color_schemes': COLOR_SCHEMES,
        'season_choices': SEASON_CHOICES,
        'lighting_choices': LIGHTING_CHOICES,
        # Forms
        'upload_form': ImageUploadForm(),
        'transform_form': WeddingTransformForm(),
    }
    
    return render(request, 'image_processing/wedding_studio.html', context)


@login_required
@require_http_methods(["POST"])
def process_wedding_image(request, pk):
    """Process wedding venue image with AI transformation - SIMPLIFIED VERSION"""
    try:
        # Get the user's image
        user_image = get_object_or_404(UserImage, id=pk, user=request.user)
        
        # Check usage limits
        from usage_limits.usage_tracker import UsageTracker
        usage_data = UsageTracker.get_usage_data(request.user)
        
        if usage_data['remaining'] <= 0:
            return JsonResponse({
                'success': False,
                'error': 'You have reached your monthly transformation limit. Please upgrade your subscription to continue.',
                'usage_data': usage_data,
                'needs_upgrade': True
            }, status=429)
        
        # Try to increment usage
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
        wedding_theme = data.get('wedding_theme', '').strip()
        space_type = data.get('space_type', '').strip()
        
        if not wedding_theme or not space_type:
            return JsonResponse({
                'success': False,
                'error': 'Wedding theme and space type are required'
            }, status=400)
        
        # Validate theme and space type exist in choices
        valid_themes = [choice[0] for choice in WEDDING_THEMES]
        valid_spaces = [choice[0] for choice in SPACE_TYPES]
        
        if wedding_theme not in valid_themes:
            return JsonResponse({
                'success': False,
                'error': f'Invalid wedding theme: {wedding_theme}'
            }, status=400)
            
        if space_type not in valid_spaces:
            return JsonResponse({
                'success': False,
                'error': f'Invalid space type: {space_type}'
            }, status=400)
        
        # Create processing job with simplified fields and FIXED parameters
        job = None
        with transaction.atomic():
            job = ImageProcessingJob(
                user_image=user_image,
                wedding_theme=wedding_theme,
                space_type=space_type,
                # FIXED AI GENERATION PARAMETERS
                strength=0.70,  # Fixed at 70%
                cfg_scale=7.5,  # Standard CFG
                steps=30,       # Fixed at 30 steps
                output_format='png'
            )
            
            # Handle SIMPLIFIED optional fields carefully - only set if valid and not empty
            optional_fields = [
                ('season', SEASON_CHOICES, 'season'),
                ('lighting', LIGHTING_CHOICES, 'lighting'),  # Updated from lighting_mood
                ('color_scheme', COLOR_SCHEMES, 'color_scheme'),
            ]
            
            for field_name, choices, data_key in optional_fields:
                value = data.get(data_key, '').strip()
                if value:  # Only process if not empty
                    # Validate against choices if applicable
                    if choices:
                        valid_values = [choice[0] for choice in choices if choice[0]]
                        if value in valid_values:
                            # Map 'lighting' to 'lighting_mood' field for backward compatibility
                            if field_name == 'lighting':
                                setattr(job, 'lighting_mood', value)
                            else:
                                setattr(job, field_name, value)
                        else:
                            logger.warning(f"Invalid {field_name}: {value}, skipping")
            
            # Handle text fields
            special_features = data.get('special_features', '').strip()
            if special_features and len(special_features) <= 500:
                job.special_features = special_features
            
            avoid = data.get('avoid', '').strip()
            if avoid and len(avoid) <= 500:
                job.avoid = avoid
            
            # Handle seed if provided
            seed_value = data.get('seed')
            if seed_value:
                try:
                    job.seed = int(seed_value)
                except (ValueError, TypeError):
                    pass  # Leave seed as None
            
            # Save the job
            job.save()
            
            logger.info(f"Created simplified job {job.id} - Theme: {wedding_theme}, Space: {space_type}")
            logger.info(f"Fixed params: strength=0.70, steps=30, cfg_scale=7.5")
            logger.info(f"Optional params: season={job.season}, lighting={job.lighting_mood}, "
                       f"color={job.color_scheme}")
            
            # Force database commit and refresh
            transaction.on_commit(lambda: None)
        
        # Refresh from database to ensure we have the committed version
        job.refresh_from_db()
        
        # Add delay to ensure database commit is visible
        import time
        time.sleep(0.1)
        
        # Verify job exists before queuing task
        try:
            verification_job = ImageProcessingJob.objects.get(id=job.id)
            logger.info(f"Job {job.id} verified in database before queuing task")
        except ImageProcessingJob.DoesNotExist:
            logger.error(f"Job {job.id} not found after creation - database issue")
            return JsonResponse({
                'success': False,
                'error': 'Database error: Job creation failed'
            }, status=500)
        
        # Queue the processing task with countdown to ensure database visibility
        task_result = process_image_async.apply_async(args=[job.id], countdown=2)
        logger.info(f"Task queued with ID: {task_result.id} for job {job.id}")
        
        # Return success with job details for frontend monitoring
        return JsonResponse({
            'success': True,
            'job_id': job.id,
            'task_id': task_result.id,
            'status': 'pending',
            'message': 'Your wedding transformation has been queued!',
            'job_details': {
                'theme': wedding_theme,
                'space_type': space_type,
                'theme_display': dict(WEDDING_THEMES).get(wedding_theme, wedding_theme),
                'space_display': dict(SPACE_TYPES).get(space_type, space_type),
                'strength': 0.70,  # Fixed value
                'cfg_scale': 7.5,  # Fixed value  
                'steps': 30        # Fixed value
            }
        })
        
    except Exception as e:
        logger.error(f"Error in process_wedding_image: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }, status=500)


@login_required
def job_status(request, job_id):
    """Get status of a processing job - simplified response"""
    try:
        job = get_object_or_404(ImageProcessingJob, id=job_id, user_image__user=request.user)
        
        data = {
            'job_id': job.id,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'wedding_theme': job.wedding_theme,
            'space_type': job.space_type,
            'strength': job.strength,
            'cfg_scale': job.cfg_scale,
            'steps': job.steps,
        }
        
        # Add display names
        if job.wedding_theme:
            data['theme_display'] = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme)
        if job.space_type:
            data['space_display'] = dict(SPACE_TYPES).get(job.space_type, job.space_type)
        
        # Add simplified optional fields only if they exist
        if job.season:
            data['season'] = job.season
        if job.lighting_mood:  # Still stored as lighting_mood in DB
            data['lighting'] = job.lighting_mood
            data['lighting_display'] = dict(LIGHTING_CHOICES).get(job.lighting_mood, job.lighting_mood)
        if job.color_scheme:
            data['color_scheme'] = job.color_scheme
            data['color_display'] = dict(COLOR_SCHEMES).get(job.color_scheme, job.color_scheme)
        if job.special_features:
            data['special_features'] = job.special_features
        if job.avoid:
            data['avoid'] = job.avoid
        
        if job.status == 'completed':
            data['completed_at'] = job.completed_at.isoformat() if job.completed_at else None
            processed_images = job.processed_images.all()
            if processed_images:
                processed_img = processed_images.first()
                data['result'] = {
                    'id': processed_img.id,
                    'image_url': processed_img.processed_image.url,
                    'seed': processed_img.stability_seed,
                    'width': processed_img.width,
                    'height': processed_img.height,
                    'file_size': processed_img.file_size,
                }
                # Check if favorited
                data['result']['is_favorited'] = Favorite.objects.filter(
                    user=request.user,
                    processed_image=processed_img
                ).exists()
        elif job.status == 'failed':
            data['error_message'] = job.error_message
        elif job.status == 'processing':
            data['started_at'] = job.started_at.isoformat() if job.started_at else None
        
        return JsonResponse(data)
        
    except Exception as e:
        logger.error(f"Error getting job status for job {job_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to get job status'
        }, status=500)


@login_required
def image_detail(request, pk):
    """Display single image with wedding processing options - simplified"""
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
        'color_schemes': COLOR_SCHEMES,
        'season_choices': SEASON_CHOICES,
        'lighting_choices': LIGHTING_CHOICES,
    }
    
    return render(request, 'image_processing/image_detail.html', context)


@login_required
def processing_history(request):
    """View all wedding processing jobs for the user - WITH CONSISTENT FAVORITES"""
    jobs = ImageProcessingJob.objects.filter(
        user_image__user=request.user
    ).select_related('user_image').prefetch_related('processed_images').order_by('-created_at')
    
    # CRITICAL: Get favorite IDs once for efficiency
    favorite_ids = set(
        Favorite.objects.filter(user=request.user)
        .values_list('processed_image_id', flat=True)
    )
    
    # Add display names and CONSISTENT favorite status to jobs
    for job in jobs:
        job.theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme) if job.wedding_theme else 'Unknown'
        job.space_display = dict(SPACE_TYPES).get(job.space_type, job.space_type) if job.space_type else 'Unknown'
        
        # Add optional field display names
        if job.lighting_mood:
            job.lighting_display = dict(LIGHTING_CHOICES).get(job.lighting_mood, job.lighting_mood)
        if job.color_scheme:
            job.color_display = dict(COLOR_SCHEMES).get(job.color_scheme, job.color_scheme)
        
        # CRITICAL: Add favorite status to ALL processed images for this job
        for processed_image in job.processed_images.all():
            processed_image.is_favorited = processed_image.id in favorite_ids
    
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
def redo_transformation_with_job(request, job_id):
    """Redirect to wedding studio with job parameters pre-filled"""
    job = get_object_or_404(ImageProcessingJob, id=job_id, user_image__user=request.user)
    
    # Build query parameters from the job settings
    params = {
        'wedding_theme': job.wedding_theme,
        'space_type': job.space_type,
    }
    
    # Add optional parameters if they exist
    if job.season:
        params['season'] = job.season
    if job.lighting_mood:
        params['lighting'] = job.lighting_mood  # Map to 'lighting' for consistency
    if job.color_scheme:
        params['color_scheme'] = job.color_scheme
    if job.special_features:
        params['special_features'] = job.special_features
    if job.avoid:
        params['avoid'] = job.avoid
    if job.seed:
        params['seed'] = job.seed
    
    # Build the redirect URL
    base_url = reverse('image_processing:wedding_studio')
    query_string = urlencode(params)
    redirect_url = f"{base_url}?{query_string}"
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'redirect_url': redirect_url,
            'message': 'Redirecting to studio with saved settings...'
        })
    
    return redirect(redirect_url)


@login_required 
def image_gallery(request):
    """Display images and transformations - WITH CONSISTENT FAVORITES"""
    # Original uploaded images
    uploaded_images = UserImage.objects.filter(user=request.user).order_by('-uploaded_at')
    
    # All processed images with favorite status
    all_transformations = ProcessedImage.objects.filter(
        processing_job__user_image__user=request.user
    ).select_related('processing_job__user_image').order_by('-created_at')
    
    # CRITICAL: CONSISTENTLY add favorite status
    all_transformations = add_favorite_status_to_processed_images(request.user, all_transformations)
    
    # Get usage data
    from usage_limits.usage_tracker import UsageTracker
    usage_data = UsageTracker.get_usage_data(request.user)
    
    # Combine and paginate all images
    all_images = []
    for img in uploaded_images:
        all_images.append({
            'type': 'original',
            'object': img,
            'date': img.uploaded_at,
            'title': img.venue_name or img.original_filename,
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
    from django.core.paginator import Paginator
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
def favorites_list(request):
    """Display favorite transformations - WITH REDO FUNCTIONALITY"""
    from django.core.paginator import Paginator
    
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'processed_image__processing_job__user_image'
    ).order_by('-created_at')
    
    # CRITICAL: Add consistent favorite status and job display names
    for favorite in favorites:
        favorite.processed_image.is_favorited = True  # Always true in favorites list
        
        # Add job display names for redo functionality
        job = favorite.processed_image.processing_job
        job.theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, 'Unknown') if job.wedding_theme else 'Unknown'
        job.space_display = dict(SPACE_TYPES).get(job.space_type, 'Unknown') if job.space_type else 'Unknown'
        
        # Add optional field display names for UI
        if job.lighting_mood:
            job.lighting_display = dict(LIGHTING_CHOICES).get(job.lighting_mood, job.lighting_mood)
        if job.color_scheme:
            job.color_display = dict(COLOR_SCHEMES).get(job.color_scheme, job.color_scheme)
    
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
    """View details of processed image - WITH CONSISTENT FAVORITES"""
    processed_image = get_object_or_404(
        ProcessedImage, 
        pk=pk, 
        processing_job__user_image__user=request.user
    )
    
    # CRITICAL: Add favorite status consistently
    processed_image.is_favorited = Favorite.objects.filter(
        user=request.user,
        processed_image=processed_image
    ).exists()
    
    # Add display names
    job = processed_image.processing_job
    theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, 'Unknown')
    space_display = dict(SPACE_TYPES).get(job.space_type, 'Unknown')
    
    # Simplified optional field display names
    color_display = dict(COLOR_SCHEMES).get(job.color_scheme, job.color_scheme) if job.color_scheme else None
    lighting_display = dict(LIGHTING_CHOICES).get(job.lighting_mood, job.lighting_mood) if job.lighting_mood else None
    
    context = {
        'processed_image': processed_image,
        'theme_display': theme_display,
        'space_display': space_display,
        'color_display': color_display,
        'lighting_display': lighting_display,
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
    """Toggle favorite status for wedding transformations"""
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
                'image_url': user_image.image.url,
                'thumbnail_url': user_image.thumbnail.url if user_image.thumbnail else user_image.image.url,
                'image_name': user_image.original_filename,
                'venue_name': user_image.venue_name or '',
                'venue_description': user_image.venue_description or '',
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


@login_required
def job_result(request, job_id):
    """Get the result of a completed processing job"""
    job = get_object_or_404(ImageProcessingJob, id=job_id, user_image__user=request.user)
    
    if job.status != 'completed':
        return JsonResponse({
            'success': False,
            'error': 'Job not completed yet'
        })
    
    # Get the processed images
    processed_images = job.processed_images.all()
    
    if not processed_images:
        return JsonResponse({
            'success': False,
            'error': 'No results found'
        })
    
    # Get the first (primary) result
    processed_image = processed_images.first()
    
    # Add favorite status
    is_favorited = Favorite.objects.filter(
        user=request.user,
        processed_image=processed_image
    ).exists()
    
    return JsonResponse({
        'success': True,
        'result': {
            'id': processed_image.id,
            'image_url': processed_image.processed_image.url,
            'width': processed_image.width,
            'height': processed_image.height,
            'file_size': processed_image.file_size,
            'created_at': processed_image.created_at.isoformat(),
            'is_favorited': is_favorited,
            'job': {
                'id': job.id,
                'theme': job.wedding_theme,
                'space': job.space_type,
                'strength': job.strength,
                'theme_display': dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme) if job.wedding_theme else None,
                'space_display': dict(SPACE_TYPES).get(job.space_type, job.space_type) if job.space_type else None,
            }
        }
    })


# Collection management views
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
    
    # Get recent favorites with consistent favorite status
    recent_favorites = Favorite.objects.filter(user=request.user).select_related(
        'processed_image__processing_job'
    ).order_by('-created_at')[:6]
    
    # Add favorite status to recent favorites (they're all favorited)
    for favorite in recent_favorites:
        favorite.processed_image.is_favorited = True
    
    context = {
        'default_collection': default_collection,
        'collections': collections,
        'recent_favorites': recent_favorites,
    }
    
    return render(request, 'image_processing/collections_list.html', context)


@login_required 
def delete_processed_image(request, pk):
    """Delete a processed image"""
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