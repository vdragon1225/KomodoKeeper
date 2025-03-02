import pygame

# Screen settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Fly boundaries
FLY_BOUNDARY_BOTTOM = 3 * SCREEN_HEIGHT // 4  # Flies can't go below this y-coordinate
FLY_BOUNDARY_TOP = SCREEN_HEIGHT // 6 + 30  # Increased to keep flies away from top boxes

# Box settings
BOX_SIZE = 50
BOX_COLORS = ['Red', 'Blue', 'Green', 'Purple']  # Colors for food, water, play, sleep
BOX_SPACING = SCREEN_WIDTH // 5
BOX_Y = SCREEN_HEIGHT // 8 - BOX_SIZE // 2  # Position closer to the top

# Font settings
TEST_FONT = None
LARGE_FONT = None
TITLE_FONT = None

# Background settings
BACKGROUND_SCROLL_SPEED = 1  # Pixels per frame - adjust for faster/slower scrolling

# Asset paths (could be expanded with all image paths)
ASSET_PATHS = {
    'background': 'graphics/background.png',
    'logo': 'graphics/startPageLogo.png',
    'fly': 'graphics/fly.png'
}

# Animation timing settings
ANIMATION_SPEED = 0.1
EATING_DURATION = 500
EGG_ANIMATION_DELAY = 1500
HUNGER_UPDATE_INTERVAL = 1000  # Base interval in ms
AGE_INCREMENT_INTERVAL = 3000  # Time between age increments in ms