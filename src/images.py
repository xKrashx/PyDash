import os
import pygame

from src.constants import PROJECT_DIR, SCREEN_SIZE, SPRITE_SIZE

def load_image(path: str, size: tuple[int, int]) -> pygame.image:
    image = pygame.image.load(os.path.join(PROJECT_DIR, path))
    image = image.convert() if not image.get_alpha() else image.convert_alpha()
    image = pygame.transform.smoothscale(image, size)
    return image

PLAYER_IMAGE = load_image("resources/images/avatar.png", SPRITE_SIZE)
SPIKE_IMAGE = load_image("resources/images/spike.png", SPRITE_SIZE)
BLOCK_IMAGE = load_image("resources/images/block.png", SPRITE_SIZE)
COIN_IMAGE = load_image("resources/images/coin.png", SPRITE_SIZE)
BACKGROUND_IMAGE = load_image("resources/images/background.png", SCREEN_SIZE)