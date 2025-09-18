import pygame
import math

from src.constants import SCREEN_SIZE
from src.obstacle import Obstacle
from src.player import Player
from src.spike import Spike
from src.block import Block

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(SCREEN_SIZE)

        from src.images import PLAYER_IMAGE

        pygame.display.set_caption('Pydash: Geometry Dash in Python')
        pygame.display.set_icon(PLAYER_IMAGE)

        self.clock = pygame.time.Clock()
        self.running = True

    def restart(self):
        from src.images import PLAYER_IMAGE

        self.player_sprite = pygame.sprite.Group()
        self.player = Player(PLAYER_IMAGE, self.player_sprite)

    def collision_checks(self, obstacle: Obstacle):
        if isinstance(obstacle, Spike): self.player.died()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]: self.player.jump()

        if self.player.is_jumping: self.player.rotate()

        for obstacle in self.obstacles:
            obstacle.move(pygame.math.Vector2(-self.player.vel.x, 0))
            if pygame.sprite.collide_rect(self.player, obstacle):
                self.collision_checks(obstacle)

    def check_window_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
                return True
            elif event.type == pygame.KEYDOWN: return True

    def wait(self):
        while True:
            if self.check_window_events(): break

    def game_over_screen(self):
        self.wait()
        self.restart()

    def run(self):
        from src.images import BACKGROUND_IMAGE, SPIKE_IMAGE, BLOCK_IMAGE

        obstacles = pygame.sprite.Group()
        self.obstacles = [ Spike(SPIKE_IMAGE, (500, SCREEN_SIZE[1] - 32), obstacles) ]

        for i in range(math.ceil(SCREEN_SIZE[0] / 32)):
            self.obstacles.append(Block(BLOCK_IMAGE, (i * 32, SCREEN_SIZE[1] - 32), obstacles))

        self.restart()

        while self.running:
            self.check_window_events()

            self.update()

            if self.player.is_dead: self.game_over_screen()

            self.screen.blit(BACKGROUND_IMAGE, (0, 0))
            self.player.draw_particle_trail(self.screen)
            self.player_sprite.update()
            self.player.blitRotate(self.screen, self.player.rotation_angle)

            obstacles.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()