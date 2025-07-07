# image_processing/tasks.py - Fixed for proper function imports

import logging
from celery import shared_task
from django.utils import timezone
from .models import ImageProcessingJob, ProcessedImage
from .services import ImageProcessingService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_image_async(self, job_id):
    """
    Asynchronously process a wedding venue image with dynamic parameters
    """
    try:
        # Get the processing job
        job = ImageProcessingJob.objects.get(id=job_id)
        
        logger.info(f"Starting processing job {job_id} for user {job.user_image.user.username}")
        
        # Update job status
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        # Initialize the processing service
        processing_service = ImageProcessingService()
        
        # Ensure we have a generated prompt (with dynamic parameters)
        if not job.generated_prompt:
            logger.info(f"Generating transformation prompt for job {job_id}")
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
                
                # Update SD3 Turbo parameters
                recommended_params = prompt_data['recommended_params']
                job.aspect_ratio = recommended_params.get('aspect_ratio', job.aspect_ratio)
                job.strength = recommended_params.get('strength', job.strength)
                job.output_format = recommended_params.get('output_format', job.output_format)
                
                job.save()
                logger.info(f"Generated dynamic prompt for job {job_id}: {job.generated_prompt[:100]}...")
                
            except Exception as e:
                logger.error(f"Error generating transformation prompt for job {job_id}: {str(e)}")
                # Create a basic fallback prompt
                job.generated_prompt = f"Transform this space to become a beautiful {job.space_type} with {job.wedding_theme} wedding style, professional wedding photography, high quality, elegant transformation"
                job.negative_prompt = "people, faces, crowd, guests, blurry, low quality, dark, messy"
                job.save()
        
        prompt_text = job.generated_prompt
        logger.info(f"Processing wedding venue with SD3 Turbo using prompt: {prompt_text[:100]}...")
        
        # Log dynamic parameters being used
        dynamic_params = {
            'guest_count': job.guest_count,
            'budget_level': job.budget_level,
            'season': job.season,
            'time_of_day': job.time_of_day,
            'color_scheme': job.color_scheme,
            'custom_colors': job.custom_colors
        }
        used_params = {k: v for k, v in dynamic_params.items() if v}
        if used_params:
            logger.info(f"Using dynamic parameters: {used_params}")
        
        # Process the image using the service (SD3 Turbo)
        success = processing_service.process_wedding_image(job)
        
        if success:
            logger.info(f"Successfully completed wedding processing job {job_id} with SD3 Turbo")
            return {
                'success': True,
                'job_id': job_id,
                'theme': job.wedding_theme,
                'space_type': job.space_type,
                'dynamic_params': used_params
            }
        else:
            logger.error(f"Wedding processing failed for job {job_id}")
            return {
                'success': False,
                'job_id': job_id,
                'error': 'SD3 Turbo processing failed'
            }
            
    except ImageProcessingJob.DoesNotExist:
        logger.error(f"Wedding processing job {job_id} not found")
        return {
            'success': False,
            'error': f'Job {job_id} not found'
        }
        
    except Exception as exc:
        logger.error(f"Error processing wedding job {job_id}: {str(exc)}", exc_info=True)
        
        # Retry logic with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)  # 60s, 120s, 240s
            logger.info(f"Retrying wedding job {job_id} in {countdown} seconds (attempt {self.request.retries + 1})")
            raise self.retry(countdown=countdown, exc=exc)
        
        # Mark job as failed if all retries exhausted
        try:
            job = ImageProcessingJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_message = f"SD3 Turbo processing failed after {self.max_retries} retries: {str(exc)}"
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
def cleanup_temporary_images():
    """
    Clean up temporary (unsaved) processed images older than 48 hours
    """
    from datetime import timedelta
    import os
    from django.conf import settings
    
    cutoff_date = timezone.now() - timedelta(hours=48)
    
    temporary_images = ProcessedImage.objects.filter(
        is_saved=False,
        created_at__lt=cutoff_date
    )
    
    deleted_count = 0
    for processed_image in temporary_images:
        try:
            # Delete the image file
            if processed_image.processed_image:
                file_path = processed_image.processed_image.path
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted temporary wedding image: {file_path}")
            
            # Delete the database record
            processed_image.delete()
            deleted_count += 1
            
        except Exception as e:
            logger.error(f"Error deleting temporary image {processed_image.id}: {str(e)}")
    
    logger.info(f"Cleaned up {deleted_count} temporary wedding images")
    return deleted_count


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
    Generate a preview prompt for a wedding theme + space transformation with dynamic params
    """
    from .models import generate_wedding_prompt_with_dynamics
    
    prompt_data = generate_wedding_prompt_with_dynamics(
        wedding_theme=theme,
        space_type=space_type,
        **dynamic_params
    )
    
    logger.info(f"Generated transformation preview prompt for {theme} + {space_type} with dynamic params")
    
    return {
        'theme': theme,
        'space_type': space_type,
        'dynamic_params': dynamic_params,
        'prompt': prompt_data['prompt'],
        'negative_prompt': prompt_data['negative_prompt']
    }