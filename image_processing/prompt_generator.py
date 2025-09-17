# image_processing/prompt_generator.py - Updated for single user_instructions field

class WeddingVenuePromptGenerator:
    """
    Enhanced wedding space prompt generation for Gemini 2.5 Flash.
    Focus: Detailed decorative styling without architectural changes.
    Updated to handle single user_instructions field for natural language input.
    """
    
    @classmethod
    def generate_prompt(cls, wedding_theme, space_type, season=None, 
                       lighting_mood=None, color_scheme=None,
                       custom_prompt=None, user_instructions=None):
        """
        Generate detailed text prompts for wedding space transformations.
        
        Args:
            wedding_theme: Theme choice (e.g., 'rustic', 'modern')
            space_type: Space type (e.g., 'wedding_ceremony', 'dining_area')
            season: Optional season
            lighting_mood: Optional lighting preference
            color_scheme: Optional color palette
            custom_prompt: Custom user prompt (overrides guided mode)
            user_instructions: Single field for any additional user requests
            
        Returns:
            str: Complete text prompt for Gemini with user instructions appended
        """
        
        # Custom prompt mode - enhance and add instructions
        if custom_prompt and custom_prompt.strip():
            prompt = custom_prompt.strip()
            
            # Add user instructions if provided
            if user_instructions and user_instructions.strip():
                prompt += f" {user_instructions.strip()}"
            
            # Ensure focus on decoration, not structure
            if 'decoration' not in prompt.lower() and 'decor' not in prompt.lower():
                prompt = f"Decorate and style this space as follows: {prompt}"
            
            # Ensure no people are included
            if 'no people' not in prompt.lower() and 'without people' not in prompt.lower():
                prompt += " Show the beautifully staged space with zero people present."
            
            return prompt
        
        # Guided mode - build detailed thematic prompt
        return cls._build_guided_prompt(
            wedding_theme, space_type, season, 
            lighting_mood, color_scheme, user_instructions
        )
    
    @classmethod
    def _build_guided_prompt(cls, wedding_theme, space_type, season=None,
                            lighting_mood=None, color_scheme=None, 
                            user_instructions=None):
        """Build detailed guided prompt from wedding parameters with user instructions"""
        
        # Get enhanced theme and space styling
        theme_styling = cls._get_theme_styling(wedding_theme, space_type)
        
        # Start with specific decoration prompt
        prompt = f"Turn this space into into a stunning {cls._get_space_description(space_type)} decorated with {theme_styling}"
        
        # Add seasonal decorative elements
        if season:
            seasonal_decor = cls._get_seasonal_decor(season)
            if seasonal_decor:
                prompt += f" {seasonal_decor}"
        
        # Add lighting design
        if lighting_mood:
            lighting_design = cls._get_lighting_design(lighting_mood)
            if lighting_design:
                prompt += f" {lighting_design}"
        
        # Add color palette styling
        if color_scheme:
            color_styling = cls._get_color_styling(color_scheme)
            if color_styling:
                prompt += f" {color_styling}"
        
        # Add user instructions naturally at the end
        if user_instructions and user_instructions.strip():
            prompt += f" {user_instructions.strip()}"
        
        # Ensure focus on decoration and empty space
        prompt += ".  Remove and show no people or text in this image."
        
        return prompt
    
    @classmethod
    def _get_theme_styling(cls, wedding_theme, space_type):
        """Get detailed styling description combining theme and space - 80+ themes"""
        
        # Theme-specific styling with consistent detail level (50-80 words each)
        theme_base = {
            # Classic Traditional Themes
            'rustic': 'rustic barn wedding featuring weathered wood farm aethetics, tables with burlap runners and white lace overlays, mason jar centerpieces filled with wildflowers and baby\'s breath, sunflowers, vintage bottles, cross-back wooden chairs with burlap bow ties, wagon wheel decorations, checkered gingham ribbons, and wine barrel cocktail tables.',
            
            'modern': 'contemporary minimalist celebration with clear acrylic ghost aethetics, tall cylinder vases holding single white orchids, metal centerpieces in gold or copper, crisp white linens with silver chargers, LED light strips in clean lines, monochromatic white flower arrangements, chrome, geometric backdrop panels, clear glass vessels, metallic balloon installations, sleek white flooring with modern sculptural elements, and precisely arranged minimalist decor.',
            
            'vintage': 'nostalgic vintage aethetics with antique brass candelabras, lace doily overlays, pearl strand garlands, mercury glass vases with roses and peonies, velvet furniture in dusty rose, crystal punch bowls, Victorian parasols, and aged brass fixtures.',
            
            'classic': 'classic traditional elegance featuring gold & ivory, tall crystal candelabras, white taper candles, white rose and lily arrangements, crystal stemware, symmetrical floral arrangements, ivory silk draping with swag, and pearl accents.',
            
            'garden': 'enchanted garden theme with wrought iron, overflowing English garden flowers including roses peonies and delphinium in aged terracotta pots, moss, bird cage decorations, vintage watering cans as vases, climbing ivy on white trellises, potted topiaries, stone garden statues, wicker baskets with flowers, garden tool displays, natural wood elements.',
            
            'beach': 'coastal beach theme featuring driftwood centerpieces, air plants, nautical rope wrapped details, starfish and shells, hurricane lanterns with sand and candles, flowing white fabric, sea glass vessels, coral displays, ship wheels, anchor decorations, striped navy and white patterns, bamboo furniture, tropical flowers, and weathered wood.',
            
            'industrial': 'urban warehouse chic with exposed Edison bulb installations, concrete planters with succulents, metal pipe structures, raw wood and metal furnitures, geometric copper centerpieces, leather seating elements, gear and pulley decorations, distressed metal signage, black metal, minimalist protea arrangements, vintage factory vibe, concrete and metal vessels, exposed brick backdrops, and industrial pendant lighting.',
            
            'bohemian': 'free-spirited bohohemian style featuring macrame hangings, layered vintage rugs, pampas grass in ceramic vessels, mixed metal lanterns, eclectic furniture pieces, dreamcatcher installations, floor cushion seating with tassels, brass tables, wildflower arrangements in mismatched bottles, feather accents, wooden bead garlands, paisley patterns, mandala decorations, incense holders.',
            
            'glamorous': 'Hollywood regency opulence with crystal, mirrored furniture and tables, sequined linens in gold and silver, tall ostrich feather centerpieces, art deco patterns, velvet draping in jewel tones, gold candelabras, rhinestone scatter, crytal & metallic, champagne tower, gilded everything, dramatic spotlighting, and luxurious metallic accents throughout.',
            
            'tropical': 'paradise island vibes featuring monstera leaves as placemats, bird of paradise vibe, bamboo furniture, tiki torches, tropical centerpieces, palm frond installations overhead, bright hibiscus flowers, rattan lanterns, colorful paper umbrellas, banana leaf runners, carved tiki elements, bright fabric in sunset colors, orchid scatter, coconut, and vibrant paper lantern clusters.',
            
            'fairy_tale': 'storybook enchantment with flowing tulle canopies embedded with sparkle, oversized paper flowers, crystal chandeliers dripping with beads, golden branch centerpieces with crystals, castle-inspired decorations, glass elements, magical forest, toadstool seating, butterfly installations, iridescent fabrics, mirror displays creating infinite reflections, and twinkling fairy lights.',
            
            # Core Basic Styles
            'minimalist': 'clean minimalist aesthetic with simple white surfaces, single stem flowers, geometric shapes, neutral colors, uncluttered arrangements, modern simplicity, straight lines, monochromatic elements, quality over quantity focus, empty space, subtle textures, refined simplicity, and thoughtful minimal elements.',
            
            'romantic': 'dreamy romantic atmosphere with soft pastel flowers, flowing fabrics, delicate lace details, rose petals, heart motifs, vintage romance elements, soft lighting, intimate seating, gentle color palettes, romance enchantment.',
            
            'elegant': 'sophisticated elegance featuring refined decorations, luxurious fabrics, polished surfaces, high-quality materials, classic arrangement with dignified presentations, upscale aesthetics, premium flowers, sophisticated lighting, and distinguished styling.',
            
            'chic': 'contemporary chic style with trendy decorations, fashion-forward elements, stylish arrangements, modern aesthetics, designer touches, current trends, sophisticated simplicity, contemporary art influences, and fashinable colors.',
            
            'timeless': 'classic timeless design with enduring beauty, traditional elements, lasting appeal, vintage charm, heritage inspirations, generational style, classic color schemes, time-honored traditions, elegant simplicity, refined taste, quality materials, and sophisticated presentations that transcend trends.',
            
            # Popular Style Variations
            'country_barn': 'country barn atmosphere with authentic farm elements, red barn aesthetics, country inspiration, rural decorations, farmhouse charm, countryside elements, agricultural touches, barn wood details, country wildflowers, rustic simplicity, and heartland American charm.',
            
            'art_deco': 'Art Deco glamour featuring geometric patterns, metallic accents, bold designs, 1920s inspiration, symmetrical arrangements, luxurious materials, dramatic presentations, vintage Hollywood cool, elegant sophistication, rich colors, and period-appropriate decorative elements.',
            
            'scandinavian': 'Scandinavian hygge comfort with natural wood elements, cozy atmosphere, Nordic beauty, functional design, light colors, minimalist comfort, Nordic inspiration, warm textiles, candle lighting, and natural materials.',
            
            'mediterranean': 'Mediterranean warmth featuring terracotta elements, olive branches, warm earth tones, coastal influences, vineyard inspirations, sun-drenched colors, natural textures, outdoor aesthetics, herb decorations, and relaxed elegant atmosphere.',
            
            'prairie_wildflower': 'prairie wildflower celebration with native flower arrangements, grassland inspirations, natural beauty, field flower bouquets, prairie grass elements, wildflower meadow aesthetics, natural colors, natural beauty, and heartland American prairie themes.',
            
            # Seasonal Specific
            'winter_wonderland': 'winter wonderland magic with snow-white decorations, crystal elements, ice-inspired designs, winter flowers, evergreen arrangements, sparkly accents, cool color palettes, cozy winter elements, holiday inspirations, frost-like details, winter romance, and winter season celebration themes.',
            
            'spring_fresh': 'fresh spring celebration with new growth inspirations, pastel color schemes, budding flowers, fresh green elements, renewal themes, light airy decorations, garden party, spring freshness emphasized throughout.',
            
            'harvest_festival': 'harvest festival abundance with autumn produce displays, pumpkin, corn stalks, fall foliage, fall harvest themes, celebration of abundance, giving thanks, autumn color schemes, seasonal fruit displays, and fall agricultural presentations.',
            
            # Approach-Based
            'whimsical': 'whimsical playful design with fun decorative elements, colorful presentations, imaginative details, playful themes, creative arrangements, unique artistic flair, fun color schemes, and imaginative decorative storytelling.',
            
            'monochrome': 'sophisticated monochrome palette with black and white elements, elegant contrast, dramatic classic color scheme, timeless sophisticated simplicity, artistic arrangements, modern elegance, and striking visual impact.',
            
            'statement_bold': 'bold statement design with dramatic decorative elements, eye-catching presentations, strong color schemes, impressive arrangements, memorable details, striking beauty, confident styling, impactful decorations.',
            
            'soft_dreamy': 'soft dreamy atmosphere with gentle decorative elements, pastel color schemes, flowing fabrics, delicate details, romantic softness, dreamy presentations, and enchanting fairy tale elements.',
            
            'luxury': 'premium luxury presentation with high-end decorative elements, expensive materials, lavish arrangements, opulent beauty, exclusive styling, sophisticated luxury, rich details, and exceptional decorative quality throughout',
            
            # Cultural & Traditional Themes - Enhanced with authentic details
            'japanese_zen': 'Japanese zen tranquility with minimalist bamboo elements, cherry blossom arrangements, zen inspirations, meditation aesthetics, natural harmony, simple beauty, peaceful arrangements, traditional Japanese elements, serene minimalist presentations, and mindful decorative balance.',
            
            'chinese_dynasty': 'Chinese dynasty elegance with red and gold, dragon motifs, lantern decorations, silk fabrics, traditional patterns, imperial styling, festive celebrations, and traditional Chinese wedding elements.',
            
            'indian_palace': 'Indian palace magnificence with rich jewel tones, ornate decorations, golden accents, vibrant fabrics, traditional patterns, spice-inspired colors, luxurious presentations, festival atmospheres, and authentic Indian wedding traditions.',
            
            'korean_hanbok': 'Korean hanbok elegance with traditional color schemes, authentic cultural decorations, Korean wedding traditions, elegant simplicity, traditional elements, respectful presentations, and beautiful Korean aesthetic inspirations.',
            
            'thai_temple': 'Thai temple serenity with golden accents, lotus flower arrangements, Buddhist inspirations, traditional Thai elements, peaceful presentations, spiritual beauty, and authentic Thai wedding traditions.',
            
            'scottish_highland': 'Scottish highland tradition with tartan patterns, thistle decorations, Celtic elements, traditional Scottish inspiration, highland beauty, traditional presentations, and authentic Scottish wedding elements.',
            
            'french_chateau': 'French château elegance with romantic French styling, vineyard inspirations, lavender decorations, French country elements, château aesthetics, romantic presentations, French cultural elements, elegant sophistication, and authentic French wedding traditions.',
            
            'greek_island': 'Greek island beauty with blue and white color schemes, Mediterranean elements, olive branch decorations, coastal inspirations, island aesthetics, Greek cultural elements, traditional presentations, and authentic Greek wedding traditions.',
            
            'italian_villa': 'Italian villa romance with Tuscan inspirations, vineyard elements, Mediterranean beauty, Italian cultural decorations, villa aesthetics, romantic presentations, Italian traditions, and beautiful Italian wedding elements.',
            
            'english_garden': 'English garden charm with cottage garden flowers, traditional English elements, garden party aesthetics, countryside beauty, English cultural traditions, pastoral presentations, and authentic English wedding elements.',
            
            'mexican_fiesta': 'Mexican fiesta celebration with vibrant colors, traditional Mexican elements, festive presentations, desert & cacti elements, and joyful Mexican wedding celebrations.',
            
            'spanish_hacienda': 'Spanish hacienda elements, Mediterranean Spanish decorations, traditional Spanish styling, hacienda aesthetics, warm presentations, Spanish traditions, and beautiful Spanish wedding elements.',
            
            'brazilian_carnival': 'Brazilian carnival energy with vibrant tropical colors, festive decorations, carnival inspirations, Brazilian cultural elements, energetic presentations, tropical beauty, and joyful Brazilian wedding celebrations.',
            
            'argentine_tango': 'Argentine tango passion with dramatic presentations, passionate colors, tango inspirations, Argentine elements, romantic authenticity, and authentic Argentine wedding traditions.',
            
            'moroccan_nights': 'Moroccan nights mystery with rich jewel tones, ornate decorations, traditional Moroccan elements, exotic beauty, mysterious presentations, and authentic Moroccan wedding traditions.',
            
            'arabian_desert': 'Arabian desert magic with rich fabrics, golden accents, desert inspirations, Middle Eastern elements, exotic presentations, traditional decorations, and authentic Arabian wedding traditions.',
            
            'african_safari': 'African safari adventure with natural earth tones, wildlife inspirations, African traditions, natural beauty, and African cultural presentations.',
            
            'egyptian_royal': 'Egyptian royal magnificence with golden decorations, pharaoh inspirations, ancient Egyptian elements, royal presentations, historical beauty, and authentic Egyptian wedding traditions.',
            
            # Nature & Seasonal Themes
            'spring_awakening': 'spring awakening freshness with new life inspirations, budding beauty, fresh green elements, seasonal renewal, nature awakening, fresh beginnings, spring flower arrangements, and seasonal celebration themes.',
            
            'summer_solstice': 'summer solstice celebration with peak summer beauty, vibrant summer elements, warm celebrations, summer flower arrangements, bright presentations, and summer fun throughout.',
            
            'autumn_harvest': 'autumn harvest with fall foliage & colors, seasonal abundance, autumn colors, thanksgiving themes, seasonal beauty, harvest celebrations, and autumn wedding elements.',
            
            'forest_enchanted': 'enchanted forest magic with woodland elements, fairy tale inspirations, natural beauty, forest decorations, whimsy branches, woodland creatures themes, and forest wedding magic.',
            
            'desert_bloom': 'desert bloom beauty with desert flower arrangements, southwestern inspirations, desert elements, natural beauty, desert colors, southwestern aesthetics, natural presentations, and desert wedding themes.',
            
            'ocean_waves': 'ocean waves serenity with coastal elements, beach inspirations, ocean beauty, seaside decorations, coastal presentations, marine elements, ocean colors, and beach wedding themes.',
            
            'mountain_vista': 'mountain vista grandeur with mountain inspirations, alpine elements, natural beauty, mountain decorations, outdoor presentations, nature themes, and mountain top elements.',
            
            # Modern & Contemporary Themes
            'metropolitan_chic': 'metropolitan chic sophistication with urban elements, city inspirations, modern presentations, contemporary beauty, urban elegance, metropolitan styling, modern sophistication, and city wedding themes.',
            
            'brooklyn_loft': 'Brooklyn loft industrial with urban loft elements, industrial beauty, city inspirations, loft aesthetics, urban presentations, Brooklyn styling, and urban wedding themes.',
            
            'rooftop_garden': 'rooftop garden urban with city garden elements, rooftop beauty, urban nature, garden presentations, city aesthetics, rooftop styling, urban garden themes, and rooftop wedding elements.',
            
            'art_deco_glam': 'Art Deco glamour with 1920s inspirations, glamorous elements, vintage Hollywood beauty, Art Deco patterns, glamorous presentations, period styling, vintage glamour, and Art Deco wedding themes.',
            
         'concrete_jungle': 'concrete jungle urban with industrial city elements, metropolitan presentations, city aesthetics, urban styling, industrial elegance, metropolitan beauty, and urban wedding themes.',
            
            'glass_house': 'glass house modern with contemporary glass elements, modern beauty, architectural presentations, contemporary aesthetics, modern styling, architectural beauty, contemporary elegance, and modern wedding themes',
            
            # Vintage & Retro Themes
            '1950s_diner': '1950s diner retro with vintage diner elements, retro beauty, 1950s inspirations, diner aesthetics, vintage styling, 1950s beauty, and retro wedding themes',
            
            '1960s_mod': '1960s mod style with mod elements, 1960s beauty, mod inspirations, retro aesthetics, mod presentations, vintage styling, 1960s elegance, and mod wedding themes',
            
            '1970s_disco': '1970s disco energy with disco elements, retro beauty, 1970s inspirations, disco aesthetics, energetic presentations, vintage styling, disco beauty, and retro wedding themes',
            
            '1980s_neon': '1980s neon bright with neon elements, retro beauty, 1980s inspirations, neon aesthetics, bright presentations, vintage styling, neon beauty, nylon fabric and retro wedding themes',
            
            '1990s_grunge': '1990s grunge alternative with grunge elements, alternative beauty, 1990s inspirations, grunge aesthetics, alternative presentations, vintage styling, and alternative wedding themes',
            
            'victorian_romance': 'Victorian romance elegance with Victorian elements, romantic beauty, period inspirations, Victorian aesthetics, romantic presentations, historical styling, Victorian beauty, and period wedding themes',
            
            'art_nouveau': 'Art Nouveau artistic with Art Nouveau elements, artistic beauty, period inspirations, Art Nouveau aesthetics, artistic presentations, historical styling, artistic beauty, and Art Nouveau wedding themes',
            
            'great_gatsby': 'Great Gatsby glamour with 1920s elements, Jazz Age beauty, Gatsby inspirations, glamorous aesthetics, luxurious presentations, period styling, Jazz Age glamour, and Gatsby wedding themes',
        }
        
        base_styling = theme_base.get(wedding_theme, f'{wedding_theme.replace("_", " ")} themed decorative styling with carefully selected elements')
        
        # Add consistent space-specific enhancements
        space_enhancements = {
            'wedding_ceremony': ', arranged for a sacred ceremony space with decorated altar, guest seating with aisle decorations, with processional pathway.',
            'dining_area': ', configured as an elegant dining space with a head table, guest table arrangements, and themed centerpiece displays.',
            'dance_floor': ', designed as a celebration space with dance area, perimeter social seating, with DJ or band platform.',
            'cocktail_hour': ', styled for socializing with high-top tables, bar station setup, appetizer displays, and confortable conversation atmosphere.',
            'bridal_suite': ', perfect for a bridal preparation suite with vanity stations, relaxation seating, and privacy.',
            'entrance_area': ', designed as a grand arrival experience with guest reception elements, gift table setup with themed bags, and memorable first impression.',
        }
        
        return base_styling + space_enhancements.get(space_type, '')
    
    @classmethod
    def _get_seasonal_decor(cls, season):
        """Get seasonal landscape/environment alterations for the venue"""
        seasonal_elements = {
            'spring': 'landscape shows fresh spring conditions with blooming or budding trees, bright green healthy grass growth, budding flowers beginning to emerge, clear blue skies with soft white clouds.',
            'summer': 'environment displays full summer conditions with lush deep green foliage on all trees and plants, fully mature landscapes, blue skies, and vibrant natural colors.',
            'fall': 'The landscape exhibits autumn transformation with trees showing golden, orange, and red foliage, some fallen leaves on the ground, crisp clear atmosphere, and natural environment in seasonal transition.',
            'winter': 'The environment shows winter conditions with bare tree branches or evergreens, light snow on the ground and surfaces, crisp cold overcast and pale winter sky, with dormant winter landscape elements.',
        }
        
        return seasonal_elements.get(season, '')
    
    @classmethod
    def _get_lighting_design(cls, lighting_mood):
        """Get consistent lighting design for all themes and spaces"""
        lighting_designs = {
            'dawn': 'Illuminated with soft dawn lighting featuring pale pink and golden hues, minimal candles just being lit, gentle ambient glow, and fresh morning atmosphere.',
            'morning': 'Brightened with clear morning light using white candles, bright ambient lighting, crystal-clear visibility, and fresh daytime energy.',
            'midday': 'Lit with full midday brightness featuring minimal decorative lighting and shadows, clear visibility throughout, bright white accents, and natural daylight.',
            'golden_hour': 'Bathed in golden hour warmth with amber-toned lighting, honeyed glow on all surfaces, and sunset-inspired ambiance.',
            'dusk': 'Enhanced with dusk magic featuring purple and pink lighting transitions, twilight color washes, and romantic evening approach.',
            'evening': 'Illuminated for evening elegance with warm string lights overhead, lights glowing softly, and intimate lighting throughout.',
            'night': 'Transformed for nighttime, uplighting on key light features, and complete artificial illumination.',
            'bright': 'Energized with bright celebration lighting, clear bulbs throughout, bright uplighting, and maximum visibility.',
            'dim': 'Softened with intimate dim lighting featuring low-wattage bulbs, gentle amber glow, and cozy atmosphere.',
            'romantic': 'Enchanted with romantic lighting, soft lights, gentle shadows, warm golden tones, and dreamy ambiance.',
            'candlelit': 'Glowing with pure candlelight featuring pillar candles, votives, floating candles, candelabras, and flickering flame ambiance throughout.',
            'natural': 'Utilizing natural light emphasis with minimal artificial additions, light-colored decorations to maximize brightness, strategic mirror placements, and organic illumination.',
            'fluorescent': 'Lit with clean fluorescent brightness featuring cool white tones, even distribution, modern clarity, and professional venue lighting.',
            'rainy': 'Adapted for overcast conditions with extra warm lighting to counter gray skies and weather-proof illumination.',
            'dramatic': 'Enhanced with dramatic lighting effects featuring bold contrasts, spotlighting on key features, dynamic shadows, theatrical presentations, and impactful illumination.',
        }
        
        return lighting_designs.get(lighting_mood, '')
    
    @classmethod
    def _get_color_styling(cls, color_scheme):
        """Get detailed color application descriptions"""
        color_applications = {
            # Primary Colors
            'red': 'Dominated by red with crimson roses, burgundy dahlias, red linens, ruby glass accents.',
            'pink': 'Enhanced with pink through blush roses, pink peonies, rose-colored fabrics, pink glass elements.',
            'coral': 'Energized with coral through coral roses, peach dahlias, coral fabrics, sunset glass accents.',
            'orange': 'Energized with orange through marigolds, orange roses, tangerine fabrics, copper vessels.',
            'yellow': 'Brightened with yellow featuring sunflowers, yellow roses, golden linens, amber glass.',
            'green': 'Refreshed with natural green using abundant foliage, green hydrangeas, sage linens, emerald accents.',
            'blue': 'Cool blues through hydrangeas, delphiniums, navy linens, cobalt glass.',
            'purple': 'Enriched with royal purple featuring orchids, lavender, plum fabrics, amethyst accents.',
            'white': 'Purified with elegant white through white roses, white linens, crystal accents, silver elements.',
            'black': 'Dramatized with sophisticated black through black accents, dark linens, silver contrasts, crystal elements.',
            
            # Pastels
            'pastel_pink': 'Softened with blush pink through pale roses, pink peonies, rose fabrics, pearl accents.',
            'pastel_peach': 'Warmed with soft peach using garden roses, peach ranunculus, coral fabrics, champagne metals.',
            'pastel_yellow': 'Brightened with soft yellow through pale yellow roses, butter-colored fabrics, cream accents, gold elements.',
            'pastel_mint': 'Freshened with mint green using eucalyptus, white flowers, sage fabrics, silver details.',
            'pastel_blue': 'Soothed with powder blue through pale hydrangeas, forget-me-nots, sky fabrics, white accents.',
            'pastel_lavender': 'Calmed with gentle lavender featuring sweet peas, lilac blooms, purple fabrics, silver accents.',
            'pastel_sage': 'Refreshed with sage green through eucalyptus, sage-colored fabrics, natural elements, wood accents.',
            'pastel_cream': 'Warmed with cream tones through cream roses, ivory fabrics, champagne accents, gold elements.',
            
            # Earth Tones
            'earth_brown': 'With rich brown through chocolate accents, wood elements, brown fabrics, copper details.',
            'earth_rust': 'Warmed with rust tones through terracotta elements, rust-colored fabrics, copper accents, earth details',
            'earth_forest': 'Enhanced with forest elements through deep green foliage, wood accents, natural fabrics, earth tones.',
            'earth_desert': 'Warmed with desert tones through sand-colored elements, copper accents, earth fabrics, natural details.',
            'earth_autumn': 'Enriched with autumn colors through fall foliage, orange accents, brown fabrics, copper elements.',
            'earth_moss': 'Refreshed with moss green through natural moss elements, green fabrics, stone accents, earth details.',
            
            # Popular Combinations
            'black_white': 'Contrasted with classic black and white through monochrome elements, dramatic contrasts, elegant simplicity, crystal accents.',
            'pink_gold': 'Romanticized with pink and gold through blush roses, golden accents, rose fabrics, champagne elements.',
            'blue_white': 'Freshened with blue and white through blue flowers, white linens, navy accents, crystal elements.',
            'red_white': 'Energized with red and white through red roses, white linens, bold contrasts, crystal accents.',
            'sage_cream': 'Softened with sage and cream through sage foliage, cream fabrics, natural elements, champagne accents.',
            'blush_gold': 'Enhanced with blush and gold through blush roses, golden accents, soft fabrics, champagne elements.',
            'navy_gold': 'Sophisticated with navy and gold through navy linens, golden accents, elegant contrasts, brass elements.',
            'burgundy_gold': 'Enriched with burgundy and gold through deep red flowers, golden accents, rich fabrics, brass elements.',
            
            # Seasonal
            'spring_fresh': 'Refreshed with spring colors including pink tulips, green foliage, yellow daffodils, and pastel elements.',
            'summer_bright': 'Energized with summer colors including coral flowers, turquoise accents, yellow elements, and bright fabrics.',
            'autumn_harvest': 'Warmed with autumn colors including orange foliage, burgundy flowers, golden elements, and harvest accents.',
            'winter_elegant': 'Sophisticated with winter colors including navy elements, silver accents, white flowers, and crystal details.',
        }
        
        return color_applications.get(color_scheme, '')
    
    @classmethod
    def _get_space_description(cls, space_type):
        """Get concise space type descriptions"""
        space_descriptions = {
            'wedding_ceremony': 'wedding ceremony with altar, guest seating with isle, ',
            'dance_floor': 'celebration area with space for dancing, small stage for DJ or band, ',
            'dining_area': 'reception and dining area with seating for a wedding',
            'cocktail_hour': 'cocktail and lounge area for conversation',
            'bridal_suite': 'bridal preparation suite with everything she needs',
            'entrance_area': 'entrance-way and welcome area for guests to arrive',
        }
        
        return space_descriptions.get(space_type, space_type.replace('_', ' '))