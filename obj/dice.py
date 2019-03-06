import pygame
import random
from settings import USEREVENTS
from obj.sprite import AnimatedSprite
from obj.utilities.decorators import run_async
class Dice(AnimatedSprite):
    def __init__(self, id_, position, size, canvas_size, **params):
        super().__init__(id_, position, size, canvas_size, **params)

    @run_async
    def throw(self):
        pygame.time.set_timer(USEREVENTS.BOARD_USEREVENT, 100)

    def increase_animation_delay(self):
        self.next_frame_time += 1
        if self.next_frame_time >= len(self.surfaces):
            self.next_frame_time -= 1
            pygame.time.set_timer(USEREVENTS.BOARD_USEREVENT, 0)    #Disabling this timer

    def animation_frame(self):
        """Changes the current showing surface (changing the index) to the next one."""
        if self.hover:   #If hovering over it
            super().animation_frame

    def randomize(self):
        pass