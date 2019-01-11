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
from paths import IMG_FOLDER, SOUND_FOLDER
from utility_box import UtilityBox
from ui_element import TextSprite
from sprite import Sprite, AnimatedSprite
from exceptions import BadSpriteException, BadStateException
from logger import Logger as LOG
from decorators import run_async

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
                        'songs_paths'       : []
    }
    STATES = ['idle', 'stopped', 'cutscene']
    SOUND_CHANNELS_AMMOUNT = 32  #Sound channels are shared between Screens
    SOUND_CHANNELS = []
    SOUNDS_FOLDER = SOUND_FOLDER+"\\common\\"
    def __init__(self, id_, event_id, resolution, dialog=None, **params):
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
        self.dialog     = pygame.sprite.GroupSingle()
        self.resolution = resolution
        #Sprites
        self.background = None  #Created in generate
        self.dialog     = dialog
        self.sprites    = pygame.sprite.OrderedUpdates()
        self.popups     = pygame.sprite.OrderedUpdates()
        #Sound & Music
        self.songs      = []    #Created in generate
        self.music_chan = None  #Created in generate
        self.song_index = 0
        self.sound_vol  = 0     #Created in generate
        self.sounds     = {}    #Created in generate
        self.playing    = False #Playing music?
        #State machine
        self.state      = Screen.STATES[0]
        Screen.generate(self)

    @staticmethod
    def generate(self):
        UtilityBox.join_dicts(self.params, Screen.__default_config.copy())
        self.background = Sprite(self.id+'_background', (0, 0), self.resolution, self.resolution,\
                                resize_mode='fill', texture=self.params['background_path'])
        if self.params['songs_paths']:
            self.music_chan = UtilityBox.get_sound_channel()
            self.music_chan.set_volume(0.75)
            for song_path in self.params['songs_paths']:
                self.songs.append(song_path)
        self.sound_vol = 0.75
        for sound in UtilityBox.get_all_files(Screen.SOUNDS_FOLDER, '.ogg', '.wav'):
            self.sounds[sound] = pygame.mixer.Sound(file=sound)
        if len(Screen.SOUND_CHANNELS) is 0:
            for _ in range (0, Screen.SOUND_CHANNELS_AMMOUNT):
                Screen.SOUND_CHANNELS.append(UtilityBox.get_sound_channel())

    def set_state(self, state):
        state = state.lower()
        if state not in Screen.STATES:
            raise BadStateException('The state '+state+' doesn`t exist in '+self.id)
        self.state = state

    def has_music(self):
        return True if self.music_chan else False

    def add_popups(self, *popups):
        for popup in popups:
            popup.set_active(False)
            popup.set_visible(False)
            self.popups.add(popup)

    def show_popup(self, id_):
        for popup in self.popups.sprites():
            if id_ in popup.id:
                popup.set_visible(True)
                popup.set_active(True)
                return
        LOG.log('debug', 'POPup ', id_,'not found')

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
        for key in self.sounds.keys():
            if 'secret' not in key:
                self.sounds[key] = sound

    def set_song(self, song_path):
        index = 0
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
        for sound in self.sounds.keys():
            if sound_id in sound or sound in sound_id:
                channel = None
                for channel in Screen.SOUND_CHANNELS:
                    if not channel.get_busy():
                        channel.set_volume(self.sound_vol)
                        channel.play(self.sounds[sound])
                        return True
        return False

    def have_dialog(self):
        """Returns:
            (boolean):  True if the screen has a Dialog, False otherwise."""
        return False if not self.dialog else True

    def dialog_active(self):
        """Returns:
            (boolean):  True if the Screen Dialog is active, False otherwise"""
        return (self.dialog.active and self.dialog.visible)

    def show_dialog(self):
        """Makes the Screen's Dialog visible. (If it exists)."""
        if self.have_dialog():  
            self.dialog.set_visible(True)
            self.dialog.set_active(True)

    def hide_dialog(self):
        """Makes the Screen's Dialog invisible. (If it exists)."""
        if self.have_dialog():  
            self.dialog.set_visible(False)
            self.dialog.set_active(False)

    def draw(self, surface):
        """Draws the screen in the input surface. This method in the Screen
        superclass only draws the background, since the sprites group is empty.
        Args:
            surface (:obj: pygame.Surface): Surface to blit to."""
        self.background.draw(surface)
        for sprite in self.sprites.sprites():
            sprite.draw(surface)
        for popup in self.popups.sprites():
            popup.draw(surface)
        if self.have_dialog() and self.dialog_active():
            self.dialog.draw(surface)

    def set_resolution(self, resolution):
        """Changes the resolution of the screen to input argument.
        Reloads the graphical elements (Only the background in this case).
        Args:
            resolution (:tuple: int, int):  Resolution to set on the Screen."""
        if resolution != self.resolution:
            self.resolution = resolution
            self.background.set_canvas_size(resolution)
            if self.dialog:
                self.dialog.sprite.set_canvas_size(resolution)
            for sprite in self.sprites.sprites():
                sprite.set_canvas_size(resolution)

    def add_sprites(self, *sprites):
        """Adds sprites to the screen. Those added sprites will be drawn automatically in the next execution.
        Args:
            *sprites (:obj: Sprites):   Sprites to add.
        Raises:
            BadSpriteException: If any of the input sprites it not of type Sprite or related."""
        for sprite in sprites:
            if not isinstance(sprite, Sprite):
                raise BadSpriteException('An object of type '+str(type(sprite))+' can"t be added to a screen.')
            self.sprites.add(sprite)

    def disable_sprite(self, *keywords):
        sprite = None
        count = 0
        sprites = self.sprites.sprites()
        for i in range(0, len(sprites)):
            matches = len([True for j in keywords if j in sprites[i].id])
            if matches > count:   
                sprite = sprites[i]
                count = matches
        if count is not 0:
            sprite.set_enabled(False)
            return True
        return False

    def disable_all_sprites(self):
        for sprite in self.sprites.sprites():
            sprite.set_enabled(False)

    def hide_popups(self):
        for popup in self.popups.sprites():
            popup.set_active(False)
            popup.set_visible(False)

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
    __default_config = {'background_path': IMG_FOLDER+'//loading_background.png',
                        'loading_sprite_path': IMG_FOLDER+'//loading_circle.png', 
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
        LoadingScreen.generate(self)

    @staticmethod
    def generate(self):
        """Loads the loading sprite image, and renders the TextSprite.
        Then adds them to Screen."""
        UtilityBox.join_dicts(self.params, LoadingScreen.__default_config)
        load_surfaces = self.generate_load_sprite(self.params['loading_sprite_path'])
        print("FSASF")
        print(load_surfaces[0].rect.size)
        loading_sprite = AnimatedSprite(self.id+'_loading_sprite', load_surfaces[0].rect.topleft,\
                                        load_surfaces[0].rect.size, self.resolution, *load_surfaces,\
                                        animation_delay=60)
        #The text sprite in the middle of the screen
        text_size   = tuple(x*ratio for x,ratio in zip(self.resolution, self.params['text_proportion']))
        text_pos    = tuple(x//2-y//2 for x, y in zip(self.resolution, text_size))
        text_sprite = TextSprite(self.id+'_text', text_pos, text_size, self.resolution, self.params['text'])
        self.sprites.add(loading_sprite, text_sprite)

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
        return UtilityBox.rotate(sprite, degrees, 360//degrees, include_original=True)
