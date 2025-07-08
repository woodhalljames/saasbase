# wedding_shopping/ai_analysis.py
"""
Enhanced AI Analysis for Wedding Shopping Items using CLIP + YOLO
Uses state-of-the-art computer vision models for accurate item identification
"""

import os
import uuid
import logging
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
from ultralytics import YOLO
import cv2
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Initialize models (cached to avoid reloading)
_clip_model = None
_clip_processor = None
_yolo_model = None

def get_clip_model():
    """Get CLIP model (cached)"""
    global _clip_model, _clip_processor
    
    if _clip_model is None:
        try:
            model_name = getattr(settings, 'CLIP_MODEL_NAME', 'openai/clip-vit-base-patch32')
            _clip_model = CLIPModel.from_pretrained(model_name)
            _clip_processor = CLIPProcessor.from_pretrained(model_name)
            
            # Move to GPU if available
            if torch.cuda.is_available():
                _clip_model = _clip_model.cuda()
                
            logger.info(f"CLIP model {model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            return None, None
    
    return _clip_model, _clip_processor

def get_yolo_model():
    """Get YOLO model (cached)"""
    global _yolo_model
    
    if _yolo_model is None:
        try:
            model_path = getattr(settings, 'YOLO_MODEL_PATH', 'yolov8n.pt')
            _yolo_model = YOLO(model_path)
            logger.info(f"YOLO model {model_path} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            return None
    
    return _yolo_model

def analyze_item_selection(image_path, selection):
    """
    Analyze a selected area of a wedding image using CLIP + YOLO
    
    Args:
        image_path (str): Path to the source image
        selection (dict): Selection coordinates {x, y, width, height}
    
    Returns:
        dict: Analysis results with item information
    """
    try:
        # Crop the selected area
        cropped_image_path = crop_selection(image_path, selection)
        
        if not cropped_image_path:
            return {
                'success': False,
                'error': 'Failed to crop image selection'
            }
        
        # Analyze using YOLO + CLIP
        analysis = analyze_with_models(cropped_image_path)
        
        # Clean up temporary file
        if os.path.exists(cropped_image_path):
            os.remove(cropped_image_path)
        
        return {
            'success': True,
            'name': analysis['name'],
            'description': analysis['description'],
            'category': analysis['category'],
            'ai_description': analysis['ai_description'],
            'confidence': analysis['confidence'],
            'tags': analysis['tags'],
            'detected_objects': analysis.get('detected_objects', []),
            'clip_similarities': analysis.get('clip_similarities', {})
        }
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def crop_selection(image_path, selection):
    """
    Crop the selected area from the image
    
    Args:
        image_path (str): Path to source image
        selection (dict): Selection coordinates
    
    Returns:
        str: Path to cropped image or None if failed
    """
    try:
        with Image.open(image_path) as img:
            # Calculate crop box with bounds checking
            x = max(0, selection['x'])
            y = max(0, selection['y'])
            width = min(selection['width'], img.width - x)
            height = min(selection['height'], img.height - y)
            
            if width <= 0 or height <= 0:
                return None
            
            box = (x, y, x + width, y + height)
            cropped = img.crop(box)
            
            # Ensure minimum size for better analysis
            if cropped.width < 64 or cropped.height < 64:
                # Resize to minimum size while maintaining aspect ratio
                cropped.thumbnail((224, 224), Image.Resampling.LANCZOS)
            
            # Save to temporary file
            temp_filename = f"/tmp/crop_{uuid.uuid4().hex}.jpg"
            cropped.save(temp_filename, 'JPEG', quality=95)
            
            return temp_filename
            
    except Exception as e:
        logger.error(f"Error cropping image: {str(e)}")
        return None

def analyze_with_models(image_path):
    """
    Analyze cropped image using YOLO for detection and CLIP for classification
    
    Args:
        image_path (str): Path to cropped image
    
    Returns:
        dict: Comprehensive analysis results
    """
    try:
        # Load models
        clip_model, clip_processor = get_clip_model()
        yolo_model = get_yolo_model()
        
        if not clip_model or not yolo_model:
            # Fallback to simple analysis if models fail to load
            return analyze_cropped_image_fallback(image_path)
        
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # YOLO Object Detection
        yolo_results = yolo_model(image_path, conf=0.3)
        detected_objects = extract_yolo_objects(yolo_results)
        
        # CLIP Classification for wedding items
        clip_results = classify_with_clip(image, clip_model, clip_processor)
        
        # Combine results for final analysis
        final_analysis = combine_analysis_results(detected_objects, clip_results, image)
        
        return final_analysis
        
    except Exception as e:
        logger.error(f"Error in model analysis: {str(e)}")
        return analyze_cropped_image_fallback(image_path)

def extract_yolo_objects(yolo_results):
    """
    Extract object information from YOLO detection results
    
    Args:
        yolo_results: YOLO detection results
    
    Returns:
        list: List of detected objects with confidence scores
    """
    objects = []
    
    try:
        for result in yolo_results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get class name and confidence
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = yolo_results[0].names[class_id]
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    
                    objects.append({
                        'class': class_name,
                        'confidence': confidence,
                        'bbox': [x1, y1, x2, y2],
                        'area': (x2 - x1) * (y2 - y1)
                    })
        
        # Sort by confidence
        objects.sort(key=lambda x: x['confidence'], reverse=True)
        
    except Exception as e:
        logger.error(f"Error extracting YOLO objects: {e}")
    
    return objects

def classify_with_clip(image, clip_model, clip_processor):
    """
    Use CLIP to classify wedding-related items
    
    Args:
        image: PIL Image
        clip_model: CLIP model
        clip_processor: CLIP processor
    
    Returns:
        dict: Classification results with similarities
    """
    try:
        # Wedding-specific text prompts for CLIP
        wedding_categories = [
            "a wedding chair",
            "a dining table for wedding",
            "wedding centerpiece with flowers",
            "wedding candles and lighting",
            "wedding tablecloth and linens",
            "wedding tableware and plates",
            "wedding cake table",
            "wedding arch or backdrop",
            "wedding decoration",
            "bridal furniture",
            "wedding bar setup",
            "wedding lounge seating",
            "wedding cocktail table",
            "wedding chandelier",
            "wedding floral arrangement",
            "wedding place setting",
            "wedding ceremony decor",
            "wedding reception furniture"
        ]
        
        # Additional specific item prompts
        specific_items = [
            "chiavari chair",
            "round dining table",
            "rectangular table",
            "floral centerpiece",
            "candle arrangement",
            "table runner",
            "charger plate",
            "wine glass",
            "cocktail table",
            "ottoman",
            "sofa",
            "bar cart",
            "chandelier",
            "pendant light",
            "ceremony arch",
            "wedding backdrop"
        ]
        
        all_prompts = wedding_categories + specific_items
        
        # Process image and text
        inputs = clip_processor(
            text=all_prompts,
            images=image,
            return_tensors="pt",
            padding=True
        )
        
        # Move to GPU if available
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Get similarities
        with torch.no_grad():
            outputs = clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
        
        # Get top predictions
        top_indices = torch.topk(probs[0], k=5).indices
        top_probs = torch.topk(probs[0], k=5).values
        
        similarities = {}
        for i, idx in enumerate(top_indices):
            prompt = all_prompts[idx]
            confidence = float(top_probs[i])
            similarities[prompt] = confidence
        
        return {
            'top_category': all_prompts[top_indices[0]],
            'confidence': float(top_probs[0]),
            'similarities': similarities
        }
        
    except Exception as e:
        logger.error(f"Error in CLIP classification: {e}")
        return {
            'top_category': 'wedding item',
            'confidence': 0.5,
            'similarities': {}
        }

def combine_analysis_results(detected_objects, clip_results, image):
    """
    Combine YOLO detection and CLIP classification results
    
    Args:
        detected_objects: List of YOLO detected objects
        clip_results: CLIP classification results
        image: PIL Image
    
    Returns:
        dict: Combined analysis results
    """
    # Get the most confident YOLO detection
    primary_object = detected_objects[0] if detected_objects else None
    
    # Get CLIP's top prediction
    clip_category = clip_results.get('top_category', 'wedding item')
    clip_confidence = clip_results.get('confidence', 0.5)
    
    # Determine final item name and category
    if primary_object and primary_object['confidence'] > 0.6:
        # High confidence YOLO detection
        base_name = primary_object['class']
        yolo_confidence = primary_object['confidence']
        
        # Enhance with CLIP context
        if 'wedding' not in clip_category.lower():
            name = f"Wedding {base_name.title()}"
        else:
            name = clip_category.replace('a ', '').title()
    else:
        # Rely more on CLIP
        name = clip_category.replace('a ', '').title()
        yolo_confidence = 0.3
    
    # Determine category
    category = determine_wedding_category(name, detected_objects, clip_results)
    
    # Generate description
    description = generate_item_description(name, category, detected_objects, clip_results)
    
    # Generate tags
    tags = generate_item_tags(name, category, detected_objects, clip_results)
    
    # Calculate combined confidence
    combined_confidence = (yolo_confidence + clip_confidence) / 2
    
    # Generate AI description
    ai_description = f"Identified as {name.lower()} using computer vision. "
    if primary_object:
        ai_description += f"Object detection confidence: {primary_object['confidence']:.2f}. "
    ai_description += f"Classification confidence: {clip_confidence:.2f}. "
    ai_description += f"Suitable for {category} category."
    
    return {
        'name': name,
        'description': description,
        'category': category,
        'ai_description': ai_description,
        'confidence': combined_confidence,
        'tags': tags,
        'detected_objects': detected_objects,
        'clip_similarities': clip_results.get('similarities', {})
    }

def determine_wedding_category(name, detected_objects, clip_results):
    """
    Determine the wedding category based on analysis results
    
    Args:
        name: Item name
        detected_objects: YOLO results
        clip_results: CLIP results
    
    Returns:
        str: Wedding category
    """
    name_lower = name.lower()
    
    # Category mapping based on item characteristics
    category_keywords = {
        'furniture': ['chair', 'table', 'sofa', 'ottoman', 'bench', 'stool', 'seating'],
        'lighting': ['chandelier', 'candle', 'lamp', 'light', 'sconce', 'lantern'],
        'flowers': ['flower', 'floral', 'bouquet', 'centerpiece', 'arrangement', 'vase'],
        'tableware': ['plate', 'glass', 'cup', 'silverware', 'charger', 'napkin'],
        'textiles': ['tablecloth', 'runner', 'linen', 'fabric', 'draping', 'curtain'],
        'ceremony': ['arch', 'altar', 'aisle', 'backdrop', 'arbor', 'ceremony'],
        'reception': ['bar', 'dance', 'stage', 'dj', 'band', 'reception']
    }
    
    # Check name against keywords
    for category, keywords in category_keywords.items():
        if any(keyword in name_lower for keyword in keywords):
            return category
    
    # Check detected objects
    if detected_objects:
        primary_object = detected_objects[0]['class'].lower()
        for category, keywords in category_keywords.items():
            if any(keyword in primary_object for keyword in keywords):
                return category
    
    # Check CLIP similarities
    clip_similarities = clip_results.get('similarities', {})
    for prompt, confidence in clip_similarities.items():
        if confidence > 0.3:
            prompt_lower = prompt.lower()
            for category, keywords in category_keywords.items():
                if any(keyword in prompt_lower for keyword in keywords):
                    return category
    
    return 'other'

def generate_item_description(name, category, detected_objects, clip_results):
    """
    Generate a natural description of the item
    
    Args:
        name: Item name
        category: Item category
        detected_objects: YOLO results
        clip_results: CLIP results
    
    Returns:
        str: Item description
    """
    descriptions = {
        'furniture': f"This {name.lower()} would be perfect for your wedding venue seating or decoration arrangement.",
        'lighting': f"This {name.lower()} can create beautiful ambient lighting for your wedding ceremony or reception.",
        'flowers': f"This {name.lower()} would make a stunning focal point for your wedding decorations.",
        'tableware': f"This {name.lower()} would complement your wedding table settings beautifully.",
        'textiles': f"This {name.lower()} can add elegance and style to your wedding venue decor.",
        'ceremony': f"This {name.lower()} would create a beautiful backdrop for your wedding ceremony.",
        'reception': f"This {name.lower()} would enhance your wedding reception atmosphere."
    }
    
    base_description = descriptions.get(category, f"This {name.lower()} would be a great addition to your wedding celebration.")
    
    # Add specific details from detection
    if detected_objects and detected_objects[0]['confidence'] > 0.7:
        base_description += f" Our AI detected this with high confidence as a {detected_objects[0]['class']}."
    
    return base_description

def generate_item_tags(name, category, detected_objects, clip_results):
    """
    Generate relevant tags for the item
    
    Args:
        name: Item name
        category: Item category
        detected_objects: YOLO results
        clip_results: CLIP results
    
    Returns:
        list: List of relevant tags
    """
    tags = ['wedding', category]
    
    # Add name-based tags
    name_words = name.lower().split()
    tags.extend([word for word in name_words if len(word) > 2])
    
    # Add object detection tags
    if detected_objects:
        for obj in detected_objects[:3]:  # Top 3 objects
            if obj['confidence'] > 0.5:
                obj_words = obj['class'].lower().split()
                tags.extend([word for word in obj_words if len(word) > 2])
    
    # Add CLIP-based tags
    clip_similarities = clip_results.get('similarities', {})
    for prompt, confidence in clip_similarities.items():
        if confidence > 0.4:
            # Extract meaningful words from prompt
            words = prompt.lower().replace('a ', '').replace('wedding ', '').split()
            tags.extend([word for word in words if len(word) > 3])
    
    # Remove duplicates and limit
    tags = list(set(tags))[:10]
    
    return tags

def analyze_cropped_image_fallback(image_path):
    """
    Fallback analysis when advanced models fail
    
    Args:
        image_path (str): Path to cropped image
    
    Returns:
        dict: Basic analysis results
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            aspect_ratio = width / height
        
        # Simple heuristics for demo purposes
        if aspect_ratio > 2:
            category = 'furniture'
            name = 'Wedding Table'
            description = 'Long furniture piece, likely a dining table or bench for your wedding'
            tags = ['furniture', 'table', 'seating', 'wedding']
        elif aspect_ratio < 0.5:
            category = 'flowers'
            name = 'Wedding Centerpiece'
            description = 'Tall decorative item, possibly a vase, candle, or floral arrangement'
            tags = ['decor', 'centerpiece', 'vase', 'wedding']
        else:
            category = 'other'
            name = 'Wedding Decoration'
            description = 'Wedding decoration or furniture item'
            tags = ['wedding', 'decor']
        
        return {
            'name': name,
            'description': description,
            'category': category,
            'ai_description': f"Basic analysis identified this as {name.lower()}. Advanced AI models unavailable.",
            'confidence': 0.4,
            'tags': tags,
            'detected_objects': [],
            'clip_similarities': {}
        }
        
    except Exception as e:
        logger.error(f"Error in fallback analysis: {str(e)}")
        return {
            'name': 'Wedding Item',
            'description': 'Could not analyze the selected area',
            'category': 'other',
            'ai_description': 'Analysis failed',
            'confidence': 0.0,
            'tags': ['wedding']
        }

# Model initialization and caching
def warm_up_models():
    """
    Warm up models for faster inference
    Should be called during Django startup or in a management command
    """
    try:
        logger.info("Warming up AI models...")
        
        # Load models
        clip_model, clip_processor = get_clip_model()
        yolo_model = get_yolo_model()
        
        if clip_model and clip_processor:
            # Create a dummy image for warm-up
            dummy_image = Image.new('RGB', (224, 224), color='white')
            dummy_text = ["a chair"]
            
            inputs = clip_processor(
                text=dummy_text,
                images=dummy_image,
                return_tensors="pt",
                padding=True
            )
            
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                _ = clip_model(**inputs)
            
            logger.info("CLIP model warmed up successfully")
        
        if yolo_model:
            # Warm up YOLO with dummy image
            dummy_array = np.zeros((224, 224, 3), dtype=np.uint8)
            _ = yolo_model(dummy_array, verbose=False)
            logger.info("YOLO model warmed up successfully")
        
        logger.info("AI models warm-up completed")
        
    except Exception as e:
        logger.error(f"Error warming up models: {e}")

# Settings for model configuration
def get_model_info():
    """
    Get information about loaded models
    
    Returns:
        dict: Model information
    """
    info = {
        'clip_model_loaded': _clip_model is not None,
        'yolo_model_loaded': _yolo_model is not None,
        'cuda_available': torch.cuda.is_available(),
        'models_ready': _clip_model is not None and _yolo_model is not None
    }
    
    if torch.cuda.is_available():
        info['gpu_name'] = torch.cuda.get_device_name(0)
        info['gpu_memory'] = torch.cuda.get_device_properties(0).total_memory
    
    return info