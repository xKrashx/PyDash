import pygame

from src.constants import SCREEN_SIZE
from src.player import Player
from src.spike import Spike

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(SCREEN_SIZE)

        from src.images import PLAYER_IMAGE

        pygame.display.set_caption('Pydash: Geometry Dash in Python')
        pygame.display.set_icon(PLAYER_IMAGE)

        self.player_sprite = pygame.sprite.Group()

        self.clock = pygame.time.Clock()
        self.player = Player(PLAYER_IMAGE, self.player_sprite)

    def run(self):
        from src.images import BACKGROUND_IMAGE, SPIKE_IMAGE

        done = False
        angle = 0

        obstacles = pygame.sprite.Group()
        self.obstacles = [ Spike(SPIKE_IMAGE, (500, SCREEN_SIZE[1] - 32), obstacles) ]

        while not done:
            for event in pygame.event.get():
                done = event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)

            keys = pygame.key.get_pressed()

            if keys[pygame.K_SPACE]: self.player.jump()

            self.screen.blit(BACKGROUND_IMAGE, (0, 0))
            self.player.draw_particle_trail(self.screen)

            self.player_sprite.update()

            if self.player.is_jumping:
                angle -= 8.1712
                self.player.blitRotate(self.screen, angle)
            else:
                self.player_sprite.draw(self.screen)

            for sprite in self.obstacles:
                sprite.rect.x -= self.player.vel.x

            obstacles.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()