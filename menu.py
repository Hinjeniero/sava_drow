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
                        'title_text_size': 0.15
    }

    def __init__(self, id_, event_id, resolution, centering_tuple, *elements, **params):
        super().__init__(id_, event_id, resolution, **params)
        #Basic info saved
        self.alignment              = centering_tuple
        UtilityBox.check_missing_keys_in_dict(self.params, Menu.__default_config)
        #Graphic elements
        self.static_sprites         = pygame.sprite.Group()             #Things without interaction
        self.dynamic_sprites        = pygame.sprite.OrderedUpdates()    #Things with interaction, like buttons and such
        self.active_sprite          = pygame.sprite.GroupSingle()       #Selected from dynamic_elements, only one at the same time
        self.active_sprite_index    = 0

        if len(elements) > 0: 
            self.add_elements(*elements)
            self.generate(self.resolution, centering=self.alignment[0], centering_mode=self.alignment[1])
        else:   raise IndexError("A menu needs at least one element prior to the generation.")

    def generate(self, resolution, centering=True, centering_mode=0):
        self.__adjust_elements(resolution)
        if centering:   self.__center_elements(centering_mode)
        self.active_sprite.add(self.dynamic_sprites.sprites()[0])

    def update_resolution(self, resolution):
        super().update_resolution(resolution)
        #Regenerate elements
        all_sprites = self.static_sprites.sprites()
        all_sprites.extend(self.dynamic_sprites.sprites())
        #TODO IM HERE RN
        for sprite in all_sprites:  sprite.generate(rect=sprite.get_rect_if_canvas_size(resolution))
        #TODO Generate elements in case it hasn't been done
        if self.have_dialog():      self.dialog.sprite.generate(rect=sprite.get_rect_if_canvas_size(resolution))
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
    
    def animation(self):
        self.active_sprite.update()

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

    def __center_elements(self, centering_mode):
        screen_width = self.resolution[0]
        sprites = self.static_sprites.sprites().copy()
        sprites.extend(self.dynamic_sprites.sprites()) 
        for sprite in sprites:
            sprite.rect.left = (screen_width-sprite.rect.width)/2
            sprite.save_state()

    def draw(self, surface, hitboxes=False, fps=True, clock=None):
        super().draw(surface)
        self.animation()
        self.static_sprites.draw(surface)
        self.dynamic_sprites.draw(surface)
        if fps: UtilityBox.draw_fps(surface, clock)
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
        if keys_pressed[pygame.K_KP_ENTER]\
            or keys_pressed[pygame.K_SPACE]:    self.active_sprite.sprite.hitbox_action('add_value')

    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if mouse_buttons[0]:    self.active_sprite.sprite.hitbox_action('first_mouse_button', value=mouse_position)
            elif mouse_buttons[2]:  self.active_sprite.sprite.hitbox_action('secondary_mouse_button', value=mouse_position)
        
        if mouse_movement: 
            colliding_sprite = pygame.sprite.spritecollideany(UtilityBox.get_mouse_sprite(mouse_position), self.dynamic_sprites.sprites())
            if colliding_sprite is not None:    self.change_active_sprite(self.get_sprite_index(colliding_sprite))  #TODO this can be done in a better way

    def change_active_sprite(self, index):
        size_sprite_list =                  len(self.dynamic_sprites.sprites())

        self.active_sprite_index =          index   #This all can be compressed in one line
        if index >= size_sprite_list:       self.active_sprite_index = 0
        elif index < 0:                     self.active_sprite_index = size_sprite_list-1
        
        if self.active_sprite.sprite is not None:   self.active_sprite.sprite.load_state()          #Change the active back to the original state
        self.active_sprite.add(self.dynamic_sprites.sprites()[self.active_sprite_index])            #Adding the new active sprite

    def get_sprite_index(self, sprite):
        sprite_list = self.dynamic_sprites.sprites()
        for i in range(0, len(sprite_list)):
            if sprite is sprite_list[i]:    return i

#List of (ids, text)
if __name__ == "__main__":
    #Variables
    resolution = (1280, 720)
    pygame.init()
    screen = pygame.display.set_mode(resolution)
    pygame.mouse.set_visible(True)
    clock = pygame.time.Clock()
    timeout = 20

    #Create elements
    sli = UiElement.factory("slider1_command_action", pygame.USEREVENT, (10,10), (800, 100), (0.2))
    but = UiElement.factory("button1_command_action", pygame.USEREVENT+1, (10, 160), (800, 100), (0, 10, 20, 30, 40))
    sli2 = UiElement.factory("slider2_command_action",pygame.USEREVENT+2, (10, 310), (800, 100), (0), text="Slider")
    but2 = UiElement.factory("button2_command_action",pygame.USEREVENT+3, (10, 460), (800, 100), ((50, 60, 70, 80)), text="Button")
    sli3 = UiElement.factory("slider3_command_action",pygame.USEREVENT+4, (10, 960), (800, 100), (1), text="SuperSlider", slider_type=0, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but3 = UiElement.factory("button3_command_action",pygame.USEREVENT+5, (10, 1110), (800, 100), ((90, 100, 110)), text="SuperButton", start_gradient = GREEN, end_gradient=BLACK)
    sli4 = UiElement.factory("slider4_command_action",pygame.USEREVENT+6, (10, 1260), (800, 100), (0.8), text="LongTextIsLongSoLongThatIsLongestEver", slider_type=2, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but4 = UiElement.factory("button4_command_action",pygame.USEREVENT+7, (10, 1410), (800, 100), (("platano", "naranja", "orange", "ouranch")), text="LongTextIsLongSoLongThatIsLongestEver", start_gradient = GREEN, end_gradient=BLACK)
    
    #Create Menu
    menu = Menu("MainMenu", pygame.USEREVENT, resolution, (True, 0), sli, but, sli2, but2, sli3, but3, sli4, but4)
    
    #Start the test
    loop = True
    while loop:
        clock.tick(144)
        menu.draw(screen, clock=clock)       #Drawing the sprite group
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       loop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:    loop = False
            elif event.type >= pygame.USEREVENT:
                print("Received event number "+str(event.type)+", with value "+str(event.value)+ ", with command "+str(event.command))
            if loop:            #If not exit yet                        
                menu.event_handler(event, pygame.key.get_pressed(), pygame.mouse.get_pressed(),\
                                    mouse_movement=(pygame.mouse.get_rel() != (0,0)), mouse_pos=pygame.mouse.get_pos())