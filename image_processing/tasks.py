import logging
from celery import shared_task
from django.utils import timezone
from .models import ImageProcessingJob, ProcessedImage
from .services import ImageProcessingService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_image_async(self, job_id):
    """
    Asynchronously process a wedding venue image with SD3.5 Large and enhanced dynamic parameters
    Now supports religion/culture elements and user-defined negative prompts
    """
    try:
        # Get the processing job
        job = ImageProcessingJob.objects.get(id=job_id)
        
        logger.info(f"Starting enhanced SD3.5 Large processing job {job_id} for user {job.user_image.user.username}")
        
        # Update job status
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        # Initialize the processing service
        processing_service = ImageProcessingService()
        
        # Ensure we have a generated prompt (with enhanced dynamic parameters)
        if not job.generated_prompt:
            logger.info(f"Generating enhanced transformation prompt for SD3.5 Large job {job_id}")
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
                    religion_culture=job.religion_culture,  # NEW: Religion/culture parameter
                    user_negative_prompt=job.user_negative_prompt,  # NEW: User negative prompt parameter
                    additional_details=job.additional_details
                )
                
                job.generated_prompt = prompt_data['prompt']
                job.negative_prompt = prompt_data['negative_prompt']
                
                # Update SD3.5 Large parameters with recommendations
                recommended_params = prompt_data['recommended_params']
                job.strength = recommended_params.get('strength', job.strength)
                job.cfg_scale = recommended_params.get('cfg_scale', job.cfg_scale)
                job.steps = recommended_params.get('steps', job.steps)
                job.output_format = recommended_params.get('output_format', job.output_format)
                # Note: aspect_ratio removed to maintain original image dimensions
                
                job.save()
                logger.info(f"Generated enhanced dynamic prompt for SD3.5 Large job {job_id}: {job.generated_prompt[:100]}...")
                
            except Exception as e:
                logger.error(f"Error generating enhanced transformation prompt for SD3.5 Large job {job_id}: {str(e)}")
                # Create a basic fallback prompt
                job.generated_prompt = f"Transform this space to become a beautiful {job.space_type} with {job.wedding_theme} wedding style, professional wedding photography, high quality, elegant transformation"
                job.negative_prompt = "people, faces, crowd, guests, blurry, low quality, dark, messy"
                job.save()
        
        prompt_text = job.generated_prompt
        logger.info(f"Processing wedding venue with SD3.5 Large using enhanced prompt: {prompt_text[:100]}...")
        
        # Log enhanced dynamic parameters and SD3.5 Large settings being used
        dynamic_params = {
            'guest_count': job.guest_count,
            'budget_level': job.budget_level,
            'season': job.season,
            'time_of_day': job.time_of_day,
            'color_scheme': job.color_scheme,
            'custom_colors': job.custom_colors,
            'religion_culture': job.religion_culture,  # NEW: Religion/culture in logging
            'user_negative_prompt': job.user_negative_prompt  # NEW: User negative prompt in logging
        }
        sd35_params = {
            'cfg_scale': job.cfg_scale,
            'steps': job.steps,
            'strength': job.strength,
        }
        
        used_params = {k: v for k, v in dynamic_params.items() if v}
        if used_params:
            logger.info(f"Using enhanced dynamic parameters: {used_params}")
        logger.info(f"Using SD3.5 Large parameters: {sd35_params}")
        
        # Special logging for new features
        if job.religion_culture:
            logger.info(f"Cultural/religious elements: {job.religion_culture}")
        if job.user_negative_prompt:
            logger.info(f"User negative prompt specified: {job.user_negative_prompt[:50]}...")
        
        # Process the image using the service (SD3.5 Large)
        success = processing_service.process_wedding_image(job)
        
        if success:
            logger.info(f"Successfully completed enhanced wedding processing job {job_id} with SD3.5 Large")
            return {
                'success': True,
                'job_id': job_id,
                'theme': job.wedding_theme,
                'space_type': job.space_type,
                'dynamic_params': used_params,
                'sd35_params': sd35_params,
                'religion_culture': job.religion_culture,
                'has_user_negative_prompt': bool(job.user_negative_prompt),
                'model': 'SD3.5-Large'
            }
        else:
            logger.error(f"Enhanced SD3.5 Large wedding processing failed for job {job_id}")
            return {
                'success': False,
                'job_id': job_id,
                'error': 'Enhanced SD3.5 Large processing failed'
            }
            
    except ImageProcessingJob.DoesNotExist:
        logger.error(f"Enhanced wedding processing job {job_id} not found")
        return {
            'success': False,
            'error': f'Job {job_id} not found'
        }
        
    except Exception as exc:
        logger.error(f"Error processing enhanced wedding job {job_id} with SD3.5 Large: {str(exc)}", exc_info=True)
        
        # Retry logic with exponential backoff - SD3.5 Large may need more time
        if self.request.retries < self.max_retries:
            countdown = 120 * (2 ** self.request.retries)  # 120s, 240s, 480s (longer for SD3.5 Large)
            logger.info(f"Retrying enhanced SD3.5 Large wedding job {job_id} in {countdown} seconds (attempt {self.request.retries + 1})")
            raise self.retry(countdown=countdown, exc=exc)
        
        # Mark job as failed if all retries exhausted
        try:
            job = ImageProcessingJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_message = f"Enhanced SD3.5 Large processing failed after {self.max_retries} retries: {str(exc)}"
            job.completed_at = timezone.now()
            job.save()
            logger.error(f"Enhanced job {job_id} marked as failed after {self.max_retries} retries")
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
    Generate a preview prompt for a wedding theme + space transformation with enhanced SD3.5 Large dynamic params
    Now supports religion/culture and user negative prompts
    """
    from .models import generate_wedding_prompt_with_dynamics
    
    prompt_data = generate_wedding_prompt_with_dynamics(
        wedding_theme=theme,
        space_type=space_type,
        **dynamic_params
    )
    
    logger.info(f"Generated enhanced SD3.5 Large transformation preview prompt for {theme} + {space_type} with enhanced dynamic params")
    
    # Log new features if used
    if dynamic_params.get('religion_culture'):
        logger.info(f"Preview includes cultural elements: {dynamic_params['religion_culture']}")
    if dynamic_params.get('user_negative_prompt'):
        logger.info(f"Preview includes user negative prompt: {dynamic_params['user_negative_prompt'][:50]}...")
    
    return {
        'theme': theme,
        'space_type': space_type,
        'dynamic_params': dynamic_params,
        'prompt': prompt_data['prompt'],
        'negative_prompt': prompt_data['negative_prompt'],
        'recommended_params': prompt_data['recommended_params'],
        'model': 'SD3.5-Large',
        'enhanced_features': {
            'religion_culture': dynamic_params.get('religion_culture'),
            'user_negative_prompt': bool(dynamic_params.get('user_negative_prompt'))
        }
    }


@shared_task
def optimize_sd35_parameters(job_id):
    """
    Optimize SD3.5 Large parameters based on theme, space type, and enhanced features
    """
    try:
        job = ImageProcessingJob.objects.get(id=job_id)
        
        # Enhanced theme-specific optimizations for SD3.5 Large
        optimizations = {
            'rustic': {'cfg_scale': 6.0, 'steps': 45, 'strength': 0.35},
            'modern': {'cfg_scale': 8.0, 'steps': 55, 'strength': 0.45},
            'vintage': {'cfg_scale': 7.5, 'steps': 50, 'strength': 0.4},
            'bohemian': {'cfg_scale': 6.5, 'steps': 45, 'strength': 0.35},
            'classic': {'cfg_scale': 8.0, 'steps': 55, 'strength': 0.4},
            'garden': {'cfg_scale': 6.0, 'steps': 45, 'strength': 0.35},
            'beach': {'cfg_scale': 6.5, 'steps': 50, 'strength': 0.4},
            'industrial': {'cfg_scale': 8.5, 'steps': 60, 'strength': 0.45},
        }
        
        # Space-specific adjustments
        space_adjustments = {
            'wedding_ceremony': {'strength': 0.0},  # Slightly less strength for ceremonies
            'reception_area': {'strength': 0.05},   # More transformation for receptions
            'dance_floor': {'cfg_scale': 1.0},      # Higher CFG for dance floors
        }
        
        # NEW: Religion/culture specific adjustments
        religion_adjustments = {
            'hindu': {'cfg_scale': 1.0, 'steps': 5},  # More detail for vibrant Hindu decorations
            'jewish': {'cfg_scale': 0.5},             # Refined control for elegant Jewish elements
            'muslim': {'cfg_scale': 0.5},             # Elegant control for Islamic elements
            'christian': {'cfg_scale': 0.5},          # Traditional control for Christian elements
            'cultural_fusion': {'cfg_scale': 1.0, 'steps': 10},  # Higher control needed for complex fusion
        }
        
        # NEW: User negative prompt adjustments
        if job.user_negative_prompt:
            # If user specified negative elements, slightly increase CFG for better adherence
            job.cfg_scale += 0.5
            logger.info(f"Increased CFG scale by 0.5 due to user negative prompt for job {job_id}")
        
        if job.wedding_theme in optimizations:
            opt = optimizations[job.wedding_theme]
            job.cfg_scale = opt.get('cfg_scale', job.cfg_scale)
            job.steps = opt.get('steps', job.steps)
            job.strength = opt.get('strength', job.strength)
        
        if job.space_type in space_adjustments:
            adj = space_adjustments[job.space_type]
            job.cfg_scale += adj.get('cfg_scale', 0)
            job.strength += adj.get('strength', 0)
        
        # Apply religion/culture specific adjustments
        if job.religion_culture in religion_adjustments:
            adj = religion_adjustments[job.religion_culture]
            job.cfg_scale += adj.get('cfg_scale', 0)
            job.steps += adj.get('steps', 0)
            logger.info(f"Applied {job.religion_culture} cultural adjustments to job {job_id}")
        
        # Clamp values to valid ranges
        job.cfg_scale = max(1.0, min(20.0, job.cfg_scale))
        job.steps = max(10, min(150, job.steps))
        job.strength = max(0.0, min(1.0, job.strength))
        
        job.save()
        
        logger.info(f"Optimized enhanced SD3.5 Large parameters for job {job_id}: cfg_scale={job.cfg_scale}, steps={job.steps}, strength={job.strength}")
        
        return {
            'success': True,
            'job_id': job_id,
            'optimized_params': {
                'cfg_scale': job.cfg_scale,
                'steps': job.steps,
                'strength': job.strength
            },
            'enhanced_features_applied': {
                'religion_culture': job.religion_culture,
                'user_negative_prompt': bool(job.user_negative_prompt)
            }
        }
        
    except Exception as e:
        logger.error(f"Error optimizing enhanced SD3.5 Large parameters for job {job_id}: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


@shared_task
def analyze_cultural_preferences():
    """
    Analyze user preferences for different cultural/religious wedding elements
    This helps improve suggestions and optimize the cultural elements system
    """
    from django.db.models import Count
    from collections import defaultdict
    
    try:
        # Analyze religion/culture usage patterns
        religion_stats = ImageProcessingJob.objects.filter(
            religion_culture__isnull=False
        ).values('religion_culture', 'wedding_theme', 'space_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Analyze success rates by religion/culture
        completed_jobs = ImageProcessingJob.objects.filter(
            status='completed',
            religion_culture__isnull=False
        ).values('religion_culture').annotate(
            completed_count=Count('id')
        )
        
        total_jobs = ImageProcessingJob.objects.filter(
            religion_culture__isnull=False
        ).values('religion_culture').annotate(
            total_count=Count('id')
        )
        
        # Calculate success rates
        success_rates = {}
        for total in total_jobs:
            religion = total['religion_culture']
            total_count = total['total_count']
            completed = next((c['completed_count'] for c in completed_jobs if c['religion_culture'] == religion), 0)
            success_rates[religion] = (completed / total_count) * 100 if total_count > 0 else 0
        
        logger.info("Cultural preference analysis completed:")
        logger.info(f"Most popular combinations: {list(religion_stats[:5])}")
        logger.info(f"Success rates by culture: {success_rates}")
        
        return {
            'success': True,
            'popular_combinations': list(religion_stats[:10]),
            'success_rates': success_rates,
            'total_cultural_jobs': sum(total['total_count'] for total in total_jobs)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing cultural preferences: {str(e)}")
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
    from PIL import Image as PILImage
    import io
    from django.core.files.base import ContentFile
    from .models import UserImage
    
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


@shared_task
def test_enhanced_prompt_generation():
    """
    Test task to verify enhanced prompt generation with religion/culture and user negative prompts
    """
    from .models import generate_wedding_prompt_with_dynamics
    
    test_cases = [
        {
            'wedding_theme': 'hindu',
            'space_type': 'wedding_ceremony',
            'religion_culture': 'hindu',
            'user_negative_prompt': 'dark colors, minimalist style, artificial flowers'
        },
        {
            'wedding_theme': 'vintage',
            'space_type': 'reception_area', 
            'religion_culture': 'jewish',
            'guest_count': 'medium',
            'user_negative_prompt': 'modern furniture, neon lights'
        },
        {
            'wedding_theme': 'modern',
            'space_type': 'cocktail_hour',
            'religion_culture': 'secular',
            'budget_level': 'luxury'
        }
    ]
    
    results = []
    for i, test_case in enumerate(test_cases):
        try:
            prompt_data = generate_wedding_prompt_with_dynamics(**test_case)
            results.append({
                'test_case': i + 1,
                'success': True,
                'prompt_length': len(prompt_data['prompt']),
                'negative_prompt_length': len(prompt_data['negative_prompt']),
                'has_cultural_elements': bool(test_case.get('religion_culture')),
                'has_user_negative': bool(test_case.get('user_negative_prompt'))
            })
            logger.info(f"Test case {i+1} successful - generated {len(prompt_data['prompt'])} char prompt")
        except Exception as e:
            results.append({
                'test_case': i + 1,
                'success': False,
                'error': str(e)
            })
            logger.error(f"Test case {i+1} failed: {str(e)}")
    
    return {
        'total_tests': len(test_cases),
        'successful_tests': sum(1 for r in results if r['success']),
        'results': results
    }