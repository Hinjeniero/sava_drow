import pygame, math, numpy
from pygame.locals import *
import gradients #Gradients in polygons
import ptext #Gradients in text
from polygons import Circle, Rectangle
from Setting import *
from pygame_test import PygameSuite

class Menu (object):``
    game_folder = os.path.dirname(__file__)
    img_folder = os.path.join(game_folder, 'img')
    sounds_folder = os.path.join(game_folder, 'sounds')
    __default_config = {'background_path': None,
                        'logo_path': None,
                        'logo_size': 0.20,
                        'title_menu': '',
                        'title_text_size': 0.15,
                        'soundtheme_path': Menu.sounds_folder+'maintheme.mp3',
                        'soundeffect_path': Menu.sounds_folder+'/option.ogg',
                        'font': None,
                        'max_font':200
    }

    def __init__(self, id, **config_params):
        #Basic info saved
        self.id = id
        self.config = Menu.__default_config.copy().update(**config_params)
        #TODO, if we pass some sliders and some shit, take it and process it

        #Graphic elements
        self.static_sprites = pygame.sprite.Group() #Things without interaction
        self.dynamic_sprites = pygame.sprite.Group() #Things with interaction, like buttons and such
        self.active_sprites = pygame.sprite.GroupSingle(_use_update=True) #Selected from dynamic_elements, only one at the same time
        self.background = self.load_background(self.settings["resolution"].current(), self.bgpath)
        self.settings = []

        #Music & sounds
        self.main_theme = pygame.mixer.music.load(self.config['soundtheme_path'])
        self.option_sound = pygame.mixer.Sound(file=self.config['soundeffect_path'])
        #self.option_sound.set_volume(1)

        self.create_menu(logo_path=logo_path, logo_size=(res[0]*logo_size, res[1]*logo_size), title_text=title_text, \
         title_size=(res[0]*title_size, res[1]*title_size), options_list=options)

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
                self.settings.append(self.__create_setting(element))
                self.dynamic_sprites.add(element[0])
            except TypeError:
                print("An element couldn't be added, due to being a tuple, but not an ui_element subclass.")
        else:
            if type(element) is pygame.Surface:
                self.static_sprites.add(element)
            else:
                raise TypeError("Elements should be a pygame.Surface, or an ui_element subclass.") 

    def __create_setting(self, element):
        graphic_element, default_value = element[0], element[1]
        if issubclass(type(graphic_element), Setting):
            if type(graphic_element) is (Slider or Button):
                return Setting.factory(pygame.USEREVENT+Menu.__event_id_counter, graphic_element, default_value)
        raise TypeError("Creating Setting subclasses are only compatible with Buttons and Sliders")

    def update_settings(self):#TODO redefine
        global screen
        screen = pygame.display.set_mode(self.settings["resolution"].current())
        
        res = self.settings["resolution"].current()
        self.top_elements.clear()
        self.elements.clear()
        self.create_menu(logo_path=self.logo_path, logo_size=(res[0]*self.logo_size, res[1]*self.logo_size), title_text=self.title,\
         title_size=(res[0]*self.title_size, res[1]*self.title_size), options_list=self.options)
        self.background = self.load_background(self.settings["resolution"].current(), self.bgpath)

    #centering --> 0 = centered, 1 = left, 2 = right   3TODO add accept button and  array of booleans 
    def create_menu(self, logo_path = None, logo_size = (0, 0), title_text = None, title_size = (0, 0), options_list=[], centering = 0, text_color = (255, 255, 255), margin = 0.05):
        res = self.settings["resolution"].current()
        margin = (res[0]*margin, res[1]*margin) #tuple containing the margin
        
        #Establishing the offsets to draw all the components of the menu
        if centering is 0: #Centered
            horizontal_offset = res[0]/2
        elif centering is 1: #Left
            horizontal_offset = margin[0]
        elif centering is 2: #Right
            horizontal_offset = res[0] - margin[0]
        vertical_offset = margin[1]
        
        #Creating logo, with his texture and position at the top
        if logo_path is not None:
            horizontal_offset = res[0]/2 - logo_size[0]/2
            logo_rect = Rectangle(horizontal_offset, vertical_offset, logo_size[0], logo_size[1]) 
            logo_texture = pygame.transform.scale(pygame.image.load(logo_path), logo_rect.size)
            logo = UI_Element('logo', logo_texture, logo_rect)
            self.top_elements.append(logo) #Adding to menu
            vertical_offset = logo.hitbox.pos[1] + logo.hitbox.size[1] + margin[1] #Getting the next free space to draw element

        #Creating title, with the rendered text and his position under the logo
        if title_text is not None:
            if centering is 0: #Centered
                horizontal_offset = res[0]/2 - title_size[0]/2
            #Centering 1 and 2 are already done up there
            title_rect = Rectangle(horizontal_offset, vertical_offset, title_size[0], title_size[1]) #Hitbox of the title text
            size_font = self.max_size_text(title_text, self.max_font, title_rect.size)
            font = pygame.font.Font(self.font, size_font)
            title_surf = font.render(title_text, True, text_color) #This returns a surface. Text will be a surface.
            title_rect.size = (title_rect.size[0], title_surf.get_height())
            title = UI_Element('title_text', title_surf, title_rect)
            self.top_elements.append(title) #Adding to menu
            vertical_offset = title.hitbox.pos[1] + title.hitbox.size[1] + margin[1] #Getting the next free space to draw element

        ui_list = []
        for option in options_list:
            opt_rect = Rectangle(0, 0, res[0]-margin[0]*2, title_size[1]) #Hitbox of the text
            size_font = self.max_size_text(option[1], self.max_font, opt_rect.size) #Using same specs as the title. 
            font = pygame.font.Font(self.font, size_font)
            opt_surf = font.render(option[1], True, text_color) #This returns a surface. Text will be a surface.
            opt_element = UI_Element(option[0], opt_surf, opt_rect)
            ui_list.append(opt_element)

        self.resize_and_place_elements(ui_list, vertical_offset=vertical_offset) #Repositioning and scaling the elements
        for element in ui_list:
            self.elements.append(element)

    def load_background(self, size, background_path=None):
        if background_path is None:
            bg_surf = gradients.vertical(size, (255, 200, 200, 255), (255, 0, 0, 255)) #Gradient from white-ish to red
        else:
            bg_surf = pygame.transform.scale(pygame.image.load(background_path), size)
        return bg_surf

    #All this follow a scheme that goes like: (horizontal_axis_pos, vertical_axis_pos), (horizontal_axis_size, vertical_axis_size)
    #0 - centered, 1 - left sided, 2 - right sided
    def resize_and_place_elements(self, elements_list, space_between_elements = 0.10, vertical_offset = 0.00, horizontal_offset = 0.00,\
    alignment_mode = 0):
        size = list(screen.get_size()) #Multiplying the entire tuple by a scalar       
        size[1] -= vertical_offset
        total = 0
        for element in elements_list:
            total += element.hitbox.size[1]*(1+space_between_elements) #Adding the size of the height (Since the width will always be the same) and the size of the inter-hitbox space  
        
        if total > size[1]: #Getting the proportion needed to make everything fit within the window
            resize_relation = size[1]/total #The relation is totalsize/myactualsize. totalsize = screen width
            for element in elements_list: #Actual resizing and reescaling
                element_size = list([int(resize_relation*x) for x in element.hitbox.size]) #Multiplying the entire tuple 
                element.hitbox.size = tuple(element_size)
                element.surface_resize()

        #Now, the placing (Position)
        last_y_position = vertical_offset
        for element in elements_list:
            position = list(element.hitbox.pos)
            position[1] = last_y_position
            last_y_position += element.hitbox.size[1]*(1+space_between_elements)
            if alignment_mode is 0:
                position[0] = size[0]/2 - element.hitbox.size[0]/2 + size[0]*horizontal_offset  #The other component of the tuple
            elif alignment_mode is 1:
                position[0] = element.hitbox.size[0] + size[0]*horizontal_offset
            elif alignment_mode is 2:
                position[0] = size[0] - element.hitbox.size[0] - size[0]*horizontal_offset
            element.hitbox.pos = tuple(position)
            element.set_surface_pos()

    def add_element(self, ui_element, ui_element_name):
        self.menus[ui_element_name] = ui_element

    def draw(self, show_fps=True, surface=screen):
        surface.blit(self.background, (0,0))
        index = 0
        for element in self.top_elements:
            self.draw_element(surface, element, hitbox=False)
        for element in self.elements:
            self.draw_element(surface, element, selected=(self.active_option_index == index))
            index+=1
        #Timer control
        if self.timer_option is fps*2:
            self.timer_option = -1 #To make it 0 after the +1
        self.timer_option+=1 

        if show_fps:
            fnt = pygame.font.Font(None, 60)
            frames = fnt.render(str(int(clock.get_fps())), True, pygame.Color('white'))
            surface.blit(frames, (50, 150))
        pygame.display.update() #We could use flip too since in here we are not specifying any part of the surface #TODO delete

    def event_handler(self, events, keys_pressed, mouse_movement=False, mouse_pos=(0, 0)):
        for event in events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                else:
                    all_keys = pygame.key.get_pressed() #Getting all keys pressed in that frame
                    if all_keys[pygame.K_DOWN]: 
                        self.change_active_option(self.active_option_index+1)
                    if all_keys[pygame.K_UP]:
                        self.change_active_option(self.active_option_index-1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_buttons_clicked = pygame.mouse.get_pressed()
                if mouse_buttons_clicked[0]: #This is a tuple, the first one is the left button
                    self.change_setting(self.elements[self.active_option_index].id, inc_index=+1)
                elif mouse_buttons_clicked[2]: #right button
                    self.change_setting(self.elements[self.active_option_index].id, inc_index=-1)
        if mouse_movement:
            self.change_active_option(self.mouse_collider(mouse_pos))
        return True

#List of (ids, text)
if __name__ == "__main__":
    timeout = 20
    testsuite = PygameSuite(fps=144)

    menu = Menu("main_menu", [("start_game", "Start game"), ("resolution", "Resolution"), ("flaity", "Flaity"), ("tio", "Tio"),\
    ("joder", "Joder"), ("loco", "Loco")], {"resolution" : resolutions}, background_path='background.jpg', logo_path="logo.jpg")
    testsuite.loop()