import os

# Color definitions (RGBA)
WHITE = (255, 255, 255, 1)
BLACK = (0, 0, 0, 1)

RED = (255, 0, 0, 1)
GREEN = (0, 255, 0, 1)
PURPLE = (255, 0, 255, 1)

# Screen and sprite dimensions
SCREEN_SIZE = (800, 608)
SPRITE_SIZE = (32, 32)

# Physics constants
GRAVITY = 0.86
MAX_VELOCITY = 100
ROTATION_ANGLE = 8
JUMP_VELOCITY = -10
OBSTACLE_SPEED = -6
JUMP_COOLDOWN_MS = 50

# Path to the project directory
PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')

BACKGROUND_IMAGE_PATH = os.path.join("resources/images", "background.png")
PORTAL_IMAGE_PATH = os.path.join("resources/images", "portal.webp")
PLAYER_IMAGE_PATH = os.path.join("resources/images", "avatar.png")
BLOCK_IMAGE_PATH = os.path.join("resources/images", "block.png")
SPIKE_IMAGE_PATH = os.path.join("resources/images", "spike.png")
COIN_IMAGE_PATH = os.path.join("resources/images", "coin.png")