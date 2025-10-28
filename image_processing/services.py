# image_processing/services.py - Simple multi-image support for Gemini 2.5 Flash

import logging
from PIL import Image as PILImage
from io import BytesIO
from django.conf import settings

logger = logging.getLogger(__name__)

class GeminiImageService:
    """
    Simple service for Gemini 2.5 Flash Image Preview.
    Text + Images → Image generation with real-time processing.
    """
    
    def __init__(self):
        """Initialize Gemini client"""
        try:
            from google import genai
            self.genai = genai
            
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if not api_key:
                raise ValueError("GEMINI_API_KEY not configured in settings")
            
            self.client = genai.Client(api_key=api_key)
            self.model = getattr(settings, 'GEMINI_MODEL')
            
            logger.info(f"Gemini service initialized with model: {self.model}")
            
        except ImportError as e:
            raise ImportError("google-genai library not installed. Run: pip install google-genai") from e
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {str(e)}")
            raise
    
    def transform_with_multiple_images(self, image_data_list, prompt):
        """
        Transform using 1-5 input images.
        
        Args:
            image_data_list: List of raw image bytes [image1_data, image2_data, ...]
            prompt: Text prompt for transformation
            
        Returns:
            dict: {'success': bool, 'image_data': bytes, 'error': str}
        """
        try:
            # Convert all images to PIL and ensure RGB
            input_images = []
            for idx, img_data in enumerate(image_data_list):
                img = PILImage.open(BytesIO(img_data))
                
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = PILImage.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert('RGB')
                
                input_images.append(img)
                logger.info(f"Prepared input image {idx + 1}: {img.size}, mode: {img.mode}")
            
            logger.info(f"Generating with {len(input_images)} input image(s)")
            logger.debug(f"Prompt: {prompt[:100]}...")
            
            # Build contents: prompt + all images
            contents = [prompt] + input_images
            
            # Generate content
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=self.genai.types.GenerateContentConfig(
                    candidate_count=1,
                    max_output_tokens=2048
                )
            )
            
            # Extract generated image
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]
            
            if image_parts:
                generated_image_data = image_parts[0]
                logger.info(f"Successfully generated image with {len(input_images)} inputs")
                
                return {
                    'success': True,
                    'image_data': generated_image_data,
                    'model': self.model,
                    'finish_reason': getattr(response.candidates[0], 'finish_reason', 'STOP')
                }
            else:
                text_parts = [
                    part.text
                    for part in response.candidates[0].content.parts
                    if part.text
                ]
                
                error_msg = f"No image generated. Response: {' '.join(text_parts[:2])}" if text_parts else "No image generated"
                logger.error(error_msg)
                
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            error_msg = f"Gemini API error: {str(e)}"
            logger.error(f"Error in image generation: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def transform_venue_image(self, image_data, prompt):
        """
        Legacy single-image method (backward compatible).
        
        Args:
            image_data: Raw image bytes
            prompt: Text prompt for transformation
            
        Returns:
            dict: {'success': bool, 'image_data': bytes, 'error': str}
        """
        return self.transform_with_multiple_images([image_data], prompt)
    
    def test_connection(self):
        """Test Gemini API connectivity"""
        try:
            test_image = PILImage.new('RGB', (512, 512), color='lightgray')
            test_buffer = BytesIO()
            test_image.save(test_buffer, format='JPEG', quality=85)
            test_image_data = test_buffer.getvalue()
            
            test_prompt = "Transform this space into an elegant wedding venue."
            
            result = self.transform_venue_image(test_image_data, test_prompt)
            
            return {
                'success': result['success'],
                'model': self.model,
                'error': result.get('error'),
                'test_image_size': len(test_image_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection test failed: {str(e)}'
            }


def test_gemini_service():
    """Test function for Gemini service connectivity"""
    try:
        service = GeminiImageService()
        return service.test_connection()
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }