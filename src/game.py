import pygame
import os

from enum import Enum

from src.level_reader import load_level_from_csv
from src.constants import SCREEN_SIZE, RED, GREEN, BLACK, PURPLE, SPRITE_SIZE, PROJECT_DIR
from src.obstacle import Obstacle
from src.player import Player
from src.spike import Spike
from src.block import Block
from src.coin import Coin
from src.portal import Portal

class Game:
    class State(Enum):
        LEVEL_SELECT = 0
        PLAYING = 1
        GAME_OVER = 2

    class MenuOption(Enum):
        RETRY = 0
        MAIN_MENU = 1
        QUIT = 2
        COUNT = 3

        def __int__(self):
            return self.value

        def __index__(self):
            return int(self)

        def __eq__(self, other):
            if isinstance(other, int): return self.value == other
            if isinstance(other, self.__class__): return self is other
            return NotImplemented

        def _wrap(self, n: int):
            return self.__class__(n % self.__class__.COUNT.value)

        def __add__(self, other):
            if isinstance(other, int): return self._wrap(self.value + other)
            if isinstance(other, Game.MenuOption): return self._wrap(self.value + other.value)
            return NotImplemented

        def __radd__(self, other):
            return self.__add__(other)

        def __sub__(self, other):
            if isinstance(other, int): return self._wrap(self.value - other)
            if isinstance(other, Game.MenuOption): return self._wrap(self.value - other.value)
            return NotImplemented

        def __rsub__(self, other):
            if isinstance(other, int): return self._wrap(other - self.value)
            return NotImplemented

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
        
        self.big_font = pygame.font.Font(os.path.join(PROJECT_DIR, "resources/fonts/PUSAB_.ttf"), 60)
        self.mid_font = pygame.font.Font(os.path.join(PROJECT_DIR, "resources/fonts/PUSAB_.ttf"), 48)
        self.small_font = pygame.font.Font(os.path.join(PROJECT_DIR, "resources/fonts/PUSAB_.ttf"), 36)

        self.state = Game.State.LEVEL_SELECT
        self.available_levels = ["levels/level1.csv", "levels/testing.csv"]
        self.selected_level = 0
        self.gameover_selection = Game.MenuOption.RETRY
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
            elif self.player.vel.y > 0: self.player.land(obstacle.rect.top)
        elif isinstance(obstacle, Coin):
            self.obstacles_group.remove(obstacle)
            self.obstacles.remove(obstacle)
            self.points += 1
        elif isinstance(obstacle, Portal): complete_level(True)

    def draw_text(self, text, font, color, x, y):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        self.screen.blit(text_obj, text_rect)

    def draw_progress_bar(self, bar_width=600, bar_height=10, color=(0, 200, 0), finish_offset=SPRITE_SIZE[0]):
        if not self.portal_obstacle or not self.initial_portal_distance: return

        current_distance = max(abs(self.portal_obstacle.rect.left - self.player.rect.left) - finish_offset, 1)
        progress = 1 - min(current_distance / self.initial_portal_distance, 1)

        fill_width = int(bar_width * progress)
        outline_rect = pygame.Rect(100, 20, bar_width, bar_height)
        fill_rect = pygame.Rect(100, 20, fill_width, bar_height)
        pygame.draw.rect(self.screen, color, fill_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), outline_rect, 2)

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
            obstacle.move(pygame.math.Vector2(-self.player.vel.x, 0))
            offset = (obstacle.rect.left - self.player.rect.left, obstacle.rect.top - self.player.rect.top)
            overlap = self.player.mask.overlap(obstacle.mask, offset)
            if overlap: self.contact_point = (overlap[0] + self.player.rect.left, overlap[1] + self.player.rect.top)
            if pygame.sprite.collide_mask(self.player, obstacle):
                self.collision_checks(obstacle)

    def check_window_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return

                if self.state == Game.State.LEVEL_SELECT:
                    if event.key == pygame.K_UP: self.selected_level = (self.selected_level - 1) % len(self.available_levels)
                    elif event.key == pygame.K_DOWN: self.selected_level = (self.selected_level + 1) % len(self.available_levels)
                    elif event.key == pygame.K_RETURN:
                        chosen = self.available_levels[self.selected_level]
                        self.restart(chosen)

                elif self.state == Game.State.GAME_OVER:
                    if event.key == pygame.K_UP: self.gameover_selection -= 1
                    elif event.key == pygame.K_DOWN: self.gameover_selection += 1
                    elif event.key == pygame.K_RETURN:
                        if self.gameover_selection == Game.MenuOption.RETRY: self.restart(self.current_level_path)
                        elif self.gameover_selection == Game.MenuOption.MAIN_MENU: self.state = Game.State.LEVEL_SELECT
                        elif self.gameover_selection == Game.MenuOption.QUIT: self.running = False

                elif self.state == Game.State.PLAYING:
                    if event.key == pygame.K_TAB: self.debug_view = not self.debug_view
                    elif self.player.is_dead: self.state = Game.State.GAME_OVER

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
            if hasattr(obstacle, "mask"): self.draw_mask(obstacle.mask, obstacle.rect, color=(255, 255, 0, 100))
        if hasattr(self, "contact_point") and self.contact_point: pygame.draw.circle(self.screen, PURPLE, self.contact_point, 5)

    def draw_level_select_menu(self):
        self.draw_text("Select Level", self.big_font, BLACK, SCREEN_SIZE[0]//2, 120)
        for i, lvl in enumerate(self.available_levels):
            name = os.path.basename(lvl)
            color = (0, 0, 0)
            x = SCREEN_SIZE[0]//2
            y = 220 + i * 60
            if i == self.selected_level: pygame.draw.rect(self.screen, (200, 200, 0), (x - 220, y - 24, 440, 48))
            self.draw_text(name, self.mid_font, color, x, y)
        self.draw_text("Use Up/Down and Enter to select", self.small_font, BLACK, SCREEN_SIZE[0]//2, SCREEN_SIZE[1] - 60)

    def draw_game_over_menu(self):
        title = "Level Complete!" if self.level_complete else "Game Over"
        self.draw_text(title, self.big_font, BLACK, SCREEN_SIZE[0]//2, 120)
        options = ["Retry", "Main Menu", "Quit"]
        for i, opt in enumerate(options):
            x = SCREEN_SIZE[0]//2
            y = 220 + i * 60
            color = BLACK
            if i == self.gameover_selection: pygame.draw.rect(self.screen, (200, 200, 0), (x - 220, y - 24, 440, 48))
            self.draw_text(opt, self.mid_font, color, x, y)
        self.draw_text(f"Points: {getattr(self, 'points', 0)}", self.small_font, BLACK, SCREEN_SIZE[0]//2, SCREEN_SIZE[1] - 80)

    def run(self):
        from src.images import BACKGROUND_IMAGE

        while self.running:
            self.check_window_events()

            if self.state == Game.State.PLAYING:
                if not getattr(self, "player", None): self.restart(self.available_levels[self.selected_level])
                if not self.player.is_dead: self.update()

                self.screen.blit(BACKGROUND_IMAGE, (0, 0))
                self.draw_text(f"Points: {getattr(self, 'points', 0)}", self.small_font, BLACK, 120, 50)

                if self.debug_view:
                    self.draw_bounding_boxes()
                else:
                    if not self.player.is_dead: self.player.draw_particle_trail(self.screen)
                    self.draw_progress_bar()
                    self.player.blitRotate(self.screen)
                    self.obstacles_group.draw(self.screen)

            elif self.state == Game.State.LEVEL_SELECT:
                self.screen.blit(BACKGROUND_IMAGE, (0, 0))
                self.draw_level_select_menu()

            elif self.state == Game.State.GAME_OVER:
                self.screen.blit(BACKGROUND_IMAGE, (0, 0))
                self.draw_game_over_menu()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()