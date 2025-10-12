from enum import Enum
import pygame

class InputHandler:
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
            if isinstance(other, InputHandler.MenuOption): return self._wrap(self.value + other.value)
            return NotImplemented

        def __radd__(self, other):
            return self.__add__(other)

        def __sub__(self, other):
            if isinstance(other, int): return self._wrap(self.value - other)
            if isinstance(other, InputHandler.MenuOption): return self._wrap(self.value - other.value)
            return NotImplemented

        def __rsub__(self, other):
            if isinstance(other, int): return self._wrap(other - self.value)
            return NotImplemented

    def __init__(self, game):
        self.game = game
        self.gameover_selection = InputHandler.MenuOption.RETRY

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.game.running = False
            elif event.type == pygame.KEYDOWN: self.handle_keydown(event)

    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE: self.game.running = False
        elif self.game.state == self.game.State.LEVEL_SELECT: self.handle_level_select(event)
        elif self.game.state == self.game.State.GAME_OVER: self.handle_game_over(event)
        elif self.game.state == self.game.State.PLAYING: self.handle_playing(event)

    def handle_level_select(self, event):
        if event.key == pygame.K_UP: self.game.selected_level = (self.game.selected_level - 1) % len(self.game.available_levels)
        elif event.key == pygame.K_DOWN: self.game.selected_level = (self.game.selected_level + 1) % len(self.game.available_levels)
        elif event.key == pygame.K_RETURN: self.game.restart(self.game.available_levels[self.game.selected_level])

    def handle_game_over(self, event):
        if event.key == pygame.K_UP: self.gameover_selection -= 1
        elif event.key == pygame.K_DOWN: self.gameover_selection += 1
        elif event.key == pygame.K_RETURN:
            if self.gameover_selection == InputHandler.MenuOption.RETRY: self.game.restart(self.game.current_level_path)
            elif self.gameover_selection == InputHandler.MenuOption.MAIN_MENU: self.game.state = self.game.State.LEVEL_SELECT
            elif self.gameover_selection == InputHandler.MenuOption.QUIT: self.game.running = False

    def handle_playing(self, event):
        if event.key == pygame.K_TAB: self.game.debug_view = not self.game.debug_view
        elif self.game.player.is_dead: self.game.state = self.game.State.GAME_OVER