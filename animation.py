"""--------------------------------------------
sprite module. Contains classes that work as a layer over the pygame.Sprite.sprite class.
Have the following classes, inheriting represented by tabs:
    Sprite
        ↑MultiSprite
            ↑Animation
--------------------------------------------"""

__all__ = ['Animation']
__version__ = '0.1'
__author__ = 'David Flaity Pardo'

from sprite import MultiSprite

class Animation(MultiSprite):
    """Assciate a signal at the end of it. Could be threaded."""
    def __init__(self):
        self.time
        self.sprites

    def draw(self):
        pass