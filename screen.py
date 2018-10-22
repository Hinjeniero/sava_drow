from paths import *
from utility_box import UtilityBox

class Screen(object):
    __default_config = {'background_path': None,
                        'soundtheme_path': SOUND_FOLDER+'\\gametheme.mp3',
                        'soundeffect_path': SOUND_FOLDER+'\\click.ogg',
                        'font': None,
                        'max_font': 200, 
                        'confirmation_element': None,
                        'confirmation_needed' : False
    }
    def __init__(self, id_, event_id, resolution, **params):
        self.id         = id_
        self.event_id   = event_id
        self.params     = Screen.__default_config.copy()
        self.params.update(params)
        self.background = UtilityBox.load_background(resolution, self.params['background_path'])
        self.resolution = resolution

    def show_confirmation(self):
        if self.params['confirmation_needed'] and self.params['confirmation_element']:
            self.params['confirmation_element'].set_visible(True)

    def draw(self, surface, hitboxes=False, fps=True, clock=None):
        surface.blit(self.background, (0,0))

    def update_resolution(self, resolution):
        self.resolution = resolution
        self.background = UtilityBox.load_background(resolution, self.params['background_path'])