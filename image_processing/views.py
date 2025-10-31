import json
import logging
import io
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
from django.core.files.base import ContentFile
from PIL import Image, ImageOps

from usage_limits.decorators import usage_limit_required
from .models import (
    UserImage, ImageProcessingJob, ProcessedImage, Collection, CollectionItem, 
    Favorite, FavoriteUpload, JobReferenceImage,
    WEDDING_THEMES, SPACE_TYPES, COLOR_SCHEMES,
    ENGAGEMENT_SETTINGS, ENGAGEMENT_ACTIVITIES,
    WEDDING_MOMENTS, WEDDING_SETTINGS, ATTIRE_STYLES,
    COMPOSITION_CHOICES, EMOTIONAL_TONE_CHOICES
)
from .forms import ImageUploadForm
from .tasks import process_image_job

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'webp']
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp']


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def apply_exif_correction(uploaded_file):
    """Apply EXIF orientation correction to uploaded image file"""
    try:
        image = Image.open(uploaded_file)
        
        if hasattr(image, '_getexif') and image._getexif() is not None:
            corrected_image = ImageOps.exif_transpose(image)
            
            if corrected_image is not image:
                logger.info(f"Applied EXIF orientation correction to {uploaded_file.name}")
                
                output = io.BytesIO()
                image_format = image.format or 'JPEG'
                
                if image_format.upper() == 'JPEG':
                    if corrected_image.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', corrected_image.size, (255, 255, 255))
                        if corrected_image.mode == 'P':
                            corrected_image = corrected_image.convert('RGBA')
                        background.paste(corrected_image, mask=corrected_image.split()[-1] if corrected_image.mode == 'RGBA' else None)
                        corrected_image = background
                    
                    corrected_image.save(output, format='JPEG', quality=95, optimize=True)
                else:
                    corrected_image.save(output, format=image_format)
                
                output.seek(0)
                corrected_file = ContentFile(output.getvalue(), name=uploaded_file.name)
                corrected_file.content_type = uploaded_file.content_type
                
                return corrected_file
            else:
                logger.info(f"No EXIF correction needed for {uploaded_file.name}")
                return uploaded_file
        else:
            logger.info(f"No EXIF data found in {uploaded_file.name}")
            return uploaded_file
            
    except Exception as e:
        logger.warning(f"Error applying EXIF correction to {uploaded_file.name}: {str(e)}")
        return uploaded_file


def validate_image_format(uploaded_file):
    """Validate image format - only JPG, PNG, WebP allowed"""
    file_ext = uploaded_file.name.lower().split('.')[-1]
    if file_ext not in ALLOWED_IMAGE_FORMATS:
        return False, f"Invalid format '.{file_ext}'. Please upload JPG, PNG, or WebP images only."
    
    if uploaded_file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid file type. Please upload JPG, PNG, or WebP images only."
    
    return True, None


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


def add_star_status_to_images(user, user_images):
    """Add is_starred attribute to user images efficiently"""
    if not user.is_authenticated:
        for img in user_images:
            img.is_starred = False
        return user_images
    
    starred_ids = set(
        FavoriteUpload.objects.filter(user=user)
        .values_list('image_id', flat=True)
    )
    
    for img in user_images:
        img.is_starred = img.id in starred_ids
    
    return user_images


def generate_prompt_for_job(studio_mode, **params):
    """
    Generate prompt BEFORE creating job.
    This is called in views, not in models.
    
    Args:
        studio_mode: 'venue', 'portrait_wedding', or 'portrait_engagement'
        **params: All other job parameters
        
    Returns:
        str: Generated prompt
    """
    try:
        if studio_mode == 'venue':
            from .prompt_generator import VenuePromptGenerator
            return VenuePromptGenerator.generate_prompt(
                wedding_theme=params.get('wedding_theme'),
                space_type=params.get('space_type'),
                season=params.get('season'),
                lighting_mood=params.get('lighting_mood'),
                color_scheme=params.get('color_scheme'),
                custom_prompt=params.get('custom_prompt'),
                user_instructions=params.get('user_instructions')
            )
        elif studio_mode in ['portrait_wedding', 'portrait_engagement']:
            from .prompt_generator import PortraitPromptGenerator
            return PortraitPromptGenerator.generate_prompt(
                studio_mode=studio_mode,
                # Engagement fields
                engagement_setting=params.get('engagement_setting'),
                engagement_activity=params.get('engagement_activity'),
                # Wedding fields
                wedding_moment=params.get('wedding_moment'),
                wedding_setting=params.get('wedding_setting'),
                # Shared fields
                attire_style=params.get('attire_style'),
                composition=params.get('composition'),
                emotional_tone=params.get('emotional_tone'),
                season=params.get('season'),
                lighting_mood=params.get('lighting_mood'),
                color_scheme=params.get('color_scheme'),
                custom_prompt=params.get('custom_prompt'),
                user_instructions=params.get('user_instructions')
            )
    except ImportError as e:
        logger.error(f"Could not import prompt generator: {e}")
        if params.get('custom_prompt'):
            return params['custom_prompt']
        return "Generate a beautiful image"


# ============================================================================
# MAIN VIEWS
# ============================================================================

