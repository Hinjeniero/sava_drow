"""--------------------------------------------
counter module. Contains classes that work as a layer over the pygame.Sprite.sprite class.
Have the following classes, inheriting represented by tabs:
    Counter
--------------------------------------------"""

__all__ = ['CounterSprite']
__version__ = '1.0'
__author__ = 'David Flaity Pardo'

import time
import pygame
import numpy
from external import ptext
from strings import FONT
from obj.sprite import Sprite, AnimatedSprite
from obj.utilities.colors import BLACK, WHITE
from obj.utilities.resizer import Resizer
from obj.utilities.exceptions import TooManySurfaces

#Max number of rendered texts before switching to rendering then in real time instead of pre-execution.
MAX_SURFACES_FOR_NORMAL_COUNTER = 1000  
class CounterSprite(AnimatedSprite):
    """CounterSprite class. Inherits from AnimatedSprite.
    A 'kind' of animated sprite, but not really. Simulates a decreasing counter by rendering the texts that should
    have a counter following the constructor arguments, and switching between them."""

    def __init__(self, id_, position, size, canvas_size, time_interval, max_second_count, **text_params):
        """Counter constructor."""
        self.count_interval = time_interval
        self.top_timer = max_second_count
        self.last_change = 0
        self.text_params = text_params
        super().__init__(id_, position, size, canvas_size, initial_surfaces=self.generate_surfaces(size, self.top_timer, self.count_interval, **self.text_params),\
                        animation_step=1)
    
    def generate_surfaces(self, size, max_count, count_interval, text_font = FONT,text_color =WHITE,\
                        text_outline =1, text_outline_color=BLACK, text_shadow_dir=(0.0, 0.0), text_lines=1, **xtra_params):
        """Called in the constructor.
        Done this way since we want to have the sprites created in advance, unless they are too much and done in real time."""
        surfaces = []
        interval = count_interval
        round_to = 0
        while not interval%1 == 0:
            round_to += 1
            interval *= 10
        if max_count/count_interval > MAX_SURFACES_FOR_NORMAL_COUNTER:
            raise TooManySurfaces("This type of counter cant create that many surfaces in advance")
        fontsizes = []
        for counter_time in numpy.arange(max_count, 0, -count_interval):
            number = round(counter_time, round_to)
            fontsizes.append(Resizer.max_font_size(str(number), size, text_font))
        fontsize_to_use = min(fontsizes)    #We want the same fontsize for all of the surfaces
        for counter_time in numpy.arange(max_count, 0, -count_interval):
            number = round(counter_time, round_to)
            surf = ptext.draw(str(number), (0, 0), fontsize=fontsize_to_use, fontname=text_font,\
                            owidth=text_outline, ocolor=text_outline_color, shadow=text_shadow_dir, surf=None)[0]
            surfaces.append(surf)
        return surfaces

    def check_counter(self):
        """Returns true if its time to update the counter sprite, false otherwise"""
        time_now = time.time()
        if time_now-self.last_change > self.count_interval:
            self.last_change = time_now
            return True
        return False
    
    def update(self):
        """Called after each drawing. Checks if its time to change the current sprite."""
        if self.check_counter():
            self.animation_frame()
            self.image = self.current_sprite()

    def draw_overlay(self, surface, offset=None):
        """no need for an overlay in a counter, so we override the superclass with an empty method."""
        pass

    def start_counter(self):
        """Starts/restarts the counter itself, and updates the start time."""
        self.animation_index = 0
        self.image = self.surfaces[self.animation_index]
        self.last_change = time.time()

    def set_canvas_size(self, canvas_size):
        """Set a new resolution for the container element (Can be the screen itself). 
        Updates self.real_rect and self.resolution.
        Args:
            canvas_size (Tuple-> int,int): Resolution to set.
        """
        super().set_canvas_size(canvas_size)
        self.surfaces = self.generate_surfaces(self.rect.size, **self.text_params)

    def set_enabled(self, state):
        """Sets the enabled attribute. If enabled is False, the element will be deactivated.
        In this case, also extends to the visible attribute.
        Args:
            state (boolean): The value to set.
        """
        super().set_enabled(state)
        super().set_visible(state)