# image_processing/models.py - UPDATED with Composition, Emotional Tone, Activities, and Wedding Moments

import os
import uuid
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


def user_image_upload_path(instance, filename):
    """Generate upload path for user images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"user_images/{instance.user.id}/{filename}"


def processed_image_upload_path(instance, filename):
    """Generate upload path for processed images - preserves human-readable filename"""
    import os
    import re
    
    base_filename = os.path.basename(filename)
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', base_filename)
    
    if '.' not in safe_filename:
        safe_filename += '.png'
    
    return f"processed_images/{instance.processing_job.user_image.user.id}/{safe_filename}"


# ==================== VENUE MODE CHOICES ====================

# Wedding Theme Choices (80+ themes)
WEDDING_THEMES = [
    # Classic Traditional Themes
    ('rustic', 'Rustic Farmhouse'),
    ('modern', 'Modern Contemporary'),
    ('vintage', 'Vintage Romance'),
    ('classic', 'Classic Traditional'),
    ('garden', 'Garden Natural'),
    ('beach', 'Beach Coastal'),
    ('industrial', 'Industrial Urban'),
    ('bohemian', 'Bohemian Chic'),
    ('glamorous', 'Glamorous Luxury'),
    ('tropical', 'Tropical Paradise'),
    ('fairy_tale', 'Fairy Tale Enchanted'),
    ('minimalist', 'Minimalist Clean'),
    ('romantic', 'Romantic Dreamy'),
    ('elegant', 'Elegant Sophisticated'),
    ('chic', 'Chic Contemporary'),
    ('timeless', 'Timeless Classic'),
    
    # Popular Style Variations
    ('country_barn', 'Country Barn'),
    ('art_deco', 'Art Deco Glamour'),
    ('scandinavian', 'Scandinavian Hygge'),
    ('mediterranean', 'Mediterranean'),
    ('prairie_wildflower', 'Prairie Wildflower'),
    
    # Seasonal Specific
    ('winter_wonderland', 'Winter Wonderland'),
    ('spring_fresh', 'Spring Fresh'),
    ('harvest_festival', 'Harvest Festival'),
    
    # Approach-Based
    ('whimsical', 'Whimsical Playful'),
    ('monochrome', 'Monochrome B&W'),
    ('statement_bold', 'Bold Statement'),
    ('soft_dreamy', 'Soft Dreamy'),
    ('luxury', 'Premium Luxury'),
    
    # Cultural & Traditional Themes
    ('japanese_zen', 'Japanese Zen'),
    ('chinese_dynasty', 'Chinese Dynasty'),
    ('indian_palace', 'Indian Palace'),
    ('korean_hanbok', 'Korean Hanbok'),
    ('thai_temple', 'Thai Temple'),
    ('scottish_highland', 'Scottish Highland'),
    ('french_chateau', 'French Château'),
    ('greek_island', 'Greek Island'),
    ('italian_villa', 'Italian Villa'),
    ('english_garden', 'English Garden'),
    ('mexican_fiesta', 'Mexican Fiesta'),
    ('spanish_hacienda', 'Spanish Hacienda'),
    ('brazilian_carnival', 'Brazilian Carnival'),
    ('argentine_tango', 'Argentine Tango'),
    ('moroccan_nights', 'Moroccan Nights'),
    ('arabian_desert', 'Arabian Desert'),
    ('african_safari', 'African Safari'),
    ('egyptian_royal', 'Egyptian Royal'),
    
    # Nature & Seasonal Themes
    ('spring_awakening', 'Spring Awakening'),
    ('summer_solstice', 'Summer Solstice'),
    ('autumn_harvest', 'Autumn Harvest'),
    ('forest_enchanted', 'Enchanted Forest'),
    ('desert_bloom', 'Desert Bloom'),
    ('ocean_waves', 'Ocean Waves'),
    ('mountain_vista', 'Mountain Vista'),
    
    # Modern & Contemporary Themes
    ('metropolitan_chic', 'Metropolitan Chic'),
    ('brooklyn_loft', 'Brooklyn Loft'),
    ('rooftop_garden', 'Rooftop Garden'),
    ('art_deco_glam', 'Art Deco Glam'),
    ('concrete_jungle', 'Concrete Jungle'),
    ('glass_house', 'Glass House'),
    
    # Vintage & Retro Themes
    ('1950s_diner', '1950s Diner Retro'),
    ('1960s_mod', '1960s Mod'),
    ('1970s_disco', '1970s Disco'),
    ('1980s_neon', '1980s Neon'),
    ('1990s_grunge', '1990s Grunge'),
    ('victorian_romance', 'Victorian Romance'),
    ('art_nouveau', 'Art Nouveau'),
    ('great_gatsby', 'Great Gatsby'),
    
    # N/A option (replaces use_pictured)
    ('na', 'N/A'),
]

SPACE_TYPES = [
    ('wedding_ceremony', 'Wedding Ceremony'),
    ('dance_floor', 'Dance Floor / Party Area'),
    ('dining_area', 'Reception Dining'),
    ('cocktail_hour', 'Cocktail Reception'),
    ('bridal_suite', 'Bridal Suite / Getting Ready'),
    ('entrance_area', 'Entrance / Welcome Area'),
    ('na', 'N/A'),
]


# ==================== PORTRAIT MODE CHOICES ====================

# Engagement Portrait - Settings (Combined from photo_theme + setting_type)
ENGAGEMENT_SETTINGS = [
    # Natural Outdoor Settings
    ('garden_park', 'Garden / Park'),
    ('beach_waterfront', 'Beach / Waterfront'),
    ('mountain_vista', 'Mountain / Vista'),
    ('forest_woods', 'Forest / Woods'),
    ('countryside_rural', 'Countryside / Rural'),
    ('lake_river', 'Lake / River'),
    ('desert_landscape', 'Desert Landscape'),
    ('meadow_field', 'Meadow / Field'),
    
    # Urban & City Settings
    ('urban_city', 'Urban / City Streets'),
    ('downtown_skyline', 'Downtown / Skyline'),
    ('historic_district', 'Historic District'),
    ('alleyway_brick', 'Alleyway / Brick Wall'),
    ('rooftop_terrace', 'Rooftop / Terrace'),
    ('bridge_overpass', 'Bridge / Overpass'),
    ('subway_station', 'Subway / Train Station'),
    ('industrial_district', 'Industrial District'),
    
    # Indoor & Cozy Settings
    ('home_living_room', 'Home / Living Room'),
    ('home_kitchen', 'Home / Kitchen'),
    ('bedroom_cozy', 'Bedroom / Cozy'),
    ('coffee_shop', 'Coffee Shop / Café'),
    ('bookstore_library', 'Bookstore / Library'),
    ('art_gallery', 'Art Gallery / Museum'),
    ('studio_indoor', 'Studio / Indoor'),
    ('restaurant_bar', 'Restaurant / Bar'),
    ('hotel_lobby', 'Hotel Lobby'),
    
    # Special & Unique Settings
    ('amusement_park', 'Amusement Park'),
    ('carnival_fair', 'Carnival / Fair'),
    ('farmers_market', 'Farmers Market'),
    ('vineyard_winery', 'Vineyard / Winery'),
    ('botanical_garden', 'Botanical Garden'),
    ('zoo_aquarium', 'Zoo / Aquarium'),
    ('sports_venue', 'Sports Venue / Stadium'),
    ('theater_concert_hall', 'Theater / Concert Hall'),
    ('historic_building', 'Historic Building / Landmark'),
    
    # Adventure & Travel Settings
    ('airport_terminal', 'Airport / Terminal'),
    ('train_platform', 'Train Platform'),
    ('road_trip', 'Road Trip / Highway'),
    ('camping_site', 'Camping Site'),
    ('ski_resort', 'Ski Resort / Slopes'),
    ('tropical_resort', 'Tropical Resort'),
    
    ('na', 'N/A'),
]

# Engagement Portrait - Activities (Expanded from pose_style)
ENGAGEMENT_ACTIVITIES = [
    # === ROMANTIC POSES ===
    ('romantic_embrace', 'Romantic Embrace'),
    ('forehead_kiss', 'Forehead Kiss'),
    ('nose_to_nose', 'Nose to Nose / Eskimo Kiss'),
    ('hand_kiss', 'Hand Kiss'),
    ('cheek_kiss', 'Cheek Kiss'),
    ('looking_into_eyes', 'Looking Into Each Other\'s Eyes'),
    ('tender_hold', 'Tender Hold / Cuddling'),
    ('back_hug', 'Back Hug / Embrace from Behind'),
    ('dip_kiss', 'Dip Kiss / Romantic Dip'),
    
    # === CANDID & JOYFUL ===
    ('candid_laughing', 'Candid Laughing / Natural Joy'),
    ('playful_fun', 'Playful & Fun / Silly Moment'),
    ('tickle_fight', 'Tickle Fight / Playful Wrestling'),
    ('piggyback_ride', 'Piggyback Ride'),
    ('twirling_spinning', 'Twirling / Spinning'),
    ('jumping_together', 'Jumping Together / Leap'),
    ('running_toward', 'Running Toward Camera / Each Other'),
    ('blowing_bubbles', 'Blowing Bubbles'),
    ('confetti_throw', 'Confetti Throw / Celebration'),
    
    # === WALKING & MOVEMENT ===
    ('walking_together', 'Walking Together Hand-in-Hand'),
    ('walking_arm_in_arm', 'Walking Arm in Arm'),
    ('walking_beach', 'Walking Along Beach / Shore'),
    ('strolling_city', 'Strolling Through City'),
    ('dancing_street', 'Dancing in the Street'),
    ('running_field', 'Running Through Field'),
    
    # === SITTING & INTIMATE ===
    ('sitting_intimate', 'Sitting Intimate / Close Together'),
    ('sitting_bench', 'Sitting on Bench'),
    ('sitting_blanket', 'Sitting on Blanket / Picnic'),
    ('sitting_steps', 'Sitting on Steps / Stairs'),
    ('sitting_dock', 'Sitting on Dock / Pier'),
    ('lying_grass', 'Lying in Grass / Field'),
    ('lying_bed', 'Lying on Bed / Cozy'),
    ('sitting_back_to_back', 'Sitting Back to Back'),
    
    # === CREATIVE & ARTISTIC ===
    ('silhouette_sunset', 'Silhouette at Sunset / Sunrise'),
    ('reflection_water', 'Reflection in Water'),
    ('mirror_reflection', 'Mirror Reflection / Glass'),
    ('through_window', 'Through Window / Glass'),
    ('framed_doorway', 'Framed by Doorway / Architecture'),
    ('with_balloons', 'Holding Balloons'),
    ('with_sparklers', 'Holding Sparklers / Fireworks'),
    ('umbrella_rain', 'Under Umbrella in Rain'),
    ('wrapped_blanket', 'Wrapped in Blanket Together'),
    
    # === FOOD & CULINARY ===
    ('cooking_together', 'Cooking Together'),
    ('baking_together', 'Baking Together / Making Dessert'),
    ('making_pizza', 'Making Pizza'),
    ('coffee_date', 'Coffee Date / Holding Mugs'),
    ('wine_tasting', 'Wine Tasting / Toast'),
    ('picnic_eating', 'Having Picnic / Eating Together'),
    ('feeding_each_other', 'Feeding Each Other'),
    ('breakfast_in_bed', 'Breakfast in Bed'),
    ('ice_cream_date', 'Ice Cream Date / Sharing'),
    ('farmers_market_shop', 'Shopping at Farmers Market'),
    
    # === SPORTS & ACTIVE ===
    ('hiking_trail', 'Hiking on Trail'),
    ('biking_together', 'Biking Together'),
    ('skiing', 'Skiing Together'),
    ('snowboarding', 'Snowboarding Together'),
    ('kayaking', 'Kayaking / Canoeing'),
    ('rock_climbing', 'Rock Climbing'),
    ('surfing', 'Surfing Together'),
    ('skateboarding', 'Skateboarding'),
    ('rollerblading', 'Rollerblading / Skating'),
    ('yoga_together', 'Doing Yoga Together'),
    ('running_jogging', 'Running / Jogging Together'),
    ('playing_frisbee', 'Playing Frisbee'),
    ('playing_catch', 'Playing Catch'),
    ('basketball_court', 'Playing Basketball'),
    ('soccer_field', 'Playing Soccer'),
    ('tennis_court', 'Playing Tennis'),
    ('golf_course', 'Golfing Together'),
    ('swimming_pool', 'Swimming / Pool'),
    ('beach_volleyball', 'Beach Volleyball'),
    
    # === CREATIVE & HOBBIES ===
    ('painting_together', 'Painting / Art Together'),
    ('pottery_making', 'Making Pottery / Ceramics'),
    ('photography_shoot', 'Taking Photos Together'),
    ('playing_music', 'Playing Music / Instruments'),
    ('singing_karaoke', 'Singing / Karaoke'),
    ('dancing_ballroom', 'Ballroom Dancing'),
    ('dancing_salsa', 'Salsa / Latin Dancing'),
    ('dancing_swing', 'Swing Dancing'),
    ('playing_board_game', 'Playing Board Game'),
    ('playing_video_games', 'Playing Video Games'),
    ('playing_cards', 'Playing Cards'),
    ('puzzle_together', 'Doing Puzzle Together'),
    ('reading_together', 'Reading Together / Books'),
    ('writing_together', 'Writing / Journaling'),
    ('crafting_diy', 'Crafting / DIY Project'),
    
    # === RELAXATION & LEISURE ===
    ('watching_sunset', 'Watching Sunset'),
    ('watching_sunrise', 'Watching Sunrise'),
    ('stargazing', 'Stargazing / Looking at Stars'),
    ('watching_movie', 'Watching Movie / TV'),
    ('lounging_couch', 'Lounging on Couch'),
    ('hammock_relaxing', 'Relaxing in Hammock'),
    ('hot_tub', 'In Hot Tub / Jacuzzi'),
    ('spa_treatment', 'Spa Treatment / Massage'),
    ('meditation', 'Meditating Together'),
    
    # === ANIMALS & PETS ===
    ('with_dog', 'With Dog / Pet Dog'),
    ('with_cat', 'With Cat / Pet Cat'),
    ('with_horse', 'With Horse / Horseback Riding'),
    ('feeding_ducks', 'Feeding Ducks / Birds'),
    ('at_petting_zoo', 'At Petting Zoo'),
    ('at_aquarium', 'At Aquarium / Viewing Tank'),
    
    # === SEASONAL ACTIVITIES ===
    ('pumpkin_patch', 'Pumpkin Patch / Picking Pumpkins'),
    ('apple_picking', 'Apple Picking / Orchard'),
    ('christmas_tree_lot', 'Christmas Tree Shopping'),
    ('decorating_tree', 'Decorating Christmas Tree'),
    ('building_snowman', 'Building Snowman'),
    ('snowball_fight', 'Snowball Fight'),
    ('fall_leaves', 'Playing in Fall Leaves'),
    ('spring_flowers', 'Picking Spring Flowers'),
    
    # === TRAVEL & ADVENTURE ===
    ('at_airport', 'At Airport / Traveling'),
    ('road_trip_car', 'Road Trip in Car'),
    ('on_boat', 'On Boat / Sailing'),
    ('hot_air_balloon', 'Hot Air Balloon Ride'),
    ('helicopter_ride', 'Helicopter Ride / View'),
    ('train_ride', 'Train Ride / Scenic Railway'),
    ('at_landmark', 'At Famous Landmark'),
    ('camping_tent', 'Camping / By Tent'),
    ('bonfire_campfire', 'By Bonfire / Campfire'),
    ('fishing_together', 'Fishing Together'),
    
    # === UNIQUE & SPECIAL ===
    ('at_concert', 'At Concert / Music Festival'),
    ('at_sports_game', 'At Sports Game / Stadium'),
    ('carnival_rides', 'On Carnival Rides'),
    ('roller_coaster', 'On Roller Coaster'),
    ('ferris_wheel', 'On Ferris Wheel'),
    ('go_kart_racing', 'Go-Kart Racing'),
    ('arcade_games', 'Playing Arcade Games'),
    ('bowling_alley', 'Bowling Together'),
    ('mini_golf', 'Playing Mini Golf'),
    ('laser_tag', 'Playing Laser Tag'),
    ('escape_room', 'Doing Escape Room'),
    ('scuba_diving', 'Scuba Diving'),
    ('snorkeling', 'Snorkeling Together'),
    ('zip_lining', 'Zip Lining'),
    ('bungee_jumping', 'Bungee Jumping'),
    ('skydiving', 'Skydiving Together'),
    
    # === FORMAL POSES ===
    ('formal_portrait', 'Formal Portrait / Traditional'),
    ('formal_standing', 'Formal Standing Pose'),
    ('formal_sitting', 'Formal Sitting Pose'),
]

# Wedding Portrait - Moments/Scenes (Combined photo_theme + pose_style)
WEDDING_MOMENTS = [
    # === CEREMONY MOMENTS ===
    ('walking_aisle', 'Walking Down the Aisle'),
    ('first_look', 'First Look / Reveal'),
    ('exchanging_vows', 'Exchanging Vows'),
    ('exchanging_rings', 'Exchanging Rings'),
    ('the_kiss', 'The First Kiss'),
    ('just_married', 'Just Married / Recessional Walk'),
    ('unity_ceremony', 'Unity Ceremony (Candle/Sand)'),
    ('signing_certificate', 'Signing Marriage Certificate'),
    ('with_officiant', 'With Officiant'),
    
    # === RECEPTION MOMENTS ===
    ('grand_entrance', 'Grand Entrance / Announced'),
    ('first_dance', 'First Dance'),
    ('father_daughter_dance', 'Father-Daughter Dance'),
    ('mother_son_dance', 'Mother-Son Dance'),
    ('cake_cutting', 'Cake Cutting'),
    ('cake_feeding', 'Feeding Each Other Cake'),
    ('toasts_speeches', 'Toasts & Speeches'),
    ('bouquet_toss', 'Bouquet Toss'),
    ('garter_toss', 'Garter Toss'),
    ('last_dance', 'Last Dance'),
    ('send_off', 'Send Off / Exit'),
    
    # === COUPLE PORTRAITS ===
    ('formal_portrait', 'Formal Portrait / Traditional'),
    ('romantic_embrace', 'Romantic Embrace / Holding Close'),
    ('forehead_kiss', 'Forehead Kiss / Tender Moment'),
    ('the_dip_kiss', 'The Dip Kiss / Dramatic'),
    ('holding_hands', 'Holding Hands / Walking'),
    ('looking_at_each_other', 'Looking at Each Other / Gazing'),
    ('laughing_together', 'Laughing Together / Candid Joy'),
    ('private_moment', 'Private Moment / Intimate'),
    ('silhouette_sunset', 'Silhouette at Sunset'),
    ('dramatic_lighting', 'Dramatic Lighting / Editorial'),
    ('walking_together', 'Walking Together / Strolling'),
    ('dancing_alone', 'Dancing Alone Together'),
    
    # === GETTING READY ===
    ('bride_getting_ready', 'Bride Getting Ready / Preparation'),
    ('groom_getting_ready', 'Groom Getting Ready / Preparation'),
    ('dress_detail', 'Wedding Dress Details'),
    ('putting_on_dress', 'Putting On Wedding Dress'),
    ('veil_placement', 'Veil Placement / Adjustment'),
    ('tying_tie', 'Tying Tie / Bowtie'),
    ('putting_on_shoes', 'Putting On Shoes'),
    ('perfume_cologne', 'Applying Perfume / Cologne'),
    ('hair_makeup', 'Hair & Makeup Session'),
    ('looking_in_mirror', 'Looking in Mirror / Reflection'),
    ('with_wedding_party_prep', 'With Wedding Party / Getting Ready'),
    
    # === BRIDAL PARTY ===
    ('full_bridal_party', 'Full Bridal Party Group'),
    ('bridesmaids_group', 'Bridesmaids Group'),
    ('groomsmen_group', 'Groomsmen Group'),
    ('bride_with_bridesmaids', 'Bride with Bridesmaids'),
    ('groom_with_groomsmen', 'Groom with Groomsmen'),
    ('flower_girl', 'Flower Girl / Ring Bearer'),
    ('bridal_party_fun', 'Bridal Party Fun / Playful'),
    ('bridesmaids_helping', 'Bridesmaids Helping Bride'),
    ('groomsmen_fun', 'Groomsmen Fun / Candid'),
    
    # === FAMILY MOMENTS ===
    ('with_parents', 'With Parents / Both Sets'),
    ('bride_with_dad', 'Bride with Father'),
    ('bride_with_mom', 'Bride with Mother'),
    ('groom_with_dad', 'Groom with Father'),
    ('groom_with_mom', 'Groom with Mother'),
    ('with_grandparents', 'With Grandparents'),
    ('with_siblings', 'With Siblings'),
    ('family_group', 'Family Group Photo'),
    ('three_generations', 'Three Generations'),
    
    # === DETAIL SHOTS ===
    ('rings_detail', 'Wedding Rings Detail'),
    ('bouquet_detail', 'Bouquet Detail / Close-up'),
    ('dress_hanging', 'Dress Hanging / Display'),
    ('shoes_accessories', 'Shoes & Accessories'),
    ('invitation_suite', 'Invitation Suite / Stationery'),
    ('corsage_boutonniere', 'Corsage & Boutonniere'),
    ('jewelry_details', 'Jewelry & Details'),
    
    # === CREATIVE & ARTISTIC ===
    ('veil_wind', 'Veil Blowing in Wind'),
    ('dress_twirl', 'Dress Twirl / Spinning'),
    ('through_veil', 'Through Veil / Sheer'),
    ('reflection_shot', 'Reflection / Mirror/Water'),
    ('from_above', 'From Above / Drone View'),
    ('from_behind', 'From Behind / Over Shoulder'),
    ('artistic_blur', 'Artistic Blur / Motion'),
    ('double_exposure', 'Double Exposure / Artistic'),
    
    # === VENUE & ATMOSPHERE ===
    ('venue_exterior', 'Venue Exterior / Arrival'),
    ('venue_interior', 'Venue Interior / Decorated'),
    ('ceremony_setup', 'Ceremony Setup / Before'),
    ('reception_setup', 'Reception Setup / Tablescape'),
    ('guest_candids', 'Guest Candids / Mingling'),
    ('dancing_guests', 'Guests Dancing / Party'),
    ('cocktail_hour', 'Cocktail Hour / Socializing'),
    
    # === SPECIAL MOMENTS ===
    ('sparkler_exit', 'Sparkler Exit / Send Off'),
    ('confetti_toss', 'Confetti Toss / Celebration'),
    ('champagne_toast', 'Champagne Toast'),
    ('champagne_pop', 'Champagne Pop / Spray'),
    ('signing_guest_book', 'Signing Guest Book'),
    ('reading_cards', 'Reading Cards / Notes'),
    ('emotional_moment', 'Emotional Moment / Tears of Joy'),
    ('surprise_moment', 'Surprise Moment'),
    
    # === CULTURAL & TRADITIONAL ===
    ('cultural_ceremony', 'Cultural Ceremony / Ritual'),
    ('traditional_dance', 'Traditional Dance / Cultural'),
    ('blessing_ceremony', 'Blessing Ceremony'),
    ('tea_ceremony', 'Tea Ceremony'),
    ('handfasting', 'Handfasting Ceremony'),
    ('breaking_glass', 'Breaking Glass / Tradition'),
    
    # === SOLO SHOTS ===
    ('bride_solo_portrait', 'Bride Solo Portrait'),
    ('groom_solo_portrait', 'Groom Solo Portrait'),
    ('bride_with_bouquet', 'Bride with Bouquet'),
    ('groom_in_venue', 'Groom in Venue'),
]

# Wedding Portrait - Settings (Location where portrait is taken)
WEDDING_SETTINGS = [
    # Ceremony & Reception Venues
    ('ceremony_site', 'Ceremony Site / Altar'),
    ('reception_venue', 'Reception Venue / Hall'),
    ('dance_floor', 'Dance Floor'),
    ('sweetheart_table', 'Sweetheart Table'),
    ('guest_tables', 'Guest Tables / Reception'),
    ('cocktail_area', 'Cocktail Hour Area'),
    ('entrance_lobby', 'Entrance / Lobby'),
    
    # Indoor Locations
    ('church_chapel', 'Church / Chapel'),
    ('ballroom', 'Ballroom / Grand Hall'),
    ('barn_rustic', 'Barn / Rustic Venue'),
    ('hotel_interior', 'Hotel Interior'),
    ('mansion_estate', 'Mansion / Estate'),
    ('loft_industrial', 'Loft / Industrial Space'),
    ('museum_gallery', 'Museum / Gallery'),
    ('restaurant_private', 'Restaurant / Private Room'),
    
    # Outdoor Locations
    ('garden_venue', 'Garden Venue'),
    ('park_outdoor', 'Park / Outdoor'),
    ('beach_waterfront', 'Beach / Waterfront'),
    ('vineyard_winery', 'Vineyard / Winery'),
    ('countryside_rural', 'Countryside / Rural'),
    ('mountain_scenic', 'Mountain / Scenic Vista'),
    ('forest_woods', 'Forest / Woods'),
    ('rooftop_terrace', 'Rooftop / Terrace'),
    ('courtyard_patio', 'Courtyard / Patio'),
    
    # Getting Ready Locations
    ('bridal_suite', 'Bridal Suite / Room'),
    ('groom_suite', 'Groom Suite / Room'),
    ('hotel_room', 'Hotel Room'),
    ('home_residence', 'Home / Private Residence'),
    
    # Unique Venues
    ('historic_building', 'Historic Building / Landmark'),
    ('castle_palace', 'Castle / Palace'),
    ('yacht_boat', 'Yacht / Boat'),
    ('tent_pavilion', 'Tent / Pavilion'),
    ('greenhouse', 'Greenhouse / Conservatory'),
    
    ('na', 'N/A'),
]

# Attire for Both Engagement & Wedding (Optional field)
ATTIRE_STYLES = [
    # Wedding Attire
    ('traditional_formal', 'Traditional Wedding Attire'),
    ('modern_chic_wedding', 'Modern Chic Wedding'),
    ('casual_elegant_wedding', 'Casual Elegant Wedding'),
    ('bohemian_wedding', 'Bohemian Wedding Style'),
    ('vintage_wedding', 'Vintage Wedding Style'),
    ('cultural_traditional', 'Cultural Traditional'),
    
    # Engagement Attire
    ('formal_elegant', 'Formal Elegant'),
    ('modern_chic', 'Modern Chic / Fashionable'),
    ('casual_elegant', 'Casual Elegant'),
    ('cozy_casual', 'Cozy Casual / Comfortable'),
    ('bohemian', 'Bohemian Style'),
    ('vintage_inspired', 'Vintage Inspired'),
    ('sporty_athletic', 'Sporty / Athletic Wear'),
    ('business_casual', 'Business Casual'),
    ('seasonal_appropriate', 'Seasonal Appropriate'),
    
    ('na', 'N/A'),
]


# ==================== SHARED CHOICES FOR ALL MODES ====================

# Composition / Camera Angles (NEW - Photographer's Perspective)
COMPOSITION_CHOICES = [
    # Standard Framing
    ('portrait_closeup', 'Portrait Close-Up / Headshot'),
    ('medium_shot', 'Medium Shot / Waist Up'),
    ('full_body', 'Full Body / Head to Toe'),
    ('three_quarter', 'Three-Quarter Length'),
    ('cowboy_shot', 'Cowboy Shot / Mid-Thigh Up'),
    
    # Environmental
    ('wide_environmental', 'Wide Environmental / Show Setting'),
    ('tight_intimate', 'Tight Intimate / Close Framing'),
    ('negative_space', 'Negative Space / Minimalist'),
    
    # Angles & Perspectives
    ('eye_level', 'Eye Level / Straight On'),
    ('high_angle', 'High Angle / Looking Down'),
    ('low_angle', 'Low Angle / Looking Up'),
    ('dutch_angle', 'Dutch Angle / Tilted'),
    ('birds_eye', 'Bird\'s Eye View / Directly Above'),
    ('worm_eye', 'Worm\'s Eye View / Ground Level Up'),
    
    # Drone & Aerial
    ('drone_overhead', 'Drone Overhead / Aerial View'),
    ('drone_high_wide', 'Drone High & Wide / Landscape'),
    ('drone_low_following', 'Drone Low Following / Tracking'),
    ('drone_orbit', 'Drone Orbit / Circling'),
    
    # Creative Composition
    ('rule_of_thirds', 'Rule of Thirds'),
    ('centered_symmetrical', 'Centered Symmetrical'),
    ('leading_lines', 'Leading Lines / Perspective'),
    ('framing_natural', 'Natural Framing / Through Objects'),
    ('foreground_interest', 'Foreground Interest / Depth'),
    ('silhouette', 'Silhouette / Backlit'),
    ('reflection', 'Reflection / Mirror/Water'),
    ('through_window', 'Through Window / Glass'),
    ('doorway_frame', 'Doorway / Architectural Frame'),
    ('over_shoulder', 'Over the Shoulder'),
    ('between_elements', 'Between Elements / Peek Through'),
    
    # Movement
    ('walking_toward', 'Walking Toward Camera'),
    ('walking_away', 'Walking Away / Departure'),
    ('motion_blur', 'Motion Blur / Movement'),
    ('frozen_action', 'Frozen Action / Sharp'),
    
    ('na', 'N/A'),
]

# Emotional Tone / Mood (NEW)
EMOTIONAL_TONE_CHOICES = [
    # Positive & Joyful
    ('joyful_happy', 'Joyful & Happy'),
    ('romantic_loving', 'Romantic & Loving'),
    ('playful_fun', 'Playful & Fun'),
    ('celebratory', 'Celebratory / Festive'),
    ('intimate_tender', 'Intimate & Tender'),
    ('passionate', 'Passionate / Intense'),
    ('serene_peaceful', 'Serene & Peaceful'),
    ('elegant_sophisticated', 'Elegant & Sophisticated'),
    
    # Candid & Natural
    ('candid_natural', 'Candid & Natural'),
    ('relaxed_comfortable', 'Relaxed & Comfortable'),
    ('authentic_genuine', 'Authentic & Genuine'),
    ('spontaneous', 'Spontaneous / In-the-Moment'),
    
    # Emotional & Meaningful
    ('emotional_touching', 'Emotional & Touching'),
    ('nostalgic', 'Nostalgic / Sentimental'),
    ('dreamy_ethereal', 'Dreamy & Ethereal'),
    ('magical_enchanted', 'Magical & Enchanted'),
    
    # Energetic & Dynamic
    ('energetic_vibrant', 'Energetic & Vibrant'),
    ('adventurous', 'Adventurous / Bold'),
    ('dynamic_action', 'Dynamic / Action-Packed'),
    
    # Artistic & Moody
    ('dramatic_striking', 'Dramatic & Striking'),
    ('moody_atmospheric', 'Moody & Atmospheric'),
    ('artistic_editorial', 'Artistic / Editorial'),
    ('vintage_timeless', 'Vintage & Timeless'),
    ('cinematic', 'Cinematic / Film-Like'),
    
    ('na', 'N/A'),
]

# Seasons
SEASONS = [
    ('spring', 'Spring'),
    ('summer', 'Summer'),
    ('fall', 'Fall / Autumn'),
    ('winter', 'Winter'),
    ('na', 'N/A'),
]

# Lighting Moods
LIGHTING_MOODS = [
    ('romantic', 'Romantic Warm'),
    ('bright', 'Bright Cheerful'),
    ('dim', 'Dim Intimate'),
    ('dramatic', 'Dramatic Contrast'),
    ('natural', 'Natural Daylight'),
    ('golden', 'Golden Hour'),
    ('dusk', 'Dusk / Twilight'),
    ('dawn', 'Dawn / Sunrise'),
    ('na', 'N/A'),
]

# Color Schemes
COLOR_SCHEMES = [
    # Primary Colors
    ('red', 'Red'),
    ('pink', 'Pink'),
    ('coral', 'Coral'),
    ('orange', 'Orange'),
    ('yellow', 'Yellow'),
    ('green', 'Green'),
    ('blue', 'Blue'),
    ('purple', 'Purple'),
    ('white', 'White'),
    ('black', 'Black'),
    
    # Pastels
    ('pastel_pink', 'Pastel Pink'),
    ('pastel_peach', 'Pastel Peach'),
    ('pastel_lavender', 'Pastel Lavender'),
    ('pastel_mint', 'Pastel Mint'),
    ('pastel_yellow', 'Pastel Yellow'),
    ('pastel_blue', 'Pastel Blue'),
    
    # Metallics
    ('gold', 'Gold'),
    ('silver', 'Silver'),
    ('copper', 'Copper / Rose Gold'),
    ('bronze', 'Bronze'),
    
    # Combinations
    ('blush_gold', 'Blush & Gold'),
    ('navy_gold', 'Navy & Gold'),
    ('burgundy_gold', 'Burgundy & Gold'),
    ('sage_gold', 'Sage Green & Gold'),
    ('dusty_blue_pink', 'Dusty Blue & Pink'),
    ('champagne_ivory', 'Champagne & Ivory'),
    ('black_white', 'Black & White'),
    ('red_white', 'Red & White'),
    ('blue_white', 'Blue & White'),
    
    # Naturals
    ('earth_tones', 'Earth Tones'),
    ('neutrals', 'Neutrals / Beige'),
    ('greens_natural', 'Greens / Natural'),
    ('browns_wood', 'Browns / Wood Tones'),
    
    # Moods
    ('jewel_tones', 'Jewel Tones / Rich'),
    ('vibrant_bold', 'Vibrant & Bold'),
    ('muted_soft', 'Muted & Soft'),
    ('monochrome', 'Monochrome'),
    
    ('na', 'N/A'),
]


# ==================== MODELS ====================

class UserImage(models.Model):
    """User uploaded images with type classification"""
    
    IMAGE_TYPE_CHOICES = [
        ('venue', 'Venue/Space Photo'),
        ('face', 'Face Photo'),
        ('reference', 'Reference Photo'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=user_image_upload_path)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    
    # Image classification
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES, default='venue')
    
    # Venue/reference metadata (optional)
    venue_name = models.CharField(max_length=255, blank=True, null=True)
    venue_description = models.TextField(blank=True, null=True)
    
    # Image metadata
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.original_filename}"
    
    def save(self, *args, **kwargs):
        if self.image and not self.width:
            try:
                img = Image.open(self.image)
                self.width, self.height = img.size
                self.file_size = self.image.size
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                self.width = 512
                self.height = 512
                self.file_size = getattr(self.image, 'size', 0) or 0
        
        super().save(*args, **kwargs)


class FavoriteUpload(models.Model):
    """Favorite user uploads (e.g., favorite faces for reuse)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_uploads')
    image = models.ForeignKey(UserImage, on_delete=models.CASCADE)
    label = models.CharField(max_length=100, blank=True, help_text="e.g., 'Bride', 'Groom', 'Mom'")
    times_used = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'image']
        ordering = ['-last_used', '-created_at']
        verbose_name = 'Favorite Upload'
        verbose_name_plural = 'Favorite Uploads'
    
    def __str__(self):
        return f"{self.user.username} ⭐ {self.image.original_filename}"
    
    def increment_usage(self):
        """Increment usage counter and update last used timestamp"""
        self.times_used += 1
        self.last_used = timezone.now()
        self.save(update_fields=['times_used', 'last_used'])


