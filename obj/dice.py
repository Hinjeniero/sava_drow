from Sprite import AnimatedSprite

class Dice(AnimatedSprite):
    def __init__(self, id_, position, size, canvas_size, **params):
        super().__init__(id_, position, size, canvas_size, **params)
        self.result = None

    def randomize(self):
        pass