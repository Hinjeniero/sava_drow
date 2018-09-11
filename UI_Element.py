import pygame, gradients, random
from polygons import *
from resizer import Resizer
from pygame_test import PygameSuite

__all__ = ["UiElement", "Button", "Slider"]
#Global names assigned to pygame default colors. For the sake of code, really.
BLACK = pygame.Color("black")
WHITE = pygame.Color("white")
RED = pygame.Color("red")
GREEN = pygame.Color("green")
BLUE = pygame.Color("blue")
DARKGRAY = pygame.Color("darkgray")
LIGHTGRAY = pygame.Color("lightgray")

UPDATE_LIMIT = 20
MAX_TRANSPARENCY = 255

class TextSprite(pygame.sprite.Sprite):
    '''Class TextSprite. Inherits from pygame.sprite, and the main surface is a text, from pygame.font.render.
    Attributes:
        image: Surface that contains the text
        rect: pygame.Rect containing the position and size of the text sprite.
    '''
    def __init__(self, font_surface, position=(0,0)):
        super().__init__()
        self.image = font_surface
        self.rect = pygame.Rect(position,self.image.get_size())

#Graphical element, automatic creation of a menu's elements
class UiElement(pygame.sprite.Sprite):
    """Superclass UI_Element. Subclasses are Button and Slider.
    This class consists of a set of basic polygons like circles or rectangles.

    Shared Class attributes:
        __default_config: Default parameters that will be assigned to each instance of the UiElement class.

    The strength of this class relies on the automatic generation and extensive flexibility
    due to all the optional parameters in the generation of the element.
    The basic generate_surface of the superclass generates a rectangle. Any other polygon
    should have that method overloaded.
    All colors have a format of a tuple of 4 values of the RGBA form.
    Attributes:
        params:     Dict containing all of the generation parameters. Can be used to generate again the image.
        image:      Surface of the sprite.
        rect:       pygame.Rect with the size and the position of the UiElement.
        pieces:     List of individual sprites that compose the big UiElement.    
        __event_id: Id of the event that is linked to this element. Triggered with a value when needed.
    Params dict attributes:
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
            user_event_id:  Id of the user defined event that this element will trigger on collision
            position:       Position of the sprite of this element.
            size:           Size of the sprit of this element.
            default_values: Set of values that the element will use. Could be a set of predefined ones, or a float.
            params:         Named parameters that will be passed in the creation of an UiElement subclass.
        Returns:
            A Button object (If set of predefined values) or a Slider object (If numerical value)
        Raise:
            AttributeError: In case of values mismatch. Need to be a set of values, or a numerical one.

        '''
        if type(default_values) is list or type(default_values) is tuple:
            return Button(user_event_id, position, size, tuple(default_values), **params)
        elif type(default_values) is int or type(default_values) is float:
            return Slider(user_event_id, position, size, float(default_values), **params)
        else:
            raise AttributeError("The provided set of default values does not follow any of the existing objects logic.")
    
    def __init__(self, user_event_id, position, size, **params):
        '''Constructor of the UiElement class.'''
        super().__init__()
        self.params =  UiElement.__default_config.copy()
        self.params.update(params)
        self.update_total   =   0
        self.update_counter =   1

        self.params["position"] = position
        self.params["size"] = size

        self.rect           =   pygame.Rect(position, size) 
        self.rect_original  =   self.rect.copy()
        self.pieces         =   pygame.sprite.OrderedUpdates()
        self.__event_id     =   user_event_id
        self.image          =   None                            #Will be assigned a good object in the next line
        self.image_original =   None
        self.generate_object()                                  #Generate the first sprite and the self.image attribute

    def generate_text(self, text, text_color, text_alignment, font, font_size):
        '''Generates a sprite-based text object following the input parameters.
        Args:
            text:           String object, is the text itself.
            text_color:     Color of the text.
            text_alignment: Decides which type of centering the text follows. 0-center, 1-left, 2-right.
            font:           Type of font that the text will have. Default value of pygame: None.
            font_size:      Size of the font (height in pixels).
        Returns:
            TextSprite object, rendered after reading the input parameters.
        Old code of method:
            #surface.blit(text_surf, (x_pos, y_pos))
            #return text_surf, pygame.Rect(x_pos, y_pos, text_surf.get_size())
        '''
        font = pygame.font.Font(font, font_size)
        text_surf = font.render(text, True, text_color)
        y_pos = (self.rect.height//2)-(text_surf.get_height()//2)
        #1 is left, 2 is right, 0 is centered
        x_pos = self.rect.width*0.02 if text_alignment is 1 else self.rect.width-text_surf.get_width() if text_alignment is 2 else (self.rect.width//2)-(text_surf.get_width()//2)
        return TextSprite(text_surf, (x_pos, y_pos))
    
    def generate_image(self):
        '''Generates the self.image surface, adding and drawing all the pieces that form part of the sprite.
        The rect attribute of the pieces after the first one are the relative position over the first sprite (piece).
        Args:       
            None
        Use:
            self.pieces    
        Returns:
            base_surf:  Complex surface containing all the individual sprites in self.pieces. 
        Raise:
            IndexError: Error if the self.pieces list is empty.
        '''
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
        '''Generates or regenerates the object, using the input rect, or the default self.rect.
        Empty the pieces list, and generate and add the pieces using the self.params values.
        This method can be overriden by subclasses, generating and adding different or more sprites.
        Lastly, the generate_image method is called again, and assigned to the self.image attribute.
        Can be used as a fancy and heavy resizer.
        Args:
            rect:           Rect containing the new size and position of the Element. Defaults to None and uses sef.rect.
            generate_image: Flag. If true, self.image is generated again using generate_image().
        Returns:
            Nothing.
        '''
        if rect is not None:        self.rect = rect
        self.params["position"] =   self.rect.topleft
        self.params["size"] =       self.rect.size
        self.pieces.empty()
        self.pieces.add(Rectangle(self.params['position'], self.params['size'], self.params['texture'], self.params['color'],\
                                self.params['border'], self.params['border_width'], self.params['border_color'],\
                                self.params['gradient'], self.params['start_gradient'], self.params['end_gradient'], self.params['gradient_type']))
        if generate_image:    
            self.image          = self.generate_image()  
            self.save_state()

    def save_state(self):
        self.image_original  =   self.image.copy()
        self.rect_original   =   self.rect.copy()        

    def restore(self):
        self.image  =   self.image_original.copy()
        self.rect   =   self.rect_original.copy()

    def send_event(self):
        '''Post the event associated with this element, along with the current value.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()'''
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
        super().__init__(user_event_id, element_position, element_size, **params)    
        self.overlay    =   pygame.Surface(self.rect.size)
        self.overlay.fill(WHITE)
        self.values     =   set_of_values
        self.index      =   0

    def update(self):
        '''Update method, will process and change image attributes to simulate animation when drawing
        Args, Returns:
            None, Nothing
        '''
        self.update_total  +=  self.update_counter
        if (self.update_total >= UPDATE_LIMIT or self.update_total < 0): self.update_counter = -self.update_counter
        self.set_overlay()

    def set_overlay(self):
        transparency_lvl    =   int((self.update_total/UPDATE_LIMIT) * MAX_TRANSPARENCY)
        self.overlay.set_alpha(transparency_lvl)
        self.image          =   self.image_original.copy() 
        self.image.blit(self.overlay, (0,0))

    def generate_object(self, rect=None, generate_image=True):
        super().generate_object(rect=rect, generate_image=False)
        
        #After adding things in the superclass initializing, we only want the attributes that we still dont have
        for key in Button.__default_config.keys(): 
            key = key.lower().replace(" ", "_")
            if not key in self.params:
                self.params[key] = Button.__default_config[key]

        fnt_size = Resizer.max_font_size(self.params['text'], self.rect.size, self.params['max_font_size'], self.params['font'])
        self.pieces.add(self.generate_text(self.params['text'], self.params['text_color'], self.params['text_centering'], self.params['font'], fnt_size)) 
        if generate_image:    
            self.image = self.generate_image() 
            self.save_state()

    #For the sake of writing short code
    def get_value(self):
        '''Returns the current value of the element.
        Returns:    Current value.
        '''
        return self.values[self.index]

    def hitbox_action(self, command, value=-1):
        ''' Decrement or increment the index of the predefined action, actively
        changing the current value of the value. After that, posts an event using send_event().
        Args:   
            command:    String. Decrement or increment the index if it contains 
                        the following substrings:
                            dec, min, left -> decrement index.
                            inc, add, right-> increment index.
            value:      Value is not used in the Button subclass
        Returns:
            Nothing.
        '''
        if 'dec' in command or 'min' in command or 'left' in command:   self.dec_index()
        elif 'inc' in command or 'add' in command or 'right' in command:  self.inc_index()
        self.send_event()

    def inc_index(self):
        '''Increment the index in a circular fassion (If over the len, goes back to the start, 0).'''
        self.index = self.index+1 if self.index < len(self.values) else 0

    def dec_index(self):
        '''Decrements the index in a circular fassion (If undex 0, goes back to the max index).'''
        self.index = self.index-1 if self.index > 0 else len(self.values)-1

class Slider (UiElement):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'text': 'default',
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
        self.value          =   default_value
        self.slider         =   None      #Due to the high access rate to this sprite, it will be on its own
        super().__init__(user_event_id, element_position, element_size, **params) 
        self.overlay        =   pygame.Surface(self.rect.size)
        self.overlay_color  =   [0, 0, 0]
        self.color_sum      =   UPDATE_LIMIT   

    def generate_object(self, rect=None, generate_image=True):
        super().generate_object(rect=rect, generate_image=False)
        
        for key in Slider.__default_config.keys():  #Can't do it like in the superclass
            key = key.lower().replace(" ", "_")
            if not key in self.params:              #If with the superclass update, we dont have this key (The user did not input it)
                self.params[key] = Slider.__default_config[key]

        fnt_size = Resizer.max_font_size(self.params['text'], self.rect.size, self.params['max_font_size'], self.params['font'])
        self.pieces.add(self.generate_text(self.params['text'], self.params['text_color'], self.params['text_centering'], self.params['font'], fnt_size//2))    
        self.slider =   self.generate_slider(self.params['slider_color'], self.params['slider_gradient'], self.params['slider_start_color'],\
                                            self.params['slider_end_color'], self.params['slider_border'], self.params['slider_border_color'],\
                                            self.params['slider_border_size'], self.params['slider_type'])
        if generate_image:    
            self.image = self.generate_image() 
            self.save_state()
            self.image.blit(self.slider.image, self.slider.rect)

    def generate_slider (self, slider_color, slider_gradient, start_color, end_color, slider_border, slider_border_color, slider_border_size, slider_type):
        '''Adds the slider to the surface parameter, and returns the slider surface for further purposes'''
        ratio = 3
        size = (self.rect.height, self.rect.height)
        #radius = self.rect.height//2
        if slider_type < 2:         #0, Circle
            slider = Circle((0,0), size, None, slider_color,\
                            slider_border, slider_border_size, slider_border_color,\
                            slider_gradient, start_color, end_color)
            if slider_type is 1:    #ellipse instead of circle, done by simply resizing the circle
                slider.rect.width //= ratio
                slider.image = pygame.transform.scale(slider.image, (slider.rect.width, slider.rect.height))
        else:                       #Rectangular one
            slider = Rectangle((0,0), (size[0]//ratio, size[1]), None, slider_color,\
                                slider_border, slider_border_size, slider_border_color,\
                                slider_gradient, start_color, end_color)
        
        slider.rect.x = self.value * (self.rect.width-slider.rect.width)     #To adjust the offset error due to transforming the surface.
        return slider

    #Position must be between 0 and 1
    #When we know in which form will the parameter be passed, we will implement this
    #Could be remade into a more generic method called set_piece_pos, that have an index as a parameter, to modify any sprite of the collection
    def set_slider_position(self, new_position):    #TODO test to check if the list works by reference
        if new_position > 0 and new_position < 1:   #This means its a porcentual ratio
            self.slider.rect.x =                int(self.rect.width*new_position)
        elif new_position > 1:
            self.slider.rect.x =                int(new_position)
            if self.slider.rect.x > self.rect.width:    self.slider.rect.x = self.rect.width-self.slider.rect.width
        else:
            self.slider.rect.x = 0

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = 0 if value < 0 else 1 if value > 1 else value

    def hitbox_action(self, command, value=-1):
        if 'dec' in command or 'min' in command or 'left' in command:       self.value -= 0.1 if self.value >= 0.1 else 1
        elif 'inc' in command or 'add' in command or 'right' in command:    self.value += 0.1 if self.value <= 0.9 else 0
        if value is not -1:
            if type(value) is tuple:            mouse_x = value[0]
            elif type(value) is pygame.Rect:    mouse_x = value.x
            else:                               raise TypeError("Type of value in slider method Hitbox_Action must be Rect or tuple.")
        pixels = mouse_x-self.rect.x         #Pixels into the bar, that the slider position has.
        value = pixels/self.rect.width
        if value != self.get_value:
            self.set_value(value) 
            self.set_slider_position(pixels)
            self.image = self.generate_image()          #Regenerate the image with the new slider position
            self.send_event()

    def restore(self):
        self.image  =   self.image_original.copy()
        self.image.blit(self.slider.image, self.slider.rect)
        self.rect   =   self.rect_original.copy()

    def update(self):
        '''Update method, will process and change image attributes to simulate animation when drawing
        Args, Returns:
            None, Nothing
        '''
        index = random.randint(0, len(self.overlay_color)-1)
        self.overlay_color[index] += self.color_sum

        for i in range (0, len(self.overlay_color)):
            if self.overlay_color[i] < 0:       self.overlay_color[i] = 0  
            elif self.overlay_color[i] > 255:   self.overlay_color[i] = 255

        if all(color >= 255 for color in self.overlay_color) or all(color <= 0 for color in self.overlay_color):    self.color_sum = -self.color_sum
        self.set_overlay()

    def set_overlay(self):
        topleft         =   (int(self.value*self.rect.width)-self.rect.height//6, 0)
        center          =   (int(self.value*self.rect.width), self.rect.height//2)
        overlay_rect    =   pygame.Rect(topleft, (self.rect.height//3, self.rect.height))
        if self.params['slider_type'] is 0:     pygame.draw.circle(self.image, self.overlay_color, center, self.rect.height//2)
        elif self.params['slider_type'] is 1:   pygame.draw.ellipse(self.image, self.overlay_color, overlay_rect)
        else:                                   pygame.draw.rect(self.image, self.overlay_color, overlay_rect)


if __name__ == "__main__":
    timeout = 20
    testsuite = PygameSuite(fps=144)
    #Create elements
    sli = UiElement.factory(pygame.USEREVENT+1, (10,10), (400, 100), (0.2))
    but = UiElement.factory(pygame.USEREVENT+2, (10, 210), (400, 100), (30, 40))
    sli2 = UiElement.factory(pygame.USEREVENT+3, (10, 410), (400, 100), (0.2), text="Slider")
    but2 = UiElement.factory(pygame.USEREVENT+4, (10, 610), (400, 100), ((30, 40)), text="Button")
    sli3 = UiElement.factory(pygame.USEREVENT+5, (510, 10), (400, 100), (0.2), text="SuperSlider", slider_type=0, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but3 = UiElement.factory(pygame.USEREVENT+6, (510, 210), (400, 100), ((30, 40)), text="SuperButton", start_gradient = GREEN, end_gradient=BLACK)
    sli4 = UiElement.factory(pygame.USEREVENT+7, (510, 410), (400, 100), (0.2), text="LongTextIsLongSoLongThatIsLongestEver", slider_type=2, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but4 = UiElement.factory(pygame.USEREVENT+8, (510, 610), (400, 100), ((30, 40)), text="LongTextIsLongSoLongThatIsLongestEver", start_gradient = GREEN, end_gradient=BLACK)
    testsuite.add_elements(sli, but, sli2, but2, sli3, but3, sli4, but4)
    testsuite.loop(seconds = timeout)