import os
import pygame

from src.entities.player import Player
from src.entities.obstacle import Obstacle
from src.constants import SCREEN_SIZE, PROJECT_DIR
from src.constants import RED, GREEN, BLACK, PURPLE, LIME, WHITE, BLUE_SEMI_TRANSPARENT, YELLOW_SEMI_TRANSPARENT, DARK_YELLOW

class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen

        self._big_font = pygame.font.Font(os.path.join(PROJECT_DIR, "resources/fonts/PUSAB_.ttf"), 60)
        self._mid_font = pygame.font.Font(os.path.join(PROJECT_DIR, "resources/fonts/PUSAB_.ttf"), 48)
        self._small_font = pygame.font.Font(os.path.join(PROJECT_DIR, "resources/fonts/PUSAB_.ttf"), 36)

    def draw_text(self, text: str, font: pygame.font.Font, color: tuple[int, int, int], x: int, y: int) -> None:
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        self._screen.blit(text_obj, text_rect)

    def draw_progress_bar(self, bar_width: int = 600, bar_height: int = 10, color: tuple[int, int, int] = LIME, current_distance: int | None = None, initial_portal_distance: int | None = None) -> None:
        if not current_distance or not initial_portal_distance: return

        progress = 1 - min(current_distance / initial_portal_distance, 1)
        fill_width = int(bar_width * progress)
        outline_rect = pygame.Rect(100, 20, bar_width, bar_height)
        fill_rect = pygame.Rect(100, 20, fill_width, bar_height)
        pygame.draw.rect(self._screen, color, fill_rect)
        pygame.draw.rect(self._screen, WHITE, outline_rect, 2)

    def draw_mask(self, mask: pygame.Mask, rect: pygame.rect.Rect, color: tuple[int, int, int, int] = BLUE_SEMI_TRANSPARENT) -> None:
        mask_surface = mask.to_surface(setcolor=color, unsetcolor=BLACK)
        mask_surface.set_colorkey(BLACK)
        mask_surface.set_alpha(100)
        self._screen.blit(mask_surface, rect.topleft)

    def draw_bounding_boxes(self, player: Player, obstacles: list[Obstacle], contact_point: tuple[int, int] | None = None) -> None:
        pygame.draw.rect(self._screen, RED, player.rect, 2)
        self.draw_mask(player.mask, player.rect, color=BLUE_SEMI_TRANSPARENT)
        for obstacle in obstacles:
            pygame.draw.rect(self._screen, GREEN, obstacle.rect, 2)
            if hasattr(obstacle, "mask"): self.draw_mask(obstacle.mask, obstacle.rect, color=YELLOW_SEMI_TRANSPARENT)
        if contact_point: pygame.draw.circle(self._screen, PURPLE, contact_point, 5)

    def draw_level_select_menu(self, available_levels: list[str], selected_level: int) -> None:
        self.draw_text("Select Level", self._big_font, BLACK, SCREEN_SIZE[0] // 2, 120)
        for i, level in enumerate(available_levels):
            name = os.path.basename(level.split(".")[0])
            color = BLACK
            x = SCREEN_SIZE[0] // 2
            y = 220 + i * 60
            if i == selected_level: pygame.draw.rect(self._screen, DARK_YELLOW, (x - 220, y - 24, 440, 48))
            self.draw_text(name, self._mid_font, color, x, y)
        self.draw_text("Use Up/Down and Enter to select", self._small_font, BLACK, SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] - 60)

    def draw_game_over_menu(self, level_complete: bool, game_over_selection: int, points: int) -> None:
        title = "Level Complete!" if level_complete else "Game Over"
        self.draw_text(title, self._big_font, BLACK, SCREEN_SIZE[0] // 2, 120)
        options = ["Retry", "Main Menu", "Quit"]
        for i, option in enumerate(options):
            x = SCREEN_SIZE[0] // 2
            y = 220 + i * 60
            color = BLACK
            if i == game_over_selection: pygame.draw.rect(self._screen, DARK_YELLOW, (x - 220, y - 24, 440, 48))
            self.draw_text(option, self._mid_font, color, x, y)
        self.draw_text(f"Points: {points}", self._small_font, BLACK, SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] - 80)