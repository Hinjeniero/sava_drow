import pygame, gradients, random, math
from polygons import *
from resizer import Resizer
from pygame_test import PygameSuite
from colors import *
from exceptions import InvalidUIElementException, BadUIElementInitException, InvalidCommandValueException,\
TooManyElementsException, InvalidSliderException
from utility_box import UtilityBox
from sprite import Sprite, MultiSprite, TextSprite
__all__ = ["TextSprite", "UIElement", "ButtonAction", "ButtonValue", "Slider", "InfoBoard", "Dialog"]
from logger import Logger as LOG

#Graphical element, automatic creation of a menu's elements
class UIElement(MultiSprite):
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
    def __init__(self, _id, command, user_event_id, position, size, canvas_size, **params):
        '''Constructor of the UiElement class.'''
        super().__init__(_id, position, size, canvas_size, shape="rectangle", **params) 
        #Basic parameters on top of those inherited from Sprite
        self.__action       = command
        self.__event_id     = user_event_id
        self.generate()

    def get_id(self):
        return self.__action
    def get_command(self):
        return self.get_id()
    def get_action(self):
        return self.get_id()
    def get_event(self):
        return self.__event_id
    def get_event_id(self):
        return self.get_event()

    def generate(self):
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
        A METHOD TO OVERLOAD, SUPER (UIELEMENT) DOES NOTHING HERE
        '''
        pass
    
    def hitbox_action(self, command, value=None):
        if self.active: self.send_event()

    def send_event(self):
        '''Post the event associated with this element, along with the current value.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()'''
        my_event = pygame.event.Event(self.get_event_id(), command=self.get_action(), value=None)
        pygame.event.post(my_event)

    def set_event(self, event_id):
        self.__event_id = event_id

    @staticmethod
    def factory(id_, command, user_event_id, position, size, canvas_size, default_values, *elements, **params):
        '''Method to decide what subclass to create according to the default values.
        If it's a number, a Slider with an associated value. 
        If its a list of shit, a button with those predetermined options.
        Factory pattern method.

        Args:
            id_:            yes.
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
        if any(x < 1 for x in size):    size        = tuple(x*y for x,y in zip(size, canvas_size))
        if any(y < 1 for y in position):position    = tuple(x*y for x,y in zip(position, canvas_size))
        if len(elements) > 0:
            if isinstance(elements[0], ButtonAction):   #Only interested in the first one, the following ones could vary
                return Dialog(id_, command, user_event_id, position, size, canvas_size, *elements, **params)
            elif isinstance(elements[0], TextSprite, pygame.sprite.Sprite):
                return InfoBoard(id_, command, user_event_id, position, size, canvas_size, *elements, **params)
            else:    raise BadUIElementInitException("Can't create an object with those *elements of type "+str(type(elements[0])))
        if isinstance(default_values, (list, tuple)):
            return ButtonValue(id_, command, user_event_id, position, size, canvas_size, tuple(default_values), **params)
        elif isinstance(default_values, (int, float)):
            return Slider(id_, command, user_event_id, position, size, canvas_size, float(default_values), **params)
        elif default_values is None:
            return ButtonAction(id_, command, user_event_id, position, size, canvas_size, **params)    
        else:
            raise BadUIElementInitException("Can't create an object with those default_values of type "+str(type(default_values)))

