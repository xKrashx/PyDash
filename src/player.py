import pygame
import random

from pygame.math import Vector2

from src.constants import WHITE, GRAVITY, MAX_VELOCITY, SCREEN_SIZE, ROTATION_ANGLE

class Player(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, *groups):
        super().__init__(*groups)
        self.position = [66, 0]

        self.image = image
        self.rect = self.image.get_rect(center=self.position)
        self.rotation_angle = 0
        self.jump_amount = 10
        self.particles = []
        self.is_jumping = False
        self.is_dead = False
        self.vel = Vector2(6, 0)

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

    def jump(self):
        if self.is_jumping: return
        self.vel.y = -self.jump_amount
        self.is_jumping = True

    def rotate(self):
        self.rotation_angle -= ROTATION_ANGLE

    def died(self):
        self.is_dead = True

    def update(self):
        self.vel.y = min(self.vel.y + GRAVITY, MAX_VELOCITY)

        self.rect.top += self.vel.y
        # TODO: Remove this cap is only for testing
        if self.rect.top >= SCREEN_SIZE[1] - self.rect.height:
            self.is_jumping = False
            self.rotation_angle = 0
            self.rect.top = SCREEN_SIZE[1] - self.rect.height

    def blitRotate(self, surface: pygame.Surface, angle: float):
        origin_position = (16, 16)
        width, height = self.image.get_size()
        box = [Vector2(point) for point in [(0, 0), (width, 0), (width, -height), (0, -height)]]
        box_rotate = [point.rotate(angle) for point in box]

        min_box = (min(box_rotate, key=lambda point: point[0])[0], min(box_rotate, key=lambda point: point[1])[1])
        max_box = (max(box_rotate, key=lambda point: point[0])[0], max(box_rotate, key=lambda point: point[1])[1])

        pivot = Vector2(origin_position[0], -origin_position[1])
        pivot_rotate = pivot.rotate(angle)
        pivot_move = pivot_rotate - pivot

        origin = (self.rect.center[0] - origin_position[0] + min_box[0] - pivot_move[0], self.rect.center[1] - origin_position[1] - max_box[1] + pivot_move[1])
        rotated_image = pygame.transform.rotozoom(self.image, angle, 1)
        surface.blit(rotated_image, origin)