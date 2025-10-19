import csv
import pygame

from src.image_manager import ImageManager
from src.entities import Block, Spike, Coin, Portal, Obstacle
from src.constants import SPRITE_SIZE, SPIKE_IMAGE_PATH, COIN_IMAGE_PATH, PORTAL_IMAGE_PATH, BLOCK_IMAGE_PATH

def load_level_from_csv(filename: str, image_manager: ImageManager, group) -> list[Obstacle]:
    obstacles: list[Obstacle] = []

    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)

        for row_idx, row in enumerate(reader):
            for col_idx, cell in enumerate(row):

                try: value = int(cell)
                except ValueError: continue

                x = col_idx * SPRITE_SIZE[0]
                y = row_idx * SPRITE_SIZE[1]

                should_rotate = value < 0
                value = abs(value)
                obj = None

                if value == 0: continue
                elif value == 1: obj = Block(image_manager.get(BLOCK_IMAGE_PATH, SPRITE_SIZE), pygame.math.Vector2(x, y), group)
                elif value == 2:
                    image = image_manager.get(SPIKE_IMAGE_PATH, SPRITE_SIZE)
                    if should_rotate: image = pygame.transform.rotate(image, 180)
                    obj = Spike(image, pygame.math.Vector2(x, y), group)
                elif value == 3: obj = Coin(image_manager.get(COIN_IMAGE_PATH, SPRITE_SIZE), pygame.math.Vector2(x, y), group)
                elif value == 4: obj = Portal(image_manager.get(PORTAL_IMAGE_PATH, (32, 64)), pygame.math.Vector2(x, y), group)

                if obj: obstacles.append(obj)

    return obstacles