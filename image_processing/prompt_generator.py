# image_processing/prompt_generator.py
# UPDATED: Comprehensive prompt generation with composition, emotional tone, activities, and wedding moments

class VenuePromptGenerator:
    """
    Enhanced wedding space prompt generation for Gemini.
    Focus: Detailed decorative styling without architectural changes.
    """
    
    @classmethod
    def generate_prompt(cls, wedding_theme, space_type=None, season=None, 
                       lighting_mood=None, color_scheme=None,
                       custom_prompt=None, user_instructions=None):
        """
        Generate detailed text prompts for wedding space transformations.
        
        Args:
            wedding_theme: Theme choice (required)
            space_type: Space type (optional)
            season: Optional season
            lighting_mood: Optional lighting preference
            color_scheme: Optional color palette
            custom_prompt: Custom user prompt (overrides guided mode)
            user_instructions: Additional user requests
            
        Returns:
            str: Complete text prompt for Gemini
        """
        
        # Custom prompt mode
        if custom_prompt and custom_prompt.strip():
            prompt = custom_prompt.strip()
            
            if user_instructions and user_instructions.strip():
                prompt += f" {user_instructions.strip()}"
            
            if 'decoration' not in prompt.lower() and 'decor' not in prompt.lower():
                prompt = f"Decorate and style this space as follows: {prompt}"
            
            if 'no people' not in prompt.lower() and 'without people' not in prompt.lower():
                prompt += " Show the beautifully staged space with zero people present."
            
            return prompt
        
        # Guided mode
        return cls._build_guided_prompt(
            wedding_theme, space_type, season, 
            lighting_mood, color_scheme, user_instructions
        )
    
    @classmethod
    def _build_guided_prompt(cls, wedding_theme, space_type=None, season=None,
                            lighting_mood=None, color_scheme=None, 
                            user_instructions=None):
        """Build detailed guided prompt from wedding parameters"""
        
        theme_styling = cls._get_theme_styling(wedding_theme, space_type)
        
        if space_type and space_type != 'na':
            prompt = f"Turn this space into a stunning {cls._get_space_description(space_type)} decorated with {theme_styling}"
        else:
            prompt = f"Decorate this wedding space with {theme_styling}"
        
        if season and season != 'na':
            seasonal_decor = cls._get_seasonal_decor(season)
            if seasonal_decor:
                prompt += f" {seasonal_decor}"
        
        if lighting_mood and lighting_mood != 'na':
            lighting_design = cls._get_lighting_design(lighting_mood)
            if lighting_design:
                prompt += f" {lighting_design}"
        
        if color_scheme and color_scheme != 'na':
            color_styling = cls._get_color_styling(color_scheme)
            if color_styling:
                prompt += f" {color_styling}"
        
        if user_instructions and user_instructions.strip():
            prompt += f" {user_instructions.strip()}"
        
        prompt += ". Remove and show no people or text in this image."
        
        return prompt
    
    @classmethod
    def _get_theme_styling(cls, wedding_theme, space_type):
        """Get detailed styling description combining theme and space - 80+ themes"""
        
        if wedding_theme == 'na':
            return "elegant wedding decor"
        
        theme_base = {
            # Classic Traditional Themes
            'rustic': 'rustic barn wedding featuring weathered wood farm aesthetics, tables with burlap runners and white lace overlays, mason jar centerpieces filled with wildflowers and baby\'s breath, sunflowers, vintage bottles, cross-back wooden chairs with burlap bow ties, wagon wheel decorations, checkered gingham ribbons, and wine barrel cocktail tables.',
            
            'modern': 'contemporary minimalist celebration with clear acrylic ghost aesthetics, tall cylinder vases holding single white orchids, metal centerpieces in gold or copper, crisp white linens with silver chargers, LED light strips in clean lines, monochromatic white flower arrangements, chrome, geometric backdrop panels, clear glass vessels, metallic balloon installations, sleek white flooring with modern sculptural elements, and precisely arranged minimalist decor.',
            
            'vintage': 'nostalgic vintage aesthetics with antique brass candelabras, lace doily overlays, pearl strand garlands, mercury glass vases with roses and peonies, velvet furniture in dusty rose, crystal punch bowls, Victorian parasols, and aged brass fixtures.',
            
            'classic': 'classic traditional elegance featuring gold & ivory, tall crystal candelabras, white taper candles, white rose and lily arrangements, crystal stemware, symmetrical floral arrangements, ivory silk draping with swag, and pearl accents.',
            
            'garden': 'enchanted garden theme with wrought iron, overflowing English garden flowers including roses peonies and delphinium in aged terracotta pots, moss, bird cage decorations, vintage watering cans as vases, climbing ivy on white trellises, potted topiaries, stone garden statues, wicker baskets with flowers, garden tool displays, natural wood elements.',
            
            'beach': 'coastal beach theme featuring driftwood centerpieces, air plants, nautical rope wrapped details, starfish and shells, hurricane lanterns with sand and candles, flowing white fabric, sea glass vessels, coral displays, ship wheels, anchor decorations, striped navy and white patterns, bamboo furniture, tropical flowers, and weathered wood.',
            
            'industrial': 'urban warehouse chic with exposed Edison bulb installations, concrete planters with succulents, metal pipe structures, raw wood and metal furniture, geometric copper centerpieces, leather seating elements, gear and pulley decorations, distressed metal signage, black metal, minimalist protea arrangements, vintage factory vibe, concrete and metal vessels, exposed brick backdrops, and industrial pendant lighting.',
            
            'bohemian': 'free-spirited bohemian style featuring macrame hangings, layered vintage rugs, pampas grass in ceramic vessels, mixed metal lanterns, eclectic furniture pieces, dreamcatcher installations, floor cushion seating with tassels, brass tables, wildflower arrangements in mismatched bottles, feather accents, wooden bead garlands, paisley patterns, mandala decorations, incense holders.',
            
            'glamorous': 'Hollywood regency opulence with crystal, mirrored furniture and tables, sequined linens in gold and silver, tall ostrich feather centerpieces, art deco patterns, velvet draping in jewel tones, gold candelabras, rhinestone scatter, crystal & metallic, champagne tower, gilded everything, dramatic spotlighting, and luxurious metallic accents throughout.',
            
            'tropical': 'vibrant tropical paradise with palm fronds, monstera leaves, bird of paradise flowers, bamboo, tiki torches, colorful orchids, pineapple displays, coconut vessels, bright hibiscus, tropical fruit arrangements, rattan furniture, vibrant sunset colors, and island-inspired decor.',
            
            'fairy_tale': 'enchanted fairy tale magic with twinkling fairy lights everywhere, crystal accents, white flowing fabric draping, flower garlands, ornate gold frames, vintage books as decor, antique keys, romantic candelabras, dreamy tulle, enchanted forest elements, and whimsical magical touches.',
            
            'minimalist': 'clean minimalist design with simple lines, monochromatic palette, sparse elegant arrangements, geometric shapes, modern vessels, negative space, understated sophistication, white or neutral tones, simple greenery, and refined simplicity.',
            
            'romantic': 'romantic dreamy ambiance with soft pink and white roses, flowing chiffon draping, candlelight, crystal chandeliers, pearl details, blush tones, delicate lace, romantic lighting, elegant script signage, and abundant soft florals.',
            
            'elegant': 'sophisticated elegance with tall floral arrangements, crystal glassware, white tablecloths, gold chiavari chairs, classic candelabras, refined centerpieces, luxurious fabrics, timeless decor, and upscale details.',
            
            'chic': 'contemporary chic style with modern clean lines, sophisticated color palettes, sleek furniture, stylish centerpieces, trendy geometric elements, fashionable accents, and upscale contemporary touches.',
            
            'timeless': 'timeless classic beauty with enduring elegant elements, traditional refined decor, sophisticated arrangements, classic white and ivory tones, crystal accents, and eternally beautiful styling.',
            
            'country_barn': 'country barn charm with hay bales, wagon wheels, checkered fabrics, wildflower bouquets, vintage farm equipment, wooden barrels, mason jars, sunflowers, and rustic country elements.',
            
            'art_deco': 'Art Deco glamour with geometric patterns, gold and black color scheme, feather centerpieces, mirror accents, stepped designs, luxurious fabrics, metallic touches, and 1920s-inspired elegance.',
            
            'scandinavian': 'Scandinavian hygge warmth with simple natural wood, white linens, greenery garlands, candles everywhere, cozy textures, minimal arrangements, neutral colors, and comfortable intimate styling.',
            
            'mediterranean': 'Mediterranean beauty with olive branches, lemons and citrus, terracotta pots, blue and white tiles, rustic wood tables, white linens, herbs as decor, coastal elements, and sunny warmth.',
            
            'prairie_wildflower': 'prairie wildflower natural beauty with abundant wildflowers, wheat stalks, natural grasses, simple mason jars, burlap accents, sunset colors, and open field-inspired decor.',
            
            'winter_wonderland': 'winter wonderland magic with white and silver everywhere, crystal snowflakes, white branches, fairy lights, silver pinecones, white flowers, frosted elements, and icy elegance.',
            
            'spring_fresh': 'fresh spring beauty with pastel flowers, tulips and daffodils, light airy fabrics, butterfly accents, cherry blossoms, fresh greenery, soft colors, and new bloom freshness.',
            
            'harvest_festival': 'harvest festival warmth with pumpkins, gourds, autumn leaves, wheat bundles, corn stalks, apple displays, fall colors, rustic wood, and abundant harvest elements.',
            
            'whimsical': 'whimsical playful charm with colorful balloons, paper flowers, bunting flags, vintage toys, mismatched furniture, rainbow colors, fun props, and creative playful touches.',
            
            'monochrome': 'striking monochrome design with black and white only, dramatic contrast, graphic elements, bold patterns, sophisticated simplicity, and classic black and white elegance.',
            
            'statement_bold': 'bold statement design with bright colors, large dramatic arrangements, eye-catching centerpieces, oversized elements, vibrant tones, and daring creative choices.',
            
            'soft_dreamy': 'soft dreamy romance with pastel colors, flowing fabrics, delicate flowers, gentle lighting, romantic details, ethereal elements, and dreamy soft touches.',
            
            'luxury': 'premium luxury opulence with the finest materials, crystal chandeliers, gold accents everywhere, lavish floral arrangements, plush seating, expensive fabrics, and extravagant elegant details.',
            
            # Cultural & Traditional Themes
            'japanese_zen': 'Japanese Zen serenity with bamboo, cherry blossoms, paper lanterns, minimalist arrangements, ikebana flower style, tatami mats, bonsai trees, stone elements, and peaceful simplicity.',
            
            'chinese_dynasty': 'Chinese Dynasty elegance with red and gold colors, paper lanterns, dragon motifs, silk fabrics, peonies, traditional patterns, ornate details, and imperial luxury.',
            
            'indian_palace': 'Indian palace grandeur with vibrant colors, marigold garlands, ornate fabrics, gold details, peacock motifs, traditional patterns, rich textiles, and opulent decorations.',
            
            'korean_hanbok': 'Korean Hanbok tradition with bright silk colors, traditional patterns, paper fans, lotus flowers, elegant simplicity, cultural motifs, and refined Korean aesthetics.',
            
            'thai_temple': 'Thai temple beauty with gold accents, lotus flowers, silk fabrics, ornate carvings, tropical flowers, traditional patterns, and temple-inspired elegance.',
            
            'scottish_highland': 'Scottish Highland heritage with tartan patterns, heather, thistles, whisky barrels, bagpipe decorations, clan colors, rustic wood, and Scottish tradition.',
            
            'french_chateau': 'French château elegance with lavender, vintage furniture, crystal chandeliers, toile fabrics, French country charm, elegant details, and château sophistication.',
            
            'greek_island': 'Greek island beauty with white and blue colors, olive branches, Mediterranean herbs, coastal elements, simple elegance, whitewashed surfaces, and Aegean charm.',
            
            'italian_villa': 'Italian villa romance with tuscan colors, grapevines, olive branches, terracotta pots, Italian cypress, rustic elegance, wine country charm, and villa sophistication.',
            
            'english_garden': 'English garden charm with roses, peonies, garden urns, vintage furniture, tea party elements, cottage flowers, climbing vines, and classic garden beauty.',
            
            'mexican_fiesta': 'Mexican fiesta celebration with bright papel picado, colorful serapes, marigolds, cacti, piñatas, vibrant textiles, festive colors, and lively Mexican spirit.',
            
            'spanish_hacienda': 'Spanish hacienda elegance with terra cotta, iron details, vibrant tiles, bougainvillea, rustic wood, Spanish patterns, courtyard elements, and hacienda charm.',
            
            'brazilian_carnival': 'Brazilian carnival energy with bright feathers, samba colors, tropical flowers, festive decorations, vibrant energy, carnival masks, and Rio celebration.',
            
            'argentine_tango': 'Argentine tango passion with deep reds, dramatic roses, elegant details, tango-inspired elements, sophisticated romance, and Buenos Aires glamour.',
            
            'moroccan_nights': 'Moroccan nights magic with jewel tones, lanterns, poufs, intricate patterns, gold details, tea glasses, spices, and exotic Moroccan beauty.',
            
            'arabian_desert': 'Arabian desert mystique with rich fabrics, gold accents, ornate lanterns, jewel tones, luxurious textiles, desert roses, and Middle Eastern elegance.',
            
            'african_safari': 'African safari adventure with natural elements, animal prints, earth tones, tribal patterns, wooden details, tropical leaves, and safari-inspired decor.',
            
            'egyptian_royal': 'Egyptian royal grandeur with gold and turquoise, papyrus, lotus flowers, hieroglyphic patterns, ornate details, regal colors, and pharaoh-inspired luxury.',
            
            # Nature & Seasonal Themes
            'spring_awakening': 'spring awakening freshness with cherry blossoms, tulips, fresh greens, pastel flowers, butterfly accents, new growth, and spring renewal.',
            
            'summer_solstice': 'summer solstice warmth with sunflowers, bright colors, garden flowers, sunny yellow, vibrant energy, outdoor elements, and peak summer beauty.',
            
            'autumn_harvest': 'autumn harvest abundance with fall leaves, pumpkins, gourds, wheat, autumn flowers, warm colors, harvest elements, and seasonal richness.',
            
            'forest_enchanted': 'enchanted forest magic with moss, ferns, tree branches, woodland flowers, natural wood, fairy lights, forest elements, and mystical nature.',
            
            'desert_bloom': 'desert bloom beauty with succulents, cacti, desert flowers, sand colors, terra cotta, southwestern elements, and desert-inspired elegance.',
            
            'ocean_waves': 'ocean waves serenity with coastal blues, shells, driftwood, sea glass, nautical touches, beach elements, and oceanic beauty.',
            
            'mountain_vista': 'mountain vista majesty with natural wood, evergreens, pine cones, stone elements, rustic touches, alpine flowers, and mountain elegance.',
            
            # Modern & Contemporary Themes
            'metropolitan_chic': 'metropolitan chic style with urban sophistication, modern lines, city elements, contemporary elegance, sleek design, and cosmopolitan flair.',
            
            'brooklyn_loft': 'Brooklyn loft vibe with exposed brick, industrial windows, Edison bulbs, urban plants, modern furniture, artistic touches, and loft sophistication.',
            
            'rooftop_garden': 'rooftop garden beauty with city views, modern planters, urban greenery, sleek furniture, contemporary outdoor style, and skyline elegance.',
            
            'art_deco_glam': 'Art Deco glam with geometric patterns, metallic accents, bold colors, vintage elegance, stepped designs, and 1920s luxury.',
            
            'concrete_jungle': 'concrete jungle modern with industrial concrete, urban plants, metal accents, contemporary style, city sophistication, and urban elegance.',
            
            'glass_house': 'glass house modern with clean lines, transparent elements, minimal decor, modern furniture, architectural beauty, and contemporary sophistication.',
            
            # Vintage & Retro Themes
            '1950s_diner': '1950s diner retro with checkered floors, chrome accents, vintage soda shop style, pastel colors, retro furniture, and classic American diner charm.',
            
            '1960s_mod': '1960s Mod style with bold patterns, bright colors, geometric shapes, vintage furniture, psychedelic touches, and swinging sixties flair.',
            
            '1970s_disco': '1970s disco energy with mirror balls, metallic accents, bold colors, funky patterns, platform style, and disco fever glamour.',
            
            '1980s_neon': '1980s neon bright with neon colors, geometric patterns, bold contrasts, metallic balloons, retro elements, and radical eighties style.',
            
            '1990s_grunge': '1990s grunge aesthetic with flannel patterns, alternative style, vintage furniture, indie vibe, muted colors, and alternative elegance.',
            
            'victorian_romance': 'Victorian romance with ornate details, velvet fabrics, antique furniture, lace elements, romantic flowers, vintage elegance, and period charm.',
            
            'art_nouveau': 'Art Nouveau beauty with organic lines, flowing forms, floral motifs, elegant curves, natural elements, and turn-of-century artistry.',
            
            'great_gatsby': 'Great Gatsby glamour with gold and black, feathers, pearls, art deco patterns, champagne towers, jazz age luxury, and roaring twenties opulence.',
        }
        
        return theme_base.get(wedding_theme, 'elegant wedding decor')
    
    @classmethod
    def _get_space_description(cls, space_type):
        """Get space type description"""
        if space_type == 'na':
            return "wedding space"
        
        spaces = {
            'wedding_ceremony': 'wedding ceremony area with aisle and altar',
            'dance_floor': 'dance floor and party area',
            'dining_area': 'reception dining area with elegant tables',
            'cocktail_hour': 'cocktail reception area',
            'bridal_suite': 'bridal suite and getting ready space',
            'entrance_area': 'entrance and welcome area',
        }
        return spaces.get(space_type, 'wedding space')
    
    @classmethod
    def _get_seasonal_decor(cls, season):
        """Get seasonal decorative elements"""
        if season == 'na':
            return ''
        
        seasons = {
            'spring': 'Add seasonal spring elements like tulips, cherry blossoms, pastel flowers, and fresh greenery.',
            'summer': 'Add seasonal summer elements like sunflowers, bright blooms, lush greenery, and warm sunshine vibes.',
            'fall': 'Add seasonal fall elements like autumn leaves, pumpkins, gourds, warm oranges and reds, and harvest touches.',
            'winter': 'Add seasonal winter elements like evergreens, pinecones, white flowers, silver accents, and cozy winter elegance.',
        }
        return seasons.get(season, '')
    
    @classmethod
    def _get_lighting_design(cls, lighting_mood):
        """Get lighting mood description"""
        if lighting_mood == 'na':
            return ''
        
        lights = {
            'romantic': 'Light the space with romantic warm lighting, creating soft glows and intimate ambiance.',
            'bright': 'Light the space with bright cheerful lighting, ensuring vibrant clear illumination.',
            'dim': 'Light the space with dim intimate lighting, creating cozy moody atmosphere.',
            'dramatic': 'Light the space with dramatic lighting using bold contrasts and theatrical effects.',
            'natural': 'Use natural daylight to illuminate the space with soft organic light.',
            'golden': 'Bathe the space in golden hour warm honeyed glow.',
            'dusk': 'Light the space with dusk twilight tones of soft purple and pink.',
            'dawn': 'Light the space with dawn fresh clear morning light.',
        }
        return lights.get(lighting_mood, '')
    
    @classmethod
    def _get_color_styling(cls, color_scheme):
        """Get color palette styling"""
        if color_scheme == 'na':
            return ''
        
        colors = {
            'red': 'Use a red color palette throughout the decor.',
            'pink': 'Use a pink color palette throughout the decor.',
            'coral': 'Use a coral color palette throughout the decor.',
            'orange': 'Use an orange color palette throughout the decor.',
            'yellow': 'Use a yellow color palette throughout the decor.',
            'green': 'Use a green color palette throughout the decor.',
            'blue': 'Use a blue color palette throughout the decor.',
            'purple': 'Use a purple color palette throughout the decor.',
            'white': 'Use a white color palette throughout the decor.',
            'black': 'Use a black color palette throughout the decor.',
            
            'gold': 'Use gold metallic accents throughout the decor.',
            'silver': 'Use silver metallic accents throughout the decor.',
            
            'blush_gold': 'Use a blush pink and gold color palette.',
            'navy_gold': 'Use a navy blue and gold color palette.',
            'burgundy_gold': 'Use a burgundy and gold color palette.',
            
            'earth_tones': 'Use natural earth tone colors throughout.',
            'jewel_tones': 'Use rich jewel tone colors throughout.',
            'vibrant_bold': 'Use vibrant bold colors with high saturation.',
            'muted_soft': 'Use muted soft colors throughout.',
            'monochrome': 'Use a monochrome color scheme.',
        }
        return colors.get(color_scheme, '')