@login_required
def wedding_studio(request):
    """Main wedding studio with multi-mode support (venue, wedding portrait, engagement portrait)"""
    
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                original_file = form.cleaned_data['image']
                corrected_file = apply_exif_correction(original_file)
                
                user_image = form.save(commit=False)
                user_image.user = request.user
                user_image.original_filename = original_file.name
                user_image.image = corrected_file
                
                if not user_image.image_type:
                    user_image.image_type = 'venue'
                
                user_image.save()
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': f'"{user_image.original_filename}" uploaded successfully!',
                        'image_id': user_image.id,
                        'image_url': user_image.image.url,
                        'thumbnail_url': user_image.thumbnail.url if user_image.thumbnail else user_image.image.url,
                        'image_name': user_image.original_filename,
                        'image_type': user_image.image_type,
                        'width': user_image.width,
                        'height': user_image.height,
                        'file_size': user_image.file_size,
                    })
                
                messages.success(request, f'"{user_image.original_filename}" uploaded successfully!')
                return redirect('image_processing:wedding_studio')
                
            except Exception as e:
                logger.error(f"Error uploading image: {str(e)}", exc_info=True)
                error_msg = f'Failed to upload image: {str(e)}'
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error_msg}, status=400)
                messages.error(request, error_msg)
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(str(error))
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': '; '.join(error_messages)}, status=400)
            
            for error in error_messages:
                messages.error(request, error)
    
    # GET request
    recent_images = UserImage.objects.filter(user=request.user).order_by('-uploaded_at')[:20]
    recent_images = add_star_status_to_images(request.user, list(recent_images))
    
    preselected_image = None
    image_id = request.GET.get('image_id')
    if image_id:
        try:
            preselected_image = UserImage.objects.get(id=image_id, user=request.user)
            logger.info(f"Preselected image: {preselected_image.original_filename}")
        except UserImage.DoesNotExist:
            logger.warning(f"Preselected image not found: {image_id}")
            messages.warning(request, "The selected image was not found.")
        except ValueError:
            logger.warning(f"Invalid image_id: {image_id}")
    
    from usage_limits.usage_tracker import UsageTracker
    usage_data = UsageTracker.get_usage_data(request.user)
    
    recent_jobs = ImageProcessingJob.objects.filter(
        user_image__user=request.user
    ).select_related('user_image').prefetch_related('processed_images').order_by('-created_at')[:5]
    
    favorite_ids = set(
        Favorite.objects.filter(user=request.user)
        .values_list('processed_image_id', flat=True)
    )
    
    for job in recent_jobs:
        for processed_image in job.processed_images.all():
            processed_image.is_favorited = processed_image.id in favorite_ids
    
    sorted_wedding_themes = sorted(WEDDING_THEMES, key=lambda x: x[1])
    sorted_color_schemes = sorted(COLOR_SCHEMES, key=lambda x: x[1])
    sorted_engagement_activities = sorted(ENGAGEMENT_ACTIVITIES, key=lambda x: x[1])
    sorted_engagement_settings = sorted(ENGAGEMENT_SETTINGS, key=lambda x: x[1])
    sorted_wedding_moments = sorted(WEDDING_MOMENTS, key=lambda x: x[1])
    sorted_wedding_settings = sorted(WEDDING_SETTINGS, key=lambda x: x[1])

    from .forms import SEASON_CHOICES, LIGHTING_CHOICES

    context = {
        'recent_images': recent_images,
        'preselected_image': preselected_image,
        'usage_data': usage_data,
        'recent_jobs': recent_jobs,
        'wedding_themes': sorted_wedding_themes,
        'space_types': SPACE_TYPES,
        'engagement_activities': sorted_engagement_activities,
        'engagement_settings': sorted_engagement_settings,
        'wedding_moments': sorted_wedding_moments,
        'wedding_settings': sorted_wedding_settings,
        'attire_styles': ATTIRE_STYLES,
        'composition_choices': COMPOSITION_CHOICES,
        'emotional_tone_choices': EMOTIONAL_TONE_CHOICES,
        'color_schemes': sorted_color_schemes,
        'season_choices': SEASON_CHOICES,
        'lighting_choices': LIGHTING_CHOICES,
        'upload_form': ImageUploadForm(),
        'gemini_model': 'gemini-2.5-flash-image-preview',
        'supports_custom_prompts': True,
        'processing_mode': 'real-time',
    }
    
    return render(request, 'image_processing/wedding_studio.html', context)

@login_required
@require_POST
def ajax_upload_image(request):
    """AJAX endpoint for image uploads with format validation and EXIF correction"""
    
    if 'image' in request.FILES:
        uploaded_file = request.FILES['image']
        is_valid, error_message = validate_image_format(uploaded_file)
        
        if not is_valid:
            logger.warning(f"Upload rejected - wrong format: {uploaded_file.name}")
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=400)
    
    mutable_post = request.POST.copy()
    
    if 'image_type' not in mutable_post or not mutable_post['image_type']:
        mutable_post['image_type'] = 'venue'
        logger.debug("Added default image_type='venue' for bulk upload")
    
    form = ImageUploadForm(mutable_post, request.FILES)
    
    if form.is_valid():
        try:
            original_file = form.cleaned_data['image']
            corrected_file = apply_exif_correction(original_file)
            
            user_image = form.save(commit=False)
            user_image.user = request.user
            user_image.original_filename = original_file.name
            user_image.image = corrected_file
            
            if not user_image.image_type:
                user_image.image_type = 'venue'
            
            user_image.save()
            
            logger.info(f"Image uploaded successfully: {user_image.original_filename} (type: {user_image.image_type}, size: {user_image.file_size} bytes)")
            
            return JsonResponse({
                'success': True,
                'image_id': user_image.id,
                'image_url': user_image.image.url,
                'thumbnail_url': user_image.thumbnail.url if user_image.thumbnail else user_image.image.url,
                'image_name': user_image.original_filename,
                'image_type': user_image.image_type,
                'width': user_image.width,
                'height': user_image.height,
                'file_size': user_image.file_size,
                'message': f'"{user_image.original_filename}" uploaded successfully!'
            })
            
        except Exception as e:
            logger.error(f"Error in AJAX upload: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'Upload failed: {str(e)}'
            }, status=500)
    
    errors = []
    for field, field_errors in form.errors.items():
        for error in field_errors:
            if field == '__all__':
                errors.append(str(error))
            else:
                errors.append(f"{field}: {error}")
    
    error_message = '; '.join(errors) if errors else 'Invalid upload data'
    logger.warning(f"Upload form validation failed: {error_message}")
    
    return JsonResponse({
        'success': False,
        'error': error_message
    }, status=400)


