# image_processing/tasks.py - SIMPLIFIED VERSION with fixed parameters

import logging
from celery import shared_task
from django.utils import timezone
from django.db import models
from .models import ImageProcessingJob, ProcessedImage, UserImage
from .services import ImageProcessingService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_image_async(self, job_id):
    """
    Asynchronously process a wedding venue image - SIMPLIFIED VERSION
    """
    try:
        # Get the processing job
        job = ImageProcessingJob.objects.get(id=job_id)
        
        logger.info(f"Starting processing job {job_id} for user {job.user_image.user.username}")
        logger.info(f"Job settings: {job.wedding_theme} + {job.space_type} (FIXED: 70% strength, 30 steps)")
        
        # Update job status
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        # Initialize the processing service
        processing_service = ImageProcessingService()
        
        # Ensure we have a generated prompt with SIMPLIFIED parameter handling
        if not job.generated_prompt:
            logger.info(f"Generating prompt for job {job_id}")
            try:
                # Import the updated function from models
                from .models import generate_wedding_prompt
                
                # SIMPLIFIED: Only pass non-empty optional parameters
                optional_params = {}
                
                # List of SIMPLIFIED optional fields
                optional_fields = ['season', 'lighting_mood', 'color_scheme', 'special_features', 'avoid']
                
                # Only include parameters that have actual values
                for field in optional_fields:
                    value = getattr(job, field, None)
                    if value and value.strip():  # Only if not empty/None
                        # Special handling for lighting_mood -> time_of_day mapping if needed
                        if field == 'lighting_mood':
                            optional_params['lighting_mood'] = value.strip()
                        else:
                            optional_params[field] = value.strip()
                
                logger.info(f"Using simplified optional parameters: {optional_params}")
                
                prompt_data = generate_wedding_prompt(
                    wedding_theme=job.wedding_theme,
                    space_type=job.space_type,
                    **optional_params  # Only pass non-empty parameters
                )
                
                job.generated_prompt = prompt_data['prompt']
                job.negative_prompt = prompt_data['negative_prompt']
                
                # FIXED: Override with our fixed parameters regardless of recommendations
                job.strength = 0.70      # Fixed at 70%
                job.cfg_scale = 7.5      # Standard CFG
                job.steps = 30           # Fixed at 30 steps
                job.output_format = 'png'
                
                job.save()
                logger.info(f"Generated prompt for job {job_id} with FIXED parameters")
                logger.info(f"Prompt preview: {job.generated_prompt[:150]}...")
                
            except Exception as e:
                logger.error(f"Error generating prompt for job {job_id}: {str(e)}")
                # Create a basic fallback prompt
                theme_name = job.theme_display_name
                space_name = job.space_display_name
                job.generated_prompt = f"elegant wedding {space_name.lower()} with {theme_name.lower()} style, professional wedding photography, high quality, elegant decoration"
                job.negative_prompt = "people, faces, crowd, guests, bride, groom, wedding party, blurry, low quality, dark, messy, text, watermark"
                
                # FIXED: Still set our fixed parameters even on fallback
                job.strength = 0.70
                job.cfg_scale = 7.5
                job.steps = 30
                job.output_format = 'png'
                job.save()
        
        # Validate critical parameters only
        if not job.wedding_theme or not job.space_type:
            raise ValueError("Missing required wedding_theme or space_type")
        
        # FIXED: Ensure our fixed parameters are always set correctly
        if job.strength != 0.70 or job.steps != 30:
            logger.info(f"Correcting parameters: strength {job.strength}->0.70, steps {job.steps}->30")
            job.strength = 0.70
            job.steps = 30
            job.cfg_scale = 7.5
            job.save()
        
        # Log final processing parameters
        logger.info(f"FIXED Processing parameters:")
        logger.info(f"  - Strength: {job.strength} (FIXED)")
        logger.info(f"  - CFG Scale: {job.cfg_scale} (FIXED)")
        logger.info(f"  - Steps: {job.steps} (FIXED)")
        logger.info(f"  - Theme: {job.wedding_theme}")
        logger.info(f"  - Space: {job.space_type}")
        
        # Simplified active parameters logging
        active_optional = []
        if job.season:
            active_optional.append(f"season={job.season}")
        if job.lighting_mood:
            active_optional.append(f"lighting={job.lighting_mood}")
        if job.color_scheme:
            active_optional.append(f"colors={job.color_scheme}")
        if job.special_features:
            active_optional.append("special_features")
        if job.avoid:
            active_optional.append("avoid_list")
            
        if active_optional:
            logger.info(f"  - Optional: {', '.join(active_optional)}")
        else:
            logger.info(f"  - Using core parameters only")
        
        # Process the image using the enhanced service
        success = processing_service.process_wedding_image(job)
        
        if success:
            logger.info(f"Successfully completed wedding processing job {job_id}")
            
            # Log final result info
            processed_images = job.processed_images.all()
            if processed_images:
                img = processed_images.first()
                logger.info(f"Final result: {img.width}x{img.height}, {img.file_size} bytes")
                
                # Validate the result
                if img.file_size < 10000:  # Less than 10KB
                    logger.warning(f"Generated image unusually small: {img.file_size} bytes")
                
                if img.width < 256 or img.height < 256:
                    logger.warning(f"Generated image low resolution: {img.width}x{img.height}")
            
            return {
                'success': True,
                'job_id': job_id,
                'theme': job.wedding_theme,
                'space_type': job.space_type,
                'strength': job.strength,
                'steps': job.steps,
                'active_optional': active_optional
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
    
    except ValueError as ve:
        logger.error(f"Validation error for job {job_id}: {str(ve)}")
        
        # Mark job as failed
        try:
            job = ImageProcessingJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_message = f"Validation error: {str(ve)}"
            job.completed_at = timezone.now()
            job.save()
        except Exception as save_error:
            logger.error(f"Failed to update job status: {str(save_error)}")
        
        return {
            'success': False,
            'job_id': job_id,
            'error': str(ve)
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
def validate_job_before_processing(job_id):
    """SIMPLIFIED validation - only check core required fields"""
    try:
        job = ImageProcessingJob.objects.get(id=job_id)
        
        validation_errors = []
        validation_warnings = []
        
        # Check required fields only
        if not job.wedding_theme:
            validation_errors.append("Missing wedding theme")
        elif job.wedding_theme not in [choice[0] for choice in job._meta.get_field('wedding_theme').choices]:
            validation_errors.append(f"Invalid wedding theme: {job.wedding_theme}")
        
        if not job.space_type:
            validation_errors.append("Missing space type")
        elif job.space_type not in [choice[0] for choice in job._meta.get_field('space_type').choices]:
            validation_errors.append(f"Invalid space type: {job.space_type}")
        
        # SIMPLIFIED: Check optional field validity (only the ones we kept)
        if job.color_scheme:
            from .models import COLOR_SCHEMES
            valid_colors = [choice[0] for choice in COLOR_SCHEMES if choice[0]]
            if job.color_scheme not in valid_colors:
                validation_warnings.append(f"Invalid color scheme: {job.color_scheme}, will be ignored")
                job.color_scheme = ''
        
        # FIXED: Force our fixed parameters regardless of what was set
        if job.strength != 0.70:
            validation_warnings.append(f"Strength reset to fixed value 0.70 (was {job.strength})")
            job.strength = 0.70
        
        if job.cfg_scale != 7.5:
            validation_warnings.append(f"CFG scale reset to fixed value 7.5 (was {job.cfg_scale})")
            job.cfg_scale = 7.5
        
        if job.steps != 30:
            validation_warnings.append(f"Steps reset to fixed value 30 (was {job.steps})")
            job.steps = 30
        
        # Check text field lengths (simplified)
        if job.special_features and len(job.special_features) > 500:
            validation_warnings.append("Special features text too long, will be truncated")
            job.special_features = job.special_features[:500]
        
        if job.avoid and len(job.avoid) > 500:
            validation_warnings.append("Avoid text too long, will be truncated")
            job.avoid = job.avoid[:500]
        
        # Save any corrections
        if validation_warnings:
            job.save()
        
        # If we have errors, mark job as failed
        if validation_errors:
            job.status = 'failed'
            job.error_message = "Validation errors: " + "; ".join(validation_errors)
            job.completed_at = timezone.now()
            job.save()
            
            logger.error(f"Job {job_id} failed validation: {validation_errors}")
            return {
                'success': False,
                'job_id': job_id,
                'validation_errors': validation_errors,
                'validation_warnings': validation_warnings
            }
        
        # Log warnings but proceed
        if validation_warnings:
            logger.warning(f"Job {job_id} validation warnings: {validation_warnings}")
        
        logger.info(f"Job {job_id} passed simplified validation")
        return {
            'success': True,
            'job_id': job_id,
            'validation_warnings': validation_warnings
        }
        
    except Exception as e:
        logger.error(f"Error validating job {job_id}: {str(e)}")
        return {
            'success': False,
            'job_id': job_id,
            'error': str(e)
        }


@shared_task
def cleanup_failed_jobs():
    """Clean up failed processing jobs older than 7 days"""
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
def monitor_stuck_jobs():
    """Monitor for stuck processing jobs and reset them"""
    from datetime import timedelta
    
    # Find jobs that have been processing for more than 10 minutes
    stuck_threshold = timezone.now() - timedelta(minutes=10)
    
    stuck_jobs = ImageProcessingJob.objects.filter(
        status='processing',
        started_at__lt=stuck_threshold
    )
    
    reset_count = 0
    for job in stuck_jobs:
        logger.warning(f"Resetting stuck job {job.id} (processing since {job.started_at})")
        job.status = 'pending'
        job.started_at = None
        job.save()
        reset_count += 1
        
        # Optionally requeue the job
        process_image_async.delay(job.id)
    
    if reset_count > 0:
        logger.info(f"Reset {reset_count} stuck processing jobs")
    
    return reset_count


@shared_task
def health_check():
    """SIMPLIFIED health check for the wedding processing system"""
    
    try:
        from datetime import timedelta
        
        # Check database connectivity
        recent_jobs_count = ImageProcessingJob.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        # Check job status distribution
        status_counts = {}
        for status, _ in ImageProcessingJob.STATUS_CHOICES:
            count = ImageProcessingJob.objects.filter(status=status).count()
            status_counts[status] = count
        
        # Check for stuck jobs
        stuck_jobs = ImageProcessingJob.objects.filter(
            status='processing',
            started_at__lt=timezone.now() - timedelta(hours=2)
        ).count()
        
        # Check for jobs with missing prompts
        jobs_without_prompts = ImageProcessingJob.objects.filter(
            generated_prompt__isnull=True,
            status='pending'
        ).count()
        
        # SIMPLIFIED: Check for jobs with incorrect fixed parameters
        incorrect_params_jobs = ImageProcessingJob.objects.filter(
            models.Q(strength__ne=0.70) | 
            models.Q(steps__ne=30) |
            models.Q(cfg_scale__ne=7.5)
        ).count()
        
        logger.info(f"Health check: {recent_jobs_count} recent jobs, {stuck_jobs} stuck jobs")
        logger.info(f"Status distribution: {status_counts}")
        
        if jobs_without_prompts > 0:
            logger.warning(f"Found {jobs_without_prompts} pending jobs without generated prompts")
        
        if incorrect_params_jobs > 0:
            logger.warning(f"Found {incorrect_params_jobs} jobs with incorrect fixed parameters")
        
        return {
            'success': True,
            'recent_jobs': recent_jobs_count,
            'stuck_jobs': stuck_jobs,
            'jobs_without_prompts': jobs_without_prompts,
            'incorrect_params_jobs': incorrect_params_jobs,
            'status_counts': status_counts,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def fix_incorrect_parameters():
    """Fix jobs with incorrect fixed parameters - NEW MAINTENANCE TASK"""
    
    try:
        # Find jobs with incorrect parameters
        incorrect_jobs = ImageProcessingJob.objects.filter(
            models.Q(strength__ne=0.70) | 
            models.Q(steps__ne=30) |
            models.Q(cfg_scale__ne=7.5)
        )
        
        fixed_count = 0
        for job in incorrect_jobs:
            old_params = f"strength={job.strength}, steps={job.steps}, cfg={job.cfg_scale}"
            
            job.strength = 0.70
            job.steps = 30
            job.cfg_scale = 7.5
            job.save()
            
            logger.info(f"Fixed job {job.id} parameters: {old_params} -> strength=0.70, steps=30, cfg=7.5")
            fixed_count += 1
        
        if fixed_count > 0:
            logger.info(f"Fixed {fixed_count} jobs with incorrect parameters")
        
        return {
            'success': True,
            'fixed_count': fixed_count
        }
        
    except Exception as e:
        logger.error(f"Error fixing parameters: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }