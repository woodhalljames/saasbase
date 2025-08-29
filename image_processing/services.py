# image_processing/services.py - SIMPLIFIED with fixed parameters

import io
import base64
import requests
import logging
from typing import List, Dict, Any, Optional, Tuple
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageEnhance, ImageFilter
from django.core.cache import cache
import hashlib

logger = logging.getLogger(__name__)


class WeddingImageAnalyzer:
    """Simple image analysis for wedding venue suitability"""
    
    @staticmethod
    def analyze_venue_image(image_path: str) -> Dict[str, Any]:
        """Basic image analysis for venue photos"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                aspect_ratio = width / height
                
                # Basic suitability checks
                warnings = []
                
                # Check minimum resolution
                if width < 512 or height < 512:
                    warnings.append("Low resolution - may affect transformation quality")
                
                # Check extreme aspect ratios
                if aspect_ratio > 3.0 or aspect_ratio < 0.33:
                    warnings.append("Extreme aspect ratio - may crop unexpectedly")
                
                return {
                    'is_suitable': True,
                    'warnings': warnings,
                    'resolution': f"{width}x{height}",
                    'aspect_ratio': round(aspect_ratio, 2)
                }
                
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return {
                'is_suitable': False,
                'error': f'Image analysis failed: {str(e)}'
            }


class StabilityAIService:
    """SIMPLIFIED service for Stability AI with FIXED parameters"""
    
    # FIXED model configuration - no more dynamic optimization
    FIXED_CONFIG = {
        'model': 'sd3.5-large',
        'max_size': 1024,
        'timeout': 300,
        # FIXED PARAMETERS - NO MORE CUSTOMIZATION
        'strength': 0.70,      # Fixed at 70%
        'cfg_scale': 7.5,      # Standard CFG
        'steps': 30,           # Fixed at 30 steps
        'output_format': 'png'
    }
    
    def __init__(self):
        self.api_key = getattr(settings, 'STABILITY_API_KEY', None)
        self.base_url = "https://api.stability.ai"
        
        if not self.api_key:
            raise ValueError("STABILITY_API_KEY must be set in settings")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": "WeddingVenueApp/1.0"
        }
    
    def _optimize_image_for_processing(self, image_path: str) -> Tuple[bytes, Dict[str, Any]]:
        """Optimize image for AI processing - PRESERVE ORIGINAL DIMENSIONS when possible"""
        
        with Image.open(image_path) as img:
            original_size = img.size
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
                logger.info(f"Converted image from {img.mode} to RGB")
            
            # Calculate optimal dimensions - PRESERVE ORIGINAL when possible
            width, height = img.size
            max_size = self.FIXED_CONFIG['max_size']
            
            # Only resize if image is significantly larger than max_size
            if max(width, height) > max_size:
                # Maintain aspect ratio while fitting within max_size
                ratio = max_size / max(width, height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                # Ensure dimensions are divisible by 8 (AI model requirement)
                new_width = (new_width // 8) * 8
                new_height = (new_height // 8) * 8
                
                # Ensure minimum size
                if new_width < 512:
                    new_width = 512
                if new_height < 512:
                    new_height = 512
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {original_size} to {img.size}")
            else:
                # Keep original size but ensure divisibility by 8
                new_width = (width // 8) * 8
                new_height = (height // 8) * 8
                
                # Only resize if adjustment is significant (more than 16px difference)
                if abs(width - new_width) > 16 or abs(height - new_height) > 16:
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    logger.info(f"Minor resize for AI compatibility: {original_size} to {img.size}")
                else:
                    logger.info(f"Preserving original dimensions: {original_size}")
            
            # SIMPLIFIED: Minimal enhancement for venue images
            if getattr(settings, 'ENHANCE_VENUE_IMAGES', True):
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.05)  # Very slight contrast boost
            
            # Convert to PNG bytes
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG', optimize=True)
            img_buffer.seek(0)
            image_bytes = img_buffer.getvalue()
            
            metadata = {
                'original_size': original_size,
                'processed_size': img.size,
                'file_size': len(image_bytes),
                'aspect_ratio': img.size[0] / img.size[1]
            }
            
            return image_bytes, metadata
    
    def image_to_image_wedding(self, 
                              image_path: str, 
                              prompt: str, 
                              negative_prompt: str = None,
                              seed: int = None) -> Dict[str, Any]:
        """
        SIMPLIFIED image-to-image generation with FIXED parameters
        """
        try:
            # Use FIXED parameters - no more customization
            config = self.FIXED_CONFIG
            strength = config['strength']
            cfg_scale = config['cfg_scale']
            steps = config['steps']
            output_format = config['output_format']
            
            logger.info(f"Starting SD3.5 generation with FIXED params:")
            logger.info(f"  - Strength: {strength} (FIXED)")
            logger.info(f"  - CFG Scale: {cfg_scale} (FIXED)")
            logger.info(f"  - Steps: {steps} (FIXED)")
            logger.info(f"  - Prompt length: {len(prompt)} chars")
            
            # Optimize image
            image_bytes, img_metadata = self._optimize_image_for_processing(image_path)
            
            logger.info(f"Image optimized: {img_metadata['processed_size']}, "
                       f"{img_metadata['file_size']} bytes")
            
            # Prepare API request with FIXED parameters
            files = {
                'image': ('image.png', image_bytes, 'image/png'),
            }
            
            data = {
                'prompt': prompt[:2000],  # Ensure prompt isn't too long
                'strength': str(strength),      # FIXED
                'output_format': output_format, # FIXED
                'cfg_scale': str(cfg_scale),    # FIXED
                'steps': str(steps),            # FIXED
            }
            
            # Add optional parameters
            if negative_prompt:
                data["negative_prompt"] = negative_prompt[:1000]
            
            if seed is not None:
                data["seed"] = str(seed)
            
            # Use SD3.5 Large endpoint
            url = f"{self.base_url}/v2beta/stable-image/generate/ultra"
            
            logger.info(f"Making API request to {url}")
            logger.info(f"FIXED parameters confirmed: strength={strength}, cfg={cfg_scale}, steps={steps}")
            
            # Make API request with retry logic
            response = self._make_api_request_with_retry(url, files, data, config['timeout'])
            
            if not response:
                raise Exception("API request failed after retries")
            
            # Process response
            result = self._process_api_response(response, config['model'], prompt)
            result['image_metadata'] = img_metadata
            result['parameters'] = {
                'strength': strength,
                'cfg_scale': cfg_scale,
                'steps': steps,
                'model': config['model']
            }
            
            return result
            
        except Exception as e:
            logger.error(f"SD3.5 service error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "model": config['model']
            }
    
    def _make_api_request_with_retry(self, url: str, files: Dict, data: Dict, timeout: int, max_retries: int = 2):
        """Make API request with retry logic - SIMPLIFIED"""
        headers = self._get_headers()
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"API request attempt {attempt + 1}/{max_retries + 1}")
                response = requests.post(
                    url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    if attempt < max_retries:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                        import time
                        time.sleep(wait_time)
                        continue
                elif response.status_code >= 500:  # Server error
                    if attempt < max_retries:
                        logger.warning(f"Server error {response.status_code}, retrying...")
                        continue
                
                # Log error and break on non-retryable errors
                logger.error(f"API error {response.status_code}: {response.text}")
                break
                
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    logger.warning("Request timeout, retrying...")
                    continue
                else:
                    logger.error("Final timeout after retries")
            except Exception as e:
                logger.error(f"Request failed: {str(e)}")
                break
        
        return None
    
    def _process_api_response(self, response, model: str, prompt: str) -> Dict[str, Any]:
        """Process API response and extract image data"""
        content_type = response.headers.get('content-type', '')
        
        if 'application/json' in content_type:
            try:
                json_response = response.json()
                
                # Check for errors
                if 'errors' in json_response:
                    raise Exception(f"API error: {json_response['errors']}")
                
                # Extract image data
                if 'image' in json_response:
                    image_data = base64.b64decode(json_response['image'])
                elif 'artifacts' in json_response and json_response['artifacts']:
                    # SDXL format fallback
                    artifact = json_response['artifacts'][0]
                    image_data = base64.b64decode(artifact['base64'])
                else:
                    raise Exception("No image data in JSON response")
                    
            except Exception as e:
                raise Exception(f"Failed to parse JSON response: {str(e)}")
        else:
            # Binary image response
            image_data = response.content
        
        # Extract metadata
        response_seed = response.headers.get("seed")
        finish_reason = response.headers.get("finish-reason", "SUCCESS")
        
        logger.info(f"Successfully generated image: {len(image_data)} bytes")
        
        return {
            "success": True,
            "results": [{
                "image_data": image_data,
                "seed": response_seed,
                "finish_reason": finish_reason
            }],
            "prompt": prompt,
            "model": model
        }
    
    def process_wedding_venue(self, image_path: str, processing_job) -> Dict[str, Any]:
        """Process wedding venue with FIXED settings"""
        
        # SIMPLIFIED: Always use fixed parameters
        logger.info(f"Processing wedding venue for job {processing_job.id}")
        logger.info(f"Theme: {processing_job.wedding_theme}, Space: {processing_job.space_type}")
        logger.info(f"Using FIXED params: strength=70%, steps=30, cfg=7.5")
        
        result = self.image_to_image_wedding(
            image_path=image_path,
            prompt=processing_job.generated_prompt,
            negative_prompt=processing_job.negative_prompt,
            seed=processing_job.seed
        )
        
        if result["success"]:
            logger.info(f"Successfully processed venue with fixed parameters")
        else:
            logger.error(f"Processing failed: {result.get('error')}")
        
        return result


class ImageProcessingService:
    """SIMPLIFIED service for wedding venue processing"""
    
    def __init__(self):
        self.stability_service = StabilityAIService()
        self.analyzer = WeddingImageAnalyzer()
    
    def process_wedding_image(self, processing_job) -> bool:
        """Process wedding venue image - SIMPLIFIED version"""
        from .models import ProcessedImage
        from django.utils import timezone
        
        try:
            # Update job status
            processing_job.status = 'processing'
            processing_job.started_at = timezone.now()
            processing_job.save()
            
            user_image = processing_job.user_image
            
            logger.info(f"Starting SIMPLIFIED processing for job {processing_job.id}")
            logger.info(f"Theme: {processing_job.wedding_theme}, Space: {processing_job.space_type}")
            logger.info(f"FIXED: strength=70%, steps=30, cfg=7.5")
            
            # Basic image analysis
            analysis = self.analyzer.analyze_venue_image(user_image.image.path)
            if not analysis.get('is_suitable', True):
                raise Exception(f"Image not suitable: {analysis.get('error', 'Unknown issue')}")
            
            # Log any warnings
            for warning in analysis.get('warnings', []):
                logger.warning(f"Image analysis: {warning}")
            
            # Process with Stability AI using FIXED parameters
            result = self.stability_service.process_wedding_venue(
                image_path=user_image.image.path,
                processing_job=processing_job
            )
            
            if result["success"] and result.get("results"):
                # Save processed results
                saved_images = self._save_processed_results(processing_job, result)
                
                if saved_images:
                    # Update job to completed
                    processing_job.status = 'completed'
                    processing_job.completed_at = timezone.now()
                    processing_job.save()
                    
                    logger.info(f"Successfully completed job {processing_job.id}")
                    logger.info(f"Saved {len(saved_images)} processed images")
                    
                    # Simple result caching
                    self._cache_processing_result(processing_job, result)
                    
                    return True
                else:
                    raise Exception("Failed to save processed images")
            else:
                raise Exception(result.get('error', 'Processing failed without specific error'))
                
        except Exception as exc:
            logger.error(f"Processing job {processing_job.id} failed: {str(exc)}")
            
            # Update job status
            processing_job.status = 'failed'
            processing_job.error_message = str(exc)
            processing_job.completed_at = timezone.now()
            processing_job.save()
            
            return False
    
    def _save_processed_results(self, processing_job, result) -> List:
        """Save processed images from API result"""
        from .models import ProcessedImage
        from django.utils import timezone
        
        saved_images = []
        
        for i, img_result in enumerate(result["results"]):
            try:
                processed_image = ProcessedImage(
                    processing_job=processing_job,
                    stability_seed=img_result.get("seed"),
                    finish_reason=img_result.get("finish_reason")
                )
                
                # Generate descriptive filename
                theme = processing_job.wedding_theme or 'unknown'
                space = processing_job.space_type or 'space'
                timestamp = int(timezone.now().timestamp())
                model = result.get('model', 'sd35').replace('.', '_')
                
                filename = f"wedding_{theme}_{space}_{model}_fixed_{processing_job.id}_{timestamp}_{i}.png"
                
                processed_image.processed_image.save(
                    filename,
                    ContentFile(img_result["image_data"]),
                    save=False
                )
                processed_image.save()
                
                saved_images.append(processed_image)
                logger.info(f"Saved processed image: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to save processed image {i}: {str(e)}")
        
        return saved_images
    
    def _cache_processing_result(self, processing_job, result):
        """Simple caching for processing results"""
        try:
            # Create cache key based on core job parameters
            cache_key = self._generate_cache_key(processing_job)
            
            # Cache minimal metadata
            cache_data = {
                'success': result['success'],
                'model': result.get('model'),
                'fixed_parameters': self.stability_service.FIXED_CONFIG,
                'job_id': processing_job.id,
                'timestamp': processing_job.completed_at.isoformat()
            }
            
            # Cache for 24 hours
            cache.set(cache_key, cache_data, 60 * 60 * 24)
            logger.info(f"Cached result for job {processing_job.id}")
            
        except Exception as e:
            logger.warning(f"Failed to cache result for job {processing_job.id}: {str(e)}")
    
    def _generate_cache_key(self, processing_job) -> str:
        """Generate cache key for processing job - SIMPLIFIED"""
        # Create key based on core parameters only
        key_data = f"{processing_job.user_image.id}_{processing_job.wedding_theme}_{processing_job.space_type}_fixed"
        return f"wedding_processing_fixed_{hashlib.md5(key_data.encode()).hexdigest()}"