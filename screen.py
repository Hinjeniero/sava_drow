"""--------------------------------------------
screen module. Contains classes that work as entire screens to be shown on display.
Have the following classes, inheriting represented by tabs:
    Screen
        ↑LoadingScreen
--------------------------------------------"""

__all__ = ["Screen", "LoadingScreen"]
__version__ = '0.2'
__author__ = 'David Flaity Pardo'

import pygame
from paths import IMG_FOLDER, SOUND_FOLDER
from utility_box import UtilityBox
from ui_element import TextSprite
from sprite import AnimatedSprite

class Screen(object):
    """Screen class. Controls an entire 'screen' (like a desktop).
    Purpose is to have an "interface" with a bit of a standard schema and functionality.
    Screen itself should be overloaded, otherwise it's kinda a bland class.
    General class attributes:
        __default_config (:dict:): Contains parameters about the text looks and positioning.
            background_path (str):  Path to the background image.
            music_path (str):   Path to the music file.
            sound_path (str):   Path to the sound effect file.
            dialog_active (boolean):    True if the Screen posseses a dialog of any type (confirm changes, exit...)
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
                        'music_path'        : '\\music.mp3',
                        'sound_path'        : '\\option.ogg',
                        'dialog_active'     : False
    }

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
        self.params     = Screen.__default_config.copy()
        self.params.update(params)
        self.background = UtilityBox.load_background(resolution, self.params['background_path'])
        self.dialog     = pygame.sprite.GroupSingle()
        self.resolution = resolution
        if dialog:  self.dialog.add(dialog)
        #Sprites
        self.sprites = pygame.sprite.OrderedUpdates()
        #Sound & Music
        self.music = pygame.mixer.music.load(SOUND_FOLDER+self.params['music_path'])
        self.sound = pygame.mixer.Sound(file=SOUND_FOLDER+self.params['sound_path'])
        if self.sound is not None:  self.sound.set_volume(0.5)
        if self.music is not None:  self.music.set_volume(0.5)
        pygame.mixer.music.play() #TODO check how to change this to change everyt ime the screen changes
        self.generate()

    def have_dialog(self):
        """Returns:
            (boolean):  True if the screen has a Dialog, False otherwise."""
        return False if self.dialog.sprite is None else True

    def dialog_is_active(self):
        """Returns:
            (boolean):  True if the Screen Dialog is active, False otherwise"""
        return self.params['dialog_active']

    def show_dialog(self):
        """Makes the Screen's Dialog visible. (If it exists)."""
        if self.have_dialog():  self.params['dialog_active'] = True

    def hide_dialog(self):
        """Makes the Screen's Dialog invisible. (If it exists)."""
        if self.have_dialog():  self.params['dialog_active'] = False

    def draw(self, surface):
        """Draws the screen in the input surface. This method in the Screen
        superclass only draws the background, since the sprites group is empty.
        Args:
            surface (:obj: pygame.Surface): Surface to blit to."""
        surface.blit(self.background, (0,0))
        for sprite in self.sprites.sprites():
            sprite.draw(surface)

    def set_resolution(self, resolution):
        """Changes the resolution of the screen to input argument.
        Reloads the graphical elements (Only the background in this case).
        Args:
            resolution (:tuple: int, int):  Resolution to set on the Screen."""
        if resolution != self.resolution:
            self.resolution = resolution
            self.background = UtilityBox.load_background(resolution, self.params['background_path'])
            for sprite in self.sprites.sprites():
                sprite.set_canvas_size(resolution)

    def generate(self):
        """Empty method that will be called upon at the end of each constructor.
        The idea behind this method is to initiate every element needed for a correct
        Screen usage. Needs to be overloaded on the subclasses that inherit from Screen."""
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
    __default_config = {'background_path': IMG_FOLDER+'loading_background.png',
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
        UtilityBox.join_dicts(params, LoadingScreen.__default_config)
        super().__init__(id_, event_id, resolution, **params)
    
    def generate(self):
        """Loads the loading sprite image, and renders the TextSprite.
        Then adds them to Screen."""
        #The animated loading sprite
        load_surfaces = self.generate_load_sprite(self.params['loading_sprite_path'])
        loading_sprite          = AnimatedSprite(self.id+'_loading_sprite', load_surfaces[0].rect.topleft,\
                                                load_surfaces[0].rect.size, self.resolution, *(load_surfaces),\
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