@login_required
@require_http_methods(["POST"])
def process_wedding_image(request, pk):
    """
    FIXED: Process image with multi-image support and 3 studio modes.
    Generate prompt BEFORE creating job.
    """
    try:
        user_image = get_object_or_404(UserImage, id=pk, user=request.user)
        
        from usage_limits.usage_tracker import UsageTracker
        usage_data = UsageTracker.get_usage_data(request.user)
        
        if usage_data['remaining'] <= 0:
            return JsonResponse({
                'success': False,
                'error': 'You have reached your monthly limit. Please upgrade your subscription.',
                'usage_data': usage_data,
                'needs_upgrade': True
            }, status=429)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid request data'
            }, status=400)
        
        studio_mode = data.get('studio_mode', 'venue')
        if studio_mode not in ['venue', 'portrait_wedding', 'portrait_engagement']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid studio mode'
            }, status=400)
        
        user_instructions = data.get('user_instructions', '').strip()
        custom_prompt = data.get('custom_prompt', '').strip()
        
        if custom_prompt and len(custom_prompt) < 10:
            return JsonResponse({
                'success': False,
                'error': 'Custom prompt is too short'
            }, status=400)
        
        # Collect all job parameters
        job_params = {
            'user_instructions': user_instructions if user_instructions else None,
            'custom_prompt': custom_prompt if custom_prompt else None
        }
        
        # Mode-specific validation and parameters
        if studio_mode == 'venue':
            wedding_theme = data.get('wedding_theme', '').strip()
            space_type = data.get('space_type', '').strip()
            
            if not custom_prompt and not wedding_theme:
                return JsonResponse({
                    'success': False,
                    'error': 'Wedding style is required for venue mode'
                }, status=400)
            
            job_params.update({
                'wedding_theme': wedding_theme,
                'space_type': space_type if space_type else '',
            })
            
        elif studio_mode == 'portrait_engagement':
            # Engagement portrait mode
            engagement_setting = data.get('engagement_setting', '').strip()
            engagement_activity = data.get('engagement_activity', '').strip()
            
            if not custom_prompt and not engagement_activity:
                return JsonResponse({
                    'success': False,
                    'error': 'Activity/pose is required for engagement mode'
                }, status=400)
            
            job_params.update({
                'engagement_setting': engagement_setting if engagement_setting else '',
                'engagement_activity': engagement_activity,
                'attire_style': data.get('attire_style', ''),
                'composition': data.get('composition', ''),
                'emotional_tone': data.get('emotional_tone', ''),
            })
            
        elif studio_mode == 'portrait_wedding':
            # Wedding portrait mode
            wedding_setting = data.get('wedding_setting', '').strip()
            wedding_moment = data.get('wedding_moment', '').strip()
            
            if not custom_prompt and not wedding_moment:
                return JsonResponse({
                    'success': False,
                    'error': 'Moment/scene is required for wedding portrait mode'
                }, status=400)
            
            job_params.update({
                'wedding_setting': wedding_setting if wedding_setting else '',
                'wedding_moment': wedding_moment,
                'attire_style': data.get('attire_style', ''),
                'composition': data.get('composition', ''),
                'emotional_tone': data.get('emotional_tone', ''),
            })
        
        # Optional fields
        optional_fields = ['season', 'lighting_mood', 'color_scheme']
        for field in optional_fields:
            value = data.get(field, '').strip()
            if value:
                job_params[field] = value
        
        # Get reference image IDs - Max 2 additional images (3 total including primary)
        reference_image_ids = data.get('reference_image_ids', [])
        if reference_image_ids and isinstance(reference_image_ids, list):
            # Enforce max 3 images total (primary + up to 2 references)
            reference_image_ids = reference_image_ids[:2]
        else:
            reference_image_ids = []
        
        # Calculate total image count
        total_image_count = 1 + len(reference_image_ids)
        
        # Validate max 3 images
        if total_image_count > 3:
            return JsonResponse({
                'success': False,
                'error': 'Maximum 3 images allowed per transformation'
            }, status=400)
        
        # CRITICAL: Generate prompt BEFORE creating job
        generated_prompt = generate_prompt_for_job(
            studio_mode=studio_mode,
            **job_params
        )
        
        logger.info(f"Generated prompt for {studio_mode} with {total_image_count} images, length: {len(generated_prompt)} chars")
        
        # Now create job with pre-generated prompt
        with transaction.atomic():
            job = ImageProcessingJob.objects.create(
                user_image=user_image,
                studio_mode=studio_mode,
                generated_prompt=generated_prompt,  # Already generated!
                **job_params
            )
            
            # Attach reference images
            for order, ref_id in enumerate(reference_image_ids):
                try:
                    ref_image = UserImage.objects.get(id=ref_id, user=request.user)
                    JobReferenceImage.objects.create(
                        job=job,
                        reference_image=ref_image,
                        order=order
                    )
                    logger.info(f"Added reference image {ref_id} to job {job.id}")
                except UserImage.DoesNotExist:
                    logger.warning(f"Reference image {ref_id} not found")
                    continue
            
            logger.info(f"Created {studio_mode} job {job.id} with prompt pre-generated, {len(reference_image_ids)} reference images")
        
        # Queue the task
        def queue_transformation():
            task_result = process_image_job.apply_async(args=[job.id])
            logger.info(f"Task queued: {task_result.id} for job {job.id}")
            return task_result
        
        transaction.on_commit(queue_transformation)
        
        return JsonResponse({
            'success': True,
            'job_id': job.id,
            'status': 'pending',
            'message': f'{job.mode_display} started!',
            'processing_mode': 'async',
            'job_details': {
                'mode': studio_mode,
                'model': 'gemini-2.5-flash-image-preview',
                'image_count': total_image_count,
                'has_user_instructions': bool(user_instructions),
                'prompt_length': len(generated_prompt)
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
    """Get real-time status of a job"""
    try:
        job = get_object_or_404(ImageProcessingJob, id=job_id, user_image__user=request.user)
        
        data = {
            'job_id': job.id,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'model': 'gemini-2.5-flash-image-preview',
            'mode': job.studio_mode,
            'has_user_instructions': bool(job.user_instructions)
        }
        
        if job.custom_prompt:
            data['custom_prompt'] = job.custom_prompt
            data['prompt_preview'] = job.custom_prompt[:100] + ('...' if len(job.custom_prompt) > 100 else '')
        else:
            if job.studio_mode == 'venue':
                data['wedding_theme'] = job.wedding_theme
                data['space_type'] = job.space_type
                if job.wedding_theme:
                    data['theme_display'] = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme)
                if job.space_type:
                    data['space_display'] = dict(SPACE_TYPES).get(job.space_type, job.space_type)
            elif job.studio_mode == 'portrait_engagement':
                # Engagement portrait mode
                data['engagement_activity'] = job.engagement_activity
                data['engagement_setting'] = job.engagement_setting
                if job.engagement_activity:
                    data['activity_display'] = dict(ENGAGEMENT_ACTIVITIES).get(job.engagement_activity, job.engagement_activity)
                if job.engagement_setting:
                    data['setting_display'] = dict(ENGAGEMENT_SETTINGS).get(job.engagement_setting, job.engagement_setting)
            elif job.studio_mode == 'portrait_wedding':
                # Wedding portrait mode
                data['wedding_moment'] = job.wedding_moment
                data['wedding_setting'] = job.wedding_setting
                if job.wedding_moment:
                    data['moment_display'] = dict(WEDDING_MOMENTS).get(job.wedding_moment, job.wedding_moment)
                if job.wedding_setting:
                    data['setting_display'] = dict(WEDDING_SETTINGS).get(job.wedding_setting, job.wedding_setting)
            
            if job.season:
                data['season'] = job.season
            if job.lighting_mood:
                data['lighting'] = job.lighting_mood
            if job.color_scheme:
                data['color_scheme'] = job.color_scheme
        
        if job.user_instructions:
            data['user_instructions'] = job.user_instructions
        
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


# ============================================================================
# FAVORITE UPLOAD VIEWS (STAR SYSTEM)
# ============================================================================

@login_required
@require_POST
def toggle_favorite_upload(request):
    """Toggle favorite status for uploaded images (star icon)"""
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        
        if not image_id:
            return JsonResponse({'success': False, 'error': 'No image specified'}, status=400)
        
        user_image = get_object_or_404(UserImage, id=image_id, user=request.user)
        
        favorite, created = FavoriteUpload.objects.get_or_create(
            user=request.user,
            image=user_image
        )
        
        if not created:
            # Already favorited - remove it
            favorite.delete()
            is_favorited = False
            message = 'Removed from quick access'
            logger.info(f"User {request.user.username} removed star from image {image_id}")
        else:
            # Newly favorited
            is_favorited = True
            message = 'Added to quick access'
            logger.info(f"User {request.user.username} starred image {image_id}")
        
        return JsonResponse({
            'success': True,
            'is_favorited': is_favorited,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Error toggling favorite upload: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Error updating favorite'}, status=500)


@login_required
def get_favorite_uploads(request):
    """Get user's favorite uploads for quick access"""
    try:
        favorites = FavoriteUpload.objects.filter(
            user=request.user
        ).select_related('image').order_by('-last_used', '-created_at')[:20]
        
        favorites_data = []
        for fav in favorites:
            favorites_data.append({
                'id': fav.id,
                'image': {
                    'id': fav.image.id,
                    'name': fav.image.original_filename,
                    'url': fav.image.image.url,
                    'thumbnail_url': fav.image.thumbnail.url if fav.image.thumbnail else fav.image.image.url,
                },
                # REMOVED: 'label' field - doesn't exist in model
                'times_used': fav.times_used,
                'created_at': fav.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'favorites': favorites_data
        })
        
    except Exception as e:
        logger.error(f"Error getting favorite uploads: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Error loading favorites'}, status=500)



@login_required
@require_POST
def remove_favorite_upload(request, favorite_id):
    """Remove a favorite upload"""
    try:
        favorite = get_object_or_404(FavoriteUpload, id=favorite_id, user=request.user)
        favorite.delete()
        
        logger.info(f"Removed favorite upload {favorite_id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Removed from favorites'
        })
        
    except Exception as e:
        logger.error(f"Error removing favorite: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Error removing favorite'}, status=500)


# ============================================================================
# FAVORITE VIEWS (HEART SYSTEM)
# ============================================================================

@login_required
@require_POST
def toggle_favorite(request):
    """Toggle favorite status for processed images (heart icon)"""
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
            logger.info(f"User {request.user.username} removed heart from processed image {processed_image_id}")
        else:
            is_favorited = True
            message = 'Added to favorites'
            logger.info(f"User {request.user.username} hearted processed image {processed_image_id}")
        
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
    """
    List user's favorites - TWO TABS:
    1. Favorite Uploads (⭐ star) - Quick Access for uploaded images
    2. Favorite Processed (❤️ heart) - Hearted AI transformations
    """
    
    # Get favorite uploads (starred uploaded images)
    favorite_uploads = FavoriteUpload.objects.filter(
        user=request.user
    ).select_related('image').order_by('-last_used', '-created_at')
    
    # Add is_starred flag to uploaded images
    for fav in favorite_uploads:
        fav.image.is_starred = True
    
    # Get favorite processed images (hearted transformations)
    favorite_processed = Favorite.objects.filter(
        user=request.user
    ).select_related(
        'processed_image__processing_job__user_image'
    ).order_by('-created_at')
    
    # Add display names for processed images
    for favorite in favorite_processed:
        job = favorite.processed_image.processing_job
        
        if job.custom_prompt:
            job.theme_display = "Custom Design"
            job.space_display = "Custom"
        elif job.studio_mode == 'venue':
            job.theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, '') if job.wedding_theme else ''
            job.space_display = dict(SPACE_TYPES).get(job.space_type, '') if job.space_type else ''
        elif job.studio_mode == 'portrait_engagement':
            # Engagement portrait mode
            job.theme_display = dict(ENGAGEMENT_ACTIVITIES).get(job.engagement_activity, '') if job.engagement_activity else ''
            job.space_display = dict(ENGAGEMENT_SETTINGS).get(job.engagement_setting, '') if job.engagement_setting else ''
        elif job.studio_mode == 'portrait_wedding':
            # Wedding portrait mode
            job.theme_display = dict(WEDDING_MOMENTS).get(job.wedding_moment, '') if job.wedding_moment else ''
            job.space_display = dict(WEDDING_SETTINGS).get(job.wedding_setting, '') if job.wedding_setting else ''
        
        # Mark as favorited
        favorite.processed_image.is_favorited = True
    
    context = {
        'favorite_uploads': favorite_uploads,
        'favorite_processed': favorite_processed,
        'total_uploads': favorite_uploads.count(),
        'total_processed': favorite_processed.count(),
    }
    
    return render(request, 'image_processing/favorites_list.html', context)

# ============================================================================
# IMAGE MANAGEMENT VIEWS
# ============================================================================

@login_required
def redo_transformation_with_job(request, job_id):
    """Redirect to wedding studio with job_id parameter to restore all settings and images"""
    job = get_object_or_404(ImageProcessingJob, id=job_id, user_image__user=request.user)
    
    # Simple redirect with just the job_id - studio will fetch details via AJAX
    base_url = reverse('image_processing:wedding_studio')
    redirect_url = f"{base_url}?job_id={job_id}"
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'redirect_url': redirect_url,
            'message': 'Redirecting to studio with saved settings...'
        })
    
    return redirect(redirect_url)


@login_required
def get_job_details(request, job_id):
    """API endpoint to get job details including all images and settings"""
    try:
        job = get_object_or_404(ImageProcessingJob, id=job_id, user_image__user=request.user)
        
        # Get all images used in this job with full data
        available_images = []
        missing_images = []
        
        # Try to add primary image with full data
        if job.user_image:
            try:
                if job.user_image.image:
                    available_images.append({
                        'id': job.user_image.id,
                        'name': job.user_image.original_filename,
                        'url': job.user_image.image.url,
                        'thumbnailUrl': job.user_image.thumbnail.url if job.user_image.thumbnail else job.user_image.image.url,
                        'width': job.user_image.width,
                        'height': job.user_image.height,
                        'file_size': job.user_image.file_size,
                        'image_type': job.user_image.image_type,
                    })
            except Exception as e:
                missing_images.append('primary')
                logger.warning(f"Primary image for job {job_id} is missing: {str(e)}")
        else:
            missing_images.append('primary')
            logger.warning(f"Primary image for job {job_id} is None")
        
        # Try to add reference images with full data
        reference_images = JobReferenceImage.objects.filter(
            job=job,
            reference_image__isnull=False
        ).select_related('reference_image').order_by('order')
        
        for ref in reference_images:
            try:
                if ref.reference_image and ref.reference_image.image:
                    available_images.append({
                        'id': ref.reference_image.id,
                        'name': ref.reference_image.original_filename,
                        'url': ref.reference_image.image.url,
                        'thumbnailUrl': ref.reference_image.thumbnail.url if ref.reference_image.thumbnail else ref.reference_image.image.url,
                        'width': ref.reference_image.width,
                        'height': ref.reference_image.height,
                        'file_size': ref.reference_image.file_size,
                        'image_type': ref.reference_image.image_type,
                    })
            except Exception as e:
                missing_images.append(f'reference_{ref.order}')
                logger.warning(f"Reference image {ref.order} for job {job_id} error: {str(e)}")
        
        # Count null reference images (deleted)
        null_references_count = JobReferenceImage.objects.filter(
            job=job,
            reference_image__isnull=True
        ).count()
        
        if null_references_count > 0:
            for i in range(null_references_count):
                missing_images.append(f'reference_deleted_{i}')
        
        # Build settings object
        settings_data = {
            'studio_mode': job.studio_mode,
        }
        
        # Add custom prompt if exists
        if job.custom_prompt:
            settings_data['custom_prompt'] = job.custom_prompt
        else:
            # Venue mode settings
            if job.wedding_theme:
                settings_data['wedding_theme'] = job.wedding_theme
            if job.space_type:
                settings_data['space_type'] = job.space_type
            
            # Engagement portrait settings
            if job.engagement_setting:
                settings_data['engagement_setting'] = job.engagement_setting
            if job.engagement_activity:
                settings_data['engagement_activity'] = job.engagement_activity
            
            # Wedding portrait settings
            if job.wedding_moment:
                settings_data['wedding_moment'] = job.wedding_moment
            if job.wedding_setting:
                settings_data['wedding_setting'] = job.wedding_setting
            
            # Shared portrait settings
            if job.attire_style:
                settings_data['attire_style'] = job.attire_style
            if job.composition:
                settings_data['composition'] = job.composition
            if job.emotional_tone:
                settings_data['emotional_tone'] = job.emotional_tone
            
            # Shared optional settings
            if job.season:
                settings_data['season'] = job.season
            if job.lighting_mood:
                settings_data['lighting_mood'] = job.lighting_mood
            if job.color_scheme:
                settings_data['color_scheme'] = job.color_scheme
        
        if job.user_instructions:
            settings_data['user_instructions'] = job.user_instructions
        
        # Prepare response with warning if images are missing
        response_data = {
            'success': True,
            'job_id': job.id,
            'images': available_images,  # Full image data, not just IDs
            'settings': settings_data,
            'images_available': len(available_images),
            'images_missing': len(missing_images)
        }
        
        # Add warning message if some images are missing
        if missing_images:
            total_images = len(available_images) + len(missing_images)
            if len(available_images) == 0:
                response_data['warning'] = f"All {total_images} images from this job have been deleted. Settings restored, but please select new images."
            else:
                response_data['warning'] = f"{len(missing_images)} of {total_images} images have been deleted. Settings restored with {len(available_images)} available image(s)."
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching job details: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to load job details'
        }, status=500)

