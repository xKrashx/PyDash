import pygame

from enum import Enum

class InputHandler:
    class MenuOption(Enum):
        RETRY = 0
        MAIN_MENU = 1
        QUIT = 2
        COUNT = 3

        def __int__(self) -> int:
            return self.value

        def __index__(self) -> int:
            return int(self)

        def __eq__(self, other) -> bool:
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

    def __init__(self, game) -> None:
        self._game = game
        self._game_over_selection: InputHandler.MenuOption = InputHandler.MenuOption.RETRY

    @property
    def game_over_selection(self) -> MenuOption:
        return self._game_over_selection

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self._game.running = False
            elif event.type == pygame.KEYDOWN: self.handle_keydown(event)

    def handle_keydown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE: self._game.running = False
        elif self._game.state == self._game.State.LEVEL_SELECT: self.handle_level_select(event)
        elif self._game.state == self._game.State.GAME_OVER: self.handle_game_over(event)
        elif self._game.state == self._game.State.PLAYING: self.handle_playing(event)

    def handle_level_select(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_UP: self._game.selected_level = (self._game.selected_level - 1) % len(self._game.available_levels)
        elif event.key == pygame.K_DOWN: self._game.selected_level = (self._game.selected_level + 1) % len(self._game.available_levels)
        elif event.key == pygame.K_RETURN: self._game.restart(self._game.available_levels[self._game.selected_level])

    def handle_game_over(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_UP: self._game_over_selection -= 1
        elif event.key == pygame.K_DOWN: self._game_over_selection += 1
        elif event.key == pygame.K_RETURN:
            if self._game_over_selection == InputHandler.MenuOption.RETRY: self._game.restart(self._game.current_level_path)
            elif self._game_over_selection == InputHandler.MenuOption.MAIN_MENU: self._game.state = self._game.State.LEVEL_SELECT
            elif self._game_over_selection == InputHandler.MenuOption.QUIT: self._game.running = False

    def handle_playing(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_TAB: self._game.debug_view = not self._game.debug_view
        elif self._game.player.is_dead: self._game.state = self._game.State.GAME_OVER