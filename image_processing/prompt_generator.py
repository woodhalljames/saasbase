# image_processing/prompt_generator.py - Enhanced with dynamic parameters
"""
Advanced prompt generation system for realistic wedding venue transformations
Optimized for Stability AI SD3 Turbo with dynamic parameters
"""

class WeddingPromptGenerator:
    """Generate comprehensive prompts for wedding venue transformations with dynamic options"""
    
    # Enhanced style descriptions
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
    
    # Guest count modifiers
    GUEST_COUNT_MODIFIERS = {
        'intimate': 'intimate small gathering setup, cozy seating arrangements, personal details',
        'medium': 'medium-sized celebration setup, balanced seating, moderate scale decorations',
        'large': 'large celebration setup, grand seating arrangements, impressive scale decorations',
        'grand': 'grand spectacular celebration setup, elaborate seating, magnificent large-scale decorations'
    }
    
    # Budget level modifiers
    BUDGET_MODIFIERS = {
        'budget': 'tasteful affordable decorations, DIY elements, simple elegant touches',
        'moderate': 'quality decorations, professional setup, refined details',
        'luxury': 'luxury high-end decorations, premium materials, sophisticated elegant details',
        'ultra_luxury': 'ultra-luxury opulent decorations, exquisite premium materials, lavish spectacular details'
    }
    
    # Season modifiers
    SEASON_MODIFIERS = {
        'spring': 'fresh spring flowers, pastel colors, light fabrics, renewal theme',
        'summer': 'vibrant summer blooms, bright colors, outdoor elements, sunny atmosphere',
        'fall': 'autumn foliage, warm colors, harvest elements, cozy atmosphere',
        'winter': 'winter elegance, rich colors, warm textures, festive elements'
    }
    
    # Time of day modifiers
    TIME_MODIFIERS = {
        'morning': 'bright morning light, fresh atmosphere, breakfast reception setup',
        'afternoon': 'natural daylight, relaxed atmosphere, lunch reception setup',
        'evening': 'golden hour lighting, romantic atmosphere, dinner reception setup',
        'night': 'dramatic evening lighting, elegant atmosphere, formal dinner setup'
    }
    
    # Color scheme modifiers
    COLOR_MODIFIERS = {
        'neutral': 'neutral color palette with whites, creams, beiges, and soft tones',
        'pastels': 'soft pastel color palette with gentle pinks, blues, and lavenders',
        'jewel_tones': 'rich jewel tone palette with emerald, sapphire, and ruby colors',
        'earth_tones': 'natural earth tone palette with browns, tans, and forest greens',
        'monochrome': 'elegant black and white monochrome palette',
        'bold_colors': 'vibrant bold color palette with bright striking colors'
    }
    
    @classmethod
    def generate_dynamic_prompt(cls, wedding_theme, space_type, guest_count=None, 
                               budget_level=None, season=None, time_of_day=None,
                               color_scheme=None, custom_colors=None, additional_details=None):
        """Generate a comprehensive prompt with dynamic parameters for SD3 Turbo"""
        
        theme_data = cls.THEME_STYLES.get(wedding_theme, cls.THEME_STYLES['classic'])
        
        # Build dynamic prompt parts
        prompt_parts = [
            # Core quality indicators
            "professional wedding photography, photorealistic, detailed, high resolution",
            
            # Core transformation
            f"Transform this {space_type.replace('_', ' ')} into a beautiful {wedding_theme} wedding venue,",
            
            # Theme description
            f"{theme_data['description']},",
        ]
        
        # Add guest count modifier
        if guest_count and guest_count in cls.GUEST_COUNT_MODIFIERS:
            prompt_parts.append(cls.GUEST_COUNT_MODIFIERS[guest_count])
        
        # Add budget modifier
        if budget_level and budget_level in cls.BUDGET_MODIFIERS:
            prompt_parts.append(cls.BUDGET_MODIFIERS[budget_level])
        
        # Add seasonal elements
        if season and season in cls.SEASON_MODIFIERS:
            prompt_parts.append(cls.SEASON_MODIFIERS[season])
        
        # Add time of day elements
        if time_of_day and time_of_day in cls.TIME_MODIFIERS:
            prompt_parts.append(cls.TIME_MODIFIERS[time_of_day])
        
        # Add color scheme
        if color_scheme and color_scheme in cls.COLOR_MODIFIERS:
            if color_scheme == 'custom' and custom_colors:
                prompt_parts.append(f"custom color palette featuring {custom_colors}")
            else:
                prompt_parts.append(cls.COLOR_MODIFIERS[color_scheme])
        else:
            # Use theme default colors
            prompt_parts.append(f"color palette: {theme_data['colors']}")
        
        # Add lighting
        prompt_parts.append(f"{theme_data['lighting']}")
        
        # Add atmosphere
        prompt_parts.append(f"{theme_data['atmosphere']}")
        
        # Add user details if provided
        if additional_details:
            prompt_parts.append(additional_details)
        
        # Final touches
        prompt_parts.append("elegant wedding setup, celebration ready, no people visible")
        
        # Join with proper spacing
        main_prompt = " ".join([part.strip() for part in prompt_parts if part.strip()])
        
        # Enhanced negative prompt
        negative_prompt = cls.generate_enhanced_negative_prompt()
        
        return {
            'prompt': main_prompt,
            'negative_prompt': negative_prompt,
            'recommended_params': cls.get_dynamic_parameters(wedding_theme, space_type, guest_count)
        }
    
    @classmethod
    def generate_enhanced_negative_prompt(cls):
        """Generate enhanced negative prompt for SD3 Turbo"""
        negative_elements = [
            # People and faces (critical for venue photos)
            "people, faces, crowd, guests, bride, groom, wedding party, humans, person",
            
            # Quality issues
            "blurry, low quality, distorted, pixelated, artifacts, noise",
            
            # Unwanted content
            "text, watermark, signature, logo, copyright",
            
            # Bad atmosphere
            "dark, dim, messy, cluttered, chaotic, unorganized",
            
            # Style issues
            "cartoon, anime, unrealistic, fake, artificial",
            
            # Composition issues
            "cropped, cut off, partial, incomplete"
        ]
        
        return ", ".join(negative_elements)
    
    @classmethod
    def get_dynamic_parameters(cls, wedding_theme, space_type, guest_count):
        """Get optimized parameters based on dynamic choices"""
        
        # Base parameters for SD3 Turbo
        base_params = {
            'aspect_ratio': '1:1',
            'strength': 0.35,
            'output_format': 'png',
        }
        
        # Adjust strength based on guest count (more guests = more transformation needed)
        if guest_count == 'intimate':
            base_params['strength'] = 0.25  # Preserve more of original for intimate spaces
        elif guest_count == 'grand':
            base_params['strength'] = 0.45  # More transformation for grand celebrations
        
        # Adjust aspect ratio for different spaces
        if space_type in ['reception_hall', 'ballroom', 'barn']:
            base_params['aspect_ratio'] = '16:9'  # Better for large horizontal spaces
        elif space_type in ['rooftop', 'garden']:
            base_params['aspect_ratio'] = '4:3'   # Good for outdoor spaces
        
        return base_params
    
    @classmethod
    def get_quick_suggestions(cls, wedding_theme, space_type):
        """Get quick suggestions for common combinations"""
        suggestions = {
            'guest_count': 'medium',
            'budget_level': 'moderate',
            'time_of_day': 'evening',
            'color_scheme': 'neutral'
        }
        
        # Theme-specific suggestions
        if wedding_theme == 'rustic':
            suggestions.update({
                'season': 'fall',
                'color_scheme': 'earth_tones'
            })
        elif wedding_theme == 'beach':
            suggestions.update({
                'season': 'summer',
                'time_of_day': 'afternoon',
                'color_scheme': 'neutral'
            })
        elif wedding_theme == 'vintage':
            suggestions.update({
                'color_scheme': 'pastels',
                'budget_level': 'luxury'
            })
        
        return suggestions