@login_required
def processing_history(request):
    """
    FIXED: View all processing jobs - removed .theme_display_name references
    """
    jobs = ImageProcessingJob.objects.filter(
        user_image__user=request.user
    ).select_related('user_image').prefetch_related(
        'processed_images',
        'reference_images__reference_image'  # Prefetch reference images to avoid N+1 queries
    ).order_by('-created_at')
    
    favorite_ids = set(
        Favorite.objects.filter(user=request.user)
        .values_list('processed_image_id', flat=True)
    )
    
    for job in jobs:
        # FIXED: Build display names manually, don't use .theme_display_name
        if job.custom_prompt:
            job.mode_display_text = 'Custom Prompt'
            job.prompt_preview = job.custom_prompt[:100] + ('...' if len(job.custom_prompt) > 100 else '')
        elif job.studio_mode == 'venue':
            job.mode_display_text = 'Venue Design'
            # Build theme display manually - don't show if not set
            job.theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, '') if job.wedding_theme else ''
            job.space_display = dict(SPACE_TYPES).get(job.space_type, '') if job.space_type else ''
        elif job.studio_mode == 'portrait_engagement':
            # Engagement portrait mode
            job.mode_display_text = 'Engagement Portrait'
            job.theme_display = dict(ENGAGEMENT_ACTIVITIES).get(job.engagement_activity, '') if job.engagement_activity else ''
            job.space_display = dict(ENGAGEMENT_SETTINGS).get(job.engagement_setting, '') if job.engagement_setting else ''
        elif job.studio_mode == 'portrait_wedding':
            # Wedding portrait mode
            job.mode_display_text = 'Wedding Portrait'
            job.theme_display = dict(WEDDING_MOMENTS).get(job.wedding_moment, '') if job.wedding_moment else ''
            job.space_display = dict(WEDDING_SETTINGS).get(job.wedding_setting, '') if job.wedding_setting else ''
        
        # Add favorite status
        for processed_image in job.processed_images.all():
            processed_image.is_favorited = processed_image.id in favorite_ids
    
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'gemini_model': 'gemini-2.5-flash-image-preview',
    }
    
    return render(request, 'image_processing/processing_history.html', context)


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
def image_detail(request, pk):
    """View details of a user's image"""
    image = get_object_or_404(UserImage, id=pk, user=request.user)
    jobs = image.processing_jobs.all().order_by('-created_at')
    
    # Add star status
    image.is_starred = FavoriteUpload.objects.filter(
        user=request.user,
        image=image
    ).exists()
    
    context = {
        'image': image,
        'jobs': jobs,
    }
    
    return render(request, 'image_processing/image_detail.html', context)


