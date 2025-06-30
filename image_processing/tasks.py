# image_processing/tasks.py - Updated for single wedding image processing

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
    Asynchronously process a single wedding venue image
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
        
        # Use the generated prompt from the job
        prompt_text = job.generated_prompt
        if not prompt_text:
            # Fallback: regenerate prompt if missing
            from .models import generate_wedding_prompt
            prompt_text = generate_wedding_prompt(job.wedding_theme, job.space_type)
            job.generated_prompt = prompt_text
            job.save()
        
        logger.info(f"Processing wedding venue with prompt: {prompt_text[:100]}...")
        
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
    
    prompt = generate_wedding_prompt(theme, space_type)
    logger.info(f"Generated wedding preview prompt for {theme} + {space_type}")
    
    return {
        'theme': theme,
        'space_type': space_type,
        'prompt': prompt
    }


@shared_task
def process_batch_wedding_images(user_id, image_ids, theme, space_type):
    """
    Process multiple images with the same wedding theme (for future use)
    Currently not used in MVP but could be useful for bulk processing
    """
    from saas_base.users.models import User
    from .models import UserImage
    
    try:
        user = User.objects.get(id=user_id)
        results = []
        
        for image_id in image_ids:
            try:
                user_image = UserImage.objects.get(id=image_id, user=user)
                
                # Create processing job
                job = ImageProcessingJob.objects.create(
                    user_image=user_image,
                    wedding_theme=theme,
                    space_type=space_type
                )
                
                # Process synchronously (could be made async for better performance)
                result = process_image_async.apply(args=[job.id])
                results.append(result.get())
                
            except UserImage.DoesNotExist:
                logger.error(f"User image {image_id} not found for user {user_id}")
                continue
                
        return {
            'success': True,
            'processed_count': len([r for r in results if r.get('success')]),
            'failed_count': len([r for r in results if not r.get('success')]),
            'results': results
        }
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {
            'success': False,
            'error': f'User {user_id} not found'
        }