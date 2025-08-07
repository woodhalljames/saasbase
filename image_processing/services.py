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
    """Service for interacting with Stability AI Stable Image Ultra API"""
    
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
    
    def image_to_image_ultra(self, 
                            image_path: str, 
                            prompt: str, 
                            negative_prompt: str = None,
                            strength: float = 0.4,
                            cfg_scale: float = 7.0,
                            steps: int = None,  # Ultra determines optimal steps automatically
                            seed: int = None,
                            output_format: str = "png") -> Dict[str, Any]:
        """
        Perform image-to-image generation using Stability AI Stable Image Ultra
        """
        try:
            logger.info(f"Starting Stable Image Ultra generation with prompt: {prompt[:100]}...")
            
            # Read and prepare image
            with open(image_path, 'rb') as image_file:
                with Image.open(image_file) as img:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # For Stable Image Ultra, optimize for quality
                    # Maintain aspect ratio while ensuring good resolution
                    max_size = 1024
                    if max(img.size) > max_size:
                        ratio = max_size / max(img.size)
                        new_size = tuple(int(dim * ratio) for dim in img.size)
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Convert to bytes
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    image_bytes = img_buffer.getvalue()
            
            # Prepare multipart form data for Stable Image Ultra
            files = {
                'image': ('image.png', image_bytes, 'image/png'),
            }
            
            # Stable Image Ultra parameters
            data = {
                'prompt': prompt,
                'strength': str(strength),
                'output_format': output_format,
            }
            
            # Add optional parameters
            if negative_prompt:
                data["negative_prompt"] = negative_prompt
            
            if seed is not None:
                data["seed"] = str(seed)
            
            # Ultra may not use all parameters, add if provided
            if cfg_scale is not None:
                data["cfg_scale"] = str(cfg_scale)
            
            if steps is not None:
                data["steps"] = str(steps)
            
            # Use the Ultra endpoint
            url = f"{self.base_url}/v2beta/stable-image/generate/ultra"
            
            logger.info(f"Making Stable Image Ultra API request to {url}")
            logger.info(f"Parameters: strength={strength}")
            if cfg_scale:
                logger.info(f"CFG Scale: {cfg_scale}")
            if steps:
                logger.info(f"Steps: {steps}")
            
            # Make the API request
            headers = self._get_headers()
            
            response = requests.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=180  # Ultra may take longer but is higher quality
            )
            
            logger.info(f"Stable Image Ultra API response status: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = f"Stability AI Ultra API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Check if response is JSON (error) or binary (image)
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                # JSON response - might be an error or JSON-wrapped image
                json_response = response.json()
                if 'errors' in json_response:
                    error_msg = f"Ultra API error: {json_response['errors']}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                # If JSON contains base64 image data
                if 'image' in json_response:
                    image_data = base64.b64decode(json_response['image'])
                else:
                    logger.error("Unexpected JSON response format from Ultra")
                    raise Exception("Unexpected API response format")
            else:
                # Binary image response
                image_data = response.content
            
            # Get metadata from response headers
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
                "model": "Stable-Image-Ultra"
            }
            
        except requests.exceptions.Timeout:
            logger.error("Stability AI Ultra API timeout")
            return {
                "success": False,
                "error": "API request timed out - Ultra model processing time exceeded"
            }
        except Exception as e:
            logger.error(f"Stability AI Ultra service error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_wedding_venue(self, image_path: str, processing_job):
        """
        Process wedding venue using Stable Image Ultra
        """
        # Get parameters from the job
        params = {
            'prompt': processing_job.generated_prompt,
            'negative_prompt': processing_job.negative_prompt,
            'strength': processing_job.strength,
            'cfg_scale': processing_job.cfg_scale,
            'steps': processing_job.steps,
            'seed': processing_job.seed,
            'output_format': processing_job.output_format
        }
        
        logger.info(f"Processing wedding venue for job {processing_job.id} with Stable Image Ultra")
        logger.info(f"Generated prompt: {params['prompt'][:200]}...")
        logger.info(f"Parameters: cfg_scale={params['cfg_scale']}, steps={params['steps']}, strength={params['strength']}")
        
        # Use Stable Image Ultra
        result = self.image_to_image_ultra(
            image_path=image_path,
            **params
        )
        
        if result["success"]:
            logger.info(f"Successfully processed with Stable Image Ultra for job {processing_job.id}")
        else:
            logger.error(f"Stable Image Ultra failed for job {processing_job.id}: {result.get('error')}")
        
        return result


class ImageProcessingService:
    """Service for handling wedding venue processing with Stable Image Ultra"""
    
    def __init__(self):
        self.stability_service = StabilityAIService()
    
    def process_wedding_image(self, processing_job):
        """Process a wedding venue image with Stable Image Ultra - images are permanently saved"""
        from .models import ProcessedImage
        from django.utils import timezone
        
        try:
            # Update job status
            processing_job.status = 'processing'
            processing_job.started_at = timezone.now()
            processing_job.save()
            
            user_image = processing_job.user_image
            
            logger.info(f"Starting Stable Image Ultra processing for job {processing_job.id}")
            
            # Process using Stable Image Ultra
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
                model_used = result.get("model", "Stable-Image-Ultra")
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
                
                logger.info(f"Successfully completed wedding processing job {processing_job.id} with Ultra")
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