@login_required
def image_gallery(request):
    """View all user uploaded images"""
    images_list = UserImage.objects.filter(user=request.user).order_by('-uploaded_at')
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        images_list = images_list.filter(
            Q(original_filename__icontains=search_query) |
            Q(venue_name__icontains=search_query) |
            Q(venue_description__icontains=search_query)
        )
    
    date_filter = request.GET.get('date_filter', '')
    if date_filter == 'today':
        today = timezone.now().date()
        images_list = images_list.filter(uploaded_at__date=today)
    elif date_filter == 'week':
        from datetime import timedelta
        week_ago = timezone.now().date() - timedelta(days=7)
        images_list = images_list.filter(uploaded_at__date__gte=week_ago)
    elif date_filter == 'month':
        from datetime import timedelta
        month_ago = timezone.now().date() - timedelta(days=30)
        images_list = images_list.filter(uploaded_at__date__gte=month_ago)
    
    paginator = Paginator(images_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add star status to images in page
    page_obj.object_list = add_star_status_to_images(request.user, list(page_obj.object_list))
    
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
def processed_image_detail(request, pk):
    """View details of a processed image"""
    processed_image = get_object_or_404(
        ProcessedImage, 
        id=pk, 
        processing_job__user_image__user=request.user
    )
    
    is_favorited = Favorite.objects.filter(
        user=request.user,
        processed_image=processed_image
    ).exists()
    
    processed_image.is_favorited = is_favorited
    
    job = processed_image.processing_job
    
    # Set display values, but don't show "Unknown"
    if job.custom_prompt:
        theme_display = "Custom Design"
        space_display = "Custom"
    elif job.studio_mode == 'venue':
        theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, '') if job.wedding_theme else ''
        space_display = dict(SPACE_TYPES).get(job.space_type, '') if job.space_type else ''
    elif job.studio_mode == 'portrait_engagement':
        theme_display = dict(ENGAGEMENT_ACTIVITIES).get(job.engagement_activity, '') if job.engagement_activity else ''
        space_display = dict(ENGAGEMENT_SETTINGS).get(job.engagement_setting, '') if job.engagement_setting else ''
    elif job.studio_mode == 'portrait_wedding':
        theme_display = dict(WEDDING_MOMENTS).get(job.wedding_moment, '') if job.wedding_moment else ''
        space_display = dict(WEDDING_SETTINGS).get(job.wedding_setting, '') if job.wedding_setting else ''
    else:
        theme_display = ''
        space_display = ''
    
    context = {
        'processed_image': processed_image,
        'job': job,
        'original_image': job.user_image,
        'theme_display': theme_display,
        'space_display': space_display,
    }
    
    return render(request, 'image_processing/processed_image_detail.html', context)


