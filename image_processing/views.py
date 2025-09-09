# image_processing/views.py - Updated with fixed APIs and collection management

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
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from usage_limits.decorators import usage_limit_required
from .models import (
    UserImage, ImageProcessingJob, ProcessedImage, Collection, CollectionItem, Favorite,
    WEDDING_THEMES, SPACE_TYPES, COLOR_SCHEMES
)
from .forms import (
    ImageUploadForm, WeddingTransformForm,
    SEASON_CHOICES, LIGHTING_CHOICES, PROMPT_MODE_CHOICES
)
from .tasks import process_venue_transformation, process_venue_realtime

logger = logging.getLogger(__name__)


# HELPER FUNCTION - Add favorite status to processed images
def add_favorite_status_to_processed_images(user, processed_images):
    """Add is_favorited attribute to processed images efficiently"""
    if not user.is_authenticated:
        for img in processed_images:
            img.is_favorited = False
        return processed_images
    
    favorite_ids = set(
        Favorite.objects.filter(user=user)
        .values_list('processed_image_id', flat=True)
    )
    
    for img in processed_images:
        img.is_favorited = img.id in favorite_ids
    
    return processed_images


@login_required
def wedding_studio(request):
    """Main wedding venue transformation studio with preselected image support"""
    
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
    
    # FIXED: Get specific image if image_id is provided
    preselected_image = None
    image_id = request.GET.get('image_id')
    if image_id:
        try:
            preselected_image = UserImage.objects.get(id=image_id, user=request.user)
            logger.info(f"Preselected image found: {preselected_image.original_filename} (ID: {image_id})")
        except UserImage.DoesNotExist:
            logger.warning(f"Preselected image not found for ID: {image_id}")
            messages.warning(request, "The selected image was not found.")
        except ValueError:
            logger.warning(f"Invalid image_id parameter: {image_id}")
    
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
    
    # Pre-fill form parameters from URL if provided (for redo functionality)
    initial_form_data = {}
    for param in ['wedding_theme', 'space_type', 'season', 'lighting', 'color_scheme', 'user_instructions', 'custom_prompt']:
        value = request.GET.get(param)
        if value:
            # Map 'lighting' URL param to 'lighting_mood' field
            if param == 'lighting':
                initial_form_data['lighting_mood'] = value
            else:
                initial_form_data[param] = value
    
    # Set prompt mode based on whether custom_prompt is provided
    if 'custom_prompt' in initial_form_data:
        initial_form_data['prompt_mode'] = 'custom'

    context = {
        'recent_images': recent_images,
        'preselected_image': preselected_image,
        'usage_data': usage_data,
        'recent_jobs': recent_jobs,
        # Core choices
        'wedding_themes': WEDDING_THEMES,
        'space_types': SPACE_TYPES,
        'color_schemes': COLOR_SCHEMES,
        'season_choices': SEASON_CHOICES,
        'lighting_choices': LIGHTING_CHOICES,
        'prompt_mode_choices': PROMPT_MODE_CHOICES,
        # Forms
        'upload_form': ImageUploadForm(),
        'transform_form': WeddingTransformForm(initial=initial_form_data),
        # Gemini-specific info
        'gemini_model': 'gemini-2.5-flash-image-preview',
        'supports_custom_prompts': True,
        'processing_mode': 'real-time',
    }
    
    return render(request, 'image_processing/wedding_studio.html', context)

