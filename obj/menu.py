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
from obj.utilities.utility_box import UtilityBox
from obj.screen import Screen
from obj.utilities.exceptions import NotEnoughSpritesException
from obj.utilities.surface_loader import ResizedSurface
from obj.ui_element import UIElement
from settings import USEREVENTS

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
    __default_config = {'slider_texture': None,
                        'do_align': False,
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
        self.active_sprite_index = 0
        Menu.generate(self, *elements)

    @staticmethod
    def generate(self, *elements):
        """Method that executes after the constructor of the superclass.
        Does all the needed work before fully deploying the menu.
        Args:
        Raises:
            NotEnoughSpritesException:  If the menu doesn't have any sprites."""
        UtilityBox.join_dicts(self.params, Menu.__default_config)
        if len(elements) > 0: 
            self.add_sprites(*elements)
        else:   
            raise NotEnoughSpritesException("A menu needs at least one element prior to the generation.")
        self.set_hit_sprite(self.sprites.sprites()[0])
        if self.params['do_align']:   
            self.center_sprites(alignment=self.params['alignment'])
        self.check_sprites()
        self.set_scroll(0)
    
    def check_sprites(self):
        """Adds a scroll if it's needed"""
        if any(sprite.rect.y > self.resolution[1] for sprite in self.sprites):
            overload = max((sprite.rect.y+sprite.rect.height)-self.resolution[1] for sprite in self.sprites)
            self.scroll_length = int(self.resolution[1]*0.10+overload)
            self.scroll_sprite  = UIElement.factory('slider_scroll_menu', "menu_scroll", USEREVENTS.DIALOG_USEREVENT,\
                                                    (0.95, 0), (0.05, 1), self.resolution, text="", default_values=0.0,\
                                                    loop=False, shows_value=False, texture=self.params['scroll_image'],\
                                                    overlap_texture=self.params['scroll_texture'])

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

    def keyboard_handler(self, keys_pressed, event):
        """Handles any pygame keyboard related event. This allows for user interaction with the object.
        Posibilities:
        TODO
        Args:
            keys_pressed (:dict: pygame.keys):  Dict in which the keys are keys and the items booleans.
                                                Said booleans will be True if that specific key was pressed.
        """
        super().keyboard_handler(keys_pressed, event)
        if self.dialog:
            return
        if self.hit_sprite and self.hit_sprite.has_input:
            self.send_to_active_sprite('add_input_character', pygame.key.name(event.key))
        if keys_pressed[pygame.K_DOWN] and self.sprites.has(self.hit_sprite):   #Handling of normal sprites
            old_index = self.active_sprite_index
            while True:
                self.change_active_sprite(self.active_sprite_index+1)
                if (self.hit_sprite.visible and self.hit_sprite.enabled)\
                or self.active_sprite_index is old_index:
                    break
        if keys_pressed[pygame.K_UP] and self.sprites.has(self.hit_sprite):
            old_index = self.active_sprite_index
            while True:
                self.change_active_sprite(self.active_sprite_index-1)
                if (self.hit_sprite.visible and self.hit_sprite.enabled)\
                or self.active_sprite_index is old_index:
                    break
        if keys_pressed[pygame.K_LEFT]:
            if self.hit_sprite == self.scroll_sprite != None:
                self.set_hit_sprite(self.sprites.sprites()[0])
            else:
                self.send_to_active_sprite('left_arrow', -1)
        if keys_pressed[pygame.K_RIGHT]:
            if self.hit_sprite == self.scroll_sprite != None:
                self.set_hit_sprite(self.sprites.sprites()[0])
            else:
                self.send_to_active_sprite('right_arrow', -1)
        if (keys_pressed[pygame.K_RETURN]\
            or keys_pressed[pygame.K_KP_ENTER]\
            or keys_pressed[pygame.K_SPACE]):
                self.send_to_active_sprite('do_action_or_add_value', -1)

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
        super().mouse_handler(event, mouse_buttons, mouse_movement, mouse_position)
        if self.dialog:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.get_colliding_sprite(): #Dont want to have the last active sprite triggering if we are not hovering it
                if mouse_buttons[0]:
                    self.send_to_active_sprite('first_mouse_button', value=mouse_position)
                elif mouse_buttons[1]:  
                    self.send_to_active_sprite('center_wheel_mouse_button', value=mouse_position)
                elif mouse_buttons[2]:  
                    self.send_to_active_sprite('secondary_mouse_button', value=mouse_position)
        if mouse_movement:
            colliding_sprite = self.get_colliding_sprite()
            if self.sprites.has(colliding_sprite):
                self.change_active_sprite(self.get_sprite_index(colliding_sprite))

    def change_active_sprite(self, index):
        """Changes the active sprite of the Menu (The one that will execute if a trigger key is pressed)
        Args:
            ineex (int):    Index of the new active sprite in the sprite list."""
        if index is not self.active_sprite_index:
            size_sprite_list = len(self.sprites.sprites())
            self.active_sprite_index = index 
            if index >= size_sprite_list:       
                self.active_sprite_index = 0
            elif index < 0:                     
                self.active_sprite_index = size_sprite_list-1
            self.set_hit_sprite(self.sprites.sprites()[self.active_sprite_index])

    def show_dialog(self, id_):
        super().show_dialog(id_)
        self.clear_active_sprite()

    def hide_dialog(self):
        super().hide_dialog()
        self.clear_active_sprite()             

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