# ============================================================================
# COLLECTION MANAGEMENT VIEWS
# ============================================================================

@login_required
def collections_list(request):
    """List user's collections"""
    collections = Collection.objects.filter(user=request.user).order_by('-updated_at')
    
    context = {
        'collections': collections,
        'total_collections': collections.count(),
    }
    
    return render(request, 'image_processing/collections_list.html', context)


@login_required
def collection_detail(request, collection_id):
    """View details of a collection"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    
    items = collection.items.select_related(
        'user_image', 'processed_image__processing_job'
    ).order_by('order', '-added_at')
    
    favorite_ids = set(
        Favorite.objects.filter(user=request.user)
        .values_list('processed_image_id', flat=True)
    )
    
    # Add display properties to items
    for item in items:
        # Set image URL
        if item.processed_image:
            item.image_url = item.processed_image.processed_image.url
            item.image_title = f"{item.processed_image.processing_job.mode_display}"
            item.processed_image.is_favorited = item.processed_image.id in favorite_ids
            
            # Add theme and space display names
            job = item.processed_image.processing_job
            if job.wedding_theme:
                item.theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme)
            if job.space_type:
                item.space_display = dict(SPACE_TYPES).get(job.space_type, job.space_type)
        elif item.user_image:
            item.image_url = item.user_image.thumbnail.url if item.user_image.thumbnail else item.user_image.image.url
            item.image_title = item.user_image.original_filename
    
    context = {
        'collection': collection,
        'items': items,
        'total_items': items.count(),
    }
    
    return render(request, 'image_processing/collection_detail.html', context)


@login_required
@require_POST
def create_collection_ajax(request):
    """AJAX endpoint to create a new collection"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return JsonResponse({
                'success': False,
                'error': 'Collection name is required'
            }, status=400)
        
        if Collection.objects.filter(user=request.user, name=name).exists():
            return JsonResponse({
                'success': False,
                'error': 'A collection with this name already exists'
            }, status=400)
        
        collection = Collection.objects.create(
            user=request.user,
            name=name,
            description=description,
            is_public=True
        )
        
        logger.info(f"Created collection '{name}' for user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'collection': {
                'id': collection.id,
                'name': collection.name,
                'description': collection.description,
                'is_public': True,
                'item_count': 0,
                'created_at': collection.created_at.isoformat()
            },
            'message': f'Collection "{name}" created successfully!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error creating collection: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Failed to create collection'
        }, status=500)


