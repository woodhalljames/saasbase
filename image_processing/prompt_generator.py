# image_processing/prompt_generator.py
"""
Advanced prompt generation system for realistic wedding venue transformations
Utilizes Stability AI SD3 parameters for professional results
"""

class WeddingPromptGenerator:
    """Generate comprehensive prompts for wedding venue transformations"""
    
    # Base style descriptions with lighting and atmosphere details
    THEME_STYLES = {
        'rustic': {
            'description': 'rustic farmhouse wedding style with warm wooden elements, vintage mason jars, burlap table runners, string lights, wildflower bouquets, antique furniture, weathered wood signs, cozy intimate lighting',
            'lighting': 'warm golden hour lighting, soft string lights, candles, natural warm tones',
            'colors': 'warm earth tones, cream, sage green, dusty rose, natural wood',
            'textures': 'weathered wood, burlap, lace, natural fabrics, vintage metals'
        },
        'modern': {
            'description': 'contemporary minimalist wedding with clean geometric lines, sleek furniture, monochromatic color palette, modern floral arrangements, architectural lighting, sophisticated elegance',
            'lighting': 'clean architectural lighting, LED strips, spotlights, modern chandeliers',
            'colors': 'white, black, grey, metallic accents, monochromatic palette',
            'textures': 'smooth surfaces, glass, metal, silk, modern fabrics'
        },
        'vintage': {
            'description': 'romantic vintage wedding with antique lace, classic roses, ornate candelabras, vintage china, pearl details, old-world charm, soft romantic lighting',
            'lighting': 'soft romantic lighting, vintage chandeliers, candles, warm ambient glow',
            'colors': 'blush pink, ivory, gold, dusty blue, antique bronze',
            'textures': 'vintage lace, silk, velvet, ornate metals, delicate fabrics'
        },
        'bohemian': {
            'description': 'free-spirited boho wedding with macrame hangings, colorful textiles, eclectic mix of patterns, pampas grass, dreamcatchers, floor cushions, natural elements',
            'lighting': 'warm ambient lighting, lanterns, fairy lights, natural sunlight',
            'colors': 'terracotta, sage, mustard, deep jewel tones, earth colors',
            'textures': 'woven textiles, macrame, natural fibers, mixed patterns'
        },
        'classic': {
            'description': 'timeless traditional wedding with elegant white flowers, formal table settings, classic drapery, crystal chandeliers, refined luxury, sophisticated grandeur',
            'lighting': 'crystal chandeliers, elegant uplighting, classic warm lighting',
            'colors': 'white, ivory, gold, champagne, classic neutrals',
            'textures': 'silk, satin, crystal, fine china, elegant fabrics'
        },
        'garden': {
            'description': 'natural garden wedding with abundant fresh flowers, greenery garlands, natural wood, botanical elements, organic arrangements, outdoor garden party feel',
            'lighting': 'natural daylight, garden string lights, soft outdoor lighting',
            'colors': 'green, white, soft pastels, natural flower colors',
            'textures': 'natural wood, fresh flowers, organic materials, garden elements'
        },
        'beach': {
            'description': 'coastal beach wedding with driftwood, seashells, flowing fabrics, nautical elements, ocean-inspired colors, breezy natural materials',
            'lighting': 'natural beach lighting, lanterns, soft coastal ambiance',
            'colors': 'ocean blue, sandy beige, coral, seafoam, natural coastal tones',
            'textures': 'weathered wood, flowing fabrics, natural beach materials'
        },
        'industrial': {
            'description': 'urban industrial wedding with exposed brick, metal fixtures, Edison bulb lighting, concrete elements, modern urban aesthetic, raw materials',
            'lighting': 'Edison bulbs, industrial fixtures, warm urban lighting',
            'colors': 'grey, black, copper, warm metallics, urban neutrals',
            'textures': 'exposed brick, metal, concrete, industrial materials'
        }
    }
    
    # Space-specific considerations
    SPACE_DETAILS = {
        'indoor_ceremony': {
            'focus': 'ceremony aisle, altar area, seating arrangement',
            'elements': 'wedding arch, aisle petals, ceremony chairs, altar decorations',
            'atmosphere': 'intimate sacred space, focused lighting on altar'
        },
        'outdoor_ceremony': {
            'focus': 'natural backdrop, outdoor seating, ceremony arch',
            'elements': 'outdoor wedding arch, natural landscaping, ceremony seating',
            'atmosphere': 'natural outdoor setting, harmony with landscape'
        },
        'reception_hall': {
            'focus': 'dining tables, dance floor, entertainment area',
            'elements': 'round dining tables, centerpieces, dance floor, DJ area',
            'atmosphere': 'celebration space, party lighting, festive mood'
        },
        'garden': {
            'focus': 'natural garden setting, outdoor dining',
            'elements': 'garden pathways, natural landscaping, outdoor furniture',
            'atmosphere': 'natural garden party, organic outdoor celebration'
        },
        'beach': {
            'focus': 'oceanview, beach setting, coastal elements',
            'elements': 'beach chairs, coastal decorations, ocean backdrop',
            'atmosphere': 'coastal celebration, ocean breeze, natural beach setting'
        },
        'barn': {
            'focus': 'rustic barn interior, wooden beams, country setting',
            'elements': 'wooden beams, barn doors, country decorations',
            'atmosphere': 'rustic country celebration, barn charm'
        },
        'ballroom': {
            'focus': 'elegant ballroom, formal dining, grand space',
            'elements': 'elegant tables, ballroom lighting, formal decorations',
            'atmosphere': 'grand formal celebration, elegant sophistication'
        },
        'rooftop': {
            'focus': 'city views, urban setting, skyline backdrop',
            'elements': 'rooftop furniture, city views, urban decorations',
            'atmosphere': 'urban celebration, city lights, elevated setting'
        }
    }
    
    @classmethod
    def generate_comprehensive_prompt(cls, wedding_theme, space_type, additional_details=None):
        """Generate a comprehensive prompt for Stability AI SD3"""
        
        theme_data = cls.THEME_STYLES.get(wedding_theme, cls.THEME_STYLES['classic'])
        space_data = cls.SPACE_DETAILS.get(space_type, cls.SPACE_DETAILS['reception_hall'])
        
        # Main prompt construction
        prompt_parts = [
            # Quality and style indicators
            "professional wedding photography, high resolution, photorealistic, detailed",
            
            # Space description
            f"Transform this {space_type.replace('_', ' ')} into a beautiful wedding venue,",
            
            # Theme application
            f"decorated in {wedding_theme} wedding style:",
            theme_data['description'],
            
            # Space-specific elements
            f"Focus on {space_data['focus']},",
            f"include {space_data['elements']},",
            
            # Lighting description
            f"Lighting: {theme_data['lighting']},",
            
            # Color palette
            f"Color palette: {theme_data['colors']},",
            
            # Atmosphere
            f"Atmosphere: {space_data['atmosphere']},",
            
            # Quality descriptors
            "elegant wedding setup, professionally decorated, realistic wedding venue transformation,",
            "maintain original architecture, enhance with wedding decorations,",
            "wedding reception ready, celebration space, romantic ambiance"
        ]
        
        if additional_details:
            prompt_parts.append(additional_details)
        
        main_prompt = " ".join(prompt_parts)
        
        # Negative prompt to avoid unwanted elements
        negative_prompt = cls.generate_negative_prompt()
        
        return {
            'prompt': main_prompt,
            'negative_prompt': negative_prompt,
            'recommended_params': cls.get_recommended_parameters(wedding_theme, space_type)
        }
    
    @classmethod
    def generate_negative_prompt(cls):
        """Generate negative prompt to avoid unwanted elements"""
        negative_elements = [
            # Quality issues
            "blurry, low quality, pixelated, distorted, artifacts",
            
            # Unwanted content
            "people, faces, crowd, guests, bride, groom",
            "text, watermark, signature, logo",
            
            # Bad lighting/atmosphere
            "dark, dim, poor lighting, harsh shadows",
            "cluttered, messy, disorganized, chaotic",
            
            # Technical issues
            "oversaturated, undersaturated, noise, grain",
            "deformed, malformed, unrealistic proportions",
            
            # Unwanted styles
            "cartoon, anime, painting, sketch, drawing",
            "gothic, scary, halloween, inappropriate themes"
        ]
        
        return ", ".join(negative_elements)
    
    @classmethod
    def get_recommended_parameters(cls, wedding_theme, space_type):
        """Get recommended Stability AI parameters for wedding venue generation"""
        
        # Base parameters optimized for realistic wedding venues
        base_params = {
            'aspect_ratio': '16:9',  # Good for venue photography
            'cfg_scale': 7.0,        # Balanced adherence to prompt
            'steps': 50,             # Good quality/speed balance
            'output_format': 'png',   # High quality output
            'mode': 'image-to-image',
            'strength': 0.35,        # Preserve original architecture while adding decorations
        }
        
        # Theme-specific adjustments
        theme_adjustments = {
            'modern': {'cfg_scale': 8.0, 'strength': 0.4},  # More precise for clean lines
            'vintage': {'cfg_scale': 6.5, 'strength': 0.3}, # Softer for romantic feel
            'industrial': {'cfg_scale': 7.5, 'strength': 0.4}, # Precise for industrial elements
            'bohemian': {'cfg_scale': 6.0, 'strength': 0.3},  # More organic/flowing
        }
        
        # Space-specific adjustments
        space_adjustments = {
            'outdoor_ceremony': {'strength': 0.25},  # Preserve natural setting more
            'ballroom': {'cfg_scale': 8.0},         # More formal precision
            'garden': {'strength': 0.25},           # Preserve natural elements
            'beach': {'strength': 0.3},             # Preserve coastal setting
        }
        
        # Apply adjustments
        final_params = base_params.copy()
        
        if wedding_theme in theme_adjustments:
            final_params.update(theme_adjustments[wedding_theme])
            
        if space_type in space_adjustments:
            final_params.update(space_adjustments[space_type])
        
        return final_params
    
    @classmethod
    def generate_variation_prompts(cls, wedding_theme, space_type, base_prompt_data):
        """Generate prompt variations for different aspects of the same venue"""
        
        variations = []
        
        # Variation 1: Focus on lighting
        lighting_prompt = base_prompt_data['prompt'] + f", emphasis on {cls.THEME_STYLES[wedding_theme]['lighting']}, dramatic lighting effects, ambient mood lighting"
        
        # Variation 2: Focus on details
        details_prompt = base_prompt_data['prompt'] + f", close-up details of {cls.THEME_STYLES[wedding_theme]['textures']}, intricate decorative elements, fine details"
        
        # Variation 3: Wide angle view
        wide_prompt = base_prompt_data['prompt'] + ", wide angle view, full venue overview, comprehensive wedding setup, spacious layout"
        
        variations = [
            {
                'name': 'Lighting Focus',
                'prompt': lighting_prompt,
                'negative_prompt': base_prompt_data['negative_prompt'],
                'params': {**base_prompt_data['recommended_params'], 'cfg_scale': 7.5}
            },
            {
                'name': 'Detail Focus', 
                'prompt': details_prompt,
                'negative_prompt': base_prompt_data['negative_prompt'],
                'params': {**base_prompt_data['recommended_params'], 'strength': 0.4}
            },
            {
                'name': 'Wide View',
                'prompt': wide_prompt,
                'negative_prompt': base_prompt_data['negative_prompt'],
                'params': {**base_prompt_data['recommended_params'], 'aspect_ratio': '21:9'}
            }
        ]
        
        return variations