# image_processing/prompt_generator.py - Comprehensive 50+ Wedding Theme Prompts
"""
Advanced prompt generation system for realistic wedding venue transformations
Optimized for Stability AI SD3 Turbo with 50+ beautiful wedding themes
"""

class WeddingPromptGenerator:
    """Generate comprehensive, specific prompts for dramatic wedding venue transformations"""
    
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
        'scandinavian_simple': {
            'description': 'clean Scandinavian wedding with minimal furniture, white wood elements, simple flowers, hygge details, Nordic style',
            'lighting': 'Scandinavian lighting, natural glow, hygge ambiance, Nordic illumination',
            'colors': 'Nordic white, Scandinavian grey, hygge cream, simple green, minimal blue',
            'atmosphere': 'clean Scandinavian celebration with hygge comfort',
            'specific_elements': 'minimal ceremony arch, white wood furniture, simple arrangements, hygge details, Nordic decorations'
        },
        'modern_monochrome': {
            'description': 'striking modern monochrome wedding with black and white elements, geometric shapes, minimal furniture, contrast details',
            'lighting': 'monochrome lighting, contrast shadows, modern glow, geometric ambiance',
            'colors': 'pure white, deep black, grey gradients, minimal silver, contrast elements',
            'atmosphere': 'striking monochrome celebration with modern contrast',
            'specific_elements': 'geometric ceremony backdrop, monochrome furniture, contrast details, minimal decorations, modern elements'
        },
        'concrete_jungle': {
            'description': 'urban concrete jungle wedding with raw concrete, industrial plants, urban furniture, jungle plants, city wild theme',
            'lighting': 'concrete lighting, urban jungle glow, industrial ambiance, wild city illumination',
            'colors': 'concrete grey, jungle green, urban brown, industrial black, wild earth',
            'atmosphere': 'urban jungle celebration with concrete character',
            'specific_elements': 'concrete ceremony backdrop, industrial plants, urban furniture, jungle elements, city wild decorations'
        },
        'glass_house': {
            'description': 'transparent glass house wedding with glass elements, modern transparency, clean lines, light refraction, architectural details',
            'lighting': 'glass house lighting, transparent glow, light refraction, architectural illumination',
            'colors': 'glass clear, transparent white, light silver, clean blue, architectural grey',
            'atmosphere': 'transparent glass celebration with architectural beauty',
            'specific_elements': 'glass ceremony structure, transparent details, light elements, architectural features, modern glass decorations'
        },

        # Fantasy & Themed Celebrations
        'enchanted_forest_fairy': {
            'description': 'magical enchanted fairy wedding with fairy lights, mushroom seating, woodland creatures, fairy wings, enchanted details',
            'lighting': 'fairy lighting, enchanted glow, magical sparkles, woodland ambiance',
            'colors': 'fairy pink, enchanted green, magical gold, woodland brown, sparkle silver',
            'atmosphere': 'magical fairy celebration with enchanted wonder',
            'specific_elements': 'fairy light ceremony arch, mushroom seating, woodland decorations, fairy details, enchanted elements'
        },
        'princess_castle': {
            'description': 'royal princess castle wedding with castle towers, princess decorations, royal throne seating, crown details, fairytale elements',
            'lighting': 'castle lighting, royal glow, princess ambiance, fairytale illumination',
            'colors': 'princess pink, royal purple, castle gold, fairytale white, crown jewels',
            'atmosphere': 'royal princess celebration with castle magic',
            'specific_elements': 'castle ceremony backdrop, royal throne seating, princess decorations, crown details, fairytale elements'
        },
        'mermaid_lagoon': {
            'description': 'underwater mermaid wedding with seashell decorations, ocean plants, mermaid tail elements, underwater theme, lagoon details',
            'lighting': 'underwater lighting, lagoon glow, ocean ambiance, mermaid illumination',
            'colors': 'mermaid teal, ocean blue, seashell pearl, lagoon green, underwater silver',
            'atmosphere': 'underwater mermaid celebration with lagoon magic',
            'specific_elements': 'seashell ceremony arch, ocean plant decorations, mermaid details, underwater elements, lagoon features'
        },
        'dragon_castle': {
            'description': 'medieval dragon castle wedding with dragon decorations, castle stones, medieval banners, knight elements, fantasy details',
            'lighting': 'castle lighting, dragon fire glow, medieval torches, fantasy ambiance',
            'colors': 'dragon red, castle stone grey, medieval gold, knight silver, fantasy purple',
            'atmosphere': 'medieval dragon celebration with castle power',
            'specific_elements': 'dragon ceremony backdrop, castle stone details, medieval banners, knight decorations, fantasy elements'
        },
        'unicorn_dreams': {
            'description': 'dreamy unicorn wedding with rainbow colors, unicorn horn details, magical flowers, dream elements, fantasy sparkles',
            'lighting': 'unicorn lighting, rainbow glow, magical sparkles, dream ambiance',
            'colors': 'unicorn white, rainbow pastels, magical pink, dream purple, sparkle gold',
            'atmosphere': 'dreamy unicorn celebration with magical wonder',
            'specific_elements': 'unicorn ceremony arch, rainbow decorations, magical flowers, dream details, fantasy sparkles'
        },
        'hollywood_glam': {
            'description': 'glamorous Hollywood wedding with red carpet, movie star elements, golden statues, spotlight details, celebrity theme',
            'lighting': 'Hollywood lighting, spotlight glow, red carpet ambiance, celebrity illumination',
            'colors': 'Hollywood gold, red carpet red, movie star black, spotlight white, celebrity silver',
            'atmosphere': 'glamorous Hollywood celebration with movie star luxury',
            'specific_elements': 'red carpet ceremony aisle, golden statue decorations, spotlight details, movie star elements, celebrity features'
        },
        'broadway_musical': {
            'description': 'theatrical Broadway wedding with stage elements, musical decorations, theater seating, spotlight areas, show tune theme',
            'lighting': 'Broadway lighting, stage spots, theater glow, musical ambiance',
            'colors': 'Broadway gold, theater red, stage black, spotlight white, musical purple',
            'atmosphere': 'theatrical Broadway celebration with musical energy',
            'specific_elements': 'stage ceremony backdrop, theater seating, musical decorations, spotlight details, Broadway elements'
        },
        'vintage_circus': {
            'description': 'whimsical vintage circus wedding with carnival decorations, circus tents, popcorn details, carnival games, vintage circus elements',
            'lighting': 'circus lighting, carnival glow, vintage ambiance, whimsical illumination',
            'colors': 'circus red, carnival yellow, vintage blue, popcorn white, carnival stripes',
            'atmosphere': 'whimsical circus celebration with carnival joy',
            'specific_elements': 'circus tent ceremony structure, carnival decorations, vintage circus details, popcorn elements, whimsical features'
        },
        'comic_book': {
            'description': 'superhero comic book wedding with comic elements, superhero decorations, pop art details, comic speech bubbles, hero theme',
            'lighting': 'comic book lighting, pop art glow, superhero ambiance, hero illumination',
            'colors': 'comic primary colors, superhero red, pop art blue, hero yellow, comic black',
            'atmosphere': 'superhero comic celebration with pop art energy',
            'specific_elements': 'comic book ceremony backdrop, superhero decorations, pop art details, speech bubble elements, hero features'
        },

        # Classic Popular Themes (enhanced versions)
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

        # Holiday & Celebration Themes (adding the remaining ones)
        'christmas_magic': {
            'description': 'magical Christmas wedding with evergreen decorations, red ribbon details, Christmas lights, ornament centerpieces, holiday elements',
            'lighting': 'Christmas lights, warm holiday glow, ornament reflections, festive ambiance',
            'colors': 'Christmas red, evergreen, holiday gold, snow white, ornament silver',
            'atmosphere': 'magical Christmas celebration with holiday joy',
            'specific_elements': 'evergreen ceremony arch, Christmas ornaments, holiday ribbons, festive lights, Christmas decorations'
        },
        'halloween_gothic': {
            'description': 'gothic Halloween wedding with dark decorations, pumpkin elements, autumn leaves, spooky details, gothic elegance',
            'lighting': 'gothic lighting, candle glow, mysterious shadows, Halloween ambiance',
            'colors': 'Halloween orange, gothic black, autumn gold, spooky purple, dark red',
            'atmosphere': 'gothic Halloween celebration with mysterious elegance',
            'specific_elements': 'gothic ceremony backdrop, pumpkin decorations, autumn elements, spooky details, dark elegance'
        },
        'valentine_romance': {
            'description': 'romantic Valentine wedding with heart decorations, rose petals, romantic red elements, love details, cupid theme',
            'lighting': 'romantic lighting, soft rose glow, love ambiance, Valentine illumination',
            'colors': 'Valentine red, romantic pink, love white, heart gold, cupid silver',
            'atmosphere': 'romantic Valentine celebration with love magic',
            'specific_elements': 'heart ceremony arch, rose petal decorations, romantic details, love elements, Valentine features'
        },
        'new_year_eve': {
            'description': 'glamorous New Year\'s Eve wedding with countdown elements, champagne details, midnight theme, celebration decorations, party elements',
            'lighting': 'New Year lighting, midnight glow, celebration sparkles, party ambiance',
            'colors': 'midnight black, champagne gold, celebration silver, party white, countdown colors',
            'atmosphere': 'glamorous New Year celebration with midnight magic',
            'specific_elements': 'countdown ceremony backdrop, champagne details, midnight decorations, celebration elements, party features'
        },
        'fourth_july': {
            'description': 'patriotic Fourth of July wedding with American flag elements, red white blue decorations, firework details, patriotic theme',
            'lighting': 'patriotic lighting, firework sparkles, American glow, Fourth of July ambiance',
            'colors': 'patriotic red, freedom white, liberty blue, American flag colors, firework gold',
            'atmosphere': 'patriotic Fourth of July celebration with American pride',
            'specific_elements': 'American flag ceremony backdrop, patriotic decorations, firework details, red white blue elements, liberty features'
        },
        'dia_muertos': {
            'description': 'colorful Día de los Muertos wedding with sugar skull decorations, marigold flowers, papel picado, Mexican celebration theme',
            'lighting': 'Día de los Muertos lighting, marigold glow, celebration ambiance, Mexican illumination',
            'colors': 'marigold orange, celebration purple, skull white, Mexican pink, fiesta colors',
            'atmosphere': 'colorful Día de los Muertos celebration with Mexican joy',
            'specific_elements': 'sugar skull ceremony decorations, marigold arrangements, papel picado, Mexican details, celebration elements'
        },
        'chinese_new_year': {
            'description': 'festive Chinese New Year wedding with dragon decorations, red lanterns, lucky elements, prosperity theme, zodiac details',
            'lighting': 'Chinese New Year lighting, red lantern glow, lucky ambiance, prosperity illumination',
            'colors': 'lucky red, prosperity gold, dragon colors, lantern orange, zodiac elements',
            'atmosphere': 'festive Chinese New Year celebration with lucky prosperity',
            'specific_elements': 'dragon ceremony backdrop, red lantern decorations, lucky elements, prosperity details, zodiac features'
        },
        'oktoberfest': {
            'description': 'traditional Oktoberfest wedding with beer hall decorations, pretzel details, German elements, lederhosen theme, festival atmosphere',
            'lighting': 'Oktoberfest lighting, beer hall glow, festival ambiance, German illumination',
            'colors': 'Oktoberfest brown, beer gold, pretzel tan, German green, festival colors',
            'atmosphere': 'traditional Oktoberfest celebration with German festival joy',
            'specific_elements': 'beer hall ceremony setup, pretzel decorations, German details, lederhosen elements, festival features'
        },
        'mardi_gras': {
            'description': 'festive Mardi Gras wedding with mask decorations, purple gold green colors, bead details, New Orleans theme, carnival atmosphere',
            'lighting': 'Mardi Gras lighting, carnival glow, New Orleans ambiance, festive illumination',
            'colors': 'Mardi Gras purple, carnival gold, celebration green, mask colors, bead elements',
            'atmosphere': 'festive Mardi Gras celebration with New Orleans carnival energy',
            'specific_elements': 'mask ceremony decorations, bead details, Mardi Gras colors, carnival elements, New Orleans features'
        },

        # Unique & Creative Themes (adding remaining ones)
        'book_lovers': {
            'description': 'literary book lovers wedding with book decorations, library elements, vintage books, reading nooks, literary theme',
            'lighting': 'library lighting, reading lamp glow, book ambiance, literary illumination',
            'colors': 'book brown, library green, vintage cream, literary gold, reading lamp warm',
            'atmosphere': 'intellectual book lovers celebration with literary charm',
            'specific_elements': 'book ceremony backdrop, library decorations, vintage book details, reading elements, literary features'
        },
        'music_festival': {
            'description': 'energetic music festival wedding with stage elements, band setup, festival decorations, music notes, concert theme',
            'lighting': 'festival lighting, stage spots, concert glow, music ambiance',
            'colors': 'festival bright colors, stage black, music gold, concert silver, band elements',
            'atmosphere': 'energetic music festival celebration with concert energy',
            'specific_elements': 'stage ceremony setup, band decorations, festival details, music elements, concert features'
        },
        'travel_adventure': {
            'description': 'adventurous travel wedding with map decorations, luggage elements, passport details, world theme, journey atmosphere',
            'lighting': 'travel lighting, adventure glow, journey ambiance, world illumination',
            'colors': 'map brown, luggage tan, passport blue, world green, journey gold',
            'atmosphere': 'adventurous travel celebration with world exploration spirit',
            'specific_elements': 'map ceremony backdrop, luggage decorations, passport details, world elements, journey features'
        },
        'wine_country': {
            'description': 'elegant wine country wedding with vineyard decorations, wine barrel elements, grape details, winery theme, sommelier atmosphere',
            'lighting': 'wine country lighting, vineyard glow, winery ambiance, sommelier illumination',
            'colors': 'wine burgundy, vineyard green, grape purple, barrel brown, sommelier gold',
            'atmosphere': 'elegant wine country celebration with vineyard sophistication',
            'specific_elements': 'vineyard ceremony arch, wine barrel decorations, grape details, winery elements, sommelier features'
        },
        'coffee_house': {
            'description': 'cozy coffee house wedding with coffee bean decorations, café elements, espresso details, barista theme, coffeehouse atmosphere',
            'lighting': 'coffee house lighting, café glow, espresso ambiance, barista illumination',
            'colors': 'coffee brown, café cream, espresso black, barista white, bean tan',
            'atmosphere': 'cozy coffee house celebration with café warmth',
            'specific_elements': 'coffee bean ceremony decorations, café details, espresso elements, barista features, coffeehouse setup'
        },
        'neon_cyberpunk': {
            'description': 'futuristic neon cyberpunk wedding with LED decorations, cyber elements, tech details, futuristic theme, digital atmosphere',
            'lighting': 'neon lighting, cyber glow, LED ambiance, futuristic illumination',
            'colors': 'neon pink, cyber blue, tech green, futuristic silver, digital purple',
            'atmosphere': 'futuristic cyberpunk celebration with neon energy',
            'specific_elements': 'LED ceremony backdrop, cyber decorations, tech details, futuristic elements, digital features'
        },
        'steampunk_victorian': {
            'description': 'vintage steampunk wedding with gear decorations, Victorian elements, brass details, mechanical theme, industrial Victorian atmosphere',
            'lighting': 'steampunk lighting, gear glow, Victorian ambiance, mechanical illumination',
            'colors': 'steampunk brass, Victorian brown, gear copper, mechanical silver, industrial gold',
            'atmosphere': 'vintage steampunk celebration with Victorian industrial charm',
            'specific_elements': 'gear ceremony decorations, Victorian details, brass elements, mechanical features, steampunk setup'
        },
        'space_galaxy': {
            'description': 'cosmic space galaxy wedding with star decorations, planet elements, cosmic details, astronaut theme, galaxy atmosphere',
            'lighting': 'space lighting, galaxy glow, cosmic ambiance, star illumination',
            'colors': 'space black, galaxy purple, star silver, planet blue, cosmic gold',
            'atmosphere': 'cosmic space celebration with galaxy wonder',
            'specific_elements': 'star ceremony backdrop, planet decorations, cosmic details, astronaut elements, galaxy features'
        },
        'under_the_sea': {
            'description': 'underwater sea wedding with ocean decorations, fish elements, coral details, submarine theme, deep sea atmosphere',
            'lighting': 'underwater lighting, ocean glow, sea ambiance, deep sea illumination',
            'colors': 'ocean blue, sea green, coral pink, fish silver, submarine yellow',
            'atmosphere': 'underwater sea celebration with ocean mystery',
            'specific_elements': 'ocean ceremony backdrop, fish decorations, coral details, submarine elements, sea features'
        },
        'secret_garden': {
            'description': 'mysterious secret garden wedding with hidden pathways, secret doors, garden mysteries, enchanted plants, magical garden atmosphere',
            'lighting': 'secret garden lighting, mysterious glow, hidden ambiance, magical illumination',
            'colors': 'secret green, garden brown, mystery purple, enchanted gold, magical silver',
            'atmosphere': 'mysterious secret garden celebration with enchanted wonder',
            'specific_elements': 'secret door ceremony entrance, hidden pathway decorations, mystery elements, enchanted details, magical features'
        },

        # Adding vintage decades
        '1950s_diner': {
            'description': '1950s diner wedding with retro booths, jukebox elements, checkered floors, vintage diner decorations, classic Americana theme',
            'lighting': '1950s diner lighting, jukebox glow, retro ambiance, vintage illumination',
            'colors': 'diner red, retro white, jukebox chrome, vintage blue, checkered black',
            'atmosphere': 'nostalgic 1950s celebration with diner charm',
            'specific_elements': 'retro booth ceremony seating, jukebox decorations, checkered details, vintage diner elements, Americana features'
        },
        '1960s_mod': {
            'description': '1960s mod wedding with geometric patterns, mod furniture, go-go decorations, psychedelic elements, swinging sixties theme',
            'lighting': '1960s mod lighting, psychedelic glow, geometric ambiance, mod illumination',
            'colors': 'mod orange, psychedelic pink, geometric yellow, swinging green, sixties purple',
            'atmosphere': 'groovy 1960s celebration with mod style',
            'specific_elements': 'geometric ceremony backdrop, mod furniture, psychedelic decorations, go-go elements, sixties features'
        },
        '1970s_disco': {
            'description': '1970s disco wedding with mirror balls, dance floor lights, disco decorations, groovy elements, Saturday Night Fever theme',
            'lighting': 'disco lighting, mirror ball reflections, dance floor glow, groovy ambiance',
            'colors': 'disco gold, groovy orange, dance floor silver, mirror chrome, seventies brown',
            'atmosphere': 'groovy 1970s celebration with disco fever',
            'specific_elements': 'mirror ball ceremony centerpiece, disco dance floor, groovy decorations, Saturday Night Fever elements, seventies features'
        },
        '1980s_neon': {
            'description': '1980s neon wedding with bright neon colors, synthesizer elements, new wave decorations, geometric shapes, eighties theme',
            'lighting': '1980s neon lighting, synthesizer glow, new wave ambiance, geometric illumination',
            'colors': 'neon pink, electric blue, synthesizer purple, new wave green, eighties orange',
            'atmosphere': 'electric 1980s celebration with neon energy',
            'specific_elements': 'neon ceremony backdrop, synthesizer decorations, new wave details, geometric elements, eighties features'
        },
        '1990s_grunge': {
            'description': '1990s grunge wedding with flannel decorations, alternative elements, Seattle theme, indie details, grunge atmosphere',
            'lighting': '1990s grunge lighting, alternative glow, Seattle ambiance, indie illumination',
            'colors': 'grunge brown, flannel red, alternative black, Seattle green, indie blue',
            'atmosphere': 'alternative 1990s celebration with grunge authenticity',
            'specific_elements': 'flannel ceremony decorations, alternative details, Seattle elements, indie features, grunge setup'
        },
        'victorian_romance': {
            'description': 'elegant Victorian romance wedding with ornate furniture, lace details, romantic Victorian elements, period decorations, vintage elegance',
            'lighting': 'Victorian lighting, romantic glow, period ambiance, elegant illumination',
            'colors': 'Victorian burgundy, romantic cream, lace white, period gold, elegant rose',
            'atmosphere': 'romantic Victorian celebration with period elegance',
            'specific_elements': 'ornate Victorian ceremony furniture, lace decorations, period details, romantic elements, elegant features'
        },
        'art_nouveau': {
            'description': 'artistic Art Nouveau wedding with flowing lines, natural motifs, artistic elements, nouveau decorations, organic designs',
            'lighting': 'Art Nouveau lighting, artistic glow, flowing ambiance, organic illumination',
            'colors': 'nouveau gold, artistic green, flowing brown, natural cream, organic earth',
            'atmosphere': 'artistic Art Nouveau celebration with flowing beauty',
            'specific_elements': 'flowing Art Nouveau ceremony arch, artistic decorations, natural motifs, nouveau details, organic features'
        },
        'great_gatsby': {
            'description': 'glamorous Great Gatsby wedding with art deco elements, jazz age decorations, 1920s luxury, Gatsby glamour, roaring twenties theme',
            'lighting': 'Great Gatsby lighting, art deco glow, jazz age ambiance, luxury illumination',
            'colors': 'Gatsby gold, art deco black, jazz age cream, luxury pearl, twenties silver',
            'atmosphere': 'glamorous Great Gatsby celebration with roaring twenties luxury',
            'specific_elements': 'art deco ceremony backdrop, Gatsby decorations, jazz age details, luxury elements, twenties features'
        }
    }
    
    # Keep the same SPACE_TRANSFORMATIONS, GUEST_COUNT_MODIFIERS, etc. from previous version
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
            'description': 'intimate gathering for 15-30 guests with cozy seating arrangement',
            'seating': '3-4 rows of chairs or 2-3 small tables',
            'scale': 'small intimate scale decorations'
        },
        'medium': {
            'description': 'medium celebration for 75-100 guests with balanced seating',
            'seating': '8-10 rows of chairs or 8-10 round tables',
            'scale': 'medium scale decorations and arrangements'
        },
        'large': {
            'description': 'large celebration for 150-200 guests with grand seating arrangement',
            'seating': '12-15 rows of chairs or 15-20 round tables',
            'scale': 'large scale decorations and impressive arrangements'
        },
        'grand': {
            'description': 'grand spectacular celebration for 250+ guests with magnificent seating',
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
        """Generate a comprehensive, specific prompt for dramatic wedding transformations"""
        
        theme_data = cls.THEME_STYLES.get(wedding_theme, cls.THEME_STYLES['classic'])
        space_data = cls.SPACE_TRANSFORMATIONS.get(space_type, cls.SPACE_TRANSFORMATIONS['wedding_ceremony'])
        
        # Build dramatic, specific prompt
        prompt_parts = [
            # High quality foundation
            "professional wedding staging, photorealistic, detailed, high resolution,",
            
            # Specific transformation instruction
            f"Change space into a complete {space_data['setup']}",
            
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
        
        # Final setup requirements
        prompt_parts.extend([
            "elegant wedding setup, celebration ready",
            "complete transformation of space",
            "no people visible, empty chairs and tables ready for guests"
        ])
        
        # Join with proper spacing
        main_prompt = " ".join([part.strip() for part in prompt_parts if part.strip()])
        
        # Enhanced negative prompt for better results
        negative_prompt = cls.generate_enhanced_negative_prompt()
        
        return {
            'prompt': main_prompt,
            'negative_prompt': negative_prompt,
            'recommended_params': cls.get_dynamic_parameters(wedding_theme, space_type, guest_count)
        }
    
    @classmethod
    def generate_enhanced_negative_prompt(cls):
        """Generate comprehensive negative prompt for wedding venue transformations"""
        negative_elements = [
            # People and faces (critical for venue photos)
            "people, faces, crowd, guests, bride, groom, wedding party, humans, person, bodies",
            
            # Quality issues
            "blurry, low quality, distorted, pixelated, artifacts, noise, low resolution",
            
            # Unwanted content
            "text, watermark, signature, logo, copyright, writing, signs",
            
            # Bad atmosphere/mood
            "dark, dim, gloomy, messy, cluttered, chaotic, unorganized, dirty",
            
            # Style issues
            "cartoon, anime, unrealistic, fake, artificial, painting, drawing",
            
            # Composition issues
            "cropped, cut off, partial, incomplete, tilted, askew",
            
            # Unwanted objects
            "cars, vehicles, modern electronics, phones, computers, inappropriate items"
        ]
        
        return ", ".join(negative_elements)
    
    @classmethod
    def get_dynamic_parameters(cls, wedding_theme, space_type, guest_count):
        """Get optimized parameters based on choices"""
        
        base_params = {
            'strength': 0.5,  # Increased for more dramatic transformation
            'output_format': 'png',
        }
        
        # Adjust strength based on guest count (more guests = more transformation needed)
        if guest_count == 'intimate':
            base_params['strength'] = 0.05  # Less transformation for intimate spaces
        elif guest_count in ['large', 'grand']:
            base_params['strength'] = 0.1   # More transformation for large celebrations
        
        # Adjust aspect ratio for different spaces
        if space_type in ['reception_area', 'dance_floor']:
            base_params['aspect_ratio'] = '16:9'  # Better for large celebration spaces
        elif space_type in ['photo_backdrop', 'bridal_suite']:
            base_params['aspect_ratio'] = '4:3'   # Good for focused areas
        
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
        elif wedding_theme == 'bohemian':
            suggestions.update({
                'season': 'summer',
                'color_scheme': 'earth_tones'
            })
        elif wedding_theme == 'classic':
            suggestions.update({
                'budget_level': 'luxury',
                'color_scheme': 'neutral'
            })
        elif wedding_theme == 'moroccan_nights':
            suggestions.update({
                'budget_level': 'luxury',
                'color_scheme': 'jewel_tones',
                'time_of_day': 'night'
            })
        elif wedding_theme == 'japanese_zen':
            suggestions.update({
                'season': 'spring',
                'color_scheme': 'neutral',
                'time_of_day': 'afternoon'
            })
        elif wedding_theme == 'indian_palace':
            suggestions.update({
                'budget_level': 'ultra_luxury',
                'color_scheme': 'jewel_tones',
                'guest_count': 'large'
            })
        
        return suggestions
    
    @classmethod
    def get_theme_suggestions(cls, wedding_theme):
        """Get specific suggestions for a wedding theme"""
        if wedding_theme not in cls.THEME_STYLES:
            return None
            
        theme_data = cls.THEME_STYLES[wedding_theme]
        
        return {
            'guest_count': 'medium',
            'budget_level': 'moderate',
            'time_of_day': 'evening',
            'color_scheme': 'neutral',
            'specific_elements': theme_data['specific_elements'],
            'atmosphere': theme_data['atmosphere']
        }