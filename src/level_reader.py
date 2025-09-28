import csv
import pygame
from src.block import Block
from src.spike import Spike
from src.coin import Coin
from src.constants import SPRITE_SIZE

def load_level_from_csv(filename, group):
    from src.images import BLOCK_IMAGE, SPIKE_IMAGE, COIN_IMAGE
    obstacles = []

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
                elif value == 1: obj = Block(BLOCK_IMAGE, (x, y), group)
                elif value == 2:
                    image = SPIKE_IMAGE
                    if should_rotate: image = pygame.transform.rotate(SPIKE_IMAGE, 180)
                    obj = Spike(image, (x, y), group)
                elif value == 3: obj = Coin(COIN_IMAGE, (x, y), group)

                if obj: obstacles.append(obj)

    return obstacles