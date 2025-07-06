"""
Advanced prompt generation system for realistic wedding venue transformations
Optimized for Stability AI SD3 Turbo for faster processing
"""

class WeddingPromptGenerator:
    """Generate comprehensive prompts for wedding venue transformations optimized for SD3 Turbo"""
    
    # Streamlined style descriptions optimized for SD3 Turbo
    THEME_STYLES = {
        'rustic': {
            'description': 'rustic farmhouse wedding with wooden elements, mason jars, burlap, string lights, wildflowers, vintage charm',
            'lighting': 'warm golden lighting, string lights, candles',
            'colors': 'warm earth tones, cream, sage green, dusty rose',
            'atmosphere': 'cozy intimate rustic celebration'
        },
        'modern': {
            'description': 'contemporary minimalist wedding with clean lines, sleek furniture, geometric elements, modern floral arrangements',
            'lighting': 'clean architectural lighting, modern chandeliers',
            'colors': 'white, black, grey, metallic accents',
            'atmosphere': 'sophisticated contemporary elegance'
        },
        'vintage': {
            'description': 'romantic vintage wedding with antique lace, classic roses, ornate details, vintage china, old-world charm',
            'lighting': 'soft romantic lighting, vintage chandeliers, warm glow',
            'colors': 'blush pink, ivory, gold, dusty blue',
            'atmosphere': 'romantic vintage elegance'
        },
        'bohemian': {
            'description': 'bohemian wedding with macrame, colorful textiles, pampas grass, natural elements, eclectic patterns',
            'lighting': 'warm ambient lighting, lanterns, fairy lights',
            'colors': 'terracotta, sage, mustard, jewel tones',
            'atmosphere': 'free-spirited boho celebration'
        },
        'classic': {
            'description': 'timeless traditional wedding with elegant white flowers, formal settings, crystal details, refined luxury',
            'lighting': 'crystal chandeliers, elegant uplighting',
            'colors': 'white, ivory, gold, champagne',
            'atmosphere': 'grand formal celebration'
        },
        'garden': {
            'description': 'natural garden wedding with abundant flowers, greenery, botanical elements, organic arrangements',
            'lighting': 'natural daylight, garden string lights',
            'colors': 'green, white, soft pastels, natural colors',
            'atmosphere': 'natural garden party celebration'
        },
        'beach': {
            'description': 'coastal beach wedding with driftwood, flowing fabrics, nautical elements, ocean-inspired colors',
            'lighting': 'natural beach lighting, soft coastal ambiance',
            'colors': 'ocean blue, sandy beige, coral, seafoam',
            'atmosphere': 'coastal beach celebration'
        },
        'industrial': {
            'description': 'urban industrial wedding with exposed brick, metal fixtures, Edison bulbs, concrete elements, modern urban aesthetic',
            'lighting': 'Edison bulbs, industrial fixtures, urban lighting',
            'colors': 'grey, black, copper, warm metallics',
            'atmosphere': 'urban industrial celebration'
        }
    }
    
    # Simplified space details for faster processing
    SPACE_DETAILS = {
        'indoor_ceremony': {
            'focus': 'ceremony aisle and altar area',
            'elements': 'wedding arch, aisle decorations, ceremony seating',
            'setup': 'intimate sacred ceremony space'
        },
        'outdoor_ceremony': {
            'focus': 'outdoor ceremony with natural backdrop',
            'elements': 'outdoor wedding arch, natural landscaping, ceremony seating',
            'setup': 'natural outdoor ceremony setting'
        },
        'reception_hall': {
            'focus': 'dining tables and celebration space',
            'elements': 'round dining tables, centerpieces, dance floor',
            'setup': 'festive reception celebration'
        },
        'garden': {
            'focus': 'garden setting with natural elements',
            'elements': 'garden landscaping, outdoor furniture, natural pathways',
            'setup': 'natural garden party atmosphere'
        },
        'beach': {
            'focus': 'beach setting with ocean views',
            'elements': 'beach decorations, coastal elements, ocean backdrop',
            'setup': 'coastal beach celebration'
        },
        'barn': {
            'focus': 'rustic barn interior with wooden beams',
            'elements': 'wooden beams, barn doors, country decorations',
            'setup': 'rustic country celebration'
        },
        'ballroom': {
            'focus': 'elegant ballroom with formal atmosphere',
            'elements': 'elegant tables, ballroom lighting, formal decorations',
            'setup': 'grand formal ballroom celebration'
        },
        'rooftop': {
            'focus': 'rooftop venue with city views',
            'elements': 'rooftop furniture, city skyline, urban decorations',
            'setup': 'elevated urban celebration'
        }
    }
    
    @classmethod
    def generate_comprehensive_prompt(cls, wedding_theme, space_type, additional_details=None):
        """Generate a comprehensive prompt optimized for SD3 Turbo processing"""
        
        theme_data = cls.THEME_STYLES.get(wedding_theme, cls.THEME_STYLES['classic'])
        space_data = cls.SPACE_DETAILS.get(space_type, cls.SPACE_DETAILS['reception_hall'])
        
        # Streamlined prompt construction for SD3 Turbo
        prompt_parts = [
            # Quality indicators (simplified for turbo)
            "professional wedding photography, photorealistic, detailed",
            
            # Core transformation description
            f"Transform this {space_type.replace('_', ' ')} into a beautiful {wedding_theme} wedding venue,",
            
            # Theme and space integration
            f"{theme_data['description']},",
            f"{space_data['setup']},",
            
            # Essential elements
            f"featuring {space_data['elements']},",
            f"{theme_data['lighting']},",
            f"color palette: {theme_data['colors']},",
            
            # Final atmosphere
            f"{theme_data['atmosphere']}, elegant wedding setup, celebration ready"
        ]
        
        # Add user details if provided
        if additional_details:
            prompt_parts.append(additional_details)
        
        # Join with spaces for cleaner prompt
        main_prompt = " ".join(prompt_parts)
        
        # Streamlined negative prompt for SD3 Turbo
        negative_prompt = cls.generate_negative_prompt()
        
        return {
            'prompt': main_prompt,
            'negative_prompt': negative_prompt,
            'recommended_params': cls.get_recommended_parameters_turbo(wedding_theme, space_type)
        }
    
    @classmethod
    def generate_negative_prompt(cls):
        """Generate streamlined negative prompt optimized for SD3 Turbo"""
        negative_elements = [
            # People and faces (core exclusions)
            "people, faces, crowd, guests, bride, groom",
            
            # Quality issues
            "blurry, low quality, distorted, pixelated",
            
            # Unwanted content
            "text, watermark, signature",
            
            # Bad atmosphere
            "dark, dim, messy, cluttered, chaotic",
            
            # Style issues
            "cartoon, anime, unrealistic"
        ]
        
        return ", ".join(negative_elements)
    
    @classmethod
    def get_recommended_parameters_turbo(cls, wedding_theme, space_type):
        """Get optimized parameters for SD3 Turbo processing"""
        
        # Base parameters optimized for SD3 Turbo speed and quality
        base_params = {
            'aspect_ratio': '1:1',     # 1024x1024 optimal for SD3 Turbo
            'strength': 0.35,          # Good balance for venue transformation
            'output_format': 'png',    # High quality output
            'mode': 'image-to-image',
        }
        
        # Theme-specific adjustments for turbo processing
        theme_adjustments = {
            'modern': {'strength': 0.4},      # More transformation for clean modern look
            'vintage': {'strength': 0.3},     # Preserve more original for vintage feel
            'industrial': {'strength': 0.4},  # Strong transformation for industrial elements
            'bohemian': {'strength': 0.3},    # Preserve natural elements
            'classic': {'strength': 0.35},    # Balanced transformation
            'garden': {'strength': 0.25},     # Preserve natural setting
            'beach': {'strength': 0.3},       # Preserve coastal elements
            'rustic': {'strength': 0.35},     # Balanced rustic transformation
        }
        
        # Space-specific adjustments
        space_adjustments = {
            'outdoor_ceremony': {'strength': 0.25},  # Preserve natural outdoor setting
            'garden': {'strength': 0.25},            # Preserve garden elements
            'beach': {'strength': 0.3},              # Preserve beach setting
            'ballroom': {'aspect_ratio': '16:9'},    # Better for large ballrooms
            'reception_hall': {'aspect_ratio': '16:9'}, # Better for reception spaces
        }
        
        # Apply adjustments
        final_params = base_params.copy()
        
        if wedding_theme in theme_adjustments:
            final_params.update(theme_adjustments[wedding_theme])
            
        if space_type in space_adjustments:
            final_params.update(space_adjustments[space_type])
        
        return final_params
    
    @classmethod
    def generate_quick_prompt(cls, wedding_theme, space_type):
        """Generate a quick, simplified prompt for ultra-fast processing"""
        
        theme_data = cls.THEME_STYLES.get(wedding_theme, cls.THEME_STYLES['classic'])
        space_data = cls.SPACE_DETAILS.get(space_type, cls.SPACE_DETAILS['reception_hall'])
        
        # Ultra-simplified prompt for maximum speed
        quick_prompt = f"Transform into {wedding_theme} wedding {space_type.replace('_', ' ')}, {theme_data['description']}, {theme_data['atmosphere']}, professional wedding photography"
        
        # Minimal negative prompt
        quick_negative = "people, faces, guests, blurry, low quality, text"
        
        return {
            'prompt': quick_prompt,
            'negative_prompt': quick_negative,
            'recommended_params': {
                'aspect_ratio': '1:1',
                'strength': 0.35,
                'output_format': 'png',
                'mode': 'image-to-image',
            }
        }
    
    @classmethod
    def generate_speed_optimized_variations(cls, wedding_theme, space_type):
        """Generate multiple speed-optimized prompt variations for A/B testing"""
        
        base_prompt_data = cls.generate_comprehensive_prompt(wedding_theme, space_type)
        
        variations = [
            # Standard comprehensive
            {
                'name': 'Comprehensive',
                'prompt': base_prompt_data['prompt'],
                'negative_prompt': base_prompt_data['negative_prompt'],
                'params': base_prompt_data['recommended_params']
            },
            
            # Quick version
            {
                'name': 'Quick',
                **cls.generate_quick_prompt(wedding_theme, space_type)
            },
            
            # Focused version (emphasize key elements)
            {
                'name': 'Focused',
                'prompt': f"{wedding_theme} wedding venue transformation, {cls.THEME_STYLES[wedding_theme]['description']}, professional photography",
                'negative_prompt': "people, faces, blurry, low quality",
                'params': {
                    'aspect_ratio': '1:1',
                    'strength': 0.4,
                    'output_format': 'png',
                    'mode': 'image-to-image',
                }
            }
        ]
        
        return variations