import pygame, math, numpy, os
from utility_box import UtilityBox
from pygame.locals import *
from ui_element import *
import gradients #Gradients in polygons
import ptext #Gradients in text
from polygons import Circle, Rectangle
from pygame_test import PygameSuite
from colors import *
from screen import Screen

class Menu (Screen):
    __default_config = {'logo_path': None,
                        'logo_size': 0.20,
                        'title_menu': '',
                        'title_text_size': 0.15,
                        'do_align': True,
                        'alignment': 'center'
    }

    def __init__(self, id_, event_id, resolution, *elements, **params):
        super().__init__(id_, event_id, resolution, **params)
        UtilityBox.join_dicts(self.params, Menu.__default_config)
        #Graphic elements
        self.static_sprites         = pygame.sprite.Group()             #Things without interaction
        self.dynamic_sprites        = pygame.sprite.OrderedUpdates()    #Things with interaction, like buttons and such
        self.active_sprite          = pygame.sprite.GroupSingle()       #Selected from dynamic_elements, only one at the same time
        self.active_sprite_index    = 0

        if len(elements) > 0: 
            self.add_elements(*elements)
            self.generate(self.resolution, centering=self.params['do_align'], alignment=self.params['alignment'])
        else:   raise IndexError("A menu needs at least one element prior to the generation.")

    def generate(self, resolution, centering=True, alignment='center'):
        self.__adjust_elements(resolution)
        if centering:   self.__center_elements()
        self.active_sprite.add(self.dynamic_sprites.sprites()[0])

    def set_resolution(self, resolution):
        super().set_resolution(resolution)
        #Regenerate elements
        for sprite in self.static_sprites.sprites():    sprite.set_canvas_size(resolution)
        for sprite in self.dynamic_sprites.sprites():   sprite.set_canvas_size(resolution)
        #if self.have_dialog():      self.dialog.sprite.generate(rect=sprite.get_rect_if_canvas_size(resolution))
        self.generate(self.resolution, centering=self.alignment[0], centering_mode=self.alignment[1])


    def add_elements(self, *elements, overwrite_eventid = False):
        for element in elements:
            if type(element) is list:
                for subelement in element:
                    self.__add_element(subelement, overwrite_eventid=overwrite_eventid)
            elif type(element) is dict:
                for subelement in element.values():
                    self.__add_element(subelement, overwrite_eventid=overwrite_eventid)
            else:
                self.__add_element(element, overwrite_eventid=overwrite_eventid)

    def __add_element(self, element, overwrite_eventid = False):
        '''Decides whether to add the element to the static or the dynamic elements
        based on the type of the element. Afterwards addes it to the chosen one.
        
        Args: 
            element: element to add'''
        if overwrite_eventid is True:               element.set_event(self.event_id)
        #After that
        if issubclass(type(element), UIElement):    self.dynamic_sprites.add(element)
        elif type(element) is pygame.Surface:       self.static_sprites.add(element)
        else:                                       raise TypeError("Elements should be a pygame.Surface, or an ui_element subclass.") 

    def __adjust_elements(self, resolution):
        total_spaces =  [0, 0]
        last_y =        [0, 0]

        #We want only shallow copies, that way we will modify the sprites directly
        total_sprites = self.static_sprites.sprites().copy()
        total_sprites.extend(self.dynamic_sprites.sprites()) 

        #Counting, adding the pixels and comparing to the resolution
        for sprite in total_sprites:
            space =         [x-y for x,y in zip(sprite.rect.topleft, last_y)]           #Total spaces between topleft position elements == all sizes+all interelement spaces
            total_spaces =  [x+y for x,y in zip(total_spaces, space)]
            last_y =        list(sprite.rect.topleft)     
        total_spaces = [sum(x) for x in zip(total_spaces, total_sprites[-1].rect.size)] #Adds the last element size to the spaces. 

        #Getting the ratios between total elements and native resolution
        ratios = [x/y for x, y in zip(resolution, total_spaces)]
        if any(ratio < 1 for ratio in ratios):                                      #If any axis needs resizing
            for sprite in total_sprites:
                position = tuple([int(x*y) if x<1 else y for x,y in zip(ratios, sprite.rect.topleft)])
                size =     tuple([int(x*y) if x<1 else y for x,y in zip(ratios, sprite.rect.size)])
                sprite.generate(rect=pygame.Rect(position, size))                #Adjusting size

    def __center_elements(self, alignment='center'):
        self.__center_sprites(self.static_sprites, alignment=alignment)
        self.__center_sprites(self.dynamic_sprites, alignment=alignment)
    
    def __center_sprites(self, sprites, alignment='center'):
        list_of_sprites = sprites.sprites() if isinstance(sprites, pygame.sprite.Group) else sprites
        screen_width = self.resolution[0]
        for sprite in list_of_sprites:
            sprite.rect.x = (screen_width-sprite.rect.width)//2 if 'center' in alignment\
            else (0.05*screen_width) if 'left' in alignment\
            else (screen_width-sprite.rect.width-0.05*screen_width)

    def draw(self, surface, hitboxes=False):
        super().draw(surface)
        for sprite in self.static_sprites.sprites(): sprite.draw(surface)
        for sprite in self.dynamic_sprites.sprites(): sprite.draw(surface)
        if self.have_dialog() and self.dialog_is_active():    self.dialog.draw(surface)
        pygame.display.update()

    def event_handler(self, event, keys_pressed, mouse_buttons_pressed, mouse_movement=False, mouse_pos=(0, 0)):
        if event.type == pygame.KEYDOWN:                    self.keyboard_handler(keys_pressed)
        if mouse_movement or any(mouse_buttons_pressed):    self.mouse_handler(event, mouse_buttons_pressed, mouse_movement, mouse_pos)                 

    def keyboard_handler(self, keys_pressed):
        if keys_pressed[pygame.K_DOWN]:         self.change_active_sprite(self.active_sprite_index+1)
        if keys_pressed[pygame.K_UP]:           self.change_active_sprite(self.active_sprite_index-1)
        if keys_pressed[pygame.K_LEFT]:         self.active_sprite.sprite.hitbox_action('left_arrow')
        if keys_pressed[pygame.K_RIGHT]:        self.active_sprite.sprite.hitbox_action('right_arrow')
        if keys_pressed[pygame.K_RETURN]\
            or keys_pressed[pygame.K_KP_ENTER]\
            or keys_pressed[pygame.K_SPACE]:    self.active_sprite.sprite.hitbox_action('do_action_or_add_value')

    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if mouse_buttons[0]:    self.active_sprite.sprite.hitbox_action('first_mouse_button', value=mouse_position)
            elif mouse_buttons[2]:  self.active_sprite.sprite.hitbox_action('secondary_mouse_button', value=mouse_position)
        if mouse_movement: 
            colliding_sprite = pygame.sprite.spritecollideany(UtilityBox.get_mouse_sprite(mouse_position), self.dynamic_sprites.sprites())
            if colliding_sprite is not None:    self.change_active_sprite(self.get_sprite_index(colliding_sprite))  

    def change_active_sprite(self, index):
        if index is not self.active_sprite_index:
            size_sprite_list                    = len(self.dynamic_sprites.sprites())

            self.active_sprite_index            = index 
            if index >= size_sprite_list:       self.active_sprite_index = 0
            elif index < 0:                     self.active_sprite_index = size_sprite_list-1
            
            if self.active_sprite.sprite is not None:   
                self.active_sprite.sprite.set_hover(False) #Change the active back to the original state
                self.active_sprite.sprite.set_active(False)
            self.active_sprite.add(self.dynamic_sprites.sprites()[self.active_sprite_index])       #Adding the new active sprite
            self.active_sprite.sprite.set_hover(True)
            self.active_sprite.sprite.set_active(True)
        
    def get_sprite_index(self, sprite):
        sprite_list = self.dynamic_sprites.sprites()
        for i in range(0, len(sprite_list)):
            if sprite is sprite_list[i]:    return i