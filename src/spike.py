from src.obstacle import Obstacle

class Spike(Obstacle):
    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)