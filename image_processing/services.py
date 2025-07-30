import io
import base64
import requests
import logging
from typing import List, Dict, Any
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image

logger = logging.getLogger(__name__)


class StabilityAIService:
    """Service for interacting with Stability AI SD3.5 Large API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'STABILITY_API_KEY', None)
        self.base_url = "https://api.stability.ai"
        
        if not self.api_key:
            raise ValueError("STABILITY_API_KEY must be set in settings")
    
    def _get_headers(self):
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
    
    def image_to_image_sd35_large(self, 
                                 image_path: str, 
                                 prompt: str, 
                                 negative_prompt: str = None,
                                 strength: float = 0.35,
                                 cfg_scale: float = 7.0,
                                 steps: int = 50,
                                 seed: int = None,
                                 output_format: str = "png") -> Dict[str, Any]:
        """
        Perform image-to-image generation using Stability AI SD3.5 Large
        """
        try:
            logger.info(f"Starting SD3.5 Large generation with prompt: {prompt[:100]}...")
            
            # Read and prepare image
            with open(image_path, 'rb') as image_file:
                with Image.open(image_file) as img:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # For SD3.5 Large, use 1024x1024 as default optimal size
                    img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
                    
                    # Convert to bytes
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    image_bytes = img_buffer.getvalue()
            
            # Prepare multipart form data for SD3.5 Large
            files = {
                'image': ('image.png', image_bytes, 'image/png'),
            }
            
            # SD3.5 Large parameters - supports cfg_scale and steps
            # Note: aspect_ratio removed to maintain original image dimensions
            data = {
                'prompt': prompt,
                'model': 'sd3.5-large',
                'mode': 'image-to-image',
                'strength': str(strength),
                'cfg_scale': str(cfg_scale),
                'steps': str(steps),
                'output_format': output_format,
            }
            
            # Add optional parameters
            if negative_prompt:
                data["negative_prompt"] = negative_prompt
            
            if seed is not None:
                data["seed"] = str(seed)
            
            # Make the API request with proper headers
            url = f"{self.base_url}/v2beta/stable-image/generate/sd3"
            
            logger.info(f"Making SD3.5 Large API request to {url}")
            logger.info(f"Parameters: cfg_scale={cfg_scale}, steps={steps}, strength={strength}")
            
            # Use the headers method and ensure proper Accept header
            headers = self._get_headers()
            
            response = requests.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=120  # SD3.5 Large may take longer than Turbo
            )
            
            logger.info(f"SD3.5 Large API response status: {response.status_code}")
            logger.info(f"SD3.5 Large API response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                error_msg = f"Stability AI SD3.5 Large API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Check if response is JSON (error) or binary (image)
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                # JSON response - might be an error or JSON-wrapped image
                json_response = response.json()
                if 'errors' in json_response:
                    error_msg = f"SD3.5 Large API error: {json_response['errors']}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                # If JSON contains base64 image data
                if 'image' in json_response:
                    image_data = base64.b64decode(json_response['image'])
                else:
                    logger.error("Unexpected JSON response format")
                    raise Exception("Unexpected API response format")
            else:
                # Binary image response
                image_data = response.content
            
            # Get seed from response headers if available
            response_seed = response.headers.get("seed", seed)
            finish_reason = response.headers.get("finish-reason", "SUCCESS")
            
            return {
                "success": True,
                "results": [{
                    "image_data": image_data,
                    "seed": response_seed,
                    "finish_reason": finish_reason
                }],
                "prompt": prompt,
                "model": "SD3.5-Large"
            }
            
        except requests.exceptions.Timeout:
            logger.error("Stability AI SD3.5 Large API timeout")
            return {
                "success": False,
                "error": "API request timed out - SD3.5 Large may require more processing time"
            }
        except Exception as e:
            logger.error(f"Stability AI SD3.5 Large service error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_wedding_venue(self, image_path: str, processing_job):
        """
        Process wedding venue using SD3.5 Large
        """
        # Get parameters from the job (SD3.5 Large supports all parameters except aspect_ratio in image-to-image)
        params = {
            'prompt': processing_job.generated_prompt,
            'negative_prompt': processing_job.negative_prompt,
            'strength': processing_job.strength,
            'cfg_scale': processing_job.cfg_scale,
            'steps': processing_job.steps,
            'seed': processing_job.seed,
            'output_format': processing_job.output_format
        }
        # Note: aspect_ratio removed to maintain original image dimensions
        
        logger.info(f"Processing wedding venue for job {processing_job.id} with SD3.5 Large")
        logger.info(f"Generated prompt: {params['prompt'][:200]}...")
        logger.info(f"Parameters: cfg_scale={params['cfg_scale']}, steps={params['steps']}, strength={params['strength']}")
        
        # Use SD3.5 Large
        result = self.image_to_image_sd35_large(
            image_path=image_path,
            **params
        )
        
        if result["success"]:
            logger.info(f"Successfully processed with SD3.5 Large for job {processing_job.id}")
        else:
            logger.error(f"SD3.5 Large failed for job {processing_job.id}: {result.get('error')}")
        
        return result


class ImageProcessingService:
    """Service for handling wedding venue processing with SD3.5 Large"""
    
    def __init__(self):
        self.stability_service = StabilityAIService()
    
    def process_wedding_image(self, processing_job):
        """Process a wedding venue image with SD3.5 Large - images are permanently saved"""
        from .models import ProcessedImage
        from django.utils import timezone
        
        try:
            # Update job status
            processing_job.status = 'processing'
            processing_job.started_at = timezone.now()
            processing_job.save()
            
            user_image = processing_job.user_image
            
            logger.info(f"Starting SD3.5 Large processing for job {processing_job.id}")
            
            # Process using SD3.5 Large
            result = self.stability_service.process_wedding_venue(
                image_path=user_image.image.path,
                processing_job=processing_job
            )
            
            if result["success"] and result["results"]:
                # Save the processed image (permanently)
                img_result = result["results"][0]
                processed_image = ProcessedImage(
                    processing_job=processing_job,
                    stability_seed=img_result.get("seed"),
                    finish_reason=img_result.get("finish_reason")
                )
                
                # Save with descriptive filename
                theme_space = f"{processing_job.wedding_theme}_{processing_job.space_type}"
                model_used = result.get("model", "SD3.5-Large")
                timestamp = int(timezone.now().timestamp())
                filename = f"wedding_{theme_space}_{model_used}_{processing_job.id}_{timestamp}.png"
                
                processed_image.processed_image.save(
                    filename,
                    ContentFile(img_result["image_data"]),
                    save=False
                )
                processed_image.save()
                
                logger.info(f"Successfully saved wedding processed image: {filename}")
                
                # Update job status to completed
                processing_job.status = 'completed'
                processing_job.completed_at = timezone.now()
                processing_job.save()
                
                logger.info(f"Successfully completed wedding processing job {processing_job.id}")
                return True
            else:
                # Processing failed
                error_msg = result.get('error', 'Wedding venue transformation failed')
                processing_job.status = 'failed'
                processing_job.error_message = error_msg
                processing_job.completed_at = timezone.now()
                processing_job.save()
                
                logger.error(f"Wedding processing failed for job {processing_job.id}: {error_msg}")
                return False
                
        except Exception as exc:
            processing_job.status = 'failed'
            processing_job.error_message = str(exc)
            processing_job.completed_at = timezone.now()
            processing_job.save()
            logger.error(f"Error in processing job {processing_job.id}: {str(exc)}")
            return False