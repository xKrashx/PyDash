import pygame

from src.images import PLAYER_IMAGE, BACKGROUND_IMAGE
from src.constants import SCREEN_SIZE
from src.player import Player

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption('Pydash: Geometry Dash in Python')
        pygame.display.set_icon(PLAYER_IMAGE)

        self.player_sprite = pygame.sprite.Group()

        self.clock = pygame.time.Clock()
        self.player = Player(self.player_sprite)

    def run(self):
        done = False
        angle = 0

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


            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()