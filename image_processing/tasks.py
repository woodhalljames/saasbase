# image_processing/tasks.py - Updated for venue, wedding, and engagement modes

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.base import ContentFile
import logging
import time
import re
import random
import string
from PIL import Image as PILImage
from io import BytesIO

from .models import ImageProcessingJob, ProcessedImage, UserImage, WEDDING_THEMES, SPACE_TYPES, PORTRAIT_THEMES, PORTRAIT_SETTINGS
from usage_limits.usage_tracker import UsageTracker

logger = logging.getLogger(__name__)
User = get_user_model()


def generate_human_readable_filename(job, file_extension='png'):
    """
    Generate human-readable filename for processed images.
    
    Format for venue: {Space}_{Theme}_{Date}_{RandomSuffix}.{ext}
    Format for portrait: {Mode}_{Theme}_{Date}_{RandomSuffix}.{ext}
    Format for custom: Custom_{Date}_{RandomSuffix}.{ext}
    
    Args:
        job: ImageProcessingJob instance
        file_extension: File extension (default: 'png')
        
    Returns:
        str: Human-readable filename
    """
    try:
        def clean_for_filename(text):
            if not text:
                return ""
            cleaned = re.sub(r'[^\w\s-]', '', str(text))
            cleaned = re.sub(r'\s+', '_', cleaned.strip())
            parts = cleaned.split('_')
            cleaned = '_'.join(word.capitalize() for word in parts if word)
            return cleaned
        
        date_str = job.created_at.strftime('%Y-%m-%d')
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        
        if job.custom_prompt:
            # Custom prompt mode
            filename_parts = ['Custom', date_str, random_suffix]
        elif job.studio_mode == 'venue':
            # Venue mode
            theme_display = dict(WEDDING_THEMES).get(job.wedding_theme, job.wedding_theme) if job.wedding_theme else 'Venue'
            space_display = dict(SPACE_TYPES).get(job.space_type, job.space_type) if job.space_type else 'Space'
            
            theme_clean = clean_for_filename(theme_display)
            space_clean = clean_for_filename(space_display)
            
            filename_parts = [space_clean, theme_clean, date_str, random_suffix]
        else:
            # Portrait mode (wedding or engagement)
            mode_name = 'Wedding' if job.studio_mode == 'portrait_wedding' else 'Engagement'
            theme_display = dict(PORTRAIT_THEMES).get(job.photo_theme, job.photo_theme) if job.photo_theme else 'Portrait'
            
            mode_clean = clean_for_filename(mode_name)
            theme_clean = clean_for_filename(theme_display)
            
            filename_parts = [mode_clean, theme_clean, date_str, random_suffix]
        
        base_name = '_'.join(part for part in filename_parts if part)
        
        # Ensure filename isn't too long
        if len(base_name) > 80:
            suffix_parts = [date_str, random_suffix]
            suffix_length = len('_'.join(suffix_parts)) + 1
            max_base_length = 80 - suffix_length
            truncated_base = base_name[:max_base_length]
            base_name = f"{truncated_base}_{date_str}_{random_suffix}"
        
        filename = f"{base_name}.{file_extension}"
        logger.info(f"Generated filename for job {job.id}: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error generating readable filename for job {job.id}: {str(e)}")
        fallback_name = f"Design_{job.created_at.strftime('%Y-%m-%d')}_{random.randint(1000, 9999)}.{file_extension}"
        return fallback_name


@shared_task(bind=True, max_retries=2)
def process_image_job(self, job_id):
    """
    Main task router for all studio modes.
    Routes to appropriate processing based on studio_mode.
    """
    try:
        job = ImageProcessingJob.objects.get(id=job_id)
        user = job.user_image.user
        
        logger.info(f"Starting processing for job {job_id}, mode: {job.studio_mode}, user: {user.username}")
        
        # Update job status
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save(update_fields=['status', 'started_at'])
        
        # Route to appropriate processor
        if job.studio_mode == 'venue':
            result = process_venue_job(job)
        elif job.studio_mode in ['portrait_wedding', 'portrait_engagement']:
            result = process_portrait_job(job)
        else:
            raise ValueError(f"Unknown studio mode: {job.studio_mode}")
        
        if result['success']:
            # Increment usage counter
            if not UsageTracker.increment_usage(user, 1):
                logger.warning(f"Usage increment failed for user {user.id} after successful generation")
            
            # Update job to completed
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save(update_fields=['status', 'completed_at'])
            
            processing_time = (job.completed_at - job.started_at).total_seconds()
            logger.info(f"Job {job_id} completed in {processing_time:.1f}s")
            
            return {
                'success': True,
                'job_id': job_id,
                'processed_image_id': result['processed_image_id'],
                'processing_time': processing_time
            }
        else:
            # Failed
            job.status = 'failed'
            job.error_message = result.get('error', 'Unknown error')
            job.save(update_fields=['status', 'error_message'])
            
            logger.error(f"Job {job_id} failed: {job.error_message}")
            
            return {
                'success': False,
                'job_id': job_id,
                'error': job.error_message
            }
            
    except ImageProcessingJob.DoesNotExist:
        logger.error(f"Job {job_id} not found")
        return {'success': False, 'error': f'Job {job_id} not found'}
        
    except Exception as e:
        logger.error(f"Unexpected error in job {job_id}: {str(e)}")
        
        try:
            job = ImageProcessingJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_message = f'System error: {str(e)}'
            job.save(update_fields=['status', 'error_message'])
        except:
            pass
        
        # Retry if we haven't exceeded max retries
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job {job_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=30)
        
        return {'success': False, 'error': str(e)}


