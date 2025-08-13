# image_processing/prompt_generator.py - Enhanced with vivid, descriptive prompts
"""
Enhanced prompt generation system with rich, textured descriptions for wedding venues
Creates immersive, inspirational visualizations that help couples envision their perfect day
"""

class WeddingPromptGenerator:
    """Generate vivid, descriptive prompts for wedding venue transformations"""
    
    @classmethod
    def generate_space_first_prompt(cls, wedding_theme, space_type, guest_count=None, 
                                   budget_level=None, season=None, time_of_day=None,
                                   color_scheme=None, custom_colors=None, additional_details=None):
        """
        Generate richly detailed, immersive prompts that create stunning wedding visualizations
        """
        
        space_data = cls.SPACE_DEFINITIONS.get(space_type, cls.SPACE_DEFINITIONS['wedding_ceremony'])
        theme_data = cls.THEME_STYLING.get(wedding_theme, cls.THEME_STYLING['classic'])
        
        # 1. QUALITY FOUNDATION - Enhanced for cinematic quality
        quality_foundation = "Award-winning wedding photography, photorealistic, ultra-high resolution 8K, professional architectural photography, golden hour lighting perfection, masterpiece quality."
        
        # 2. PRIMARY SPACE TRANSFORMATION - Rich detail
        space_transformation = f"Transform this space into an breathtaking {space_data['function']}."
        
        # 3. SPACE ARCHITECTURE - Immersive description
        space_architecture = f"Architectural vision: {space_data['layout']}. Essential elements: {space_data['elements']}."
        
        # 4. FUNCTIONAL REQUIREMENTS - Practical beauty
        functional_setup = f"Functional elegance: {space_data['requirements']}."
        
        # 5. CAPACITY AND SCALE - Guest experience
        capacity_setup = cls._get_capacity_specification(guest_count, space_type)
        
        # 6. THEME STYLING - Rich, textured description
        theme_styling = f"Design aesthetic: {theme_data['description']}. Decorative elements: {theme_data['elements']}."
        
        # 7. ATMOSPHERIC DETAILS - Sensory experience
        atmosphere_details = f"Atmosphere: {theme_data['atmosphere']}. Lighting design: {theme_data['lighting']}."
        
        # 8. MATERIAL AND COLOR PALETTE - Visual richness
        color_specification = cls._get_color_specification(color_scheme, custom_colors, theme_data)
        
        # 9. TEXTURE AND MATERIALS - Tactile elements
        texture_materials = f"Materials and textures: {theme_data.get('textures', 'premium wedding materials, elegant fabrics, refined surfaces')}."
        
        # 10. PRODUCTION LEVEL - Quality context
        production_level = cls._get_production_level(budget_level)
        
        # 11. SEASONAL/TEMPORAL CONTEXT - Time and season
        temporal_context = cls._get_temporal_context(season, time_of_day)
        
        # 12. SPECIAL TOUCHES - Unique elements
        special_touches = f"Special details: {theme_data.get('special_touches', 'thoughtful wedding touches, personalized elements')}."
        
        # 13. USER SPECIFICATIONS
        user_specifications = f"Custom requirements: {additional_details}." if additional_details else ""
        
        # 14. TECHNICAL REQUIREMENTS - Final specs
        technical_requirements = "Professional wedding venue ready for celebration, no people visible, pristine condition, magazine-worthy presentation, architectural digest quality, luxury wedding publication standard."
        
        # ASSEMBLE RICH, DESCRIPTIVE PROMPT
        prompt_sections = [
            quality_foundation,
            space_transformation,
            space_architecture,
            functional_setup,
            capacity_setup,
            theme_styling,
            atmosphere_details,
            color_specification,
            texture_materials,
            production_level,
            temporal_context,
            special_touches,
            user_specifications,
            technical_requirements
        ]
        
        final_prompt = " ".join([section.strip() for section in prompt_sections if section.strip()])
        
        negative_prompt = cls.generate_enhanced_negative_prompt()
        
        return {
            'prompt': final_prompt,
            'negative_prompt': negative_prompt,
            'recommended_params': cls.get_space_optimized_parameters(space_type, wedding_theme, guest_count, budget_level)
        }
    
    # ENHANCED SPACE DEFINITIONS - More immersive and detailed
    SPACE_DEFINITIONS = {
        'wedding_ceremony': {
            'function': 'majestic wedding ceremony sanctuary with breathtaking processional aisle and elegant guest seating amphitheater',
            'layout': 'symmetrical guest seating in graceful rows creating perfect sightlines to ceremonial focal point, dramatic center aisle with runner for grand entrance, elevated altar platform',
            'elements': 'stunning ceremony altar or architectural arch as centerpiece, premium chiavari chairs or elegant benches in perfect rows, luxurious aisle runner with petal scatter, ceremonial unity table with candles, dedicated musician/quartet area, guest entrance with welcome display',
            'requirements': 'flawless acoustic design for vows and music, dramatic focal point for ceremony, professional lighting for photography, climate comfort for guests, accessibility considerations',
            'scale_factor': 'ceremony_focused'
        },
        'dance_floor': {
            'function': 'spectacular dance floor entertainment pavilion with professional performance stage and atmospheric party lighting',
            'layout': 'expansive central dance floor with premium surface, surrounding VIP lounge seating areas, elevated DJ booth or live band stage, theatrical lighting grid overhead',
            'elements': 'gleaming hardwood or LED dance floor surface, professional sound system towers, intelligent moving head lights, comfortable perimeter seating lounges, dedicated bar service area, mirror ball or chandelier centerpiece, fog machines for first dance',
            'requirements': 'professional-grade flooring for dancing, concert-quality sound system, dynamic lighting control, climate control for comfort, proper ventilation',
            'scale_factor': 'entertainment_focused'
        },
        'dining_area': {
            'function': 'sophisticated dining hall for elegant wedding feast with impeccable table service and ambiance',
            'layout': 'strategically arranged dining tables with optimal spacing, clear service corridors, prominent head table or sweetheart table, buffet or family-style service areas',
            'elements': 'round tables with fine linens and charger plates, elegant centerpieces with varying heights, ambient uplighting, crystal glassware place settings, decorative chair covers with sashes, suspended floral installations, cake display area',
            'requirements': 'comfortable spacing for service staff, proper sight lines to head table, acoustic treatment for speeches, adjustable lighting for different moments, temperature control',
            'scale_factor': 'dining_focused'
        },
        'cocktail_hour': {
            'function': 'sophisticated cocktail reception lounge for pre-dinner mingling with craft beverages and gourmet appetizers',
            'layout': 'flowing layout with multiple conversation zones, premium bar setups, chef-attended food stations, mix of high cocktail tables and lounge seating areas',
            'elements': 'illuminated bar with professional setup, cocktail tables with linens, passed appetizer staging area, signature drink display, lounge furniture groupings, live music corner, interactive food stations, welcome signage',
            'requirements': 'multiple bar service points, food station accessibility, ambient background music setup, comfortable standing and seating options, smooth traffic flow',
            'scale_factor': 'social_focused'
        },
        'lounge_area': {
            'function': 'luxurious relaxation lounge for intimate conversations and comfortable respite from festivities',
            'layout': 'curated furniture vignettes creating cozy conversation nooks, varied seating heights and styles, strategic lighting for ambiance',
            'elements': 'plush velvet sofas and tufted ottomans, vintage armchairs with throw pillows, marble coffee tables with floral arrangements, side tables with candles, soft area rugs defining spaces, decorative screens for intimacy, accent lighting',
            'requirements': 'ultra-comfortable seating arrangements, conversation-friendly acoustics, mood lighting control, climate comfort, accessible pathways',
            'scale_factor': 'intimate_focused'
        }
    }
    
    # RICHLY DETAILED THEME STYLING - Every theme now vivid and textured
    THEME_STYLING = {
        # Classic Popular Themes - Enhanced with rich detail
        'rustic': {
            'description': 'warm countryside charm with authentic farmhouse elegance',
            'elements': 'reclaimed barn wood installations, suspended mason jar chandeliers, burlap and lace table runners, wildflower meadow arrangements in vintage milk glass, wooden wine barrel cocktail tables, antique ladder displays with family photos, hay bale lounge seating with plaid blankets, cast iron lanterns',
            'lighting': 'warm Edison bulb string light canopy, mason jar pendant clusters, hurricane lanterns on shepherd hooks, firefly lights in branches, candlelit pathway markers',
            'colors': 'warm ivory, sage green, dusty rose, weathered wood brown, soft wheat gold, lavender purple, cream linen',
            'atmosphere': 'intimate countryside celebration with heartfelt rustic romance, barn dance energy, harvest moon magic',
            'textures': 'rough-hewn wood, soft burlap, delicate lace, smooth mason jar glass, worn leather, fresh wildflowers',
            'special_touches': 'vintage typewriter guest book, whiskey barrel ring toss, s\'mores station with fire pit, bluegrass band corner'
        },
        
        'modern': {
            'description': 'sleek contemporary sophistication with architectural precision',
            'elements': 'geometric acrylic installations, minimalist orchid arrangements, lucite ghost chairs, mirrored surfaces, metallic geometric centerpieces, LED light installations, glass charger plates, structured floral designs, concrete planters',
            'lighting': 'programmable LED strips, geometric pendant fixtures, architectural uplighting, color-changing mood lights, laser light displays',
            'colors': 'pure white, charcoal grey, metallic silver, black accents, crystal clear, platinum, dove grey',
            'atmosphere': 'sophisticated urban elegance with gallery-like refinement, architectural beauty, metropolitan chic',
            'textures': 'polished concrete, smooth acrylic, brushed metal, mirror finish, crisp linen, structural flowers',
            'special_touches': 'molecular gastronomy cocktails, digital guest book, projection mapping, contemporary art installations'
        },
        
        'vintage': {
            'description': 'timeless old-world romance with antique treasures and nostalgic charm',
            'elements': 'ornate vintage chandeliers, antique gold mirrors, lace doily details, pearl string garlands, vintage china place settings, Victorian furniture pieces, old leather suitcases, typewriter centerpieces, gramophone displays',
            'lighting': 'crystal chandeliers, antique candelabras, vintage marquee letters, warm amber uplighting, tea light votives',
            'colors': 'blush pink, antique ivory, champagne gold, dusty blue, mauve, pearl white, vintage rose',
            'atmosphere': 'romantic nostalgia with Great Gatsby glamour, timeless elegance, old Hollywood charm',
            'textures': 'aged velvet, antique lace, tarnished silver, weathered leather, silk ribbons, dried flowers',
            'special_touches': 'vintage photo booth with props, antique key escort cards, vinyl record guest book, champagne tower'
        },
        
        'bohemian': {
            'description': 'free-spirited artistic celebration with eclectic natural beauty',
            'elements': 'macrame backdrop installations, pampas grass clouds, layered vintage rugs, low wooden tables with floor cushions, hanging plant installations, dreamcatcher details, mixed metal lanterns, feather accents, tapestry draping',
            'lighting': 'moroccan lanterns, fairy light curtains, candles in colored glass, paper lanterns, firefly jars',
            'colors': 'terracotta, sage green, dusty pink, ochre yellow, deep teal, burgundy, natural hemp',
            'atmosphere': 'artistic free-flowing celebration with wanderlust spirit, festival vibes, creative expression',
            'textures': 'woven macrame, soft cotton, rough jute, smooth river stones, dried grasses, raw wood',
            'special_touches': 'tarot card reader station, flower crown making bar, acoustic guitar circle, incense and sage'
        },
        
        'classic': {
            'description': 'timeless traditional elegance with refined sophistication',
            'elements': 'crystal chandeliers, white rose and peony arrangements, gold-rimmed china, damask linens, tall taper candles, formal place cards, draped fabric ceiling, columnar pedestals',
            'lighting': 'grand crystal chandeliers, elegant sconces, tall candelabras, soft perimeter uplighting',
            'colors': 'pure white, soft ivory, champagne, gold accents, pale pink, silver details',
            'atmosphere': 'refined traditional celebration with ballroom elegance, formal sophistication, timeless grace',
            'textures': 'smooth satin, crisp damask, polished silver, crystal glass, fresh roses, marble surfaces',
            'special_touches': 'string quartet, champagne butler service, calligraphy place cards, white glove service'
        },
        
        'garden': {
            'description': 'enchanted botanical paradise with natural floral abundance',
            'elements': 'cascading greenery installations, garden roses in full bloom, wisteria draping, butterfly releases, trellis archways, potted topiaries, stone fountains, garden statuary, moss table runners',
            'lighting': 'twinkling garden lights, lanterns in trees, solar path lights, uplighting on trees, candles in hurricane glass',
            'colors': 'soft white, blush pink, sage green, lavender, butter yellow, sky blue, natural greens',
            'atmosphere': 'secret garden romance with English countryside charm, botanical beauty, natural elegance',
            'textures': 'soft petals, rough bark, smooth leaves, natural stone, flowing water, morning dew',
            'special_touches': 'butterfly release, flower petal toss, garden games on lawn, botanical cocktails'
        },
        
        'beach': {
            'description': 'coastal paradise celebration with ocean breeze romance',
            'elements': 'driftwood arbor, flowing white fabric pavilions, seashell and starfish accents, nautical rope details, beach grass arrangements, hurricane lanterns, sand ceremony vessels, tiki torches',
            'lighting': 'tiki torch pathways, hurricane lanterns, string lights on poles, sunset golden hour, bonfire glow',
            'colors': 'ocean blue, sandy beige, coral pink, seafoam green, crisp white, sunset orange',
            'atmosphere': 'relaxed coastal celebration with barefoot elegance, ocean rhythm, sunset romance',
            'textures': 'smooth shells, rough driftwood, flowing fabric, natural rope, sea glass, warm sand',
            'special_touches': 'barefoot ceremony, conch shell announcement, beach bonfire, steel drum band'
        },
        
        'industrial': {
            'description': 'urban warehouse chic with raw architectural beauty',
            'elements': 'exposed Edison bulb installations, metal and wood furniture, concrete planters, copper pipe structures, geometric terrariums, metal mesh backdrops, vintage factory lights',
            'lighting': 'Edison bulb chandeliers, industrial pendant lights, exposed filament strings, neon signage',
            'colors': 'charcoal grey, copper, brass, deep green, burgundy, black steel, warm wood',
            'atmosphere': 'edgy urban celebration with converted warehouse vibes, Brooklyn loft style, raw elegance',
            'textures': 'raw steel, exposed brick, smooth concrete, reclaimed wood, vintage leather, oxidized copper',
            'special_touches': 'craft beer bar, food truck catering, graffiti artist, vinyl DJ setup'
        },
        
        # Cultural & Religious Themes - Rich, respectful, and detailed
        'japanese_zen': {
            'description': 'serene Japanese garden wedding with minimalist zen harmony',
            'elements': 'bamboo installations, cherry blossom branches, paper lanterns, origami crane displays, zen rock gardens, bonsai centerpieces, sake barrel display, traditional low tables, silk cushions',
            'lighting': 'soft paper lanterns, bamboo torches, candles in stone holders, subtle uplighting, moonlight effect',
            'colors': 'soft sakura pink, natural bamboo, white, sage green, charcoal grey, gold accents',
            'atmosphere': 'peaceful zen celebration with mindful beauty, cherry blossom serenity, harmonious balance',
            'textures': 'smooth bamboo, delicate paper, rough stone, silk fabric, polished wood, fresh moss',
            'special_touches': 'sake ceremony, origami guest favors, koi pond feature, traditional koto music'
        },
        
        'indian_palace': {
            'description': 'opulent maharaja palace celebration with vibrant colors and gold',
            'elements': 'marigold garlands everywhere, ornate mandap structure, brass vessels, paisley patterns, elephant statuary, jeweled fabrics, rangoli floor designs, hanging bells',
            'lighting': 'brass oil lamps (diyas), colorful lanterns, string lights, candles in colored glass, chandeliers',
            'colors': 'deep red, bright orange, fuchsia, gold, emerald green, royal purple, saffron yellow',
            'atmosphere': 'lavish palace celebration with Bollywood glamour, festive joy, cultural richness',
            'textures': 'rich silk, metallic brocade, fresh marigolds, brass metal, jeweled embellishments',
            'special_touches': 'henna station, dhol drummers, mango lassi bar, traditional sweets display'
        },
        
        'moroccan_nights': {
            'description': 'exotic Arabian nights fantasy with rich patterns and warm spices',
            'elements': 'ornate metal lanterns, rich tapestries, low seating with cushions, brass tea sets, geometric patterns, arched doorways, mosaic details, hookah lounges',
            'lighting': 'pierced metal lanterns, colored glass pendants, candles in geometric holders, warm amber glow',
            'colors': 'deep purple, rich gold, turquoise, burnt orange, ruby red, emerald, bronze',
            'atmosphere': 'mysterious Arabian nights with exotic luxury, spice market richness, desert palace magic',
            'textures': 'plush velvet, intricate metalwork, smooth tile, soft cushions, sheer fabrics, aromatic spices',
            'special_touches': 'belly dancer performance, mint tea service, spice favors, henna artist'
        },
        
        'french_chateau': {
            'description': 'elegant château romance with Versailles-inspired grandeur',
            'elements': 'ornate gold mirrors, toile de jouy fabrics, lavender bundles, champagne towers, macaroon displays, wrought iron details, French garden urns, baroque frames',
            'lighting': 'crystal chandeliers, gold candelabras, soft sconces, garden lights, champagne glow',
            'colors': 'soft lavender, cream, gold leaf, dusty blue, blush pink, sage green, champagne',
            'atmosphere': 'refined château elegance with French countryside romance, aristocratic beauty, wine country charm',
            'textures': 'smooth silk, antique gold leaf, fresh lavender, aged wine barrels, soft toile, crystal',
            'special_touches': 'champagne sabering ceremony, French pastry display, accordion player, lavender toss'
        },
        
        'italian_villa': {
            'description': 'Tuscan villa romance with Mediterranean warmth and abundance',
            'elements': 'lemon tree centerpieces, olive branch garlands, terra cotta pots, vintage wine barrels, string lights over long tables, checked tablecloths, sunflower arrangements',
            'lighting': 'string lights overhead, candles in wine bottles, lanterns on posts, tuscan sunset glow',
            'colors': 'warm terracotta, olive green, sunflower yellow, wine red, cream, rustic orange',
            'atmosphere': 'warm Italian hospitality with vineyard views, family feast feeling, Mediterranean joy',
            'textures': 'rough stone, smooth olive wood, fresh herbs, aged wine barrels, linen fabrics',
            'special_touches': 'prosecco bar, olive oil tasting, Italian serenade, limoncello favors'
        },
        
        'scottish_highland': {
            'description': 'dramatic Highland celebration with Celtic traditions and tartan',
            'elements': 'clan tartan patterns, thistle arrangements, bagpiper entrance, whisky barrels, heather bundles, Celtic knots, stone castle elements, antler decorations',
            'lighting': 'candlelit chandeliers, fireplace glow, torches, lanterns, moody dramatic lighting',
            'colors': 'deep green, burgundy, navy, gold, purple heather, grey stone, rich brown',
            'atmosphere': 'dramatic Highland romance with castle grandeur, Celtic mystique, clan gathering warmth',
            'textures': 'wool tartan, rough stone, smooth whisky barrels, fresh heather, worn leather',
            'special_touches': 'bagpiper processional, whisky tasting, ceilidh dancing, handfasting ceremony'
        },
        
        'mexican_fiesta': {
            'description': 'vibrant fiesta celebration with colorful papel picado and mariachi',
            'elements': 'papel picado banners, bright paper flowers, piñatas, marigold arrangements, talavera pottery, serape table runners, sugar skull details, cactus centerpieces',
            'lighting': 'string lights with paper lanterns, luminarias pathways, candles in punched tin, festive colors',
            'colors': 'hot pink, turquoise, yellow, orange, lime green, purple, red, multi-color',
            'atmosphere': 'joyful fiesta energy with mariachi music, family celebration, cultural pride',
            'textures': 'tissue paper, rough pottery, smooth tiles, woven fabrics, fresh flowers',
            'special_touches': 'mariachi band, tequila bar, churro station, traditional dance performance'
        },
        
        'chinese_dynasty': {
            'description': 'imperial dynasty elegance with red and gold prosperity symbols',
            'elements': 'red lanterns, gold dragons, double happiness symbols, bamboo, peonies, tea ceremony setup, jade accents, silk fans, calligraphy scrolls',
            'lighting': 'red paper lanterns, gold uplighting, candles in jade holders, warm ambient glow',
            'colors': 'lucky red, imperial gold, jade green, black lacquer, pearl white, pink peony',
            'atmosphere': 'imperial palace grandeur with prosperity symbols, ancestral honor, festive abundance',
            'textures': 'smooth silk, lacquered wood, delicate paper, jade stone, gold embroidery',
            'special_touches': 'tea ceremony, lion dance, calligraphy station, red envelope gifts'
        },
        
        # Seasonal Themes - Vivid seasonal experiences
        'winter_wonderland': {
            'description': 'magical winter palace with sparkling ice and cozy warmth',
            'elements': 'white branch centerpieces, crystal icicles, faux snow, silver ornaments, white fur throws, ice sculptures, frosted pinecones, birch tree installations',
            'lighting': 'cool blue uplighting, warm white fairy lights, crystal chandeliers, candle glow, aurora effects',
            'colors': 'pure white, silver, ice blue, crystal clear, soft grey, champagne, midnight blue',
            'atmosphere': 'enchanted ice palace with cozy fireside warmth, snow globe magic, frozen elegance',
            'textures': 'soft fur, smooth ice, crystalline surfaces, frosted glass, velvet warmth',
            'special_touches': 'ice bar, hot cocoa station, fur wrap favors, snow machine first dance'
        },
        
        'autumn_harvest': {
            'description': 'abundant harvest celebration with rich fall colors and cozy warmth',
            'elements': 'pumpkin arrangements, fall leaves garlands, apple centerpieces, wheat bundles, cranberry accents, wooden crates, plaid blankets, corn stalks',
            'lighting': 'warm amber lighting, candles in mason jars, string lights, fireplace glow, lanterns',
            'colors': 'burnt orange, deep red, golden yellow, rust brown, forest green, burgundy, copper',
            'atmosphere': 'cozy harvest gathering with apple orchard charm, thanksgiving abundance, fireside warmth',
            'textures': 'rough burlap, smooth pumpkins, crisp leaves, soft wool, weathered wood',
            'special_touches': 'apple cider bar, s\'mores station, hayride entrance, pumpkin carving'
        },
        
        'spring_awakening': {
            'description': 'fresh spring garden with blooming flowers and renewal energy',
            'elements': 'tulip arrangements, cherry blossoms, pastel ribbons, bird nest accents, butterfly details, fresh green garlands, daffodils, Easter eggs',
            'lighting': 'soft natural light, delicate string lights, pastel uplighting, garden lanterns',
            'colors': 'soft pink, mint green, butter yellow, lavender, sky blue, peach, cream',
            'atmosphere': 'fresh spring renewal with garden party elegance, Easter morning joy, blooming romance',
            'textures': 'soft petals, new leaves, smooth eggs, flowing ribbons, fresh grass',
            'special_touches': 'butterfly release, flower crown station, garden games, Easter egg hunt'
        },
        
        'summer_solstice': {
            'description': 'sun-drenched celebration with endless daylight and vibrant energy',
            'elements': 'sunflower arrangements, citrus centerpieces, bright wildflowers, fruit displays, colorful parasols, lemonade stands, ice cream cart, lawn games',
            'lighting': 'golden hour sunshine, festoon lights, tiki torches, firefly jars, sunset glow',
            'colors': 'sunshine yellow, bright orange, hot pink, turquoise, lime green, coral',
            'atmosphere': 'endless summer day with festival energy, barefoot freedom, sunset celebration',
            'textures': 'sun-warmed wood, cool ice, fresh fruit, flowing cotton, smooth grass',
            'special_touches': 'lemonade bar, ice cream sundae station, lawn games, sparkler send-off'
        },
        
        # Fantasy & Unique Themes
        'fairy_tale': {
            'description': 'enchanted fairy tale castle with magical storybook elements',
            'elements': 'castle backdrop, glass slipper display, enchanted roses, fairy lights, crown centerpieces, magical wands, storybook props, carriage entrance',
            'lighting': 'twinkling fairy lights everywhere, magical uplighting, candelabras, starlight projection',
            'colors': 'royal purple, gold, blush pink, midnight blue, silver, rose red, pearl',
            'atmosphere': 'storybook magic with happily ever after, enchanted castle, princess dreams',
            'textures': 'velvet drapes, satin ribbons, crystal elements, fresh roses, golden details',
            'special_touches': 'horse carriage arrival, midnight countdown, glass slipper ceremony, fairy godmother'
        },
        
        'great_gatsby': {
            'description': 'roaring twenties Art Deco glamour with champagne and jazz',
            'elements': 'Art Deco patterns, feather centerpieces, pearl strands, gold geometric designs, champagne towers, vintage cars, cigarette girls, jazz band setup',
            'lighting': 'crystal chandeliers, Art Deco sconces, gold uplighting, champagne bottle sparklers',
            'colors': 'black, gold, champagne, ivory, emerald green, deep red, silver',
            'atmosphere': 'prohibition era glamour with jazz age sophistication, speakeasy secrets, champagne dreams',
            'textures': 'smooth satin, ostrich feathers, pearl strands, crystal beads, polished gold',
            'special_touches': 'champagne tower, jazz band, Charleston dance floor, Art Deco photo booth'
        }
    }
    
    @classmethod
    def _get_capacity_specification(cls, guest_count, space_type):
        """Generate richly detailed capacity specifications"""
        
        capacity_descriptions = {
            'intimate': {
                'description': 'intimate gathering',
                'details': 'creating warm closeness where every guest feels personally connected'
            },
            'medium': {
                'description': 'perfectly balanced celebration',
                'details': 'ideal size for both grand moments and personal connections'
            },
            'large': {
                'description': 'grand celebration',
                'details': 'impressive scale while maintaining elegant coordination'
            },
            'grand': {
                'description': 'spectacular gala',
                'details': 'magnificent scale befitting a royal celebration'
            }
        }
        
        guest_level = guest_count or 'medium'
        capacity_info = capacity_descriptions.get(guest_level, capacity_descriptions['medium'])
        
        space_capacity_requirements = {
            'wedding_ceremony': {
                'intimate': f"Ceremony sanctuary for {capacity_info['description']} of 15-50 guests with 3-5 rows of seating, {capacity_info['details']}, creating perfect intimacy for vow exchange",
                'medium': f"Ceremony venue for {capacity_info['description']} of 75-100 guests with 8-10 rows, {capacity_info['details']}, ensuring everyone has perfect view of the couple",
                'large': f"Grand ceremony space for {capacity_info['description']} of 150-200 guests with 12-15 rows, {capacity_info['details']}, maintaining ceremony reverence",
                'grand': f"Cathedral-scale ceremony for {capacity_info['description']} of 250+ guests with 20+ rows, {capacity_info['details']}, creating awe-inspiring processional"
            },
            'dining_area': {
                'intimate': f"Cozy dining room for {capacity_info['description']} of 15-50 guests with family-style tables, {capacity_info['details']}, encouraging conversation",
                'medium': f"Elegant dining hall for {capacity_info['description']} of 75-100 guests with 8-10 round tables, {capacity_info['details']}, perfect for toasts and mingling",
                'large': f"Grand ballroom dining for {capacity_info['description']} of 150-200 guests with 15-20 tables, {capacity_info['details']}, orchestrated service flow",
                'grand': f"Palace-scale banquet for {capacity_info['description']} of 250+ guests with 25+ tables, {capacity_info['details']}, multiple service stations"
            },
            'dance_floor': {
                'intimate': f"Cozy dance floor for {capacity_info['description']} of 15-50 guests, {capacity_info['details']}, everyone on the dance floor together",
                'medium': f"Energetic dance floor for {capacity_info['description']} of 75-100 guests, {capacity_info['details']}, perfect party atmosphere",
                'large': f"Expansive dance floor for {capacity_info['description']} of 150-200 guests, {capacity_info['details']}, multiple dance zones",
                'grand': f"Concert-scale dance floor for {capacity_info['description']} of 250+ guests, {capacity_info['details']}, festival energy"
            },
            'cocktail_hour': {
                'intimate': f"Boutique cocktail lounge for {capacity_info['description']} of 15-50 guests, {capacity_info['details']}, personal mingling",
                'medium': f"Sophisticated cocktail reception for {capacity_info['description']} of 75-100 guests, {capacity_info['details']}, natural conversation flow",
                'large': f"Grand cocktail reception for {capacity_info['description']} of 150-200 guests, {capacity_info['details']}, multiple bar stations",
                'grand': f"Gala cocktail reception for {capacity_info['description']} of 250+ guests, {capacity_info['details']}, impressive scale"
            },
            'lounge_area': {
                'intimate': f"Intimate lounge for {capacity_info['description']} of 15-50 guests, {capacity_info['details']}, like a living room gathering",
                'medium': f"Comfortable lounge for {capacity_info['description']} of 75-100 guests, {capacity_info['details']}, multiple conversation areas",
                'large': f"Expansive lounge for {capacity_info['description']} of 150-200 guests, {capacity_info['details']}, varied seating vignettes",
                'grand': f"Luxury hotel lobby scale lounge for {capacity_info['description']} of 250+ guests, {capacity_info['details']}, numerous intimate zones"
            }
        }
        
        space_requirements = space_capacity_requirements.get(space_type, {})
        capacity_spec = space_requirements.get(guest_level, space_requirements.get('medium', ''))
        
        return f"Guest accommodation: {capacity_spec}"
    
    @classmethod
    def _get_color_specification(cls, color_scheme, custom_colors, theme_data):
        """Generate rich color palette descriptions"""
        
        color_schemes = {
            'neutral': 'sophisticated neutral elegance with creamy whites, warm ivories, soft beiges, champagne highlights, taupe accents, creating timeless refinement',
            'pastels': 'romantic pastel dreamscape with blushing pink, lavender mist, baby blue sky, mint cream, buttery yellow, creating soft ethereal beauty',
            'jewel_tones': 'luxurious jewel tone opulence with emerald forest, sapphire depths, ruby passion, amethyst mystery, golden topaz, creating regal richness',
            'earth_tones': 'organic earth tone harmony with sage wisdom, terracotta warmth, sienna sunset, moss tranquility, sand neutrality, creating natural grounding',
            'monochrome': 'dramatic monochromatic sophistication with pure white brilliance, charcoal depth, silver metallics, onyx accents, creating striking contrast',
            'bold_colors': 'vibrant celebration palette with fuchsia energy, tangerine zest, turquoise paradise, lime vitality, electric purple, creating joyful exuberance'
        }
        
        if color_scheme == 'custom' and custom_colors:
            return f"Custom color story featuring {custom_colors}, creating personalized palette perfection."
        elif color_scheme and color_scheme in color_schemes:
            return f"Color palette: {color_schemes[color_scheme]}."
        else:
            return f"Signature colors: {theme_data.get('colors', 'elegant wedding palette with sophisticated color harmony')}."
    
    @classmethod
    def _get_production_level(cls, budget_level):
        """Generate detailed production quality descriptions"""
        
        production_levels = {
            'budget': 'thoughtfully curated budget-conscious design with creative DIY elements, repurposed vintage finds, handcrafted details, proving that beauty doesn\'t require wealth, focusing on meaningful personal touches over expensive decorations',
            'moderate': 'professionally designed celebration with quality rentals, fresh floral arrangements, coordinated linens, ambient lighting design, balanced between elegance and value, creating magazine-worthy results',
            'luxury': 'high-end luxury production with designer furniture, premium floral installations, couture linens, professional lighting design, imported elements, creating five-star hotel ambiance',
            'ultra_luxury': 'no-expense-spared ultra-luxury production with bespoke everything, rare flowers flown in, crystal everything, museum-quality art pieces, celebrity event planner level, creating once-in-a-lifetime spectacular'
        }
        
        level = production_levels.get(budget_level, 'professionally styled wedding with attention to every detail, balanced beauty and quality')
        return f"Production caliber: {level}."
    
    @classmethod
    def _get_temporal_context(cls, season, time_of_day):
        """Generate atmospheric temporal descriptions"""
        
        contexts = []
        
        if season:
            seasonal_atmospheres = {
                'spring': 'fresh spring awakening with cherry blossoms, tulips, daffodils, baby\'s breath, creating renewal and new beginning symbolism',
                'summer': 'peak summer abundance with sunflowers, dahlias, zinnias, creating warmth and vitality, endless daylight celebration',
                'fall': 'rich autumn splendor with chrysanthemums, maple leaves, harvest fruits, creating cozy abundance and grateful gathering',
                'winter': 'winter enchantment with evergreens, holly, white roses, silver branches, creating magical frozen palace atmosphere'
            }
            if season in seasonal_atmospheres:
                contexts.append(f"Seasonal magic: {seasonal_atmospheres[season]}")
        
        if time_of_day:
            temporal_atmospheres = {
                'morning': 'fresh morning celebration with soft sunrise light, dewdrops on flowers, birds singing, breakfast feast setup',
                'afternoon': 'golden afternoon gathering with natural sunlight streaming, garden party atmosphere, leisurely celebration pace',
                'evening': 'romantic evening celebration with golden hour photography light, sunset ceremony timing, candlelit reception',
                'night': 'enchanted night celebration with dramatic lighting, stars overhead, candlelight everywhere, dance until dawn energy'
            }
            if time_of_day in temporal_atmospheres:
                contexts.append(f"Temporal atmosphere: {temporal_atmospheres[time_of_day]}")
        
        return " ".join(contexts) + "." if contexts else ""
    
    @classmethod
    def generate_enhanced_negative_prompt(cls):
        """Comprehensive negative prompt for pristine results"""
        negative_elements = [
            # People and crowds
            "people, faces, crowd, guests, bride, groom, wedding party, photographer, vendors, staff",
            
            # Quality issues
            "blurry, low quality, distorted, pixelated, artifacts, noise, grain, low resolution, compression",
            
            # Unwanted elements
            "text, watermark, signature, logo, copyright, writing, signs, labels, numbers, dates",
            
            # Poor conditions
            "messy, cluttered, dirty, stained, damaged, broken, incomplete, unfinished, construction",
            
            # Style issues
            "cartoon, anime, illustration, painting, drawing, sketch, render, CGI, fake, artificial",
            
            # Lighting problems
            "dark, dim, underexposed, overexposed, harsh shadows, blown highlights, flat lighting",
            
            # Composition issues
            "cropped, cut off, partial, tilted, askew, distorted perspective, fisheye, bad framing"
        ]
        
        return ", ".join(negative_elements)
    
    @classmethod
    def get_space_optimized_parameters(cls, space_type, wedding_theme, guest_count, budget_level):
        """Optimized parameters considering all factors"""
        
        base_params = {
            'strength': 0.4,
            'cfg_scale': 7.0,
            'steps': 50,
            'output_format': 'png',
        }
        
        # Space-specific optimizations
        space_optimizations = {
            'wedding_ceremony': {'strength': 0.35, 'cfg_scale': 6.5, 'steps': 55},
            'dining_area': {'strength': 0.4, 'cfg_scale': 7.0, 'steps': 50},
            'dance_floor': {'strength': 0.45, 'cfg_scale': 7.5, 'steps': 45},
            'cocktail_hour': {'strength': 0.4, 'cfg_scale': 7.0, 'steps': 50},
            'lounge_area': {'strength': 0.35, 'cfg_scale': 6.5, 'steps': 50},
        }
        
        # Theme adjustments
        theme_adjustments = {
            'rustic': {'cfg_scale': -0.5, 'strength': 0.05},
            'modern': {'cfg_scale': 0.5, 'steps': 5},
            'vintage': {'strength': -0.05},
            'industrial': {'cfg_scale': 1.0, 'steps': 10},
            'garden': {'strength': -0.05},
            'japanese_zen': {'cfg_scale': -1.0, 'strength': -0.1},
            'indian_palace': {'cfg_scale': 1.0, 'steps': 10, 'strength': 0.05},
        }
        
        # Budget level affects detail
        budget_adjustments = {
            'budget': {'steps': -5, 'strength': 0.05},
            'moderate': {},
            'luxury': {'steps': 5, 'cfg_scale': 0.5},
            'ultra_luxury': {'steps': 10, 'cfg_scale': 1.0}
        }
        
        # Apply space optimizations
        if space_type in space_optimizations:
            for key, value in space_optimizations[space_type].items():
                base_params[key] = value
        
        # Apply theme adjustments
        if wedding_theme in theme_adjustments:
            adj = theme_adjustments[wedding_theme]
            base_params['cfg_scale'] += adj.get('cfg_scale', 0)
            base_params['steps'] += adj.get('steps', 0)
            base_params['strength'] += adj.get('strength', 0)
        
        # Apply budget adjustments
        if budget_level in budget_adjustments:
            adj = budget_adjustments[budget_level]
            base_params['cfg_scale'] += adj.get('cfg_scale', 0)
            base_params['steps'] += adj.get('steps', 0)
            base_params['strength'] += adj.get('strength', 0)
        
        # Guest count affects transformation intensity
        if guest_count in ['large', 'grand']:
            base_params['strength'] += 0.05
            base_params['steps'] += 5
        elif guest_count == 'intimate':
            base_params['strength'] -= 0.05
        
        # Clamp values
        base_params['cfg_scale'] = max(1.0, min(20.0, base_params['cfg_scale']))
        base_params['steps'] = max(10, min(150, base_params['steps']))
        base_params['strength'] = max(0.0, min(1.0, base_params['strength']))
        
        return base_params