@login_required
@require_http_methods(["POST"])
def process_wedding_image(request, pk):
    """Process wedding venue image with real-time Gemini transformation"""
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
        
        # Parse request data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid request data'
            }, status=400)
        
        # Determine processing mode
        prompt_mode = data.get('prompt_mode', 'guided')
        
        # Get user instructions (applies to both modes)
        user_instructions = data.get('user_instructions', '').strip()
        
        # Validate and create job based on mode
        if prompt_mode == 'custom':
            # Custom prompt mode
            custom_prompt = data.get('custom_prompt', '').strip()
            
            if not custom_prompt:
                return JsonResponse({
                    'success': False,
                    'error': 'Custom prompt is required for custom mode'
                }, status=400)
            
            if len(custom_prompt) < 10:
                return JsonResponse({
                    'success': False,
                    'error': 'Custom prompt is too short - please provide more detail'
                }, status=400)
            
            # Create job for custom prompt
            job_data = {
                'user_image': user_image,
                'custom_prompt': custom_prompt,
                'user_instructions': user_instructions if user_instructions else None,
                'wedding_theme': '',
                'space_type': ''
            }
            
        else:
            # Guided mode
            wedding_theme = data.get('wedding_theme', '').strip()
            space_type = data.get('space_type', '').strip()
            
            if not wedding_theme or not space_type:
                return JsonResponse({
                    'success': False,
                    'error': 'Wedding theme and space type are required for guided mode'
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
            
            # Create guided job data
            job_data = {
                'user_image': user_image,
                'wedding_theme': wedding_theme,
                'space_type': space_type,
                'user_instructions': user_instructions if user_instructions else None
            }
            
            # Handle optional fields for guided mode
            optional_fields = [
                ('season', SEASON_CHOICES, 'season'),
                ('lighting_mood', LIGHTING_CHOICES, 'lighting'),
                ('color_scheme', COLOR_SCHEMES, 'color_scheme'),
            ]
            
            for field_name, choices, data_key in optional_fields:
                value = data.get(data_key, '').strip()
                if value:
                    if choices:
                        valid_values = [choice[0] for choice in choices if choice[0]]
                        if value in valid_values:
                            job_data[field_name] = value
                        else:
                            logger.warning(f"Invalid {field_name}: {value}, skipping")
        
        # Create and save the job
        with transaction.atomic():
            job = ImageProcessingJob.objects.create(**job_data)
            
            logger.info(f"Created venue transformation job {job.id} - Mode: {prompt_mode}, User: {request.user.username}")
            if prompt_mode == 'custom':
                logger.info(f"Custom prompt: {job.custom_prompt[:100]}...")
            else:
                logger.info(f"Guided: {job.wedding_theme} + {job.space_type}")
            
            if user_instructions:
                logger.info(f"User instructions: {user_instructions[:100]}...")
        
        # Choose processing method based on preference
        use_realtime = data.get('realtime', False) or getattr(request.user, 'prefer_realtime', False)
        
        if use_realtime:
            # Real-time processing - process immediately
            try:
                result = process_venue_realtime(job.id)
                
                if result['success']:
                    # Get the processed image details
                    processed_image = ProcessedImage.objects.get(id=result['processed_image_id'])
                    
                    return JsonResponse({
                        'success': True,
                        'job_id': job.id,
                        'status': 'completed',
                        'message': 'Venue transformation completed!',
                        'processing_mode': 'realtime',
                        'result': {
                            'id': processed_image.id,
                            'image_url': processed_image.processed_image.url,
                            'width': processed_image.width,
                            'height': processed_image.height,
                            'is_favorited': False  # New image, not favorited yet
                        },
                        'job_details': _get_job_details(job, prompt_mode)
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'job_id': job.id,
                        'error': result.get('error', 'Transformation failed'),
                        'processing_mode': 'realtime'
                    }, status=500)
                    
            except Exception as e:
                logger.error(f"Real-time processing failed for job {job.id}: {str(e)}")
                # Fall back to async processing
                pass
        
        # Async processing (default or fallback)
        def queue_transformation():
            task_result = process_venue_transformation.apply_async(args=[job.id])
            logger.info(f"Venue transformation task queued: {task_result.id} for job {job.id}")
            return task_result
        
        # Queue the task after transaction commits
        transaction.on_commit(queue_transformation)
        
        # Return success with job details
        return JsonResponse({
            'success': True,
            'job_id': job.id,
            'status': 'pending',
            'message': 'Venue transformation started with Gemini!',
            'processing_mode': 'async',
            'job_details': _get_job_details(job, prompt_mode)
        })
        
    except Exception as e:
        logger.error(f"Error in process_wedding_image: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }, status=500)


def _get_job_details(job, prompt_mode):
    """Helper to get job details for JSON response"""
    details = {
        'mode': prompt_mode,
        'model': 'gemini-2.5-flash-image-preview',
        'has_user_instructions': bool(job.user_instructions)
    }
    
    if prompt_mode == 'custom':
        details['custom_prompt'] = job.custom_prompt[:100] + ('...' if len(job.custom_prompt) > 100 else '')
    else:
        details.update({
            'theme': job.wedding_theme,
            'space_type': job.space_type,
            'theme_display': dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme),
            'space_display': dict(SPACE_TYPES).get(job.space_type, job.space_type),
        })
        
        # Add optional details if present
        if job.season:
            details['season'] = job.season
        if job.lighting_mood:
            details['lighting'] = job.lighting_mood
            details['lighting_display'] = dict(LIGHTING_CHOICES).get(job.lighting_mood, job.lighting_mood)
        if job.color_scheme:
            details['color_scheme'] = job.color_scheme
            details['color_display'] = dict(COLOR_SCHEMES).get(job.color_scheme, job.color_scheme)
    
    return details


@login_required
def job_status(request, job_id):
    """Get real-time status of a venue transformation job"""
    try:
        job = get_object_or_404(ImageProcessingJob, id=job_id, user_image__user=request.user)
        
        data = {
            'job_id': job.id,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'model': 'gemini-2.5-flash-image-preview',
            'mode': 'custom' if job.custom_prompt else 'guided',
            'has_user_instructions': bool(job.user_instructions)
        }
        
        # Add details based on mode
        if job.custom_prompt:
            data['custom_prompt'] = job.custom_prompt
            data['prompt_preview'] = job.custom_prompt[:100] + ('...' if len(job.custom_prompt) > 100 else '')
        else:
            data['wedding_theme'] = job.wedding_theme
            data['space_type'] = job.space_type
            
            # Add display names
            if job.wedding_theme:
                data['theme_display'] = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme)
            if job.space_type:
                data['space_display'] = dict(SPACE_TYPES).get(job.space_type, job.space_type)
            
            # Add optional fields only if they exist
            if job.season:
                data['season'] = job.season
            if job.lighting_mood:
                data['lighting'] = job.lighting_mood
                data['lighting_display'] = dict(LIGHTING_CHOICES).get(job.lighting_mood, job.lighting_mood)
            if job.color_scheme:
                data['color_scheme'] = job.color_scheme
                data['color_display'] = dict(COLOR_SCHEMES).get(job.color_scheme, job.color_scheme)
        
        # Add user instructions if present
        if job.user_instructions:
            data['user_instructions'] = job.user_instructions
            data['user_instructions_preview'] = job.user_instructions[:100] + ('...' if len(job.user_instructions) > 100 else '')
        
        if job.status == 'completed':
            data['completed_at'] = job.completed_at.isoformat() if job.completed_at else None
            processed_images = job.processed_images.all()
            if processed_images:
                processed_img = processed_images.first()
                data['result'] = {
                    'id': processed_img.id,
                    'image_url': processed_img.processed_image.url,
                    'width': processed_img.width,
                    'height': processed_img.height,
                    'file_size': processed_img.file_size,
                    'gemini_model': processed_img.gemini_model,
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
def test_gemini_api(request):
    """Test endpoint for Gemini API connectivity"""
    try:
        from .services import test_gemini_service
        
        result = test_gemini_service()
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': 'Gemini 2.5 Flash Image Preview API connection successful!',
                'model': result.get('model'),
                'test_image_size': result.get('test_image_size', 0),
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f"Gemini API test failed: {result.get('error')}"
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error testing Gemini API: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Gemini API test failed'
        }, status=500)


