# wedding_vision/services.py
import io
import base64
import requests
import random
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class StabilityAIService:
    """Service for interacting with Stability AI API"""
    
    @staticmethod
    def image_to_image(venue_image, theme, seed=None):
        """Transform venue image using selected theme"""
        api_key = getattr(settings, "STABILITY_API_KEY", "")
        if not api_key:
            logger.error("STABILITY_API_KEY not found in settings")
            return {"success": False, "error": "API key not configured"}
            
        api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image"
        
        # Generate seed if not provided for reproducibility
        if not seed:
            seed = random.randint(0, 4294967295)
        
        # Prepare the image
        image_bytes = io.BytesIO()
        venue_image.image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        
        # Build the prompt
        prompt = theme.prompt_template
        
        # Prepare the files and data for the request
        files = {
            "init_image": image_bytes.read()
        }
        
        payload = {
            "text_prompts[0][text]": prompt,
            "text_prompts[0][weight]": 1,
            "init_image_mode": "IMAGE_STRENGTH",
            "image_strength": 0.35,  # Preserve some of the original
            "cfg_scale": 7,
            "samples": 1,
            "steps": 30,
            "seed": seed,
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                files=files,
                data=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                # Get image data from response
                image_data = base64.b64decode(data["artifacts"][0]["base64"])
                return {
                    "success": True,
                    "image_data": image_data,
                    "seed": seed
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {response.text}"
                }
        except Exception as e:
            logger.exception("Error calling Stability API")
            return {
                "success": False,
                "error": f"Exception: {str(e)}"
            }
    
    @staticmethod
    def upscale_image(generated_image_id):
        """Upscale a generated image"""
        from .models import GeneratedImage
        
        api_key = getattr(settings, "STABILITY_API_KEY", "")
        if not api_key:
            return {"success": False, "error": "API key not configured"}
            
        api_url = "https://api.stability.ai/v1/generation/esrgan-v1/image-to-image/upscale"
        
        try:
            generated_image = GeneratedImage.objects.get(id=generated_image_id)
            
            # Prepare the image data
            image_bytes = io.BytesIO(generated_image.image_data)
            
            files = {
                "image": image_bytes.read()
            }
            
            data = {
                "width": 2048  # Target width
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            response = requests.post(
                api_url,
                headers=headers,
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                data = response.json()
                upscaled_image_data = base64.b64decode(data["artifacts"][0]["base64"])
                
                # Create an upscaled version of the image
                upscaled_image = GeneratedImage.objects.create(
                    user=generated_image.user,
                    venue_image=generated_image.venue_image,
                    theme=generated_image.theme,
                    image_data=upscaled_image_data,
                    parent_image=generated_image,
                    is_upscaled=True,
                    seed=generated_image.seed
                )
                
                return {
                    "success": True,
                    "upscaled_image_id": upscaled_image.id
                }
            else:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {response.text}"
                }
        except Exception as e:
            logger.exception("Error upscaling image")
            return {
                "success": False,
                "error": str(e)
            }