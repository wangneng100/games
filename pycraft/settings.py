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

# Health tank settings
HEALTH_TANK_WIDTH = 160  # Width of health tank
HEALTH_TANK_HEIGHT = 20  # Height of health tank
HEALTH_TANK_X = 20  # Same X as hotbar
HEALTH_TANK_Y = 80  # Below hotbar (hotbar height + padding)
HEALTH_TANK_BORDER_COLOR = (100, 100, 100)  # Gray border
HEALTH_TANK_BACKGROUND_COLOR = (40, 40, 40)  # Dark background
HEALTH_BLOOD_COLOR = (30, 179, 38)  # Blood red
HEALTH_VOID_COLOR = (255, 255, 255)  # White for void damage
HEALTH_DRAIN_SPEED = 1000.0  # How fast blood drains when damaged (20x faster)
HEALTH_FLUID_GRAVITY = 400.0  # How fast fluid settles (20x faster)
HEALTH_FLUID_VISCOSITY = 0.015  # Even lower viscosity for instant flow (20x faster)
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
ARROW_HITBOX_SIZE = 16  # Better hitbox for arrows (doubled)  
ARROW_KNOCKBACK_MULTIPLIER = 1.2  # More realistic arrow knockback
ARROW_PIERCE_COUNT = 3  # Number of blocks arrows can pierce through (increased!)

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
ENEMY_ATTACK_RANGE = 80  # How close enemy needs to be to attack
ENEMY_ATTACK_KNOCKBACK_FORCE = 6  # Force of enemy attacks
ENEMY_STAFF_SCALE = 3.0  # 3x bigger staff for dramatic attacks
ENEMY_STAFF_DAMAGE = 20  # Staff damage per hit
ENEMY_STAFF_REACH = 100  # Long reach for large staff
ENEMY_STAFF_SPIN_SPEED = 20  # Degrees per frame during spin
ENEMY_STAFF_CHARGE_TIME = 0.5  # Time to charge back before stab
ENEMY_STAFF_STAB_SPEED = 12  # Speed of forward dash during stab
ENEMY_STAFF_JUMP_FORCE = -8  # Upward force when jumping back
ENEMY_STAFF_BACK_SPEED = 15  # Horizontal speed when jumping back
ENEMY_STAFF_ROTATION_OFFSET = -45  # Default rotation offset (45 degrees to the left)
ENEMY_ROTATIONAL_OFFSET = -45  # Additional rotational offset for weapon facing
ENEMY_GLOW_COLOR = (100, 150, 255)  # Blue glow color

# Improved collision settings
COLLISION_SUBSTEPS = 1  # Reduced for performance - single step collision
WALL_PENETRATION_THRESHOLD = 3  # Slightly more tolerant for smoother movement
PLAYER_KNOCKBACK_DISABLED = True  # Disable player knockback for better feel

# World settings
TILE_SIZE = 40