@login_required
def redo_transformation_with_job(request, job_id):
    """Redirect to wedding studio with job parameters pre-filled - UPDATED for all form fields"""
    job = get_object_or_404(ImageProcessingJob, id=job_id, user_image__user=request.user)
    
    # Build query parameters from the job settings
    params = {}
    
    if job.custom_prompt:
        # Custom prompt mode
        params['prompt_mode'] = 'custom'
        params['custom_prompt'] = job.custom_prompt
    else:
        # Guided mode
        params['prompt_mode'] = 'guided'
        if job.wedding_theme:
            params['wedding_theme'] = job.wedding_theme
        if job.space_type:
            params['space_type'] = job.space_type
        
        # Add optional parameters if they exist
        if job.season:
            params['season'] = job.season
        if job.lighting_mood:
            params['lighting'] = job.lighting_mood  # Note: URL param is 'lighting', field is 'lighting_mood'
        if job.color_scheme:
            params['color_scheme'] = job.color_scheme
    
    # Add user instructions (applies to both modes)
    if job.user_instructions:
        params['user_instructions'] = job.user_instructions
    
    # Add image selection
    params['image_id'] = job.user_image.id
    
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

# Additional view functions (favorites, collections, etc.) remain the same
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


# Image management views
@login_required
def image_detail(request, pk):
    """View details of a user's image"""
    image = get_object_or_404(UserImage, id=pk, user=request.user)
    
    # Get processing jobs for this image
    jobs = image.processing_jobs.all().order_by('-created_at')
    
    context = {
        'image': image,
        'jobs': jobs,
    }
    
    return render(request, 'image_processing/image_detail.html', context)


