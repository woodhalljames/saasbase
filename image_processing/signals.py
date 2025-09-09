# image_processing/signals.py - Simplified for real-time processing

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import logging

from .models import ImageProcessingJob, ProcessedImage, UserImage

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ProcessedImage)
def log_successful_processing(sender, instance, created, **kwargs):
    """Log successful wedding venue transformations for monitoring"""
    if created:
        job = instance.processing_job
        user = job.user_image.user
        
        # Determine transformation type
        if job.custom_prompt:
            transform_type = "Custom"
            details = f"Custom prompt: {job.custom_prompt[:50]}..."
        else:
            transform_type = f"{job.theme_display_name} {job.space_display_name}"
            details = f"Theme: {job.wedding_theme}, Space: {job.space_type}"
        
        logger.info(
            f"Wedding venue transformation completed - "
            f"User: {user.username}, "
            f"Type: {transform_type}, "
            f"Model: {instance.gemini_model}, "
            f"Size: {instance.width}x{instance.height}, "
            f"Details: {details}"
        )

@receiver(pre_delete, sender=UserImage)
def cleanup_image_deletion(sender, instance, **kwargs):
    """Clean up processing jobs when user image is deleted"""
    try:
        job_count = ImageProcessingJob.objects.filter(user_image=instance).count()
        
        if job_count > 0:
            logger.info(f"Deleting {job_count} processing jobs for image: {instance.original_filename}")
            
    except Exception as e:
        logger.error(f"Error during image deletion cleanup: {str(e)}")

@receiver(post_save, sender=ImageProcessingJob)
def log_job_creation(sender, instance, created, **kwargs):
    """Log job creation for monitoring"""
    if created:
        user = instance.user_image.user
        
        if instance.custom_prompt:
            job_type = f"Custom: {instance.custom_prompt[:50]}..."
        else:
            job_type = f"{instance.wedding_theme} {instance.space_type}"
        
        logger.info(f"Wedding transformation job created - User: {user.username}, Type: {job_type}")