@login_required
@require_POST
def add_to_collection(request):
    """Add an image to a collection"""
    collection_id = request.POST.get('collection_id')
    processed_image_id = request.POST.get('processed_image_id')
    user_image_id = request.POST.get('user_image_id')
    
    if not collection_id:
        return JsonResponse({'success': False, 'error': 'No collection specified'})
    
    if not processed_image_id and not user_image_id:
        return JsonResponse({'success': False, 'error': 'No image specified'})
    
    try:
        collection = get_object_or_404(Collection, id=collection_id, user=request.user)
        
        if processed_image_id:
            processed_image = get_object_or_404(
                ProcessedImage,
                id=processed_image_id,
                processing_job__user_image__user=request.user
            )
            
            item, created = CollectionItem.objects.get_or_create(
                collection=collection,
                processed_image=processed_image,
                defaults={'order': collection.items.count()}
            )
        else:
            user_image = get_object_or_404(UserImage, id=user_image_id, user=request.user)
            
            item, created = CollectionItem.objects.get_or_create(
                collection=collection,
                user_image=user_image,
                defaults={'order': collection.items.count()}
            )
        
        if created:
            collection.updated_at = timezone.now()
            collection.save(update_fields=['updated_at'])
            
            logger.info(f"Added image to collection '{collection.name}'")
            
            return JsonResponse({
                'success': True,
                'message': f'Added to "{collection.name}"'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Already in "{collection.name}"'
            })
        
    except Exception as e:
        logger.error(f"Error adding to collection: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Error adding to collection'})


@login_required
@require_POST
def remove_from_collection(request, collection_id, item_id):
    """Remove an item from a collection by item ID"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    collection_item = get_object_or_404(CollectionItem, id=item_id, collection=collection)
    
    try:
        collection_item.delete()
        
        collection.updated_at = timezone.now()
        collection.save(update_fields=['updated_at'])
        
        logger.info(f"Removed item {item_id} from collection '{collection.name}'")
        
        return JsonResponse({
            'success': True,
            'message': f'Removed from "{collection.name}"'
        })
        
    except Exception as e:
        logger.error(f"Error removing from collection: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Error removing from collection'})


@login_required
@require_POST
def remove_image_from_collection(request, collection_id):
    """Remove an image from a collection by image ID"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    
    processed_image_id = request.POST.get('processed_image_id')
    user_image_id = request.POST.get('user_image_id')
    
    if not processed_image_id and not user_image_id:
        return JsonResponse({'success': False, 'error': 'No image specified'})
    
    try:
        if processed_image_id:
            item = get_object_or_404(
                CollectionItem,
                collection=collection,
                processed_image_id=processed_image_id
            )
        else:
            item = get_object_or_404(
                CollectionItem,
                collection=collection,
                user_image_id=user_image_id
            )
        
        item.delete()
        
        collection.updated_at = timezone.now()
        collection.save(update_fields=['updated_at'])
        
        return JsonResponse({
            'success': True,
            'message': f'Removed from "{collection.name}"'
        })
        
    except Exception as e:
        logger.error(f"Error removing from collection: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Error removing from collection'})


@login_required
def get_user_collections(request):
    """API endpoint to get user's collections"""
    try:
        collections = Collection.objects.filter(user=request.user).order_by('-updated_at')
        
        collections_data = []
        for collection in collections:
            collections_data.append({
                'id': collection.id,
                'name': collection.name,
                'description': collection.description,
                'is_public': collection.is_public,
                'is_default': collection.is_default,
                'item_count': collection.item_count,
                'created_at': collection.created_at.isoformat(),
                'updated_at': collection.updated_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'collections': collections_data
        })
        
    except Exception as e:
        logger.error(f"Error getting collections: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to load collections'
        }, status=500)


@login_required
def get_processed_image_collections(request, processed_image_id):
    """Get collections that contain a specific processed image"""
    try:
        processed_image = get_object_or_404(
            ProcessedImage,
            id=processed_image_id,
            processing_job__user_image__user=request.user
        )
        
        collection_ids = list(
            CollectionItem.objects.filter(
                processed_image=processed_image
            ).values_list('collection_id', flat=True)
        )
        
        return JsonResponse({
            'success': True,
            'collection_ids': collection_ids
        })
        
    except Exception as e:
        logger.error(f"Error getting image collections: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error loading collections'
        }, status=500)


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
                collection = get_object_or_404(Collection, id=collection_id, user=request.user)
                
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
                message = f'Added to {added_count} collections'
            
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


