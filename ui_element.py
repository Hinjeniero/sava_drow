"""--------------------------------------------
ui_element module. Contains classes that work as elements for a graphical interface.
Every class inherits from Sprite, and adds interaction.
Have the following classes, inheriting represented by tabs:
    UIElement
        ↑ButtonAction
        ↑ButtonValue
        ↑Slider
        ↑InfoBoard
        ↑Dialog
--------------------------------------------"""

__all__ = ["UIElement", "TextSprite", "ButtonAction", "ButtonValue", "Slider", "InfoBoard", "Dialog"]
__version__ = '0.5'
__author__ = 'David Flaity Pardo'

#Python libraries
import pygame
import math
#Selfmade libraries
from polygons import Circle, Rectangle
from resizer import Resizer
from pygame_test import PygameSuite
from colors import WHITE, RED, DARKGRAY, LIGHTGRAY, GREEN, BLACK
from exceptions import  InvalidUIElementException, BadUIElementInitException, InvalidCommandValueException,\
                        TooManyElementsException, InvalidSliderException
from utility_box import UtilityBox
from sprite import Sprite, MultiSprite, TextSprite
from logger import Logger as LOG

class UIElement(MultiSprite):
    """Superclass UI_Element. Inherits from MultiSprite.
    It's an element of a graphical interface, with action and events associated.
    It links the graphic work of the Sprite method with interaction support.

    Attributes: 
        action (str):   Action/Command/Id of this action. It is used in join with event_id to do an action.
        event_id (int): Id of the event that is linked to this element and van be triggered. Sent with a payload when needed.
    """
    def __init__(self, id_, command, user_event_id, position, size, canvas_size, **params):
        """Constructor of the UiElement class.
        Args:
            id_ (str):  Identifier of the Sprite.
            command (str):  Command linked with the element. Will be sent in the payload of the event.
            user_event_id (int): Identifier of the event that will be sent.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            params (:dict:):    Dict of keywords and values as parameters to create the self.image attribute.
                                Variety going from fill_color and use_gradient to text_only.
        """
        super().__init__(id_, position, size, canvas_size, shape="rectangle", **params) 
        #Basic parameters on top of those inherited from Sprite
        self.action       = command
        self.event_id     = user_event_id
        self.generate()

    def get_id(self):
        """Returns:
            (str):  Action triggered by this element."""
        return self.action

    def get_command(self):
        """Returns: 
            (str):  Command sent when this element is triggered."""
        return self.get_id()

    def get_action(self):
        """Returns: 
            (str):  Action triggered by this element."""
        return self.get_id()

    def get_event(self):
        """Returns:
            (int):  Id of the event that will be sent upon interaction."""
        return self.event_id

    def get_event_id(self):
        """Returns:
            (int):  Id of the event that will be sent upon interaction."""
        return self.get_event()
    
    def hitbox_action(self):
        """Executes the associated action of the element. To be called when a click or key-press happens."""
        if self.active: self.send_event()

    def send_event(self):
        """Post (send) the event associated with this element, along with the command.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()"""
        my_event = pygame.event.Event(self.get_event_id(), command=self.get_action())
        pygame.event.post(my_event)

    def set_event(self, event_id):
        """Sets the event id of the element. This will be sent when a trigger happens."""
        self.__event_id = event_id

    @staticmethod
    def factory(id_, command, user_event_id, position, size, canvas_size, *elements, default_values=None, **params):
        """Method that returns a different subclass of UI_Element, taking into account the input arguments.
        If the devault_values it's an int/float, a Slider will be created. 
        If its a tuple of options, a ButtonValues with those predetermined options.
        If it's nothing, a ButtonAction with only the command and user_event_id.
        If there are *elements, an InfoBoard or Dialog is returned, if the first element is a TextSprite or a ButtonAction.
        Uses the Factory pattern.

        Args:
            id_ (str):            Identifier/command of the element
            user_event_id (int):  Id of the user defined event that this element will trigger.
            position (:tuple: int, int):    Position of the element. In pixels
            size (:tuple: int, int):        Size of the element. In pixels.
            default_values (:tuple: any...):    Set of values that the element will use. Can be a number or a tuple of values.
            *elements   (:obj: UI_Element): Subelements to be added, separated by commas.
            **params (:dict:):    Named parameters that will be passed in the creation of an UiElement subclass.
        Returns:
            (UI_Element subclass).  The UI_Element subclass that adapts better to hold the input arguments.
        Raises:
            AttributeError: In case of values mismatch. Need to be a set of values, or a numerical one.

        """
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
    """ButtonAction class. Inherits from UIElement.
    It's just an UIElement with text blitted on top. Have some interesting
    attributes to modify the way that text look.
    When clicked, will post an event with the a payload containing the command(.command).
    General class attributes:
        __default_config (:dict:): Contains parameters about the text looks and positioning.
            text (str): Text that will be drawn
            text_proportion (float):    Percentage that the text will occupy in the element
            text_alignment (str):   Alignment inside the element. Center, Left, Right.
    """
    __default_config = {'text': 'ButtonAction', 
                        'text_proportion': 0.5, 
                        'text_alignment': 'center'}

    def __init__(self, id_, command, user_event_id, position, size, canvas_size, **params):
        """ButtonAction constructor.
        Args:
            id_ (str):  Identifier of the Sprite.
            command (str):  Command linked with the element. Will be sent in the payload of the event.
            user_event_id (int): Identifier of the event that will be sent.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            params (:dict:):    Dict of keywords and values as parameters to create the self.image attribute.
                                Variety going from fill_color and use_gradient to text_only.
            """
        UtilityBox.join_dicts(self.params, ButtonAction.__default_config)
        super().__init__(id_, command, user_event_id, position, size, canvas_size, **params)  
        #No need to call generate here cuz THIS class generate is already called in the super()

    def generate(self):
        """Method that executes at the end of the constructor. Generates the base surface and
        adds the text with the params that we used in the init call.
        In short, build the MultiSprite adding the Sprites of ButtonAction."""
        text_size = [x//(1//self.params['text_proportion']) for x in self.rect.size]
        self.add_text_sprite(self.id+"_text", self.params['text'], text_size=text_size, alignment=self.params['text_alignment'])

class ButtonValue (UIElement):
    """ButtonAction class. Inherits from UIElement.
    UIElement with text blitted on top. Have some interesting attributes to modify the way that text look.
    Posseses a set of values with an active one, that the user can change when interacting with the element.
    When clicked, will post an event with a payload containing the command(.command) and the new set value.
    General class attributes:
        __default_config (:dict:): Contains parameters about the text looks and positioning.
            text (str): Text that will be drawn
            text_proportion (float):    Percentage that the text will occupy in the element
            text_alignment (str):   Alignment inside the element. Center, Left, Right.
            shows_value (boolean):  True if the current value is drawn in the MultiSprite.
    Attributes:
        values (:tuple: any...):    Set of values of this button. The active value can (and should) change  
                                    when needed/requested.
        current_index (int):        Index of the current active value.
    """
    __default_config = {'text': 'ButtonValue', 
                        'text_proportion': 0.33,
                        'text_alignment': 'center',
                        'shows_value': True}

    def __init__(self, id_, command, user_event_id, position, size, canvas_size, set_of_values, **params):
        """ButtonValue constructor.
        Args:
            id_ (str):  Identifier of the Sprite.
            command (str):  Command linked with the element. Will be sent in the payload of the event.
            user_event_id (int): Identifier of the event that will be sent.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            set_of_values (:tuple: any...): Set of values of the button. The active value can change.
            params (:dict:):    Dict of keywords and values as parameters to create the self.image attribute.
                                Variety going from fill_color and use_gradient to text_only.
            """
        UtilityBox.join_dicts(self.params, ButtonValue.__default_config)
        self.values             = set_of_values
        self.current_index      = 0  
        super().__init__(id_, command, user_event_id, position, size, canvas_size, **params) 

    def generate(self):
        """Method that executes at the end of the constructor. Generates the base surface and
        adds the text with the params that we used in the init call.
        Can blit the value text too, if shows_value is True.
        In short, build the MultiSprite adding the Sprites of ButtonValue."""
        text_size = [x//(1//self.params['text_proportion']) for x in self.rect.size]
        if self.params['shows_value']:
            self.add_text_sprite(self.id+"_text", self.params['text'], text_size=text_size, alignment='left')
            self.add_text_sprite(self.id+"_value", str(self.get_value()), text_size=text_size, alignment='right')
        else:
            self.add_text_sprite(self.id+"_text", self.params['text'], text_size=text_size, alignment=self.params['text_alignment'])

    #For the sake of writing short code
    def get_value(self):
        """Returns the current value of the element.
        Returns:    
            (any):  Current value."""
        return self.values[self.current_index]

    def hitbox_action(self, command, value):
        """Decrement or increment the index of the predefined action, actively
        changing the current value of the value. After that, posts an event using send_event().
        Args:   
            command (str):  Decrement or increment the index if it contains 
                            the following substrings:
                                dec, min, left, sec && mouse    -> decrement index.
                                inc, add, right, first && mouse -> increment index.
            value (int):    Value to be sent in the payload.
        """
        if self.active:
            if 'dec' in command or 'min' in command or 'left' in command or ("mouse" in command and "sec" in command):      self.dec_index()
            elif 'inc' in command or 'add' in command or 'right' in command or ("mouse" in command and "first" in command): self.inc_index()
            self.send_event()

    def update_value(self):
        """After a change in value, change the TextSprite and regenerates the image
        to show up the change in a graphic way. Only executes if shows_value is True."""
        if self.params['shows_value']:  
            self.sprites.sprites()[-1].set_text(str(self.get_value()))
            self.regenerate_image()

    def inc_index(self):
        """Increment the index in a circular way (If over the len, goes back to the start, 0).
        Also updates the value to change the Sprite if needed."""
        self.current_index = self.current_index+1 if self.current_index < len(self.values)-1 else 0
        self.update_value()

    def dec_index(self):
        """Decrements the index in a circular fassion (If index 0, goes back to the max index).
        Also updates the value to change the Sprite if needed."""
        self.current_index = self.current_index-1 if self.current_index > 0 else len(self.values)-1
        self.update_value()

    def send_event(self):
        """Post the event associated with this element, along with the current value and the command.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()"""
        my_event = pygame.event.Event(self.get_event_id(), command=self.get_action(), value=self.get_value())
        pygame.event.post(my_event)

class Slider (UIElement):   #TODO CHANGE SLIDER NAMEs TO DIAL
    """Slider class. Inherits from UIElement.
    UIElement with text blitted on top. Have some interesting attributes to modify the way that text look.
    Also has a dial blitted on top too. The slider can have numerous shapes.
    Has a current value that goes from 0 to 1, depending on the position of the slider dial itself.
    When clicked, will change the value and the dial if proceeds, and post an event with a payload containing 
    the command(.command) and the new set value (.value).
    General class attributes:
        __default_config (:dict:): Contains parameters about the text looks and positioning.
            text (str): Text that will be drawn
            text_proportion (float):    Percentage that the text will occupy in the element
            text_alignment (str):   Alignment inside the element. Center, Left, Right.
            shows_value (boolean):  True if the current value is drawn in the MultiSprite.
            slider_fill_color (:tuple: int, int, int):  RGB color of the surface background. 
                                                        Used if slider_use_gradient is False.
            slider_use_gradient (boolean):  True if we want a gradient instead of a solid color.
            slider_gradient (:tuple of 2 tuples: int, int, int):    Interval of RGB colors of the gradient.
            slider_border (boolean):    True if the slider dial generated has a border.
            slider_border_color (:tuple: int, int, int):    Color of the dial border. RGBA/RGB format.
            slider_border_width (int):  Size of the dial border in pixels.  
            slider_shape (str): Shape of the dial itself. Options are circular, elliptical, rectangular.
    Attributes:
        value (float):  Value of the slider. Depends on the current position of the dial.
    """
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
                        'slider_shape': 'rectangular'
    }

    def __init__(self, id_, command, user_event_id, position, size, canvas_size, default_value, **params):
        """Slider constructor.
        Args:
            id_ (str):  Identifier of the Sprite.
            command (str):  Command linked with the element. Will be sent in the payload of the event.
            user_event_id (int): Identifier of the event that will be sent.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            default_value (float):  Initial value that the slider has. Dial will be set accordingly.
            params (:dict:):    Dict of keywords and values as parameters to create the self.image attribute.
                                Variety going from fill_color and use_gradient to text_only.
            """
        UtilityBox.join_dicts(self.params, Slider.__default_config) 
        self.value = default_value 
        super().__init__(id_, command, user_event_id, position, size, canvas_size, **params)

    def generate(self):
        """Method that executes at the end of the constructor. Generates the base surface and
        adds the text with the params that we used in the init call.
        In short, build the MultiSprite adding the Sprites of Slider.
        Blits the value too if shows_value is True.
        In the end it generates the dial and blits it."""
        super().generate()
        _ = self.params  #For the sake of short code, params already have understandable names anyway
        text_size = [x//(1//_['text_proportion']) for x in self.rect.size]
        #Text sprite
        self.add_text_sprite(self.id+"_text", _['text'], text_size=text_size, alignment=_['text_alignment'])
        #Value sprite
        if _['shows_value']:
            self.add_text_sprite(self.id+"_text", _['text'], text_size=text_size, alignment='left')
            self.add_text_sprite(self.id+"_value", str(self.get_value()), text_size=text_size, alignment='right')
        else:
            self.add_text_sprite(self.id+"_text", _['text'], text_size=text_size, alignment=_['text_alignment'])
        #Slider sprite
        self.generate_dial(_['slider_fill_color'], _['slider_use_gradient'], _['slider_gradient'], _['slider_border'],\
                            _['slider_border_color'], _['slider_border_width'], _['slider_shape'])

    def generate_dial (self, fill_color, use_gradient, gradient, border, border_color, border_width, shape):
        """Generates a dial (following the input arguments), that will be added and blitted to the element.
        Args:
            fill_color (:tuple: int, int, int):  RGB color of the surface background. 
                                                        Used if slider_use_gradient is False.
            use_gradient (boolean): True if we want a gradient instead of a solid color.
            gradient (:tuple of 2 tuples: int, int, int):   Interval of RGB colors of the gradient.
            border (boolean):   True if the slider dial generated has a border.
            border_color (:tuple: int, int, int):   Color of the dial border. RGBA/RGB format.
            border_width (int): Size of the dial border in pixels.  
            shape (str):    Shape of the dial itself. Options are circular, elliptical, rectangular.
        Raises:
            InvalidSliderException: If the shape of the dial is not recognized. 
        """
        ratio = 3   #Ratio to resize square into rectangle and circle into ellipse
        slider_size = (self.rect.height, self.rect.height)
        slider_id   = self.id+"_dial"
        if 'circ' in shape or 'ellip' in shape: 
            slider = Circle(slider_id, (0, 0), slider_size, self.rect.size,\
                            fill_color=fill_color, fill_gradient=use_gradient, gradient=gradient,\
                            border=border, border_width=border_width, border_color=border_color)
            if 'ellip' in shape:
                slider.rect.width //= ratio
                slider.image = pygame.transform.smoothscale(slider.image, slider.rect.size)
        elif 'rect' in shape:
            slider = Rectangle( slider_id, (0, 0), (slider_size[0]//ratio, slider_size[1]), self.rect.size,\
                                fill_color=fill_color, fill_gradient=use_gradient, gradient=gradient,\
                                border=border, border_width=border_width, border_color=border_color)
        else:  
            raise InvalidSliderException('Slider of type '+str(shape)+' is not available')
        slider.rect.center = (int(self.get_value()*self.rect.width), self.rect.height//2)
        slider.set_position(slider.rect.topleft)
        self.add_sprite(slider)

    def set_slider_position(self, position):
        """Changes the dial position to the input parameter. Changes the graphics and the value accordingly.
        Distinguises between values between 0 and 1 (position in value), and values over 1 (position in pixels).
        Args:
            position (float||int): Position of the dial to set."""
        slider = self.get_sprite("dial")
        slider_position = int(self.rect.width*position) if (0 <= position <= 1) else int(position)                                      #Converting the slider position to pixels.
        slider_position = 0 if slider_position < 0 else self.rect.width if slider_position > self.rect.width else slider_position       #Checking if it's out of bounds 
        slider.rect.x = slider_position-(slider.rect.width//2)
        value_text = self.get_sprite("value")
        value_text.set_text(str(round(self.get_value(), 2)))
        self.regenerate_image()                                                                    #To compensate the graphical offset of managing center/top-left

    def get_value(self):
        """Returns:
            (float):    Current value of the slider"""
        return self.value

    def set_value(self, value):
        """Set a value as the current value of the slider. It also changes the slider position and graphics
        to show the change.
        Args:
            value (float):  Value to set. Must be between 0 and 1, will be parsed otherwise."""
        if      (self.value is 0 and value<0):  self.value = 1              #It goes all the way around from 0 to 1
        elif    (self.value is 1 and value>1):  self.value = 0              #It goes all the way around from 1 to 0
        else:   self.value = 0 if value < 0 else 1 if value > 1 else value  #The value it not yet absolute 1 or 0.
        self.set_slider_position(self.value)

    def hitbox_action(self, command, value):
        """Decrement or increment the value if a keyboard key is pressed, or set a value
        if its a mouse action. After that, posts an event with the new value.
        Args:   
            command (str):  Decrement or increment the index if it contains 
                            the following substrings:
                                dec, min, left  -> decrement index.
                                inc, add, right -> increment index.
                                mouse && click  -> Sets whatever value.
            value (int):    Value to be set.
        Raises:
            InvalidCommandValueException:   If the value input argument is not a tuple nor a rect.
        """
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
        """Post the event associated with this element, along with the current value.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()"""
        my_event = pygame.event.Event(self.get_event_id(), command=self.get_action(), value=self.get_value())
        pygame.event.post(my_event)

    def update(self):
        """Update method, will process and change image attributes to simulate animation when drawing.
        In slider does nothing. This way we don't do the useless work of super() update, useless in Slider."""
        pass 

    def draw_overlay(self, surface):
        """Draws an overlay of a random color each time over the dial. Simulates animation in this way.
        The overlay has the same shape as the dial.
        Args:
            surface (:obj: pygame.Surface): Surface in which to draw the dial overlay."""
        color   = UtilityBox.random_rgb_color()
        slider  = self.get_sprite('button')
        _       = self.params
        slider_rect = pygame.Rect(self.get_sprite_abs_position(slider), slider.rect.size)
        if 'circ' in _['slider_type']:      pygame.draw.circle(surface, color, slider_rect.center, slider.rect.height//2)
        elif 'ellip' in _['slider_type']:   pygame.draw.ellipse(surface, color, slider_rect)
        else:                               pygame.draw.rect(surface, color, slider_rect)

class InfoBoard (UIElement):
    """InfoBoard class. Inherits from UIElement.
    It's a grid of different sprites. It was made with the purpose of showing every bit of info
    that an object can give (a player in our case). Every Sprite has the same status here.
    In short, it's a background with a lot of Sprites/TextSprites blitted on top. 
    The grid can have a different ammount of columns and rows, it will adjust the Sprites to them. 
    General class attributes:
        __default_config (:dict:): Contains parameters about the text looks and positioning.
            rows (int): rows of the grid
            cols (int): columns of the grid
    Attributes:
        spaces (int)
        taken_spaces (int)
    """    
    __default_config = {'rows'  : 6,
                        'cols'  : 3 
    }

    def __init__(self, id_, user_event_id, position, size, canvas_size, *elements, **params):
        """InfoBoard constructor.
        Args:
            id_ (str):  Identifier of the Sprite.
            command (str):  Command linked with the element. Will be sent in the payload of the event.
            user_event_id (int): Identifier of the event that will be sent.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            *elements (:tuple: UI_Element, int):    Subelements to be added, separated by commas. Usually TextSprites.
                                                    The tuple follows the schema (UIElement, infoboard spaces taken).
            **params (:dict:):  Dict of keywords and values as parameters to create the self.image attribute.
                                Variety going from fill_color and use_gradient to text_only.
            """
        super().__init__(id_, "Infoboard_no_command_bro", user_event_id, position, size, canvas_size, **params)    
        UtilityBox.join_dicts(self.params, InfoBoard.__default_config)
        self.spaces         = self.params['rows']*self.params['cols']
        self.taken_spaces   = 0
        UtilityBox.join_dicts(self.params, InfoBoard.__default_config)
        self.add_and_adjust_sprites(*elements)
        self.use_overlay = False
    
    #Modify to also add elements when there are elements inside already
    def add_and_adjust_sprites(self, *elements, scale=0.95):
        """Adds all the UIElements to the Infoboard, adjusting and placing them.
        The number of spaces taken won't be modified if it's under the row number,
        but will be rounded up otherwise. This is due to the impossibility of showing
        a split sprite between columns.
        Args:
            *elements (:tuple: UI_Element, int):    Subelements to be added, separated by commas. Usually TextSprites.
                                                    The tuple follows the schema (UIElement, infoboard spaces taken).
            scale (float):  Percent of the spaces that the Sprite will take. Default is 0.95.
        Raises:
            InvalidUIElementException:  If one of the elements doesn't follow the tuple schema (uielement, spaces_taken)
        """
        UtilityBox.draw_grid(self.image, 6, 3)
        rows, columns       = self.params['rows'], self.params['cols']
        size_per_element    = (self.rect.width//columns, self.rect.height//rows)
        for element in elements:
            current_pos         = ((self.taken_spaces%columns)*size_per_element[0], (self.taken_spaces//columns)*size_per_element[1])
            spaces = element[1]
            if not isinstance(element, tuple) or not isinstance(element[1], float):  
                raise InvalidUIElementException("Elements of infoboard must follow the [(element, spaces_to_occupy), ...] scheme")
            if spaces > columns:    spaces = columns*math.ceil(spaces/columns) #Other type of occupied spaces are irreal
            #if spaces%columns = 0 FULL WIDTH
            height_ratio = columns if spaces>=columns else spaces%columns
            ratios              = (height_ratio, math.ceil(spaces/columns)) #Width, height
            element_size        = tuple([x*y for x,y in zip(size_per_element, ratios)])
            #element[0].image = pygame.transform.smoothscale(element[0].image, element_size) #This was just to test how it looks like
            Resizer.resize_same_aspect_ratio(element[0], tuple([x*scale for x in element_size]))
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