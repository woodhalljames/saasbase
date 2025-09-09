# image_processing/services.py - Modern Gemini 2.5 Flash Image Preview API

import logging
from PIL import Image as PILImage
from io import BytesIO
from django.conf import settings

logger = logging.getLogger(__name__)

class GeminiImageService:
    """
    Simplified service for Gemini 2.5 Flash Image Preview.
    Text + Image → Image generation with real-time processing.
    """
    
    def __init__(self):
        """Initialize Gemini client"""
        try:
            from google import genai
            self.genai = genai
            
            # Get API key from settings
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if not api_key:
                raise ValueError("GEMINI_API_KEY not configured in settings")
            
            # Initialize the client with API key
            self.client = genai.Client(api_key=api_key)
            # Try the correct model name format
            self.model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
            
            logger.info(f"Gemini service initialized with model: {self.model}")
            
        except ImportError as e:
            raise ImportError("google-genai library not installed. Run: pip install google-genai") from e
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {str(e)}")
            raise
    
    def transform_venue_image(self, image_data, prompt):
        """
        Transform a wedding venue image using Gemini 2.5 Flash.
        
        Args:
            image_data: Raw image bytes
            prompt: Text prompt for transformation
            
        Returns:
            dict: {'success': bool, 'image_data': bytes, 'error': str}
        """
        try:
            # Convert image bytes to PIL Image
            input_image = PILImage.open(BytesIO(image_data))
            
            # Ensure image is in supported format
            if input_image.mode in ('RGBA', 'LA', 'P'):
                # Convert to RGB for better compatibility
                background = PILImage.new('RGB', input_image.size, (255, 255, 255))
                if input_image.mode == 'P':
                    input_image = input_image.convert('RGBA')
                if input_image.mode == 'RGBA':
                    background.paste(input_image, mask=input_image.split()[-1])
                    input_image = background
                else:
                    input_image = input_image.convert('RGB')
            
            logger.info(f"Generating wedding venue transformation with Gemini")
            logger.debug(f"Prompt: {prompt[:100]}...")
            
            # Generate content with Gemini 2.5 Flash
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, input_image],
                config=self.genai.types.GenerateContentConfig(
                    temperature=0.55,  # Balanced creativity for wedding venues
                    candidate_count=1,
                    max_output_tokens=2048
                )
            )
            
            # Extract generated image from response
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]
            
            if image_parts:
                generated_image_data = image_parts[0]
                logger.info(f"Successfully generated venue transformation")
                
                return {
                    'success': True,
                    'image_data': generated_image_data,
                    'model': self.model,
                    'finish_reason': getattr(response.candidates[0], 'finish_reason', 'STOP')
                }
            else:
                # Check for text response (might contain error info)
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
            logger.error(f"Error in venue transformation: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def test_connection(self):
        """Test Gemini API connectivity with a simple venue transformation"""
        try:
            # Create a simple test image
            test_image = PILImage.new('RGB', (512, 512), color='lightgray')
            test_buffer = BytesIO()
            test_image.save(test_buffer, format='JPEG', quality=85)
            test_image_data = test_buffer.getvalue()
            
            # Test prompt
            test_prompt = "Transform this space into an elegant wedding ceremony area with white flowers and romantic lighting."
            
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