import pygame
import os

from src.level_reader import load_level_from_csv
from src.constants import SCREEN_SIZE, RED, GREEN, BLACK, PURPLE, SPRITE_SIZE
from src.obstacle import Obstacle
from src.player import Player
from src.spike import Spike
from src.block import Block
from src.coin import Coin
from src.portal import Portal

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(SCREEN_SIZE)

        from src.images import PLAYER_IMAGE

        pygame.display.set_caption('Pydash: Geometry Dash in Python')
        pygame.display.set_icon(PLAYER_IMAGE)

        self.clock = pygame.time.Clock()
        self.obstacles_group = pygame.sprite.Group()
        self.running = True
        self.debug_view = False

    def restart(self):
        from src.images import PLAYER_IMAGE

        self.debug_view = False
        self.points = 0

        self.player_sprite = pygame.sprite.Group()
        self.player = Player(PLAYER_IMAGE, self.player_sprite)

        self.obstacles_group.empty()
        self.obstacles = load_level_from_csv("levels/level1.csv", self.obstacles_group)
        self.portal_obstacle = next((o for o in self.obstacles if isinstance(o, Portal)), None)
        if self.portal_obstacle: self.initial_portal_distance = abs(self.portal_obstacle.rect.left - self.player.rect.left)

        pygame.mixer_music.load(os.path.join("resources/music", "bossfight-Vextron.mp3"))
        pygame.mixer_music.play()

    def collision_checks(self, obstacle: Obstacle):
        if isinstance(obstacle, Spike):
            self.player.died()
            pygame.mixer_music.stop()
            print(self.points)
        elif isinstance(obstacle, Block) and self.player.vel.y > 0:
            self.player.land(obstacle.rect.top)
        elif isinstance(obstacle, Coin):
            self.obstacles_group.remove(obstacle)
            self.obstacles.remove(obstacle)
            self.points += 1
        elif isinstance(obstacle, Portal):
            self.player.died()
            pygame.mixer_music.stop()
            print("Level Complete! Points:", self.points)

    def draw_progress_bar(self, bar_width=600, bar_height=10, color=(0, 200, 0), finish_offset=SPRITE_SIZE[0]):
        if not self.portal_obstacle or not self.initial_portal_distance: return

        current_distance = max(abs(self.portal_obstacle.rect.left - self.player.rect.left) - finish_offset, 1)
        progress = 1 - min(current_distance / self.initial_portal_distance, 1)

        fill_width = int(bar_width * progress)
        outline_rect = pygame.Rect(100, 20, bar_width, bar_height)
        fill_rect = pygame.Rect(100, 20, fill_width, bar_height)
        pygame.draw.rect(self.screen, color, fill_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), outline_rect, 2)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]: self.player.jump()

        self.contact_point = None
        if self.player.is_jumping: self.player.rotate()

        self.player.update()

        for obstacle in self.obstacles:
            obstacle.move(pygame.math.Vector2(-self.player.vel.x, 0))
            offset = (obstacle.rect.left - self.player.rect.left, obstacle.rect.top - self.player.rect.top)
            overlap = self.player.mask.overlap(obstacle.mask, offset)
            if overlap: self.contact_point = (overlap[0] + self.player.rect.left, overlap[1] + self.player.rect.top)
            if pygame.sprite.collide_mask(self.player, obstacle):
                self.collision_checks(obstacle)

    def check_window_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.debug_view = not self.debug_view
                    return
                if self.player.is_dead: self.restart()

    def draw_mask(self, mask, rect, color=(0, 0, 255, 100)):
        mask_surface = mask.to_surface(setcolor=color, unsetcolor=BLACK)
        mask_surface.set_colorkey(BLACK)
        mask_surface.set_alpha(100)
        self.screen.blit(mask_surface, rect.topleft)

    def draw_bounding_boxes(self):
        pygame.draw.rect(self.screen, RED, self.player.rect, 2)
        self.draw_mask(self.player.mask, self.player.rect, color=(0, 0, 255, 100))
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, GREEN, obstacle.rect, 2)
            if hasattr(obstacle, "mask"):
                self.draw_mask(obstacle.mask, obstacle.rect, color=(255, 255, 0, 100))
        if hasattr(self, "contact_point") and self.contact_point:
            pygame.draw.circle(self.screen, PURPLE, self.contact_point, 5)

    def run(self):
        from src.images import BACKGROUND_IMAGE

        self.obstacles = load_level_from_csv("levels/level1.csv", self.obstacles_group)

        self.restart()

        while self.running:
            self.check_window_events()

            if not self.player.is_dead: self.update()

            self.screen.blit(BACKGROUND_IMAGE, (0, 0))

            if self.debug_view:
                self.draw_bounding_boxes()
            else:
                if not self.player.is_dead: self.player.draw_particle_trail(self.screen)
                self.draw_progress_bar()
                self.player.blitRotate(self.screen)
                self.obstacles_group.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
