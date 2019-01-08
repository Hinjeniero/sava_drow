"""--------------------------------------------
sprite module. Contains classes that work as a layer over the pygame.Sprite.sprite class.
Have the following classes, inheriting represented by tabs:
    Sprite
        ↑TextSprite
        ↑AnimatedSprite
        ↑MultiSprite
--------------------------------------------"""

__all__ = ['Animation']
__version__ = '0.1'
__author__ = 'David Flaity Pardo'

from sprite import AnimatedSprite

class Animation(AnimatedSprite):
    """Assciate a signal at the end of it. Could be threaded."""
    def __init__(self):
        pass

    def draw(self):
        pass