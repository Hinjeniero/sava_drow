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

from sprite import AnimatedSprite, MultiSprite

class ScriptedSprite(AnimatedSprite):
    def __init__(self, id_, size, canvas_size, fps, *sprite_list, sprite_folder=None, animation_delay=5):
        super().__init__(id_, (0, 0), size, canvas_size, *sprite_list, sprite_folder, animation_delay)
        self.frames = {}    #Distinct positions according to time
        self.fps    = fps   #Can be a tuple, can be an int

    def add_movement(self, init_pos, end_pos, time):
        if not isinstance(self.fps, tuple):
            self.fps = self.fps,
        vector_mvnt = tuple(end-init for end, init in zip(end_pos, init_pos))
        for fps in self.fps:
            self.frames[fps] = []
            total_frames = int(time*fps)
            for frame_index in range(0, total_frames):
                frame_pos = tuple(frame_index*mvnt/total_frames for mvnt in vector_mvnt)
                self.frames[fps].append(frame_pos)

class Animation(MultiSprite):
    """Assciate a signal at the end of it. Could be threaded."""
    def __init__(self):
        self.total_time = 0

    def draw(self):
        pass