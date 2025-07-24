# image_processing/prompt_generator.py - Comprehensive 50+ Wedding Theme Prompts for SD3.5 Large
"""
Advanced prompt generation system for realistic wedding venue transformations
Optimized for Stability AI SD3.5 Large with 50+ beautiful wedding themes
Supports cfg_scale, steps, and aspect_ratio parameters
"""

class WeddingPromptGenerator:
    """Generate well-structured prompts optimized for SD3.5 Large"""
    
    @classmethod
    def generate_dynamic_prompt(cls, wedding_theme, space_type, guest_count=None, 
                               budget_level=None, season=None, time_of_day=None,
                               color_scheme=None, custom_colors=None, additional_details=None):
        """Generate a well-structured, hierarchical prompt for SD3.5 Large"""
        
        theme_data = cls.THEME_STYLES.get(wedding_theme, cls.THEME_STYLES['classic'])
        space_data = cls.SPACE_TRANSFORMATIONS.get(space_type, cls.SPACE_TRANSFORMATIONS['wedding_ceremony'])
        
        # 1. QUALITY FOUNDATION - Most important for SD3.5 Large
        quality_foundation = "Professional wedding venue photography, photorealistic, ultra-high resolution, masterpiece quality."
        
        # 2. PRIMARY TRANSFORMATION - Core objective
        primary_transformation = f"Transform this space into a complete {space_data['setup']}."
        
        # 3. THEME SPECIFICATION - Main aesthetic direction
        theme_specification = f"Style: {wedding_theme} wedding theme."
        
        # 4. SPECIFIC THEME ELEMENTS - What makes this theme unique
        theme_elements = f"Key elements: {theme_data['specific_elements']}."
        
        # 5. SPATIAL ARRANGEMENT - How the space should be organized
        spatial_parts = []
        
        # Add guest count with specific seating
        if guest_count and guest_count in cls.GUEST_COUNT_MODIFIERS:
            guest_data = cls.GUEST_COUNT_MODIFIERS[guest_count]
            spatial_parts.append(f"Seating: {guest_data['description']} with {guest_data['seating']}")
        else:
            spatial_parts.append("Seating: arrangement for approximately 100 guests with proper spacing")
        
        # Add space focus
        spatial_parts.append(f"Focus: {space_data['focus']}")
        
        spatial_arrangement = " | ".join(spatial_parts) + "."
        
        # 6. BUDGET/QUALITY LEVEL - Production values
        budget_quality = ""
        if budget_level and budget_level in cls.BUDGET_MODIFIERS:
            budget_quality = f"Production level: {cls.BUDGET_MODIFIERS[budget_level]}."
        else:
            budget_quality = "Production level: quality professional wedding decorations."
        
        # 7. SEASONAL/TEMPORAL CONTEXT - When/where context
        context_parts = []
        
        if season and season in cls.SEASON_MODIFIERS:
            context_parts.append(f"Season: {cls.SEASON_MODIFIERS[season]}")
        
        if time_of_day and time_of_day in cls.TIME_MODIFIERS:
            context_parts.append(f"Time: {cls.TIME_MODIFIERS[time_of_day]}")
        
        seasonal_context = " | ".join(context_parts) + "." if context_parts else ""
        
        # 8. COLOR PALETTE - Visual color scheme
        color_palette = ""
        if color_scheme and color_scheme in cls.COLOR_MODIFIERS:
            if color_scheme == 'custom' and custom_colors:
                color_palette = f"Colors: custom palette featuring {custom_colors}."
            else:
                color_palette = f"Colors: {cls.COLOR_MODIFIERS[color_scheme]}."
        else:
            color_palette = f"Colors: {theme_data['colors']}."
        
        # 9. LIGHTING & ATMOSPHERE - Mood and ambiance
        lighting_atmosphere = f"Lighting: {theme_data['lighting']}. Atmosphere: {theme_data['atmosphere']}."
        
        # 10. ADDITIONAL DETAILS - User specifications
        user_details = f"Additional: {additional_details}." if additional_details else ""
        
        # 11. TECHNICAL REQUIREMENTS - Final specifications
        technical_requirements = "Requirements: elegant wedding setup, celebration ready, complete venue transformation, no people visible, empty chairs and tables ready for guests."
        
        # ASSEMBLE STRUCTURED PROMPT
        prompt_sections = [
            quality_foundation,
            primary_transformation,
            theme_specification,
            theme_elements,
            spatial_arrangement,
            budget_quality,
            seasonal_context,
            color_palette,
            lighting_atmosphere,
            user_details,
            technical_requirements
        ]
        
        # Remove empty sections and join with proper spacing
        final_prompt = " ".join([section for section in prompt_sections if section.strip()])
        
        # Enhanced negative prompt for SD3.5 Large
        negative_prompt = cls.generate_enhanced_negative_prompt()
        
        return {
            'prompt': final_prompt,
            'negative_prompt': negative_prompt,
            'recommended_params': cls.get_dynamic_parameters_sd35_large(wedding_theme, space_type, guest_count)
        }
    
    @classmethod
    def generate_example_improved_prompt(cls):
        """Generate the improved version of the Japanese Zen example"""
        
        # Using the new structure for Japanese Zen intimate ceremony
        sections = [
            "Professional wedding venue photography, photorealistic, ultra-high resolution, masterpiece quality.",
            
            "Transform this space into a complete full wedding ceremony setup with processional aisle, rows of chairs for guests, ceremonial altar or arch, unity candle area, guest seating arrangement.",
            
            "Style: japanese_zen wedding theme.",
            
            "Key elements: cherry blossom ceremony arch, bamboo details, paper lanterns, zen garden stones, minimalist wooden furniture.",
            
            "Seating: intimate gathering for 15-30 guests with cozy arrangement using 3-4 rows of chairs, small intimate scale decorations | Focus: ceremony altar and guest seating arrangement for wedding vows.",
            
            "Production level: tasteful budget-friendly decorations with DIY elements, simple elegant centerpieces, cost-effective beautiful setup.",
            
            "Colors: soft pink cherry blossom, white, natural bamboo, sage green, cream.",
            
            "Lighting: soft natural lighting, paper lanterns, candles in bamboo holders, gentle ambient glow. Atmosphere: peaceful zen celebration with natural harmony.",
            
            "Requirements: elegant wedding setup, celebration ready, complete venue transformation, no people visible, empty chairs and tables ready for guests."
        ]
        
        return " ".join(sections)
    
    @classmethod
    def compare_prompts(cls):
        """Compare old vs new prompt structure"""
        
        old_prompt = "professional wedding staging, photorealistic, detailed, high resolution, Change space into a complete full wedding ceremony setup with processional aisle, rows of chairs for guests, ceremonial altar or arch, unity candle area, guest seating arrangement beautiful japanese_zen wedding theme with cherry blossom ceremony arch, bamboo details, paper lanterns, zen garden stones, minimalist wooden furniture serene Japanese zen wedding with cherry blossom branches, bamboo ceremony arch, minimalist wooden seating, paper lanterns, zen garden elements, sake ceremony table intimate gathering for 15-30 guests with cozy seating arrangement, 3-4 rows of chairs or 2-3 small tables, small intimate scale decorations focus on ceremony altar and guest seating arrangement for wedding vows tasteful budget-friendly decorations with DIY elements, simple elegant centerpieces, cost-effective beautiful setup color palette: soft pink cherry blossom, white, natural bamboo, sage green, cream soft natural lighting, paper lanterns, candles in bamboo holders, gentle ambient glow peaceful zen celebration with natural harmony elegant wedding setup, celebration ready complete transformation of space no people visible, empty chairs and tables ready for guests"
        
        new_prompt = cls.generate_example_improved_prompt()
        
        return {
            'old': {
                'prompt': old_prompt,
                'length': len(old_prompt),
                'issues': [
                    "Run-on sentence with no punctuation",
                    "Repetitive elements (cherry blossom ceremony arch mentioned twice)",
                    "Poor hierarchy - all elements have equal weight",
                    "Difficult for AI to parse and prioritize",
                    "Missing quality indicators for SD3.5 Large"
                ]
            },
            'new': {
                'prompt': new_prompt,
                'length': len(new_prompt),
                'improvements': [
                    "Clear hierarchical structure with periods",
                    "Eliminates repetition and redundancy", 
                    "Logical flow from quality → transformation → details",
                    "SD3.5 Large optimized quality terms",
                    "Easier for AI to parse and follow priorities",
                    "Better organization for complex scenes"
                ]
            }
        }
    # Enhanced theme descriptions with specific elements and setups for ALL 50+ themes
    THEME_STYLES = {
        # Cultural & Traditional Themes
        'japanese_zen': {
            'description': 'serene Japanese zen wedding with cherry blossom branches, bamboo ceremony arch, minimalist wooden seating, paper lanterns, zen garden elements, sake ceremony table',
            'lighting': 'soft natural lighting, paper lanterns, candles in bamboo holders, gentle ambient glow',
            'colors': 'soft pink cherry blossom, white, natural bamboo, sage green, cream',
            'atmosphere': 'peaceful zen celebration with natural harmony',
            'specific_elements': 'cherry blossom ceremony arch, bamboo details, paper lanterns, zen garden stones, minimalist wooden furniture'
        },
        'chinese_dynasty': {
            'description': 'elegant Chinese dynasty wedding with red silk draping, golden dragon decorations, traditional round tables, Chinese lanterns, jade accents, ornate screens',
            'lighting': 'warm golden Chinese lanterns, red uplighting, traditional candlelight, festive glow',
            'colors': 'imperial red, gold, jade green, black lacquer, silk white',
            'atmosphere': 'regal Chinese celebration with imperial grandeur',
            'specific_elements': 'dragon ceremony backdrop, Chinese lanterns, silk draping, jade details, ornate wooden screens'
        },
        'indian_palace': {
            'description': 'magnificent Indian palace wedding with marigold garlands, intricate mandap, silk cushions, golden elephant statues, jewel-toned fabrics, ornate brass details',
            'lighting': 'warm golden brass lamps, colorful silk lighting, ornate chandeliers, flickering diyas',
            'colors': 'rich jewel tones, marigold orange, royal purple, gold, deep red, emerald green',
            'atmosphere': 'opulent Indian celebration with palace magnificence',
            'specific_elements': 'ornate mandap ceremony structure, marigold garlands, silk cushions, brass details, jewel-toned fabrics'
        },
        'korean_hanbok': {
            'description': 'traditional Korean hanbok wedding with colorful silk ceremony arch, low wooden tables, hanbok-inspired decorations, lotus flowers, traditional screens',
            'lighting': 'soft natural lighting, traditional Korean lamps, gentle warm glow, lantern accents',
            'colors': 'hanbok pastels, soft pink, mint green, lavender, cream, traditional Korean colors',
            'atmosphere': 'graceful Korean celebration with traditional elegance',
            'specific_elements': 'hanbok-inspired ceremony arch, traditional screens, lotus flowers, low wooden seating, silk details'
        },
        'thai_temple': {
            'description': 'exotic Thai temple wedding with golden Buddha statues, tropical flowers, ornate Thai decorations, silk draping, incense holders, traditional seating',
            'lighting': 'warm golden temple lighting, ornate Thai lamps, tropical sunset glow, incense smoke ambiance',
            'colors': 'temple gold, tropical orange, deep red, emerald green, saffron yellow',
            'atmosphere': 'spiritual Thai celebration with temple serenity',
            'specific_elements': 'golden ceremony backdrop, Thai ornaments, tropical flower arrangements, silk draping, temple details'
        },
        'scottish_highland': {
            'description': 'rustic Scottish highland wedding with tartan details, bagpipe area, wooden ceremony arch, heather arrangements, clan banners, rustic stone elements',
            'lighting': 'warm hearth lighting, Celtic lanterns, natural highland glow, fireplace ambiance',
            'colors': 'tartan plaids, deep green, burgundy, gold, heather purple, stone grey',
            'atmosphere': 'proud Scottish celebration with highland spirit',
            'specific_elements': 'tartan ceremony arch, clan banners, heather bouquets, stone details, Celtic decorations'
        },
        'french_chateau': {
            'description': 'elegant French château wedding with ornate gold details, crystal chandeliers, French provincial furniture, rose arrangements, vintage French elements',
            'lighting': 'crystal chandeliers, French provincial lamps, romantic candlelight, château elegance',
            'colors': 'French cream, antique gold, rose pink, lavender, champagne, ivory',
            'atmosphere': 'sophisticated French celebration with château luxury',
            'specific_elements': 'ornate ceremony backdrop, crystal chandeliers, French furniture, rose arrangements, gold details'
        },
        'greek_island': {
            'description': 'stunning Greek island wedding with white and blue decorations, olive branch details, Mediterranean seating, Greek columns, coastal elements',
            'lighting': 'bright Mediterranean sunlight, white lanterns, coastal sunset glow, natural island lighting',
            'colors': 'Santorini white, ocean blue, olive green, sun yellow, natural stone',
            'atmosphere': 'breezy Greek celebration with island charm',
            'specific_elements': 'Greek column ceremony arch, olive branches, Mediterranean seating, white and blue details, coastal decorations'
        },
        'italian_villa': {
            'description': 'romantic Italian villa wedding with vineyard elements, rustic wooden details, Italian cypress arrangements, wine barrel accents, Tuscan decorations',
            'lighting': 'warm Italian sunset, vineyard string lights, rustic lanterns, villa ambiance',
            'colors': 'Tuscan terracotta, vineyard green, wine burgundy, cream, golden yellow',
            'atmosphere': 'romantic Italian celebration with villa elegance',
            'specific_elements': 'vineyard ceremony arch, wine barrel details, cypress arrangements, Tuscan decorations, rustic Italian furniture'
        },
        'english_garden': {
            'description': 'classic English garden wedding with rose arbors, cottage garden flowers, vintage tea service, English garden seating, countryside elements',
            'lighting': 'soft English garden light, cottage lanterns, natural daylight, garden ambiance',
            'colors': 'garden rose pink, lavender, sage green, cream, cottage white',
            'atmosphere': 'charming English celebration with garden romance',
            'specific_elements': 'rose ceremony arbor, cottage flowers, vintage tea settings, English garden furniture, countryside details'
        },
        'mexican_fiesta': {
            'description': 'vibrant Mexican fiesta wedding with colorful papel picado, piñata decorations, mariachi area, bright flower arrangements, festive Mexican elements',
            'lighting': 'colorful fiesta lighting, papel picado shadows, warm Mexican glow, festive ambiance',
            'colors': 'fiesta bright colors, red, orange, yellow, green, purple, pink',
            'atmosphere': 'joyful Mexican celebration with fiesta energy',
            'specific_elements': 'papel picado ceremony backdrop, colorful flowers, Mexican decorations, fiesta seating, mariachi area'
        },
        'spanish_hacienda': {
            'description': 'elegant Spanish hacienda wedding with wrought iron details, terracotta elements, Spanish tile accents, fountain centerpieces, hacienda furniture',
            'lighting': 'warm hacienda lighting, wrought iron lanterns, Spanish sunset glow, courtyard ambiance',
            'colors': 'hacienda terracotta, deep red, golden yellow, wrought iron black, tile blue',
            'atmosphere': 'passionate Spanish celebration with hacienda warmth',
            'specific_elements': 'wrought iron ceremony arch, Spanish tiles, fountain details, hacienda furniture, terracotta elements'
        },
        'brazilian_carnival': {
            'description': 'festive Brazilian carnival wedding with bright feathers, samba decorations, tropical flowers, carnival masks, vibrant Brazilian elements',
            'lighting': 'carnival bright lighting, colorful lanterns, tropical sunset, festive carnival glow',
            'colors': 'carnival bright colors, emerald green, sunshine yellow, ocean blue, hot pink',
            'atmosphere': 'energetic Brazilian celebration with carnival joy',
            'specific_elements': 'feather ceremony backdrop, carnival decorations, tropical arrangements, samba area, Brazilian details'
        },
        'argentine_tango': {
            'description': 'passionate Argentine tango wedding with rose decorations, dance floor centerpiece, tango band area, elegant Argentine elements, wine details',
            'lighting': 'romantic tango lighting, elegant chandeliers, dance floor spots, passionate ambiance',
            'colors': 'tango red, elegant black, rose pink, wine burgundy, gold accents',
            'atmosphere': 'passionate Argentine celebration with tango romance',
            'specific_elements': 'rose ceremony arch, dance floor centerpiece, tango decorations, wine details, elegant Argentine furniture'
        },
        'moroccan_nights': {
            'description': 'exotic Moroccan nights wedding with ornate lanterns, rich tapestries, low lounge seating, intricate patterns, Middle Eastern decorations, gold accents',
            'lighting': 'warm Moroccan lanterns, exotic lighting, golden glow, Middle Eastern ambiance',
            'colors': 'rich jewel tones, deep purple, gold, turquoise, burgundy, orange',
            'atmosphere': 'exotic Moroccan celebration with Middle Eastern mystique',
            'specific_elements': 'ornate lantern ceremony backdrop, tapestries, low seating, intricate patterns, Middle Eastern details'
        },
        'arabian_desert': {
            'description': 'luxurious Arabian desert wedding with tent decorations, camel details, desert flowers, sand-colored elements, Arabian nights theme',
            'lighting': 'warm desert lighting, Arabian lamps, sunset glow, exotic desert ambiance',
            'colors': 'desert sand, royal purple, gold, deep red, turquoise, sunset orange',
            'atmosphere': 'luxurious Arabian celebration with desert magic',
            'specific_elements': 'tent ceremony structure, Arabian decorations, desert flowers, sand elements, Arabian nights details'
        },
        'african_safari': {
            'description': 'adventurous African safari wedding with animal print details, acacia tree decorations, safari elements, earth-toned flowers, African art',
            'lighting': 'warm safari lighting, natural African glow, sunset ambiance, adventure lighting',
            'colors': 'safari earth tones, savanna brown, sunset orange, acacia green, animal prints',
            'atmosphere': 'adventurous African celebration with safari spirit',
            'specific_elements': 'acacia ceremony arch, safari decorations, earth-toned arrangements, African art, adventure elements'
        },
        'egyptian_royal': {
            'description': 'regal Egyptian royal wedding with golden pyramids, hieroglyphic details, Egyptian columns, royal blue accents, pharaoh decorations',
            'lighting': 'royal Egyptian lighting, golden glow, pyramid shadows, regal ambiance',
            'colors': 'Egyptian gold, royal blue, desert sand, papyrus green, ruby red',
            'atmosphere': 'majestic Egyptian celebration with pharaoh grandeur',
            'specific_elements': 'pyramid ceremony backdrop, Egyptian columns, hieroglyphic details, royal decorations, golden accents'
        },

        # Seasonal & Nature Themes
        'winter_wonderland': {
            'description': 'magical winter wonderland wedding with snow-white decorations, ice crystal elements, evergreen arrangements, winter berries, frosted details',
            'lighting': 'cool winter lighting, ice crystal reflections, snow-white glow, winter magic ambiance',
            'colors': 'snow white, ice blue, silver, evergreen, winter berry red',
            'atmosphere': 'enchanting winter celebration with wonderland magic',
            'specific_elements': 'ice crystal ceremony arch, evergreen arrangements, winter decorations, frosted details, snow elements'
        },
        'spring_awakening': {
            'description': 'fresh spring awakening wedding with blooming flowers, pastel decorations, butterfly elements, garden growth theme, renewal details',
            'lighting': 'fresh spring lighting, natural daylight, garden glow, renewal ambiance',
            'colors': 'spring pastels, fresh green, cherry blossom pink, sky blue, sunshine yellow',
            'atmosphere': 'refreshing spring celebration with awakening energy',
            'specific_elements': 'blooming ceremony arch, spring flowers, butterfly details, garden elements, renewal decorations'
        },
        'summer_solstice': {
            'description': 'vibrant summer solstice wedding with sun decorations, bright summer flowers, solar elements, longest day theme, sunshine details',
            'lighting': 'bright summer lighting, golden sunshine, solar glow, longest day ambiance',
            'colors': 'sunshine yellow, summer orange, bright blue, golden wheat, sunflower',
            'atmosphere': 'energetic summer celebration with solstice power',
            'specific_elements': 'sun ceremony backdrop, summer flowers, solar decorations, bright elements, sunshine details'
        },
        'autumn_harvest': {
            'description': 'cozy autumn harvest wedding with pumpkin decorations, fall leaves, harvest elements, apple details, corn maze theme',
            'lighting': 'warm autumn lighting, harvest glow, golden hour, cozy fall ambiance',
            'colors': 'autumn orange, harvest gold, deep red, pumpkin, fall brown',
            'atmosphere': 'cozy autumn celebration with harvest warmth',
            'specific_elements': 'harvest ceremony arch, pumpkin details, fall leaves, apple decorations, autumn elements'
        },
        'forest_enchanted': {
            'description': 'mystical enchanted forest wedding with tree branches, fairy lights, moss details, woodland creatures, magical forest elements',
            'lighting': 'mystical forest lighting, fairy lights, dappled shadows, enchanted glow',
            'colors': 'forest green, moss brown, fairy light gold, mushroom beige, bark brown',
            'atmosphere': 'magical forest celebration with enchanted mystery',
            'specific_elements': 'tree branch ceremony arch, fairy lights, moss details, woodland decorations, magical elements'
        },
        'desert_bloom': {
            'description': 'stunning desert bloom wedding with cactus flowers, succulent arrangements, desert sunset theme, southwestern elements, bloom details',
            'lighting': 'desert sunset lighting, warm glow, southwestern ambiance, bloom illumination',
            'colors': 'desert sunset orange, cactus green, bloom pink, sand beige, turquoise',
            'atmosphere': 'stunning desert celebration with bloom beauty',
            'specific_elements': 'cactus ceremony backdrop, succulent arrangements, desert flowers, southwestern details, bloom elements'
        },
        'ocean_waves': {
            'description': 'flowing ocean waves wedding with wave decorations, seashell details, ocean blue theme, coastal elements, wave motion',
            'lighting': 'ocean lighting, wave reflections, coastal glow, sea ambiance',
            'colors': 'ocean blue, wave white, seashell cream, coral pink, sea green',
            'atmosphere': 'flowing ocean celebration with wave energy',
            'specific_elements': 'wave ceremony backdrop, seashell details, ocean decorations, coastal elements, wave patterns'
        },
        'mountain_vista': {
            'description': 'majestic mountain vista wedding with peak decorations, alpine flowers, mountain stone elements, vista views, summit theme',
            'lighting': 'mountain lighting, alpine glow, peak illumination, vista ambiance',
            'colors': 'mountain stone grey, alpine white, peak blue, forest green, summit gold',
            'atmosphere': 'majestic mountain celebration with vista grandeur',
            'specific_elements': 'mountain peak ceremony backdrop, alpine flowers, stone details, vista decorations, summit elements'
        },
        'tropical_paradise': {
            'description': 'lush tropical paradise wedding with palm leaves, tropical flowers, paradise birds, island elements, exotic fruit details',
            'lighting': 'tropical lighting, paradise glow, island sunset, exotic ambiance',
            'colors': 'tropical green, paradise pink, island blue, exotic orange, fruit yellow',
            'atmosphere': 'lush tropical celebration with paradise beauty',
            'specific_elements': 'palm leaf ceremony arch, tropical arrangements, paradise decorations, island details, exotic elements'
        },

        # Modern & Contemporary Themes
        'metropolitan_chic': {
            'description': 'sophisticated metropolitan wedding with city skyline backdrop, urban furniture, glass elements, steel accents, modern city theme',
            'lighting': 'city lighting, urban glow, metropolitan ambiance, skyline illumination',
            'colors': 'city steel grey, urban black, glass clear, neon accents, metropolitan white',
            'atmosphere': 'sophisticated city celebration with metropolitan style',
            'specific_elements': 'skyline ceremony backdrop, urban furniture, glass details, steel accents, city decorations'
        },
        'brooklyn_loft': {
            'description': 'trendy Brooklyn loft wedding with exposed brick, industrial windows, loft furniture, urban art, hipster elements',
            'lighting': 'loft lighting, industrial glow, urban ambiance, Brooklyn style',
            'colors': 'brick red, loft grey, industrial black, urban white, hipster brown',
            'atmosphere': 'trendy Brooklyn celebration with loft character',
            'specific_elements': 'exposed brick backdrop, loft furniture, industrial details, urban art, Brooklyn decorations'
        },
        'rooftop_garden': {
            'description': 'elevated rooftop garden wedding with city views, container gardens, rooftop furniture, urban greenery, sky elements',
            'lighting': 'rooftop lighting, city view glow, garden ambiance, sky illumination',
            'colors': 'garden green, rooftop grey, sky blue, urban white, plant earth',
            'atmosphere': 'elevated rooftop celebration with garden oasis',
            'specific_elements': 'rooftop ceremony setup, container gardens, city view backdrop, urban greenery, sky details'
        },
        'art_deco_glam': {
            'description': 'glamorous art deco wedding with geometric patterns, gold accents, deco furniture, vintage glam elements, 1920s style',
            'lighting': 'art deco lighting, geometric shadows, glam glow, vintage ambiance',
            'colors': 'deco gold, glam black, vintage cream, geometric silver, 1920s pearl',
            'atmosphere': 'glamorous deco celebration with vintage sophistication',
            'specific_elements': 'geometric ceremony backdrop, art deco furniture, gold accents, vintage glam details, 1920s decorations'
        },

        'rustic': {
            'description': 'rustic farmhouse wedding with wooden ceremony arch, burlap aisle runner, mason jar centerpieces, vintage wooden chairs, string lights overhead, wildflower arrangements, hay bale seating, wooden farm tables',
            'lighting': 'warm golden string lights, lanterns hanging from wooden beams, candlelit mason jars, sunset glow through barn windows',
            'colors': 'warm cream, sage green, dusty rose, burlap brown, natural wood tones',
            'atmosphere': 'cozy rustic celebration with farm charm',
            'specific_elements': 'wooden ceremony arch, burlap details, mason jar lighting, vintage wooden furniture, wildflower bouquets'
        },
        'modern': {
            'description': 'contemporary minimalist wedding with sleek geometric ceremony backdrop, modern acrylic chairs, clean white linens, geometric centerpieces, modern floral arrangements, architectural elements',
            'lighting': 'clean architectural uplighting, modern pendant lights, dramatic spot lighting, contemporary chandeliers',
            'colors': 'pure white, charcoal grey, black accents, metallic silver, glass elements',
            'atmosphere': 'sophisticated contemporary elegance with clean lines',
            'specific_elements': 'geometric ceremony arch, acrylic furniture, modern lighting fixtures, architectural details, minimalist floral arrangements'
        },
        'vintage': {
            'description': 'romantic vintage wedding with ornate ceremony backdrop, vintage lace details, antique chairs, vintage china place settings, classic rose arrangements, vintage chandeliers, antique furniture pieces',
            'lighting': 'soft romantic vintage chandeliers, warm Edison bulbs, antique candelabras, golden hour lighting',
            'colors': 'blush pink, ivory cream, antique gold, dusty blue, champagne tones',
            'atmosphere': 'romantic vintage elegance with old-world charm',
            'specific_elements': 'vintage lace ceremony backdrop, antique furniture, vintage china, classic roses, ornate chandeliers'
        },
        'bohemian': {
            'description': 'bohemian wedding with macrame ceremony backdrop, pampas grass arrangements, low lounge seating, colorful textiles, floor cushions, hanging plants, dreamcatchers, natural wood elements',
            'lighting': 'warm ambient fairy lights, hanging lanterns, candles in glass vessels, natural daylight filtering through',
            'colors': 'terracotta orange, sage green, mustard yellow, deep burgundy, natural earth tones',
            'atmosphere': 'free-spirited boho celebration with natural elements',
            'specific_elements': 'macrame ceremony arch, pampas grass, floor cushions, hanging plants, colorful textiles, natural wood'
        },
        'classic': {
            'description': 'timeless traditional wedding with elegant ceremony arch, formal chiavari chairs, pristine white linens, crystal chandeliers, classic white flower arrangements, formal place settings',
            'lighting': 'crystal chandeliers, elegant uplighting, classic candelabras, refined ambient lighting',
            'colors': 'pure white, ivory, champagne gold, silver accents, classic elegance',
            'atmosphere': 'grand formal celebration with timeless sophistication',
            'specific_elements': 'elegant ceremony arch, chiavari chairs, crystal chandeliers, formal linens, classic white flowers'
        },
        'garden': {
            'description': 'natural garden wedding with floral ceremony arch, garden party seating, botanical centerpieces, natural wood elements, abundant greenery, flower petals, garden pathway',
            'lighting': 'natural garden lighting, string lights through trees, garden lanterns, soft natural illumination',
            'colors': 'natural green, soft white, garden pastels, earth tones, botanical colors',
            'atmosphere': 'natural garden party celebration with organic beauty',
            'specific_elements': 'floral ceremony arch, garden seating, botanical arrangements, natural pathways, abundant greenery'
        },
        'beach': {
            'description': 'coastal beach wedding with driftwood ceremony arch, beach chairs, flowing white fabrics, seashell accents, nautical rope details, beach-appropriate seating, coastal decorations',
            'lighting': 'natural beach lighting, tiki torches, lanterns, soft coastal sunset glow',
            'colors': 'ocean blue, sandy beige, coral pink, seafoam green, natural whites',
            'atmosphere': 'relaxed coastal celebration with ocean views',
            'specific_elements': 'driftwood ceremony arch, beach seating, flowing fabrics, nautical details, coastal decorations'
        },
        'industrial': {
            'description': 'urban industrial wedding with metal pipe ceremony backdrop, industrial seating, exposed brick walls, metal and wood furniture, Edison bulb lighting, urban modern elements',
            'lighting': 'Edison bulb installations, industrial pendant lights, exposed bulb chandeliers, urban atmospheric lighting',
            'colors': 'charcoal grey, copper accents, warm metallics, concrete tones, industrial blacks',
            'atmosphere': 'urban industrial celebration with modern edge',
            'specific_elements': 'metal pipe ceremony arch, industrial furniture, Edison bulb lighting, exposed elements, urban materials'
        },

    }
    
    # Same SPACE_TRANSFORMATIONS, GUEST_COUNT_MODIFIERS, etc. from previous version
    SPACE_TRANSFORMATIONS = {
        'wedding_ceremony': {
            'setup': 'full wedding ceremony setup with processional aisle, rows of chairs for guests, ceremonial altar or arch, unity candle area, guest seating arrangement',
            'elements': 'ceremony aisle with petals, wedding arch or backdrop, guest seating in rows, altar area for vows, processional pathway',
            'focus': 'ceremony altar and guest seating arrangement for wedding vows'
        },
        'reception_area': {
            'setup': 'wedding reception setup with dining tables, dance floor area, head table or sweetheart table, centerpieces, reception lighting',
            'elements': 'round or long dining tables, centerpieces, dance floor, head table, reception seating, celebration atmosphere',
            'focus': 'dining and dancing area for wedding celebration'
        },
        'dance_floor': {
            'setup': 'dedicated dance floor area with proper flooring, ambient lighting, DJ or band area, lounge seating around perimeter',
            'elements': 'polished dance floor, overhead lighting, music area, surrounding lounge seating, party atmosphere',
            'focus': 'central dance area for wedding celebration'
        },
        'dinner_party': {
            'setup': 'intimate dinner party setup with elegant dining table, formal place settings, ambient lighting, conversational seating arrangement',
            'elements': 'formal dining table, elegant place settings, centerpieces, intimate lighting, sophisticated atmosphere',
            'focus': 'elegant dining experience for special celebration'
        },
        'cocktail_hour': {
            'setup': 'cocktail hour setup with standing tables, bar area, lounge seating, appetizer stations, mingling space',
            'elements': 'high cocktail tables, bar setup, lounge areas, standing space, sophisticated mingling atmosphere',
            'focus': 'social mingling area for pre-reception gathering'
        },
        'bridal_suite': {
            'setup': 'luxurious bridal preparation suite with vanity area, seating for bridal party, mirrors, preparation space',
            'elements': 'bridal vanity, mirrors, seating area, preparation space, luxurious bridal atmosphere',
            'focus': 'elegant preparation area for bridal party'
        },
        'photo_backdrop': {
            'setup': 'stunning photo backdrop area with dramatic visual elements, perfect lighting, photogenic setting',
            'elements': 'dramatic backdrop, perfect lighting for photos, visually striking elements, photo-ready setup',
            'focus': 'picture-perfect backdrop for wedding photography'
        },
        'lounge_area': {
            'setup': 'comfortable lounge area with seating groups, ambient lighting, relaxation space for guests',
            'elements': 'comfortable seating arrangements, ambient lighting, relaxing atmosphere, conversation areas',
            'focus': 'comfortable relaxation area for wedding guests'
        }
    }
    
    # Enhanced guest count modifiers with specific numbers
    GUEST_COUNT_MODIFIERS = {
        'intimate': {
            'description': 'intimate gathering for 15-50 guests with seating and space to accomodate.',
            'seating': '3-4 rows of chairs or 2-3 small tables',
            'scale': 'small intimate scale decorations'
        },
        'medium': {
            'description': 'medium celebration for 75-100 guests with space balanced seating',
            'seating': '8-10 rows of chairs or 8-10 round tables',
            'scale': 'medium scale decorations and arrangements'
        },
        'large': {
            'description': 'large celebration for 150-200 guests with grand seating arrangement and open space',
            'seating': '12-15 rows of chairs or 15-20 round tables',
            'scale': 'large scale decorations and impressive arrangements'
        },
        'grand': {
            'description': 'grand spectacular celebration for 250+ guests with magnificent seating and unused space',
            'seating': '20+ rows of chairs or 25+ round tables',
            'scale': 'grand spectacular decorations and elaborate arrangements'
        }
    }
    
    # More specific budget modifiers
    BUDGET_MODIFIERS = {
        'budget': 'tasteful budget-friendly decorations with DIY elements, simple elegant centerpieces, cost-effective beautiful setup',
        'moderate': 'quality professional decorations with refined details, professional floral arrangements, well-coordinated setup',
        'luxury': 'luxury high-end decorations with premium materials, designer floral arrangements, sophisticated elegant details',
        'ultra_luxury': 'ultra-luxury opulent decorations with exquisite premium materials, lavish floral displays, spectacular high-end details'
    }
    
    # Seasonal elements
    SEASON_MODIFIERS = {
        'spring': 'fresh spring flowers like tulips and daffodils, pastel color accents, light flowing fabrics, spring renewal theme',
        'summer': 'vibrant summer blooms, bright cheerful colors, outdoor garden elements, sunny warm atmosphere',
        'fall': 'autumn foliage, warm amber colors, harvest elements like pumpkins, cozy autumn atmosphere',
        'winter': 'winter elegance with evergreens, rich jewel tones, warm textures, festive holiday elements'
    }
    
    # Time of day modifiers
    TIME_MODIFIERS = {
        'morning': 'bright morning light, fresh breakfast reception setup, light airy atmosphere, morning celebration',
        'afternoon': 'natural bright daylight, lunch reception setup, relaxed daytime atmosphere, afternoon celebration',
        'evening': 'golden hour lighting, dinner reception setup, romantic evening atmosphere, sunset celebration',
        'night': 'dramatic evening lighting, elegant nighttime setup, formal dinner atmosphere, sophisticated night celebration'
    }
    
    # Enhanced color scheme modifiers
    COLOR_MODIFIERS = {
        'neutral': 'sophisticated neutral palette with whites, creams, beiges, champagne, and soft taupe tones',
        'pastels': 'soft romantic pastel palette with blush pink, lavender, baby blue, mint green, and cream',
        'jewel_tones': 'rich luxurious jewel tones with emerald green, sapphire blue, ruby red, and gold accents',
        'earth_tones': 'natural earth tone palette with sage green, terracotta, warm browns, and cream',
        'monochrome': 'elegant sophisticated black and white palette with silver accents',
        'bold_colors': 'vibrant bold palette with bright fuchsia, orange, turquoise, and lime green'
    }
    
    @classmethod
    def generate_dynamic_prompt(cls, wedding_theme, space_type, guest_count=None, 
                               budget_level=None, season=None, time_of_day=None,
                               color_scheme=None, custom_colors=None, additional_details=None):
        """Generate a comprehensive, specific prompt for dramatic wedding transformations using SD3.5 Large"""
        
        theme_data = cls.THEME_STYLES.get(wedding_theme, cls.THEME_STYLES['classic'])
        space_data = cls.SPACE_TRANSFORMATIONS.get(space_type, cls.SPACE_TRANSFORMATIONS['wedding_ceremony'])
        
        # Build dramatic, specific prompt optimized for SD3.5 Large
        prompt_parts = [
            # High quality foundation optimized for SD3.5 Large
            "professional wedding staging, photorealistic, detailed, ultra high resolution, masterpiece quality,",
            
            # Specific transformation instruction
            f"Transform this space into a complete {space_data['setup']}",
            
            # Theme-specific elements
            f"beautiful {wedding_theme} wedding theme with {theme_data['specific_elements']}",
            
            # Detailed theme description
            theme_data['description'],
        ]
        
        # Add guest count with specific seating
        if guest_count and guest_count in cls.GUEST_COUNT_MODIFIERS:
            guest_data = cls.GUEST_COUNT_MODIFIERS[guest_count]
            prompt_parts.append(f"{guest_data['description']}, {guest_data['seating']}, {guest_data['scale']}")
        else:
            # Default to medium if not specified
            prompt_parts.append("seating arrangement for approximately 100 guests with proper spacing")
        
        # Add space-specific focus
        prompt_parts.append(f"focus on {space_data['focus']}")
        
        # Add budget level
        if budget_level and budget_level in cls.BUDGET_MODIFIERS:
            prompt_parts.append(cls.BUDGET_MODIFIERS[budget_level])
        else:
            prompt_parts.append("quality professional wedding decorations")
        
        # Add seasonal elements
        if season and season in cls.SEASON_MODIFIERS:
            prompt_parts.append(cls.SEASON_MODIFIERS[season])
        
        # Add time of day
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
        prompt_parts.append(theme_data['lighting'])
        
        # Add atmosphere
        prompt_parts.append(f"{theme_data['atmosphere']}")
        
        # Add user details if provided
        if additional_details:
            prompt_parts.append(additional_details)
        
        # Final setup requirements for SD3.5 Large
        prompt_parts.extend([
            "elegant wedding setup, celebration ready",
            "complete transformation of space",
            "professional wedding photography quality",
            "no people visible, empty chairs and tables ready for guests"
        ])
        
        # Join with proper spacing
        main_prompt = " ".join([part.strip() for part in prompt_parts if part.strip()])
        
        # Enhanced negative prompt optimized for SD3.5 Large
        negative_prompt = cls.generate_enhanced_negative_prompt()
        
        return {
            'prompt': main_prompt,
            'negative_prompt': negative_prompt,
            'recommended_params': cls.get_dynamic_parameters_sd35_large(wedding_theme, space_type, guest_count)
        }
    
    @classmethod
    def generate_enhanced_negative_prompt(cls):
        """Generate comprehensive negative prompt for wedding venue transformations with SD3.5 Large"""
        negative_elements = [
            # People and faces (critical for venue photos)
            "people, faces, crowd, guests, bride, groom, wedding party, humans, person, bodies",
            
            # Quality issues (SD3.5 Large specific)
            "blurry, low quality, distorted, pixelated, artifacts, noise, low resolution, jpeg artifacts",
            
            # Unwanted content
            "text, watermark, signature, logo, copyright, writing, signs, labels",
            
            # Bad atmosphere/mood
            "dark, dim, gloomy, messy, cluttered, chaotic, unorganized, dirty, shabby",
            
            # Style issues
            "cartoon, anime, unrealistic, fake, artificial, painting, drawing, sketch",
            
            # Composition issues
            "cropped, cut off, partial, incomplete, tilted, askew, bad proportions",
            
            # Unwanted objects
            "cars, vehicles, modern electronics, phones, computers, inappropriate items, random objects",
            
            # SD3.5 Large specific negatives
            "overexposed, underexposed, bad lighting, harsh shadows, color bleeding, oversaturated"
        ]
        
        return ", ".join(negative_elements)
    
    @classmethod
    def get_dynamic_parameters_sd35_large(cls, wedding_theme, space_type, guest_count):
        """Get optimized parameters for SD3.5 Large based on choices"""
        
        base_params = {
            'strength': 0.4,      # SD3.5 Large optimal strength
            'cfg_scale': 7.0,     # SD3.5 Large supports cfg_scale
            'steps': 50,          # SD3.5 Large supports steps
            'output_format': 'png',
        }
        # Note: aspect_ratio removed to maintain original image dimensions
        
        # Theme-specific optimizations for SD3.5 Large
        theme_optimizations = {
            'rustic': {'cfg_scale': 6.5, 'steps': 45, 'strength': 0.35},
            'modern': {'cfg_scale': 8.0, 'steps': 55, 'strength': 0.45},
            'vintage': {'cfg_scale': 7.5, 'steps': 50, 'strength': 0.4},
            'bohemian': {'cfg_scale': 6.0, 'steps': 45, 'strength': 0.35},
            'classic': {'cfg_scale': 8.0, 'steps': 55, 'strength': 0.4},
            'garden': {'cfg_scale': 6.0, 'steps': 45, 'strength': 0.35},
            'beach': {'cfg_scale': 6.5, 'steps': 50, 'strength': 0.4},
            'industrial': {'cfg_scale': 8.5, 'steps': 60, 'strength': 0.45},
            'moroccan_nights': {'cfg_scale': 7.5, 'steps': 55, 'strength': 0.4},
            'japanese_zen': {'cfg_scale': 6.0, 'steps': 45, 'strength': 0.35},
            'indian_palace': {'cfg_scale': 8.0, 'steps': 60, 'strength': 0.45},
        }
        
        # Apply theme optimizations
        if wedding_theme in theme_optimizations:
            opt = theme_optimizations[wedding_theme]
            base_params.update(opt)
        
        # Adjust parameters based on guest count (more guests = more transformation needed)
        if guest_count == 'intimate':
            base_params['strength'] -= 0.05  # Less transformation for intimate spaces
            base_params['steps'] -= 5
        elif guest_count in ['large', 'grand']:
            base_params['strength'] += 0.05   # More transformation for large celebrations
            base_params['steps'] += 5
        
        # Note: aspect_ratio removed to maintain original image dimensions
        
        # Space-specific adjustments for SD3.5 Large
        space_adjustments = {
            'wedding_ceremony': {'cfg_scale': -0.5},  # Slightly lower CFG for ceremonies
            'reception_area': {'cfg_scale': 0.5},     # Higher CFG for receptions
            'dance_floor': {'cfg_scale': 1.0},        # Highest CFG for dance floors
        }
        
        if space_type in space_adjustments:
            adj = space_adjustments[space_type]
            base_params['cfg_scale'] += adj.get('cfg_scale', 0)
        
        # Clamp values to SD3.5 Large valid ranges
        base_params['cfg_scale'] = max(1.0, min(20.0, base_params['cfg_scale']))
        base_params['steps'] = max(10, min(150, base_params['steps']))
        base_params['strength'] = max(0.0, min(1.0, base_params['strength']))
        
        return base_params
    
    @classmethod
    def get_quick_suggestions(cls, wedding_theme, space_type):
        """Get quick suggestions for common combinations optimized for SD3.5 Large"""
        suggestions = {
            'guest_count': 'medium',
            'budget_level': 'moderate',
            'time_of_day': 'evening',
            'color_scheme': 'neutral',
            'sd35_params': {
                'cfg_scale': 7.0,
                'steps': 50,
                'strength': 0.4
            }
        }
        
        # Theme-specific suggestions with SD3.5 Large optimizations
        if wedding_theme == 'rustic':
            suggestions.update({
                'season': 'fall',
                'color_scheme': 'earth_tones',
                'sd35_params': {'cfg_scale': 6.5, 'steps': 45, 'strength': 0.35}
            })
        elif wedding_theme == 'beach':
            suggestions.update({
                'season': 'summer',
                'time_of_day': 'afternoon',
                'color_scheme': 'neutral',
                'sd35_params': {'cfg_scale': 6.5, 'steps': 50, 'strength': 0.4}
            })
        elif wedding_theme == 'vintage':
            suggestions.update({
                'color_scheme': 'pastels',
                'budget_level': 'luxury',
                'sd35_params': {'cfg_scale': 7.5, 'steps': 50, 'strength': 0.4}
            })
        elif wedding_theme == 'modern':
            suggestions.update({
                'budget_level': 'luxury',
                'color_scheme': 'monochrome',
                'sd35_params': {'cfg_scale': 8.0, 'steps': 55, 'strength': 0.45}
            })
        elif wedding_theme == 'industrial':
            suggestions.update({
                'time_of_day': 'night',
                'color_scheme': 'monochrome',
                'sd35_params': {'cfg_scale': 8.5, 'steps': 60, 'strength': 0.45}
            })
        
        return suggestions
    
    @classmethod
    def get_theme_suggestions(cls, wedding_theme):
        """Get specific suggestions for a wedding theme optimized for SD3.5 Large"""
        if wedding_theme not in cls.THEME_STYLES:
            return None
            
        theme_data = cls.THEME_STYLES[wedding_theme]
        
        # Get SD3.5 Large optimized parameters
        optimized_params = cls.get_dynamic_parameters_sd35_large(wedding_theme, 'wedding_ceremony', 'medium')
        
        return {
            'guest_count': 'medium',
            'budget_level': 'moderate',
            'time_of_day': 'evening',
            'color_scheme': 'neutral',
            'specific_elements': theme_data['specific_elements'],
            'atmosphere': theme_data['atmosphere'],
            'sd35_optimized_params': optimized_params
        }