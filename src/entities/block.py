from src.entities.obstacle import Obstacle

class Block(Obstacle):
    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)