import pygame

from src.entities.obstacle import Obstacle

class Block(Obstacle):
    def __init__(self, image: pygame.Surface, pos: pygame.math.Vector2, *groups) -> None:
        super().__init__(image, pos, *groups)