import pygame

from src.constants import WHITE

def main():
    pygame.init()

    screen = pygame.display.set_mode([800, 600])
    pygame.display.set_caption('Pydash: Geometry Dash in Python')

    done = False

    clock = pygame.time.Clock()

    alpha_surf = pygame.Surface(screen.get_size())

    while not done:
        alpha_surf.fill(WHITE)
        screen.blit(alpha_surf, (0, 0))

        for event in pygame.event.get():
            done = event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main()