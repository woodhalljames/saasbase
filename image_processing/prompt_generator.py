# image_processing/prompt_generator.py - Enhanced Wedding Venue Transformation System
"""
Enhanced prompt generation system with vivid descriptions and imaginative details
Always generates rich, detailed prompts optimized for Stability AI SD3.5 Large
"""

class WeddingPromptGenerator:
    """Generate vivid, imaginative prompts for wedding venue transformations"""
    
    @classmethod
    def generate_space_first_prompt(cls, wedding_theme, space_type, guest_count=None, 
                                   budget_level=None, season=None, time_of_day=None,
                                   color_scheme=None, custom_colors=None, additional_details=None):
        """
        Generate rich, detailed prompts with vivid descriptions
        """
        
        space_data = cls.SPACE_DEFINITIONS.get(space_type, cls.SPACE_DEFINITIONS['wedding_ceremony'])
        theme_data = cls.THEME_STYLING.get(wedding_theme, cls.THEME_STYLING.get('classic'))
        
        # Build dynamic elements based on ALL user inputs
        dynamic_elements = cls._build_dynamic_elements(
            guest_count, budget_level, season, time_of_day, color_scheme, custom_colors
        )
        
        # 1. PHOTOGRAPHIC QUALITY
        quality_foundation = "Ultra-high resolution professional wedding photography, photorealistic details, magazine-quality composition, perfect lighting, breathtaking atmosphere."
        
        # 2. VIVID SPACE TRANSFORMATION
        space_transformation = f"Dramatically transform this space into {space_data['description']}."
        
        # 3. DETAILED THEME IMPLEMENTATION
        theme_implementation = cls._get_theme_details(
            wedding_theme, space_type, theme_data, dynamic_elements
        )
        
        # 4. ATMOSPHERIC ELEMENTS
        atmosphere = cls._create_atmosphere(theme_data, season, time_of_day)
        
        # 5. DECORATIVE DETAILS
        decorative_details = cls._get_decorative_details(
            theme_data, space_type, guest_count, budget_level, color_scheme, custom_colors
        )
        
        # 6. USER VISION INTEGRATION
        user_vision = cls._integrate_user_vision(additional_details, theme_data)
        
        # 7. TECHNICAL EXCELLENCE
        technical_specs = "Golden hour lighting quality, bokeh depth of field, ultra-detailed textures, 8K resolution rendering."
        
        # ASSEMBLE PROMPT
        prompt_sections = [
            quality_foundation,
            space_transformation,
            theme_implementation,
            decorative_details,
            atmosphere,
            user_vision,
            technical_specs,
            "Empty venue ready for guests, no people visible."
        ]
        
        # Clean and join with proper flow
        final_prompt = " ".join([s.strip() for s in prompt_sections if s.strip()])
        
        # Enhanced negative prompt specific to theme
        negative_prompt = cls._get_enhanced_negative_prompt(wedding_theme)
        
        return {
            'prompt': final_prompt,
            'negative_prompt': negative_prompt,
            'recommended_params': cls._get_optimized_parameters(space_type, wedding_theme, budget_level)
        }
    
    # VIVID SPACE DEFINITIONS - Always rich and detailed
    SPACE_DEFINITIONS = {
        'wedding_ceremony': {
            'function': 'sacred wedding ceremony space',
            'description': 'an enchanting wedding ceremony sanctuary with a breathtaking processional aisle lined with romantic details, elegant guest seating arranged in perfect symmetry, and a stunning ceremonial focal point',
            'layout': 'perfectly aligned rows of decorated chairs facing an elevated altar area, dramatic center aisle with decorative runner',
            'elements': 'magnificent floral arch or architectural altar, decorated aisle markers, ceremonial platform, ambient lighting installations',
            'requirements': 'dramatic focal point for vows, photogenic ceremony backdrop, acoustic perfection for intimate moments'
        },
        'dance_floor': {
            'function': 'vibrant celebration dance space',
            'description': 'an electrifying dance floor paradise with gleaming floors reflecting spectacular lighting, surrounded by plush lounge areas and state-of-the-art entertainment setup',
            'layout': 'spacious central dance area with mood lighting, perimeter VIP seating, professional DJ/band stage',
            'elements': 'mirror-finish dance floor, intelligent lighting rigs, LED uplighting, comfortable banquettes, entertainment platform',
            'requirements': 'dynamic lighting systems, premium sound setup, energetic atmosphere creation'
        },
        'dining_area': {
            'function': 'elegant reception dining experience',
            'description': 'a sophisticated dining paradise with beautifully appointed tables, stunning centerpieces reaching toward dramatic ceiling treatments, and ambient lighting creating magical intimacy',
            'layout': 'strategically placed round tables with chiavari chairs, head table prominence, graceful service corridors',
            'elements': 'elaborate floral centerpieces, fine china and crystal, dramatic table linens, suspended installations, candlelit ambiance',
            'requirements': 'perfect table spacing, elegant place settings, memorable dining atmosphere'
        },
        'cocktail_hour': {
            'function': 'sophisticated cocktail reception space',
            'description': 'a chic cocktail lounge atmosphere with stylish high-top tables, artfully designed bar areas, and intimate conversation nooks bathed in warm ambient lighting',
            'layout': 'flowing space with cocktail tables, multiple bar stations, cozy seating vignettes',
            'elements': 'illuminated bar displays, decorative cocktail tables, appetizer stations with elegant displays, lounge furniture groupings',
            'requirements': 'social flow optimization, multiple service points, sophisticated ambiance'
        },
        'lounge_area': {
            'function': 'luxurious relaxation retreat',
            'description': 'an intimate lounge oasis with sumptuous seating arrangements, soft mood lighting, and thoughtfully curated comfort zones for meaningful conversations',
            'layout': 'multiple conversation areas with plush furniture, ambient lighting zones, decorative privacy elements',
            'elements': 'velvet sofas, ottoman groupings, decorative pillows, soft area rugs, artistic lighting features, botanical accents',
            'requirements': 'ultimate comfort seating, conversation-friendly acoustics, romantic ambiance'
        }
    }
    
    # RICH THEME STYLING - Always vivid and detailed
    THEME_STYLING = {
        'rustic': {
            'elements': 'weathered wood farm tables with burlap runners, cascading wildflower arrangements in mason jars, vintage ladder displays with family photos, wine barrel cocktail tables, antique lanterns with pillar candles',
            'details': 'exposed wooden beams wrapped in twinkling fairy lights, hay bale lounge seating with plaid blankets, rustic wooden signs with calligraphy, vintage milk jugs filled with sunflowers, wooden crates overflowing with seasonal blooms',
            'lighting': 'warm Edison bulb string lights creating canopy of stars, mason jar chandeliers, candlelit lanterns on shepherd hooks',
            'colors': 'warm honey wood, sage green, dusty rose, cream, natural burlap, touches of navy blue',
            'atmosphere': 'cozy barn celebration with authentic countryside charm, nostalgic and heartwarming',
            'textures': 'rough-hewn wood, soft burlap, delicate lace, galvanized metal, natural jute'
        },
        'modern': {
            'elements': 'sleek acrylic ghost chairs, geometric gold centerpieces, minimalist orchid arrangements, LED light installations, mirror-top tables',
            'details': 'dramatic geometric backdrops in metallic tones, floating acrylic shelves with candles, angular floral designs with tropical leaves, crystalline chandeliers, holographic details',
            'lighting': 'programmable LED uplighting in cool tones, geometric pendant lights, laser-cut shadow projections',
            'colors': 'crisp white, charcoal grey, metallic gold, black accents, pops of emerald green',
            'atmosphere': 'sophisticated urban gallery feel with cutting-edge design elements',
            'textures': 'polished marble, brushed metal, smooth acrylic, velvet accents, glass surfaces'
        },
        'vintage': {
            'elements': 'antique gold candelabras, lace table overlays, pearl details, vintage china place settings, ornate picture frames',
            'details': 'cascading roses in soft pastels, vintage typewriters for guest messages, antique books as centerpiece bases, Victorian furniture vignettes, silk ribbon details',
            'lighting': 'crystal chandeliers with warm amber glow, antique brass sconces, strings of pearl lights',
            'colors': 'blush pink, champagne, dusty blue, antique gold, ivory, lavender',
            'atmosphere': 'romantic time capsule with old-world elegance and nostalgic beauty',
            'textures': 'delicate lace, worn velvet, aged brass, soft tulle, vintage brocade'
        },
        'bohemian': {
            'elements': 'macrame ceremony backdrops, pampas grass clouds, moroccan poufs, tapestry table runners, dreamcatcher details',
            'details': 'layered vintage rugs creating aisle, suspended dried flower installations, eclectic mix of colored glassware, feather accents, mandala projections',
            'lighting': 'moroccan lanterns casting intricate shadows, firefly lights in glass orbs, candles in geometric holders',
            'colors': 'terracotta, sage, mustard, deep purple, dusty pink, turquoise accents',
            'atmosphere': 'free-spirited desert festival with artistic soul and wanderlust spirit',
            'textures': 'woven textiles, fringe details, natural fibers, hammered metals, dried botanicals'
        },
        'classic': {
            'elements': 'crystal chandeliers, white rose centerpieces, gold-rimmed china, silk drapery, ornate candelabras',
            'details': 'towering floral arrangements with roses and peonies, gold chiavari chairs with ivory cushions, monogrammed details, pearl accents, formal place cards',
            'lighting': 'grand crystal chandeliers, soft candlelight, warm white uplighting, elegant sconces',
            'colors': 'pure white, ivory, champagne gold, soft blush, silver accents',
            'atmosphere': 'timeless traditional elegance with formal sophistication and refined grace',
            'textures': 'smooth silk, crisp linen, polished silver, crystal glass, fresh rose petals'
        },
        'garden': {
            'elements': 'overflowing floral installations, living walls, butterfly releases, garden arch with climbing roses, moss-covered details',
            'details': 'suspended flower clouds, botanical print linens, potted herb centerpieces, vintage watering cans with wildflowers, secret garden pathways',
            'lighting': 'natural sunlight filtering through leaves, paper lanterns in trees, firefly jar lights',
            'colors': 'every shade of green, soft white, peach, lavender, butter yellow, rose pink',
            'atmosphere': 'enchanted botanical wonderland with natural romance and organic beauty',
            'textures': 'fresh petals, natural wood, woven baskets, stone elements, living moss'
        },
        'beach': {
            'elements': 'driftwood arbors, nautical rope details, seashell accents, flowing white fabric pavilions, tiki torches',
            'details': 'aisle lined with conch shells and starfish, hurricane lanterns on posts, coral centerpieces, message-in-bottle favors, barefoot luxury details',
            'lighting': 'sunset golden hour glow, tiki torch flames, lanterns reflecting on water, string lights between palm trees',
            'colors': 'ocean blues, sandy neutrals, coral pink, seafoam green, sunset orange, crisp white',
            'atmosphere': 'tropical paradise with ocean breeze and barefoot elegance',
            'textures': 'weathered wood, rope details, smooth shells, flowing linen, natural raffia'
        },
        'industrial': {
            'elements': 'exposed brick walls, metal beam structures, Edison bulb installations, concrete planters, copper pipe fixtures',
            'details': 'geometric metal centerpieces, leather furniture accents, wire basket displays, urban greenery walls, minimalist concrete details',
            'lighting': 'exposed Edison bulb chandeliers, industrial pendant lights, copper string lights, neon accent signs',
            'colors': 'charcoal grey, copper, warm brass, concrete gray, deep burgundy, forest green',
            'atmosphere': 'urban warehouse chic with raw elegance and modern edge',
            'textures': 'rough brick, smooth concrete, aged metal, worn leather, industrial glass'
        },
        'glamorous': {
            'elements': 'crystal curtain backdrops, sequined linens, mirror furniture, chandelier installations, metallic balloons',
            'details': 'floor-to-ceiling sequin walls, acrylic boxes filled with roses, LED dance floor, champagne towers, glitter canon reveals',
            'lighting': 'cascading crystal chandeliers, pin-spot lighting on centerpieces, sparkler effects, mirror ball reflections',
            'colors': 'rose gold, champagne, black, crystal white, touches of blush',
            'atmosphere': 'Hollywood red carpet luxury with maximum sparkle and drama',
            'textures': 'sequins, crystals, mirrors, metallic surfaces, plush velvet'
        },
        # Cultural themes with rich details
        'japanese_zen': {
            'elements': 'bamboo screens, cherry blossom branches, minimalist wooden platforms, paper lanterns, zen rock gardens',
            'details': 'origami crane installations, sake ceremony setup, low wooden tables with floor cushions, ikebana floral arrangements, bamboo water features',
            'lighting': 'soft paper lantern glow, bamboo torches, candles floating in water, subtle accent lighting',
            'colors': 'soft pink cherry blossom, natural bamboo, white, sage green, charcoal black',
            'atmosphere': 'serene zen sanctuary with minimalist harmony and peaceful elegance',
            'textures': 'smooth bamboo, rice paper, polished wood, river stones, silk fabrics'
        },
        'moroccan_nights': {
            'elements': 'ornate metal lanterns, rich tapestries, low cushioned seating, brass tea sets, mosaic details',
            'details': 'jewel-toned fabric draping, intricate tile patterns, brass tray tables, colorful poufs, hookah lounge areas',
            'lighting': 'hundreds of moroccan lanterns, candlelit ambiance, warm amber uplighting, projected patterns',
            'colors': 'deep purple, rich gold, turquoise, burnt orange, ruby red, midnight blue',
            'atmosphere': 'exotic Arabian nights palace with luxurious mystique and sensory richness',
            'textures': 'embroidered fabrics, hammered metal, smooth tiles, plush cushions, woven rugs'
        },
        'tropical_paradise': {
            'elements': 'palm frond installations, tropical flower arrangements, bamboo structures, tiki elements, fruit displays',
            'details': 'hanging orchid gardens, pineapple centerpieces, monstera leaf table runners, flamingo accents, coconut details',
            'lighting': 'tiki torches, string lights through palms, colored uplighting, sunset projections',
            'colors': 'hot pink, lime green, turquoise, sunset orange, golden yellow, palm green',
            'atmosphere': 'vibrant island paradise with tropical exuberance and vacation luxury',
            'textures': 'natural palm fronds, smooth bamboo, tropical flowers, woven grass, painted wood'
        }
    }
    
    @classmethod
    def _build_dynamic_elements(cls, guest_count, budget_level, season, time_of_day, color_scheme, custom_colors):
        """Build rich dynamic elements from user inputs"""
        elements = {}
        
        # Guest count impacts scale and grandeur
        if guest_count == 'intimate':
            elements['scale'] = 'intimate gathering with personal touches at every seat, cozy atmosphere'
        elif guest_count == 'medium':
            elements['scale'] = 'perfectly balanced celebration space with comfortable flow'
        elif guest_count == 'large':
            elements['scale'] = 'grand celebration with impressive scale and dramatic proportions'
        elif guest_count == 'grand':
            elements['scale'] = 'spectacular ballroom-scale magnificence with breathtaking grandeur'
        
        # Budget impacts luxury details
        if budget_level == 'budget':
            elements['luxury'] = 'thoughtfully curated DIY elegance with handcrafted charm'
        elif budget_level == 'moderate':
            elements['luxury'] = 'professionally designed with polished details and refined touches'
        elif budget_level == 'luxury':
            elements['luxury'] = 'luxury appointments with premium materials and exquisite craftsmanship'
        elif budget_level == 'ultra_luxury':
            elements['luxury'] = 'no-expense-spared opulence with extraordinary details and rare elements'
        
        # Season adds specific elements
        if season:
            seasonal_elements = {
                'spring': 'cherry blossoms, tulips, daffodils, fresh greenery, pastel ribbons, butterfly accents',
                'summer': 'sunflowers, bright dahlias, citrus accents, tropical leaves, vibrant colors',
                'fall': 'autumn leaves, pumpkins, warm amber tones, harvest wheat, burgundy dahlias',
                'winter': 'evergreen garlands, silver branches, white roses, crystal icicles, velvet ribbons'
            }
            elements['seasonal'] = seasonal_elements.get(season, '')
        
        # Time creates lighting mood
        if time_of_day:
            time_moods = {
                'morning': 'bright natural morning light streaming through windows creating fresh ambiance',
                'afternoon': 'warm afternoon sunshine creating golden pools of light',
                'evening': 'romantic sunset glow transitioning to candlelit intimacy',
                'night': 'dramatic uplighting with twinkling stars and moonlight atmosphere'
            }
            elements['lighting_mood'] = time_moods.get(time_of_day, '')
        
        # Colors override default palette
        if custom_colors:
            elements['colors'] = f"sophisticated custom color palette featuring {custom_colors} throughout all decorative elements"
        elif color_scheme:
            scheme_palettes = {
                'neutral': 'elegant neutrals with white, cream, beige, champagne, and taupe',
                'pastels': 'romantic soft pastels with blush pink, lavender, mint green, butter yellow',
                'jewel_tones': 'rich luxurious jewel tones with emerald, sapphire, ruby, amethyst',
                'earth_tones': 'organic earth tones with terracotta, sage, sand, warm browns',
                'monochrome': 'dramatic black and white with metallic silver and gold accents',
                'bold_colors': 'vibrant celebration colors with fuchsia, orange, turquoise, lime'
            }
            elements['colors'] = scheme_palettes.get(color_scheme, '')
        
        return elements
    
    @classmethod
    def _get_theme_details(cls, theme, space_type, theme_data, dynamic_elements):
        """Create rich, specific theme implementation"""
        
        # Base theme elements with vivid details
        details = [f"Luxuriously decorated in {theme} style featuring {theme_data.get('details', '')}"]
        
        # Add dynamic scale
        if 'scale' in dynamic_elements:
            details.append(dynamic_elements['scale'])
        
        # Add luxury level details
        if 'luxury' in dynamic_elements:
            details.append(f"showcasing {dynamic_elements['luxury']}")
        
        # Add seasonal elements
        if 'seasonal' in dynamic_elements:
            details.append(f"adorned with seasonal {dynamic_elements['seasonal']}")
        
        # Space-specific theme adaptations with rich details
        space_adaptations = {
            'wedding_ceremony': f"ceremony space magnificently adorned with {theme_data.get('elements', '')}",
            'dance_floor': f"party atmosphere electrified by {theme_data.get('lighting', '')}",
            'dining_area': f"dining tables luxuriously appointed with {theme_data.get('textures', '')}",
            'cocktail_hour': f"social spaces artfully styled with {theme_data.get('details', '')}",
            'lounge_area': f"comfort zones sumptuously decorated with {theme_data.get('textures', '')}"
        }
        
        if space_type in space_adaptations:
            details.append(space_adaptations[space_type])
        
        return " ".join(details)
    
    @classmethod
    def _create_atmosphere(cls, theme_data, season, time_of_day):
        """Create vivid atmospheric description"""
        
        atmosphere_parts = [theme_data.get('atmosphere', '')]
        
        # Add time-based lighting with rich descriptions
        if time_of_day:
            time_atmospheres = {
                'morning': 'bathed in fresh golden morning light with dewdrops sparkling like diamonds',
                'afternoon': 'glowing in warm honeyed afternoon sunshine with soft shadows',
                'evening': 'romantic golden hour ambiance with sunset painting everything in warm hues',
                'night': 'enchanted evening atmosphere with thousands of twinkling lights under starlit sky'
            }
            atmosphere_parts.append(time_atmospheres.get(time_of_day, ''))
        
        # Add seasonal atmosphere with sensory details
        if season:
            seasonal_atmospheres = {
                'spring': 'fresh spring air filled with floral fragrance and new beginnings',
                'summer': 'warm summer celebration energy with golden sunshine and joy',
                'fall': 'cozy autumn warmth with rich harvest abundance and golden leaves',
                'winter': 'magical winter wonderland sparkle with crystalline beauty'
            }
            atmosphere_parts.append(seasonal_atmospheres.get(season, ''))
        
        return f"Atmosphere: {', '.join([a for a in atmosphere_parts if a])}."
    
    @classmethod
    def _get_decorative_details(cls, theme_data, space_type, guest_count, budget_level, color_scheme, custom_colors):
        """Generate specific decorative elements with rich details"""
        
        details = []
        
        # Theme-specific decorations with vivid descriptions
        details.append(f"Spectacular decorative elements including {theme_data.get('elements', '')}")
        
        # Color implementation with artistic description
        if custom_colors:
            details.append(f"Artistic color story expressed through {custom_colors} woven throughout all decorative elements")
        elif color_scheme:
            details.append(f"Cohesive {color_scheme} creating visual harmony throughout the space")
        else:
            details.append(f"Rich color palette of {theme_data.get('colors', '')} creating stunning visual impact")
        
        # Texture layers with sensory appeal
        details.append(f"Luxurious layered textures including {theme_data.get('textures', '')} adding depth and richness")
        
        # Lighting design with dramatic effect
        details.append(f"Breathtaking lighting design featuring {theme_data.get('lighting', '')} creating magical ambiance")
        
        return " ".join(details)
    
    @classmethod
    def _integrate_user_vision(cls, additional_details, theme_data):
        """Prioritize and integrate user's specific vision"""
        
        if not additional_details:
            return ""
        
        # Give high weight to user specifications with emphasis
        return f"IMPORTANT featured elements: {additional_details}. These specific details must be prominently showcased in the transformation."
    
    @classmethod
    def _get_enhanced_negative_prompt(cls, wedding_theme):
        """Theme-specific negative prompts for better results"""
        
        base_negatives = [
            "people, faces, crowd, guests, bride, groom, wedding party, humans",
            "blurry, low quality, distorted, pixelated, amateur, ugly",
            "text, watermark, signature, logo, writing",
            "messy, cluttered, unorganized, dirty, broken",
            "cartoon, anime, illustration, painting, drawing"
        ]
        
        # Theme-specific negatives to avoid conflicting styles
        theme_negatives = {
            'rustic': "modern furniture, sleek surfaces, urban elements, minimalist, futuristic, industrial",
            'modern': "vintage items, antique furniture, rustic wood, old-fashioned, weathered, shabby",
            'vintage': "modern technology, contemporary furniture, minimalist design, industrial elements",
            'bohemian': "formal arrangements, rigid structure, traditional setup, corporate feeling",
            'garden': "industrial materials, urban elements, concrete, artificial flowers, plastic",
            'beach': "mountain elements, forest themes, urban settings, snow, desert",
            'glamorous': "casual elements, rustic items, simple decorations, understated, plain",
            'industrial': "frilly decorations, vintage lace, rustic farm elements, beach themes"
        }
        
        if wedding_theme in theme_negatives:
            base_negatives.append(theme_negatives[wedding_theme])
        
        return ", ".join(base_negatives)
    
    @classmethod
    def _get_optimized_parameters(cls, space_type, wedding_theme, budget_level):
        """Get optimized SD3.5 Large parameters"""
        
        base_params = {
            'strength': 0.42,  # Slightly higher for more transformation
            'cfg_scale': 7.5,
            'steps': 55,  # More steps for better quality
            'output_format': 'png',
        }
        
        # Space-specific optimizations
        space_params = {
            'wedding_ceremony': {'strength': 0.38, 'cfg_scale': 7.0, 'steps': 60},
            'dining_area': {'strength': 0.42, 'cfg_scale': 7.5, 'steps': 55},
            'dance_floor': {'strength': 0.48, 'cfg_scale': 8.0, 'steps': 60},
            'cocktail_hour': {'strength': 0.42, 'cfg_scale': 7.5, 'steps': 55},
            'lounge_area': {'strength': 0.38, 'cfg_scale': 7.0, 'steps': 55},
        }
        
        # Budget level affects quality settings
        budget_params = {
            'budget': {'steps': -5, 'cfg_scale': -0.5},
            'moderate': {'steps': 0, 'cfg_scale': 0},
            'luxury': {'steps': 10, 'cfg_scale': 0.5},
            'ultra_luxury': {'steps': 15, 'cfg_scale': 1.0}
        }
        
        # Apply space settings
        if space_type in space_params:
            base_params.update(space_params[space_type])
        
        # Apply budget adjustments
        if budget_level in budget_params:
            adj = budget_params[budget_level]
            base_params['steps'] += adj.get('steps', 0)
            base_params['cfg_scale'] += adj.get('cfg_scale', 0)
        
        # Ensure valid ranges
        base_params['cfg_scale'] = max(1.0, min(20.0, base_params['cfg_scale']))
        base_params['steps'] = max(10, min(150, base_params['steps']))
        base_params['strength'] = max(0.0, min(1.0, base_params['strength']))
        
        return base_params