@login_required
def image_gallery(request):
    """UPDATED: View all user uploaded images with mobile-friendly design"""
    # Get all user images
    images_list = UserImage.objects.filter(user=request.user).order_by('-uploaded_at')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        images_list = images_list.filter(
            Q(original_filename__icontains=search_query) |
            Q(venue_name__icontains=search_query) |
            Q(venue_description__icontains=search_query)
        )
    
    # Filter by date
    date_filter = request.GET.get('date_filter', '')
    if date_filter == 'today':
        from django.utils import timezone
        today = timezone.now().date()
        images_list = images_list.filter(uploaded_at__date=today)
    elif date_filter == 'week':
        from datetime import timedelta
        from django.utils import timezone
        week_ago = timezone.now().date() - timedelta(days=7)
        images_list = images_list.filter(uploaded_at__date__gte=week_ago)
    elif date_filter == 'month':
        from datetime import timedelta
        from django.utils import timezone
        month_ago = timezone.now().date() - timedelta(days=30)
        images_list = images_list.filter(uploaded_at__date__gte=month_ago)
    
    # Pagination - mobile friendly (smaller page size)
    paginator = Paginator(images_list, 12)  # 12 images per page for mobile
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add stats
    total_images = UserImage.objects.filter(user=request.user).count()
    total_transformations = ImageProcessingJob.objects.filter(user_image__user=request.user).count()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'date_filter': date_filter,
        'total_images': total_images,
        'total_transformations': total_transformations,
    }
    
    return render(request, 'image_processing/image_gallery.html', context)


@login_required
def processing_history(request):
    """View all wedding venue transformation jobs"""
    jobs = ImageProcessingJob.objects.filter(
        user_image__user=request.user
    ).select_related('user_image').prefetch_related('processed_images').order_by('-created_at')
    
    # Get favorite IDs once for efficiency
    favorite_ids = set(
        Favorite.objects.filter(user=request.user)
        .values_list('processed_image_id', flat=True)
    )
    
    # Add display names and favorite status to jobs
    for job in jobs:
        # Handle both custom and guided modes
        if job.custom_prompt:
            job.mode_display = 'Custom Prompt'
            job.theme_display = 'Custom Design'
            job.space_display = 'Custom Space'
            job.prompt_preview = job.custom_prompt[:100] + ('...' if len(job.custom_prompt) > 100 else '')
        else:
            job.mode_display = 'Guided Design'
            job.theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme) if job.wedding_theme else 'Unknown'
            job.space_display = dict(SPACE_TYPES).get(job.space_type, job.space_type) if job.space_type else 'Unknown'
        
        # Add user instructions info
        job.has_user_instructions = bool(job.user_instructions)
        if job.user_instructions:
            job.user_instructions_preview = job.user_instructions[:50] + ('...' if len(job.user_instructions) > 50 else '')
        
        # Add optional field display names for guided mode
        if job.lighting_mood:
            job.lighting_display = dict(LIGHTING_CHOICES).get(job.lighting_mood, job.lighting_mood)
        if job.color_scheme:
            job.color_display = dict(COLOR_SCHEMES).get(job.color_scheme, job.color_scheme)
        
        # Add favorite status to ALL processed images for this job
        for processed_image in job.processed_images.all():
            processed_image.is_favorited = processed_image.id in favorite_ids
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'gemini_model': 'gemini-2.5-flash-image-preview',
    }
    
    return render(request, 'image_processing/processing_history.html', context)


