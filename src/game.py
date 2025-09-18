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

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]: self.player.jump()

        if self.player.is_jumping: self.player.rotate()

        for obstacle in self.obstacles:
            obstacle.move(pygame.math.Vector2(-self.player.vel.x, 0))

    # TODO: Fix this nonsense
    def check_window_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): return True
        return False

    def run(self):
        from src.images import BACKGROUND_IMAGE, SPIKE_IMAGE

        obstacles = pygame.sprite.Group()
        self.obstacles = [ Spike(SPIKE_IMAGE, (500, SCREEN_SIZE[1] - 32), obstacles) ]

        while True:
            if self.check_window_events(): break

            self.update()

            self.screen.blit(BACKGROUND_IMAGE, (0, 0))
            self.player.draw_particle_trail(self.screen)
            self.player_sprite.update()
            self.player.blitRotate(self.screen, self.player.rotation_angle)

            obstacles.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()