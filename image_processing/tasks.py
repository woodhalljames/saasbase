import logging
from celery import shared_task
from django.utils import timezone
from .models import ImageProcessingJob, ProcessedImage
from .services import ImageProcessingService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_image_async(self, job_id):
    """
    Asynchronously process a wedding venue image with Stable Image Ultra and dynamic parameters
    """
    try:
        # Get the processing job
        job = ImageProcessingJob.objects.get(id=job_id)
        
        logger.info(f"Starting Stable Image Ultra processing job {job_id} for user {job.user_image.user.username}")
        
        # Update job status
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        # Initialize the processing service
        processing_service = ImageProcessingService()
        
        # Ensure we have a generated prompt (with dynamic parameters)
        if not job.generated_prompt:
            logger.info(f"Generating transformation prompt for Stable Image Ultra job {job_id}")
            try:
                # Import the function here to avoid circular imports
                from .models import generate_wedding_prompt_with_dynamics
                
                prompt_data = generate_wedding_prompt_with_dynamics(
                    wedding_theme=job.wedding_theme,
                    space_type=job.space_type,
                    guest_count=job.guest_count,
                    budget_level=job.budget_level,
                    season=job.season,
                    time_of_day=job.time_of_day,
                    color_scheme=job.color_scheme,
                    custom_colors=job.custom_colors,
                    additional_details=job.additional_details
                )
                
                job.generated_prompt = prompt_data['prompt']
                job.negative_prompt = prompt_data['negative_prompt']
                
                # Update Stable Image Ultra parameters with recommendations
                recommended_params = prompt_data['recommended_params']
                job.strength = recommended_params.get('strength', job.strength)
                job.cfg_scale = recommended_params.get('cfg_scale', job.cfg_scale)
                job.steps = recommended_params.get('steps', job.steps)
                job.output_format = recommended_params.get('output_format', job.output_format)
                
                job.save()
                logger.info(f"Generated concise prompt for Stable Image Ultra job {job_id}: {job.generated_prompt[:100]}...")
                
            except Exception as e:
                logger.error(f"Error generating transformation prompt for Ultra job {job_id}: {str(e)}")
                # Create a basic fallback prompt
                job.generated_prompt = f"Transform this space to become a beautiful {job.space_type} with {job.wedding_theme} wedding style, professional wedding photography, high quality, elegant transformation"
                job.negative_prompt = "people, faces, crowd, guests, blurry, low quality, dark, messy"
                job.save()
        
        prompt_text = job.generated_prompt
        logger.info(f"Processing wedding venue with Stable Image Ultra using prompt: {prompt_text[:100]}...")
        
        # Log dynamic parameters and Ultra settings being used
        dynamic_params = {
            'guest_count': job.guest_count,
            'budget_level': job.budget_level,
            'season': job.season,
            'time_of_day': job.time_of_day,
            'color_scheme': job.color_scheme,
            'custom_colors': job.custom_colors
        }
        ultra_params = {
            'cfg_scale': job.cfg_scale,
            'steps': job.steps,
            'strength': job.strength,
        }
        
        used_params = {k: v for k, v in dynamic_params.items() if v}
        if used_params:
            logger.info(f"Using dynamic parameters: {used_params}")
        logger.info(f"Using Stable Image Ultra parameters: {ultra_params}")
        
        # Process the image using the service (Stable Image Ultra)
        success = processing_service.process_wedding_image(job)
        
        if success:
            logger.info(f"Successfully completed wedding processing job {job_id} with Stable Image Ultra")
            return {
                'success': True,
                'job_id': job_id,
                'theme': job.wedding_theme,
                'space_type': job.space_type,
                'dynamic_params': used_params,
                'ultra_params': ultra_params,
                'model': 'Stable-Image-Ultra'
            }
        else:
            logger.error(f"Stable Image Ultra wedding processing failed for job {job_id}")
            return {
                'success': False,
                'job_id': job_id,
                'error': 'Stable Image Ultra processing failed'
            }
            
    except ImageProcessingJob.DoesNotExist:
        logger.error(f"Wedding processing job {job_id} not found")
        return {
            'success': False,
            'error': f'Job {job_id} not found'
        }
        
    except Exception as exc:
        logger.error(f"Error processing wedding job {job_id} with Stable Image Ultra: {str(exc)}", exc_info=True)
        
        # Retry logic with exponential backoff - Ultra is typically faster but still needs time for quality
        if self.request.retries < self.max_retries:
            countdown = 90 * (2 ** self.request.retries)  # 90s, 180s, 360s (adjusted for Ultra)
            logger.info(f"Retrying Stable Image Ultra wedding job {job_id} in {countdown} seconds (attempt {self.request.retries + 1})")
            raise self.retry(countdown=countdown, exc=exc)
        
        # Mark job as failed if all retries exhausted
        try:
            job = ImageProcessingJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_message = f"Stable Image Ultra processing failed after {self.max_retries} retries: {str(exc)}"
            job.completed_at = timezone.now()
            job.save()
            logger.error(f"Job {job_id} marked as failed after {self.max_retries} retries")
        except Exception as save_error:
            logger.error(f"Failed to update job status: {str(save_error)}")
        
        return {
            'success': False,
            'job_id': job_id,
            'error': str(exc)
        }


@shared_task
def cleanup_failed_jobs():
    """
    Clean up failed processing jobs older than 7 days
    """
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=7)
    
    failed_jobs = ImageProcessingJob.objects.filter(
        status='failed',
        created_at__lt=cutoff_date
    )
    
    deleted_count = failed_jobs.count()
    failed_jobs.delete()
    
    logger.info(f"Cleaned up {deleted_count} old failed job records")
    return deleted_count


