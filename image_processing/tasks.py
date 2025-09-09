# image_processing/tasks.py - Simplified for real-time Gemini processing

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.base import ContentFile
import logging
import time
from PIL import Image as PILImage
from io import BytesIO

from .models import ImageProcessingJob, ProcessedImage, UserImage
from usage_limits.usage_tracker import UsageTracker

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task(bind=True, max_retries=2)
def process_venue_transformation(self, job_id):
    """
    Process wedding venue transformation with Gemini 2.5 Flash.
    Real-time processing with direct API calls.
    """
    try:
        job = ImageProcessingJob.objects.get(id=job_id)
        user = job.user_image.user
        
        logger.info(f"Starting Gemini venue transformation for job {job_id}, user {user.username}")
        
        # Update job status to processing
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save(update_fields=['status', 'started_at'])
        
        # Process with Gemini
        result = transform_venue_with_gemini(job)
        
        if result['success']:
            # Success - increment usage counter
            if not UsageTracker.increment_usage(user, 1):
                logger.warning(f"Usage increment failed for user {user.id} after successful transformation")
                # Continue anyway since transformation was completed
            
            # Update job to completed
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save(update_fields=['status', 'completed_at'])
            
            processing_time = (job.completed_at - job.started_at).total_seconds()
            logger.info(f"Venue transformation completed in {processing_time:.1f}s - Job {job_id}, User {user.username}")
            
            return {
                'success': True,
                'job_id': job_id,
                'processed_image_id': result['processed_image_id'],
                'processing_time': processing_time
            }
        else:
            # Failed - don't increment usage
            job.status = 'failed'
            job.error_message = result.get('error', 'Unknown transformation error')
            job.save(update_fields=['status', 'error_message'])
            
            logger.error(f"Venue transformation failed - Job {job_id}: {job.error_message}")
            
            return {
                'success': False,
                'job_id': job_id,
                'error': job.error_message
            }
            
    except ImageProcessingJob.DoesNotExist:
        logger.error(f"Processing job {job_id} not found")
        return {'success': False, 'error': f'Job {job_id} not found'}
        
    except Exception as e:
        logger.error(f"Unexpected error in venue transformation {job_id}: {str(e)}")
        
        # Try to update job status
        try:
            job = ImageProcessingJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_message = f'System error: {str(e)}'
            job.save(update_fields=['status', 'error_message'])
        except:
            pass
        
        # Retry if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying venue transformation job {job_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=30)
        
        return {'success': False, 'error': str(e)}


def transform_venue_with_gemini(job):
    """
    Transform wedding venue using Gemini 2.5 Flash Image Preview.
    Direct API call with real-time processing.
    """
    try:
        from .services import GeminiImageService
        
        # Initialize Gemini service
        service = GeminiImageService()
        
        # Read the original image
        with job.user_image.image.open('rb') as image_file:
            image_data = image_file.read()
        
        # Get the generated prompt
        prompt = job.generated_prompt or "Transform this space into a beautiful wedding venue"
        
        logger.info(f"Transforming venue with Gemini 2.5 - Job {job.id}")
        logger.debug(f"Prompt length: {len(prompt)} chars")
        
        # Call Gemini API for venue transformation
        result = service.transform_venue_image(
            image_data=image_data,
            prompt=prompt
        )
        
        if result['success']:
            # Create and save the transformed image
            processed_image = ProcessedImage(
                processing_job=job,
                gemini_model=result.get('model', 'gemini-2.5-flash-image-preview'),
                finish_reason=result.get('finish_reason', 'STOP')
            )
            
            # Save the generated image
            image_content = ContentFile(result['image_data'])
            filename = f"wedding_venue_{job.id}_{int(time.time())}.png"
            processed_image.processed_image.save(filename, image_content, save=True)
            
            logger.info(f"Successfully saved wedding venue transformation - Job {job.id}")
            
            return {
                'success': True,
                'processed_image_id': processed_image.id,
                'model': result.get('model', 'gemini-2.5-flash-image-preview'),
                'finish_reason': result.get('finish_reason', 'STOP')
            }
        else:
            logger.error(f"Gemini transformation failed for job {job.id}: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error', 'Gemini API transformation failed')
            }
            
    except Exception as e:
        logger.error(f"Error in venue transformation for job {job.id}: {str(e)}")
        return {
            'success': False,
            'error': f'Transformation error: {str(e)}'
        }


@shared_task
def process_venue_realtime(job_id):
    """
    Synchronous venue transformation for real-time processing.
    Used when we want immediate results without Celery delay.
    """
    try:
        job = ImageProcessingJob.objects.get(id=job_id)
        
        # Mark as processing
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save(update_fields=['status', 'started_at'])
        
        # Transform immediately
        result = transform_venue_with_gemini(job)
        
        if result['success']:
            # Increment usage
            user = job.user_image.user
            UsageTracker.increment_usage(user, 1)
            
            # Mark as completed
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save(update_fields=['status', 'completed_at'])
            
            return {
                'success': True,
                'job_id': job_id,
                'processed_image_id': result['processed_image_id']
            }
        else:
            # Mark as failed
            job.status = 'failed'
            job.error_message = result.get('error')
            job.save(update_fields=['status', 'error_message'])
            
            return {
                'success': False,
                'job_id': job_id,
                'error': result.get('error')
            }
            
    except Exception as e:
        logger.error(f"Error in real-time venue processing {job_id}: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task(bind=True)
def cleanup_old_jobs(self):
    """
    Cleanup task for old processing jobs and failed transformations.
    Runs periodically to keep database clean.
    """
    from datetime import timedelta
    
    try:
        # Find jobs that have been processing for more than 30 minutes (stuck jobs)
        cutoff_time = timezone.now() - timedelta(minutes=30)
        stuck_jobs = ImageProcessingJob.objects.filter(
            status='processing',
            started_at__lt=cutoff_time
        )
        
        cleaned_count = 0
        for job in stuck_jobs:
            try:
                job.status = 'failed'
                job.error_message = 'Processing timeout - job stuck for over 30 minutes'
                job.save(update_fields=['status', 'error_message'])
                
                cleaned_count += 1
                logger.info(f"Marked stuck venue transformation job {job.id} as failed")
                
            except Exception as e:
                logger.error(f"Error cleaning up stuck job {job.id}: {str(e)}")
        
        # Clean up very old failed jobs (older than 7 days)
        old_failed_cutoff = timezone.now() - timedelta(days=7)
        old_failed_jobs = ImageProcessingJob.objects.filter(
            status='failed',
            created_at__lt=old_failed_cutoff
        )
        
        deleted_count = old_failed_jobs.count()
        if deleted_count > 0:
            old_failed_jobs.delete()
            logger.info(f"Deleted {deleted_count} old failed jobs")
        
        if cleaned_count > 0 or deleted_count > 0:
            logger.info(f"Cleanup completed: {cleaned_count} stuck jobs marked failed, {deleted_count} old jobs deleted")
        
        return {'cleaned_jobs': cleaned_count, 'deleted_jobs': deleted_count}
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_jobs: {str(e)}")
        return {'error': str(e)}