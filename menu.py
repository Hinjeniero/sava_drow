import pygame, math, numpy
from pygame.locals import *
import gradients #Gradients in polygons
import ptext #Gradients in text
from polygons import Circle, Rectangle

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
resolution = (800, 600)
max_font = 200
pygame.mouse.set_visible(True)
clock = pygame.time.Clock()
fps = 60
half_fps = fps/2
screen = pygame.display.set_mode(resolution)
menus = {}

class Setting:
    def __init__(self, options=[], index=0):
        self.options=options
        self.index=index

    #For the sake of writing short code
    def current(self):
        return self.options[self.index]

class UI_Element:
    def __init__(self, id, surface, rect):
        self.surface = surface
        self.surface_position = (0, 0)
        self.id = id
        self.hitbox = rect #Contains the position and the size
        self.options = [] #Contains the possibilities
        self.options_active_index = 0

    #Resizing the surface to fit in the hitbox preserving the ratio, instead of fuckin it up
    def surface_resize(self):
        new_surf_size = list(self.surface.get_size()) #Copy of the size of the surface
        for surf_axis_size, hitbox_axis_size in zip(new_surf_size, self.hitbox.size):
            if surf_axis_size > hitbox_axis_size:
                ratio = (hitbox_axis_size/surf_axis_size)
                for i in range (0, len(new_surf_size)): #This way it modifies the list, the normal iterator doesn't work that way, assigning names and shit
                    new_surf_size[i] = int(new_surf_size[i]*ratio)
        self.surface = pygame.transform.scale(self.surface, tuple(new_surf_size)) #Resizing the surface

    #Sets the surface position on the hitbox
    def set_surface_pos(self, horizontal_offset=0, centering = 0):
        position = list(self.surface_position)
        if centering is 0: #Center
            position[0] = (self.hitbox.size[0]/2) - (self.surface.get_size()[0]/2)
        elif centering is 1: #Left
            position[0] = horizontal_offset
        elif centering is 2:
            position[0] = self.hitbox.size[0]-horizontal_offset
        self.surface_position = tuple(position)

