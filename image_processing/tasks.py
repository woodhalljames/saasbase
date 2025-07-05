# image_processing/tasks.py - Updated to remove batch processing

import logging
from celery import shared_task
from django.utils import timezone
from django.core.files.base import ContentFile
from .models import ImageProcessingJob, ProcessedImage
from .services import ImageProcessingService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_image_async(self, job_id):
    """
    Asynchronously process a single wedding venue image with enhanced error handling
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
        from .services import ImageProcessingService
        processing_service = ImageProcessingService()
        
        # Ensure we have a generated prompt
        if not job.generated_prompt:
            logger.info(f"Generating prompt for job {job_id}")
            try:
                from .models import generate_wedding_prompt
                prompt_data = generate_wedding_prompt(job.wedding_theme, job.space_type, job.additional_details)
                job.generated_prompt = prompt_data['prompt']
                job.negative_prompt = prompt_data['negative_prompt']
                
                # Update parameters with recommendations
                recommended_params = prompt_data['recommended_params']
                job.cfg_scale = recommended_params.get('cfg_scale', job.cfg_scale)
                job.steps = recommended_params.get('steps', job.steps)
                job.aspect_ratio = recommended_params.get('aspect_ratio', job.aspect_ratio)
                job.strength = recommended_params.get('strength', job.strength)
                job.output_format = recommended_params.get('output_format', job.output_format)
                
                job.save()
                logger.info(f"Generated prompt for job {job_id}: {job.generated_prompt[:100]}...")
                
            except Exception as e:
                logger.error(f"Error generating prompt for job {job_id}: {str(e)}")
                # Create a basic fallback prompt
                job.generated_prompt = f"Transform this {job.space_type} into a beautiful {job.wedding_theme} wedding venue, professional wedding photography, high quality, elegant decoration"
                job.negative_prompt = "people, faces, crowd, guests, blurry, low quality, dark, messy"
                job.save()
        
        prompt_text = job.generated_prompt
        logger.info(f"Processing wedding venue with prompt: {prompt_text[:100]}...")
        
        # Process the image using the service
        success = processing_service.process_wedding_image(job)
        
        if success:
            logger.info(f"Successfully completed wedding processing job {job_id}")
            return {
                'success': True,
                'job_id': job_id,
                'theme': job.wedding_theme,
                'space': job.space_type
            }
        else:
            logger.error(f"Wedding processing failed for job {job_id}")
            return {
                'success': False,
                'job_id': job_id,
                'error': 'Processing failed'
            }
            
    except ImageProcessingJob.DoesNotExist:
        logger.error(f"Wedding processing job {job_id} not found")
        return {
            'success': False,
            'error': f'Job {job_id} not found'
        }
        
    except Exception as exc:
        logger.error(f"Error processing wedding job {job_id}: {str(exc)}", exc_info=True)
        
        # Retry logic
        if self.request.retries < self.max_retries:
            # Exponential backoff: 60s, 120s, 240s
            countdown = 60 * (2 ** self.request.retries)
            logger.info(f"Retrying wedding job {job_id} in {countdown} seconds (attempt {self.request.retries + 1})")
            raise self.retry(countdown=countdown, exc=exc)
        
        # Mark job as failed if all retries exhausted
        try:
            job = ImageProcessingJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_message = f"Processing failed after {self.max_retries} retries: {str(exc)}"
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
    Run this daily to keep storage manageable
    """
    from datetime import timedelta
    import os
    from django.conf import settings
    
    # Delete unsaved processed images older than 48 hours
    cutoff_date = timezone.now() - timedelta(hours=48)
    
    from .models import ProcessedImage
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
    These don't have processed images so just clean up the job records
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
def generate_wedding_preview(theme, space_type):
    """
    Generate a preview of what a wedding theme + space combination might look like
    This could be used for showing examples before processing
    """
    from .models import generate_wedding_prompt
    
    prompt_data = generate_wedding_prompt(theme, space_type)
    logger.info(f"Generated wedding preview prompt for {theme} + {space_type}")
    
    return {
        'theme': theme,
        'space_type': space_type,
        'prompt': prompt_data['prompt']
    }