@login_required
@require_POST
def create_collection(request):
    """Create a new collection"""
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    
    if not name:
        messages.error(request, 'Collection name is required')
        return redirect('image_processing:collections_list')
    
    try:
        collection = Collection.objects.create(
            user=request.user,
            name=name,
            description=description,
            is_public=True
        )
        messages.success(request, f'Collection "{name}" created successfully!')
    except Exception as e:
        logger.error(f"Error creating collection: {str(e)}")
        messages.error(request, 'Error creating collection')
    
    return redirect('image_processing:collections_list')


@login_required
@require_POST
def edit_collection(request, collection_id):
    """Edit an existing collection"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    
    if not name:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Collection name is required'
            }, status=400)
        
        messages.error(request, 'Collection name is required')
        return redirect('image_processing:collection_detail', collection_id=collection_id)
    
    try:
        collection.name = name
        collection.description = description
        collection.is_public = True
        collection.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Collection "{name}" updated successfully!'
            })
        
        messages.success(request, f'Collection "{name}" updated successfully!')
        return redirect('image_processing:collection_detail', collection_id=collection_id)
        
    except Exception as e:
        logger.error(f"Error updating collection: {str(e)}")
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Error updating collection'
            }, status=500)
        
        messages.error(request, 'Error updating collection')
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
def delete_processed_image(request, pk):
    """Delete a processed image"""
    try:
        processed_image = get_object_or_404(
            ProcessedImage,
            id=pk,
            processing_job__user_image__user=request.user
        )
        
        CollectionItem.objects.filter(processed_image=processed_image).delete()
        Favorite.objects.filter(processed_image=processed_image).delete()
        
        if processed_image.processed_image:
            try:
                processed_image.processed_image.delete(save=False)
            except Exception as e:
                logger.warning(f"Could not delete image file: {str(e)}")
        
        processed_image.delete()
        
        logger.info(f"Deleted processed image {pk}")
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Image deleted successfully'
            })
        
        messages.success(request, 'Image deleted successfully')
        return redirect('image_processing:processing_history')
        
    except Exception as e:
        logger.error(f"Error deleting processed image: {str(e)}")
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Failed to delete image'
            }, status=500)
        
        messages.error(request, 'Failed to delete image')
        return redirect('image_processing:processing_history')


# ============================================================================
# UTILITY / TEST VIEWS
# ============================================================================

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