import pygame
from paths import *
from utility_box import UtilityBox
from ui_element import TextSprite
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

    def update_resolution(self, resolution):
        self.resolution = resolution
        self.background = UtilityBox.load_background(resolution, self.params['background_path'])

    def generate(self):
        pass
    
class LoadingScreen(Screen):
    def __init__(self, id_, event_id, resolution, text, loading_sprite = None, **params):
        super().__init__(id_, event_id, resolution, **params)
        self.full_sprite    = self.generate_load_sprite(loading_sprite)
        self.loading_sprite = self.copy_sprite(0, *self.full_sprite)
        self.real_rect_sprt = (tuple(x//y for x, y in zip(self.loading_sprite[0].rect.size, self.resolution)),\
                            tuple(x//y for x, y in zip(self.loading_sprite[0].rect.topleft, self.resolution)))
        self.index_sprite   = 0

        self.text_sprite    = TextSprite(self.id, text, (int(0.6*self.resolution[0]), int(0.1*self.resolution[1])))
        self.text_sprite.set_position(self.resolution, 0)
        self.count          = 0
    
    def generate_load_sprite(self, path, degrees=45):
        sprite = pygame.sprite.Sprite()
        sprite.image        = pygame.image.load(IMG_FOLDER+"//loading_circle.png") if path is None else pygame.image.load(path)
        sprite.rect         = sprite.image.get_rect()
        sprite.rect.topleft = (self.resolution[0]//2-sprite.rect.width//2, self.resolution[1]-sprite.rect.height*1.5)
        return UtilityBox.rotate(sprite, 360//8, 8, include_original=True)
    
    def update(self):
        if self.count is 100:
            self.index_sprite = 0 if self.index_sprite is (len(self.loading_sprite)-1) else self.index_sprite+1
            self.count = 0
        else: self.count+=1

    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.loading_sprite[self.index_sprite].image, self.loading_sprite[self.index_sprite].rect)
        surface.blit(self.text_sprite.image, self.text_sprite.rect)
        self.update()

    def copy_sprite(self, new_size, *sprite_list):
        sprites_copy = []
        for sprite in sprite_list:
            spr = pygame.sprite.Sprite()
            spr.image, spr.rect = sprite.image.copy(), sprite.rect.copy()
            sprites_copy.append(spr)
        return sprites_copy

    def update_resolution(self, resolution):
        super().update_resolution(resolution)
        #for sprite in self.loading_sprite:
            #sprite.image = pygame.transform.smoot
