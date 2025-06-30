# image_processing/tasks.py - Updated for wedding venue processing

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
    Asynchronously process a wedding venue image with generated prompt
    """
    try:
        # Get the processing job
        job = ImageProcessingJob.objects.get(id=job_id)
        
        # Update job status
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        # Initialize the processing service
        processing_service = ImageProcessingService()
        
        # For wedding processing, use the generated prompt directly
        prompt_text = job.generated_prompt
        if not prompt_text:
            # Fallback: regenerate prompt if missing
            from .models import generate_wedding_prompt
            prompt_text = generate_wedding_prompt(job.wedding_theme, job.space_type)
            job.generated_prompt = prompt_text
            job.save()
        
        logger.info(f"Processing wedding image with prompt: {prompt_text[:100]}...")
        
        # Process the image
        result = processing_service.stability_service.image_to_image(
            image_path=job.user_image.image.path,
            prompt=prompt_text,
            cfg_scale=job.cfg_scale,
            steps=job.steps,
            seed=job.seed
        )
        
        if result["success"] and result["results"]:
            # Save the processed image
            for img_result in result["results"]:
                processed_image = ProcessedImage(
                    processing_job=job,
                    prompt_template=None,  # We don't use prompt templates for wedding processing
                    stability_seed=img_result.get("seed"),
                    finish_reason=img_result.get("finish_reason")
                )
                
                # Save the image file with wedding context in filename
                theme_space = f"{job.wedding_theme}_{job.space_type}"
                filename = f"wedding_{theme_space}_{job.id}_{timezone.now().timestamp()}.png"
                processed_image.processed_image.save(
                    filename,
                    ContentFile(img_result["image_data"]),
                    save=False
                )
                processed_image.save()
                
                logger.info(f"Successfully saved wedding processed image: {filename}")
            
            # Update job status to completed
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save()
            
            logger.info(f"Successfully completed wedding processing job {job_id}")
            return {
                'success': True,
                'job_id': job_id,
                'theme': job.wedding_theme,
                'space': job.space_type
            }
        else:
            # No successful results
            error_msg = result.get('error', 'No images were successfully processed')
            job.status = 'failed'
            job.error_message = error_msg
            job.completed_at = timezone.now()
            job.save()
            
            logger.error(f"Wedding processing failed for job {job_id}: {error_msg}")
            return {
                'success': False,
                'job_id': job_id,
                'error': error_msg
            }
            
    except ImageProcessingJob.DoesNotExist:
        logger.error(f"Wedding processing job {job_id} not found")
        return {
            'success': False,
            'error': f'Job {job_id} not found'
        }
        
    except Exception as exc:
        logger.error(f"Error processing wedding job {job_id}: {str(exc)}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            # Exponential backoff: 60s, 120s, 240s
            countdown = 60 * (2 ** self.request.retries)
            logger.info(f"Retrying wedding job {job_id} in {countdown} seconds")
            raise self.retry(countdown=countdown, exc=exc)
        
        # Mark job as failed if all retries exhausted
        try:
            job = ImageProcessingJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_message = f"Processing failed after {self.max_retries} retries: {str(exc)}"
            job.completed_at = timezone.now()
            job.save()
        except Exception:
            pass
        
        return {
            'success': False,
            'job_id': job_id,
            'error': str(exc)
        }


@shared_task
def cleanup_old_wedding_jobs():
    """
    Clean up old wedding processing jobs and their files
    Run this daily to keep storage manageable
    """
    from datetime import timedelta
    import os
    from django.conf import settings
    
    # Delete jobs older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    
    old_jobs = ImageProcessingJob.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['completed', 'failed']
    )
    
    deleted_count = 0
    for job in old_jobs:
        try:
            # Delete associated processed images
            for processed_image in job.processed_images.all():
                if processed_image.processed_image:
                    file_path = processed_image.processed_image.path
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Deleted old wedding image: {file_path}")
            
            # Delete the job
            job.delete()
            deleted_count += 1
            
        except Exception as e:
            logger.error(f"Error deleting old wedding job {job.id}: {str(e)}")
    
    logger.info(f"Cleaned up {deleted_count} old wedding processing jobs")
    return deleted_count


@shared_task
def generate_wedding_preview(theme, space_type):
    """
    Generate a preview of what a wedding theme + space combination might look like
    This could be used for showing examples before processing
    """
    from .models import generate_wedding_prompt
    
    prompt = generate_wedding_prompt(theme, space_type)
    logger.info(f"Generated wedding preview prompt for {theme} + {space_type}")
    
    return {
        'theme': theme,
        'space_type': space_type,
        'prompt': prompt
    }