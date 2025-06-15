import logging
from celery import shared_task
from django.utils import timezone
from .models import ImageProcessingJob
from .services import ImageProcessingService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_image_async(self, job_id):
    """
    Asynchronously process an image with Stability AI
    """
    try:
        # Get the processing job
        job = ImageProcessingJob.objects.get(id=job_id)
        
        # Initialize the processing service
        processing_service = ImageProcessingService()
        
        # Process the image
        results = processing_service.process_image_with_prompts(job)
        
        if results:
            logger.info(f"Successfully processed job {job_id} with {len(results)} results")
            return {
                'success': True,
                'job_id': job_id,
                'processed_count': len(results)
            }
        else:
            logger.error(f"No results for job {job_id}")
            return {
                'success': False,
                'job_id': job_id,
                'error': 'No images were processed successfully'
            }
            
    except ImageProcessingJob.DoesNotExist:
        logger.error(f"Processing job {job_id} not found")
        return {
            'success': False,
            'error': f'Job {job_id} not found'
        }
        
    except Exception as exc:
        logger.error(f"Error processing job {job_id}: {str(exc)}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            # Exponential backoff: 60s, 120s, 240s
            countdown = 60 * (2 ** self.request.retries)
            logger.info(f"Retrying job {job_id} in {countdown} seconds")
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
def cleanup_old_processing_jobs():
    """
    Clean up old processing jobs and their files
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
            
            # Delete the job
            job.delete()
            deleted_count += 1
            
        except Exception as e:
            logger.error(f"Error deleting old job {job.id}: {str(e)}")
    
    logger.info(f"Cleaned up {deleted_count} old processing jobs")
    return deleted_count


@shared_task
def check_stability_ai_balance():
    """
    Check Stability AI account balance and log warnings if low
    """
    try:
        from .services import StabilityAIService
        
        service = StabilityAIService()
        balance = service.get_account_balance()
        
        credits = balance.get('credits', 0)
        
        if credits < 10:
            logger.warning(f"Stability AI credits running low: {credits} remaining")
        elif credits < 50:
            logger.info(f"Stability AI credits: {credits} remaining")
        
        return {
            'success': True,
            'credits': credits
        }
        
    except Exception as e:
        logger.error(f"Error checking Stability AI balance: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }