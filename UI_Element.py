import pygame, gradients
from polygons import *
from resizer import Resizer
from pygame_test import PygameSuite

BLACK = pygame.Color("black")
WHITE = pygame.Color("white")
RED = pygame.Color("red")
GREEN = pygame.Color("green")
BLUE = pygame.Color("blue")
DARKGRAY = pygame.Color("darkgray")
LIGHTGRAY = pygame.Color("lightgray")

class TextSprite(pygame.sprite.Sprite):
    def __init__(self, font_surface, position=(0,0)):
        super().__init__()
        self.image = font_surface
        self.rect = pygame.Rect(position,self.image.get_size())

#Graphical element, automatic creation of a menu's elements
class UiElement(pygame.sprite.Sprite):
    """Superclass UI_Element. Subclasses are Button and Slider.
    This class consists of a set of basic polygons like circles or rectangles.

    The strength of this class relies on the automatic generation and extensive flexibility
    due to all the optional parameters in the generation of the element.
    The basic generate_surface of the superclass generates a rectangle. Any other polygon
    should have that method overloaded.
    All colors have a format of a tuple of 4 values of the RGBA form.
    Attributes:
        position: Position that this surface will have on the destination surface if it's drawed.
        size: Size of the surface containing the polygon, is a tuple (width, height).
        surf_color: Background color of the polygon if gradient and image are false. Default is solid red.
        surf_image: Texture to use in the surface. It's a loaded image. Default is None.
        border: True if the polygon has a border. Default is True.
        border_size: Width of the border in pixels. Default is 2 pixels.
        border_color: Color of the border. Default is solid white.
        use_gradient: True if the polygon color is a gradient. Default is True.
        start_color: Starting color of the gradient. Default is gray.
        end_color: Ending color of the gradient. Default is dark gray.
        gradient_type: Orientation of the gradient, 0 for vertical, 1 or whatever for horizontal. Default is 0 (Vertical)
    """
    __default_config = {'position': (0, 0),
                        'size': (0, 0),
                        'texture': None,
                        'color': RED,
                        'border': True,
                        'border_width': 2,
                        'border_color': WHITE,
                        'gradient': True,
                        'start_gradient': LIGHTGRAY,
                        'end_gradient': DARKGRAY,
                        'gradient_type': 0
    }

    @staticmethod
    def factory(user_event_id, position, size, default_values, **params):
        '''Method to decide what subclass to create according to the default values.
        If it's a number, a Slider with an associated value. 
        If its a list of shit, a button with those predetermined options.
        Factory pattern method.

        Args:
            user_event_id:
            ui_element:
            default_values:
        
        Raise:
            AttributeError:
        '''
        if type(default_values) is (list or tuple):
            return Button(user_event_id, position, size, tuple(default_values), params)
        elif type(default_values) is (int or float):
            return Slider(user_event_id, position, size, float(default_values), params)
        else:
            return AttributeError("The provided set of default values does not follow any of the existing objects logic.")
    
    def __init__(self, user_event_id, position, size, **params):
        #Hierarchy from sprite
        super().__init__()
        self.params =  UiElement.__default_config.copy().update(**params)
        self.params["position"] = position
        self.params["size"] = size

        self.rect = pygame.Rect(position, size) 
        self.pieces = pygame.sprite.OrderedUpdates()
        self.__event_id = user_event_id
        self.image = None           #Will be assigned a good object in the next line
        self.generate_object()      #Generate the first sprite and the self.image attribute
    
    def dict_update(self, new_dict):
        pass

    def generate_text(self, text, text_color, text_alignment, font, font_size):
        font = pygame.font.Font(font, font_size)
        text_surf = font.render(text, True, text_color)
        y_pos = (self.rect.height//2)-(text_surf.get_height()//2)
        #1 is left, 2 is right, 0 is centered
        x_pos = self.rect.width*0.02 if text_alignment is 1 else self.rect.width-text_surf.get_width() if text_alignment is 2 else (self.rect.width//2)-(text_surf.get_width()//2)
        return TextSprite(text_surf, (x_pos, y_pos))
        #surface.blit(text_surf, (x_pos, y_pos))
        #return text_surf, pygame.Rect(x_pos, y_pos, text_surf.get_size())
    
    def generate_image(self):
        try:
            sprites = self.pieces.sprites().copy()
            base_surf = sprites[0].image.copy()
            del sprites[0]
            for sprite in sprites:
                base_surf.blit(sprite.image, sprite.rect.topleft)
            return base_surf
        except IndexError:
            print("To generate an image you need at least one sprite in the list of sprites")

    def generate_object(self, rect=None, generate_image=True):
        if rect is not None:        self.rect = rect
        self.params["position"] =   self.rect.topleft
        self.params["size"] =       self.rect.size
        self.pieces.empty()
        self.pieces.add(Rectangle(self.params['position'], self.params['size'], self.params['texture'], self.params['color'],\
                                self.params['border'], self.params['border_width'], self.params['border_color'],\
                                self.params['gradient'], self.params['start_gradient'], self.params['end_gradient'], self.params['gradient_type']))
        if generate_image:    self.image = self.generate_image()

    def draw(self, surface):
        pass

    def send_event(self):
        my_event = pygame.event.Event(self.__event_id, value=self.get_value())
        pygame.event.post(my_event)

class Button (UiElement):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'text': 'default',
                        'font': None,
                        'max_font_size': 50,
                        'text_centering': 0,
                        'text_color': WHITE,
                        'shows_value': False
    }

    def __init__(self, user_event_id, element_position, element_size, set_of_values, **params):
        #Initializing super class
        super().__init__(element_position, element_size, params)

        for key in Button.__default_config.keys(): #Can't do it like in the superclass
            key = key.lower().replace(" ", "_")
            if self.params.has_key(key):
                self.params[key] = Button.__default_config[key]

        self.generate_object()      #Generate the first sprite and the self.image attribute
        
        #Regarding funcionality
        self.values = set_of_values
        self.index = 0

        #Regarding animation
        self.speed = 5
        self.mask_color = WHITE
        self.transparency = 0
        self.transparency_speed = 15

    def update(self):
        self.rect.x += self.speed
        if self.rect.x < self.speed:    self.speed = -self.speed

        self.transparency += self.transparency_speed
        if self.transparency >= 255:    self.transparency_speed = -self.transparency_speed 

    def generate_object(self, rect=None, generate_image=True):
        super().generate_object(rect=rect, generate_image=False)
        fnt_size = Resizer.max_font_size(self.params['text'], self.rect.size, self.params['max_font_size'], self.params['font'])
        self.pieces.add(self.generate_text(self.params['text'], self.params['text_color'], self.params['text_centering'], self.params['font'], fnt_size)) 
        if generate_image:    self.image = self.generate_image()

    def resize(self, new_size):
        new_surf = Resizer.surface_resize(self.image, new_size)
        ratio = new_surf.get_size()/self.rect.size      #Ratio going from 0 to 1 
        #for hitbox_pos, text_pos in zip(self.rect.topleft, self.text_rect.topleft)

    def return_active_surface(self):
        overlay = pygame.Surface(self.rect.size).fill(self.mask_color)
        return self.image.copy().blit(overlay, (0,0))

    #For the sake of writing short code
    def get_value(self):
        return self.values[self.index]

    def hitbox_action(self, command, value=-1):
        if 'dec' in command or 'min' in command or 'left' in command:   self.dec_index()
        elif 'inc' in command or 'add' in command or 'right' in command:  self.inc_index()
        self.send_event()


    def inc_index(self):
        self.index += 1 if self.index < len(self.values) else 0

    def dec_index(self):
        self.index -= 1 if self.index > 0 else len(self.values)-1

class Slider (UiElement):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'text': 'null',
                        'font': None,
                        'max_font_size': 50,
                        'text_centering': 1,
                        'text_color': WHITE,
                        'shows_value': False,
                        'slider_color': GREEN,
                        'slider_gradient': True,
                        'slider_start_color': LIGHTGRAY,
                        'slider_end_color': DARKGRAY,
                        'slider_border': True, 
                        'slider_border_color': BLACK,
                        'slider_border_size': 2,
                        'slider_type': 1
    }

    def __init__(self, user_event_id, element_position, element_size, default_value, **params):
        #Initializing super class
        super().__init__(element_position, element_size, params)

        for key in Button.__default_config.keys():  #Can't do it like in the superclass
            key = key.lower().replace(" ", "_")
            if not self.params.has_key(key):        #If with the superclass update, we dont have this key (The user did not input it)
                self.params[key] = Button.__default_config[key]
        
        self.generate_object()  
        
        #Regarding funcionality 
        self.value = default_value

    def generate_object(self, rect=None, generate_image=True):
        super().generate_object(rect=rect, generate_image=False)
        fnt_size = Resizer.max_font_size(self.params['text'], self.rect.size, self.params['max_font_size'], self.params['font'])
        self.pieces.add(self.generate_text(self.params['text'], self.params['text_color'], self.params['text_centering'], self.params['font_text'], fnt_size//2))    
        self.pieces.add(self.generate_slider(self.params['slider_color'], self.params['slider_gradient'], self.params['slider_start_color'],\
                                            self.params['slider_end_color'], self.params['slider_border'], self.params['slider_border_color'],\
                                            self.params['slider_border_size'], self.params['slider_type']))    
        if generate_image:    self.image = self.generate_image()

    def generate_slider (self, slider_color, slider_gradient, start_color, end_color, slider_border, slider_border_color, slider_border_size, slider_type):
        '''Adds the slider to the surface parameter, and returns the slider surface for further purposes'''
        ratio = 3
        size = (self.rect.height, self.rect.height)
        #radius = self.rect.height//2
        if slider_type < 2:         #Circle
            slider = Circle((0,0), size, None, slider_color,\
                            slider_border, slider_border_size, slider_border_color,\
                            slider_gradient, start_color, end_color)
            if slider_type is 1:    #ellipse instead of circle, done by simply resizing the circle
                slider.rect.width //= ratio
                slider.image = pygame.transform.scale(slider.image, (slider.rect.width, slider.rect.height))
        else:                       #Rectangular one
            slider = Rectangle((0,0), tuple(size[0]//ratio, size[1]), None, slider_color,\
                                slider_border, slider_border_size, slider_border_color,\
                                slider_gradient, start_color, end_color)
        
        slider.rect.x = (self.rect.width-slider.rect.width)//2     #To adjust the offset error due to transforming the surface.
        return slider

    #Position must be between 0 and 1
    #When we know in which form will the parameter be passed, we will implement this
    #Could be remade into a more generic method called set_piece_pos, that have an index as a parameter, to modify any sprite of the collection
    def set_slider_position(self, new_position):    #TODO test to check if the list works by reference
        sprites = self.pieces.sprites()
        if new_position > 0 and new_position < 1:   #This means its a porcentual ratio
            sprites[-1].rect.x = self.rect.width*new_position
        elif new_position > 1:
            sprites[-1].rect.x = int(new_position)
        else:
            raise AttributeError ("Can't set a negative slider position")

    def get_value(self):
        return self.value

    def hitbox_action(self, command, value=-1):
        if 'dec' in command or 'min' in command or 'left' in command:       self.value -= 0.1 if self.value >= 0.1 else 1
        elif 'inc' in command or 'add' in command or 'right' in command:    self.value += 0.1 if self.value <= 0.9 else 0
        if value is not -1:
            if type(value) is tuple:            mouse_x = value[0]
            elif type(value) is pygame.Rect:    mouse_x = value.x
            else:                               raise TypeError("Type of value in slider method Hitbox_Action must be Rect or tuple.")
        pixels = mouse_x-self.sprite.rect.x         #Pixels into the bar, that the slider position has.
        self.value = (pixels) / self.sprite.rect.width
        self.set_slider_position(pixels)
        self.image = self.generate_image()          #Regenerate the image with the new slider position
        self.send_event()

if __name__ == "__main__":
    timeout = 20
    testsuite = PygameSuite(fps=144)
    '''slidie = Slider((50, 50), (100, 25), "test1.5", None, 200)
    slidou = Slider( (250, 50), (300, 25),"test1.5", None, 200)
    slede = Slider( (600, 50), (600, 25), "test1.5", None, 200)
    slada = Slider( (200, 100), (400, 50), "test1.5", None, 200, slider_type=0)
    buttkun = Button( (200, 200), (800, 50),"Shitty Button", None, 200)
    baton = Button((200, 300), (800, 400), "SUPER BUTTON", None, 200)
    print(type(baton))
    print(issubclass(type(baton), UiElement))
    print(type(slidie))
    #Adding elements
    testsuite.add_elements(slidou, slidie, slede, slada, buttkun, baton)'''
    testsuite.loop(seconds = timeout)