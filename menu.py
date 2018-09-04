import pygame, math, numpy, os
from pygame.locals import *
import gradients #Gradients in polygons
import ptext #Gradients in text
from polygons import Circle, Rectangle
from pygame_test import PygameSuite

class Menu (object):
    game_folder = os.path.dirname(__file__)
    img_folder = os.path.join(game_folder, 'img')
    sounds_folder = os.path.join(game_folder, 'sounds')

    __default_config = {'background_path': None,
                        'logo_path': None,
                        'logo_size': 0.20,
                        'title_menu': '',
                        'title_text_size': 0.15,
                        'soundtheme_path': sounds_folder+'maintheme.mp3',
                        'soundeffect_path': sounds_folder+'/option.ogg',
                        'font': None,
                        'max_font':200
    }

    def __init__(self, id, resolution, **params):
        #Basic info saved
        self.id = id
        self.config = Menu.__default_config.copy().update(**params)
        
        #Graphic elements
        self.static_sprites = pygame.sprite.Group() #Things without interaction
        self.dynamic_sprites = pygame.sprite.OrderedUpdates() #Things with interaction, like buttons and such
        self.active_sprite = pygame.sprite.GroupSingle(_use_update=True) #Selected from dynamic_elements, only one at the same time
        self.active_sprite_index = 0
        self.background = self.load_background(resolution, self.config['background_path'])

        #Music & sounds
        self.main_theme = pygame.mixer.music.load(self.config['soundtheme_path'])
        self.option_sound = pygame.mixer.Sound(file=self.config['soundeffect_path'])
        #self.option_sound.set_volume(1)

        self.generate(resolution)

        pygame.mixer.music.play()

    def add_elements(self, *elements):
        for element in elements:
            if type(element) is list:
                for subelement in element:
                    self.__add_element(subelement)
            elif type(element) is dict:
                for subelement in element.values():
                    self.__add_element(subelement)
            else:
                self.__add_element(element)

    def __add_element(self, element):
        '''Decides whether to add the element to the static or the dynamic elements
        based on the type of the element. Afterwards addes it to the chosen one.
        
        Args: 
            element: element to add'''
        if type(element) is tuple:      #UiElement or issubclass(type(element), UiElement), its a (uielement, default_Values) tuple
            try:
                self.dynamic_sprites.add(element[0])
            except TypeError:
                print("An element couldn't be added, due to being a tuple, but not an ui_element subclass.")
        else:
            if type(element) is pygame.Surface:
                self.static_sprites.add(element)
            else:
                raise TypeError("Elements should be a pygame.Surface, or an ui_element subclass.") 

    def __adjust_elements(self, resolution):
        total_pixels = [0, 0]
        #We want only shallow copies, that way we will modify the sprites directly
        total_sprites = self.static_sprites.sprites().copy().extend(self.dynamic_sprites.sprites()) 
        
        #Counting, adding the pixels and comparing to the resolution
        for sprite in total_sprites:
            for x, y in zip(total_pixels, sprite.rect.size):  x += y

        #Getting the ratios between total elements and native resolution
        ratios = [x/y for x, y in zip(resolution, total_pixels)]

        if any(ratio < 1 for ratio in ratios):                                                          #If any axis needs resizing
            for sprite in total_sprites:
                sprite.regenerate([x*y for x,y in zip(ratios, sprite.rect.size) if x<1])                #Adjusting size
                sprite.rect.topleft = tuple([x*y for x,y in zip(ratios, sprite.rect.topleft) if x<1])   #Adjusting positions

    def generate(self, resolution):
        self.__adjust_elements(resolution)

    def load_background(self, size, background_path=None):
        if background_path is None:
            bg_surf = gradients.vertical(size, (255, 200, 200, 255), (255, 0, 0, 255)) #Gradient from white-ish to red
        else:
            bg_surf = pygame.transform.scale(pygame.image.load(background_path), size)
        return bg_surf

    def draw(self, surface, show_fps=True):
        surface.blit(self.background, (0,0))
        self.static_sprites.draw(surface)
        self.dynamic_sprites.draw(surface)

    def event_handler(self, event, keys_pressed, mouse_buttons_pressed, mouse_movement=False, mouse_pos=(0, 0)):
        if event.type == pygame.KEYDOWN:        #Handling regarding keyboard
            if keys_pressed[pygame.K_DOWN]:         self.change_active_sprite(self.active_sprite_index+1)
            if keys_pressed[pygame.K_UP]:           self.change_active_sprite(self.active_sprite_index-1)

            if keys_pressed[pygame.K_LEFT]:         self.active_sprite.sprite.hitbox_action('left_arrow', value=mouse_pos)
            if keys_pressed[pygame.K_RIGHT]:        self.active_sprite.sprite.hitbox_action('right_arrow', value=mouse_pos)

            if keys_pressed[pygame.K_KP_ENTER]\
                or keys_pressed[pygame.K_SPACE]:    self.active_sprite.sprite.hitbox_action('add_value', value=mouse_pos)

        self.mouse_handler(mouse_buttons_pressed, mouse_movement, mouse_pos)                    #Handling regarding mouse #TODO complete call

    def mouse_handler(self, mouse_buttons, mouse_movement, mouse_position):
        #elif event.type == pygame.MOUSEBUTTONDOWN:             #If a mouse button was clicked
        if mouse_buttons_clicked[0]:    self.active_sprite.sprite.hitbox_action('left_mouse_button', value=mouse_pos)
        elif mouse_buttons_clicked[2]:  self.active_sprite.sprite.hitbox_action('right_mouse_button', value=mouse_pos)
        
        if mouse_movement: 
            mouse_hitbox = pygame.sprite.Sprite()
            mouse_hitbox.rect = pygame.Rect(mouse_position, (2,2))
            colliding_sprite = pygame.sprite.spritecollideany(mouse_hitbox, self.dynamic_sprites.sprites())
            self.change_active_sprite(self.get_sprite_index(colliding_sprite))

    def change_active_sprite(self, index):
        size_sprite_list =                  len(self.dynamic_sprites.sprites())

        self.active_sprite_index =          index
        if index >= size_sprite_list:       self.active_sprite_index = 0
        elif index < 0:                     self.active_sprite_index = size_sprite_list-1
        
        self.active_sprite.sprite.generate_object()                                   #Change the active back to the original state
        self.active_sprite.add(self.dynamic_sprites.sprites()[self.active_sprite_index])    #Adding the new active sprite

    def get_sprite_index(self, sprite):
        sprite_list = self.dynamic_sprites.sprites()
        return i for i in range(0, len(sprite_list)) if sprite is sprite_list[i]

#List of (ids, text)
if __name__ == "__main__":
    timeout = 20
    testsuite = PygameSuite(fps=144)

    menu = Menu("main_menu", [("start_game", "Start game"), ("resolution", "Resolution"), ("flaity", "Flaity"), ("tio", "Tio"),\
    ("joder", "Joder"), ("loco", "Loco")], {"resolution" : resolutions}, background_path='background.jpg', logo_path="logo.jpg")
    testsuite.loop()