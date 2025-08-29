# image_processing/prompt_generator.py - Simplified and improved for better image generation

class WeddingPromptGenerator:
    """SIMPLIFIED wedding venue prompt generation - fixed parameters, core functionality only"""
    
    @classmethod
    def generate_wedding_prompt(cls, wedding_theme, space_type, season=None, 
                               lighting_mood=None, color_scheme=None,
                               special_features=None, avoid=None, **kwargs):
        """
        Generate SIMPLIFIED prompts for SD3.5 Large with FIXED parameters
        Only handles: wedding_theme, space_type, season, lighting_mood, color_scheme, special_features, avoid
        """
        
        # Get the core transformation description
        core_description = cls._get_core_transformation(wedding_theme, space_type)
        
        # Add simplified contextual modifiers
        context_modifiers = cls._get_context_modifiers(season, lighting_mood, color_scheme)
        
        # Build the final prompt (keep it focused)
        prompt_parts = [core_description]
        if context_modifiers:
            prompt_parts.append(context_modifiers)
        
        # Add special features if provided
        if special_features and special_features.strip():
            prompt_parts.append(f"incorporating {special_features.strip()}")
        
        # Add quality indicators (minimal and effective)
        prompt_parts.append("elegant wedding design, professional photography, beautiful lighting, high quality")
        
        final_prompt = ", ".join(prompt_parts)
        
        # Generate focused negative prompt
        negative_prompt = cls._generate_focused_negative_prompt(avoid)
        
        # FIXED parameters - no more customization
        return {
            'prompt': final_prompt,
            'negative_prompt': negative_prompt,
            'recommended_params': {
                'strength': 0.70,      # FIXED at 70%
                'cfg_scale': 7.5,      # FIXED standard CFG
                'steps': 30,           # FIXED at 30 steps
                'output_format': 'png'
            }
        }
    
    @classmethod
    def _get_core_transformation(cls, wedding_theme, space_type):
        """Get the core transformation description - simplified and clear"""
        
        # Simplified theme descriptions focusing on key visual elements
        theme_styles = {
            # Core Popular Themes
            'rustic': 'rustic farmhouse style with wooden elements, burlap, mason jars, string lights',
            'modern': 'modern contemporary design with clean lines, minimalist decor, geometric elements',
            'vintage': 'vintage romantic style with antique furniture, lace details, soft florals',
            'bohemian': 'bohemian style with macrame, pampas grass, earth tones, natural textures',
            'classic': 'classic elegant style with white roses, gold accents, formal table settings',
            'garden': 'garden style with natural greenery, flowering plants, organic arrangements',
            'beach': 'coastal style with driftwood, shells, light colors, natural materials',
            'industrial': 'industrial style with exposed brick, metal elements, Edison bulbs',
            'glamorous': 'glamorous luxury style with crystals, gold details, elegant fabrics',
            'tropical': 'tropical style with palm leaves, bright flowers, bamboo elements',
            
            # Extended themes (simplified)
            'fairy_tale': 'fairy tale enchanted style with magical elements, soft lighting',
            'winter_wonderland': 'winter wonderland style with white decorations, silver accents',
            'spring_awakening': 'spring style with fresh blooms, pastel colors, light fabrics',
            'summer_solstice': 'summer style with bright colors, lush greenery, abundant flowers',
            'autumn_harvest': 'autumn style with warm colors, pumpkins, fall foliage',
            
            # Cultural themes (essential ones)
            'japanese_zen': 'Japanese zen style with minimalist elements, natural materials',
            'french_chateau': 'French chateau style with elegant vintage details',
            'italian_villa': 'Italian villa style with romantic European elements',
            'spanish_hacienda': 'Spanish hacienda style with warm terracotta and rustic charm',
        }
        
        # Space type descriptions - SIMPLIFIED to 4 core spaces
        space_descriptions = {
            'wedding_ceremony': 'wedding ceremony space with altar area and guest seating',
            'dance_floor': 'dance floor with open space for dancing and celebration',
            'dining_area': 'reception dining with tables and chairs for guests',
            'entrance_area': 'entrance foyer with welcoming decorations',
        }
        
        theme_desc = theme_styles.get(wedding_theme, f'{wedding_theme.replace("_", " ")} wedding style')
        space_desc = space_descriptions.get(space_type, f'{space_type.replace("_", " ")}')
        
        return f"elegant {space_desc} decorated in {theme_desc}"
    
    @classmethod
    def _get_context_modifiers(cls, season, lighting_mood, color_scheme):
        """Get simplified contextual modifiers"""
        
        modifiers = []
        
        # Seasonal elements (simplified)
        if season:
            seasonal_elements = {
                'spring': 'with spring flowers and fresh greenery',
                'summer': 'with lush summer blooms and bright atmosphere',
                'fall': 'with autumn colors and warm tones',
                'winter': 'with winter elegance and rich textures'
            }
            if season in seasonal_elements:
                modifiers.append(seasonal_elements[season])
        
        # Lighting mood (simplified from the original lighting_moods and time_of_day)
        if lighting_mood:
            lighting_descriptions = {
                'romantic': 'romantic warm lighting',
                'bright': 'bright cheerful lighting',
                'dim': 'intimate dim lighting',
                'dramatic': 'dramatic moody lighting',
                'natural': 'natural daylight',
                'golden': 'golden hour lighting',
                'dusk': 'twilight dusk atmosphere',
                'dawn': 'soft morning light'
            }
            if lighting_mood in lighting_descriptions:
                modifiers.append(lighting_descriptions[lighting_mood])
        
        # Color scheme (simplified)
        if color_scheme:
            color_descriptions = {
                'neutral': 'neutral color palette with whites and creams',
                'pastels': 'soft pastel colors',
                'jewel_tones': 'rich jewel tone colors',
                'earth_tones': 'warm earth tone colors',
                'monochrome': 'black and white color scheme',
                'bold_colors': 'vibrant bold colors',
                'blush_gold': 'blush and gold color palette',
                'sage_cream': 'sage and cream color palette',
                'navy_copper': 'navy and copper color palette',
                'burgundy_ivory': 'burgundy and ivory color palette'
            }
            if color_scheme in color_descriptions:
                modifiers.append(color_descriptions[color_scheme])
        
        return ", ".join(modifiers) if modifiers else ""
    
    @classmethod
    def _generate_focused_negative_prompt(cls, user_negative_prompt):
        """Generate a focused negative prompt - essential negatives only"""
        
        # Core negatives that are essential for wedding venue transformation
        core_negatives = [
            "people, faces, humans, guests, bride, groom, wedding party",
            "blurry, low quality, dark, poorly lit, overexposed",
            "messy, cluttered, unfinished, damaged, dirty",
            "text, watermark, logos, signatures"
        ]
        
        # Add user negatives if provided
        if user_negative_prompt and user_negative_prompt.strip():
            core_negatives.append(user_negative_prompt.strip())
        
        return ", ".join(core_negatives)


# Backward compatibility functions
def generate_wedding_prompt_with_dynamics(**kwargs):
    """Backward compatibility wrapper - now uses simplified version"""
    return WeddingPromptGenerator.generate_wedding_prompt(**kwargs)


def generate_enhanced_wedding_prompt(**kwargs):
    """Backward compatibility wrapper - now uses simplified version"""
    return WeddingPromptGenerator.generate_wedding_prompt(**kwargs)