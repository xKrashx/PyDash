from src.entities.obstacle import Obstacle

class Portal(Obstacle):
    def __init__(self, image, position, *groups):
        super().__init__(image, position, *groups)