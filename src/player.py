import pygame
import random

from pygame.math import Vector2

from src.constants import WHITE, GRAVITY, MAX_VELOCITY, ROTATION_ANGLE

class Player(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, *groups):
        super().__init__(*groups)
        self.position = Vector2(66, 50)

        self.image = image
        self.rect = self.image.get_rect(center=(int(self.position.x), int(self.position.y)))
        self.mask = pygame.mask.from_surface(self.image)

        self.rotation_angle = 0
        self.jump_amount = 10
        self.particles = []
        self.is_jumping = False
        self.is_dead = False
        self.is_on_ground = False
        self.vel = Vector2(6, 0)

        self.jump_cooldown_ms = 50
        self.last_jump_time = -self.jump_cooldown_ms

    def draw_particle_trail(self, surface: pygame.Surface, color=WHITE):
        self.particles.append([
            [self.rect.left - 6, self.rect.bottom - 6], # position
            [random.randint(0, 25) // 10 - 1, 0],       # velocity
            random.randint(5, 8)                        # size/life
        ])

        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.2
            particle[1][0] -= 0.1
            pygame.draw.rect(surface, color, ([particle[0][0], particle[0][1]], [particle[2], particle[2]]))
            if particle[2] <= 0: self.particles.remove(particle)

    def jump(self) -> None:
        if self.is_jumping: return

        now = pygame.time.get_ticks()

        if now - self.last_jump_time < self.jump_cooldown_ms: return

        self.vel.y = -self.jump_amount
        self.is_jumping = True
        self.is_on_ground = False
        self.last_jump_time = now

    def rotate(self) -> None:
        self.rotation_angle -= ROTATION_ANGLE

    def died(self) -> None:
        self.is_dead = True

    def land(self, ground: int) -> None:
        self.is_jumping = False
        self.is_on_ground = True
        self.rotation_angle = 0
        self.position.y = ground - self.image.get_height() // 2
        self.rect.center = (int(self.position.x), int(self.position.y))
        self.vel.y = 0
        rotated_image = pygame.transform.rotozoom(self.image, self.rotation_angle, 1)
        self.mask = pygame.mask.from_surface(rotated_image)
        self.last_jump_time = pygame.time.get_ticks()

    def update(self):
        if not self.is_on_ground:
            self.vel.y = min(self.vel.y + GRAVITY, MAX_VELOCITY)
        self.position.y += self.vel.y
        self.rect.center = (int(self.position.x), int(self.position.y))

    def blitRotate(self, surface: pygame.Surface):
        origin_position = (16, 16)
        width, height = self.image.get_size()
        box = [Vector2(point) for point in [(0, 0), (width, 0), (width, -height), (0, -height)]]
        box_rotate = [point.rotate(self.rotation_angle) for point in box]

        min_box = (min(box_rotate, key=lambda point: point[0])[0], min(box_rotate, key=lambda point: point[1])[1])
        max_box = (max(box_rotate, key=lambda point: point[0])[0], max(box_rotate, key=lambda point: point[1])[1])

        pivot = Vector2(origin_position[0], -origin_position[1])
        pivot_rotate = pivot.rotate(self.rotation_angle)
        pivot_move = pivot_rotate - pivot

        center = self.position
        origin = (
            center[0] - origin_position[0] + min_box[0] - pivot_move[0],
            center[1] - origin_position[1] - max_box[1] + pivot_move[1]
        )

        current_image = pygame.transform.rotozoom(self.image, self.rotation_angle, 1)
        surface.blit(current_image, origin)

        self.rect = current_image.get_rect(topleft=origin)
        self.mask = pygame.mask.from_surface(current_image)