from src.entities.obstacle import Obstacle

class Coin(Obstacle):
    def __init__(self, image, pos, *groups) -> None:
        super().__init__(image, pos, *groups)