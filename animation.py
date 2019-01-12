"""--------------------------------------------
animation module. Contains classes that make up the cutscenes
with the game assets.
Have the following classes, inheriting represented by tabs:
    AnimationSprite
        ↑ScriptedSprite
    Animation
--------------------------------------------"""

__all__ = ['ScriptedSprite', 'Animation']
__version__ = '0.2'
__author__ = 'David Flaity Pardo'

#Python libraries
import time, pygame
#Selfmade libraries
from sprite import AnimatedSprite, MultiSprite
from decorators import time_it

class ScriptedSprite(AnimatedSprite):
    """Class ScriptedSprite. Inherits from AnimatedSprite.
    Has an animated sprite that moves accross different positions on the screen,
    all with a previous calculated 'script' of positions at each time.
    In short, each of the components of a cutscene or animation. Each of the sprites.
    Attributes:
        starting_position(:tuple: int, int):    Initial position of the sprite. Will return to it
                                                when it ends moving around.
        frames(:dict: list...): List of all the positions in each frame (following the current fps rate).
                                Is calculated beforehand. Each key is the fps rate. #TODO complete this attribute.
        index(int): Current position(frame) that the sprite is in.    
        fps(int):   Frames per second of the animation.
        fps_modes(:tuple: int...):  The different frames per second refresh rates
                                    that we want the Sprite to be ready for.
        frame_jump(int):    Jump of frames in each drawing. Normally is 1, to follow all the frames. 
                            If we want the sprite to speed up we can increase this value, thus skipping frames.
        time(float):    Duration of the actions of the sprite (The spotlight time of this sprite). In seconds.
        init_time(float):   The time in seconds at which this sprite animation starts. It's used when added to an animation.
        end_time(float):   The time in seconds at which this sprite animation ends. It's used when added to an animation.
    """

    def __init__(self, id_, position, size, canvas_size, fps, fps_modes, *sprite_list, sprite_folder=None, keywords=None, animation_delay=5):
        """ScriptedSprite constructor.
        Args:
            id_ (str):  Identifier of the Sprite.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            fps(int):   Frames per second of the animation.
            fps_modes(:tuple: int...):  The different frames per second refresh rates
                                        that we want the Sprite to be ready for.
            *sprite_list (:obj: pygame.Surface):    Surfaces that are to be added separated by commas.
            sprite_folder (str):    Path of the folder that contains the surfaces to be loaded.
            keywords(:tuple: str..., default=None): The specific images to load from a folder, in the case
                                                    that we don't want all of the contained ones.
            animation_delay (int):  Frames that occur between each animatino (Change of surface).
        """
        super().__init__(id_, position, size, canvas_size, *sprite_list, sprite_folder=sprite_folder, keywords=keywords, animation_delay=animation_delay)
        self.starting_pos = position
        self.frames = {}            #Distinct positions according to time
        self.index  = 0
        self.fps    = fps           #Current frames per second value of animations
        self.fps_modes  = fps_modes #All the possible fps modes
        self.frame_jump = 1         #To speedup the animation
        self.time   = 0
        self.init_time = 0
        self.end_time = 0

    def add_movement(self, init_pos, end_pos, time):
        """Adds a linear movement to the sprite. A complex movement
        can be achieved coupling a lot of those.s
        Args:
            init_pos(:tuple: int, int): Starting position of the movement on the screen. In pixels.
            end_pos(:tuple: int, int):  Ending position of the movement on the screen. In pixels.
            time(float):    Duration of the movement in seconds."""
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

    def update(self):
        """Changes the image to the next surface when its time.
        After that, it updates the position of the sprite, following the scripted
        movements. If it reaches the end of the movement, this method restarts all the attributes.
        Returns:
            (boolean):  True if the movement has ended. False otherwise."""
        super().update()    #This changes the image to the next frame.
        self.rect.topleft = self.frames[self.fps][self.index]
        self.index += self.frame_jump
        if self.index >= len(self.frames[self.fps]):
            self.restart()
            return True
        return False   

    def set_refresh_rate(self, fps):
        """Updates the refresh rate and the number of frames of the movements of this sprite.
        An higher fps will end in a smoother movement, with the counter of a heavier method. #TODO find some better way to describe this shit.
        Args:
            fps(int):   Frames per second to set as refresh rate."""
        draws_per_second = self.fps/self.next_frame_time
        self.next_frame_time = int(fps//draws_per_second)
        if self.index is not 0: #If it has started
            ratio = fps/self.fps
            self.index = int(ratio*self.index)
        self.fps = fps

    def restart(self):
        """Restarts the movement's attributes and the position to the initial ones."""
        self.index = 0
        self.rect.topleft = self.starting_pos

class Animation(object):
    """Animation class. Inherits from object.
    Its the frame that contains the sprites that make up an entire animation/cutscene.
    Controls the time at which each sprite triggers and ends, and when to stop the animation itself.
    Also has implemented the logic to replay a couple of times, forever or only play 1 time.
    Attributes:
        id(str):
        total_time(float):  Total duration of this animation. In seconds.
        init_time(float):   Initial time at which the animation started. In seconds from the UNIX 0.
        current_time(float):Time that the animation has been playing. In seconds.
        scripted_sprites(:list: ScriptedSprites):
        currently_playing(:list: ScriptedSprites):
        end_event(:obj: pygame.event):  Event that will be sent when the animation ends all of its loops. Notifies the end.
        loops(int): Number of times that the animation will play. If the input argument is 0/negative, it will continue decreasing.
                    No problem, it always compares to zero to end, so with those inputs the animation will play 'forever'.  
        """

    def __init__(self, name, end_event, loops=1):
        """Animation constructor.
        Args:
            name(str):
            end_event(:obj: pygame.event):
            loops(int, default=1):
        """
        self.id                 = name
        self.total_time         = 0
        self.init_time          = 0
        self.current_time       = 0
        self.scripted_sprites   = []
        self.currently_playing  = []
        self.end_event          = end_event
        self.loops              = loops

    def add_sprite(self, sprite, init_time, end_time):
        """Adds a sprite/component to the animation, with the starting time and 
        the ending time in seconds.
        Args:
            sprite(:obj: ScriptedSprite): Sprite to add.
            init_time(float):   Starting time of the animated sprite.
            end_time(float):    Ending time of the sprite's animation."""
        sprite.init_time = init_time
        sprite.end_time = end_time
        self.scripted_sprites.append(sprite)
        if end_time > self.total_time:
            self.total_time = end_time

    def set_loops(self, loops):
        """Sets the number of replays of this animation.
        If the input argument is 0 or negative, the animation plays forever.
        Args:
            loops(int): Number of replays for this animation. 0/negative makes it
                        play forever."""
        self.loops = loops

    def end_loop(self):
        """Ends a loop/replay on the animation. Decreases the loops in 1,
        and if after that the loops equal 0, sends the associated end event.
        Restarts the time attributes too."""
        self.loops -= 1
        self.init_time = 0
        self.current_time = 0
        for sprite in self.scripted_sprites:
            sprite.restart()
        if self.loops is 0:
            event = pygame.event.Event(self.end_event, command=self.id+"_end_animation")
            pygame.event.post(event)

    def play(self, surface):
        """Plays the animation. Draws a frame of it and updates the attributes to
        continue the animation the next time this method is called.
        Args:
            (:obj: pygame.Surface): Surface to draw the animation frame on."""
        self.update_clocks()
        if self.current_time > self.total_time:
            self.end_loop()
        else:
            for sprite in self.currently_playing:
                sprite.draw(surface)
            for sprite in self.scripted_sprites:    #WIth a for range i, could be deleted in a more efficient manner
                if self.current_time > sprite.init_time: 
                    self.currently_playing.append(sprite)
                    self.scripted_sprites.remove(sprite) #TODO check with init time, have naother list with all of the sprites

    def update_clocks(self):
        """Updates the time attributes. Called along with the play() method."""
        time_now = time.time()
        self.current_time = self.init_time - time.time()
        if self.init_time is 0: #First time playing this loop
            self.init_time = time_now

    def set_fps(self, fps):
        """Sets the refresh rate of the animation.
        Args:
            fps(int):   Frames per second to set as refresh rate."""
        for sprite in self.scripted_sprites:
            sprite.set_refresh_rate(fps)
    
    def speedup(self, ratio):
        """Speeds up the animation by increasing the frame jump attribute.
        Args:
            ratio(int|float):   The factor to speed up the animation.
                                e.g: A ratio 2 makes the animation go double the speed."""
        ratio = int(ratio)
        for sprite in self.scripted_sprites:
            sprite.time /= ratio
            sprite.frame_jump = ratio

    def shrink_time(self, ratio):
        """Divides the time of the animation by the ratio, getting a shorter animation by a factor of x
        Deletes frames in the process, irreversible method. This leads to a speed up animation.
        Args:
            ratio(int|float):   The factor to shrink the frames lists.
                                e.g: A ratio 2 deletes half the sprites, thus making the animation
                                half the duration.
                                A ratio 3 deletes 2/3 the sprites, thus making the animation one third
                                the duration."""
        ratio = int(ratio)
        for sprite in self.scripted_sprites:
            sprite.index //= ratio
            sprite.time /= ratio
            for key in sprite.frames.keys():
                new_frame_list = []
                for i in range(0, len(sprite.frames[key])):
                    if i%ratio != 0:
                        new_frame_list.append(sprite.frames[key][i])
                sprite.frames[key] = new_frame_list