class Menu:
    def __init__(self, id, options, settings, background_path=None, logo_path=None, theme_path=None, option_sound_path=None,\
    logo_size=0.20, title_text="Game", title_size=0.15, font=None, max_font=200):
        #Basic info saved
        self.id = id
        self.font = font
        self.bgpath = background_path
        self.logo_path = logo_path
        self.logo_size = logo_size
        self.title = title_text
        self.title_size = title_size
        self.options = options
        self.max_font = max_font
        
        #Music & sounds
        self.main_theme = pygame.mixer.music.load("maintheme.mp3")
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.15)
        self.option_sound = pygame.mixer.Sound(file="option.ogg")
        self.option_sound.set_volume(2)

        self.timer_option = 0 #This takes care of the graphical effects of the selected option
        self.top_elements = [] #The non-clickable elements (could be a logo, a drawing, a title...)
        self.elements = [] #The graphical elements that compose the menus
        self.settings = settings #The logical part of the menus, changing parameters like resolution and shit
        self.active_option_index = 0

        res = self.settings["resolution"].current()
        self.last_resolution = res #In case we want to implement the low_cost resize of the resolution

        self.font_size_table = self.fill_font_size_table()
        self.create_menu(logo_path=logo_path, logo_size=(res[0]*logo_size, res[1]*logo_size), title_text=title_text, \
         title_size=(res[0]*title_size, res[1]*title_size), options_list=options)
        self.background = self.load_background(self.settings["resolution"].current(), self.bgpath)

    #[rows increment font size, columns increment number of letters]
    def fill_font_size_table(self):
        aux = numpy.empty([self.max_font, self.max_font], dtype=(int, 2))
        for i in range (0, self.max_font):
            font = pygame.font.Font(self.font, i)
            txt = ""
            for j in range (0, self.max_font):
                aux[i][j]=font.size(txt)
                txt+="W" #Usually capital w is the biggest letter
        return aux
        
    #The id is the string that will identify the setting to change
    def add_setting(self, id_setting, options = []):
       setting = Setting(options=options)
       self.settings[id_setting.lower()] = setting

    #Incrementing the index of the option of the setting. (To use each time a click is detected on the option)
    def change_setting(self, id_setting, index=None, inc_index=None):
        id = id_setting.lower()
        if index is not None:
            self.settings[id].index = index
        elif inc_index is not None:
            self.settings[id].index += inc_index
        
        #Control of errors
        if self.settings[id].index > len(self.settings[id].options)-1:
            self.settings[id].index = 0
        elif self.settings[id].index < 0:
            self.settings[id].index = len(self.settings[id].options)-1
        self.update_settings()

    def get_setting (self, id_setting): 
        try:
            return self.settings[id_setting].current()
        except KeyError:
            print("The setting "+id_setting+"is not in this menu with id "+self.id)

    def update_settings(self):
        global screen
        screen = pygame.display.set_mode(self.settings["resolution"].current())
        
        res = self.settings["resolution"].current()
        self.top_elements.clear()
        self.elements.clear()
        self.create_menu(logo_path=self.logo_path, logo_size=(res[0]*self.logo_size, res[1]*self.logo_size), title_text=self.title,\
         title_size=(res[0]*self.title_size, res[1]*self.title_size), options_list=self.options)
        self.background = self.load_background(self.settings["resolution"].current(), self.bgpath)

    def change_active_option(self, index):
        if index != self.active_option_index: #If the option has changed
            self.option_sound.play()
            self.active_option_index = index
            self.timer_option = 0 #Restarting the graphical breathing effect
            if self.active_option_index >= len(self.elements):
                self.active_option_index = 0
            elif self.active_option_index < 0:
                self.active_option_index = len(self.elements)-1

    #centering --> 0 = centered, 1 = left, 2 = right
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

    def max_size_text_old(self, text, max_font, rect_size, font_chosen=None): #To check the max font that would fit
        for i in range (max_font, 0, -1): #Counter from max_text to 0
            font = pygame.font.Font(font_chosen, i)
            size = font.size(text) #Getting the needed size to render this text with i size
            if size[0] < rect_size[0] and size[1] < rect_size[1]: #If the rendered text fits in the rect, we return that font size
                return i

    def max_size_text(self, text, max_font, rect_size): #To check the max font that would fit
        length = len(text)
        for i in range (max_font-1, 0, -1): #Counter from max_text to 0
            text_size = tuple(self.font_size_table[i][length])
            if text_size[0] < rect_size[0] and text_size[1] < rect_size[1]: #If the rendered text fits in the rect, we return that font size
                return i

    def load_background(self, size, background_path=None):
        if background_path is None:
            bg_surf = gradients.vertical(size, (255, 200, 200, 255), (255, 0, 0, 255)) #Gradient from white-ish to red
        else:
            bg_surf = pygame.transform.scale(pygame.image.load(background_path), size)
        return bg_surf

    def update_resolution_low_cost(self, old_resolution, new_resolution):
        self.background = self.load_background(self.settings["resolution"].current(), background_path=self.bgpath)
        ratio = tuple(y/z for y,z in zip(old_resolution, new_resolution))
        for element in self.showing_menu:
            element.hitbox.size = tuple(int(x*ratio) for x in element.hitbox.size) 
            element.hitbox.pos = tuple(int(x*ratio) for x in element.hitbox.pos) 


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

    def draw_element(self, surface, element, hitbox=True, selected=False, scale_selected_option = 1.2):
        border_width = 2 #in px
        if hitbox:
            if not selected:
                color = element.hitbox.color #We cant use this later since this will mess up the reference, its not a copy
                position = element.hitbox.pos
                size = element.hitbox.size
            else: #active option, this part takes on the grasphical effects load
                #Color smooth transition
                clr = []
                for x in element.hitbox.color:
                    aux = self.timer_option
                    if aux > fps: #To create the bounding color effect
                        aux = fps-(aux-fps)
                    x+=aux*4
                    if x > 255:
                        x = 255
                    clr.append(x)
                color = tuple(clr)

                #Pos smooth transition
                aux = self.timer_option
                if aux > fps:
                    aux = fps-(aux-fps)
                pos = list(element.hitbox.pos)
                pos[0] -= half_fps+(aux/2)
                if pos[0] < 0:
                    pos[0] = 0
                position = tuple(pos)

                size = element.hitbox.size
                '''#Pos size transition
                aux = self.timer_option
                if aux > fps: #To create the bounding color effect
                    aux = fps-(aux-fps)
                dif = (aux/fps)/3
                print(dif)
                size = tuple([int(x*(1+dif)) for x in element.hitbox.size])'''

            border_rect = tuple([x+(border_width*2) for x in size])
            option_surf = pygame.Surface(border_rect)
                
            pygame.draw.rect(option_surf, (0, 0, 255), (0,0)+(border_rect), border_width) #Tuple of 4 components
            filling_rect = (border_width, border_width) + size #Tuple fo 4 components
            pygame.draw.rect(option_surf, color, filling_rect, 0)
            option_surf.set_alpha(255)

            option_surf.blit(element.surface, element.surface_position)
            surface.blit(option_surf, position)
        else: #If not hitbox
            surface.blit(element.surface, element.hitbox.pos)

    #Does all the shit related to the mouse hovering an option
    def mouse_collider(self, mouse_position):
        index = 0
        for ui_element in self.elements: #Mouse_position is a two component tuple
            if mouse_position[0] > ui_element.hitbox.pos[0] and mouse_position[0] < ui_element.hitbox.pos[0]+ui_element.hitbox.size[0] \
            and mouse_position[1] > ui_element.hitbox.pos[1] and mouse_position[1] < ui_element.hitbox.pos[1]+ui_element.hitbox.size[1]:
                return index
            index+=1
        return self.active_option_index #No option is selected, we leave whatever was active

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

    def test(self):
        loop = True
        while loop:
            clock.tick(fps)
            self.draw()
            if pygame.mouse.get_rel() != (0,0): #If there is mouse movement
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed(), mouse_movement=True, mouse_pos=pygame.mouse.get_pos())
            else:
                loop = self.event_handler(pygame.event.get(), pygame.key.get_pressed())

#List of (ids, text)
if __name__ == "__main__":
    resolutions = Setting(options=[(800, 600), (1024, 768), (1280, 720), (1366, 768), (160, 120), (320, 240), (640, 480)])
    menu = Menu("main_menu", [("start_game", "Start game"), ("resolution", "Resolution"), ("flaity", "Flaity"), ("tio", "Tio"),\
    ("joder", "Joder"), ("loco", "Loco")], {"resolution" : resolutions}, background_path='background.jpg', logo_path="logo.jpg")
    menu.test()