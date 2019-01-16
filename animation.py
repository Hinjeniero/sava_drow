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

    def __init__(self, id_, position, size, canvas_size, fps, fps_modes, *sprite_list, sprite_folder=None, keywords=None,
                animation_delay=5, resize_mode='fit'):
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
        super().__init__(id_, position, size, canvas_size, *sprite_list, sprite_folder=sprite_folder, keywords=keywords,\
                        animation_delay=animation_delay, resize_mode=resize_mode)
        self.starting_pos = position
        self.frames = {}            #Distinct positions according to time
        self.real_frames = {}       #Real position (0->1 in the screen)
        self.index  = 0
        self.fps    = fps           #Current frames per second value of animations
        self.fps_modes  = fps_modes #All the possible fps modes
        self.frame_jump = 1         #To speedup the animation
        self.time       = 0
        self.init_time  = 0         #Used when added to an animation
        self.end_time   = 0         #Used when added to an animation
        self.layer      = 0         #Used when added to an animation
        ScriptedSprite.generate(self)

    @staticmethod
    def generate(self):
        for fps in self.fps_modes:
            self.frames[fps]        = []
            self.real_frames[fps]   = []

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
            total_frames = int(time*fps)
            for frame_index in range(0, total_frames):
                frame_pos = tuple(int(init+(frame_index*mvnt/total_frames)) for init, mvnt in zip(init_pos, vector_mvnt))
                self.frames[fps].append(frame_pos)
                self.real_frames[fps].append(tuple(frame_axis/res for frame_axis, res in zip(frame_pos, self.resolution)))
        self.time += time

    def set_canvas_size(self, resolution):
        super().set_canvas_size(resolution)
        for fps in self.fps_modes:
            del self.frames[fps][:]
            for real_frame in self.real_frames[fps]:
                self.frames[fps].append(tuple(real_axis*res for real_axis, res in zip(real_frame, self.resolution)))

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

    def restart(self):
        """Restarts the movement's attributes and the position to the initial ones."""
        self.index = 0
        self.rect.topleft = self.starting_pos

    def set_refresh_rate(self, fps):
        """Updates the refresh rate and the number of frames of the movements of this sprite. Also fix the frame index if the sprite was active.
        An higher fps will end in a smoother movement, with the counter of a heavier method. #TODO find some better way to describe this shit.
        Args:
            fps(int):   Frames per second to set as refresh rate."""
        draws_per_second = self.fps/self.next_frame_time
        self.next_frame_time = int(fps//draws_per_second)
        if self.next_frame_time < 1:
            self.next_frame_time = 1
        if self.index is not 0: #If it has started
            ratio = fps/self.fps
            self.index = int(ratio*self.index)
        self.fps = fps

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
        self.all_sprites        = []    #To make methods to all the sprites in one line
        self.idle_sprites       = []
        self.playing_sprites    = []
        self.done_sprites       = []
        self.end_event          = end_event
        self.loops              = loops

    def set_resolution(self, resolution):
        for sprite in self.all_sprites:
            sprite.set_canvas_size(resolution)

    def add_sprite(self, sprite, init_time, end_time, layer=0):
        """Adds a sprite/component to the animation, with the starting time and 
        the ending time in seconds.
        Args:
            sprite(:obj: ScriptedSprite): Sprite to add.
            init_time(float):   Starting time of the animated sprite.
            end_time(float):    Ending time of the sprite's animation.
            layer(int, default=0):  Layer in which the sprite will be drawn."""
        sprite.init_time = init_time
        sprite.end_time = end_time
        sprite.layer = layer
        self.all_sprites.append(sprite)
        self.idle_sprites.append(sprite)
        self.sort_sprites()
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
        if self.loops >= 0:
            self.loops -= 1
        self.init_time = 0
        self.current_time = 0
        self.restart()
        if self.loops is 0: #Only will end for self.loops over zero.
            event = pygame.event.Event(self.end_event, command=self.id+"_end_animation")
            pygame.event.post(event)

    def sort_sprites(self, idle=True, playing=False):
        """sorts by init time or end itme, the idle sprites and the playing sprites."""
        if idle:
            self.idle_sprites.sort(key=lambda spr: spr.init_time)
        if playing:
            self.playing_sprites.sort(key=lambda sprite: (sprite.layer, sprite.end_time))

    def restart(self):  #TODO CHECK OUT THIS METHOD
        for sprite in self.playing_sprites:
            sprite.restart()
            self.idle_sprites.append(sprite)
        for sprite in self.done_sprites:
            self.idle_sprites.append(sprite)
        self.clear_animation_cache()
        self.sort_sprites()

    def clear_animation_cache(self):
        del self.playing_sprites[:]
        del self.done_sprites[:]

    def play(self, surface, infinite=False):
        """Plays the animation. Draws a frame of it and updates the attributes to
        continue the animation the next time this method is called.
        Args:
            (:obj: pygame.Surface): Surface to draw the animation frame on."""
        self.update_clocks()
        self.trigger_sprites()
        if not infinite and (self.current_time > self.total_time):
            self.end_loop()
        else:
            for sprite in self.playing_sprites:
                sprite.draw(surface)

    def draw(self, surface):
        """Acronym"""
        self.play(surface)

    def update_clocks(self):
        """Updates the time attributes. Called along with the play() method."""
        time_now = time.time()
        if self.init_time is 0: #First time playing this loop
            self.init_time = time_now
        self.current_time = time_now-self.init_time

    def trigger_sprites(self):
        #Checking sprites that have completed their animation to end them.
        indexes_to_end = []
        for index in range (0, len(self.playing_sprites)):
            if self.current_time > self.playing_sprites[0].end_time:
                indexes_to_end.append(index)
        self.end_sprites(*indexes_to_end)

        #Checking sprites to trigger/start.
        indexes_to_start = []
        for index in range (0, len(self.idle_sprites)):
            if self.current_time > self.idle_sprites[index].init_time:
                indexes_to_start.append(index)
        self.init_sprites(*indexes_to_start)

    def init_sprites(self, *indexes):
        offset = 0
        for index in indexes:
            sprite = self.idle_sprites[index-offset]
            self.playing_sprites.append(sprite)
            del self.idle_sprites[index-offset]
            offset+=1
        self.sort_sprites(idle=True, playing=True)

    def end_sprites(self, *indexes):
        offset = 0
        for index in indexes:
            sprite = self.playing_sprites[index-offset]
            sprite.restart()
            self.done_sprites.append(sprite)
            del self.playing_sprites[index-offset]
            offset+=1

    def set_fps(self, fps):
        """Sets the refresh rate of the animation.
        Args:
            fps(int):   Frames per second to set as refresh rate."""
        for sprite in self.all_sprites:
            sprite.set_refresh_rate(fps)
    
    def speedup(self, ratio):
        """Speeds up the animation by increasing the frame jump attribute.
        If wanted to speed down, a number between 0 and 1 must be used.
        Args:
            ratio(int|float):   The factor to speed up the animation.
                                e.g: A ratio 2 makes the animation go double the speed.
                                ratio 0.5 makes it go half the speed."""
        ratio = int(ratio)
        for sprite in self.all_sprites:
            sprite.time /= ratio
            sprite.frame_jump *= ratio

    def set_speed(self, speed):
        """Sets the speed of the animation by setting the frame jump attribute and time.
        A speed of 1 is the default speedof the animation.
        Args:
            ratio(int|float):   The factor to speed up the animation.
                                e.g: A ratio 2 makes the animation go double the speed."""
        speed = int(speed)
        for sprite in self.all_sprites:
            sprite.time /= (speed/sprite.frame_jump)
            sprite.frame_jump = speed    

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
        for sprite in self.all_sprites:
            sprite.index //= ratio
            sprite.time /= ratio
            for key in sprite.frames.keys():
                new_frame_list = []
                for i in range(0, len(sprite.frames[key])):
                    if i%ratio != 0:
                        new_frame_list.append(sprite.frames[key][i])
                sprite.frames[key] = new_frame_list

class LoopedAnimation(Animation):
    """LoopedAnimation class. Inherits from Animation.
    The sprites in this animation will loop back as soon as they are done.
    In this way specific sprites can be restarted before than others.
    Has no loops funcionality, plays forever.
    All the sprites are called from the get-go, no triggering based in time.
    It's like a basic and lite version of Animation, perfect for menu animations and such.
    If you want an infinite animation, but with different trigger times for sprites, use Animation
    with loops set to 0 or a negative number.
    """
    def __init__(self, name, loops=1):
        super().__init__(name, -1, -1)

    def trigger_sprites(self):
        #Checking sprites to trigger/start. They are sorted, sooo...
        indexes_to_start = []
        for index in range (0, len(self.idle_sprites)):
            if self.current_time > self.idle_sprites[index].init_time:
                indexes_to_start.append(index)
                continue    #Next iteration
            self.init_sprites(*indexes_to_start)
            break

    def play(self, surface):
        """Plays the animation. Draws a frame of it and updates the attributes to
        continue the animation the next time this method is called.
        Args:
            (:obj: pygame.Surface): Surface to draw the animation frame on."""
        super().play(surface, infinite=True)