import pygame
from paths import *
from utility_box import UtilityBox

class Screen(object):
    __default_config = {'background_path'   : None,
                        'music_path'        : '\\music.mp3',
                        'sound_path'        : '\\option.ogg',
                        'font'              : None,
                        'max_font'          : 200, 
                        'dialog_active'     : False
    }
    def __init__(self, id_, event_id, resolution, **params):
        self.id         = id_
        self.event_id   = event_id
        self.params     = Screen.__default_config.copy()
        self.params.update(params)
        self.background = UtilityBox.load_background(resolution, self.params['background_path'])
        self.dialog     = pygame.sprite.GroupSingle()
        self.resolution = resolution
        try:                self.dialog.add(self.params['dialog'])
        except KeyError:    pass
        #sound
        self.music = pygame.mixer.music.load(SOUND_FOLDER+self.params['music_path'])
        self.sound = pygame.mixer.Sound(file=SOUND_FOLDER+self.params['sound_path'])
        if self.sound is not None:  self.sound.set_volume(0.5)
        if self.music is not None:  self.music.set_volume(0.5)
        pygame.mixer.music.play() #TODO check how to change this to change everyt ime the screen changes

    def have_dialog(self):
        return False if self.dialog.sprite is None else True

    def dialog_is_active(self):
        return self.params['dialog_active']

    def show_dialog(self):
        if self.have_dialog():  self.params['dialog_active'] = True

    def hide_dialog(self):
        if self.have_dialog():  self.params['dialog_active'] = False

    def draw(self, surface):
        surface.blit(self.background, (0,0))

    def update_resolution(self, resolution):
        self.resolution = resolution
        self.background = UtilityBox.load_background(resolution, self.params['background_path'])

    def generate(self):
        pass
    