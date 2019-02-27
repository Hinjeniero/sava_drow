"""--------------------------------------------
screen module. Contains classes that work as entire screens to be shown on display.
Have the following classes, inheriting represented by tabs:
    Screen
        ↑LoadingScreen
--------------------------------------------"""
__all__ = ['Screen', 'LoadingScreen']
__version__ = '0.2'
__author__ = 'David Flaity Pardo'
from os import listdir
from os.path import isfile, join, dirname
import pygame
from obj.utilities.utility_box import UtilityBox
from obj.ui_element import TextSprite
from obj.sprite import Sprite, AnimatedSprite
from obj.utilities.exceptions import BadSpriteException, BadStateException
from obj.utilities.logger import Logger as LOG
from obj.utilities.decorators import run_async
from obj.utilities.synch_dict import Dictionary
from settings import PATHS, STATES, EXTENSIONS, SOUND_PARAMS, INIT_PARAMS

from animation_generator import AnimationGenerator

class Screen(object):
    """Screen class. Controls an entire 'screen' (like a desktop).
    Purpose is to have an "interface" with a bit of a standard schema and functionality.
    Screen itself should be overloaded, otherwise it's kinda a bland class.
    General class attributes:
        __default_config (:dict:): Contains parameters about the text looks and positioning.
            background_path (str):  Path to the background image.
            music_path (str):   Path to the music file.
            sound_path (str):   Path to the sound effect file.
    Attributes:
        id (str):   Identifier of this screen.
        event_id (int): Event id associated with this screen. Can be used to overwrite the event ids of added elements.
        params (:dict:):    Dict of keywords and values as parameters to create the screen.
                            background_path, music_path, sound_path, dialog_active.
        background (:obj: pygame.Surface):  The background image/surface. Will be drawn at resolution size.
        dialog (:obj: UIElement->Dialog):   Dialog to be shown when it's needed, like to exit or confirm some changes.
                                            It's optional.
        resolution (:tuple: int, int):  Resolution of the current display.
        music (:obj: Music):    Music theme object.
        sound (:obj: Sound):    Sound effect object.
    """
    __default_config = {'background_path'   : None,
                        'animated_background': None,
                        'songs_paths'       : UtilityBox.get_all_files(PATHS.COMMON_SONGS, *EXTENSIONS.MUSIC_FORMATS),
                        'scroll_image'      : None,
                        'scroll_texture'    : None
    }
    SOUND_CHANNELS = []
    SOUNDS = Dictionary()
    
    def __init__(self, id_, event_id, resolution, **params):
        """Screen constructor.
        Args:
            id_ (str):  Identifier of the Screen.
            event_id (int): Identifier of the event of the screen.
            resolution (:tuple: int, int):  Resolution of the current display.
            dialog (:obj: UIElement->Dialog, optional): Important actions dialog of the screen.
            **params (:dict:):  Dict of keywords and values as parameters to create the Screen.
                                background_path, music_path, sound_path, dialog_active.
        """
        self.id         = id_
        self.event_id   = event_id
        self.params     = params
        self.resolution = resolution
        #Sprites
        self.background = None  #Created in generate
        self.dialog     = None
        self.dialogs    = pygame.sprite.Group()
        self.sprites    = pygame.sprite.OrderedUpdates()
        self.hit_sprite = None
        #Sound & Music
        self.songs      = []    #Created in generate
        self.music_chan = None  #Created in generate
        self.song_index = 0
        self.sound_vol  = 0     #Created in generate
        self.playing    = False #Playing music?
        #State machine
        self.state      = STATES.SCREEN[0]
        #Animations
        self.animations = []
        self.animation  = None  #The current playing animation
        self.animated_background = False
        #Scroll
        self.scroll_offset = (0, 0)
        self.scroll_sprite = None
        self.scroll_length = 0
        Screen.generate(self)

    @staticmethod
    def generate(self):
        UtilityBox.join_dicts(self.params, Screen.__default_config.copy())
        #GRAPHICS
        if self.params['animated_background']:
            self.background = self.params['animated_background']
            self.animated_background = True
        else:
            self.background = Sprite(self.id+'_background', (0, 0), self.resolution, self.resolution,\
                                    resize_mode='fill', texture=self.params['background_path'])
        #SOUNDS
        if self.params['songs_paths']:
            self.music_chan = UtilityBox.get_sound_channel()
            self.music_chan.set_volume(SOUND_PARAMS.INIT_VOLUME)
            for song_path in self.params['songs_paths']:
                self.songs.append(song_path)
        self.sound_vol = SOUND_PARAMS.INIT_VOLUME
        #Adding to the LUT of sounds
        for sound_path in UtilityBox.get_all_files(PATHS.SOUNDS_FOLDER, '.ogg', '.wav'):
            if not Screen.SOUNDS.get_item(sound_path):
                Screen.SOUNDS.add_item(sound_path, pygame.mixer.Sound(file=sound_path))
        #Adding the sound channels
        if len(Screen.SOUND_CHANNELS) is 0:
            for _ in range (0, SOUND_PARAMS.SOUND_CHANNELS_AMMOUNT):
                Screen.SOUND_CHANNELS.append(UtilityBox.get_sound_channel())

    def add_dialogs(self, *dialogs):
        for dialog in dialogs:
            dialog.set_visible(False)
            self.dialogs.add(dialog)

    def add_animation(self, animation):
        """Sets the animatino and linlks it with a specific staet"""
        if not any(animation.id in contained_anim.id for contained_anim in self.animations):
            self.animations.append(animation) 
            self.animation = animation

    def play_animation(self, animation_id):
        for animation in self.animations:
            if animation.id in self.animations:
                self.animation = animation
                return True
        LOG.log('WARNING', 'The animation ', animation_id, 'was not found in ', self.id)
        return False

    def update_fps(self, fps):
        for animation in self.animations:
            animation.set_fps(fps)

    def set_state(self, state):
        state = state.lower()
        if state not in STATES.SCREEN:
            raise BadStateException('The state '+state+' doesn`t exist in '+self.id)
        self.state = state

    def has_music(self):
        return True if self.music_chan else False

    def play_music(self):
        if len(self.songs) is not 0 and not self.playing:
            if self.music_chan.get_busy():
                self.music_chan.unpause()
            else:
                song = pygame.mixer.Sound(file=self.songs[self.song_index])
                self.music_chan.play(song, loops=-1)
            self.playing = True

    def pause_music(self):
        if self.playing:
            self.music_chan.pause()
            self.playing = False

    def set_volume(self, volume, sound=False, music=True):
        if sound:
            self.sound_vol = volume
        if music and self.music_chan:
            self.music_chan.set_volume(volume)

    @run_async
    def hijack_music(self, song_path):
        """For easter eggs"""
        if self.music_chan:
            self.music_chan.stop() 
            song = pygame.mixer.Sound(file=song_path)
            self.music_chan.play(song, loops=-1)
            if not self.playing:    #Continue playing if it was playing before
                self.music_chan.pause()      

    @run_async
    def hijack_sound(self, sound_path):
        """For easter eggs, substitutes everything except secret sounds"""
        sound = pygame.mixer.Sound(file=sound_path)
        for key in Screen.SOUNDS.keys():
            if 'secret' not in key:
                Screen.SOUNDS.add_item(key, sound)

    def set_song(self, song_path):
        index = 0
        if self.params['songs_paths']:
            for song in self.params['songs_paths']:
                if song_path in song:
                    LOG.log('debug', 'Changing song to ', song,' in ', self.id)
                    song = pygame.mixer.Sound(file=song)
                    self.music_chan.play(song, loops=-1)
                    if not self.playing:
                        self.music_chan.pause()
                    self.song_index = index
                    return
            LOG.log('debug', 'Didn`t find ', song_path,' in ', self.id)

    def play_sound(self, sound_id):
        for sound in Screen.SOUNDS.keys():
            if sound_id in sound or sound in sound_id:
                channel = None
                for channel in Screen.SOUND_CHANNELS:
                    if not channel.get_busy():
                        channel.set_volume(self.sound_vol)
                        channel.play(Screen.SOUNDS.get_item(sound))
                        return True
        return False


    def event_handler(self, event, keys_pressed, mouse_buttons_pressed, mouse_movement=False, mouse_pos=(0, 0)):
        """Handles any pygame event. This allows for user interaction with the object.
        Args:
            event (:obj: pygame.event): Event received from the pygame queue.
            keys_pressed (:dict: pygame.keys):  Dict in which the keys are keys and the items booleans.
                                                Said booleans will be True if that specific key was pressed.
            mouse_buttons_pressed (:list: booleans):    List with 3 positions regarding the 3 normal buttons on a mouse.
                                                        Each will be True if that button was pressed.
            mouse_movement (boolean, default=False):    True if there was mouse movement since the last call.
            mouse_pos (:tuple: int, int, default=(0,0)):Current mouse position. In pixels.
        """
        if event.type == pygame.KEYDOWN:                 
            self.keyboard_handler(keys_pressed, event)
        if mouse_movement or event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:    
            self.mouse_handler(event, mouse_buttons_pressed, mouse_movement, mouse_pos)      

    def keyboard_handler(self, keys_pressed, event):
        """Handles any pygame keyboard related event. This allows for user interaction with the object.
        HANDLES ONLY INTERACTION WITH THE DIALOG AND THE SCROLLBAR.
        Posibilities:
        TODO
        Args:
            keys_pressed (:dict: pygame.keys):  Dict in which the keys are keys and the items booleans.
                                                Said booleans will be True if that specific key was pressed.
        """
        self.play_sound('key')
        if keys_pressed[pygame.K_DOWN]:
            if self.dialog:
                pass
            elif self.hit_sprite == self.scroll_sprite != None:
                self.send_to_active_sprite('right_arrow', -1)
        if keys_pressed[pygame.K_UP]:
            if self.dialog:
                pass
            elif self.hit_sprite == self.scroll_sprite != None:
                self.send_to_active_sprite('left_arrow', -1)
        if keys_pressed[pygame.K_KP_ENTER] or keys_pressed[pygame.K_SPACE]:
            if self.dialog:
                self.dialog.trigger_all_elements()
        if keys_pressed[pygame.K_LEFT]:
            if self.active_sprite_in_dialog() and self.hit_sprite.has_input:
                self.send_to_active_sprite('left_arrow', -1)
        if keys_pressed[pygame.K_RIGHT]:
            if self.active_sprite_in_dialog() and self.hit_sprite.has_input:
                self.send_to_active_sprite('right_arrow', -1)
        else:
            if self.dialog and self.dialog.elements.has(self.hit_sprite) and self.hit_sprite.has_input:
                self.send_to_active_sprite('add_input_character', pygame.key.name(event.key))

    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        """Handles any mouse related pygame event. This allows for user interaction with the object.
        TAKES CARE ONLY OF CONTACT WITH DIALOGS AND THE SCROLL BAR. 
        Sets in hit_sprite the collided sprite in every mouse movement (This includes also normal sprites)
        Posibilities:
        TODO
        Args:
            event (:obj: pygame.event): Event received from the pygame queue.
            mouse_buttons (:list: booleans):    List with 3 positions regarding the 3 normal buttons on a mouse.
                                                Each will be True if that button was pressed.
            mouse_movement( boolean, default=False):    True if there was mouse movement since the last call.
            mouse_position (:tuple: int, int, default=(0,0)):   Current mouse position. In pixels.
        """
        if mouse_movement:
            colliding_sprite = self.get_colliding_sprite()
            if self.dialog and self.dialog.elements.has(colliding_sprite):
                self.set_hit_sprite(colliding_sprite)
            elif colliding_sprite and colliding_sprite.enabled:
                self.set_hit_sprite(colliding_sprite)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.active_sprite_in_dialog():
                if self.hit_sprite.has_input:
                    adjusted_mouse_pos = tuple(x-y for x, y in zip(mouse_position, self.dialog.rect.topleft))
                    self.send_to_active_sprite('mouse_button', value=adjusted_mouse_pos)
                else:
                    self.send_to_active_sprite('do_action_or_add_value', -1)
            elif self.scroll_sprite != None:
                new_scroll_value = self.scroll_sprite.get_value()
                if event.button == 4:
                    new_scroll_value -= 0.05
                elif event.button == 5:
                    new_scroll_value += 0.05
                self.set_scroll(new_scroll_value)

    def active_sprite_in_dialog(self):
        """True if the dialog is active, and if the active sprite is from the dialog as well."""
        return (self.dialog and self.dialog.elements.has(self.hit_sprite))

    def send_to_active_sprite(self, *payload, **kw_payload):
        if self.hit_sprite:
            self.hit_sprite.hitbox_action(*payload, **kw_payload)

    def set_hit_sprite(self, sprite):
        """Called to set the hitten sprite. Can be overloaded"""
        if sprite != self.hit_sprite:
            if self.hit_sprite: 
                self.hit_sprite.set_hover(False) #Change the active back to the original state
                self.hit_sprite.set_active(False)
            self.hit_sprite = sprite             #Adding the new active sprite
            self.hit_sprite.set_hover(True)
            self.hit_sprite.set_active(True)

    def clear_active_sprite(self):
        if self.hit_sprite != None:   
            self.hit_sprite.set_hover(False)
            self.hit_sprite.set_active(False)
            self.hit_sprite = None

    def dialog_active(self):
        """Returns:
            (boolean):  True if the Screen Dialog is active, False otherwise"""
        return True if self.dialog else False

    def show_dialog(self, id_):
        """Makes the Screen's Dialog visible. (If it exists)."""
        for dialog in self.dialogs:
            try:
                if id_ in dialog.id or dialog.id in id_\
                or id_ in dialog.command or dialog.command in id_:
                    dialog.set_visible(True)
                    self.dialog = dialog
                    self.dialog.send_event()
                    return
            except AttributeError:  #It doesn't have a command. If its comparing commands, the id_ wasnt found in the id
                LOG.error_traceback()
        LOG.log('warning', 'The input with id ', id_, 'was not found.')

    def hide_dialog(self):
        """Makes the Screen's Dialog invisible. (If it exists)."""
        if self.dialog and self.dialog_active:  
            self.dialog.set_visible(False)
            self.dialog = None

    def draw(self, surface):
        """Draws the screen in the input surface. This method in the Screen
        superclass only draws the background, since the sprites group is empty.
        Args:
            surface (:obj: pygame.Surface): Surface to blit to."""
        if self.dialog:
            self.dialog.draw(surface)
        else:
            if self.animated_background:
                self.background.play(surface)
            else:
                self.background.draw(surface)
            for sprite in self.sprites:
                if self.scroll_offset != (0, 0):
                    sprite.draw(surface, offset=self.scroll_offset)
                else:
                    sprite.draw(surface)
            if self.scroll_sprite:
                self.scroll_sprite.draw(surface)       
            if self.animation:
                self.animation.play(surface)
                
    '''def draw(self, surface):
        """Draws the screen in the input surface. This method in the Screen
        superclass only draws the background, since the sprites group is empty.
        Args:
            surface (:obj: pygame.Surface): Surface to blit to."""
        if self.animated_background:
            self.background.play(surface)
        else:
            self.background.draw(surface)
        for sprite in self.sprites:
            if self.scroll_offset != (0, 0):
                sprite.draw(surface, offset=self.scroll_offset)
            else:
                sprite.draw(surface)
        if self.scroll_sprite:
            self.scroll_sprite.draw(surface)       
        if self.animation:
            self.animation.play(surface)
        if self.dialog:
            self.dialog.draw(surface)'''

    def set_resolution(self, resolution):
        """Changes the resolution of the screen to input argument.
        Reloads the graphical elements (Only the background in this case).
        Args:
            resolution (:tuple: int, int):  Resolution to set on the Screen."""
        if resolution != self.resolution:
            self.resolution = resolution
            if self.animated_background:
                self.background.set_resolution(resolution)
            else:
                self.background.set_canvas_size(resolution)
            if self.dialog:
                self.dialog.set_canvas_size(resolution)
            for sprite in self.sprites.sprites():
                sprite.set_canvas_size(resolution)
            if self.scroll_sprite:
                self.scroll_sprite.set_canvas_size(resolution)
                self.set_scroll(0)
            for animation in self.animations:
                animation.set_resolution(resolution)
                
    def set_scroll(self, value):
        if self.scroll_sprite:
            self.scroll_sprite.set_value(value)
            if value <= 0:
                self.scroll_offset = (0, 0)
            elif value >= 1:
                self.scroll_offset = (0, -self.scroll_length)
            else:
                pixels = int(-value*self.scroll_length)
                self.scroll_offset=(0, pixels)
            screen_rect = pygame.Rect((0, 0), self.resolution)
            for sprite in self.sprites:
                sprite_rect = sprite.rect.copy()
                sprite_rect.topleft = tuple(off+pos for off, pos in zip(self.scroll_offset, sprite_rect.topleft))
                if screen_rect.colliderect(sprite_rect):
                    sprite.set_visible(True)
                else:
                    sprite.set_visible(False)

    def add_sprites(self, *sprites):
        """Adds sprites to the screen. Those added sprites will be drawn automatically in the next execution.
        Args:
            *sprites (:obj: Sprites):   Sprites to add.
        Raises:
            BadSpriteException: If any of the input sprites it not of type Sprite or related."""
        if not all(isinstance(sprite, Sprite) for sprite in sprites):   #error control
            bad_sprite = next(not isinstance(sprite, Sprite) for sprite in sprites)
            raise BadSpriteException('An object of type '+str(type(bad_sprite))+' can`t be added to a screen.')
        sprites = sorted(list(sprites), key=lambda sprite: (sprite.rect.y, sprite.rect.x))  #Ordering them following position
        for sprite in sprites:
            self.sprites.add(sprite)

    def enable_sprite(self, *keywords, state=True):
        sprite = None
        count = 0
        sprites = self.sprites.sprites()
        for i in range(0, len(sprites)):
            matches = len([True for j in keywords if j in sprites[i].id])
            if matches > count:   
                sprite = sprites[i]
                count = matches
        if count is not 0:
            sprite.set_enabled(state)
            return True
        return False

    def enable_all_sprites(self, state=True):
        for sprite in self.sprites:
            sprite.set_enabled(state)

    def enable_sprites(self, state=True, *keywords):
        for sprite in self.sprites:
            if all(kw in sprite.get_id() for kw in keywords):
                sprite.set_enabled(state)

    def get_colliding_sprite(self):
        """Collides with dialog, scroll, and sprites taking the scroll into account."""
        mouse_sprite = UtilityBox.get_mouse_sprite()
        
        #Check if colliding with dialog
        if self.dialog:
            return self.dialog.get_collisions(mouse_sprite, first_only=True)

        #Check if colliding with scroll
        if self.scroll_sprite and mouse_sprite.rect.colliderect(self.scroll_sprite.rect):
            return self.scroll_sprite
        if self.scroll_offset:
            for sprite in self.sprites:
                if sprite.visible and sprite.enabled:
                    sprite_rect = sprite.rect.copy()
                    sprite_rect.topleft = tuple(off+pos for off, pos in zip(self.scroll_offset, sprite_rect.topleft))
                    if sprite_rect.colliderect(mouse_sprite.rect):
                        return sprite
        else:
            return pygame.sprite.spritecollideany(mouse_sprite, self.sprites.sprites())
        
    def destroy(self):
        """Called when exiting the game, in case we have some subthreads we need dead.
        To overload."""
        pass

