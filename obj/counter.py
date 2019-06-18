import time
import pygame
import numpy
from external import ptext
from strings import FONT
from obj.sprite import Sprite, AnimatedSprite
from obj.utilities.colors import BLACK, WHITE
from obj.utilities.resizer import Resizer
from obj.utilities.exceptions import TooManySurfaces

MAX_SURFACES_FOR_NORMAL_COUNTER = 1000
class CounterSprite(AnimatedSprite):
    """A 'kind' of animated sprite, but not really."""
    def __init__(self, id_, position, size, canvas_size, time_interval, max_second_count, **text_params):
        self.count_interval = time_interval
        self.top_timer = max_second_count
        self.last_change = 0
        self.text_params = text_params
        super().__init__(id_, position, size, canvas_size, initial_surfaces=self.generate_surfaces(size, self.top_timer, self.count_interval, **self.text_params),\
                        animation_step=1)
    
    def generate_surfaces(self, size, max_count, count_interval, text_font = FONT,text_color =WHITE,\
                        text_outline =1, text_outline_color=BLACK, text_shadow_dir=(0.0, 0.0), text_lines=1, **xtra_params):
        """Done this way since we want to have the sprites created in advance, unless they are too much."""
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
        if self.check_counter():
            self.animation_frame()
            self.image = self.current_sprite()

    def draw_overlay(self, surface, offset=None):
        """no need for an overlay in a counter"""
        pass

    def start_counter(self):
        self.animation_index = 0
        self.image = self.surfaces[self.animation_index]
        self.last_change = time.time()

    def set_canvas_size(self, canvas_size):
        super().set_canvas_size(canvas_size)
        self.surfaces = self.generate_surfaces(self.rect.size, **self.text_params)

    def set_enabled(self, state):
        super().set_enabled(state)
        super().set_visible(state)

# class InstantCounterSprite(Sprite):
#    """A 'kind' of animated sprite, but not really. DO NOT CREATE THE SURFACES IN ADVANCE"""
#     def __init__(self, id_, position, size, canvas_size, time_interval, max_second_count, **text_params):
#         CounterSprite.generate(self)
#         self.count_interval = time_interval
#         self.last_change = 0
#         super().__init__(id_, position, size, canvas_size)
    
#     def generate(size):
#         """Done this way since we want to have the sprites created in advance, unless they are too much."""
        
#         return surfaces

#     def check_counter(self):
#         """Returns true if its time to update the counter sprite, false otherwise"""
#         time_now = time.time()
#         if time_now-self.last_change > self.count_interval:
#             self.last_change = time_now
#             return True
#         return False
    
#     def update(self):
#         if self.check_counter():
#             self.animation_frame()

#     def draw(self):
#         super().draw()
#         self.check_counter()

#     def draw_overlay(self, surface, offset=None):
#         """no need for an overlay in a counter"""
#         pass

#     def animation_frame(self):
#         """no need for this neither in a counter"""
#         pass

#     def set_canvas_size(self):