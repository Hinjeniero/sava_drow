import pygame, math, numpy, os
from pygame.locals import *
from UI_Element import *
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
                        'soundtheme_path': sounds_folder+'\maintheme.mp3',
                        'soundeffect_path': sounds_folder+'\option.ogg',
                        'font': None,
                        'max_font':200,
    }

    def __init__(self, id, resolution, centering_tuple, *elements, **params):
        #Basic info saved
        self.id = id
        self.resolution = resolution
        self.config = Menu.__default_config.copy()
        self.config.update(params)
        
        #Graphic elements
        self.static_sprites = pygame.sprite.Group() #Things without interaction
        self.dynamic_sprites = pygame.sprite.OrderedUpdates() #Things with interaction, like buttons and such
        self.active_sprite = pygame.sprite.GroupSingle() #Selected from dynamic_elements, only one at the same time
        self.active_sprite_index = 0
        self.background = self.load_background(resolution, self.config['background_path'])

        #Music & sounds
        self.main_theme = pygame.mixer.music.load(self.config['soundtheme_path'])
        self.option_sound = pygame.mixer.Sound(file=self.config['soundeffect_path'])
        #self.option_sound.set_volume(1)

        if len(elements) > 0: 
            self.add_elements(*elements) 
            self.generate(self.resolution, centering=centering_tuple[0], centering_mode=centering_tuple[1])
        else:   raise IndexError("A menu needs at least one element prior to the generation.")

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
        if issubclass(type(element), UiElement):    self.dynamic_sprites.add(element)
        elif type(element) is pygame.Surface:       self.static_sprites.add(element)
        else:                                       raise TypeError("Elements should be a pygame.Surface, or an ui_element subclass.") 
    
    def animation(self):
        self.active_sprite.update()

    def generate(self, resolution, centering=True, centering_mode=0):
        self.__adjust_elements(resolution)
        if centering:   self.__center_elements(centering_mode)
        self.active_sprite.add(self.dynamic_sprites.sprites()[0])

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
        if any(ratio < 1 for ratio in ratios):                                          #If any axis needs resizing
            for sprite in total_sprites:
                position = tuple([int(x*y) if x<1 else y for x,y in zip(ratios, sprite.rect.topleft)])
                size =     tuple([int(x*y) if x<1 else y for x,y in zip(ratios, sprite.rect.size)])
                sprite.generate_object(rect=pygame.Rect(position, size))                #Adjusting size

    def __center_elements(self, centering_mode):
        screen_width = self.resolution[0]
        sprites = self.static_sprites.sprites().copy()
        sprites.extend(self.dynamic_sprites.sprites()) 
        for sprite in sprites:
            sprite.rect.left = (screen_width-sprite.rect.width)/2
            sprite.save_state()

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
            
        self.mouse_handler(event, mouse_buttons_pressed, mouse_movement, mouse_pos)                    #Handling regarding mouse #TODO complete call

    def mouse_handler(self, event, mouse_buttons, mouse_movement, mouse_position):
        if event.type == pygame.MOUSEBUTTONDOWN:             #If a mouse button was clicked
            if mouse_buttons[0]:    self.active_sprite.sprite.hitbox_action('add_mouse_button', value=mouse_position)
            elif mouse_buttons[2]:  self.active_sprite.sprite.hitbox_action('dec_mouse_button', value=mouse_position)
        
        if mouse_movement: 
            mouse_hitbox = pygame.sprite.Sprite()
            mouse_hitbox.rect = pygame.Rect(mouse_position, (2,2))
            colliding_sprite = pygame.sprite.spritecollideany(mouse_hitbox, self.dynamic_sprites.sprites())
            if colliding_sprite is not None:    self.change_active_sprite(self.get_sprite_index(colliding_sprite))

    def change_active_sprite(self, index):
        size_sprite_list =                  len(self.dynamic_sprites.sprites())

        self.active_sprite_index =          index
        if index >= size_sprite_list:       self.active_sprite_index = 0
        elif index < 0:                     self.active_sprite_index = size_sprite_list-1
        
        if self.active_sprite.sprite is not None:   self.active_sprite.sprite.restore()     #Change the active back to the original state
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
    BLACK = pygame.Color("black")
    WHITE = pygame.Color("white")
    RED = pygame.Color("red")
    GREEN = pygame.Color("green")
    BLUE = pygame.Color("blue")
    DARKGRAY = pygame.Color("darkgray")
    LIGHTGRAY = pygame.Color("lightgray")
    timeout = 20

    #Create elements
    sli = UiElement.factory(pygame.USEREVENT+1, (10,10), (800, 100), (0.2))
    but = UiElement.factory(pygame.USEREVENT+2, (10, 160), (800, 100), (30, 40))
    sli2 = UiElement.factory(pygame.USEREVENT+3, (10, 310), (800, 100), (0), text="Slider")
    but2 = UiElement.factory(pygame.USEREVENT+4, (10, 460), (800, 100), ((30, 40)), text="Button")
    sli3 = UiElement.factory(pygame.USEREVENT+5, (10, 960), (800, 100), (1), text="SuperSlider", slider_type=0, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but3 = UiElement.factory(pygame.USEREVENT+6, (10, 1110), (800, 100), ((30, 40)), text="SuperButton", start_gradient = GREEN, end_gradient=BLACK)
    sli4 = UiElement.factory(pygame.USEREVENT+7, (10, 1260), (800, 100), (0.8), text="LongTextIsLongSoLongThatIsLongestEver", slider_type=2, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but4 = UiElement.factory(pygame.USEREVENT+8, (10, 1410), (800, 100), ((30, 40)), text="LongTextIsLongSoLongThatIsLongestEver", start_gradient = GREEN, end_gradient=BLACK)
    
    #Create Menu
    menu = Menu("MainMenu", resolution, (True, 0), sli, but, sli2, but2, sli3, but3, sli4, but4)
    
    #Start the test
    loop = True
    while loop:
        clock.tick(144)
        menu.animation()
        menu.draw(screen)       #Drawing the sprite group
        fnt = pygame.font.Font(None, 60)
        frames = fnt.render(str(int(clock.get_fps())), True, pygame.Color('white'))
        screen.blit(frames, (50, 150))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       loop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:    loop = False
            else:                               menu.event_handler(event, pygame.key.get_pressed(), pygame.mouse.get_pressed(),\
                                                                    mouse_movement=(pygame.mouse.get_rel() != (0,0)), mouse_pos=pygame.mouse.get_pos())
        pygame.display.update()  #Updating the screen