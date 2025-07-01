# image_processing/services.py - Updated for Stability AI SD3 with comprehensive parameters
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
    """Service for interacting with Stability AI SD3 API with full parameter support"""
    
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
    
    def prepare_image_for_api(self, image_path: str, target_resolution: tuple = None):
        """
        Prepare image for Stability AI API with optimal resolution
        SD3 works best with specific resolutions
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # SD3 optimal resolutions based on aspect ratio
                if target_resolution:
                    img = img.resize(target_resolution, Image.Resampling.LANCZOS)
                else:
                    # Auto-determine best resolution based on aspect ratio
                    optimal_size = self._get_optimal_resolution(img.size)
                    if optimal_size != img.size:
                        img = img.resize(optimal_size, Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                image_data = buffer.getvalue()
                
                return base64.b64encode(image_data).decode()
        except Exception as e:
            logger.error(f"Error preparing image: {str(e)}")
            raise
    
    def _get_optimal_resolution(self, current_size):
        """Get optimal resolution for SD3 based on current image size"""
        width, height = current_size
        aspect_ratio = width / height
        
        # SD3 optimal resolutions (maintaining aspect ratios)
        optimal_resolutions = {
            '1:1': (1024, 1024),
            '16:9': (1344, 768),
            '21:9': (1536, 640),
            '2:3': (832, 1216),
            '3:2': (1216, 832),
            '4:5': (896, 1152),
            '5:4': (1152, 896),
            '9:16': (768, 1344),
            '9:21': (640, 1536),
        }
        
        # Find closest aspect ratio
        closest_ratio = min(optimal_resolutions.keys(), 
                          key=lambda x: abs(aspect_ratio - eval(x.replace(':', '/'))))
        
        return optimal_resolutions[closest_ratio]
    
    def image_to_image_sd3(self, 
                          image_path: str, 
                          prompt: str, 
                          negative_prompt: str = None,
                          strength: float = 0.35,
                          cfg_scale: float = 7.0,
                          steps: int = 50,
                          seed: int = None,
                          aspect_ratio: str = "16:9",
                          output_format: str = "png") -> Dict[str, Any]:
        """
        Perform image-to-image generation using Stability AI SD3
        Uses the v2beta/stable-image/generate/sd3 endpoint
        """
        try:
            # Prepare the image with optimal resolution
            resolution_map = {
                "1:1": (1024, 1024),
                "16:9": (1344, 768), 
                "21:9": (1536, 640),
                "2:3": (832, 1216),
                "3:2": (1216, 832),
                "4:5": (896, 1152),
                "5:4": (1152, 896),
                "9:16": (768, 1344),
                "9:21": (640, 1536),
            }
            
            target_resolution = resolution_map.get(aspect_ratio, (1344, 768))
            init_image_b64 = self.prepare_image_for_api(image_path, target_resolution)
            
            # Prepare form data for SD3 API
            data = {
                "prompt": prompt,
                "mode": "image-to-image",
                "image": init_image_b64,
                "strength": strength,
                "aspect_ratio": aspect_ratio,
                "output_format": output_format,
            }
            
            # Add optional parameters
            if negative_prompt:
                data["negative_prompt"] = negative_prompt
            
            if seed is not None:
                data["seed"] = seed
            
            # Note: SD3 doesn't use traditional cfg_scale and steps parameters
            # These are handled internally by the model
            
            # Make the API request to SD3 endpoint
            url = f"{self.base_url}/v2beta/stable-image/generate/sd3"
            
            # SD3 uses multipart/form-data instead of JSON
            files = {}
            for key, value in data.items():
                if key == "image":
                    # Image data needs to be sent as bytes
                    files[key] = base64.b64decode(value)
                else:
                    files[key] = (None, str(value))
            
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files,
                timeout=120  # SD3 can take longer
            )
            
            if response.status_code != 200:
                error_msg = f"Stability AI SD3 API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # SD3 returns the image directly
            image_data = response.content
            
            return {
                "success": True,
                "results": [{
                    "image_data": image_data,
                    "seed": seed,  # SD3 doesn't return seed in response
                    "finish_reason": "SUCCESS"
                }],
                "prompt": prompt,
                "model": "SD3"
            }
            
        except requests.exceptions.Timeout:
            logger.error("Stability AI SD3 API timeout")
            return {
                "success": False,
                "error": "API request timed out"
            }
        except Exception as e:
            logger.error(f"Stability AI SD3 service error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def image_to_image_legacy(self, 
                             image_path: str, 
                             prompt: str, 
                             negative_prompt: str = None,
                             image_strength: float = 0.35,
                             cfg_scale: float = 7.0,
                             steps: int = 50,
                             seed: int = None) -> Dict[str, Any]:
        """
        Fallback to legacy image-to-image API if SD3 is not available
        """
        try:
            # Use the existing logic but with updated parameters
            init_image_b64 = self.prepare_image_for_api(image_path)
            
            data = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": cfg_scale,
                "image_strength": image_strength,
                "init_image": init_image_b64,
                "samples": 1,
                "steps": steps,
            }
            
            if negative_prompt:
                data["text_prompts"].append({
                    "text": negative_prompt,
                    "weight": -1.0
                })
            
            if seed is not None:
                data["seed"] = seed
            
            # Use legacy endpoint
            url = f"{self.base_url}/v1/generation/stable-diffusion-v1-6/image-to-image"
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"Stability AI Legacy API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            
            # Process the artifacts
            results = []
            for i, artifact in enumerate(response_data.get("artifacts", [])):
                if artifact.get("finish_reason") == "SUCCESS":
                    image_data = base64.b64decode(artifact["base64"])
                    results.append({
                        "image_data": image_data,
                        "seed": artifact.get("seed"),
                        "finish_reason": artifact.get("finish_reason")
                    })
            
            return {
                "success": True,
                "results": results,
                "prompt": prompt,
                "model": "SD1.6"
            }
            
        except Exception as e:
            logger.error(f"Legacy API error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_wedding_venue(self, image_path: str, processing_job):
        """
        Process wedding venue using optimal API based on parameters
        """
        # Get all parameters from the job
        params = processing_job.get_stability_ai_params()
        
        try:
            # Try SD3 first (recommended for realistic images)
            result = self.image_to_image_sd3(
                image_path=image_path,
                prompt=params['prompt'],
                negative_prompt=params['negative_prompt'],
                strength=params['strength'],
                aspect_ratio=params['aspect_ratio'],
                output_format=params['output_format'],
                seed=params['seed']
            )
            
            if result["success"]:
                logger.info(f"Successfully processed with SD3 for job {processing_job.id}")
                return result
                
        except Exception as e:
            logger.warning(f"SD3 failed, falling back to legacy API: {str(e)}")
        
        # Fallback to legacy API
        result = self.image_to_image_legacy(
            image_path=image_path,
            prompt=params['prompt'],
            negative_prompt=params['negative_prompt'],
            image_strength=params['strength'],
            cfg_scale=params['cfg_scale'],
            steps=params['steps'],
            seed=params['seed']
        )
        
        if result["success"]:
            logger.info(f"Successfully processed with legacy API for job {processing_job.id}")
        
        return result
    
    def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance from Stability AI"""
        try:
            url = f"{self.base_url}/v1/user/balance"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get balance: {response.status_code}")
                return {"credits": 0}
                
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return {"credits": 0}


