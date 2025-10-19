import pygame

from src.entities.obstacle import Obstacle

class Portal(Obstacle):
    def __init__(self, image: pygame.Surface, position: pygame.math.Vector2, *groups) -> None:
        super().__init__(image, position, *groups)