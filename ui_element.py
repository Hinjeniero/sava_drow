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
                        TooManyElementsException, InvalidSliderException, NotEnoughSpaceException
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
        params['shape'] = 'rectangle'
        super().__init__(id_, position, size, canvas_size, **params) 
        #Basic parameters on top of those inherited from Sprite
        self.action       = command
        self.event_id     = user_event_id

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
    
    def hitbox_action(self, command, value):
        """Executes the associated action of the element. To be called when a click or key-press happens."""
        if self.active and self.enabled: self.send_event()

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
            elif isinstance(elements[0], (TextSprite, pygame.sprite.Sprite)):
                return InfoBoard(id_, command, user_event_id, position, size, canvas_size, *elements, **params)
            else:    
                raise BadUIElementInitException("Can't create an object with those *elements of type "+str(type(elements[0])))
        if isinstance(default_values, (list, tuple)):
            return ButtonValue(id_, command, user_event_id, position, size, canvas_size, tuple(default_values), **params)
        elif isinstance(default_values, (int, float)):
            if size[0] > size[1]:
                return Slider(id_, command, user_event_id, position, size, canvas_size, float(default_values), **params)
            else:
                return VerticalSlider(id_, command, user_event_id, position, size, canvas_size, float(default_values), **params)
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
                        'text_proportion': 0.66, 
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
        super().__init__(id_, command, user_event_id, position, size, canvas_size, **params)
        ButtonAction.generate(self)
    
    @staticmethod
    def generate(self):
        """Method that executes at the end of the constructor. Generates the base surface and
        adds the text with the params that we used in the init call.
        In short, build the MultiSprite adding the Sprites of ButtonAction."""
        UtilityBox.join_dicts(self.params, ButtonAction.__default_config)
        text_size = [int(x*self.params['text_proportion']) for x in self.rect.size]
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
                        'text_proportion': 0.66,
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
        super().__init__(id_, command, user_event_id, position, size, canvas_size, **params) 
        self.values             = set_of_values
        self.current_index      = 0  
        ButtonValue.generate(self)

    def generate(self):
        """Method that executes at the end of the constructor. Generates the base surface and
        adds the text with the params that we used in the init call.
        Can blit the value text too, if shows_value is True.
        In short, build the MultiSprite adding the Sprites of ButtonValue."""
        UtilityBox.join_dicts(self.params, ButtonValue.__default_config)
        text_size = [int(x*self.params['text_proportion']) for x in self.rect.size]
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
        if self.active and self.enabled:
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