@shared_task
def generate_wedding_preview(theme, space_type, **dynamic_params):
    """
    Generate a preview prompt for a wedding theme + space transformation with Stable Image Ultra dynamic params
    """
    from .models import generate_wedding_prompt_with_dynamics
    
    prompt_data = generate_wedding_prompt_with_dynamics(
        wedding_theme=theme,
        space_type=space_type,
        **dynamic_params
    )
    
    logger.info(f"Generated Stable Image Ultra transformation preview prompt for {theme} + {space_type} with dynamic params")
    
    return {
        'theme': theme,
        'space_type': space_type,
        'dynamic_params': dynamic_params,
        'prompt': prompt_data['prompt'],
        'negative_prompt': prompt_data['negative_prompt'],
        'recommended_params': prompt_data['recommended_params'],
        'model': 'Stable-Image-Ultra'
    }


@shared_task
def optimize_ultra_parameters(job_id):
    """
    Optimize Stable Image Ultra parameters based on theme and space type
    """
    try:
        job = ImageProcessingJob.objects.get(id=job_id)
        
        # Theme-specific optimizations for Stable Image Ultra
        optimizations = {
            'rustic': {'cfg_scale': 6.0, 'steps': 35, 'strength': 0.35},
            'modern': {'cfg_scale': 8.0, 'steps': 45, 'strength': 0.45},
            'vintage': {'cfg_scale': 7.5, 'steps': 40, 'strength': 0.4},
            'bohemian': {'cfg_scale': 6.5, 'steps': 35, 'strength': 0.35},
            'classic': {'cfg_scale': 8.0, 'steps': 45, 'strength': 0.4},
            'garden': {'cfg_scale': 6.0, 'steps': 35, 'strength': 0.35},
            'beach': {'cfg_scale': 6.5, 'steps': 40, 'strength': 0.4},
            'industrial': {'cfg_scale': 8.5, 'steps': 45, 'strength': 0.45},
            'indian_palace': {'cfg_scale': 7.5, 'steps': 40, 'strength': 0.4},
            'japanese_zen': {'cfg_scale': 6.0, 'steps': 35, 'strength': 0.35},
            'moroccan_nights': {'cfg_scale': 7.0, 'steps': 40, 'strength': 0.4},
        }
        
        # Space-specific adjustments
        space_adjustments = {
            'wedding_ceremony': {'strength': -0.05},  # Slightly less strength for ceremonies
            'dance_floor': {'cfg_scale': 1.0, 'strength': 0.05},  # More transformation for dance floors
            'dining_area': {'strength': 0.0},         # Neutral for dining
            'cocktail_hour': {'strength': 0.0},       # Neutral for social space
            'lounge_area': {'strength': -0.05},       # Gentler for intimate spaces
        }
        
        if job.wedding_theme in optimizations:
            opt = optimizations[job.wedding_theme]
            job.cfg_scale = opt.get('cfg_scale', job.cfg_scale)
            job.steps = opt.get('steps', job.steps)
            job.strength = opt.get('strength', job.strength)
        
        if job.space_type in space_adjustments:
            adj = space_adjustments[job.space_type]
            job.cfg_scale += adj.get('cfg_scale', 0)
            job.strength += adj.get('strength', 0)
        
        # Clamp values to valid ranges for Stable Image Ultra
        job.cfg_scale = max(1.0, min(20.0, job.cfg_scale))
        job.steps = max(10, min(50, job.steps))  # Ultra uses fewer steps
        job.strength = max(0.0, min(1.0, job.strength))
        
        job.save()
        
        logger.info(f"Optimized Stable Image Ultra parameters for job {job_id}: cfg_scale={job.cfg_scale}, steps={job.steps}, strength={job.strength}")
        
        return {
            'success': True,
            'job_id': job_id,
            'optimized_params': {
                'cfg_scale': job.cfg_scale,
                'steps': job.steps,
                'strength': job.strength
            }
        }
        
    except Exception as e:
        logger.error(f"Error optimizing Ultra parameters for job {job_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def cleanup_orphaned_images():
    """
    Clean up orphaned processed images (without processing jobs) older than 30 days
    This is a safety cleanup for any data integrity issues
    """
    from datetime import timedelta
    import os
    
    cutoff_date = timezone.now() - timedelta(days=30)
    
    # Find processed images without processing jobs
    orphaned_images = ProcessedImage.objects.filter(
        processing_job__isnull=True,
        created_at__lt=cutoff_date
    )
    
    deleted_count = 0
    for processed_image in orphaned_images:
        try:
            # Delete the image file
            if processed_image.processed_image:
                file_path = processed_image.processed_image.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted orphaned image file: {file_path}")
            
            # Delete the database record
            processed_image.delete()
            deleted_count += 1
            
        except Exception as e:
            logger.error(f"Error deleting orphaned image {processed_image.id}: {str(e)}")
    
    logger.info(f"Cleaned up {deleted_count} orphaned processed images")
    return deleted_count


@shared_task
def optimize_image_storage():
    """
    Optimize image storage by compressing old images and generating missing thumbnails
    """
    from .models import UserImage
    from PIL import Image as PILImage
    import io
    from django.core.files.base import ContentFile
    
    optimized_count = 0
    
    # Generate missing thumbnails for user images
    user_images_without_thumbnails = UserImage.objects.filter(thumbnail__isnull=True)
    
    for user_image in user_images_without_thumbnails[:50]:  # Process 50 at a time
        try:
            user_image.create_thumbnail()
            optimized_count += 1
            logger.info(f"Generated thumbnail for image: {user_image.original_filename}")
        except Exception as e:
            logger.error(f"Error generating thumbnail for {user_image.id}: {str(e)}")
    
    logger.info(f"Optimized {optimized_count} images")
    return optimized_count