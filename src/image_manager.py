import os
import pygame

from typing import Tuple
from src.constants import PROJECT_DIR

class ImageManager:
    def __init__(self) -> None:
        self._originals: dict[str, pygame.Surface] = {}
        self._cache: dict[tuple[str, Tuple[int, int]], pygame.Surface] = {}

    def _load_original(self, relative_path: str) -> pygame.Surface:
        if relative_path in self._originals: return self._originals[relative_path]
        full = os.path.join(PROJECT_DIR, relative_path)
        surf = pygame.image.load(full)
        surf = surf.convert_alpha() if surf.get_alpha() else surf.convert()
        self._originals[relative_path] = surf
        return surf

    def get(self, relative_path: str, size: Tuple[int, int]) -> pygame.Surface:
        cache_key = (relative_path, size)
        if cache_key in self._cache: return self._cache[cache_key]

        surface = self._load_original(relative_path)
        surface = pygame.transform.smoothscale(surface, size)

        self._cache[cache_key] = surface
        return surface