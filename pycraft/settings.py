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


# Staff settings
STAFF_TILT_ANGLE = -45
STAFF_SIZE = 3
STAFF_OFFSET = 60

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

# Trail settings
TRAIL_LENGTH = 12  # Number of trail segments
TRAIL_FADE_RATE = 0.8  # How quickly trail fades (0.0 to 1.0)
ARROW_TRAIL_COLOR = (135, 206, 235)  # Sky blue trail for arrows
TRAIL_WIDTH = 6  # Base width of trail lines

# Hotbar settings
HOTBAR_SLOTS = 12
HOTBAR_SLOT_SIZE = 48  # Smaller for horizontal layout
HOTBAR_PADDING = 4
HOTBAR_X = 20  # Top left of screen
HOTBAR_Y = 20  # Top of screen
HOTBAR_BACKGROUND_COLOR = (40, 40, 40, 180)  # Dark gray with transparency
HOTBAR_BORDER_COLOR = (100, 100, 100)
HOTBAR_SELECTED_COLOR = (255, 255, 255)
HOTBAR_KEYS = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, 
               pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0, pygame.K_MINUS, pygame.K_EQUALS]

# World settings
TILE_SIZE = 40