@login_required
def processed_image_detail(request, pk):
    """View details of a processed image with proper theme/space display"""
    processed_image = get_object_or_404(
        ProcessedImage, 
        id=pk, 
        processing_job__user_image__user=request.user
    )
    
    # Check if favorited
    is_favorited = Favorite.objects.filter(
        user=request.user,
        processed_image=processed_image
    ).exists()
    
    processed_image.is_favorited = is_favorited
    
    # Get the job for theme/space display
    job = processed_image.processing_job
    
    # Determine theme and space display names
    if job.custom_prompt:
        theme_display = "Custom Design"
        space_display = "Custom Space"
    else:
        theme_display = job.theme_display_name if hasattr(job, 'theme_display_name') else dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme or 'Unknown')
        space_display = job.space_display_name if hasattr(job, 'space_display_name') else dict(SPACE_TYPES).get(job.space_type, job.space_type or 'Unknown')
    
    context = {
        'processed_image': processed_image,
        'job': job,
        'original_image': job.user_image,
        'theme_display': theme_display,
        'space_display': space_display,
    }
    
    return render(request, 'image_processing/processed_image_detail.html', context)

@login_required
@require_POST
def delete_processed_image(request, pk):
    """Delete a processed image"""
    try:
        # Get the processed image, ensuring it belongs to the current user
        processed_image = get_object_or_404(
            ProcessedImage, 
            id=pk, 
            processing_job__user_image__user=request.user
        )
        
        # Store details for response
        image_title = processed_image.transformation_title
        job_id = processed_image.processing_job.id
        
        # Delete the processed image (this will also remove the file)
        processed_image.delete()
        
        logger.info(f"User {request.user.username} deleted processed image {pk}")
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Deleted "{image_title}" successfully',
                'redirect_url': reverse('image_processing:processing_history')
            })
        else:
            messages.success(request, f'Deleted "{image_title}" successfully')
            return redirect('image_processing:processing_history')
            
    except ProcessedImage.DoesNotExist:
        error_msg = 'Image not found or you do not have permission to delete it'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': error_msg
            }, status=404)
        else:
            messages.error(request, error_msg)
            return redirect('image_processing:processing_history')
            
    except Exception as e:
        logger.error(f"Error deleting processed image {pk}: {str(e)}")
        error_msg = 'An error occurred while deleting the image'
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': error_msg
            }, status=500)
        else:
            messages.error(request, error_msg)
            return redirect('image_processing:processing_history')


@login_required
def favorites_list(request):
    """List user's favorite images"""
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'processed_image__processing_job__user_image'
    ).order_by('-created_at')
    
    # Add favorited status (always True for this view)
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
def ajax_upload_image(request):
    """AJAX endpoint for image uploads"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    form = ImageUploadForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            user_image = form.save(commit=False)
            user_image.user = request.user
            user_image.original_filename = form.cleaned_data['image'].name
            user_image.save()
            
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
            
        except Exception as e:
            logger.error(f"Error uploading image via AJAX: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Failed to upload image: {str(e)}'
            }, status=400)
    else:
        # Handle form errors
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(str(error))
        
        return JsonResponse({
            'success': False,
            'error': '; '.join(error_messages)
        }, status=400)


# Collection management views - UPDATED for improved API and mobile

@login_required
def collections_list(request):
    """Display user's wedding inspiration collections"""
    collections = Collection.objects.filter(user=request.user).order_by('-updated_at')
    
    recent_favorites = Favorite.objects.filter(user=request.user).select_related(
        'processed_image__processing_job'
    ).order_by('-created_at')[:6]
    
    for favorite in recent_favorites:
        favorite.processed_image.is_favorited = True
    
    context = {
        'collections': collections,
        'recent_favorites': recent_favorites,
    }
    
    return render(request, 'image_processing/collections_list.html', context)