class LoadingScreen(Screen):
    """LoadingScreen class. Inherits from Screen.
    Its purpose it's pretty obvious, being a middle screen until whatever
    you want ends loading. Don't have music nor sound.
    General class attributes:
        __default_config (:dict:):  Contains parameters about the text looks and positioning.
            loading_sprite_path (str):  Path to the loading sprite image. Default in /img.
            text (str): Text that will be shown on the screen. Default is 'Loading...'
            text_proportion (str):  Tuple containing the text proportion vs the resolution.
                                    Default is (0.6, 0.1)
    """
    __default_config = {'background_path': PATHS.LOADING_BG,
                        'loading_sprite_path': PATHS.LOADING_STATIC_CIRCLE, 
                        'text': 'Loading...',
                        'text_proportion': (0.6, 0.1)}

    def __init__(self, id_, event_id, resolution, **params):
        """LoadingScreen constructor.
        Args:
            id_ (str):  Identifier of the Screen.
            event_id (int): Identifier of the event of the screen.
            resolution (:tuple: int, int):  Resolution of the current display.
            **params (:dict:):  Dict of keywords and values as parameters to create the Screen.
                                background_path, music_path, sound_path, loading_sprite_path,
                                text, text_proportion.
        """
        if 'background_path' not in params:   
            params['background_path'] = LoadingScreen.__default_config['background_path']
        super().__init__(id_, event_id, resolution, **params)
        self.msg_queue = None   #To add messages on screen about what it's happening
        LoadingScreen.generate(self)

    @staticmethod
    def generate(self):
        """Loads the loading sprite image, and renders the TextSprite.
        Then adds them to Screen."""
        UtilityBox.join_dicts(self.params, LoadingScreen.__default_config)
        #The text sprite in the middle of the screen
        text_size   = tuple(x*ratio for x,ratio in zip(self.resolution, self.params['text_proportion']))
        text_sprite = TextSprite(self.id+'_text', (0, 0), text_size, self.resolution, self.params['text'])
        text_sprite.set_position(tuple(x//2-y//2 for x, y in zip(self.resolution, text_sprite.rect.size)))
        self.sprites.add(text_sprite)
        self.add_animation(AnimationGenerator.explosions_bottom(INIT_PARAMS.INITIAL_RESOLUTION, *INIT_PARAMS.ALL_FPS))

    def generate_static_rotating_load_sprite(self):
        load_surfaces = self.generate_load_sprite(self.params['loading_sprite_path'])
        loading_sprite = AnimatedSprite(self.id+'_loading_sprite', load_surfaces[0].rect.topleft,\
                                        load_surfaces[0].rect.size, self.resolution, initial_surfaces=load_surfaces,\
                                        animation_delay=60)
        self.sprites.add(loading_sprite)

    def generate_load_sprite(self, path, degrees=45):
        """Gets an image from a path, and rotates it until it completes en entier circle (360º).
        Then gets all those rotated surfaces and returns them. In short, creates an animation
        from a static image.
        Args:
            path (str): Path of the image to load.
            degrees (int, default=45):  Degrees rotated in each iteration.
                                        For 45º, it would rotate the surface 8 times."""
        sprite              = pygame.sprite.Sprite()
        sprite.image        = pygame.image.load(path)
        sprite.rect         = sprite.image.get_rect()
        sprite.rect.topleft = (self.resolution[0]//2-sprite.rect.width//2, self.resolution[1]-sprite.rect.height*1.5)
        return UtilityBox.rotate(sprite, degrees, 360//degrees, include_original=True, name='loading_sprite')