# image_processing/prompt_generator.py - Enhanced Wedding Designer Edition
"""
Professional Wedding Designer & Planner Prompt Generation System
Incorporating 2024-2025 trends, luxury transformation techniques, and cultural fusion elements
Creates magazine-worthy venue transformations that clients will love
"""

class WeddingPromptGenerator:
    """Generate stunning, professional-grade prompts optimized for Stable Image Ultra"""
    
    @classmethod
    def generate_space_first_prompt(cls, wedding_theme, space_type, guest_count=None, 
                                   budget_level=None, season=None, time_of_day=None,
                                   color_scheme=None, custom_colors=None, additional_details=None):
        """
        Generate luxury venue transformation prompts with professional designer expertise
        """
        
        space_data = cls.SPACE_DEFINITIONS.get(space_type, cls.SPACE_DEFINITIONS['wedding_ceremony'])
        theme_data = cls.ENHANCED_THEME_STYLING.get(wedding_theme, cls.ENHANCED_THEME_STYLING['classic'])
        
        # 1. SPACE TRANSFORMATION - Clear and direct
        space_transformation = f"Transform this space into {space_data['function']}"
        
        # 2. CAPACITY AND SCALE - Professional scale planning
        capacity_spec = cls._get_professional_capacity_spec(guest_count, space_type, space_data)
        
        # 3. VENUE ARCHITECTURE - Key structural elements
        venue_elements = f"{space_data['elements']}, {space_data['layout_features']}"
        
        # 4. LUXURY TRANSFORMATION TECHNIQUES - Professional methods
        transformation_techniques = cls._get_transformation_techniques(theme_data, space_type)
        
        # 5. THEME IMMERSION - Complete thematic experience
        theme_experience = f"{wedding_theme} wedding theme with {theme_data['signature_elements']}"
        
        # 6. PROFESSIONAL LIGHTING DESIGN - Mood and ambiance
        lighting_design = f"Professional lighting: {theme_data['lighting_design']}"
        
        # 7. LUXURY MATERIALS & TEXTURES - High-end finishes
        luxury_finishes = f"Luxury materials: {theme_data['luxury_materials']}"
        
        # 8. COLOR MASTERY - Professional color coordination
        color_palette = cls._get_professional_color_palette(color_scheme, custom_colors, theme_data)
        
        # 9. SEASONAL & CONTEXTUAL ENHANCEMENT - When relevant
        contextual_elements = cls._get_contextual_enhancements(season, time_of_day, budget_level)
        
        # 10. FINISHING TOUCHES - Professional polish
        finishing_details = f"Finishing touches: {theme_data['finishing_details']}"
        
        # 11. USER PERSONALIZATION - Custom requests
        personal_touches = f"Custom details: {additional_details}" if additional_details else ""
        
        # 12. PROFESSIONAL OUTPUT SPEC - Final requirements
        output_spec = f"Professional result: spectacular {wedding_theme} wedding venue transformation, celebration-ready space, no people visible, magazine-quality setup"
        
        # ASSEMBLE DESIGNER-QUALITY PROMPT
        prompt_elements = [
            space_transformation + ".",
            capacity_spec + ".",
            venue_elements + ".",
            transformation_techniques + ".",
            theme_experience + ".",
            lighting_design + ".",
            luxury_finishes + ".",
            color_palette + ".",
            contextual_elements,
            finishing_details + ".",
            personal_touches,
            output_spec + "."
        ]
        
        # Clean and assemble
        final_prompt = " ".join([element.strip() for element in prompt_elements if element.strip()])
        
        # Professional negative prompt
        negative_prompt = cls.generate_professional_negative_prompt()
        
        return {
            'prompt': final_prompt,
            'negative_prompt': negative_prompt,
            'recommended_params': cls.get_ultra_designer_parameters(space_type, wedding_theme, guest_count)
        }
    
    # ENHANCED SPACE DEFINITIONS - Professional venue planning
    SPACE_DEFINITIONS = {
        'wedding_ceremony': {
            'function': 'an elegant wedding ceremony venue with processional grandeur and intimate guest seating',
            'elements': 'stunning ceremony altar or floral arch, organized guest seating rows, dramatic center aisle, unity ceremony area, bridal party positioning',
            'layout_features': 'clear sightlines to ceremonial focal point, processional pathway with petal scatter, professional sound considerations'
        },
        'dance_floor': {
            'function': 'a glamorous dance floor entertainment area with luxury lounge seating',
            'elements': 'polished dance floor surface, professional DJ booth with LED panels, sophisticated perimeter lounge seating, dramatic overhead lighting installations, VIP seating areas',
            'layout_features': 'central dance space with intimate conversation zones, elevated DJ area, flow between dance and lounge areas'
        },
        'dining_area': {
            'function': 'an exquisite dining space for sophisticated wedding reception service',
            'elements': 'elegantly appointed dining tables, luxury chair selections, show-stopping centerpieces, refined place settings, butler service stations',
            'layout_features': 'optimized table spacing for service flow, clear pathways for seamless service, intimate dining clusters'
        },
        'cocktail_hour': {
            'function': 'a chic cocktail reception area for sophisticated guest mingling',
            'elements': 'stylish high-top cocktail tables, elegant bar installations, interactive food stations, designer lounge groupings, ambient lighting features',
            'layout_features': 'multiple conversation zones, strategic bar placement, flow between indoor and outdoor areas'
        },
        'lounge_area': {
            'function': 'a luxurious lounge space for intimate conversations and relaxation',
            'elements': 'plush designer sofas and armchairs, artisan coffee tables, statement lighting fixtures, curated art pieces, intimate seating clusters',
            'layout_features': 'cozy conversation groupings, soft ambient lighting, private intimate corners'
        }
    }
    
    # ENHANCED THEME STYLING - Professional designer specifications
    ENHANCED_THEME_STYLING = {
        # CLASSIC POPULAR THEMES - Enhanced with 2024-2025 trends
        'rustic': {
            'signature_elements': 'reclaimed barn wood installations, cascading wildflower arrangements, vintage mason jar chandeliers, burlap table runners with lace overlays, string light canopies, antique furniture pieces',
            'lighting_design': 'warm Edison bulb installations, mason jar pendant lighting, flickering candles in wooden lanterns, fairy lights woven through ceiling beams',
            'luxury_materials': 'weathered wood textures, natural linen fabrics, wrought iron accents, vintage brass fixtures, handcrafted pottery',
            'finishing_details': 'vintage signage with calligraphy, rustic photo displays, herb-scented table runners, artisanal bread service',
            'color_palette': 'warm sage green, dusty rose, cream ivory, natural wood tones, burnt orange accents'
        },
        'modern': {
            'signature_elements': 'sleek geometric furniture designs, contemporary acrylic chairs, minimalist floral arrangements, clean-lined architectural elements, LED integration, metallic accents',
            'lighting_design': 'geometric pendant installations, LED strip lighting, contemporary chandeliers, dramatic uplighting with color-changing capabilities',
            'luxury_materials': 'polished marble surfaces, brushed metal finishes, crystal glass elements, high-gloss lacquers, contemporary ceramics',
            'finishing_details': 'digital displays with custom graphics, contemporary art installations, modern sculptural centerpieces, tech-integrated guest experiences',
            'color_palette': 'pure white, charcoal gray, metallic silver, black accents, crystal clear elements'
        },
        'vintage': {
            'signature_elements': 'authentic antique furniture collections, ornate crystal chandeliers, vintage lace table overlays, classic rose garden arrangements, antique china place settings, vintage photo displays',
            'lighting_design': 'crystal chandelier installations, antique brass candelabras, warm Edison bulbs in vintage fixtures, romantic candlelight clusters',
            'luxury_materials': 'silk damask fabrics, ornate gold leaf details, vintage crystal glassware, antique silver serving pieces, handcrafted lace elements',
            'finishing_details': 'vintage postcard displays, antique book centerpieces, heritage family photos, vintage perfume bottle arrangements',
            'color_palette': 'blush pink, ivory cream, antique gold, dusty blue, champagne tones'
        },
        'bohemian': {
            'signature_elements': 'macrame wall hangings, oversized pampas grass installations, colorful vintage rugs, floor cushion seating areas, hanging plants in woven baskets, dreamcatcher installations',
            'lighting_design': 'hanging Moroccan lanterns, fairy lights in glass terrariums, candles in eclectic vintage holders, warm ambient string lights',
            'luxury_materials': 'handwoven textiles, natural fiber rugs, artisan ceramics, vintage brass accents, exotic wood elements',
            'finishing_details': 'vintage tapestry backdrops, succulent garden displays, artisan-made table runners, eclectic vintage glassware',
            'color_palette': 'terracotta orange, sage green, mustard yellow, deep burgundy, natural earth tones'
        },
        'classic': {
            'signature_elements': 'elegant formal furniture, crystal chandelier installations, pristine white linens with gold accents, classic white rose arrangements, formal china place settings, traditional architectural details',
            'lighting_design': 'grand crystal chandeliers, elegant uplighting, classic candelabra arrangements, refined ambient lighting',
            'luxury_materials': 'silk tablecloths, crystal stemware, gold-rimmed china, marble accents, polished silver details',
            'finishing_details': 'formal place cards with calligraphy, elegant menu presentations, classic floral arrangements, refined napkin presentations',
            'color_palette': 'pure white, ivory, champagne gold, silver accents, classic elegance tones'
        },
        
        # CULTURAL & INTERNATIONAL THEMES - Enhanced with authenticity
        'indian_palace': {
            'signature_elements': 'ornate golden mandap structure, rich silk draping in jewel tones, marigold flower cascades, intricate henna-pattern table runners, brass lantern installations, peacock feather accents',
            'lighting_design': 'ornate brass lanterns with warm LED, golden uplighting, hanging diyas with flickering candles, colorful string lights creating mandala patterns',
            'luxury_materials': 'rich silk brocades, gold leaf details, ornate brass fixtures, hand-carved wooden elements, jewel-toned fabrics',
            'finishing_details': 'rangoli floor patterns, traditional copper vessels, marigold petal carpets, ornate elephant figurines, gold-threaded table runners',
            'color_palette': 'rich gold, deep red, royal purple, saffron orange, emerald green'
        },
        'japanese_zen': {
            'signature_elements': 'minimalist bamboo screen installations, cherry blossom branch arrangements, low wooden tables, paper lantern clusters, zen garden elements, flowing water features',
            'lighting_design': 'soft paper lantern installations, warm bamboo pendant lights, subtle LED strip lighting, candles in stone holders',
            'luxury_materials': 'natural bamboo textures, handcrafted ceramics, silk screen panels, natural stone elements, woven grass mats',
            'finishing_details': 'origami crane displays, bonsai tree centerpieces, traditional sake service, bamboo place settings, zen stone arrangements',
            'color_palette': 'soft pink cherry blossom, natural bamboo, sage green, cream white, charcoal gray'
        },
        'moroccan_nights': {
            'signature_elements': 'ornate metallic lantern installations, rich tapestry wall hangings, low cushioned seating areas, intricate tile pattern displays, hanging fabric canopies, exotic spice arrangements',
            'lighting_design': 'ornate Moroccan lanterns casting intricate shadows, warm golden uplighting, candles in colorful glass holders, string lights creating geometric patterns',
            'luxury_materials': 'rich velvet cushions, ornate metalwork, handwoven rugs, exotic wood carvings, jewel-toned silks',
            'finishing_details': 'traditional tea service displays, exotic flower arrangements, ornate mirror installations, handcrafted pottery displays',
            'color_palette': 'deep jewel tones, rich purple, gold, turquoise, burgundy, warm orange'
        },
        'french_chateau': {
            'signature_elements': 'elegant antique furniture, crystal chandelier installations, fine French lace details, lavender and rose arrangements, vintage wine barrel accents, ornate mirror displays',
            'lighting_design': 'French crystal chandeliers, elegant candelabra arrangements, warm ambient lighting, vintage French pendant lights',
            'luxury_materials': 'fine French lace, antique gold details, crystal stemware, vintage silver serving pieces, silk damask fabrics',
            'finishing_details': 'French vintage postcards, antique perfume bottles, lavender bundles, vintage French wine displays, elegant calligraphy signage',
            'color_palette': 'champagne, soft lavender, antique gold, cream white, dusty rose'
        },
        'greek_island': {
            'signature_elements': 'whitewashed furniture and architectural elements, azure blue fabric accents, olive branch arrangements, Mediterranean pottery displays, nautical rope details, coastal driftwood accents',
            'lighting_design': 'white lantern installations, natural Mediterranean lighting, string lights mimicking stars, candles in sea glass holders',
            'luxury_materials': 'natural white linens, azure blue ceramics, olive wood accents, sea glass elements, whitewashed wood textures',
            'finishing_details': 'olive branch centerpieces, Mediterranean herb displays, nautical rope details, sea shell accents, traditional Greek pottery',
            'color_palette': 'pure white, azure blue, olive green, sandy beige, natural stone gray'
        },
        
        # TRENDY 2024-2025 THEMES - Current and exciting
        'luxe_minimalism': {
            'signature_elements': 'clean geometric furniture, high-quality natural materials, statement sculptural pieces, subtle metallic accents, architectural lighting, premium textile selections',
            'lighting_design': 'architectural LED installations, geometric pendant lights, subtle uplighting, contemporary chandeliers with clean lines',
            'luxury_materials': 'premium marble surfaces, brushed gold details, high-thread-count linens, contemporary ceramics, natural stone elements',
            'finishing_details': 'sculptural centerpieces, contemporary art pieces, premium glassware, minimalist floral arrangements, architectural details',
            'color_palette': 'warm whites, soft grays, champagne gold, natural stone tones, subtle blush accents'
        },
        'maximalist_glamour': {
            'signature_elements': 'bold patterned fabrics, mixing metallic finishes, oversized floral installations, dramatic ceiling treatments, eclectic furniture mixing, statement art pieces',
            'lighting_design': 'dramatic chandelier installations, colorful uplighting, decorative string lights, bold pendant combinations, theatrical spotlighting',
            'luxury_materials': 'rich velvet fabrics, mixed metallic finishes, ornate glassware, dramatic silk draping, jewel-toned accents',
            'finishing_details': 'oversized floral arrangements, eclectic vintage collections, bold patterned linens, dramatic ceiling installations, statement candelabras',
            'color_palette': 'rich jewel tones, mixed metallics, bold florals, dramatic contrasts, vibrant accent colors'
        },
        'celestial_romance': {
            'signature_elements': 'starry ceiling installations, crescent moon archways, cosmic-inspired metallic accents, constellation lighting patterns, celestial-themed centerpieces, galaxy fabric draping',
            'lighting_design': 'star projection systems, LED constellation patterns, moonlight-inspired uplighting, twinkling fairy light installations, cosmic color-changing lights',
            'luxury_materials': 'metallic star accents, shimmering fabrics, crystal elements, iridescent details, celestial-themed ceramics',
            'finishing_details': 'constellation maps as table numbers, starry table runners, moon phase displays, cosmic-themed place cards, celestial jewelry accents',
            'color_palette': 'deep midnight blue, metallic gold, silver stars, cosmic purple, moonlight white'
        },
        'tropical_modern': {
            'signature_elements': 'oversized tropical leaf installations, contemporary bamboo furniture, hanging garden displays, modern tiki elements, geometric planters, natural fiber textures',
            'lighting_design': 'modern tiki torch installations, LED uplighting through palm fronds, contemporary lantern displays, natural bamboo pendant lights',
            'luxury_materials': 'natural bamboo textures, contemporary ceramics, tropical hardwoods, modern rattan elements, premium natural fibers',
            'finishing_details': 'oversized tropical leaf displays, modern pineapple accents, geometric planter arrangements, contemporary tiki elements, natural fiber table runners',
            'color_palette': 'vibrant coral, tropical turquoise, natural bamboo, fresh lime green, sunset orange'
        },
        'gothic_romance': {
            'signature_elements': 'dramatic dark floral arrangements, ornate candelabra installations, rich velvet draping, antique mirror displays, gothic architectural elements, mysterious mood lighting',
            'lighting_design': 'dramatic candelabra lighting, moody uplighting, flickering candle installations, gothic chandelier displays, mysterious shadow effects',
            'luxury_materials': 'rich burgundy velvets, ornate dark metals, antique glass elements, dramatic silk draping, vintage lace details',
            'finishing_details': 'dark floral arrangements, antique book displays, ornate mirror installations, vintage candelabras, mysterious table settings',
            'color_palette': 'deep burgundy, midnight black, antique gold, dark purple, rich wine tones'
        }
    }
    
    @classmethod
    def _get_professional_capacity_spec(cls, guest_count, space_type, space_data):
        """Generate professional capacity specifications with luxury details"""
        
        capacity_luxury_specs = {
            'intimate': {
                'guests': '15-50 guests',
                'luxury_approach': 'intimate luxury experience with personalized attention',
                'service_style': 'white-glove personalized service'
            },
            'medium': {
                'guests': '75-100 guests', 
                'luxury_approach': 'balanced elegance with sophisticated group dynamics',
                'service_style': 'premium coordinated service'
            },
            'large': {
                'guests': '150-200 guests',
                'luxury_approach': 'grand celebration with multiple service zones',
                'service_style': 'orchestrated luxury service team'
            },
            'grand': {
                'guests': '250+ guests',
                'luxury_approach': 'spectacular celebration with multiple experience areas',
                'service_style': 'full concierge-level service coordination'
            }
        }
        
        guest_spec = capacity_luxury_specs.get(guest_count, capacity_luxury_specs['medium'])
        
        space_capacity_mapping = {
            'wedding_ceremony': f"ceremony seating for {guest_spec['guests']} with {guest_spec['luxury_approach']}",
            'dining_area': f"luxury dining for {guest_spec['guests']} with {guest_spec['service_style']}",
            'dance_floor': f"entertainment space for {guest_spec['guests']} with sophisticated party atmosphere",
            'cocktail_hour': f"cocktail reception for {guest_spec['guests']} with multiple interaction zones",
            'lounge_area': f"luxury lounge seating for {guest_spec['guests']} with intimate conversation areas"
        }
        
        return space_capacity_mapping.get(space_type, f"luxury setup for {guest_spec['guests']}")
    
    @classmethod
    def _get_transformation_techniques(cls, theme_data, space_type):
        """Professional venue transformation techniques from 2024-2025 trends"""
        
        # Advanced transformation methods used by top wedding designers
        transformation_methods = [
            "dramatic ceiling draping installations",
            "professional uplighting design",
            "strategic fabric draping to reshape space",
            "statement floral installations",
            "custom furniture positioning",
            "architectural lighting enhancements"
        ]
        
        space_specific_techniques = {
            'wedding_ceremony': "processional aisle transformation with petal scattering, altar backdrop installation, guest seating arrangement optimization",
            'dance_floor': "elevated DJ platform setup, perimeter lounge area creation, dynamic lighting programming",
            'dining_area': "table arrangement optimization, centerpiece height variation, service flow enhancement",
            'cocktail_hour': "multiple conversation zone creation, bar placement strategy, interactive station positioning",
            'lounge_area': "intimate seating cluster arrangement, ambient lighting zones, cozy corner creation"
        }
        
        base_techniques = f"Professional transformation: {', '.join(transformation_methods[:3])}"
        space_techniques = space_specific_techniques.get(space_type, "luxury space optimization")
        
        return f"{base_techniques}, {space_techniques}"
    
    @classmethod
    def _get_professional_color_palette(cls, color_scheme, custom_colors, theme_data):
        """Professional color coordination with 2024-2025 palettes"""
        
        if color_scheme == 'custom' and custom_colors:
            return f"Custom color palette: {custom_colors} with professional coordination"
        elif color_scheme:
            professional_palettes = {
                'neutral': 'sophisticated neutral palette with whites, creams, champagne tones, and warm beiges',
                'pastels': 'romantic pastel collection with blush pink, soft lavender, mint green, and cream accents',
                'jewel_tones': 'luxurious jewel palette with emerald green, sapphire blue, ruby red, and gold metallic accents',
                'earth_tones': 'organic earth palette with sage green, terracotta, warm cognac, and natural cream tones',
                'monochrome': 'elegant monochromatic scheme with black, white, and sophisticated silver metallic details',
                'bold_colors': 'vibrant contemporary palette with coral pink, turquoise blue, sunny yellow, and lime green'
            }
            return f"Professional colors: {professional_palettes.get(color_scheme, theme_data['color_palette'])}"
        else:
            return f"Theme colors: {theme_data['color_palette']}"
    
    @classmethod
    def _get_contextual_enhancements(cls, season, time_of_day, budget_level):
        """Contextual enhancements based on season, time, and budget"""
        
        enhancements = []
        
        if season:
            seasonal_luxury = {
                'spring': 'fresh spring elements with blooming branches, light flowing fabrics, renewal-inspired arrangements',
                'summer': 'vibrant summer installations with lush greenery, bright seasonal blooms, open-air elegance',
                'fall': 'rich autumn elements with seasonal foliage, warm textured fabrics, harvest-inspired displays',
                'winter': 'sophisticated winter elegance with evergreen installations, rich textures, festive luxury elements'
            }
            if season in seasonal_luxury:
                enhancements.append(seasonal_luxury[season])
        
        if time_of_day:
            timing_elements = {
                'morning': 'bright morning elegance with fresh breakfast reception atmosphere',
                'afternoon': 'natural daylight optimization with garden party sophistication',
                'evening': 'golden hour romance with dramatic sunset-inspired lighting',
                'night': 'sophisticated evening glamour with dramatic nighttime ambiance'
            }
            if time_of_day in timing_elements:
                enhancements.append(timing_elements[time_of_day])
        
        if budget_level:
            luxury_levels = {
                'budget': 'thoughtfully curated budget-conscious elegance with high-impact design choices',
                'moderate': 'professional quality setup with refined details and coordinated elements',
                'luxury': 'luxury high-end installations with premium materials and designer-level coordination',
                'ultra_luxury': 'ultra-luxury opulent transformation with exquisite materials and white-glove execution'
            }
            if budget_level in luxury_levels:
                enhancements.append(luxury_levels[budget_level])
        
        return " ".join(enhancements) + "." if enhancements else ""
    
    @classmethod
    def generate_professional_negative_prompt(cls):
        """Professional negative prompt optimized for Stable Image Ultra"""
        negative_elements = [
            # People (critical for venue shots)
            "people, faces, crowd, guests, bride, groom, wedding party, humans, person",
            
            # Quality issues
            "blurry, low quality, distorted, pixelated, artifacts, noise, low resolution",
            
            # Unwanted content  
            "text, watermark, signature, logo, writing, signs",
            
            # Poor conditions
            "dark, dim, gloomy, messy, cluttered, chaotic, dirty, shabby, unorganized",
            
            # Style issues
            "cartoon, anime, unrealistic, fake, painting, sketch, drawing",
            
            # Composition problems
            "cropped, cut off, tilted, bad proportions, awkward angles"
        ]
        
        return ", ".join(negative_elements)
    
    @classmethod
    def get_ultra_designer_parameters(cls, space_type, wedding_theme, guest_count):
        """Designer-optimized parameters for Stable Image Ultra"""
        
        base_params = {
            'strength': 0.4,
            'cfg_scale': 7.0,
            'steps': 40,
            'output_format': 'png',
        }
        
        # Space-specific designer optimizations
        space_optimizations = {
            'wedding_ceremony': {'strength': 0.35, 'cfg_scale': 6.5},  # Gentle for sacred space
            'dining_area': {'strength': 0.4, 'cfg_scale': 7.0},        # Balanced elegance
            'dance_floor': {'strength': 0.45, 'cfg_scale': 7.5},       # Dynamic transformation
            'cocktail_hour': {'strength': 0.4, 'cfg_scale': 7.0},      # Social sophistication
            'lounge_area': {'strength': 0.35, 'cfg_scale': 6.5},       # Intimate luxury
        }
        
        # Theme-specific designer adjustments
        theme_optimizations = {
            'rustic': {'cfg_scale': -0.5},                 # More organic feel
            'modern': {'cfg_scale': 0.5, 'steps': 5},      # Precise modern lines
            'luxe_minimalism': {'cfg_scale': 1.0},         # Highest precision
            'maximalist_glamour': {'cfg_scale': 0.5},      # Controlled complexity
            'indian_palace': {'cfg_scale': 0.5},           # Rich detail control
            'celestial_romance': {'cfg_scale': 0.5},       # Magical precision
            'gothic_romance': {'cfg_scale': 0.5},          # Dramatic mood control
        }
        
        # Apply designer optimizations
        if space_type in space_optimizations:
            base_params.update(space_optimizations[space_type])
        
        if wedding_theme in theme_optimizations:
            adj = theme_optimizations[wedding_theme]
            base_params['cfg_scale'] += adj.get('cfg_scale', 0)
            base_params['steps'] += adj.get('steps', 0)
        
        # Guest count refinements
        if guest_count in ['large', 'grand']:
            base_params['strength'] += 0.05  # More transformation for larger scale
        elif guest_count == 'intimate':
            base_params['strength'] -= 0.05  # Gentler for intimate settings
        
        # Ensure valid ranges
        base_params['cfg_scale'] = max(1.0, min(20.0, base_params['cfg_scale']))
        base_params['steps'] = max(10, min(50, base_params['steps']))
        base_params['strength'] = max(0.0, min(1.0, base_params['strength']))
        
        return base_params