@login_required
def get_user_collections(request):
    """FIXED API endpoint to get user's collections as JSON with better error handling"""
    try:
        # Get collections ordered by creation date (newest first), exclude default
        collections = Collection.objects.filter(
            user=request.user, 
            is_default=False
        ).order_by('-created_at')  # Changed to -created_at for newest first
        
        collections_data = []
        for collection in collections:
            collections_data.append({
                'id': collection.id,
                'name': collection.name,
                'description': collection.description or '',
                'item_count': collection.item_count,
                'is_default': collection.is_default,
                'is_public': collection.is_public,
                'created_at': collection.created_at.isoformat(),
                'updated_at': collection.updated_at.isoformat(),
            })
        
        logger.info(f"Retrieved {len(collections_data)} collections for user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'collections': collections_data,
            'total_count': len(collections_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting user collections: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to load collections',
            'collections': []
        }, status=500)


@login_required
def get_processed_image_collections(request, processed_image_id):
    """FIXED: Get collections that contain a specific processed image"""
    try:
        # Verify the processed image belongs to the user
        processed_image = get_object_or_404(
            ProcessedImage,
            id=processed_image_id,
            processing_job__user_image__user=request.user
        )
        
        # Get collection IDs that contain this image
        collection_ids = list(
            CollectionItem.objects.filter(
                processed_image=processed_image
            ).values_list('collection_id', flat=True)
        )
        
        logger.info(f"Found {len(collection_ids)} collections containing processed image {processed_image_id}")
        
        return JsonResponse({
            'success': True,
            'collection_ids': collection_ids
        })
        
    except ProcessedImage.DoesNotExist:
        logger.warning(f"Processed image {processed_image_id} not found for user {request.user.username}")
        return JsonResponse({
            'success': False,
            'error': 'Image not found',
            'collection_ids': []
        }, status=404)
        
    except Exception as e:
        logger.error(f"Error getting image collections: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error loading collections',
            'collection_ids': []
        }, status=500)


@login_required
@require_POST
def add_to_collection(request):
    """FIXED: Add an image to a collection with better error handling"""
    collection_id = request.POST.get('collection_id')
    processed_image_id = request.POST.get('processed_image_id')
    user_image_id = request.POST.get('user_image_id')
    
    if not collection_id:
        return JsonResponse({'success': False, 'message': 'No collection specified'})
    
    try:
        # Verify collection belongs to user
        collection = get_object_or_404(Collection, id=collection_id, user=request.user)
        
        if processed_image_id:
            # Verify processed image belongs to user
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
                logger.info(f"Added processed image {processed_image_id} to collection {collection_id}")
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
            # Verify user image belongs to user
            user_image = get_object_or_404(UserImage, id=user_image_id, user=request.user)
            
            collection_item, created = CollectionItem.objects.get_or_create(
                collection=collection,
                user_image=user_image,
                defaults={'notes': f'Added on {timezone.now().strftime("%B %d, %Y")}'}
            )
            
            if created:
                logger.info(f"Added user image {user_image_id} to collection {collection_id}")
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
def remove_image_from_collection(request, collection_id):
    """FIXED: Remove a specific processed image from a collection"""
    try:
        collection = get_object_or_404(Collection, id=collection_id, user=request.user)
        processed_image_id = request.POST.get('processed_image_id')
        user_image_id = request.POST.get('user_image_id')
        
        if processed_image_id:
            processed_image = get_object_or_404(
                ProcessedImage,
                id=processed_image_id,
                processing_job__user_image__user=request.user
            )
            
            collection_item = get_object_or_404(
                CollectionItem,
                collection=collection,
                processed_image=processed_image
            )
            
        elif user_image_id:
            user_image = get_object_or_404(UserImage, id=user_image_id, user=request.user)
            
            collection_item = get_object_or_404(
                CollectionItem,
                collection=collection,
                user_image=user_image
            )
        else:
            return JsonResponse({'success': False, 'message': 'No image specified'})
        
        collection_item.delete()
        
        logger.info(f"Removed image from collection {collection_id}")
        
        return JsonResponse({
            'success': True,
            'message': f'Removed from "{collection.name}"'
        })
        
    except Exception as e:
        logger.error(f"Error removing from collection: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error removing from collection'
        }, status=500)


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
            is_public=is_public,
            is_default=False
        )
        messages.success(request, f'Collection "{name}" created successfully!')
    except Exception as e:
        logger.error(f"Error creating collection: {str(e)}")
        messages.error(request, 'Error creating collection')
    
    return redirect('image_processing:collections_list')


