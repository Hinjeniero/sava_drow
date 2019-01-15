"""--------------------------------------------
menu module. Has the menu screen object, with methods and attributes
to support interaction.  
Have the following classes:
    Menu
--------------------------------------------"""
__all__     = ['Menu']
__version__ = '0.9'
__author__  = 'David Flaity Pardo'

#python libraries
import pygame
import math
import numpy
import os
from pygame.locals import *
#Selfmade libraries
from utility_box import UtilityBox
from screen import Screen
from exceptions import NotEnoughSpritesException

class Menu (Screen):
    """Menu class. Inherits from Screen.
    In short, it's an interactive menu for a game. 
    Has elements with collision detection. A game can have more than one.
    General class attributes:
        __default_config (:dict:): Contains parameters about the menu looks and elements.E
            do_align (boolean): True if we want to auto-modify the position of the input elements.
            alignment (str):    Alignment of the elements if do_align is True. Left, Center, Right.
    Attributes:
        active_sprite (:obj: pygame.sprite.GroupSingle):    Active element in the menu.
        active_sprite_index (int):  
    """
    __default_config = {'do_align': True,
                        'alignment': 'center'
    }

    def __init__(self, id_, event_id, resolution, *elements, **params):
        """Menu constructor. Inherits from Screen.
        Args:
            id_ (str):  Identifier of the Screen.
            event_id (int): Identifier of the Screen event.
            resolution (:tuple: int,int):  Size of the Screen. In pixels.
            *elements (:obj: Sprite):   Interactive elements/sprites of this menu. Usually buttons.            
            **params (:dict:):  Dict of keywords and values as parameters to create the Screen.
                                do_align, alignment.
        """
        #Graphic elements
        super().__init__(id_, event_id, resolution, **params)
        self.active_sprite          = pygame.sprite.GroupSingle()       #Selected from dynamic_elements, only one at the same time
        self.active_sprite_index    = 0
        Menu.generate(self, *elements)

    @staticmethod
    def generate(self, *elements):
        """Method that executes after the constructor of the superclass.
        Does all the needed work before fully deploying the menu.
        Args:
            *elements (:obj: Sprite):   Interactive elements/sprites of this menu. Usually buttons.
        Raises:
            NotEnoughSpritesException:  If the menu doesn't have any sprites."""
        UtilityBox.join_dicts(self.params, Menu.__default_config)
        if len(elements) > 0: 
            self.add_sprites(*elements)
        else:   
            raise NotEnoughSpritesException("A menu needs at least one element prior to the generation.")
        self.active_sprite.add(self.sprites.sprites()[0])
        self.active_sprite.sprite.set_hover(True)
        self.active_sprite.sprite.set_active(True)
        self.adjust_sprites()
        if self.params['do_align']:   
            self.center_sprites(alignment=self.params['alignment'])

    def adjust_sprites(self):
        """Adjust the current sprites of the Menu, to make them all fit within the Screen.
        First of all, we calculate how much space them all take. After that, we get the 
        ratio to which multiply them all so they fit tightly in the end.
        Changes sizes and positions of the sprites if required."""
        total_spaces    = (0, 0)
        last_y          = (0, 0)
        sprites         = self.sprites.sprites()
        #Counting, adding the pixels and comparing to the resolution
        for sprite in sprites:
            #Total spaces between topleft position elements == all sizes+all interelement spaces
            space       = tuple(x-y for x,y in zip(sprite.rect.topleft, last_y)) 
            total_spaces= tuple(x+y for x,y in zip(total_spaces, space))
            last_y      = list(sprite.rect.topleft)
        #Adds the last element size to the spaces.
        total_spaces    = tuple(sum(x) for x in zip(total_spaces, sprites[-1].rect.size))    

        #Getting the ratios between total elements and native resolution
        ratios = tuple(x/y for x, y in zip(self.resolution, total_spaces))
        if any(ratio < 1 for ratio in ratios):                  #If any axis needs resizing
            for sprite in sprites:
                position = tuple([int(x*y) if x<1 else y for x,y in zip(ratios, sprite.rect.topleft)])
                size =     tuple([int(x*y) if x<1 else y for x,y in zip(ratios, sprite.rect.size)])
                sprite.set_rect(pygame.Rect(position, size))    #Adjusting size
    
    def center_sprites(self, alignment='center'):
        """Center the current sprites of Menu. The alignment itself depends on the argument.
        Changes positions of the sprites if required.
        Args:
            alignment (str):    Alignment mode of the elements. Center, Left, Right."""
        screen_width = self.resolution[0]
        for sprite in self.sprites.sprites():
            x = (screen_width-sprite.rect.width)//2 if 'center' in alignment\
            else (0.05*screen_width) if 'left' in alignment\
            else (screen_width-sprite.rect.width-0.05*screen_width)
            sprite.set_position((x, sprite.rect.y))

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
        if event.type == pygame.KEYDOWN:                    self.keyboard_handler(keys_pressed)
        if mouse_movement or any(mouse_buttons_pressed):    self.mouse_handler(event, mouse_buttons_pressed, mouse_movement, mouse_pos)                 

    def keyboard_handler(self, keys_pressed):
        """Handles any pygame keyboard related event. This allows for user interaction with the object.
        Posibilities:
        TODO
        Args:
            keys_pressed (:dict: pygame.keys):  Dict in which the keys are keys and the items booleans.
                                                Said booleans will be True if that specific key was pressed.
        """
        self.play_sound('key')
        if keys_pressed[pygame.K_DOWN]:         self.change_active_sprite(self.active_sprite_index+1)
        if keys_pressed[pygame.K_UP]:           self.change_active_sprite(self.active_sprite_index-1)
        if keys_pressed[pygame.K_LEFT]:         self.active_sprite.sprite.hitbox_action('left_arrow', -1)
        if keys_pressed[pygame.K_RIGHT]:        self.active_sprite.sprite.hitbox_action('right_arrow', -1)
        if keys_pressed[pygame.K_RETURN]\
            or keys_pressed[pygame.K_KP_ENTER]\
            or keys_pressed[pygame.K_SPACE]:    self.active_sprite.sprite.hitbox_action('do_action_or_add_value', -1)

    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        """Handles any mouse related pygame event. This allows for user interaction with the object.
        Posibilities:
        TODO
        Args:
            event (:obj: pygame.event): Event received from the pygame queue.
            mouse_buttons (:list: booleans):    List with 3 positions regarding the 3 normal buttons on a mouse.
                                                Each will be True if that button was pressed.
            mouse_movement( boolean, default=False):    True if there was mouse movement since the last call.
            mouse_position (:tuple: int, int, default=(0,0)):   Current mouse position. In pixels.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if mouse_buttons[0]:    self.active_sprite.sprite.hitbox_action('first_mouse_button', value=mouse_position)
            elif mouse_buttons[2]:  self.active_sprite.sprite.hitbox_action('secondary_mouse_button', value=mouse_position)
        if mouse_movement: 
            colliding_sprite = pygame.sprite.spritecollideany(UtilityBox.get_mouse_sprite(), self.sprites.sprites())
            if colliding_sprite is not None:    self.change_active_sprite(self.get_sprite_index(colliding_sprite))  

    def change_active_sprite(self, index):
        """Changes the active sprite of the Menu (The one that will execute if a trigger key is pressed)
        Args:
            ineex (int):    Index of the new active sprite in the sprite list."""
        if index is not self.active_sprite_index:
            size_sprite_list                    = len(self.sprites.sprites())

            self.active_sprite_index            = index 
            if index >= size_sprite_list:       self.active_sprite_index = 0
            elif index < 0:                     self.active_sprite_index = size_sprite_list-1
            
            if self.active_sprite.sprite is not None:   
                self.active_sprite.sprite.set_hover(False) #Change the active back to the original state
                self.active_sprite.sprite.set_active(False)
            self.active_sprite.add(self.sprites.sprites()[self.active_sprite_index])       #Adding the new active sprite
            self.active_sprite.sprite.set_hover(True)
            self.active_sprite.sprite.set_active(True)
        
    def get_sprite_index(self, sprite):
        """Gets the index of a sprite in the sprite list.
        Args:
            (:obj: Sprite): The sprite whose index we want to know.
        Returns:
            (int):  Index of the input sprite in the sprite list."""
        sprite_list = self.sprites.sprites()
        for i in range(0, len(sprite_list)):
            if sprite is sprite_list[i]:    
                return i