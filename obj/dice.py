import pygame
import random
from settings import USEREVENTS
from obj.sprite import AnimatedSprite
from obj.utilities.decorators import run_async
class Dice(AnimatedSprite):
    def __init__(self, id_, position, size, canvas_size, shuffle_time=0, rotate_kw='rot', result_kw='res', **params):
        """Shuffle time in miliseconds"""
        super().__init__(id_, position, size, canvas_size, **params)
        self.shuffle_time = shuffle_time
        self.event = pygame.event.Event(USEREVENTS.BOARD_USEREVENT, command='dice', value=None)
        self.rotate_kw = rotate_kw
        self.result_kw = result_kw
        '''for i in range(0, len(self.names)):
            if self.rotate_kw in self.names[i]:
                self.image = self.surfaces[i]
                break'''

    @run_async
    def shuffle(self):
        if not self.shuffle_time:
            pygame.time.set_timer(USEREVENTS.BOARD_USEREVENT, 100)
        else:
            pygame.time.set_timer(USEREVENTS.BOARD_USEREVENT, self.shuffle_time//len(self.surfaces))

    def increase_animation_delay(self):
        self.next_frame_time += 1
        if self.next_frame_time >= len(self.surfaces):
            self.next_frame_time -= 1
            pygame.time.set_timer(USEREVENTS.BOARD_USEREVENT, 0)    #Disabling this timer
            self.throw()

    def animation_frame(self):
        """Changes the current showing surface (changing the index) to the next one."""
        if self.hover and self.enabled:   #If hovering over it
            while True:
                super().animation_frame()
                if self.rotate_kw in self.names[self.animation_index]:
                    break

    def throw(self):
        self.event.value = random.randint(1, 6)
        pygame.event.post(self.event)
        print("RESULT IS "+str(self.event.value))
        for i in range(0, len(self.names)):
            if self.result_kw in self.names[i] and str(self.event.value) in self.names[i]:
                print("FOUNG THE RESULT SPRITE "+self.names[i])
                self.image = self.surfaces[i]
                #self.enabled = False
                return