import pygame
import os

from enum import Enum

from src.renderer import Renderer
from src.input_handler import InputHandler
from src.level_reader import load_level_from_csv
from src.constants import SCREEN_SIZE, RED, GREEN, BLACK, PURPLE, SPRITE_SIZE, OBSTACLE_SPEED, PROJECT_DIR
from src.entities import Player, Spike, Block, Coin, Portal, Obstacle

class Game:
    class State(Enum):
        LEVEL_SELECT = 0
        PLAYING = 1
        GAME_OVER = 2

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(SCREEN_SIZE)

        from src.images import PLAYER_IMAGE

        pygame.display.set_caption('Pydash: Geometry Dash in Python')
        pygame.display.set_icon(PLAYER_IMAGE)

        self.input_handler = InputHandler(self)
        self.renderer = Renderer(self.screen)

        self.clock = pygame.time.Clock()
        self.obstacles_group = pygame.sprite.Group()
        self.running = True
        self.debug_view = False

        self.state = Game.State.LEVEL_SELECT
        self.available_levels = ["levels/level1.csv", "levels/testing.csv"]
        self.selected_level = 0
        self.level_complete = False
        self.current_level_path = None

    def restart(self, level_path=None):
        from src.images import PLAYER_IMAGE

        self.state = Game.State.PLAYING
        self.level_complete = False

        self.debug_view = False
        self.points = 0

        self.player_sprite = pygame.sprite.Group()
        self.player = Player(PLAYER_IMAGE, self.player_sprite)

        self.obstacles_group.empty()
        level_to_load = level_path or "levels/level1.csv"
        self.current_level_path = level_to_load
        self.obstacles = load_level_from_csv(level_to_load, self.obstacles_group)
        self.portal_obstacle = next((o for o in self.obstacles if isinstance(o, Portal)), None)
        if self.portal_obstacle: self.initial_portal_distance = abs(self.portal_obstacle.rect.left - self.player.rect.left)

        pygame.mixer_music.load(os.path.join("resources/music", "bossfight-Vextron.mp3"))
        pygame.mixer_music.play()

    def collision_checks(self, obstacle: Obstacle):
        def complete_level(has_completed: bool):
            self.player.died()
            pygame.mixer_music.stop()
            self.state = Game.State.GAME_OVER
            self.level_complete = has_completed
        if isinstance(obstacle, Spike): complete_level(False)
        elif isinstance(obstacle, Block):
            if obstacle.rect.top <= self.player.rect.center[1] or self.player.rect.center[1] >= obstacle.rect.bottom:  complete_level(False)
            elif self.player.velocity > 0: self.player.land(obstacle.rect.top)
        elif isinstance(obstacle, Coin):
            self.obstacles_group.remove(obstacle)
            self.obstacles.remove(obstacle)
            self.points += 1
        elif isinstance(obstacle, Portal): complete_level(True)

    def has_block_above(self) -> bool:
        head_rect = self.player.rect.copy()
        head_rect.height = 4
        head_rect.top = self.player.rect.top - head_rect.height - 1
        return any(isinstance(obstacle, Block) and obstacle.rect.colliderect(head_rect) for obstacle in self.obstacles)

    def has_block_below(self) -> bool:
        head_rect = self.player.rect.copy()
        head_rect.height = 4
        head_rect.bottom = self.player.rect.bottom + head_rect.height + 1
        return any(isinstance(obstacle, Block) and obstacle.rect.colliderect(head_rect) for obstacle in self.obstacles)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self.has_block_above(): self.player.jump()

        if not self.player.is_jumping and not self.has_block_below(): self.player.is_on_ground = False

        self.contact_point = None
        if not self.player.is_on_ground: self.player.rotate()

        self.player.update()

        for obstacle in self.obstacles:
            obstacle.move(pygame.math.Vector2(OBSTACLE_SPEED, 0))
            offset = (obstacle.rect.left - self.player.rect.left, obstacle.rect.top - self.player.rect.top)
            overlap = self.player.mask.overlap(obstacle.mask, offset)
            if overlap: self.contact_point = (overlap[0] + self.player.rect.left, overlap[1] + self.player.rect.top)
            if pygame.sprite.collide_mask(self.player, obstacle):
                self.collision_checks(obstacle)

    def run(self):
        while self.running:
            self.input_handler.handle_events()
            self.screen.blit(BACKGROUND_IMAGE, (0, 0))

            if self.state == Game.State.PLAYING:
                if not getattr(self, "player", None): self.restart(self.available_levels[self.selected_level])
                if not self.player.is_dead: self.update()

                self.renderer.draw_text(f"Points: {getattr(self, 'points', 0)}", self.renderer.small_font, BLACK, 120, 50)

                if self.debug_view:
                    self.renderer.draw_bounding_boxes(self.player, self.obstacles, self.contact_point)
                else:
                    if not self.player.is_dead: self.player.draw_particle_trail(self.screen)
                    if self.portal_obstacle and not self.player.is_dead: self.renderer.draw_progress_bar(current_distance=abs(self.portal_obstacle.rect.left - self.player.rect.left), initial_portal_distance=self.initial_portal_distance)
                    self.player.display(self.screen)
                    self.obstacles_group.draw(self.screen)

            elif self.state == Game.State.LEVEL_SELECT: self.renderer.draw_level_select_menu(self.available_levels, self.selected_level)
            elif self.state == Game.State.GAME_OVER: self.renderer.draw_game_over_menu(self.level_complete, self.input_handler.game_over_selection, self.points)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()