@login_required
@require_POST
def create_collection_ajax(request):
    """FIXED: Create a new collection via AJAX with better validation"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        is_public = data.get('is_public', False)
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Collection name is required'})
        
        if len(name) > 100:
            return JsonResponse({'success': False, 'error': 'Collection name too long (max 100 characters)'})
        
        # Check if collection name already exists for this user
        if Collection.objects.filter(user=request.user, name=name).exists():
            return JsonResponse({'success': False, 'error': 'A collection with this name already exists'})
        
        collection = Collection.objects.create(
            user=request.user,
            name=name,
            description=description,
            is_public=is_public,
            is_default=False
        )
        
        logger.info(f"Created collection '{name}' for user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': f'Collection "{name}" created successfully!',
            'collection': {
                'id': collection.id,
                'name': collection.name,
                'description': collection.description,
                'is_public': collection.is_public,
                'is_default': collection.is_default,
                'item_count': 0,
                'created_at': collection.created_at.isoformat(),
                'updated_at': collection.updated_at.isoformat(),
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request data'})
    except Exception as e:
        logger.error(f"Error creating collection: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Error creating collection'})


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
@require_POST  
def edit_collection(request, collection_id):
    """Edit an existing collection"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    
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
@require_POST
def add_to_multiple_collections(request):
    """Add an image to multiple collections"""
    try:
        data = json.loads(request.body)
        collection_ids = data.get('collection_ids', [])
        processed_image_id = data.get('processed_image_id')
        user_image_id = data.get('user_image_id')
        
        if not collection_ids:
            return JsonResponse({'success': False, 'error': 'No collections specified'})
        
        # Get the image
        if processed_image_id:
            processed_image = get_object_or_404(
                ProcessedImage,
                id=processed_image_id,
                processing_job__user_image__user=request.user
            )
            image_obj = processed_image
            image_type = 'processed'
        elif user_image_id:
            user_image = get_object_or_404(UserImage, id=user_image_id, user=request.user)
            image_obj = user_image
            image_type = 'user'
        else:
            return JsonResponse({'success': False, 'error': 'No image specified'})
        
        added_count = 0
        collection_names = []
        
        for collection_id in collection_ids:
            try:
                # Only allow custom collections (no default)
                collection = get_object_or_404(
                    Collection, 
                    id=collection_id, 
                    user=request.user, 
                    is_default=False
                )
                
                if image_type == 'processed':
                    collection_item, created = CollectionItem.objects.get_or_create(
                        collection=collection,
                        processed_image=processed_image,
                        defaults={'notes': f'Added on {timezone.now().strftime("%B %d, %Y")}'}
                    )
                else:
                    collection_item, created = CollectionItem.objects.get_or_create(
                        collection=collection,
                        user_image=user_image,
                        defaults={'notes': f'Added on {timezone.now().strftime("%B %d, %Y")}'}
                    )
                
                if created:
                    added_count += 1
                    collection_names.append(collection.name)
                    
            except Exception as e:
                logger.warning(f"Error adding to collection {collection_id}: {str(e)}")
                continue
        
        if added_count > 0:
            if added_count == 1:
                message = f'Added to "{collection_names[0]}"'
            else:
                message = f'Added to {added_count} collections: {", ".join(collection_names)}'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'added_count': added_count
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Image was already in all selected collections'
            })
            
    except Exception as e:
        logger.error(f"Error adding to multiple collections: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Error adding to collections'})