class ButtonAction(UIElement):
    __default_config = {'text': 'ButtonAction', 
                        'text_proportion': 0.5, 
                        'text_alignment': 'center'}
    def __init__(self, id_, command, user_event_id, position, size, canvas_size, **params):
        super().__init__(id_, command, user_event_id, position, size, canvas_size, **params)  
        #No need to call generate here cuz THIS class generate is already called in the super()

    def generate(self):
        super().generate()
        UtilityBox.join_dicts(self.params, ButtonAction.__default_config) #We need those default config params now to generate
        text_size = [x//(1//self.params['text_proportion']) for x in self.rect.size]
        self.add_text_sprite(self.id+"_text", self.params['text'], text_size=text_size, alignment=self.params['text_alignment'])

class ButtonValue (UIElement):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'text': 'ButtonValue', 
                        'text_proportion': 0.33,
                        'text_alignment': 'center',
                        'shows_value': True}
    def __init__(self, id_, command, user_event_id, position, size, canvas_size, set_of_values, **params):
        self.values             = set_of_values
        self.current_index      = 0  
        super().__init__(id_, command, user_event_id, position, size, canvas_size, **params) 

    def generate(self):
        super().generate()
        UtilityBox.join_dicts(self.params, ButtonValue.__default_config)
        text_size = [x//(1//self.params['text_proportion']) for x in self.rect.size]
        if self.params['shows_value']:
            self.add_text_sprite(self.id+"_text", self.params['text'], text_size=text_size, alignment='left')
            self.add_text_sprite(self.id+"_value", str(self.get_value()), text_size=text_size, alignment='right')
        else:
            self.add_text_sprite(self.id+"_text", self.params['text'], text_size=text_size, alignment=self.params['text_alignment'])

    #For the sake of writing short code
    def get_value(self):
        '''Returns the current value of the element.
        Returns:    Current value.
        '''
        return self.values[self.current_index]

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
        if self.active:
            if 'dec' in command or 'min' in command or 'left' in command or ("mouse" in command and "sec" in command):      self.dec_index()
            elif 'inc' in command or 'add' in command or 'right' in command or ("mouse" in command and "first" in command): self.inc_index()
            self.send_event()

    def update_value(self):
        if self.params['shows_value']:  self.sprites.sprites()[-1].set_text(str(self.get_value()))
        self.regenerate_image()

    def inc_index(self):
        '''Increment the index in a circular fassion (If over the len, goes back to the start, 0).'''
        self.current_index = self.current_index+1 if self.current_index < len(self.values)-1 else 0
        self.update_value()

    def dec_index(self):
        '''Decrements the index in a circular fassion (If undex 0, goes back to the max index).'''
        self.current_index = self.current_index-1 if self.current_index > 0 else len(self.values)-1
        self.update_value()

    def send_event(self):
        '''Post the event associated with this element, along with the current value.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()'''
        my_event = pygame.event.Event(self.get_event_id(), command=self.get_action(), value=self.get_value())
        pygame.event.post(my_event)

#CONTINUE HERE
class Slider (UIElement):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'text': 'Slider',
                        'text_proportion': 0.33,
                        'text_alignment': 'left',
                        'shows_value': True,
                        'slider_fill_color': GREEN,
                        'slider_use_gradient': True,
                        'slider_gradient': (LIGHTGRAY, DARKGRAY),
                        'slider_border': True, 
                        'slider_border_color': BLACK,
                        'slider_border_width': 2,
                        'slider_type': 'rectangular'
    }

    def __init__(self, id_, command, user_event_id, position, size, canvas_size, default_value, **params):
        self.value = default_value 
        super().__init__(id_, command, user_event_id, position, size, canvas_size, **params)

    def generate(self):
        super().generate()
        UtilityBox.join_dicts(self.params, Slider.__default_config) 
        _ = self.params  #For the sake of short code, params already have understandable names anyway
        text_size = [x//(1//_['text_proportion']) for x in self.rect.size]
        #Text sprite
        self.add_text_sprite(self.id+"_text", _['text'], text_size=text_size, alignment=_['text_alignment'])
        #Value sprite
        if self.params['shows_value']:
            self.add_text_sprite(self.id+"_text", self.params['text'], text_size=text_size, alignment='left')
            self.add_text_sprite(self.id+"_value", str(self.get_value()), text_size=text_size, alignment='right')
        else:
            self.add_text_sprite(self.id+"_text", self.params['text'], text_size=text_size, alignment=self.params['text_alignment'])
        #Slider sprite
        self.generate_slider(_['slider_fill_color'], _['slider_use_gradient'], _['slider_gradient'], _['slider_border'],\
                            _['slider_border_color'], _['slider_border_width'], _['slider_type'])

    def generate_slider (self, fill_color, use_gradient, gradient, border, border_color, border_width, slider_type):
        '''Adds the slider to the surface parameter, and returns the slider surface for further purposes'''
        ratio = 3   #Ratio to resize square into rectangle and circle into ellipse
        slider_size = (self.rect.height, self.rect.height)
        slider_id   = self.id+"button"
        if 'circ' in slider_type or 'ellip' in slider_type:  #Circ for circular or circle
            slider = Circle(slider_id, (0, 0), slider_size, self.get_canvas_size(),\
                            fill_color=fill_color, fill_gradient=use_gradient, gradient=gradient,\
                            border=border, border_width=border_width, border_color=border_color)
            if 'ellip' in slider_type:          #Ellip for elliptical or ellipse
                slider.rect.width //= ratio     #ellipse instead of circle, done by simply resizing the circle
                slider.image = pygame.transform.smoothscale(slider.image, slider.rect.size)  #Aaand using that modified rect

        elif 'rect' in slider_type:             #rect for rectangular or rectangle
            slider = Rectangle(slider_id, (0, 0), (slider_size[0]//ratio, slider_size[1]), self.get_canvas_size(),\
                            fill_color=fill_color, fill_gradient=use_gradient, gradient=gradient,\
                            border=border, border_width=border_width, border_color=border_color)

        else:   raise InvalidSliderException("Slider of type "+str(slider_type)+" is not available")
        
        slider.rect.center = (int(self.get_value()*self.rect.width), self.rect.height//2)   #Centering the slider in a start
        self.add_sprite(slider)

    def set_slider_position(self, position):
        slider = self.get_sprite("button")
        slider_position = int(self.rect.width*position) if (0 <= position <= 1) else int(position)                                      #Converting the slider position to pixels.
        slider_position = 0 if slider_position < 0 else self.rect.width if slider_position > self.rect.width else slider_position       #Checking if it's out of bounds 
        slider.rect.x = slider_position-(slider.rect.width//2)
        value_text = self.get_sprite("value")
        value_text.set_text(str(round(self.get_value(), 2)))
        self.regenerate_image()                                                                    #To compensate the graphical offset of managing center/top-left

    def get_value(self):
        return self.value

    def set_value(self, value):
        if      (self.value is 0 and value<0):  self.value = 1              #It goes all the way around from 0 to 1
        elif    (self.value is 1 and value>1):  self.value = 0              #It goes all the way around from 1 to 0
        else:   self.value = 0 if value < 0 else 1 if value > 1 else value  #The value it not yet absolute 1 or 0.
        self.set_slider_position(self.value)

    def hitbox_action(self, command, value=-1):
        if 'dec' in command or 'min' in command or 'left' in command:       self.set_value(self.get_value()-0.1)
        elif 'inc' in command or 'add' in command or 'right' in command:    self.set_value(self.get_value()+0.1)
        elif ('mouse' in command and ('click' in command or 'button' in command)):
            if isinstance(value, tuple):            mouse_x = value[0]
            elif isinstance(value, pygame.Rect):    mouse_x = value.x
            else:                                   raise InvalidCommandValueException("Value in slider hitbox can't be of type "+str(type(value)))

            pixels = mouse_x-self.rect.x        #Pixels into the bar, that the slider position has.
            value = pixels/self.rect.width      #Converting to float value between 0-1
            if value != self.get_value:         #If its a new value, we create another slider and value and blit it.
                self.set_value(value)
        self.send_event()

    def send_event(self):
        '''Post the event associated with this element, along with the current value.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()'''
        my_event = pygame.event.Event(self.get_event_id(), command=self.get_action(), value=self.get_value())
        pygame.event.post(my_event)

    def update(self):
        '''Update method, will process and change image attributes to simulate animation when drawing
        Args, Returns:
            None, Nothing
        '''
        pass #This way we don't do the useless work of super() update (useless in this specific subclass)

    def draw_overlay(self, surface):
        color   = UtilityBox.random_rgb_color()
        slider  = self.get_sprite('button')
        _       = self.params
        slider_rect = pygame.Rect(self.get_sprite_abs_position(slider), slider.rect.size)
        if 'circ' in _['slider_type']:      pygame.draw.circle(surface, color, slider_rect.center, slider.rect.height//2)
        elif 'ellip' in _['slider_type']:   pygame.draw.ellipse(surface, color, slider_rect)
        else:                               pygame.draw.rect(surface, color, slider_rect)

class InfoBoard (UIElement):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'rows'  : 6,
                        'cols'  : 3 
    }
    def __init__(self, id_, user_event_id, position, size, canvas_size, *elements, **params):
        super().__init__(id_, "Infoboard_no_command_bro", user_event_id, position, size, canvas_size, **params)    
        UtilityBox.join_dicts(self.params, InfoBoard.__default_config)
        self.spaces         = self.params['rows']*self.params['cols']
        self.taken_spaces   = 0
        UtilityBox.join_dicts(self.params, InfoBoard.__default_config)
        self.add_and_adjust_sprites(*elements)
        self.use_overlay = False
    
    #Modify to also add elements when there are elements inside already
    def add_and_adjust_sprites(self, *elements, element_scale=0.95):
        UtilityBox.draw_grid(self.image, 6, 3)
        rows, columns       = self.params['rows'], self.params['cols']
        size_per_element    = (self.rect.width//columns, self.rect.height//rows)
        for element in elements:
            current_pos         = ((self.taken_spaces%columns)*size_per_element[0], (self.taken_spaces//columns)*size_per_element[1])
            spaces = element[1]
            if not isinstance(element, tuple):  raise BadUIElementInitException("Elements of infoboard must follow the [(element, spaces_to_occupy), ...] scheme")
            if spaces > columns:    spaces = columns*math.ceil(spaces/columns) #Other type of occupied spaces are irreal
            #if spaces%columns = 0 FULL WIDTH
            height_ratio = columns if spaces>=columns else spaces%columns
            ratios              = (height_ratio, math.ceil(spaces/columns)) #Width, height
            element_size        = tuple([x*y for x,y in zip(size_per_element, ratios)])
            #element[0].image = pygame.transform.smoothscale(element[0].image, element_size) #This was just to test how it looks like
            Resizer.resize_same_aspect_ratio(element[0], tuple([x*element_scale for x in element_size]))
            current_center      = [x+y//2 for x,y in zip(current_pos, element_size)]
            element[0].rect.center   = tuple(x for x in current_center)
            self.add_sprite(element[0])
            self.taken_spaces   += spaces 
            if self.taken_spaces > self.spaces: raise TooManyElementsException("Too many elements in infoboard") 

class Dialog (UIElement):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'text'          : 'exit_dialog',
                        'font'          : None,
                        'max_font_size' : 50,
                        'font_size'     : 0,
                        'text_color'    : WHITE,
                        'auto_center'   : True,
                        'rows'          : 1,
                        'cols'          : 1
    }

    def __init__(self, id_, user_event_id, element_position, element_size, canvas_size, *buttons, **params):
        pass
        '''self.buttons            = pygame.sprite.Group()
        for button in buttons:  self.buttons.add(button)
        super().__init__(id_, user_event_id, element_position, element_size, canvas_size, **params)

    def generate(self, rect=None, generate_image=True):
        super().generate(rect=rect, generate_image=False)
        UtilityBox.check_missing_keys_in_dict(self.params, Dialog.__default_config)
        #self.adjust_buttons()
        self.pieces.add(UIElement.close_button(self.get_id()+"_close_exit_button", self.get_event_id(), self.rect))
        self.params['font_size'] = Resizer.max_font_size(self.params['text'], self.rect.size, self.params['max_font_size'], self.params['font'])//2
        self.add_text(self.params['text'], self.params['font'], self.rect, [x//1.5 for x in self.rect.size], self.params['max_font_size'], self.params['text_color'], 0)    
        if self.params['auto_center']:  self.rect.topleft = [(x//2-y//2) for x, y in zip(self.get_canvas_size(), self.rect.size)]
        if generate_image:    
            self.image = self.generate_image() 
            self.save_state()   

    def set_visible(self, visible):
        self.image.set_alpha(0) if visible is False else self.image.set_alpha(255)

    def update(self):
        pass

    def adjust_buttons(self, button_percentage=0.50):
        if len(self.buttons.sprites()) > self.params['rows']*self.params['cols']:  
            self.params['rows'] = math.ceil(len(self.buttons.sprites())//self.params['cols'])
        size    = (self.rect.width//self.params['cols'], (self.rect.height*button_percentage)//self.params['rows'])     #Size per element
        pos     = [0, 0]
        buttons = self.buttons.sprites()
        for i in range(0, self.params['rows']):
            pos[0]  = 0
            for j in range(0, self.params['cols']):
                index = i*self.params['cols']+j
                buttons[index].generate(pygame.Rect(size, pos), True)
                pos[0] += size[0]
            pos[1]  += size[1]'''