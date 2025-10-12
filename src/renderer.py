import os
import pygame

from src.constants import SCREEN_SIZE, RED, GREEN, BLACK, PURPLE, PROJECT_DIR

class Renderer:
    def __init__(self, screen) -> None:
        self.screen = screen

        self.big_font = pygame.font.Font(os.path.join(PROJECT_DIR, "resources/fonts/PUSAB_.ttf"), 60)
        self.mid_font = pygame.font.Font(os.path.join(PROJECT_DIR, "resources/fonts/PUSAB_.ttf"), 48)
        self.small_font = pygame.font.Font(os.path.join(PROJECT_DIR, "resources/fonts/PUSAB_.ttf"), 36)

    def draw_text(self, text, font, color, x, y) -> None:
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(center=(x, y))
        self.screen.blit(text_obj, text_rect)

    def draw_progress_bar(self, bar_width=600, bar_height=10, color=(0, 200, 0), current_distance=None, initial_portal_distance=None) -> None:
        if not current_distance or not initial_portal_distance: return

        progress = 1 - min(current_distance / initial_portal_distance, 1)
        fill_width = int(bar_width * progress)
        outline_rect = pygame.Rect(100, 20, bar_width, bar_height)
        fill_rect = pygame.Rect(100, 20, fill_width, bar_height)
        pygame.draw.rect(self.screen, color, fill_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), outline_rect, 2)

    def draw_mask(self, mask, rect, color=(0, 0, 255, 100)) -> None:
        mask_surface = mask.to_surface(setcolor=color, unsetcolor=BLACK)
        mask_surface.set_colorkey(BLACK)
        mask_surface.set_alpha(100)
        self.screen.blit(mask_surface, rect.topleft)

    def draw_bounding_boxes(self, player, obstacles, contact_point=None) -> None:
        pygame.draw.rect(self.screen, RED, player.rect, 2)
        self.draw_mask(player.mask, player.rect, color=(0, 0, 255, 100))
        for obstacle in obstacles:
            pygame.draw.rect(self.screen, GREEN, obstacle.rect, 2)
            if hasattr(obstacle, "mask"): self.draw_mask(obstacle.mask, obstacle.rect, color=(255, 255, 0, 100))
        if contact_point: pygame.draw.circle(self.screen, PURPLE, contact_point, 5)

    def draw_level_select_menu(self, available_levels: list[str], selected_level: int) -> None:
        self.draw_text("Select Level", self.big_font, BLACK, SCREEN_SIZE[0] // 2, 120)
        for i, level in enumerate(available_levels):
            name = os.path.basename(level)
            color = (0, 0, 0)
            x = SCREEN_SIZE[0] // 2
            y = 220 + i * 60
            if i == selected_level: pygame.draw.rect(self.screen, (200, 200, 0), (x - 220, y - 24, 440, 48))
            self.draw_text(name, self.mid_font, color, x, y)
        self.draw_text("Use Up/Down and Enter to select", self.small_font, BLACK, SCREEN_SIZE[0]//2, SCREEN_SIZE[1] - 60)

    def draw_game_over_menu(self, level_complete: bool, game_over_selection: int, points: int) -> None:
        title = "Level Complete!" if level_complete else "Game Over"
        self.draw_text(title, self.big_font, BLACK, SCREEN_SIZE[0]//2, 120)
        options = ["Retry", "Main Menu", "Quit"]
        for i, opt in enumerate(options):
            x = SCREEN_SIZE[0]//2
            y = 220 + i * 60
            color = BLACK
            if i == game_over_selection: pygame.draw.rect(self.screen, (200, 200, 0), (x - 220, y - 24, 440, 48))
            self.draw_text(opt, self.mid_font, color, x, y)
        self.draw_text(f"Points: {points}", self.small_font, BLACK, SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] - 80)