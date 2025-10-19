import pygame
import os

from enum import Enum

from src.renderer import Renderer
from src.input_handler import InputHandler
from src.image_manager import ImageManager
from src.level_reader import load_level_from_csv
from src.entities import Player, Spike, Block, Coin, Portal, Obstacle
from src.constants import SCREEN_SIZE, BLACK, OBSTACLE_SPEED, PLAYER_IMAGE_PATH, BACKGROUND_IMAGE_PATH, SPRITE_SIZE

class Game:
    class State(Enum):
        LEVEL_SELECT = 0
        PLAYING = 1
        GAME_OVER = 2

    def __init__(self) -> None:
        pygame.init()

        self._screen = pygame.display.set_mode(SCREEN_SIZE)
        self._image_manager = ImageManager()

        pygame.display.set_caption('Pydash: Geometry Dash in Python')
        pygame.display.set_icon(self._image_manager.get(PLAYER_IMAGE_PATH, SPRITE_SIZE))

        self._input_handler = InputHandler(self)
        self._renderer = Renderer(self._screen)

        self._clock = pygame.time.Clock()
        self._obstacles_group = pygame.sprite.Group()
        self._running = True
        self._debug_view = False

        self._state = Game.State.LEVEL_SELECT
        self._available_levels = ["levels/level1.csv", "levels/testing.csv"]
        self._selected_level = 0
        self._level_complete = False
        self._current_level_path = ""

    @property
    def state(self) -> State:
        return self._state

    @state.setter
    def state(self, value: State) -> None:
        self._state = value

    @property
    def available_levels(self) -> list[str]:
        return self._available_levels

    @property
    def selected_level(self) -> int:
        return self._selected_level

    @selected_level.setter
    def selected_level(self, value: int) -> None:
        self._selected_level = value

    @property
    def player(self) -> Player:
        return self._player

    @property
    def debug_view(self) -> bool:
        return self._debug_view

    @debug_view.setter
    def debug_view(self, value: bool) -> None:
        self._debug_view = value

    @property
    def current_level_path(self) -> str:
        return self._current_level_path

    @property
    def running(self) -> bool:
        return self._running

    @running.setter
    def running(self, value: bool) -> None:
        self._running = value

    def restart(self, level_path: str = "") -> None:
        self._state = Game.State.PLAYING
        self._level_complete = False

        self._debug_view = False
        self._points = 0

        self._player_sprite = pygame.sprite.Group()
        self._player = Player(self._image_manager.get(PLAYER_IMAGE_PATH, SPRITE_SIZE), self._player_sprite)

        self._obstacles_group.empty()
        level_to_load = level_path or "levels/level1.csv"
        self._current_level_path = level_to_load
        self._obstacles = load_level_from_csv(level_to_load, self._image_manager, self._obstacles_group)
        self._portal_obstacle = next((o for o in self._obstacles if isinstance(o, Portal)), None)
        if self._portal_obstacle: self._initial_portal_distance = abs(self._portal_obstacle.rect.left - self._player.rect.left)

        pygame.mixer_music.load(os.path.join("resources/music", "bossfight-Vextron.mp3"))
        pygame.mixer_music.play()

    def collision_checks(self, obstacle: Obstacle):
        def complete_level(has_completed: bool):
            self._player.died()
            pygame.mixer_music.stop()
            self._state = Game.State.GAME_OVER
            self._level_complete = has_completed
        if isinstance(obstacle, Spike): complete_level(False)
        elif isinstance(obstacle, Block):
            if obstacle.rect.top <= self._player.rect.center[1] or self._player.rect.center[1] >= obstacle.rect.bottom:  complete_level(False)
            elif self._player.velocity > 0: self._player.land(obstacle.rect.top)
        elif isinstance(obstacle, Coin):
            self._obstacles_group.remove(obstacle)
            self._obstacles.remove(obstacle)
            self._points += 1
        elif isinstance(obstacle, Portal): complete_level(True)

    def has_block_above(self) -> bool:
        head_rect = self._player.rect.copy()
        head_rect.height = 4
        head_rect.top = self._player.rect.top - head_rect.height - 1
        return any(isinstance(obstacle, Block) and obstacle.rect.colliderect(head_rect) for obstacle in self._obstacles)

    def has_block_below(self) -> bool:
        head_rect = self._player.rect.copy()
        head_rect.height = 4
        head_rect.bottom = self._player.rect.bottom + head_rect.height + 1
        return any(isinstance(obstacle, Block) and obstacle.rect.colliderect(head_rect) for obstacle in self._obstacles)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self.has_block_above(): self._player.jump()

        if not self._player.is_jumping and not self.has_block_below(): self._player.is_on_ground = False

        self.contact_point = None
        if not self._player.is_on_ground: self._player.rotate()

        self._player.update()

        for obstacle in self._obstacles:
            obstacle.move(pygame.math.Vector2(OBSTACLE_SPEED, 0))
            offset = (obstacle.rect.left - self._player.rect.left, obstacle.rect.top - self._player.rect.top)
            overlap = self._player.mask.overlap(obstacle.mask, offset)
            if overlap: self.contact_point = (overlap[0] + self._player.rect.left, overlap[1] + self._player.rect.top)
            if pygame.sprite.collide_mask(self._player, obstacle):
                self.collision_checks(obstacle)

    def run(self):
        while self._running:
            self._input_handler.handle_events()
            self._screen.blit(self._image_manager.get(BACKGROUND_IMAGE_PATH, SCREEN_SIZE), (0, 0))

            if self._state == Game.State.PLAYING:
                if not getattr(self, "player", None): self.restart(self._available_levels[self._selected_level])
                if not self._player.is_dead: self.update()

                self._renderer.draw_text(f"Points: {getattr(self, 'points', 0)}", self._renderer._small_font, BLACK, 120, 50)
                if self._portal_obstacle and not self._player.is_dead: self._renderer.draw_progress_bar(current_distance=abs(self._portal_obstacle.rect.left - self._player.rect.left), initial_portal_distance=self._initial_portal_distance)

                if self._debug_view:
                    self._renderer.draw_bounding_boxes(self._player, self._obstacles, self.contact_point)
                else:
                    if not self._player.is_dead: self._player.draw_particle_trail(self._screen)
                    self._player.display(self._screen)
                    self._obstacles_group.draw(self._screen)

            elif self._state == Game.State.LEVEL_SELECT: self._renderer.draw_level_select_menu(self._available_levels, self._selected_level)
            elif self._state == Game.State.GAME_OVER: self._renderer.draw_game_over_menu(self._level_complete, self._input_handler.game_over_selection.value, self._points)

            pygame.display.flip()
            self._clock.tick(60)

        pygame.quit()