class PortraitPromptGenerator:
    """
    Enhanced portrait prompt generation for engagement and wedding photos.
    NEW: Includes composition, emotional tone, extensive activities, and wedding moments.
    """
    
    @classmethod
    def generate_prompt(cls, studio_mode, 
                       # Engagement fields
                       engagement_setting=None, engagement_activity=None,
                       # Wedding fields
                       wedding_moment=None, wedding_setting=None,
                       # Shared fields
                       attire_style=None, composition=None, emotional_tone=None,
                       season=None, lighting_mood=None, color_scheme=None,
                       custom_prompt=None, user_instructions=None):
        """
        Generate portrait prompts for engagement or wedding photos.
        
        Args:
            studio_mode: 'portrait_engagement' or 'portrait_wedding'
            engagement_setting: Setting for engagement (optional)
            engagement_activity: Activity for engagement (required for engagement)
            wedding_moment: Moment/scene for wedding (required for wedding)
            wedding_setting: Setting for wedding (optional)
            attire_style: Clothing style (optional)
            composition: Camera angle/framing (optional)
            emotional_tone: Mood/feeling (optional)
            season: Optional season
            lighting_mood: Optional lighting
            color_scheme: Optional color palette
            custom_prompt: Custom user prompt (overrides guided mode)
            user_instructions: Additional user requests
            
        Returns:
            str: Complete text prompt for Gemini
        """
        
        # Custom prompt mode
        if custom_prompt and custom_prompt.strip():
            prompt = custom_prompt.strip()
            
            if user_instructions and user_instructions.strip():
                prompt += f" {user_instructions.strip()}"
            
            return prompt
        
        # Guided mode
        if studio_mode == 'portrait_engagement':
            return cls._build_engagement_prompt(
                engagement_setting, engagement_activity,
                attire_style, composition, emotional_tone,
                season, lighting_mood, color_scheme,
                user_instructions
            )
        else:  # portrait_wedding
            return cls._build_wedding_prompt(
                wedding_moment, wedding_setting,
                attire_style, composition, emotional_tone,
                season, lighting_mood, color_scheme,
                user_instructions
            )
    
    @classmethod
    def _build_engagement_prompt(cls, setting, activity, attire, composition, 
                                 emotional_tone, season, lighting, color_scheme,
                                 user_instructions):
        """Build engagement portrait prompt"""
        
        # Start with activity (required)
        prompt = f"Create a beautiful engagement portrait. {cls._get_activity_description(activity)}"
        
        # Add setting if provided (with embedded season if setting exists)
        if setting and setting != 'na':
            prompt += f" {cls._get_setting_description(setting, 'engagement', season)}"
        # Add season independently if no setting was provided
        elif season and season != 'na':
            seasonal_atmosphere = cls._get_seasonal_atmosphere(season)
            if seasonal_atmosphere:
                prompt += f" {seasonal_atmosphere}"
        
        # Add attire if provided
        if attire and attire != 'na':
            prompt += f" {cls._get_attire_description(attire, 'engagement')}"
        
        # Add composition if provided
        if composition and composition != 'na':
            prompt += f" {cls._get_composition_description(composition)}"
        
        # Add emotional tone if provided
        if emotional_tone and emotional_tone != 'na':
            prompt += f" {cls._get_emotional_tone_description(emotional_tone)}"
        
        # Add lighting if provided
        if lighting and lighting != 'na':
            prompt += f" {cls._get_lighting_description(lighting)}"
        
        # Add color scheme if provided
        if color_scheme and color_scheme != 'na':
            prompt += f" {cls._get_color_description(color_scheme)}"
        
        # Add user instructions
        if user_instructions and user_instructions.strip():
            prompt += f" {user_instructions.strip()}"
        
        prompt += ""
        
        return prompt
    
    @classmethod
    def _build_wedding_prompt(cls, moment, setting, attire, composition,
                             emotional_tone, season, lighting, color_scheme,
                             user_instructions):
        """Build wedding portrait prompt"""
        
        # Start with moment/scene (required)
        prompt = f"A beautiful wedding portrait. {cls._get_wedding_moment_description(moment)}"
        
        # Add setting if provided (with embedded season if setting exists)
        if setting and setting != 'na':
            prompt += f" {cls._get_wedding_setting_description(setting, season)}"
        # Add season independently if no setting was provided
        elif season and season != 'na':
            seasonal_atmosphere = cls._get_seasonal_atmosphere(season)
            if seasonal_atmosphere:
                prompt += f" {seasonal_atmosphere}"
        
        # Add attire if provided
        if attire and attire != 'na':
            prompt += f" {cls._get_attire_description(attire, 'wedding')}"
        
        # Add composition if provided
        if composition and composition != 'na':
            prompt += f" {cls._get_composition_description(composition)}"
        
        # Add emotional tone if provided
        if emotional_tone and emotional_tone != 'na':
            prompt += f" {cls._get_emotional_tone_description(emotional_tone)}"
        
        # Add lighting if provided
        if lighting and lighting != 'na':
            prompt += f" {cls._get_lighting_description(lighting)}"
        
        # Add color scheme if provided
        if color_scheme and color_scheme != 'na':
            prompt += f" {cls._get_color_description(color_scheme)}"
        
        # Add user instructions
        if user_instructions and user_instructions.strip():
            prompt += f" {user_instructions.strip()}"
        
        prompt += ""
        
        return prompt
    
    # === NEW: COMPOSITION DESCRIPTIONS ===
    @classmethod
    def _get_composition_description(cls, composition):
        """Get camera angle and framing description"""
        compositions = {
            # Standard Framing
            'portrait_closeup': 'Frame as a portrait close-up, capturing the face and upper shoulders in detail.',
            'medium_shot': 'Frame as a medium shot, showing from the waist up.',
            'full_body': 'Frame as a full body shot, showing from head to toe.',
            'three_quarter': 'Frame as a three-quarter length shot.',
            'cowboy_shot': 'Frame as a cowboy shot, from mid-thigh up.',
            
            # Environmental
            'wide_environmental': 'Use a wide environmental composition that shows the full setting and context.',
            'tight_intimate': 'Use tight intimate framing, filling the frame with the subjects.',
            'negative_space': 'Use negative space composition with minimalist framing.',
            
            # Angles & Perspectives
            'eye_level': 'Shoot from eye level, straight on.',
            'high_angle': 'Shoot from a high angle, looking down at the subjects.',
            'low_angle': 'Shoot from a low angle, looking up at the subjects for a dramatic perspective.',
            'dutch_angle': 'Use a dutch angle with a slight tilt for dynamic energy.',
            'birds_eye': 'Shoot from a bird\'s eye view, directly above the subjects.',
            'worm_eye': 'Shoot from a worm\'s eye view, from ground level looking up.',
            
            # Drone & Aerial
            'drone_overhead': 'Capture with a drone overhead aerial view, looking straight down.',
            'drone_high_wide': 'Capture with a drone from high altitude showing the wide landscape.',
            'drone_low_following': 'Capture with a drone at low altitude, following the subjects.',
            'drone_orbit': 'Capture with a drone orbiting around the subjects.',
            
            # Creative Composition
            'rule_of_thirds': 'Compose using the rule of thirds for balanced framing.',
            'centered_symmetrical': 'Use centered symmetrical composition.',
            'leading_lines': 'Use leading lines and perspective to draw the eye.',
            'framing_natural': 'Frame the subjects naturally through architectural or natural elements.',
            'foreground_interest': 'Include foreground interest elements to create depth.',
            'silhouette': 'Create a silhouette with backlit subjects.',
            'reflection': 'Capture reflection in water or mirror.',
            'through_window': 'Photograph through a window or glass.',
            'doorway_frame': 'Frame through a doorway or architectural element.',
            'over_shoulder': 'Shoot from an over-the-shoulder perspective.',
            'between_elements': 'Peek between elements or through objects.',
            
            # Movement
            'walking_toward': 'Capture subjects walking toward the camera.',
            'walking_away': 'Capture subjects walking away from the camera.',
            'motion_blur': 'Use motion blur to show movement and energy.',
            'frozen_action': 'Freeze the action with sharp focus.',
        }
        return compositions.get(composition, '')
    
    # === NEW: EMOTIONAL TONE DESCRIPTIONS ===
    @classmethod
    def _get_emotional_tone_description(cls, emotional_tone):
        """Get mood and feeling description"""
        tones = {
            # Positive & Joyful
            'joyful_happy': 'Capture a joyful and happy mood, filled with smiles and laughter.',
            'romantic_loving': 'Convey a romantic and loving mood, showing deep affection.',
            'playful_fun': 'Create a playful and fun atmosphere with spontaneous energy.',
            'celebratory': 'Capture a celebratory and festive mood.',
            'intimate_tender': 'Show intimate and tender moments with gentle closeness.',
            'passionate': 'Convey passionate and intense emotion.',
            'serene_peaceful': 'Create a serene and peaceful mood.',
            'elegant_sophisticated': 'Show elegant and sophisticated refinement.',
            
            # Candid & Natural
            'candid_natural': 'Capture candid and natural authentic moments.',
            'relaxed_comfortable': 'Show relaxed and comfortable ease.',
            'authentic_genuine': 'Convey authentic and genuine emotion.',
            'spontaneous': 'Capture spontaneous in-the-moment energy.',
            
            # Emotional & Meaningful
            'emotional_touching': 'Create emotional and touching depth.',
            'nostalgic': 'Convey nostalgic and sentimental feeling.',
            'dreamy_ethereal': 'Show dreamy and ethereal quality.',
            'magical_enchanted': 'Create magical and enchanted wonder.',
            
            # Energetic & Dynamic
            'energetic_vibrant': 'Capture energetic and vibrant excitement.',
            'adventurous': 'Show adventurous and bold spirit.',
            'dynamic_action': 'Convey dynamic action-packed energy.',
            
            # Artistic & Moody
            'dramatic_striking': 'Create dramatic and striking impact.',
            'moody_atmospheric': 'Show moody atmospheric depth.',
            'artistic_editorial': 'Use artistic editorial style.',
            'vintage_timeless': 'Create vintage timeless feel.',
            'cinematic': 'Use cinematic film-like quality.',
        }
        return tones.get(emotional_tone, '')
    
    # === ACTIVITY DESCRIPTIONS (150+ Activities) ===
    @classmethod
    def _get_activity_description(cls, activity):
        """Get engagement activity description"""
        activities = {
            # === ROMANTIC POSES ===
            'romantic_embrace': 'The couple is in a romantic embrace, holding each other close.',
            'forehead_kiss': 'One person is gently kissing the other on the forehead.',
            'nose_to_nose': 'The couple is nose to nose in an Eskimo kiss.',
            'hand_kiss': 'One person is kissing the other\'s hand romantically.',
            'cheek_kiss': 'One person is kissing the other on the cheek.',
            'looking_into_eyes': 'The couple is looking deeply into each other\'s eyes.',
            'tender_hold': 'They are in a tender hold, cuddling closely.',
            'back_hug': 'One person is hugging the other from behind.',
            'dip_kiss': 'They are in a romantic dip kiss pose.',
            
            # === CANDID & JOYFUL ===
            'candid_laughing': 'The couple is laughing naturally with genuine joy.',
            'playful_fun': 'They are in a playful, fun moment together.',
            'tickle_fight': 'They are having a tickle fight, laughing playfully.',
            'piggyback_ride': 'One person is giving the other a piggyback ride.',
            'twirling_spinning': 'One person is twirling or spinning the other.',
            'jumping_together': 'They are jumping together in celebration.',
            'running_toward': 'They are running toward the camera or each other.',
            'blowing_bubbles': 'They are blowing bubbles together playfully.',
            'confetti_throw': 'They are throwing confetti in celebration.',
            
            # === WALKING & MOVEMENT ===
            'walking_together': 'The couple is walking together hand-in-hand.',
            'walking_arm_in_arm': 'They are walking arm in arm.',
            'walking_beach': 'They are walking along the beach or shore.',
            'strolling_city': 'They are strolling through city streets.',
            'dancing_street': 'They are dancing together in the street.',
            'running_field': 'They are running through an open field.',
            
            # === SITTING & INTIMATE ===
            'sitting_intimate': 'The couple is sitting close together intimately.',
            'sitting_bench': 'They are sitting together on a bench.',
            'sitting_blanket': 'They are sitting on a blanket for a picnic.',
            'sitting_steps': 'They are sitting on steps or stairs.',
            'sitting_dock': 'They are sitting on a dock or pier.',
            'lying_grass': 'They are lying together in the grass.',
            'lying_bed': 'They are lying on a bed cozily.',
            'sitting_back_to_back': 'They are sitting back to back.',
            
            # === CREATIVE & ARTISTIC ===
            'silhouette_sunset': 'Capture them as silhouettes at sunset or sunrise.',
            'reflection_water': 'Capture their reflection in water.',
            'mirror_reflection': 'Show their reflection in a mirror or glass.',
            'through_window': 'Photograph them through a window.',
            'framed_doorway': 'Frame them in a doorway or architectural element.',
            'with_balloons': 'They are holding colorful balloons.',
            'with_sparklers': 'They are holding sparklers or small fireworks.',
            'umbrella_rain': 'They are under an umbrella in the rain.',
            'wrapped_blanket': 'They are wrapped together in a cozy blanket.',
            
            # === FOOD & CULINARY ===
            'cooking_together': 'The couple is cooking together in a kitchen.',
            'baking_together': 'They are baking together, making dessert.',
            'making_pizza': 'They are making pizza together playfully.',
            'coffee_date': 'They are having a coffee date, holding warm mugs.',
            'wine_tasting': 'They are wine tasting or toasting with wine glasses.',
            'picnic_eating': 'They are having a romantic picnic together.',
            'feeding_each_other': 'They are feeding each other food.',
            'breakfast_in_bed': 'They are having breakfast in bed.',
            'ice_cream_date': 'They are on an ice cream date, sharing.',
            'farmers_market_shop': 'They are shopping together at a farmers market.',
            
            # === SPORTS & ACTIVE ===
            'hiking_trail': 'The couple is hiking on a mountain trail.',
            'biking_together': 'They are biking together on a path.',
            'skiing': 'They are skiing together on snowy slopes.',
            'snowboarding': 'They are snowboarding together.',
            'kayaking': 'They are kayaking or canoeing together.',
            'rock_climbing': 'They are rock climbing together.',
            'surfing': 'They are surfing together in the ocean.',
            'skateboarding': 'They are skateboarding together.',
            'rollerblading': 'They are rollerblading or skating together.',
            'yoga_together': 'They are doing yoga poses together.',
            'running_jogging': 'They are running or jogging together.',
            'playing_frisbee': 'They are playing frisbee together.',
            'playing_catch': 'They are playing catch with a ball.',
            'basketball_court': 'They are playing basketball together.',
            'soccer_field': 'They are playing soccer together.',
            'tennis_court': 'They are playing tennis together.',
            'golf_course': 'They are golfing together on a course.',
            'swimming_pool': 'They are swimming together in a pool.',
            'beach_volleyball': 'They are playing beach volleyball.',
            
            # === CREATIVE & HOBBIES ===
            'painting_together': 'The couple is painting or creating art together.',
            'pottery_making': 'They are making pottery or ceramics together.',
            'photography_shoot': 'They are taking photos together with a camera.',
            'playing_music': 'They are playing musical instruments together.',
            'singing_karaoke': 'They are singing karaoke together.',
            'dancing_ballroom': 'They are ballroom dancing elegantly.',
            'dancing_salsa': 'They are salsa or Latin dancing together.',
            'dancing_swing': 'They are swing dancing together.',
            'playing_board_game': 'They are playing a board game together.',
            'playing_video_games': 'They are playing video games together.',
            'playing_cards': 'They are playing cards together.',
            'puzzle_together': 'They are doing a puzzle together.',
            'reading_together': 'They are reading books together.',
            'writing_together': 'They are writing or journaling together.',
            'crafting_diy': 'They are working on a craft or DIY project.',
            
            # === RELAXATION & LEISURE ===
            'watching_sunset': 'The couple is watching the sunset together.',
            'watching_sunrise': 'They are watching the sunrise together.',
            'stargazing': 'They are stargazing, looking at the stars.',
            'watching_movie': 'They are watching a movie or TV together.',
            'lounging_couch': 'They are lounging together on a couch.',
            'hammock_relaxing': 'They are relaxing together in a hammock.',
            'hot_tub': 'They are in a hot tub or jacuzzi together.',
            'spa_treatment': 'They are getting a spa treatment or massage.',
            'meditation': 'They are meditating together peacefully.',
            
            # === ANIMALS & PETS ===
            'with_dog': 'The couple is with their pet dog.',
            'with_cat': 'They are with their pet cat.',
            'with_horse': 'They are with a horse, or horseback riding.',
            'feeding_ducks': 'They are feeding ducks or birds together.',
            'at_petting_zoo': 'They are at a petting zoo with animals.',
            'at_aquarium': 'They are at an aquarium viewing the tanks.',
            
            # === SEASONAL ACTIVITIES ===
            'pumpkin_patch': 'The couple is at a pumpkin patch picking pumpkins.',
            'apple_picking': 'They are picking apples at an orchard.',
            'christmas_tree_lot': 'They are shopping for a Christmas tree.',
            'decorating_tree': 'They are decorating a Christmas tree together.',
            'building_snowman': 'They are building a snowman together.',
            'snowball_fight': 'They are having a snowball fight.',
            'fall_leaves': 'They are playing in fall leaves.',
            'spring_flowers': 'They are picking spring flowers together.',
            
            # === TRAVEL & ADVENTURE ===
            'at_airport': 'The couple is at the airport, traveling together.',
            'road_trip_car': 'They are on a road trip in a car.',
            'on_boat': 'They are on a boat or sailing together.',
            'hot_air_balloon': 'They are on a hot air balloon ride.',
            'helicopter_ride': 'They are on a helicopter ride with scenic views.',
            'train_ride': 'They are on a scenic train ride together.',
            'at_landmark': 'They are at a famous landmark.',
            'camping_tent': 'They are camping by a tent.',
            'bonfire_campfire': 'They are sitting by a bonfire or campfire.',
            'fishing_together': 'They are fishing together.',
            
            # === UNIQUE & SPECIAL ===
            'at_concert': 'The couple is at a concert or music festival.',
            'at_sports_game': 'They are at a sports game in a stadium.',
            'carnival_rides': 'They are on carnival rides together.',
            'roller_coaster': 'They are on a roller coaster together.',
            'ferris_wheel': 'They are on a ferris wheel.',
            'go_kart_racing': 'They are go-kart racing together.',
            'arcade_games': 'They are playing arcade games.',
            'bowling_alley': 'They are bowling together.',
            'mini_golf': 'They are playing mini golf.',
            'laser_tag': 'They are playing laser tag together.',
            'escape_room': 'They are doing an escape room challenge.',
            'scuba_diving': 'They are scuba diving together.',
            'snorkeling': 'They are snorkeling together.',
            'zip_lining': 'They are zip lining together.',
            'bungee_jumping': 'They are bungee jumping together.',
            'skydiving': 'They are skydiving together.',
            
            # === FORMAL POSES ===
            'formal_portrait': 'The couple is posed formally in a traditional portrait.',
            'formal_standing': 'They are in a formal standing pose.',
            'formal_sitting': 'They are in a formal sitting pose.',
        }
        return activities.get(activity, 'The couple is posed beautifully together.')
    
    # === WEDDING MOMENT DESCRIPTIONS (100+ Moments) ===
    @classmethod
    def _get_wedding_moment_description(cls, moment):
        """Get wedding moment/scene description"""
        moments = {
            # === CEREMONY MOMENTS ===
            'walking_aisle': 'Capture the moment of walking down the aisle.',
            'first_look': 'Capture the emotional first look reveal moment.',
            'exchanging_vows': 'Capture the intimate moment of exchanging wedding vows.',
            'exchanging_rings': 'Capture the moment of exchanging wedding rings.',
            'the_kiss': 'Capture the first kiss as a married couple.',
            'just_married': 'Capture the just married moment, walking down the aisle as newlyweds.',
            'unity_ceremony': 'Capture the unity ceremony with candle or sand.',
            'signing_certificate': 'Capture the moment of signing the marriage certificate.',
            'with_officiant': 'Capture the couple with their wedding officiant.',
            
            # === RECEPTION MOMENTS ===
            'grand_entrance': 'Capture the grand entrance as they are announced.',
            'first_dance': 'Capture the romantic first dance.',
            'father_daughter_dance': 'Capture the emotional father-daughter dance.',
            'mother_son_dance': 'Capture the touching mother-son dance.',
            'cake_cutting': 'Capture the moment of cutting the wedding cake.',
            'cake_feeding': 'Capture them feeding each other wedding cake.',
            'toasts_speeches': 'Capture the moment during toasts and speeches.',
            'bouquet_toss': 'Capture the bouquet toss moment.',
            'garter_toss': 'Capture the garter toss moment.',
            'last_dance': 'Capture the last dance of the evening.',
            'send_off': 'Capture the send off or exit.',
            
            # === COUPLE PORTRAITS ===
            'formal_portrait': 'Create a formal traditional wedding portrait.',
            'romantic_embrace': 'Capture a romantic embrace, holding each other close.',
            'forehead_kiss': 'Capture a tender forehead kiss moment.',
            'the_dip_kiss': 'Capture a dramatic dip kiss.',
            'holding_hands': 'Capture them holding hands while walking.',
            'looking_at_each_other': 'Capture them gazing lovingly at each other.',
            'laughing_together': 'Capture them laughing together with joy.',
            'private_moment': 'Capture a quiet private intimate moment.',
            'silhouette_sunset': 'Capture their silhouette at sunset.',
            'dramatic_lighting': 'Create a dramatic portrait with striking lighting.',
            'walking_together': 'Capture them walking together as newlyweds.',
            'dancing_alone': 'Capture them dancing alone together.',
            
            # === GETTING READY ===
            'bride_getting_ready': 'Capture the bride getting ready and preparing.',
            'groom_getting_ready': 'Capture the groom getting ready and preparing.',
            'dress_detail': 'Capture beautiful wedding dress details.',
            'putting_on_dress': 'Capture the moment of putting on the wedding dress.',
            'veil_placement': 'Capture the veil being placed or adjusted.',
            'tying_tie': 'Capture the groom tying his tie or bowtie.',
            'putting_on_shoes': 'Capture putting on wedding shoes.',
            'perfume_cologne': 'Capture applying perfume or cologne.',
            'hair_makeup': 'Capture the hair and makeup preparation.',
            'looking_in_mirror': 'Capture looking in the mirror, final preparations.',
            'with_wedding_party_prep': 'Capture getting ready with the wedding party.',
            
            # === BRIDAL PARTY ===
            'full_bridal_party': 'Capture the full bridal party group photo.',
            'bridesmaids_group': 'Capture the bridesmaids group together.',
            'groomsmen_group': 'Capture the groomsmen group together.',
            'bride_with_bridesmaids': 'Capture the bride with her bridesmaids.',
            'groom_with_groomsmen': 'Capture the groom with his groomsmen.',
            'flower_girl': 'Capture the sweet flower girl or ring bearer.',
            'bridal_party_fun': 'Capture the bridal party having fun together.',
            'bridesmaids_helping': 'Capture bridesmaids helping the bride.',
            'groomsmen_fun': 'Capture candid fun moments with groomsmen.',
            
            # === FAMILY MOMENTS ===
            'with_parents': 'Capture the couple with both sets of parents.',
            'bride_with_dad': 'Capture the bride with her father.',
            'bride_with_mom': 'Capture the bride with her mother.',
            'groom_with_dad': 'Capture the groom with his father.',
            'groom_with_mom': 'Capture the groom with his mother.',
            'with_grandparents': 'Capture the couple with grandparents.',
            'with_siblings': 'Capture the couple with their siblings.',
            'family_group': 'Capture a family group photo.',
            'three_generations': 'Capture three generations together.',
            
            # === DETAIL SHOTS ===
            'rings_detail': 'Capture beautiful wedding ring details.',
            'bouquet_detail': 'Capture the bridal bouquet in detail.',
            'dress_hanging': 'Capture the wedding dress hanging beautifully.',
            'shoes_accessories': 'Capture shoes and accessories in detail.',
            'invitation_suite': 'Capture the invitation suite and stationery.',
            'corsage_boutonniere': 'Capture corsage and boutonniere details.',
            'jewelry_details': 'Capture jewelry and accessory details.',
            
            # === CREATIVE & ARTISTIC ===
            'veil_wind': 'Capture the veil blowing dramatically in the wind.',
            'dress_twirl': 'Capture the wedding dress twirling or spinning.',
            'through_veil': 'Capture the couple through the wedding veil.',
            'reflection_shot': 'Capture an artistic reflection in mirror or water.',
            'from_above': 'Capture from above in a bird\'s eye or drone view.',
            'from_behind': 'Capture from behind looking over their shoulders.',
            'artistic_blur': 'Create artistic blur or motion effects.',
            'double_exposure': 'Create a double exposure artistic portrait.',
            
            # === VENUE & ATMOSPHERE ===
            'venue_exterior': 'Capture the wedding venue exterior and arrival.',
            'venue_interior': 'Capture the beautifully decorated venue interior.',
            'ceremony_setup': 'Capture the ceremony setup before guests arrive.',
            'reception_setup': 'Capture the elegant reception setup and tablescape.',
            'guest_candids': 'Capture candid moments of guests mingling.',
            'dancing_guests': 'Capture guests dancing and celebrating.',
            'cocktail_hour': 'Capture the cocktail hour socializing.',
            
            # === SPECIAL MOMENTS ===
            'sparkler_exit': 'Capture the dramatic sparkler exit send off.',
            'confetti_toss': 'Capture confetti being tossed in celebration.',
            'champagne_toast': 'Capture a champagne toast moment.',
            'champagne_pop': 'Capture champagne being popped and sprayed.',
            'signing_guest_book': 'Capture signing the guest book.',
            'reading_cards': 'Capture reading cards or notes.',
            'emotional_moment': 'Capture an emotional moment with tears of joy.',
            'surprise_moment': 'Capture a surprise moment during the celebration.',
            
            # === CULTURAL & TRADITIONAL ===
            'cultural_ceremony': 'Capture a cultural ceremony or ritual.',
            'traditional_dance': 'Capture a traditional cultural dance.',
            'blessing_ceremony': 'Capture a blessing ceremony.',
            'tea_ceremony': 'Capture a traditional tea ceremony.',
            'handfasting': 'Capture a handfasting ceremony.',
            'breaking_glass': 'Capture breaking glass or other tradition.',
            
            # === SOLO SHOTS ===
            'bride_solo_portrait': 'Create a beautiful solo portrait of the bride.',
            'groom_solo_portrait': 'Create a handsome solo portrait of the groom.',
            'bride_with_bouquet': 'Capture the bride with her beautiful bouquet.',
            'groom_in_venue': 'Capture the groom in the wedding venue.',
        }
        return moments.get(moment, '')
    
    # === SETTING DESCRIPTIONS ===
    @classmethod
    def _get_setting_description(cls, setting, mode, season=None):
        """Get engagement setting description"""
        if setting == 'na':
            return ''
        
        settings = {
            # Natural Outdoor Settings
            'garden_park': 'in a beautiful garden or park',
            'beach_waterfront': 'at the beach or waterfront',
            'mountain_vista': 'at a mountain or scenic vista',
            'forest_woods': 'in a forest or wooded area',
            'countryside_rural': 'in the countryside or rural setting',
            'lake_river': 'by a lake or river',
            'desert_landscape': 'in a desert landscape',
            'meadow_field': 'in a meadow or open field',
            
            # Urban & City Settings
            'urban_city': 'in urban city streets',
            'downtown_skyline': 'downtown with skyline views',
            'historic_district': 'in a historic district',
            'alleyway_brick': 'in an alleyway with brick walls',
            'rooftop_terrace': 'on a rooftop or terrace',
            'bridge_overpass': 'on a bridge or overpass',
            'subway_station': 'in a subway or train station',
            'industrial_district': 'in an industrial district',
            
            # Indoor & Cozy Settings
            'home_living_room': 'in a home living room',
            'home_kitchen': 'in a home kitchen',
            'bedroom_cozy': 'in a cozy bedroom',
            'coffee_shop': 'in a coffee shop or café',
            'bookstore_library': 'in a bookstore or library',
            'art_gallery': 'in an art gallery or museum',
            'studio_indoor': 'in a studio or indoor space',
            'restaurant_bar': 'in a restaurant or bar',
            'hotel_lobby': 'in a hotel lobby',
            
            # Special & Unique Settings
            'amusement_park': 'at an amusement park',
            'carnival_fair': 'at a carnival or fair',
            'farmers_market': 'at a farmers market',
            'vineyard_winery': 'at a vineyard or winery',
            'botanical_garden': 'in a botanical garden',
            'zoo_aquarium': 'at a zoo or aquarium',
            'sports_venue': 'at a sports venue or stadium',
            'theater_concert_hall': 'in a theater or concert hall',
            'historic_building': 'at a historic building or landmark',
            
            # Adventure & Travel Settings
            'airport_terminal': 'at an airport terminal',
            'train_platform': 'on a train platform',
            'road_trip': 'on a road trip or highway',
            'camping_site': 'at a camping site',
            'ski_resort': 'at a ski resort on the slopes',
            'tropical_resort': 'at a tropical resort',
        }
        
        setting_desc = f"The photo is set {settings.get(setting, 'in a beautiful location')}"
        
        # Add seasonal context if provided
        if season and season != 'na':
            seasonal = {
                'spring': ' with spring flowers and fresh greenery',
                'summer': ' with bright summer sunshine and lush vegetation',
                'fall': ' with colorful autumn foliage and golden light',
                'winter': ' with winter atmosphere and seasonal charm',
            }
            setting_desc += seasonal.get(season, '')
        
        return setting_desc + '.'
    
    @classmethod
    def _get_wedding_setting_description(cls, setting, season=None):
        """Get wedding setting description"""
        if setting == 'na':
            return ''
        
        settings = {
            # Ceremony & Reception Venues
            'ceremony_site': 'at the wedding ceremony site with the altar',
            'reception_venue': 'in the elegant reception venue',
            'dance_floor': 'on the dance floor',
            'sweetheart_table': 'at the sweetheart table',
            'guest_tables': 'among the beautifully decorated guest tables',
            'cocktail_area': 'in the cocktail hour area',
            'entrance_lobby': 'at the entrance or lobby',
            
            # Indoor Locations
            'church_chapel': 'in a church or chapel',
            'ballroom': 'in a grand ballroom',
            'barn_rustic': 'in a rustic barn venue',
            'hotel_interior': 'in a hotel interior',
            'mansion_estate': 'at a mansion or estate',
            'loft_industrial': 'in an industrial loft space',
            'museum_gallery': 'in a museum or gallery',
            'restaurant_private': 'in a private restaurant room',
            
            # Outdoor Locations
            'garden_venue': 'in a beautiful garden venue',
            'park_outdoor': 'in an outdoor park',
            'beach_waterfront': 'at the beach or waterfront',
            'vineyard_winery': 'at a vineyard or winery',
            'countryside_rural': 'in the countryside',
            'mountain_scenic': 'at a mountain with scenic views',
            'forest_woods': 'in a forest or wooded area',
            'rooftop_terrace': 'on a rooftop or terrace',
            'courtyard_patio': 'in a courtyard or patio',
            
            # Getting Ready Locations
            'bridal_suite': 'in the bridal suite',
            'groom_suite': 'in the groom\'s suite',
            'hotel_room': 'in a hotel room',
            'home_residence': 'at home or a private residence',
            
            # Unique Venues
            'historic_building': 'at a historic building or landmark',
            'castle_palace': 'at a castle or palace',
            'yacht_boat': 'on a yacht or boat',
            'tent_pavilion': 'in an elegant tent or pavilion',
            'greenhouse': 'in a greenhouse or conservatory',
        }
        
        setting_desc = f"The scene takes place {settings.get(setting, 'at the beautiful venue')}"
        
        # Add seasonal context if provided
        if season and season != 'na':
            seasonal = {
                'spring': ' with spring blooms and fresh atmosphere',
                'summer': ' with bright summer ambiance',
                'fall': ' with autumn colors and warm atmosphere',
                'winter': ' with elegant winter styling',
            }
            setting_desc += seasonal.get(season, '')
        
        return setting_desc + '.'
    
    # === ATTIRE DESCRIPTIONS ===
    @classmethod
    def _get_attire_description(cls, attire, mode):
        """Get clothing description"""
        if attire == 'na':
            return ''
        
        if mode == 'wedding':
            attires = {
                'traditional_formal': 'The bride wears an elegant white wedding gown with veil, the groom wears a classic tuxedo.',
                'modern_chic_wedding': 'They wear modern, contemporary wedding attire with designer styling.',
                'casual_elegant_wedding': 'They wear casually elegant wedding attire.',
                'bohemian_wedding': 'They wear bohemian-style wedding attire with flowing fabrics.',
                'vintage_wedding': 'They wear vintage-inspired wedding attire.',
                'cultural_traditional': 'They wear traditional cultural wedding attire.',
            }
        else:  # Engagement
            attires = {
                'formal_elegant': 'They wear formal elegant outfits.',
                'modern_chic': 'They wear modern, chic, and fashionable outfits.',
                'casual_elegant': 'They wear casual but elegant clothing.',
                'cozy_casual': 'They wear cozy casual clothing like sweaters.',
                'bohemian': 'They wear bohemian-style clothing.',
                'vintage_inspired': 'They wear vintage-inspired outfits.',
                'sporty_athletic': 'They wear sporty athletic wear.',
                'business_casual': 'They wear business casual attire.',
                'seasonal_appropriate': 'They wear seasonally appropriate clothing.',
            }
        
        return attires.get(attire, '')
    
    # === LIGHTING DESCRIPTIONS ===
    @classmethod
    def _get_lighting_description(cls, lighting):
        """Get lighting atmosphere"""
        if lighting == 'na':
            return ''
        
        lights = {
            'romantic': 'Illuminate with romantic warm lighting for soft dreamy glow.',
            'bright': 'Use bright cheerful lighting for sharp energetic atmosphere.',
            'dim': 'Use dim intimate lighting for cozy moody atmosphere.',
            'dramatic': 'Use dramatic lighting with bold contrasts.',
            'natural': 'Use soft natural daylight for organic look.',
            'golden': 'Bathe in golden hour warm honeyed glow.',
            'dusk': 'Enhance with soft dusk twilight tones.',
            'dawn': 'Illuminate with fresh dawn morning light.',
        }
        return lights.get(lighting, '')
    
    # === COLOR DESCRIPTIONS ===
    @classmethod
    def _get_color_description(cls, color_scheme):
        """Get color palette application"""
        if color_scheme == 'na':
            return ''
        
        colors = {
            'vibrant_bold': 'Use vibrant bold colors with high saturation.',
            'muted_soft': 'Use light airy soft muted tones.',
            'earth_tones': 'Use natural earth tones.',
            'jewel_tones': 'Use rich jewel tone colors.',
            'monochrome': 'Use monochrome black and white.',
            'warm_tones': 'Emphasize warm tones with reds, oranges, yellows.',
            'cool_tones': 'Emphasize cool tones with blues, greens, purples.',
        }
        return colors.get(color_scheme, '')
    
    # === SEASONAL ATMOSPHERE (FOR PORTRAITS) ===
    @classmethod
    def _get_seasonal_atmosphere(cls, season):
        """Get seasonal atmosphere for portrait modes (independent of setting)"""
        if season == 'na':
            return ''
        
        seasons = {
            'spring': 'Capture the fresh essence of spring with blooming flowers and renewed growth.',
            'summer': 'Embrace bright summer sunshine with lush greenery and warm golden light.',
            'fall': 'Feature autumn colors with golden foliage and warm harvest tones.',
            'winter': 'Showcase elegant winter atmosphere with crisp air and seasonal beauty.',
        }
        return seasons.get(season, '')