class ImageProcessingService:
    """Service for handling image processing workflows with advanced parameters"""
    
    def __init__(self):
        self.stability_service = StabilityAIService()
    
    def process_wedding_image(self, processing_job):
        """Process a wedding venue image with comprehensive parameters"""
        from .models import ProcessedImage
        from django.utils import timezone
        
        try:
            # Update job status
            processing_job.status = 'processing'
            processing_job.started_at = timezone.now()
            processing_job.save()
            
            user_image = processing_job.user_image
            
            # Process using the new comprehensive system
            result = self.stability_service.process_wedding_venue(
                image_path=user_image.image.path,
                processing_job=processing_job
            )
            
            if result["success"] and result["results"]:
                # Save the processed image
                for img_result in result["results"]:
                    processed_image = ProcessedImage(
                        processing_job=processing_job,
                        stability_seed=img_result.get("seed"),
                        finish_reason=img_result.get("finish_reason")
                    )
                    
                    # Save the image file with wedding context in filename
                    theme_space = f"{processing_job.wedding_theme}_{processing_job.space_type}"
                    model_used = result.get("model", "SD3")
                    filename = f"wedding_{theme_space}_{model_used}_{processing_job.id}_{timezone.now().timestamp()}.png"
                    
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
                # No successful results
                error_msg = result.get('error', 'No images were successfully processed')
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