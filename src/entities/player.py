import pygame
import random

from pygame.math import Vector2

from src.constants import WHITE, GRAVITY, MAX_VELOCITY, ROTATION_ANGLE, JUMP_VELOCITY, JUMP_COOLDOWN_MS

class Player(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, *groups) -> None:
        super().__init__(*groups)
        self._position = Vector2(66, 50)

        self._image = image
        self._rect = self._image.get_rect(center=(int(self._position.x), int(self._position.y)))
        self._mask = pygame.mask.from_surface(self._image)

        self._particles = []

        self._is_jumping = False
        self._is_dead = False
        self._is_on_ground = False

        self._rotation_angle = 0
        self._velocity = 0

        self._last_jump_time = -JUMP_COOLDOWN_MS

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    @property
    def mask(self) -> pygame.Mask:
        return self._mask

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def is_jumping(self) -> bool:
        return self._is_jumping

    @property
    def is_on_ground(self) -> bool:
        return self._is_on_ground

    @is_on_ground.setter
    def is_on_ground(self, value: bool) -> None:
        self._is_on_ground = value

    @property
    def is_dead(self) -> bool:
        return self._is_dead

    def draw_particle_trail(self, surface: pygame.Surface, color: tuple[int, int, int] = WHITE) -> None:
        self._particles.append([
            [self._rect.left - 6, self._rect.bottom - 6], # position
            [random.randint(0, 25) // 10 - 1, 0],       # velocity
            random.randint(5, 8)                        # size/life
        ])

        for particle in self._particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.2
            particle[1][0] -= 0.1
            pygame.draw.rect(surface, color, ([particle[0][0], particle[0][1]], [particle[2], particle[2]]))
            if particle[2] <= 0: self._particles.remove(particle)

    def jump(self) -> None:
        if self._is_jumping or not self._is_on_ground: return

        now = pygame.time.get_ticks()

        if now - self._last_jump_time < JUMP_COOLDOWN_MS: return

        self._velocity = JUMP_VELOCITY
        self._is_jumping = True
        self._is_on_ground = False
        self._last_jump_time = now

    def rotate(self) -> None:
        self._rotation_angle -= ROTATION_ANGLE

    def died(self) -> None:
        self._is_dead = True

    def land(self, ground: int) -> None:
        self._is_jumping = False
        self._is_on_ground = True
        self._rotation_angle = 0
        self._position.y = ground - self._image.get_height() // 2
        self._rect.center = (int(self._position.x), int(self._position.y))
        self._velocity = 0
        rotated_image = pygame.transform.rotozoom(self._image, self._rotation_angle, 1)
        self._mask = pygame.mask.from_surface(rotated_image)
        self._last_jump_time = pygame.time.get_ticks()

    def update(self) -> None:
        if not self._is_on_ground: self._velocity = min(self._velocity + GRAVITY, MAX_VELOCITY)
        self._position.y += self._velocity
        self._rect.center = (int(self._position.x), int(self._position.y))

    def display(self, surface: pygame.Surface):
        origin_position = (16, 16)
        width, height = self._image.get_size()
        box = [Vector2(point) for point in [(0, 0), (width, 0), (width, -height), (0, -height)]]
        box_rotate = [point.rotate(self._rotation_angle) for point in box]

        min_box = (min(box_rotate, key=lambda point: point[0])[0], min(box_rotate, key=lambda point: point[1])[1])
        max_box = (max(box_rotate, key=lambda point: point[0])[0], max(box_rotate, key=lambda point: point[1])[1])

        pivot = Vector2(origin_position[0], -origin_position[1])
        pivot_rotate = pivot.rotate(self._rotation_angle)
        pivot_move = pivot_rotate - pivot

        center = self._position
        origin = (
            center[0] - origin_position[0] + min_box[0] - pivot_move[0],
            center[1] - origin_position[1] - max_box[1] + pivot_move[1]
        )

        current_image = pygame.transform.rotozoom(self._image, self._rotation_angle, 1)
        surface.blit(current_image, origin)

        self._rect = current_image.get_rect(topleft=origin)
        self._mask = pygame.mask.from_surface(current_image)