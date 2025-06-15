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
    """Service for interacting with Stability AI API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'STABILITY_AI_API_KEY', None)
        self.base_url = "https://api.stability.ai"
        self.engine_id = getattr(settings, 'STABILITY_AI_ENGINE', 'stable-diffusion-v1-6')
        
        if not self.api_key:
            raise ValueError("STABILITY_AI_API_KEY must be set in settings")
    
    def _get_headers(self):
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
    
    def prepare_image_for_api(self, image_path: str, max_size: tuple = (1024, 1024)) -> str:
        """
        Prepare image for Stability AI API
        Returns base64 encoded image
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                image_data = buffer.getvalue()
                
                return base64.b64encode(image_data).decode()
        except Exception as e:
            logger.error(f"Error preparing image: {str(e)}")
            raise
    
    def image_to_image(self, 
                      image_path: str, 
                      prompt: str, 
                      negative_prompt: str = None,
                      image_strength: float = 0.35,
                      cfg_scale: float = 7.0,
                      steps: int = 50,
                      seed: int = None) -> Dict[str, Any]:
        """
        Perform image-to-image generation using Stability AI
        """
        try:
            # Prepare the image
            init_image_b64 = self.prepare_image_for_api(image_path)
            
            # Prepare the request data
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
            
            # Make the API request
            url = f"{self.base_url}/v1/generation/{self.engine_id}/image-to-image"
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"Stability AI API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            response_data = response.json()
            
            # Process the artifacts (generated images)
            results = []
            for i, artifact in enumerate(response_data.get("artifacts", [])):
                if artifact.get("finish_reason") == "SUCCESS":
                    image_data = base64.b64decode(artifact["base64"])
                    results.append({
                        "image_data": image_data,
                        "seed": artifact.get("seed"),
                        "finish_reason": artifact.get("finish_reason")
                    })
                else:
                    logger.warning(f"Image generation failed: {artifact.get('finish_reason')}")
            
            return {
                "success": True,
                "results": results,
                "prompt": prompt
            }
            
        except requests.exceptions.Timeout:
            logger.error("Stability AI API timeout")
            return {
                "success": False,
                "error": "API request timed out"
            }
        except Exception as e:
            logger.error(f"Stability AI service error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
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
    """Service for handling image processing workflows"""
    
    def __init__(self):
        self.stability_service = StabilityAIService()
    
    def process_image_with_prompts(self, processing_job):
        """Process a single image with multiple prompts"""
        from .models import ProcessedImage
        from django.utils import timezone
        
        try:
            # Update job status
            processing_job.status = 'processing'
            processing_job.started_at = timezone.now()
            processing_job.save()
            
            user_image = processing_job.user_image
            results = []
            
            # Process each prompt
            for prompt_template in processing_job.prompts.all():
                try:
                    result = self.stability_service.image_to_image(
                        image_path=user_image.image.path,
                        prompt=prompt_template.prompt_text,
                        cfg_scale=processing_job.cfg_scale,
                        steps=processing_job.steps,
                        seed=processing_job.seed
                    )
                    
                    if result["success"] and result["results"]:
                        # Save the processed image
                        for img_result in result["results"]:
                            processed_image = ProcessedImage(
                                processing_job=processing_job,
                                prompt_template=prompt_template,
                                stability_seed=img_result.get("seed"),
                                finish_reason=img_result.get("finish_reason")
                            )
                            
                            # Save the image file
                            filename = f"processed_{processing_job.id}_{prompt_template.id}_{timezone.now().timestamp()}.png"
                            processed_image.processed_image.save(
                                filename,
                                ContentFile(img_result["image_data"]),
                                save=False
                            )
                            processed_image.save()
                            results.append(processed_image)
                            
                except Exception as e:
                    logger.error(f"Error processing prompt {prompt_template.id}: {str(e)}")
                    continue
            
            # Update job status
            if results:
                processing_job.status = 'completed'
            else:
                processing_job.status = 'failed'
                processing_job.error_message = "No images were successfully processed"
            
            processing_job.completed_at = timezone.now()
            processing_job.save()
            
            return results
            
        except Exception as e:
            processing_job.status = 'failed'
            processing_job.error_message = str(e)
            processing_job.completed_at = timezone.now()
            processing_job.save()
            logger.error(f"Error in processing job {processing_job.id}: {str(e)}")
            return []