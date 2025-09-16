import pygame

from src.constants import RED, SCREEN_SIZE

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption('Pydash: Geometry Dash in Python')

        self.clock = pygame.time.Clock()

    def run(self):
        done = False

        while not done:
            alpha_surf = pygame.Surface(self.screen.get_size())
            alpha_surf.fill(RED)

            self.screen.blit(alpha_surf, (0, 0))

            for event in pygame.event.get():
                done = event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()