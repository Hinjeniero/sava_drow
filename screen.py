import pygame
from paths import *
from utility_box import UtilityBox
from ui_element import TextSprite
from sprite import AnimatedSprite

class Screen(object):
    __default_config = {'background_path'   : None,
                        'music_path'        : '\\music.mp3',
                        'sound_path'        : '\\option.ogg',
                        'font'              : None,
                        'max_font'          : 200, 
                        'dialog_active'     : False,
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

    def set_resolution(self, resolution):
        self.resolution = resolution
        self.background = UtilityBox.load_background(resolution, self.params['background_path'])

    def generate(self):
        pass
    
class LoadingScreen(Screen):
    def __init__(self, id_, event_id, resolution, text, loading_sprite_path=IMG_FOLDER+"//loading_circle.png", **params):
        super().__init__(id_, event_id, resolution, **params)
        self.loading_sprite, self.text_sprite = self.generate_sprites(text, loading_sprite_path=loading_sprite_path)
    
    def generate_sprites(self, text, loading_sprite_path=None):
        loading_sprite  = None
        load_sprites    = self.generate_load_sprite(loading_sprite_path)
        if loading_sprite_path:
            loading_sprite  = AnimatedSprite(self.id+'_loading_sprite', load_sprites[0].rect.topleft,\
                            load_sprites[0].rect.size, self.resolution, *(load_sprites), animation_delay=60)

        text_size   = (int(0.6*self.resolution[0]), int(0.1*self.resolution[1]))
        text_pos    = tuple([x//2-y//2 for x, y in zip(self.resolution, text_size)])
        text_sprite = TextSprite(self.id+'_text', text_pos, text_size, self.resolution, text)
        return loading_sprite, text_sprite

    def generate_load_sprite(self, path, degrees=45):
        sprite              = pygame.sprite.Sprite()
        sprite.image        = pygame.image.load(path)
        sprite.rect         = sprite.image.get_rect()
        sprite.rect.topleft = (self.resolution[0]//2-sprite.rect.width//2, self.resolution[1]-sprite.rect.height*1.5)
        return UtilityBox.rotate(sprite, 360//8, 8, include_original=True)

    def draw(self, surface):
        super().draw(surface)
        self.loading_sprite.draw(surface)
        self.text_sprite.draw(surface)

    def copy_sprite(self, new_size, *sprites):
        sprites_copy = []
        for sprite in sprites:
            spr = pygame.sprite.Sprite()
            spr.image, spr.rect = sprite.image.copy(), sprite.rect.copy()
            sprites_copy.append(spr)
        return sprites_copy

    def set_resolution(self, resolution):
        super().set_resolution(resolution)
        self.loading_sprite.set_canvas_size(resolution)
        self.text_sprite.set_canvas_size(resolution)