class ImageProcessingJob(models.Model):
    """Processing jobs - supports venue, wedding portrait, and engagement portrait modes"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    STUDIO_MODES = [
        ('venue', 'Venue Design'),
        ('portrait_wedding', 'Wedding Portrait'),
        ('portrait_engagement', 'Engagement Portrait'),
    ]
    
    # Primary image (main input)
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, related_name='processing_jobs')
    
    # Studio mode selection
    studio_mode = models.CharField(max_length=20, choices=STUDIO_MODES, default='venue')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # === VENUE MODE FIELDS ===
    wedding_theme = models.CharField(max_length=50, choices=WEDDING_THEMES, blank=True)
    space_type = models.CharField(max_length=20, choices=SPACE_TYPES, blank=True)
    
    # === ENGAGEMENT PORTRAIT FIELDS ===
    engagement_setting = models.CharField(max_length=50, choices=ENGAGEMENT_SETTINGS, blank=True)
    engagement_activity = models.CharField(max_length=50, choices=ENGAGEMENT_ACTIVITIES, blank=True)
    
    # === WEDDING PORTRAIT FIELDS ===
    wedding_moment = models.CharField(max_length=50, choices=WEDDING_MOMENTS, blank=True)
    wedding_setting = models.CharField(max_length=50, choices=WEDDING_SETTINGS, blank=True)
    
    # === SHARED PORTRAIT FIELD ===
    attire_style = models.CharField(max_length=50, choices=ATTIRE_STYLES, blank=True)
    
    # === NEW SHARED FIELDS FOR ALL PORTRAIT MODES ===
    composition = models.CharField(max_length=50, choices=COMPOSITION_CHOICES, blank=True)
    emotional_tone = models.CharField(max_length=50, choices=EMOTIONAL_TONE_CHOICES, blank=True)
    
    # === EXISTING SHARED OPTIONAL FIELDS ===
    season = models.CharField(max_length=20, choices=SEASONS, blank=True)
    lighting_mood = models.CharField(max_length=20, choices=LIGHTING_MOODS, blank=True)
    color_scheme = models.CharField(max_length=30, choices=COLOR_SCHEMES, blank=True)
    
    # Custom prompt (overrides guided mode)
    custom_prompt = models.TextField(blank=True, null=True)
    
    # User instructions (appended to all prompts)
    user_instructions = models.TextField(blank=True, null=True)
    
    # Generated final prompt (cached)
    generated_prompt = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        mode_display = dict(self.STUDIO_MODES).get(self.studio_mode, self.studio_mode)
        return f"Job {self.id} - {mode_display} ({self.status})"
    
    @property
    def is_venue_mode(self):
        return self.studio_mode == 'venue'
    
    @property
    def is_portrait_mode(self):
        return self.studio_mode.startswith('portrait_')
    
    @property
    def mode_display(self):
        return dict(self.STUDIO_MODES).get(self.studio_mode, self.studio_mode)


class JobReferenceImage(models.Model):
    """Links multiple reference images to a single processing job (up to 3 images total)"""
    job = models.ForeignKey(
        ImageProcessingJob, 
        on_delete=models.CASCADE,
        related_name='reference_images'
    )
    reference_image = models.ForeignKey(
        UserImage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    order = models.IntegerField(default=0, help_text="Order of reference images")
    
    class Meta:
        ordering = ['order']
        unique_together = ['job', 'reference_image']
    
    def __str__(self):
        return f"Job {self.job.id} - Reference {self.order + 1}"


class ProcessedImage(models.Model):
    """Processed images from Gemini"""
    processing_job = models.ForeignKey(ImageProcessingJob, on_delete=models.CASCADE, related_name='processed_images')
    processed_image = models.ImageField(upload_to=processed_image_upload_path)
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    
    # Gemini generation metadata
    gemini_model = models.CharField(max_length=50, default='gemini-2.5-flash-image-preview')
    finish_reason = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.processed_image and not self.width:
            try:
                img = Image.open(self.processed_image)
                self.width, self.height = img.size
                self.file_size = self.processed_image.size
            except Exception as e:
                logger.error(f"Error getting image dimensions: {str(e)}")
                self.width = 512
                self.height = 512
                self.file_size = getattr(self.processed_image, 'size', 0) or 0
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.processing_job.mode_display} - Output"


# Collections and Favorites for Processed Images
class Collection(models.Model):
    """User collections for organizing designs"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    @classmethod
    def get_or_create_default(cls, user):
        collection, created = cls.objects.get_or_create(
            user=user,
            is_default=True,
            defaults={
                'name': 'My Designs',
                'description': 'Your saved designs',
            }
        )
        return collection
    
    @property
    def item_count(self):
        return self.items.count()
    
    @property
    def thumbnail(self):
        first_item = self.items.first()
        if first_item:
            if first_item.processed_image:
                return first_item.processed_image.processed_image
            else:
                return first_item.user_image.thumbnail or first_item.user_image.image
        return None


class CollectionItem(models.Model):
    """Items within a collection"""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='items')
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE, null=True, blank=True)
    processed_image = models.ForeignKey('ProcessedImage', on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True, null=True, help_text="Personal notes about this design")
    order = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-added_at']
        unique_together = [
            ['collection', 'user_image'],
            ['collection', 'processed_image']
        ]
    
    def __str__(self):
        if self.processed_image:
            return f"{self.collection.name} - {self.processed_image}"
        else:
            return f"{self.collection.name} - {self.user_image.original_filename}"


class Favorite(models.Model):
    """Favorites for processed images (heart icon)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    processed_image = models.ForeignKey('ProcessedImage', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'processed_image']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} ♥ {self.processed_image}"