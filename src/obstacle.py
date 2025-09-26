import pygame

from src.constants import SCREEN_SIZE

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image, pos, *groups) -> None:
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, direction: pygame.math.Vector2) -> None:
        self.rect.x += direction.x
        self.rect.y += direction.y

        # TODO: I have to remove this. It is only here so the development of a collision system would be easier.
        if self.rect.x <= 0: self.rect.x = SCREEN_SIZE[0]