class Slider (UIElement):
    """Slider class. Inherits from UIElement.
    UIElement with text blitted on top. Have some interesting attributes to modify the way that text look.
    Also has a dial blitted on top too. The dial can have numerous shapes.
    Has a current value that goes from 0 to 1, depending on the position of the slider dial itself.
    When clicked, will change the value and the dial if proceeds, and post an event with a payload containing 
    the command(.command) and the new set value (.value).
    General class attributes:
        __default_config (:dict:): Contains parameters about the text looks and positioning.
            text (str): Text that will be drawn
            text_proportion (float):    Percentage that the text will occupy in the element
            text_alignment (str):   Alignment inside the element. Center, Left, Right.
            shows_value (boolean):  True if the current value is drawn in the MultiSprite.
            dial_fill_color (:tuple: int, int, int):  RGB color of the surface background. 
                                                        Used if dial_use_gradient is False.
            dial_use_gradient (boolean):  True if we want a gradient instead of a solid color.
            dial_gradient (:tuple of 2 tuples: int, int, int):    Interval of RGB colors of the gradient.
            dial_border (boolean):    True if the slider dial generated has a border.
            dial_border_color (:tuple: int, int, int):    Color of the dial border. RGBA/RGB format.
            dial_border_width (int):  Size of the dial border in pixels.  
            dial_shape (str): Shape of the dial itself. Options are circular, elliptical, rectangular.
    Attributes:
        value (float):  Value of the slider. Depends on the current position of the dial.
    """
    __default_config = {'text': 'Slider',
                        'text_proportion': 0.66,
                        'text_alignment': 'left',
                        'shows_value': True,
                        'dial_fill_color': GREEN,
                        'dial_use_gradient': True,
                        'dial_gradient': (LIGHTGRAY, DARKGRAY),
                        'dial_border': True, 
                        'dial_border_color': BLACK,
                        'dial_border_width': 2,
                        'dial_shape': 'rectangular'
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
        super().__init__(id_, command, user_event_id, position, size, canvas_size, **params)
        self.value = default_value 
        Slider.generate(self)

    @staticmethod
    def generate(self):
        """Method that executes at the end of the constructor. Generates the base surface and
        adds the text with the params that we used in the init call.
        In short, build the MultiSprite adding the Sprites of Slider.
        Blits the value too if shows_value is True.
        In the end it generates the dial and blits it.
        """
        UtilityBox.join_dicts(self.params, Slider.__default_config) 
        _ = self.params  #For the sake of short code, params has keys with already understandable names anyway
        text_size = [int(x*_['text_proportion']) for x in self.rect.size]
        #Text sprite
        self.add_text_sprite(self.id+"_text", _['text'], text_size=text_size, alignment=_['text_alignment'])
        #Value sprite
        if _['shows_value']:
            self.add_text_sprite(self.id+"_text", _['text'], text_size=text_size, alignment='left')
            self.add_text_sprite(self.id+"_value", str(self.get_value()), text_size=text_size, alignment='right')
        else:
            self.add_text_sprite(self.id+"_text", _['text'], text_size=text_size, alignment=_['text_alignment'])
        #Slider sprite
        self.generate_dial(_['dial_fill_color'], _['dial_use_gradient'], _['dial_gradient'], _['dial_border'],\
                            _['dial_border_color'], _['dial_border_width'], _['dial_shape'])

    def generate_dial (self, fill_color, use_gradient, gradient, border, border_color, border_width, shape):
        """Generates a dial (following the input arguments), that will be added and blitted to the element.
        Args:
            fill_color (:tuple: int, int, int):  RGB color of the surface background. 
                                                        Used if dial_use_gradient is False.
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
        dial_size = [min(self.rect.size), min(self.rect.size)]
        dial_id   = self.id+'_dial'
        if 'circ' in shape or 'ellip' in shape: 
            dial = Circle(dial_id, (0, 0), tuple(dial_size), self.rect.size,\
                            fill_color=fill_color, fill_gradient=use_gradient, gradient=gradient,\
                            border=border, border_width=border_width, border_color=border_color)
            if 'ellip' in shape:
                if self.rect.width < self.rect.height:
                    dial.rect.height //= ratio
                else:
                    dial.rect.width //= ratio
                dial.image = pygame.transform.smoothscale(dial.image, dial.rect.size)
        elif 'rect' in shape:
            if self.rect.width < self.rect.height:
                dial_size[1] //= ratio
            else:
                dial_size[0] //= ratio
            dial = Rectangle( dial_id, (0, 0), tuple(dial_size), self.rect.size,\
                                fill_color=fill_color, fill_gradient=use_gradient, gradient=gradient,\
                                border=border, border_width=border_width, border_color=border_color)
        else:  
            raise InvalidSliderException('Slider of type '+str(shape)+' is not available')
        if self.rect.width < self.rect.height:
            dial.rect.center = (self.rect.width//2, int(self.get_value()*self.rect.height))
        else:
            dial.rect.center = (int(self.get_value()*self.rect.width), self.rect.height//2)
        dial.set_position(dial.rect.topleft)
        self.add_sprite(dial)

    def set_dial_position(self, position):
        """Changes the dial position to the input parameter. Changes the graphics and the value accordingly.
        Distinguises between values between 0 and 1 (position in value), and values over 1 (position in pixels).
        Args:
            position (float||int): Position of the dial to set."""
        dial = self.get_sprite('dial')
        dial_position = int(self.rect.width*position) if (0 <= position <= 1) else int(position) #Converting the dial position to pixels.
        dial_position = 0 if dial_position < 0\
                        else self.rect.width if dial_position > self.rect.width \
                        else dial_position       #Checking if it's out of bounds 
        dial_x = dial_position-(dial.rect.width//2)
        dial.set_position((dial_x, dial.rect.y))
        value_text = self.get_sprite('value')
        value_text.set_text(str(round(self.get_value(), 2)))
        self.regenerate_image()  #To compensate the graphical offset of managing center/top-left

    def get_value(self):
        """Returns:
            (float):    Current value of the slider"""
        return round(self.value, 2)

    def set_value(self, value):
        """Set a value as the current value of the slider. It also changes the slider position and graphics
        to show the change.
        Args:
            value (float):  Value to set. Must be between 0 and 1, will be parsed otherwise."""
        if      (self.value == 0 and value<0):  self.value = 1              #It goes all the way around from 0 to 1
        elif    (self.value == 1 and value>1):  self.value = 0              #It goes all the way around from 1 to 0
        else:   self.value = 0 if value < 0 else 1 if value > 1 else value  #The value it not yet absolute 1 or 0.
        self.set_dial_position(self.value)

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
        if not self.enabled:    return  #Element is not enabled, byebye, no action from this one.
        if 'dec' in command or 'min' in command or 'left' in command:       self.set_value(self.get_value()-0.1)
        elif 'inc' in command or 'add' in command or 'right' in command:    self.set_value(self.get_value()+0.1)
        elif ('mouse' in command and ('click' in command or 'button' in command)):
            if isinstance(value, tuple):            mouse_x = value[0]
            elif isinstance(value, pygame.Rect):    mouse_x = value.x
            else:                                   raise InvalidCommandValueException("Value in slider hitbox can't be of type "+str(type(value)))

            pixels = mouse_x-self.rect.x        #Pixels into the bar, that the dial position has.
            value = pixels/self.rect.width      #Converting to float value between 0-1
            if value != self.get_value:         #If its a new value, we create another dial and value and blit it.
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

    def draw_overlay(self, surface, offset=None):
        """Draws an overlay of a random color each time over the dial. Simulates animation in this way.
        The overlay has the same shape as the dial.
        Args:
            surface (:obj: pygame.Surface): Surface in which to draw the dial overlay."""
        color   = UtilityBox.random_rgb_color()
        dial    = self.get_sprite('dial')
        _       = self.params
        dial_rect = pygame.Rect(self.get_sprite_abs_position(dial), dial.rect.size)
        if offset:
            dial_rect.topleft = tuple(off+pos for off, pos in zip(offset, dial_rect.topleft))
        if 'circ' in _['dial_shape']:       pygame.draw.circle(surface, color, dial_rect.center, dial.rect.height//2)
        elif 'ellip' in _['dial_shape']:    pygame.draw.ellipse(surface, color, dial_rect)
        else:                               pygame.draw.rect(surface, color, dial_rect)

class VerticalSlider(Slider):
    def __init__(self, id_, command, user_event_id, position, size, canvas_size, default_value, **params):
        """VerticalSlider constructor.
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
        super().__init__(id_, command, user_event_id, position, size, canvas_size, default_value, **params)

    def set_dial_position(self, position):
        """Changes the dial position to the input parameter. Changes the graphics and the value accordingly.
        Distinguises between values between 0 and 1 (position in value), and values over 1 (position in pixels).
        Args:
            position (float||int): Position of the dial to set."""
        dial = self.get_sprite('dial')
        dial_position = int(self.rect.height*position) if (0 <= position <= 1) else int(position) #Converting the dial position to pixels.
        dial_position = 0 if dial_position < 0\
                        else self.rect.height if dial_position > self.rect.height \
                        else dial_position       #Checking if it's out of bounds 
        dial_y = dial_position-(dial.rect.height//2)
        dial.set_position((dial.rect.x, dial_y))
        value_text = self.get_sprite('value')
        value_text.set_text(str(round(self.get_value(), 2)))
        self.regenerate_image()  #To compensate the graphical offset of managing center/top-left

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
        if not self.enabled:    return  #Element is not enabled, byebye, no action from this one.
        if 'dec' in command or 'min' in command or 'left' in command:       self.set_value(self.get_value()-0.1)
        elif 'inc' in command or 'add' in command or 'right' in command:    self.set_value(self.get_value()+0.1)
        elif ('mouse' in command and ('click' in command or 'button' in command)):
            if isinstance(value, tuple):            mouse_y = value[1]
            elif isinstance(value, pygame.Rect):    mouse_y = value.y
            else:                                   raise InvalidCommandValueException("Value in slider hitbox can't be of type "+str(type(value)))

            pixels = mouse_y-self.rect.y        #Pixels into the bar, that the dial position has.
            value = pixels/self.rect.height      #Converting to float value between 0-1
            if value != self.get_value:         #If its a new value, we create another dial and value and blit it.
                self.set_value(value)
        self.send_event()


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
                        'cols'  : 2 
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
        super().__init__(id_,  id_+'command', user_event_id, position, size, canvas_size, **params)    
        self.spaces         = 0     #Created in InfoBoard.generate
        self.taken_spaces   = 0
        self.element_size   = (0, 0)#Created in InfoBoard.generate
        InfoBoard.generate(self, *elements)

    @staticmethod
    def generate(self, *elements):
        """Raises:
            InvalidUIElementException:  If one of the elements doesn't follow the tuple schema (uielement, spaces_taken)"""
        self.clear()
        UtilityBox.join_dicts(self.params, InfoBoard.__default_config)
        self.spaces = self.params['rows']*self.params['cols']
        self.element_size = (int(self.rect.width//self.params['cols']), int(self.rect.height//self.params['rows'])) 
        self.use_overlay = False
        #TEST
        for element in elements:
            if not isinstance(element, tuple) or not isinstance(element[1], int):  
                raise InvalidUIElementException("Elements of infoboard must follow the [(element, spaces_to_occupy), ...] scheme.")
        #Test passed
        self.add_and_adjust_sprites(*elements)
        #UtilityBox.draw_grid(self.image, self.params['rows'], self.params['cols']) #TODO delete
    
    def add_text_element(self, id_, text, spaces, scale=0.95):
        if spaces > self.spaces-self.taken_spaces:
            raise NotEnoughSpaceException("There is not enough space in the infoboard to add that sprite")
        spaces = self.parse_element_spaces(spaces)
        size        = self.get_element_size(spaces, scale)
        text        = TextSprite(id_, (0, 0), size, self.rect.size, text, text_color = (0, 0, 0))
        position    = self.get_element_position(spaces, text.rect.size)
        text.set_position(position)
        self.add_sprite(text)
        self.taken_spaces += spaces
    
    def get_element_size(self, spaces, scale):
        cols = self.params['cols']
        width_element = spaces%cols*self.element_size[0] if spaces < cols else self.rect.width
        height_element = math.ceil(spaces/cols)*self.element_size[1]
        return (int(width_element*scale), int(height_element*scale))

    def get_element_position(self, spaces, size):
        cols = self.params['cols']
        if self.taken_spaces%cols + spaces > cols: #Modifies taken spaces to align again
            self.taken_spaces = int(math.ceil(self.taken_spaces/cols)*cols)
        x_axis = (self.taken_spaces%cols*self.element_size[0])   #Basic offset
        if spaces >= 3:
            x_axis += (self.rect.width-size[0])//2
        else:
            x_axis += ((spaces*self.element_size[0])-size[0])//2

        y_axis = ((self.taken_spaces//cols)*self.element_size[1])\
        + (((math.ceil(spaces/cols)*self.element_size[1])//2)-(size[1]//2))
        return (x_axis, y_axis)

    def set_canvas_size(self, res):
        #print("BEGORE "+str(len(self.sprites)))
        #for sprite in self.sprites:
            #print(sprite.rects_to_str())
        super().set_canvas_size(res)
        #print("AFTER "+str(len(self.sprites)))
        #for sprite in self.sprites:
            #print(sprite.rects_to_str())

    #Modify to also add elements when there are elements inside already
    def add_and_adjust_sprites(self, *elements, scale=0.95): #TODO convert to generator
        """Adds all the UIElements to the Infoboard, adjusting and placing them.
        The number of spaces taken won't be modified if it's under the row number,
        but will be rounded up otherwise. This is due to the impossibility of showing
        a split sprite between columns.
        Args:
            *elements (:tuple: UI_Element, int):    Subelements to be added, separated by commas. Usually TextSprites.
                                                    The tuple follows the schema (UIElement, infoboard spaces taken).
            scale (float):  Percent of the spaces that the Sprite will take. Default is 0.95.
        """
        rows, columns       = self.params['rows'], self.params['cols']
        size_per_element    = (self.rect.width//columns, self.rect.height//rows)
        for element in elements:
            #(x_axis, y_axis)
            current_pos         = ((self.taken_spaces%columns)*size_per_element[0],\
                                    (self.taken_spaces//columns)*size_per_element[1])
            spaces = self.parse_element_spaces(element[1])
            #if spaces%columns = 0 FULL WIDTH
            height_ratio = columns if spaces>=columns else spaces%columns
            ratios              = (height_ratio, math.ceil(spaces/columns)) #Width, height
            element_size        = tuple([x*y for x,y in zip(size_per_element, ratios)])
            #element[0].image = pygame.transform.smoothscale(element[0].image, element_size) #This was just to test how it looks like
            Resizer.resize(element[0], tuple([x*scale for x in element_size]))
            current_center      = [x+y//2 for x,y in zip(current_pos, element_size)]
            element[0].rect.center   = tuple(x for x in current_center)
            self.add_sprite(element[0])
            self.taken_spaces   += spaces 
            if self.taken_spaces > self.spaces: 
                raise TooManyElementsException("Too many elements in infoboard") 

    def parse_element_spaces(self, spaces):
        return self.params['cols']*math.ceil(spaces/self.params['cols']) if spaces > self.params['cols'] else spaces

    def get_cols(self):
        return self.params['cols']

    def get_rows(self):
        return self.params['rows']

    def clear(self):
        self.sprites.empty()
        
class Dialog (InfoBoard):
    __default_config = {'rows'  : 3,
                        'cols'  : 4 
    }

    def __init__(self, id_, user_event_id, element_size, canvas_size, *elements, **params):
        UtilityBox.join_dicts(params, Dialog.__default_config)
        super().__init__(id_, user_event_id, (0, 0), element_size, canvas_size, **params)
        Dialog.generate(self)

    @staticmethod
    def generate(self):
        self.clear()    #To delete the text fromn the button
        position = tuple(x//2 - y//2 for x, y in zip(self.resolution, self.rect.size))
        self.set_position(position)
        self.add_text_element(self.id+'_text', self.params['text'], (self.params['rows']*self.params['cols'])-self.params['cols'])

    def add_button(self, spaces, text, command, scale=1, **button_params):
        spaces = self.parse_element_spaces(spaces)
        size = self.get_element_size(spaces, scale)
        position = self.get_element_position(spaces, size)
        button = ButtonAction(self.id+"_button", command, self.event_id, position, size, self.rect.size, text=text, **button_params)
        self.add_sprite(button)