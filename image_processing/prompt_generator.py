# image_processing/prompt_generator.py - Space-First Prompt Generation for Superior Wedding Venue Transformations
"""
Completely overhauled prompt generation system prioritizing SPACE FUNCTION first, then theme styling
Optimized for Stability AI SD3.5 Large with focus on actual space transformation
Space-first approach ensures AI understands what type of venue to create before applying decorative themes
"""

class WeddingPromptGenerator:
    """Generate space-first prompts optimized for SD3.5 Large wedding venue transformations"""
    
    @classmethod
    def generate_space_first_prompt(cls, wedding_theme, space_type, guest_count=None, 
                                   budget_level=None, season=None, time_of_day=None,
                                   color_scheme=None, custom_colors=None, additional_details=None):
        """
        NEW APPROACH: Space function defines the transformation, theme provides styling
        This ensures the AI actually transforms the space rather than just decorating it
        """
        
        space_data = cls.SPACE_DEFINITIONS.get(space_type, cls.SPACE_DEFINITIONS['wedding_ceremony'])
        theme_data = cls.THEME_STYLING.get(wedding_theme, cls.THEME_STYLING['classic'])
        
        # 1. QUALITY FOUNDATION - Critical for SD3.5 Large
        quality_foundation = "Professional wedding venue photography, photorealistic, ultra-high resolution, masterpiece quality."
        
        # 2. PRIMARY SPACE TRANSFORMATION - Most Important Section
        space_transformation = f"Transform this space into a complete {space_data['function']}."
        
        # 3. SPACE ARCHITECTURE AND LAYOUT - Defines the physical setup
        space_architecture = f"Spatial layout: {space_data['layout']}. Key elements: {space_data['elements']}."
        
        # 4. FUNCTIONAL REQUIREMENTS - What makes this space work
        functional_setup = f"Functional requirements: {space_data['requirements']}."
        
        # 5. CAPACITY AND SCALE - Size appropriate for space type
        capacity_setup = cls._get_capacity_specification(guest_count, space_type)
        
        # 6. THEME STYLING LAYER - Secondary enhancement, not primary focus
        theme_styling = f"Decorative styling: {wedding_theme} wedding theme featuring {theme_data['elements']}."
        
        # 7. MATERIAL AND COLOR PALETTE - Visual enhancement
        color_specification = cls._get_color_specification(color_scheme, custom_colors, theme_data)
        
        # 8. LIGHTING AND ATMOSPHERE - Mood setting
        lighting_atmosphere = f"Lighting: {theme_data['lighting']}. Atmosphere: {theme_data['atmosphere']}."
        
        # 9. PRODUCTION QUALITY LEVEL - Budget/quality context
        production_level = cls._get_production_level(budget_level)
        
        # 10. SEASONAL/TEMPORAL CONTEXT - When appropriate
        temporal_context = cls._get_temporal_context(season, time_of_day)
        
        # 11. USER SPECIFICATIONS - Additional details
        user_specifications = f"Additional specifications: {additional_details}." if additional_details else ""
        
        # 12. TECHNICAL REQUIREMENTS - Final specifications
        technical_requirements = "Output requirements: professional wedding setup ready for guests, no people visible, celebration-ready venue, elegant transformation complete."
        
        # ASSEMBLE SPACE-FIRST PROMPT with proper hierarchy
        prompt_sections = [
            quality_foundation,
            space_transformation,
            space_architecture,
            functional_setup,
            capacity_setup,
            theme_styling,
            color_specification,
            lighting_atmosphere,
            production_level,
            temporal_context,
            user_specifications,
            technical_requirements
        ]
        
        # Clean and join sections
        final_prompt = " ".join([section.strip() for section in prompt_sections if section.strip()])
        
        # Enhanced negative prompt for SD3.5 Large
        negative_prompt = cls.generate_enhanced_negative_prompt()
        
        return {
            'prompt': final_prompt,
            'negative_prompt': negative_prompt,
            'recommended_params': cls.get_space_optimized_parameters(space_type, wedding_theme, guest_count)
        }
    
    # SPACE DEFINITIONS - Primary focus on what each space IS and DOES
    SPACE_DEFINITIONS = {
        'wedding_ceremony': {
            'function': 'wedding ceremony venue with processional aisle and formal guest seating arrangement',
            'layout': 'guests seated in organized rows facing ceremonial altar area, center processional aisle for wedding party entrance',
            'elements': 'ceremony altar or decorative arch, guest seating in rows, processional aisle runner, unity ceremony area, officiant space',
            'requirements': 'clear sightlines to ceremony altar, adequate space for wedding party, acoustic considerations for vows, processional pathway',
            'scale_factor': 'ceremony_focused'
        },
        'dance_floor': {
            'function': 'dedicated dance floor area for wedding reception entertainment and dancing',
            'layout': 'central polished dance floor with surrounding lounge seating and music performance area',
            'elements': 'smooth dance floor surface, DJ or band setup area, perimeter lounge seating, dance floor lighting, entertainment space',
            'requirements': 'proper flooring for dancing, sound system positioning, adequate lighting for dancing, comfortable viewing areas',
            'scale_factor': 'entertainment_focused'
        },
        'dining_area': {
            'function': 'formal dining space for wedding reception meal service and guest dining',
            'layout': 'dining tables arranged with proper spacing for service access and guest comfort',
            'elements': 'dining tables with chair seating, table place settings, centerpiece displays, service pathways, serving stations',
            'requirements': 'adequate table spacing for service, comfortable seating arrangements, clear service pathways, proper dining ambiance',
            'scale_factor': 'dining_focused'
        },
        'cocktail_hour': {
            'function': 'cocktail reception area for guest mingling, drinks, and appetizer service',
            'layout': 'mix of standing cocktail tables, bar areas, and casual seating for social interaction',
            'elements': 'high cocktail tables, bar setup with seating, standing areas, appetizer stations, conversational seating groups',
            'requirements': 'bar service areas, food service stations, standing and seating options, social interaction spaces',
            'scale_factor': 'social_focused'
        },
        'lounge_area': {
            'function': 'comfortable relaxation space for guest conversation and intimate gatherings',
            'layout': 'grouped comfortable seating arrangements creating intimate conversation areas',
            'elements': 'comfortable sofas and armchairs, coffee tables, side tables, ambient lighting, intimate seating clusters',
            'requirements': 'comfortable seating furniture, conversation-friendly layout, soft ambient lighting, relaxed atmosphere',
            'scale_factor': 'intimate_focused'
        }
    }
    
    # THEME STYLING - Secondary layer that enhances space function
    THEME_STYLING = {
        # Classic Popular Themes - Updated for space-first approach
        'rustic': {
            'elements': 'reclaimed wood furniture, burlap table runners, mason jar lighting, wildflower arrangements, string light canopies, barn-style decorative accents',
            'lighting': 'warm string lights, mason jar pendant lighting, candles in wooden holders, natural ambient lighting',
            'colors': 'warm cream, sage green, dusty rose, natural wood tones, burlap brown',
            'atmosphere': 'cozy farmhouse celebration with rustic charm and natural warmth'
        },
        'modern': {
            'elements': 'sleek geometric furniture, contemporary acrylic chairs, minimalist centerpieces, clean-lined decorative elements, modern lighting fixtures',
            'lighting': 'contemporary pendant lighting, geometric chandeliers, LED accent lighting, clean architectural lighting',
            'colors': 'pure white, charcoal grey, black accents, metallic silver, glass elements',
            'atmosphere': 'sophisticated contemporary elegance with clean modern aesthetic'
        },
        'vintage': {
            'elements': 'antique furniture pieces, vintage lace details, ornate chandeliers, classic rose arrangements, vintage china settings, period decorative pieces',
            'lighting': 'vintage crystal chandeliers, antique candelabras, warm Edison bulbs, romantic vintage lighting',
            'colors': 'blush pink, ivory cream, antique gold, dusty blue, champagne tones',
            'atmosphere': 'romantic vintage elegance with timeless old-world charm'
        },
        'bohemian': {
            'elements': 'macrame wall hangings, pampas grass arrangements, colorful textile runners, floor cushions, hanging plants, natural wood elements',
            'lighting': 'hanging lanterns, fairy lights, candles in glass vessels, natural ambient lighting',
            'colors': 'terracotta orange, sage green, mustard yellow, deep burgundy, natural earth tones',
            'atmosphere': 'free-spirited boho celebration with natural organic elements'
        },
        'classic': {
            'elements': 'elegant formal furniture, crystal chandeliers, pristine white linens, classic white flower arrangements, formal place settings, traditional decor',
            'lighting': 'crystal chandeliers, elegant uplighting, classic candelabras, refined ambient lighting',
            'colors': 'pure white, ivory, champagne gold, silver accents, classic elegance',
            'atmosphere': 'timeless traditional elegance with formal sophistication'
        },
        'garden': {
            'elements': 'natural flower arrangements, greenery garlands, botanical centerpieces, garden-style furniture, organic decorative elements',
            'lighting': 'natural garden lighting, string lights through greenery, garden lanterns, soft natural illumination',
            'colors': 'natural green, soft white, garden pastels, earth tones, botanical colors',
            'atmosphere': 'natural garden party celebration with organic beauty and fresh elegance'
        },
        'beach': {
            'elements': 'driftwood decorative pieces, flowing white fabric draping, seashell accents, nautical rope details, coastal furniture, ocean-inspired decor',
            'lighting': 'natural coastal lighting, tiki torches, hurricane lanterns, soft sunset-inspired lighting',
            'colors': 'ocean blue, sandy beige, coral pink, seafoam green, natural whites',
            'atmosphere': 'relaxed coastal celebration with ocean-inspired serenity'
        },
        'industrial': {
            'elements': 'metal and wood furniture combinations, exposed bulb lighting, concrete planters, urban materials, industrial decorative accents',
            'lighting': 'Edison bulb installations, industrial pendant lights, exposed bulb chandeliers, urban atmospheric lighting',
            'colors': 'charcoal grey, copper accents, warm metallics, concrete tones, industrial blacks',
            'atmosphere': 'urban industrial celebration with modern edge and contemporary style'
        },
        
        # Cultural Themes
        'japanese_zen': {
            'elements': 'bamboo decorative screens, cherry blossom arrangements, minimalist wooden furniture, paper lanterns, zen garden elements, sake ceremony table',
            'lighting': 'soft paper lanterns, bamboo lighting fixtures, candles in stone holders, gentle ambient zen lighting',
            'colors': 'soft pink cherry blossom, white, natural bamboo, sage green, cream',
            'atmosphere': 'peaceful zen celebration with minimalist harmony and natural serenity'
        },
        'moroccan_nights': {
            'elements': 'ornate metallic lanterns, rich tapestry draping, low cushioned seating, intricate patterned textiles, Middle Eastern decorative pieces',
            'lighting': 'ornate Moroccan lanterns, warm golden lighting, exotic pendant lights, Middle Eastern ambiance',
            'colors': 'rich jewel tones, deep purple, gold, turquoise, burgundy, warm orange',
            'atmosphere': 'exotic Moroccan celebration with luxurious Middle Eastern mystique'
        },
        
        # Add more themes as needed but focus on the most popular ones for initial implementation
    }
    
    @classmethod
    def _get_capacity_specification(cls, guest_count, space_type):
        """Generate capacity-appropriate specifications for each space type"""
        
        capacity_specs = {
            'intimate': {'guests': '15-50', 'scale': 'intimate'},
            'medium': {'guests': '75-100', 'scale': 'medium'},
            'large': {'guests': '150-200', 'scale': 'large'},
            'grand': {'guests': '250+', 'scale': 'grand'}
        }
        
        space_capacity_requirements = {
            'wedding_ceremony': {
                'intimate': 'ceremony seating for 15-50 guests in 3-4 rows, intimate ceremony scale',
                'medium': 'ceremony seating for 75-100 guests in 8-10 rows, balanced ceremony arrangement',
                'large': 'ceremony seating for 150-200 guests in 12-15 rows, grand ceremony setup',
                'grand': 'ceremony seating for 250+ guests in 20+ rows, spectacular ceremony arrangement'
            },
            'dining_area': {
                'intimate': 'dining for 15-50 guests with 2-3 round tables or long farm tables, cozy dining scale',
                'medium': 'dining for 75-100 guests with 8-10 round tables, comfortable dining arrangement',
                'large': 'dining for 150-200 guests with 15-20 round tables, elegant dining setup',
                'grand': 'dining for 250+ guests with 25+ round tables, spectacular dining arrangement'
            },
            'dance_floor': {
                'intimate': 'dance floor for 15-50 guests with cozy perimeter seating, intimate party scale',
                'medium': 'dance floor for 75-100 guests with adequate perimeter seating, lively party setup',
                'large': 'dance floor for 150-200 guests with extensive perimeter seating, grand party arrangement',
                'grand': 'dance floor for 250+ guests with spectacular perimeter seating, massive celebration setup'
            },
            'cocktail_hour': {
                'intimate': 'cocktail setup for 15-50 guests with 3-4 cocktail tables, intimate mingling space',
                'medium': 'cocktail setup for 75-100 guests with 8-10 cocktail tables, social mingling area',
                'large': 'cocktail setup for 150-200 guests with 15-20 cocktail tables, grand social space',
                'grand': 'cocktail setup for 250+ guests with 25+ cocktail tables, spectacular social venue'
            },
            'lounge_area': {
                'intimate': 'lounge seating for 15-50 guests with 2-3 seating groups, cozy conversation areas',
                'medium': 'lounge seating for 75-100 guests with 5-6 seating groups, comfortable social areas',
                'large': 'lounge seating for 150-200 guests with 8-10 seating groups, extensive relaxation space',
                'grand': 'lounge seating for 250+ guests with 12+ seating groups, luxurious relaxation venue'
            }
        }
        
        guest_level = guest_count or 'medium'
        space_requirements = space_capacity_requirements.get(space_type, {})
        capacity_spec = space_requirements.get(guest_level, space_requirements.get('medium', 'appropriate seating for wedding guests'))
        
        return f"Capacity requirements: {capacity_spec}."
    
    @classmethod
    def _get_color_specification(cls, color_scheme, custom_colors, theme_data):
        """Generate color palette specification"""
        
        color_schemes = {
            'neutral': 'sophisticated neutral palette with whites, creams, beiges, champagne, and soft taupe tones',
            'pastels': 'soft romantic pastel palette with blush pink, lavender, baby blue, mint green, and cream',
            'jewel_tones': 'rich luxurious jewel tones with emerald green, sapphire blue, ruby red, and gold accents',
            'earth_tones': 'natural earth tone palette with sage green, terracotta, warm browns, and cream',
            'monochrome': 'elegant sophisticated black and white palette with silver accents',
            'bold_colors': 'vibrant bold palette with bright fuchsia, orange, turquoise, and lime green'
        }
        
        if color_scheme == 'custom' and custom_colors:
            return f"Color palette: custom colors featuring {custom_colors}."
        elif color_scheme and color_scheme in color_schemes:
            return f"Color palette: {color_schemes[color_scheme]}."
        else:
            return f"Color palette: {theme_data['colors']}."
    
    @classmethod
    def _get_production_level(cls, budget_level):
        """Generate production quality specification"""
        
        production_levels = {
            'budget': 'thoughtful budget-friendly setup with DIY elements, simple elegant arrangements, cost-effective beautiful decorations',
            'moderate': 'professional quality setup with refined details, well-coordinated arrangements, quality decorations',
            'luxury': 'luxury high-end setup with premium materials, designer arrangements, sophisticated elegant details',
            'ultra_luxury': 'ultra-luxury opulent setup with exquisite premium materials, lavish displays, spectacular high-end details'
        }
        
        level = production_levels.get(budget_level, 'professional quality wedding setup with elegant decorations')
        return f"Production quality: {level}."
    
    @classmethod
    def _get_temporal_context(cls, season, time_of_day):
        """Generate seasonal and time context"""
        
        contexts = []
        
        if season:
            seasonal_elements = {
                'spring': 'fresh spring flowers, light flowing fabrics, renewal atmosphere',
                'summer': 'vibrant summer blooms, bright cheerful elements, sunny atmosphere',
                'fall': 'autumn foliage, warm amber elements, cozy harvest atmosphere',
                'winter': 'winter elegance with evergreens, rich textures, festive elements'
            }
            if season in seasonal_elements:
                contexts.append(f"Seasonal elements: {seasonal_elements[season]}")
        
        if time_of_day:
            time_elements = {
                'morning': 'bright morning ambiance, fresh breakfast setup atmosphere',
                'afternoon': 'natural daylight ambiance, relaxed daytime atmosphere',
                'evening': 'golden hour lighting, romantic evening atmosphere',
                'night': 'dramatic evening lighting, elegant nighttime atmosphere'
            }
            if time_of_day in time_elements:
                contexts.append(f"Temporal setting: {time_elements[time_of_day]}")
        
        return " ".join(contexts) + "." if contexts else ""
    
    @classmethod
    def generate_enhanced_negative_prompt(cls):
        """Generate comprehensive negative prompt for SD3.5 Large"""
        negative_elements = [
            # People and crowds (critical for venue photos)
            "people, faces, crowd, guests, bride, groom, wedding party, humans, person, bodies",
            
            # Quality issues specific to SD3.5 Large
            "blurry, low quality, distorted, pixelated, artifacts, noise, low resolution, jpeg artifacts",
            
            # Unwanted content
            "text, watermark, signature, logo, copyright, writing, signs, labels",
            
            # Poor atmosphere
            "dark, dim, gloomy, messy, cluttered, chaotic, unorganized, dirty, shabby",
            
            # Style issues
            "cartoon, anime, unrealistic, fake, artificial, painting, drawing, sketch",
            
            # Composition problems
            "cropped, cut off, partial, incomplete, tilted, askew, bad proportions",
            
            # Unwanted objects
            "cars, vehicles, modern electronics, phones, computers, inappropriate items",
            
            # SD3.5 Large specific negatives
            "overexposed, underexposed, bad lighting, harsh shadows, color bleeding, oversaturated"
        ]
        
        return ", ".join(negative_elements)
    
    @classmethod
    def get_space_optimized_parameters(cls, space_type, wedding_theme, guest_count):
        """Get SD3.5 Large parameters optimized for space transformation success"""
        
        base_params = {
            'strength': 0.4,
            'cfg_scale': 7.0,
            'steps': 50,
            'output_format': 'png',
        }
        
        # Space-specific optimizations (space function is primary)
        space_optimizations = {
            'wedding_ceremony': {'strength': 0.35, 'cfg_scale': 6.5},  # Less aggressive for ceremony spaces
            'dining_area': {'strength': 0.4, 'cfg_scale': 7.0},        # Balanced for dining
            'dance_floor': {'strength': 0.45, 'cfg_scale': 7.5},       # More transformation for entertainment
            'cocktail_hour': {'strength': 0.4, 'cfg_scale': 7.0},      # Balanced for social space
            'lounge_area': {'strength': 0.35, 'cfg_scale': 6.5},       # Gentler for intimate spaces
        }
        
        # Theme-specific fine-tuning (secondary to space)
        theme_adjustments = {
            'rustic': {'cfg_scale': -0.5, 'steps': -5},      # Slightly more organic
            'modern': {'cfg_scale': 0.5, 'steps': 5},        # More precise control
            'industrial': {'cfg_scale': 1.0, 'steps': 10},   # Highest precision
            'vintage': {'cfg_scale': 0.5},                   # Good detail control
            'classic': {'cfg_scale': 0.5},                   # Refined control
        }
        
        # Apply space optimizations first (primary)
        if space_type in space_optimizations:
            base_params.update(space_optimizations[space_type])
        
        # Apply theme adjustments (secondary)
        if wedding_theme in theme_adjustments:
            adj = theme_adjustments[wedding_theme]
            base_params['cfg_scale'] += adj.get('cfg_scale', 0)
            base_params['steps'] += adj.get('steps', 0)
        
        # Guest count adjustments (affects transformation intensity)
        if guest_count in ['large', 'grand']:
            base_params['strength'] += 0.05  # More transformation for larger events
        elif guest_count == 'intimate':
            base_params['strength'] -= 0.05  # Gentler for intimate spaces
        
        # Clamp to valid SD3.5 Large ranges
        base_params['cfg_scale'] = max(1.0, min(20.0, base_params['cfg_scale']))
        base_params['steps'] = max(10, min(150, base_params['steps']))
        base_params['strength'] = max(0.0, min(1.0, base_params['strength']))
        
        return base_params
    
    @classmethod
    def get_space_suggestions(cls, space_type):
        """Get suggestions optimized for specific space types"""
        
        space_suggestions = {
            'wedding_ceremony': {
                'guest_count': 'medium',
                'budget_level': 'moderate',
                'time_of_day': 'afternoon',
                'color_scheme': 'neutral',
                'theme_recommendations': ['classic', 'garden', 'vintage', 'romantic']
            },
            'dining_area': {
                'guest_count': 'medium',
                'budget_level': 'moderate',
                'time_of_day': 'evening',
                'color_scheme': 'neutral',
                'theme_recommendations': ['classic', 'modern', 'vintage', 'elegant']
            },
            'dance_floor': {
                'guest_count': 'large',
                'budget_level': 'luxury',
                'time_of_day': 'night',
                'color_scheme': 'bold_colors',
                'theme_recommendations': ['modern', 'industrial', 'glamorous', 'party']
            },
            'cocktail_hour': {
                'guest_count': 'medium',
                'budget_level': 'moderate',
                'time_of_day': 'evening',
                'color_scheme': 'jewel_tones',
                'theme_recommendations': ['modern', 'classic', 'sophisticated', 'social']
            },
            'lounge_area': {
                'guest_count': 'intimate',
                'budget_level': 'luxury',
                'time_of_day': 'evening',
                'color_scheme': 'pastels',
                'theme_recommendations': ['bohemian', 'vintage', 'comfortable', 'relaxed']
            }
        }
        
        return space_suggestions.get(space_type, space_suggestions['wedding_ceremony'])