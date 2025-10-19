import pygame

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, pos: pygame.math.Vector2, *groups) -> None:
        super().__init__(*groups)
        self._image = image
        self._rect = self._image.get_rect(topleft=pos)
        self._mask = pygame.mask.from_surface(self._image)

    def move(self, direction: pygame.math.Vector2) -> None:
        self._rect.x += int(direction.x)
        self._rect.y += int(direction.y)

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    @property
    def mask(self) -> pygame.mask.Mask:
        return self._mask