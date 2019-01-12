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

import time, pygame
from sprite import AnimatedSprite, MultiSprite
from decorators import time_it

class ScriptedSprite(AnimatedSprite):
    def __init__(self, id_, position, size, canvas_size, fps, fps_modes, *sprite_list, sprite_folder=None, keywords=None, animation_delay=5):
        super().__init__(id_, position, size, canvas_size, *sprite_list, sprite_folder=sprite_folder, keywords=keywords, animation_delay=animation_delay)
        self.starting_pos = position
        self.frames = {}            #Distinct positions according to time
        self.index  = 0
        self.fps    = fps           #Current frames per second value of animations
        self.fps_modes  = fps_modes  #All the possible fps modes
        self.frame_jump = 1         #To speedup the animation
        self.time   = 0

    def add_movement(self, init_pos, end_pos, time):
        self.starting_pos = init_pos
        if not isinstance(self.fps_modes, tuple):
            self.fps_modes = self.fps_modes,
        vector_mvnt = tuple(end-init for end, init in zip(end_pos, init_pos))
        for fps in self.fps_modes:
            try:
                self.frames[fps]
            except KeyError:
                self.frames[fps] = []
            total_frames = int(time*fps)
            for frame_index in range(0, total_frames):
                frame_pos = tuple(int(init+(frame_index*mvnt/total_frames)) for init, mvnt in zip(init_pos, vector_mvnt))
                self.frames[fps].append(frame_pos)
        self.time += time

    def draw(self, surface):
        super().draw(surface)
        self.rect.topleft = self.frames[self.fps][self.index]
        self.index += self.frame_jump
        if self.index >= len(self.frames[self.fps]):
            self.restart()
            return False
        return True

    def set_refresh_rate(self, fps):
        draws_per_second = self.fps/self.next_frame_time
        self.next_frame_time = int(fps//draws_per_second)
        if self.index is not 0: #If it has started
            ratio = fps/self.fps
            self.index = int(ratio*self.index)
        self.fps = fps

    def restart(self):
        self.index = 0
        self.rect.topleft = self.starting_pos

class Animation(object):
    """Assciate a signal at the end of it. Could be threaded."""
    def __init__(self, name, end_event, loops=1):
        self.id                 = name
        self.total_time         = 0
        self.init_time          = 0
        self.scripted_sprites   = []
        self.end_event          = end_event
        self.loops              = loops

    def add_sprite(self, sprite):
        self.scripted_sprites.append(sprite)
        if sprite.time > self.total_time:
            self.total_time = sprite.time
        #self.total_time += sprite.time

    def set_loops(self, loops):
        self.loops = loops

    def end_loop(self):
        self.loops -= 1
        self.init_time = 0
        for sprite in self.scripted_sprites:
            sprite.restart()
        if self.loops is 0:
            event = pygame.event.Event(self.end_event, command=self.id+"_end_animation")
            pygame.event.post(event)

    def play(self, surface):
        if self.init_time is 0:
            self.init_time = time.time()
        if time.time()-self.init_time > self.total_time:
            self.end_loop()
        for sprite in self.scripted_sprites:
            sprite.draw(surface)

    def set_fps(self, fps):
        for sprite in self.scripted_sprites:
            sprite.set_refresh_rate(fps)
    
    def speedup(self, ratio):
        ratio = int(ratio)
        for sprite in self.scripted_sprites:
            sprite.time /= ratio
            sprite.frame_jump = ratio

    def shrink_time(self, ratio):
        """Divides the time of the animation by the ratio, getting a shorter animation by a factor of x"""
        ratio = int(ratio)
        print("RATIO "+str(ratio))
        for sprite in self.scripted_sprites:
            sprite.index //= ratio
            sprite.time /= ratio
            for key in sprite.frames.keys():
                new_frame_list = []
                for i in range(0, len(sprite.frames[key])):
                    if i%ratio != 0:
                        new_frame_list.append(sprite.frames[key][i])
                sprite.frames[key] = new_frame_list