def process_venue_job(job):
    """
    Process venue transformation job.
    Can use multiple input images for context.
    """
    try:
        from .services import GeminiImageService
        
        service = GeminiImageService()
        
        # Get all reference images (up to 5)
        reference_images = [job.user_image]  # Start with primary image
        
        # Add additional reference images if any
        for ref in job.reference_images.all()[:4]:  # Max 4 additional (5 total)
            reference_images.append(ref.reference_image)
        
        logger.info(f"Processing venue job {job.id} with {len(reference_images)} image(s)")
        
        # Read all images
        image_data_list = []
        for img in reference_images:
            with img.image.open('rb') as image_file:
                image_data_list.append(image_file.read())
        
        # Get the generated prompt
        prompt = job.generated_prompt or "Transform this space into a beautiful wedding venue"
        
        logger.info(f"Venue prompt length: {len(prompt)} chars")
        
        # Call Gemini API with multiple images - NO MODE PARAMETER
        result = service.transform_with_multiple_images(
            image_data_list=image_data_list,
            prompt=prompt
        )
        
        if result['success']:
            # Save the generated image
            processed_image = ProcessedImage(
                processing_job=job,
                gemini_model=result.get('model', 'gemini-2.5-flash-image-preview'),
                finish_reason=result.get('finish_reason', 'STOP')
            )
            
            # Generate human-readable filename
            readable_filename = generate_human_readable_filename(job, 'png')
            
            # Save the generated image
            image_content = ContentFile(result['image_data'])
            processed_image.processed_image.save(readable_filename, image_content, save=True)
            
            logger.info(f"Successfully saved venue transformation: {readable_filename}")
            
            return {
                'success': True,
                'processed_image_id': processed_image.id,
                'model': result.get('model', 'gemini-2.5-flash-image-preview'),
                'finish_reason': result.get('finish_reason', 'STOP'),
                'filename': readable_filename
            }
        else:
            logger.error(f"Venue transformation failed for job {job.id}: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error', 'Gemini API failed')
            }
            
    except Exception as e:
        logger.error(f"Error in venue processing for job {job.id}: {str(e)}")
        return {
            'success': False,
            'error': f'Processing error: {str(e)}'
        }


def process_portrait_job(job):
    """
    Process portrait job (wedding or engagement).
    Uses multiple reference images (faces, clothing, pets, etc).
    """
    try:
        from .services import GeminiImageService
        
        service = GeminiImageService()
        
        # Get all reference images (up to 5)
        reference_images = [job.user_image]  # Start with primary image
        
        # Add additional reference images
        for ref in job.reference_images.all()[:4]:  # Max 4 additional (5 total)
            reference_images.append(ref.reference_image)
        
        logger.info(f"Processing portrait job {job.id} with {len(reference_images)} reference image(s)")
        
        # Read all images
        image_data_list = []
        for img in reference_images:
            with img.image.open('rb') as image_file:
                image_data_list.append(image_file.read())
        
        # Get the generated prompt
        prompt = job.generated_prompt or "Generate a beautiful portrait photograph"
        
        logger.info(f"Portrait prompt length: {len(prompt)} chars")
        
        # Call Gemini API with multiple reference images - NO MODE PARAMETER
        result = service.transform_with_multiple_images(
            image_data_list=image_data_list,
            prompt=prompt
        )
        
        if result['success']:
            # Save the generated portrait
            processed_image = ProcessedImage(
                processing_job=job,
                gemini_model=result.get('model', 'gemini-2.5-flash-image-preview'),
                finish_reason=result.get('finish_reason', 'STOP')
            )
            
            # Generate human-readable filename
            readable_filename = generate_human_readable_filename(job, 'png')
            
            # Save the generated image
            image_content = ContentFile(result['image_data'])
            processed_image.processed_image.save(readable_filename, image_content, save=True)
            
            logger.info(f"Successfully saved portrait: {readable_filename}")
            
            return {
                'success': True,
                'processed_image_id': processed_image.id,
                'model': result.get('model', 'gemini-2.5-flash-image-preview'),
                'finish_reason': result.get('finish_reason', 'STOP'),
                'filename': readable_filename
            }
        else:
            logger.error(f"Portrait generation failed for job {job.id}: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error', 'Gemini API failed')
            }
            
    except Exception as e:
        logger.error(f"Error in portrait processing for job {job.id}: {str(e)}")
        return {
            'success': False,
            'error': f'Processing error: {str(e)}'
        }


@shared_task
def process_realtime(job_id):
    """
    Synchronous processing for real-time results.
    Used when immediate results are needed.
    """
    try:
        job = ImageProcessingJob.objects.get(id=job_id)
        
        # Mark as processing
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save(update_fields=['status', 'started_at'])
        
        # Process based on mode
        if job.studio_mode == 'venue':
            result = process_venue_job(job)
        elif job.studio_mode in ['portrait_wedding', 'portrait_engagement']:
            result = process_portrait_job(job)
        else:
            raise ValueError(f"Unknown studio mode: {job.studio_mode}")
        
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
                'processed_image_id': result['processed_image_id'],
                'filename': result.get('filename', 'Output.png')
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
        logger.error(f"Error in real-time processing {job_id}: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task(bind=True)
def cleanup_old_jobs(self):
    """
    Cleanup task for old processing jobs and failed jobs.
    Runs periodically to keep database clean.
    """
    from datetime import timedelta
    
    try:
        # Find stuck jobs (processing for more than 30 minutes)
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
                logger.info(f"Marked stuck job {job.id} as failed")
                
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
            logger.info(f"Cleanup completed: {cleaned_count} stuck jobs, {deleted_count} deleted")
        
        return {'cleaned_jobs': cleaned_count, 'deleted_jobs': deleted_count}
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_jobs: {str(e)}")
        return {'error': str(e)}