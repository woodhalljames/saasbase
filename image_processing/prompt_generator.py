# image_processing/prompt_generator.py - Enhanced prompts for Gemini 2.5

class WeddingVenuePromptGenerator:
    """
    Enhanced wedding space prompt generation for Gemini 2.5 Flash.
    Focus: Detailed decorative styling without architectural changes.
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
            user_instructions: Additional user instructions
            
        Returns:
            str: Complete text prompt for Gemini
        """
        
        # Custom prompt mode - enhance and add user instructions
        if custom_prompt and custom_prompt.strip():
            prompt = custom_prompt.strip()
            
            # Add user instructions if provided
            if user_instructions and user_instructions.strip():
                prompt += f" Additionally, {user_instructions.strip()}"
            
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
                            lighting_mood=None, color_scheme=None, user_instructions=None):
        """Build detailed guided prompt from wedding parameters"""
        
        # Get enhanced theme and space styling
        theme_styling = cls._get_theme_styling(wedding_theme, space_type)
        
        # Start with specific decoration prompt
        prompt = f"Transform this space into a stunning {cls._get_space_description(space_type)} decorated with {theme_styling}"
        
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
        
        # Add user instructions
        if user_instructions and user_instructions.strip():
            prompt += f" Additionally, incorporate these elements: {user_instructions.strip()}"
        
        # Ensure focus on decoration and empty space
        prompt += " The decorated venue should appear complete, polished, and ready for the celebration, with no people visible in the scene."
        
        return prompt
    
    @classmethod
    def _get_theme_styling(cls, wedding_theme, space_type):
        """Get detailed styling description combining theme and space - 80+ themes"""
        
        # Theme-specific styling with consistent detail level (50-80 words each)
        theme_base = {
            # Classic Traditional Themes
            'rustic': 'rustic barn wedding featuring weathered wood farm tables with burlap runners and white lace overlays, mason jar centerpieces filled with wildflowers and baby\'s breath, galvanized metal buckets with sunflowers, vintage milk bottles, cross-back wooden chairs with burlap bow ties, wagon wheel decorations, hay bale seating areas with plaid blankets, suspended Edison bulb string lights on black wire, wooden crate displays, hand-painted wooden signs, antique farm tools as wall decor, checkered gingham ribbons, and wine barrel cocktail tables',
            
            'modern': 'contemporary minimalist celebration with clear acrylic ghost chairs, tall cylinder vases holding single white orchids, geometric metal centerpieces in gold or copper, crisp white linens with silver chargers, LED light strips in clean lines, mirror-top tables, monochromatic white flower arrangements, lucite table numbers, chrome bar setups, geometric backdrop panels, clear glass vessels, metallic balloon installations, sleek white dance floor with patterns, modern sculptural elements, and precisely arranged minimalist decor',
            
            'vintage': 'nostalgic vintage romance with antique brass candelabras, mixed china place settings in pastels, lace doily overlays on tables, pearl strand garlands, vintage suitcase card holders, old typewriters as guest book stations, antique picture frames with sepia photos, mercury glass vases with roses and peonies, velvet furniture in dusty rose, vintage book centerpieces, cameo brooch napkin rings, pocket watch displays, crystal punch bowls, Victorian parasols, and aged brass fixtures',
            
            'classic': 'timeless traditional elegance featuring gold Chiavari chairs with ivory cushions, tall crystal candelabras with white taper candles, white rose and lily arrangements in silver pedestal vases, pristine white tablecloths with gold-rimmed china, crystal stemware, symmetrical floral arrangements, ivory silk draping with swags, formal place cards in gold script, silver charger plates, traditional wedding cake display, damask napkins, pearl accents, and refined crystal chandelier installations',
            
            'garden': 'enchanted garden party with wrought iron furniture, overflowing English garden flowers including roses peonies and delphinium in aged terracotta pots, moss table runners, bird cage decorations, vintage watering cans as vases, climbing ivy on white trellises, potted topiaries, wooden garden signs, butterfly decorations, stone garden statues, wicker baskets with flowers, garden tool displays, paper parasols, natural wood elements, and market string lights between poles',
            
            'beach': 'coastal celebration featuring driftwood centerpieces with air plants, nautical rope wrapped details, starfish and shell scatter, hurricane lanterns with sand and candles, flowing white fabric panels, fishing net backdrops with lights, sea glass vessels, coral displays, ship wheels, anchor decorations, striped navy and white patterns, bamboo chairs, tropical flowers, message in bottle place cards, and weathered wood signs',
            
            'industrial': 'urban warehouse chic with exposed Edison bulb installations, concrete planter centerpieces with succulents, metal pipe structures, raw wood and metal tables, geometric copper centerpieces, leather seating elements, gear and pulley decorations, distressed metal signage, black metal chairs, minimalist protea arrangements, wire basket displays, vintage factory carts as bars, concrete and metal vessels, exposed brick backdrops, and industrial pendant lighting',
            
            'bohemian': 'free-spirited boho celebration featuring macrame wall hangings, layered vintage rugs, pampas grass in ceramic vessels, mixed metal lanterns, eclectic furniture pieces, dreamcatcher installations, tapestry backdrops, floor cushion seating with tassels, brass tray tables, wildflower arrangements in mismatched bottles, feather accents, wooden bead garlands, paisley patterns, mandala decorations, incense holders, and warm globe string lights overhead',
            
            'glamorous': 'Hollywood regency opulence with crystal chandeliers, mirrored furniture and table tops, sequined linens in gold and silver, tall ostrich feather centerpieces, art deco patterns, metallic balloon installations, velvet draping in jewel tones, gold candelabras, rhinestone scatter, illuminated marquee letters, crystal curtain backdrops, champagne towers, gilded everything, dramatic spotlighting, and luxurious metallic accents throughout',
            
            'tropical': 'paradise island vibes featuring monstera leaves as placemats, bird of paradise arrangements, bamboo furniture, tiki torches, pineapple centerpieces, palm frond installations overhead, bright hibiscus flowers, rattan lanterns, tropical fruit displays, colorful paper umbrellas, banana leaf runners, carved tiki elements, bright fabric in sunset colors, orchid scatter, coconut vessels, and vibrant paper lantern clusters',
            
            'fairy_tale': 'storybook enchantment with flowing tulle canopies embedded with lights, oversized paper flowers, crystal chandeliers dripping with beads, golden branch centerpieces with crystals, castle-inspired decorations, clock displays, glass slipper elements, crown and tiara accents, magical forest backdrops, toadstool seating, butterfly installations, iridescent fabrics, mirror displays creating infinite reflections, wand decorations, and thousands of twinkling fairy lights',
            
            # Expanded Classic Themes
            'minimalist': 'refined minimalist aesthetic with single-stem flowers in slim vases, monochromatic white palette, clean geometric shapes, simple linen runners, modern white chairs, sparse but impactful decorations, negative space emphasis, single floating candles, simple greenery, white ceramic vessels, understated elegance, clear glass elements, subtle lighting, streamlined furniture, and purposeful restraint in every decorative choice',
            
            'maximalist': 'bold maximalist explosion with layers of patterns and textures, abundant floral installations covering every surface, mixed metallic finishes, multiple fabric types, ornate furniture pieces, countless candles, oversized decorations, bold color combinations, dramatic ceiling installations, pattern mixing, texture layering, multiple centerpiece elements, abundant lighting sources, and more-is-more philosophy throughout',
            
            'art_deco': 'roaring twenties glamour featuring geometric patterns in gold and black, fan motifs, stepped designs, peacock feathers, champagne towers, beaded curtains, brass fixtures, angular floral arrangements, mirror and chrome details, bold geometric floor patterns, vintage barware, cigarette girl trays, jazz age posters, geometric backdrop panels, and metallic sunburst decorations',
            
            'mid_century': 'retro mid-century style with atomic age patterns, starburst decorations, teak wood elements, orange and turquoise accents, vintage bar carts, geometric planters, bold graphic prints, chrome details, low profile furniture, abstract art pieces, vintage glassware, space age elements, boomerang patterns, kidney-shaped tables, and Palm Springs inspired colors',
            
            'mediterranean': 'sun-soaked Mediterranean style featuring olive branches in ceramic vessels, lemon and orange displays, terracotta elements, blue and white pottery, wrought iron details, grapevine installations, lavender bundles, rustic wood tables, wine bottle centerpieces, herb bouquets, white flowing fabrics, mosaic tile accents, basket weave textures, coastal elements, and warm golden lighting',
            
            'southwestern': 'desert southwestern charm with terra cotta pottery, cacti and succulent gardens, Native American inspired patterns, leather and suede accents, turquoise details, wooden beam elements, sand-colored fabrics, geometric blanket patterns, metal sun decorations, dried flower arrangements, cow skull replicas, rope details, warm earth tones, copper accents, and desert plant installations',
            
            'preppy': 'classic preppy style featuring navy and white stripes, monogrammed everything, whale motifs, madras plaid patterns, pearl details, anchor decorations, sailing elements, country club aesthetics, grosgrain ribbons, needlepoint pillows, chinoiserie vases, boxwood topiaries, silver julep cups, tennis and golf motifs, and traditional East Coast elegance',
            
            'scandinavian': 'Nordic minimalist beauty with white and natural wood, simple greenery, white candles in abundance, cozy textiles, hygge elements, geometric patterns, neutral colors, birch branch installations, simple wildflowers, frosted glass vessels, wool blankets, minimalist furniture, paper star lanterns, natural materials, and understated Scandi elegance',
            
            # Sports & Activities
            'football_fanatic': 'football championship celebration with team color decorations, pennant banners, football centerpieces, goal post structures, turf table runners, stadium seat replicas, tailgate food stations, foam finger displays, jersey number table markers, helmet decorations, referee stripe patterns, football field layout designs, team logo projections, trophy displays, and sports memorabilia throughout',
            
            'baseball_diamond': 'America\'s pastime theme featuring vintage baseball mitts as decoration, base markers for dance floor corners, baseball centerpieces in glass bowls, pennant flags, peanuts and Cracker Jack boxes, stadium seat numbers, vintage baseball cards, home plate designs, dugout bench seating, scoreboard displays, hot dog bar stations, baseball bat details, team jerseys, and ballpark organ music setup',
            
            'hockey_rink': 'ice hockey celebration with hockey stick archways, puck decorations scattered on tables, team jerseys displayed, ice blue and white color scheme, goal net photo backdrops, penalty box seating area, zamboni toy displays, hockey helmet centerpieces, rink board designs, face-off circle dance floor markers, Stanley Cup replicas, referee stripe details, and frozen-inspired decorations',
            
            'basketball_court': 'basketball game theme featuring mini hoops as centerpieces, basketball centerpieces, court line tape designs on dance floor, scoreboard displays, jersey number markers, orange and black decorations, net details, sneaker displays, championship banner replicas, basketball texture elements, team bench seating areas, shot clock decorations, and March Madness bracket displays',
            
            'soccer_pitch': 'world soccer celebration with soccer ball centerpieces, goal net installations, international flag displays, pitch green table runners, corner flag markers, soccer cleat displays, World Cup trophy replicas, team scarf decorations, referee cards as place cards, soccer field layout designs, stadium seating areas, team colors throughout, and penalty kick photo stations',
            
            'golf_course': 'golf club elegance featuring golf ball vase fillers, miniature flag centerpieces, artificial putting green runners, golf club displays, argyle patterns, golf cart decorations, scorecard menus, tee markers, sand trap inspired elements, country club aesthetics, golf bag card holders, 19th hole bar setup, green and fairway designs, and Masters Tournament inspired details',
            
            'tennis_match': 'tennis club sophistication with tennis ball centerpiece vessels, racquet displays, net divider decorations, court green colors, white line details, score keeping elements, Wimbledon inspired strawberries and cream, tennis skirt inspired linens, ball can vases, trophy displays, umpire chair photo spot, court surface patterns, and championship aesthetics',
            
            'skiing_lodge': 'alpine ski resort featuring vintage ski displays, ski lift chair seating, snow-covered branch centerpieces, lodge fireplace setups, hot cocoa bars, plaid blankets, wooden ski signs, gondola decorations, slope map displays, après-ski elements, ski pole decorations, mountain backdrop images, warming hut aesthetics, and cozy cabin ambiance',
            
            'surfing_beach': 'surf culture celebration with surfboard displays, beach sand centerpieces, wave pattern decorations, surf wax favors, tropical flowers, beach photography, vintage surf posters, board shorts pattern fabrics, shell leis, wave projection lighting, surf shack bar setup, beach bonfire elements, coastal driftwood, and endless summer vibes',
            
            'yoga_zen': 'peaceful yoga retreat with meditation cushions, bamboo elements, lotus flower arrangements, Sanskrit symbol decorations, essential oil diffusers, crystal displays, mandala patterns, zen garden centerpieces, prayer flag installations, singing bowl stations, bamboo fountains, natural fiber mats, chakra color elements, mindfulness quotes, and serene minimalist aesthetics',
            
            'crossfit_gym': 'crossfit box celebration featuring kettlebell decorations, rope climb installations, box jump platforms as display stands, barbell details, chalk bucket elements, tire decorations, motivational banner quotes, gym equipment displays, WOD board menus, protein shake bar, athletic achievements display, industrial gym aesthetics, rubber mat flooring elements, and competitive spirit decorations',
            
            'marathon_runner': 'running celebration with race bib table numbers, medal displays, running shoe decorations, mile marker signs, finish line tape, water station setups, energy gel favors, race route maps, timing clock displays, personal record celebrations, marathon distance markers, runner silhouettes, track lane designs, and victory celebration elements',
            
            'rock_climbing': 'climbing adventure theme featuring carabiner decorations, climbing rope details, chalk bag centerpieces, mountain silhouette backdrops, climbing hold elements, harness displays, topographic map table runners, summit flag decorations, camping lanterns, adventure quotes, outdoor gear displays, rock texture elements, belay station setups, and vertical challenge aesthetics',
            
            # Hobbies & Interests
            'bookworm_library': 'literary celebration with stacked vintage books as centerpieces, library card catalog drawers, reading nook seating areas, bookmark favors, literary quote displays, antique typewriter stations, globe decorations, leather-bound details, paper rose bouquets made from book pages, library ladder displays, card pocket place cards, dewey decimal table numbers, author portrait galleries, and first edition displays',
            
            'video_game_arcade': 'retro arcade featuring pixel art decorations, arcade cabinet replicas, joystick centerpieces, coin slot details, high score displays, 8-bit decorations, neon lighting, game controller elements, power-up symbols, level-up signage, pixelated flowers, achievement unlock banners, game cartridge displays, and classic arcade carpet patterns',
            
            'board_game_night': 'game night extravaganza with oversized dice decorations, Scrabble tile place cards, chess piece centerpieces, Monopoly money details, game board table runners, playing card displays, puzzle piece elements, spinner decorations, meeple figures, game box stacks, trivia cards, score pad menus, game piece favors, and winner\'s circle elements',
            
            'comic_book_hero': 'superhero headquarters with comic panel backdrop walls, action figure displays, cape decorations, mask elements, pow and bam signage, speech bubble props, comic book centerpieces, hero logo projections, cityscape silhouettes, vintage comic displays, superhero emblems, comic strip runners, graphic novel stacks, and dynamic action decorations',
            
            'movie_theater': 'cinema celebration featuring movie reel decorations, popcorn box centerpieces, ticket stub place cards, red carpet runner, velvet rope barriers, clapperboard signs, film strip garlands, marquee letter lights, director chair seating, Oscar statue replicas, movie poster displays, concession stand setup, theater seat arrangements, and Hollywood spotlight effects',
            
            'music_festival': 'festival vibes with vinyl record decorations, concert poster walls, band merchandise displays, guitar pick confetti, music note garlands, festival wristbands, stage pass badges, amplifier stack decorations, microphone centerpieces, setlist menus, tour poster galleries, instrument displays, band tee banners, and backstage pass elements',
            
            'vinyl_collector': 'record shop aesthetic featuring album cover displays, record player stations, 45 adapter decorations, milk crate storage displays, liner note details, groove pattern elements, turntable centerpieces, record sleeve place settings, vintage hi-fi equipment, music genre sections, rare pressing displays, record cleaning station setup, listening booth areas, and analog warmth throughout',
            
            'photography_studio': 'camera enthusiast paradise with vintage camera displays, film strip garlands, darkroom red lighting accents, photo development line setups, lens cap decorations, tripod elements, light meter details, film canister favors, contact sheet displays, aperture decorations, shutter speed references, photo booth setups, gallery wall displays, and f-stop table numbers',
            
            'art_studio': 'creative artist space featuring paint palette centerpieces, brush bouquets in paint cans, color wheel decorations, canvas displays, easel setups, paint tube details, artist smock elements, splatter paint effects, gallery lighting, sketch pad menus, pencil holder vases, art supply decorations, frame displays, and creative chaos aesthetics',
            
            'pottery_ceramic': 'ceramic studio charm with handmade pottery displays, clay texture elements, potter\'s wheel stations, glaze sample decorations, kiln-fired centerpieces, tool displays, apron decorations, thrown vessel arrangements, ceramic tile details, mud and clay earth tones, artisan pottery collections, wheel throwing demonstrations setup, and handcrafted beauty',
            
            'knitting_crafts': 'crafty celebration featuring yarn ball centerpieces, knitting needle displays, crochet doily overlays, patchwork quilt backdrops, button collections, fabric flower bouquets, embroidery hoop decorations, sewing machine displays, pin cushion details, measuring tape garlands, thimble favors, cross-stitch samplers, pattern displays, and handmade warmth',
            
            'gardening_greenhouse': 'garden enthusiast haven with seed packet place cards, terra cotta pot centerpieces, garden tool displays, plant marker signs, watering can arrangements, greenhouse structure elements, soil and mulch textures, garden glove decorations, trowel and spade details, plant identification tags, botanical print displays, potting bench setups, and growing garden beauty',
            
            'cooking_chef': 'culinary celebration featuring chef hat decorations, whisk and spatula bouquets, cutting board displays, recipe card menus, apron elements, spice jar centerpieces, kitchen utensil garlands, cookbook stacks, measuring cup vessels, ingredient displays, chef knife details, mise en place organization, tasting spoon favors, and gourmet kitchen aesthetics',
            
            'wine_enthusiast': 'vineyard elegance with wine barrel tables, cork centerpieces, grape cluster decorations, wine bottle displays, decanter elements, tasting note cards, corkscrew details, wine glass markers, barrel stave signs, vintage label displays, wine region maps, sommelier elements, cellar aesthetics, and sophisticated tasting room ambiance',
            
            'craft_beer_brewery': 'brewery taproom featuring hop garlands, beer flight centerpieces, growler displays, coaster collections, tap handle decorations, grain and barley elements, brewery barrel tables, pint glass arrangements, beer label art, fermentation tank replicas, brewing equipment displays, tasting paddle setups, pub table arrangements, and craft beer culture',
            
            'coffee_shop': 'coffeehouse vibes with burlap coffee sack decorations, espresso cup centerpieces, coffee bean vase fillers, vintage grinder displays, pour-over stations, latte art prints, coffee plant arrangements, mug collection displays, French press elements, roasting elements, café menu boards, coffeehouse furniture, bean origin maps, and aromatic ambiance',
            
            'tea_ceremony': 'tea parlor elegance featuring vintage teapot centerpieces, teacup arrangements, tea tin displays, loose leaf decorations, strainer and infuser details, sugar cube pyramids, lemon slice accents, scone tier displays, doily overlays, tea garden elements, ceremony table settings, porcelain collections, tea leaf readings setup, and refined afternoon tea aesthetics',
            
            # Travel & Adventure
            'world_traveler': 'global adventure with vintage suitcase stacks, world map backdrops, passport invitation designs, boarding pass place cards, globe centerpieces, postcard displays, currency decorations, landmark replicas, travel tag garlands, compass rose details, airplane models, travel journal stations, destination signs, international flag bunting, and wanderlust elements',
            
            'road_trip': 'highway adventure featuring vintage map decorations, license plate displays, route marker signs, gas station memorabilia, roadside diner elements, car dashboard setups, mile marker decorations, rest stop signs, travel game displays, snack station setups, playlist decorations, windshield photo frames, rearview mirror details, and endless highway vibes',
            
            'camping_outdoors': 'wilderness camping with lantern centerpieces, plaid blanket table runners, tent card displays, campfire elements, s\'mores stations, trail mix bars, sleeping bag seating, camp chair arrangements, wilderness signs, nature guide books, flashlight decorations, camping gear displays, forest elements, and outdoor adventure spirit',
            
            'nautical_sailing': 'sailing yacht elegance with rope knot decorations, anchor centerpieces, nautical flag bunting, compass displays, ship wheel elements, porthole mirrors, sailing chart table runners, buoy decorations, marina elements, yacht club pennants, brass nautical instruments, deck furniture, sail cloth draping, and maritime sophistication',
            
            'train_station': 'railway romance featuring vintage luggage, train ticket displays, conductor hat elements, railway lanterns, station clock replicas, platform signs, railroad track details, dining car setups, pullman car aesthetics, steam engine elements, railway map displays, porter uniform details, first class cabin decor, and nostalgic travel elegance',
            
            'aviation_pilot': 'flight deck celebration with propeller decorations, aviator goggle displays, flight path maps, control panel elements, pilot wing badges, airplane model centerpieces, navigation chart runners, altimeter decorations, runway lighting, hangar aesthetics, vintage aviation posters, cockpit setups, flight log books, and sky-high sophistication',
            
            # Food & Culinary Themes
            'pizza_parlor': 'pizzeria paradise featuring pizza box centerpieces, red checkered tablecloths, oregano and basil plants, pizza peel displays, mozzarella and tomato arrangements, Italian flag colors, dough rolling elements, brick oven replicas, menu board signs, parmesan shakers, crushed red pepper details, delivery box stacks, and authentic Italian touches',
            
            'taco_truck': 'street taco fiesta with papel picado in bright colors, lime and cilantro displays, hot sauce bottle collections, corn and flour tortilla elements, salsa bar setups, Mexican tile patterns, cactus decorations, serape table runners, tequila elements, mariachi decorations, food truck signage, picnic table setups, and vibrant street food energy',
            
            'sushi_bar': 'Japanese sushi elegance featuring bamboo mat runners, chopstick displays, soy sauce vessels, wasabi and ginger accents, minimalist orchid arrangements, sake service elements, bento box inspirations, nori decorations, rice paper lanterns, ceramic dish displays, sushi roll models, bamboo elements, zen simplicity, and authentic Japanese aesthetics',
            
            'bbq_pitmaster': 'smokehouse celebration with grill decorations, sauce bottle displays, checkered flag patterns, picnic table setups, corn on the cob elements, mason jar drinks, butcher paper runners, smoke effect elements, meat thermometer details, apron displays, wood chip accents, cast iron displays, backyard BBQ vibes, and southern hospitality',
            
            'farmers_market': 'market day freshness featuring produce crate displays, chalkboard signs, basket centerpieces, fresh herb bundles, seasonal fruit arrangements, burlap and twine details, scale decorations, price tag elements, vendor booth setups, honey jar displays, flower bucket arrangements, farm stand aesthetics, and local harvest abundance',
            
            'bakery_patisserie': 'French bakery charm with macaron tower displays, cupcake stand centerpieces, rolling pin decorations, flour dust effects, vintage cake stands, pastry box stacks, baker\'s twine details, bread basket displays, icing bag decorations, cookie cutter garlands, mixing bowl elements, patisserie case setups, and sweet shop elegance',
            
            'ice_cream_social': 'sweet shop celebration featuring ice cream cone decorations, sundae bar setups, sprinkle confetti, cherry on top elements, waffle cone displays, vintage ice cream scoops, pastel color schemes, parlor chair seating, banana split boats, topping stations, freezer cart replicas, candy shop jars, and nostalgic sweetness',
            
            # Pets & Animals
            'dog_lover': 'puppy paradise with paw print decorations, dog bone centerpieces, leash and collar displays, photo galleries of dogs, hydrant replicas, tennis ball decorations, dog park elements, breed silhouettes, adoption celebration elements, doghouse card boxes, treat jar displays, dog toy arrangements, kennel club aesthetics, and best friend tributes',
            
            'cat_cafe': 'feline fancy featuring cat silhouette decorations, yarn ball centerpieces, scratching post elements, catnip plant displays, fish bone details, milk saucer elements, cat toy arrangements, whisker details, paw print trails, cat tower structures, cozy blanket nooks, window perch setups, and purr-fect sophistication',
            
            'horse_equestrian': 'stable elegance with horseshoe decorations, saddle displays, riding boot arrangements, hay bale seating, bridle and bit details, ribbon rosette displays, jump obstacle elements, grooming brush bouquets, stable door backdrops, trophy displays, riding helmet decorations, crop and whip details, and equestrian club sophistication',
            
            'bird_watching': 'aviary celebration featuring bird cage decorations, feather centerpieces, nest displays, bird guide books, binocular elements, bird bath features, seed packet favors, branch perch installations, egg replicas, field guide displays, migration map decorations, bird call elements, and ornithological beauty',
            
            # Tech & Gaming
            'tech_startup': 'Silicon Valley chic with circuit board decorations, keyboard key place cards, monitor display setups, coding elements, startup poster displays, ping pong table elements, energy drink stations, standing desk setups, whiteboard idea walls, laptop sticker collections, cable management jokes, beta test elements, and innovation hub aesthetics',
            
            'drone_pilot': 'aerial adventure featuring drone displays, propeller decorations, flight controller elements, FPV goggle stations, racing gate structures, battery charging stations, aerial photography displays, GPS coordinate decorations, altitude markers, racing flag elements, repair station setups, and high-flying technology',
            
            'cryptocurrency': 'blockchain celebration with bitcoin decorations, mining rig displays, QR code elements, digital wallet cards, crypto coin replicas, chart displays, blockchain visualizations, ledger elements, moon and rocket themes, HODL signs, decentralized decorations, and digital revolution aesthetics',
            
            'podcast_studio': 'on-air elegance featuring microphone centerpieces, headphone displays, soundwave decorations, recording light signs, acoustic panel backdrops, mixing board elements, episode list displays, sponsor banners, studio furniture, pop filter decorations, cable management, broadcast elements, and professional studio vibes',
            
            'youtube_creator': 'content creation station with ring light decorations, camera displays, subscribe button elements, play button awards, thumbnail galleries, comment section props, notification bell details, studio setup recreations, tripod elements, editing timeline decorations, channel banner displays, and viral video energy',
            
            # Unique Interests
            'astronomy_stargazer': 'celestial celebration featuring constellation map backdrops, telescope displays, planet model centerpieces, star projections, moon phase decorations, galaxy swirl patterns, meteorite replicas, NASA elements, space mission patches, astrolabe decorations, star chart runners, nebula color schemes, and cosmic wonder',
            
            'marine_biology': 'ocean research theme with coral reef centerpieces, seashell collections, marine specimen displays, dive equipment decorations, ocean current maps, submarine elements, research vessel details, aquarium features, kelp forest decorations, tide pool replicas, maritime charts, and deep sea discoveries',
            
            'archaeology_dig': 'ancient discoveries featuring artifact replicas, dig site elements, brush and tool displays, fossil decorations, ancient map reproductions, expedition crate stacks, field notebook displays, carbon dating jokes, pottery shard arrangements, hieroglyph decorations, excavation grid patterns, and historical mystery',
            
            'magic_illusion': 'mystic magician theme with playing card cascades, top hat centerpieces, wand displays, rabbit decorations, magic trick setups, crystal ball elements, cape and costume details, illusion mirror effects, levitation elements, escape artist props, prestidigitation decorations, and enchanted mystery',
            
            'casino_vegas': 'high roller elegance featuring poker chip stacks, playing card displays, dice decorations, roulette wheel elements, slot machine replicas, jackpot signs, neon Vegas lights, felt table runners, dealer accessories, lucky charm displays, betting elements, and winning celebration vibes',
            
            'detective_mystery': 'noir investigation with magnifying glass decorations, evidence bag displays, crime scene tape, fingerprint details, case file folders, vintage typewriter stations, fedora hat elements, mysterious clue trails, interrogation lamp setups, witness board displays, cold case elements, and suspenseful atmosphere',
            
            'steampunk_victorian': 'retrofuturistic wonder with gear and cog decorations, brass goggles displays, clockwork elements, copper pipe structures, Victorian corsets details, airship models, mechanical wings, vintage key collections, pressure gauge decorations, leather and brass combinations, time machine elements, and industrial Victorian fusion',
            
            'medieval_renaissance': 'castle court celebration featuring heraldic banners, goblet centerpieces, candlestick displays, tapestry backdrops, coat of arms decorations, medieval feast elements, throne chair setups, suit of armor replicas, scroll invitations, wax seal details, castle tower elements, and royal court grandeur',
            
            'circus_carnival': 'big top spectacular with striped tent elements, popcorn and cotton candy stations, circus poster displays, juggling pin decorations, acrobat silhouettes, carousel horse replicas, ticket booth setups, ring master elements, vintage carnival games, balloon arrangements, clown accessories, and spectacular showmanship',
            
            'motorcycle_rally': 'biker celebration featuring leather and chrome details, motorcycle helmet displays, bandana decorations, chain link elements, exhaust pipe decorations, gas tank art, road sign displays, vintage bike posters, garage aesthetics, tool displays, racing flag elements, and rebellious spirit',
            
            'tiny_house': 'minimalist living with multi-functional furniture displays, space-saving elements, loft bed models, compact kitchen setups, fold-away decorations, tiny plant arrangements, efficient storage solutions, small-scale everything, cozy textiles, sustainable elements, micro living aesthetics, and intimate scaled beauty',
            
            'escape_room': 'puzzle adventure featuring lock and key decorations, cipher code displays, hidden compartment elements, timer countdown clocks, clue card trails, puzzle piece decorations, mystery box centerpieces, riddle displays, secret passage hints, team challenge elements, breakthrough moments, and intellectual adventure',
            
            'dungeons_dragons': 'fantasy quest celebration with d20 dice decorations, character sheet place cards, miniature figure displays, dungeon map table runners, dragon elements, treasure chest centerpieces, tavern aesthetics, spell book displays, adventure party elements, critical hit celebrations, campaign poster displays, and epic fantasy adventure'
        }
        
        base_styling = theme_base.get(wedding_theme, f'{wedding_theme.replace("_", " ")} themed decorative styling with carefully selected elements')
        
        # Add consistent space-specific enhancements
        space_enhancements = {
            'wedding_ceremony': ', arranged for a sacred ceremony space with decorated altar, guest seating with aisle decorations, and processional pathway style',
            'dining_area': ', configured as an elegant dining space with head table prominence, guest table arrangements, centerpiece displays, and coordinated place settings',
            'dance_floor': ', designed as a celebration space with defined dance area, perimeter social seating, DJ or band platform, and dynamic lighting effects',
            'cocktail_hour': ', styled for sophisticated mingling with high-top tables, bar station setups, appetizer displays, and comfortable conversation areas',
            'bridal_suite': ', created as a luxurious preparation sanctuary with vanity stations, relaxation seating, photo-worthy backdrops, and personal touches',
            'entrance_area': ', designed as a grand arrival experience with welcome signage, guest reception elements, gift table setup, and memorable first impressions',
        }
        
        return base_styling + space_enhancements.get(space_type, '')
    
    @classmethod
    def _get_seasonal_decor(cls, season):
        """Get seasonal landscape/environment alterations for the venue"""
        seasonal_elements = {
            'spring': 'The landscape shows fresh spring conditions with blooming trees, bright green new grass growth, budding flowers beginning to emerge, clear blue skies with soft white clouds.',
            'summer': 'The environment displays full summer conditions with lush deep green foliage on all trees and plants, fully mature landscapes, deep blue skies, and vibrant natural colors.',
            'fall': 'The landscape exhibits autumn transformation with trees showing golden, orange, and red foliage, some fallen leaves on the ground, crisp clear atmosphere, and natural environment in seasonal transition.',
            'winter': 'The environment shows winter conditions with bare tree branches or evergreens, potential frost or snow on the ground and surfaces, crisp cold overcast or pale blue winter sky, and dormant landscape elements.',
        }
        
        return seasonal_elements.get(season, '')
    
    @classmethod
    def _get_lighting_design(cls, lighting_mood):
        """Get consistent lighting design for all themes and spaces"""
        lighting_designs = {
            'dawn': 'Illuminated with soft dawn lighting featuring pale pink and golden hues, minimal candles just being lit, gentle ambient glow, and fresh morning atmosphere.',
            'morning': 'Brightened with clear morning light using white candles, bright ambient lighting, crystal-clear visibility, and fresh daytime energy.',
            'midday': 'Lit with full midday brightness featuring minimal decorative lighting, clear visibility throughout, bright white accents, and natural daylight simulation.',
            'golden_hour': 'Bathed in golden hour warmth with amber-toned lighting, warm candles throughout, honeyed glow on all surfaces, and sunset-inspired ambiance.',
            'dusk': 'Enhanced with dusk magic featuring purple and pink lighting transitions, candles being lit throughout, twilight color washes, and romantic evening approach.',
            'evening': 'Illuminated for evening elegance with full candlelight displays, warm string lights overhead, lanterns glowing softly, and intimate lighting throughout.',
            'night': 'Transformed for nighttime magic with abundant candles, string light canopies, lanterns at every level, uplighting on key features, and complete artificial illumination.',
            'bright': 'Energized with bright celebration lighting using white LED strings, clear bulbs throughout, bright uplighting, and maximum visibility.',
            'dim': 'Softened with intimate dim lighting featuring scattered candles, low-wattage bulbs, gentle amber glow, and cozy atmosphere.',
            'romantic': 'Enchanted with romantic lighting through hundreds of candles, soft string lights, gentle shadows, warm golden tones, and dreamy ambiance.',
            'candlelit': 'Glowing with pure candlelight featuring pillar candles, votives, floating candles, candelabras, and flickering flame ambiance throughout.',
            'natural': 'Utilizing natural light emphasis with minimal artificial additions, light-colored decorations to maximize brightness, strategic mirror placements, and organic illumination.',
            'fluorescent': 'Lit with clean fluorescent brightness featuring cool white tones, even distribution, modern clarity, and professional venue lighting.',
            'rainy': 'Adapted for overcast conditions with extra warm lighting to counter gray skies, abundant candles for coziness, string lights for cheerfulness, and weather-proof illumination.',
        }
        
        return lighting_designs.get(lighting_mood, '')
    
    @classmethod
    def _get_color_styling(cls, color_scheme):
        """Get detailed color application descriptions"""
        color_applications = {
            # Primary Colors
            'red': 'Dominated by passionate red with crimson roses, burgundy dahlias, red linens, ruby glass accents, and red uplighting creating bold energy.',
            'orange': 'Energized with vibrant orange through marigolds, orange roses, tangerine fabrics, copper vessels, and warm orange lighting.',
            'yellow': 'Brightened with sunny yellow featuring sunflowers, yellow roses, golden linens, amber glass, and warm yellow lighting.',
            'green': 'Refreshed with natural green using abundant foliage, green hydrangeas, sage linens, emerald accents, and forest lighting.',
            'blue': 'Cooled with serene blue through hydrangeas, delphiniums, navy linens, cobalt glass, and ocean-inspired lighting.',
            'purple': 'Enriched with royal purple featuring orchids, lavender, plum fabrics, amethyst accents, and deep purple lighting.',
            
            # Pastels
            'pastel_pink': 'Softened with blush pink through pale roses, pink peonies, rose fabrics, pearl accents, and gentle pink lighting.',
            'pastel_peach': 'Warmed with soft peach using garden roses, peach ranunculus, coral fabrics, champagne metals, and sunset lighting.',
            'pastel_lavender': 'Calmed with gentle lavender featuring sweet peas, lilac blooms, purple fabrics, silver accents, and ethereal lighting.',
            'pastel_blue': 'Soothed with powder blue through pale hydrangeas, forget-me-nots, sky fabrics, white accents, and soft blue washes.',
            'pastel_mint': 'Freshened with mint green using eucalyptus, white flowers, sage fabrics, silver details, and cool lighting.',
            
            # Neons
            'neon_pink': 'Electrified with hot pink featuring bright gerberas, fuchsia fabrics, fluorescent accents, and vibrant pink lighting.',
            'neon_green': 'Energized with lime green through tropical leaves, bright ribbons, electric accents, and vivid green lighting.',
            'neon_orange': 'Blazing with electric orange using bright marigolds, orange fabrics, fluorescent details, and intense orange glow.',
            'neon_yellow': 'Glowing with electric yellow featuring bright sunflowers, neon ribbons, fluorescent elements, and brilliant yellow light.',
            
            # Earth Tones
            'earth_brown': 'Grounded with rich brown through chocolate cosmos, wood elements, leather details, and warm brown lighting.',
            'earth_terracotta': 'Warmed with terracotta using rust roses, clay vessels, sienna fabrics, and desert-inspired lighting.',
            'earth_sage': 'Naturalized with sage green through eucalyptus, olive branches, moss elements, and organic lighting.',
            'earth_sand': 'Neutralized with sand tones using dried grasses, beige fabrics, natural fibers, and soft warm lighting.',
            
            # Muted/Dusty
            'muted_rose': 'Sophisticated with dusty rose through mauve flowers, blush fabrics, antique metals, and soft pink lighting.',
            'muted_blue': 'Refined with dusty blue using pale delphiniums, gray-blue fabrics, silver accents, and subtle blue lighting.',
            'muted_sage': 'Organic with dusty sage through dried eucalyptus, green-gray fabrics, natural woods, and earthy lighting.',
            
            # Jewel Tones
            'jewel_emerald': 'Luxurious with emerald green using deep green flowers, velvet fabrics, gold accents, and rich green lighting.',
            'jewel_sapphire': 'Opulent with sapphire blue through deep blue flowers, navy fabrics, silver details, and royal blue lighting.',
            'jewel_ruby': 'Rich with ruby red using burgundy blooms, wine fabrics, gold elements, and deep red lighting.',
            'jewel_amethyst': 'Regal with amethyst purple through deep purple orchids, plum fabrics, silver accents, and violet lighting.',
            
            # Temperature Palettes
            'cool_palette': 'Cooled throughout with blues, greens, and purples in flowers and fabrics, silver metals, and cool-toned lighting.',
            'warm_palette': 'Warmed throughout with reds, oranges, and yellows in blooms and linens, gold metals, and warm lighting.',
            
            # Metallics
            'metallic_gold': 'Gilded in luxury with gold vessels, golden roses, champagne fabrics, brass details, and warm golden lighting.',
            'metallic_silver': 'Shimmering with silver through mercury glass, white flowers, gray fabrics, chrome details, and cool silver lighting.',
            'metallic_rose_gold': 'Glowing with rose gold using pink flowers, blush fabrics, copper accents, and warm pink metallic lighting.',
            'metallic_copper': 'Warmed with copper through orange flowers, rust fabrics, copper vessels, and amber metallic lighting.',
            'metallic_bronze': 'Antiqued with bronze using brown flowers, chocolate fabrics, aged metals, and deep bronze lighting.',
            
            # Monochromes
            'all_white': 'Pure white elegance with white flowers, ivory fabrics, pearl accents, crystal details, and bright white lighting.',
            'all_black': 'Dramatic black sophistication using deep purple flowers, black linens, silver accents, and moody lighting.',
            'greyscale': 'Graduated grays from white to black with silver flowers, gray fabrics, metallic accents, and balanced lighting.',
            
            # Vintage Colors
            'vintage_sepia': 'Aged in sepia tones with cream and brown flowers, antique fabrics, brass details, and warm vintage lighting.',
            'vintage_dusty': 'Softened with vintage dusty tones using muted flowers, faded fabrics, antique metals, and nostalgic lighting.',
            
            # Retro Colors
            'retro_70s': 'Groovy with orange, brown, and gold using autumn flowers, corduroy textures, brass details, and warm retro lighting.',
            'retro_80s': 'Bold with neon pink, electric blue, and lime using bright flowers, geometric patterns, chrome details, and colorful lighting.',
            'retro_90s': 'Nostalgic with teal, purple, and hot pink using mixed flowers, holographic accents, and color-changing lighting.',
        }
        
        return color_applications.get(color_scheme, '')
    
    @classmethod
    def _get_space_description(cls, space_type):
        """Get concise space type descriptions"""
        space_descriptions = {
            'wedding_ceremony': 'wedding ceremony staging area',
            'dance_floor': 'dance floor celebration area',
            'dining_area': 'reception dining area',
            'cocktail_hour': 'cocktail reception area',
            'bridal_suite': 'bridal preparation suite',
            'entrance_area': 'entrance-way and welcome area',
        }
        
        return space_descriptions.get(space_type, space_type.replace('_', ' '))