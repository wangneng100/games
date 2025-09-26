import pygame

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)

# Player settings
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 32
PLAYER_ACC = 0.5
GROUND_FRICTION = -0.1
AIR_FRICTION = -0.05
PLAYER_MAX_SPEED = 5
JUMP_STRENGTH = -12
GRAVITY = 0.7




# Bow settings
BOW_SIZE = 2.5
BOW_OFFSET = 50
BOW_TILT_ANGLE = -45

# Knife settings
KNIFE_SCALE = 0.06  # Even tinier knife
KNIFE_OFFSET = 12  # Very close to player
KNIFE_STAB_EXTENSION = 24  # Extension during stab (3x)
KNIFE_STAB_DURATION = 0.2  # Total stab duration
KNIFE_STAB_FORWARD_RATIO = 1/6  # Quick forward (1 part of 6 total)
KNIFE_STAB_RETURN_RATIO = 5/6   # Slow return (5 parts of 6 total)
KNIFE_ATTACK_COOLDOWN = 0  # Attack cooldown (4.4 clicks per second)
KNIFE_HITBOX_SIZE = 6  # Smaller hitbox
KNIFE_DAMAGE_MULTIPLIER = 1.5  # Decent damage for melee
KNIFE_RIGHT_CLICK_MULTIPLIER = 1.2  # Right click does 1x damage/knockback

# Arrow settings
ARROW_BASE_SPEED = 8  # Minimum arrow speed
ARROW_MAX_SPEED = 24  # Maximum arrow speed when fully charged
ARROW_GRAVITY = 0.2
ARROW_SIZE = 1.0
ARROW_BLUE_TINT = (100, 150, 255)  # Blue tint color

# Bow charging settings
BOW_CHARGE_TIME = 1.1  # Seconds to reach full charge
BOW_SHAKE_INTENSITY = 3  # Maximum shake offset in pixels
BOW_SHAKE_FREQUENCY = 0.2  # How fast the shake oscillates
BOW_ARROW_OFFSET = 30  # How far back the arrow is drawn when charging
BOW_ARROW_SCALE = 1.3  # Scale of the arrow when held in bow (much bigger)

# Trail settings
TRAIL_LENGTH = 12  # Number of trail segments
TRAIL_FADE_RATE = 0.8  # How quickly trail fades (0.0 to 1.0)
ARROW_TRAIL_COLOR = (135, 206, 235)  # Sky blue trail for arrows
TRAIL_WIDTH = 6  # Base width of trail lines

# Hotbar settings
HOTBAR_SLOTS = 3  # Simplified for bow-only game
HOTBAR_SLOT_SIZE = 48  # Smaller for horizontal layout
HOTBAR_PADDING = 4
HOTBAR_X = 20  # Top left of screen
HOTBAR_Y = 20  # Top of screen
HOTBAR_BACKGROUND_COLOR = (40, 40, 40, 180)  # Dark gray with transparency
HOTBAR_BORDER_COLOR = (100, 100, 100)
HOTBAR_SELECTED_COLOR = (255, 255, 255)
HOTBAR_KEYS = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, 
               pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0, pygame.K_MINUS, pygame.K_EQUALS]

# Dash settings
DASH_INITIAL_SPEED = 20  # Initial dash velocity (higher for quick start)
DASH_DECELERATION = 0.85  # Speed multiplier per frame (creates deceleration)
DASH_DURATION = 0.15  # How long dash lasts in seconds (quicker)
DASH_COOLDOWN = 0.8  # Cooldown between dashes in seconds
DASH_ROLL_SPEED = 8  # How fast the player rotates during dash

# Knockback settings
BASE_KNOCKBACK_FORCE = 4  # Base knockback force
KNOCKBACK_DECELERATION = 0.88  # More realistic knockback slowdown
KNOCKBACK_MIN_DURATION = 0.1  # Minimum knockback time
KNOCKBACK_MAX_DURATION = 0.5  # Maximum knockback time
ARROW_HITBOX_SIZE = 8  # Smaller hitbox for arrows  
ARROW_KNOCKBACK_MULTIPLIER = 1.2  # More realistic arrow knockback
ARROW_PIERCE_COUNT = 1  # Number of blocks arrows can pierce through

# Hit effect settings
HIT_FLASH_DURATION = 0.15  # How long the red flash lasts
HIT_FLASH_COLOR = (255, 100, 100)  # Red flash color
DASH_INVINCIBILITY = True  # Player is invincible while dashing
ENEMY_COLLISION_KNOCKBACK_RATIO = 0.0  # Enemy takes no knockback when hitting player
COLLISION_SEPARATION_FORCE = 2  # Force to separate overlapping entities

# Particle system settings
PARTICLE_COUNT = 8  # Number of particles per explosion
PARTICLE_SPEED_MIN = 2  # Minimum particle speed
PARTICLE_SPEED_MAX = 6  # Maximum particle speed
PARTICLE_LIFETIME = 1.0  # How long particles last in seconds
PARTICLE_SIZE = 3  # Size of particles
ARROW_PARTICLE_COLOR = (100, 150, 255)  # Blue particles for arrows
DASH_TRAIL_COLOR = (255, 255, 255)  # White trail for dash
DASH_TRAIL_LENGTH = 8  # Number of trail segments for dash
DASH_KEY = pygame.K_SPACE  # Space key for dash



# Enemy settings
ENEMY_ATTACK_COOLDOWN = 1.5  # Seconds between enemy attacks
ENEMY_ATTACK_RANGE = 50  # How close enemy needs to be to attack
ENEMY_ATTACK_KNOCKBACK_FORCE = 6  # Force of enemy attacks

# Improved collision settings
COLLISION_SUBSTEPS = 1  # Reduced for performance - single step collision
WALL_PENETRATION_THRESHOLD = 3  # Slightly more tolerant for smoother movement
PLAYER_KNOCKBACK_DISABLED = True  # Disable player knockback for better feel

# World settings
TILE_SIZE = 40