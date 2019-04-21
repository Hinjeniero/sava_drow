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

__all__ = ["UIElement", "TextSprite", "ButtonAction", "ButtonValue", "Slider", "InfoBoard", "Dialog", "TextBox", "ScrollingText"]
__version__ = '0.9'
__author__ = 'David Flaity Pardo'

#Python libraries
import pygame
import math
from wrapt import synchronized
#Selfmade libraries
from obj.polygons import Circle, Rectangle
from obj.sprite import Sprite, MultiSprite, TextSprite
from obj.utilities.resizer import Resizer
from obj.utilities.colors import WHITE, RED, DARKGRAY, LIGHTGRAY, GREEN, BLACK
from obj.utilities.exceptions import    InvalidUIElementException, BadUIElementInitException, InvalidCommandValueException,\
                                        TooManyElementsException, InvalidSliderException, NotEnoughSpaceException
from obj.utilities.utility_box import UtilityBox
from obj.utilities.decorators import run_async
from obj.utilities.logger import Logger as LOG

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
        self.action     = command
        self.event_id   = user_event_id
        self.has_input  = False

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
        if self.active and self.enabled:
            if self.hover_dialog and 'center' in command and 'mouse' in command:    #MouseWheel click
                if self.dialog_active:          self.hide_help_dialog()
                elif not self.dialog_active:    self.show_help_dialog()
                return
            self.send_event()

    def send_event(self):
        """Post (send) the event associated with this element, along with the command.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()"""
        my_event = pygame.event.Event(self.get_event_id(), command=self.get_action())
        pygame.event.post(my_event)

    def set_event(self, event_id):
        """Sets the event id of the element. This will be sent when a trigger happens."""
        self.__event_id = event_id

    def get_collisions(self, mouse_sprite, list_sprites=None, first_only=False):
        """list sprites in case a subclass want to check another implemented list"""
        list_to_check = list_sprites if list_sprites else self.sprites
        old_mouse_position = mouse_sprite.rect.topleft
        mouse_sprite.rect.topleft = tuple(x-y for x, y in zip(old_mouse_position, self.rect.topleft))
        if first_only:
            collisions = pygame.sprite.spritecollideany(mouse_sprite, list_to_check)
        else:
            collisions = pygame.sprite.spritecollide(mouse_sprite, list_to_check, False)
        mouse_sprite.rect.topleft = old_mouse_position
        return collisions

    @staticmethod
    def factory(id_, command, user_event_id, position, size, canvas_size, *elements, default_values=None, **params):
        """Method that returns a different subclass of UI_Element, taking into account the input arguments.
        The following inputs will return the following objects:
            -If the size is None or has the exact same size as the resolution, a SCROLLINGTEXT will be created.
            If the command is None/False/0, 
                -if there are input elements, an INFOBOARD will be created.
                -else, a DIALOG will be created.
            If there are default_values,
                if default_values is an int/float,
                    -if the width>height, a SLIDER will be created.
                    -else, a VERTICALSLIDER will be created. 
                -elif its a tuple of options, a BUTTONVALUE will be created.
            Elif there are not default_values,
                -if there is a 'text' key in params with actual text, a BUTTONACTION will be created
                -else a TEXTBOX will be created.
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
        if not size or size == 1 or size == canvas_size:
            return ScrollingText(id_, user_event_id, position, canvas_size, *elements, **params)
        if any(0 <= x <= 1 for x in size):      size    = tuple(x*y for x,y in zip(size, canvas_size))
        if any(0 <= x <= 1 for x in position):  position= tuple(x*y for x,y in zip(position, canvas_size))
        if not command:
            if len(elements) > 0:
                if isinstance(elements[0], tuple):
                    return InfoBoard(id_, user_event_id, position, size, canvas_size, *elements, **params)
            else:
                return Dialog(id_, user_event_id, size, canvas_size, **params)
        if default_values or default_values == 0:
            if isinstance(default_values, (list, tuple)):
                return ButtonValue(id_, command, user_event_id, position, size, canvas_size, tuple(default_values), **params)
            elif isinstance(default_values, (int, float)):
                if size[0] > size[1]:
                    return Slider(id_, command, user_event_id, position, size, canvas_size, float(default_values), **params)
                else:
                    return VerticalSlider(id_, command, user_event_id, position, size, canvas_size, float(default_values), **params)
        else:
            try:
                if params['text'] != '':
                    return ButtonAction(id_, command, user_event_id, position, size, canvas_size, **params)
            except KeyError:
                pass
            return TextBox(id_, command, user_event_id, position, size, canvas_size, **params)
        raise BadUIElementInitException("Can't create an object with those input parameters")

    @staticmethod
    @run_async
    def threaded_factory(result, id_, command, user_event_id, position, size, canvas_size, *elements, default_values=None, **params):
        element = UIElement.factory(id_, command, user_event_id, position, size, canvas_size, *elements, default_values=default_values, **params)
        try:
            result.append(element)
        except AttributeError:
            try:
                result.add(element)
            except AttributeError:
                result = element

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
        try:
            if self.params['only_text']: return
        except KeyError:
            pass
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

    @staticmethod
    def generate(self):
        """Method that executes at the end of the constructor. Generates the base surface and
        adds the text with the params that we used in the init call.
        Can blit the value text too, if shows_value is True.
        In short, build the MultiSprite adding the Sprites of ButtonValue."""
        UtilityBox.join_dicts(self.params, ButtonValue.__default_config)
        text_size = [int(x*self.params['text_proportion']) for x in self.rect.size]
        try:
            if self.params['only_text']:
                try:
                    if self.params['shows_value']:
                        self.add_text_sprite(self.id+"_value", str(self.get_value()), text_size=tuple(x//2 for x in text_size), alignment='right')
                except KeyError:
                    pass
                return
        except KeyError:
            pass
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
            super().hitbox_action(command, value)

    def update_value(self):
        """After a change in value, change the TextSprite and regenerates the image
        to show up the change in a graphic way. Only executes if shows_value is True."""
        if self.params['shows_value']:  
            if self.hover_dialog:
                self.sprites.sprites()[-2].set_text(str(self.get_value()))
            else:
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
                        'bar_border': 6,
                        'bar_texture': None,
                        'dial_texture': None,
                        'dial_fill_color': GREEN,
                        'dial_use_gradient': True,
                        'dial_gradient': (LIGHTGRAY, DARKGRAY),
                        'dial_border': True, 
                        'dial_border_color': BLACK,
                        'dial_border_width': 2,
                        'dial_shape': 'rectangular',
                        'loop'      : True
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
        #Bar sprite
        if _['bar_texture']:
            self.add_sprite(self.generate_bar(_['bar_texture'], _['bar_border']))
        #Text and Value sprite
        if _['shows_value']:
            self.add_text_sprite(self.id+"_text", _['text'], text_size=text_size, alignment='left')
            self.add_text_sprite(self.id+"_value", str(self.get_value()), text_size=text_size, alignment='right')
        else:
            self.add_text_sprite(self.id+"_text", _['text'], text_size=text_size, alignment=_['text_alignment'])
        #Slider sprite
        dial = self.generate_dial(_['dial_texture'], _['dial_fill_color'], _['dial_use_gradient'], _['dial_gradient'], _['dial_border'],\
                                _['dial_border_color'], _['dial_border_width'], _['dial_shape'])
        self.add_sprite(dial)
        self.overlay = self.generate_overlay(dial.image, WHITE)

    def regenerate_image(self):
        self.sprites.remove(self.get_sprite('dial'))    #Have to do this in this way because ellipses.
        #Regenerating from here
        super().regenerate_image()
        #Adding again what is needed for a slider
        _ = self.params
        if _['bar_texture']:
            bar = self.get_sprite('bar')
            bar = self.generate_bar(_['bar_texture'], _['bar_border'])    #Swapping the bar
        dial = self.generate_dial(_['dial_texture'], _['dial_fill_color'], _['dial_use_gradient'], _['dial_gradient'], _['dial_border'],\
                        _['dial_border_color'], _['dial_border_width'], _['dial_shape'])
        self.add_sprite(dial)
        self.overlay = self.generate_overlay(dial.image, WHITE)
        if not self.enabled:
            self.overlay.set_alpha(200)
        #self.set_dial_position(self.value)
        
    def generate_bar(self, texture, border, resize_mode='fit', resize_smooth=True, keep_aspect_ratio=False):
        size = tuple(x-border for x in self.rect.size)
        bar = Sprite('bar', (border//2, border//2), size, self.rect.size, texture=texture, resize_mode=resize_mode,\
                    resize_smooth=resize_smooth, keep_aspect_ratio=keep_aspect_ratio)
        bar.image = bar.image.subsurface(pygame.Rect((0, 0), (int(bar.rect.width*self.value), bar.rect.height)))
        return bar

    def generate_dial (self, texture, fill_color, use_gradient, gradient, border, border_color, border_width, shape):
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
        if texture:
            dial = Sprite(dial_id, (border//2, border//2), dial_size, self.rect.size, texture=texture)
        elif 'circ' in shape or 'ellip' in shape: 
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
        return dial
    
    def draw(self, surface, offset=None):
        super().draw(surface, offset=offset)
        if (self.use_overlay and self.active) or not self.enabled:
            self.draw_overlay(surface, offset=offset)   #To draw it on top, otherwise is drawn below the dial and all

    def draw_overlay(self, surface, offset=None):
        """Draws the overlay over a surface.
        Args:
            surface (:obj: pygame.Surface): Surface to draw the Sprite. It's usually the display
        """
        dial = self.get_sprite('dial')
        position = dial.abs_position if dial.abs_position else dial.rect.topleft
        if offset:
            surface.blit(self.overlay, tuple(off+pos for off, pos in zip(offset, position)))
        else:
            surface.blit(self.overlay, position)
        if self.enabled:
            self.animation_frame()

    @run_async
    def set_dial_position(self, position):
        """Changes the dial position to the input parameter. Changes the graphics and the value accordingly.
        Distinguises between values between 0 and 1 (position in value), and values over 1 (position in pixels).
        Args:
            position (float||int): Position of the dial to set."""
        bar = self.get_sprite('bar')
        if bar:
            try:
                bar.image = bar.image.get_parent().subsurface(pygame.Rect((0, 0), (int(bar.rect.width*self.value), bar.rect.height)))
            except AttributeError:
                bar.image = bar.image.subsurface(pygame.Rect((0, 0), (int(bar.rect.width*self.value), bar.rect.height)))
        dial = self.get_sprite('dial')
        dial_position = int(self.rect.width*position) if (0 <= position <= 1) else int(position) #Converting the dial position to pixels.
        dial_position = 0 if dial_position < 0\
                        else self.rect.width if dial_position > self.rect.width \
                        else dial_position       #Checking if it's out of bounds 
        dial_x = dial_position-(dial.rect.width//2)
        dial.set_position((dial_x, dial.rect.y))
        if self.params['shows_value']:
            self.get_sprite('value').set_text(str(round(self.get_value(), 2)))

    def get_value(self):
        """Returns:
            (float):    Current value of the slider"""
        return round(self.value, 2)

    def set_value(self, value):
        """Set a value as the current value of the slider. It also changes the slider position and graphics
        to show the change.
        Args:
            value (float):  Value to set. Must be between 0 and 1, will be parsed otherwise."""
        if value != self.get_value():
            if      (self.value == 0 and value<0):  self.value = 1 if self.params['loop'] else 0
            elif    (self.value == 1 and value>1):  self.value = 0 if self.params['loop'] else 1
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

class VerticalSlider(Slider):
    def __init__(self, id_, command, user_event_id, position, size, canvas_size, default_value=0.0, **params):
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
        if self.params['shows_value']:
            value_text = self.get_sprite('value')
            value_text.set_text(str(round(self.get_value(), 2)))
            self.regenerate_image()

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
    def generate(self, *elements, draw_grid=False):
        """Clears the useless params filled in superclasses, and generates the useful ones that are still empty.
        Called at the end of the constructor. Also adds the input elements to the infoboard.
        Raises:
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
        if draw_grid:   #Testing purposes
            UtilityBox.draw_grid(self.image, self.params['rows'], self.params['cols'])
    
    def add_text_element(self, id_, text, spaces, color=(0, 0, 0), scale=0.95):
        """Creates and adds a text sprite with a size matching the number of occupied spaces
        defined on the input.
        The position and size are determined with helping methods. 
        Args:
            id_ (str):  Id of the text sprite that will be created.
            text (str): Text to render and blit to the infoboard.
            spaces (int):  Number of spaces occupied by the text. Will determine the size and the position to some extent.
            scale (float, default=0.95):    Proportional size of the text (Against the full size (looking purely at spaces).
        Raises:
            NotEnoughSpaceException:    If the number of spaces of the element plus the already taken spaces is more than the 
                                        total spaces of the infoboard."""
        if spaces > self.spaces-self.taken_spaces:
            raise NotEnoughSpaceException("There is not enough space in the infoboard to add that sprite")
        spaces = self.parse_element_spaces(spaces)
        size        = self.get_element_size(spaces, scale)
        text        = TextSprite(id_, (0, 0), size, self.rect.size, text, text_color=color)
        position    = self.get_element_position(spaces, text.rect.size)
        self.add_sprite(text)
        text.set_position(position)
        self.taken_spaces += spaces
    
    def get_element_size(self, spaces, scale):
        """Calculates the size of the input spaces. The scale is the proportion in a real number.
        Args:
            spaces (int):   The spaces that the size should match.
            scale (float):  The proportion of the size against the full/max size in a real interval (0->1)
                            (Full proportion->1).
        Returns:
            (tuple->(int, int)):    The size (in pixels) of the element that takes the input spaces."""
        cols = self.params['cols']
        width_element = spaces%cols*self.element_size[0] if spaces < cols else self.rect.width
        height_element = math.ceil(spaces/cols)*self.element_size[1]
        return (int(width_element*scale), int(height_element*scale))

    def get_element_position(self, spaces, size):
        """Calculates the position taking as a basis the input spaces. Takes into account the 
        already taken spaces, and the possible offset in the row in the case of odd spaces.
        Args:
            spaces (int):   The spaces that will determine the topleft position.
            size (int): The size of the element.
        Returns:
            (tuple->(int, int)):    The position (in pixels) of the element inside the infoboard."""
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
        """Gets the input spaces, and check if it is essential to add to them to maintain a decent layout on
        the infoboard. Basically, if it's over a row spaces, but with an odd divission, it makes the math.ceil of
        the value to occupy a row more.
        Args:
            spaces (int):   Spaces to parse.
        Returns:
            The parsed number of spaces, ready to be used for whatever."""
        return self.params['cols']*math.ceil(spaces/self.params['cols']) if spaces > self.params['cols'] else spaces

    def get_cols(self):
        """Returns:
            (int):  Number of columns that this infoboard possesses."""
        return self.params['cols']

    def get_rows(self):
        """Returns:
            (int):  Number of columns that this infoboard possesses."""
        return self.params['rows']

    def set_rows(self, rows):
        rows = 1 if rows < 1 else rows
        self.params['rows'] = rows
        self.spaces = self.params['rows']*self.params['cols']
        self.element_size = (int(self.rect.width//self.params['cols']), int(self.rect.height//self.params['rows']))

    def set_cols(self, cols):
        cols = 1 if cols < 1 else cols
        self.params['cols'] = cols
        self.spaces = self.params['rows']*self.params['cols']
        self.element_size = (int(self.rect.width//self.params['cols']), int(self.rect.height//self.params['rows']))

    def clear(self):
        """Deletes all the sprites of the infoboard. Useful when deleting the texts."""
        self.sprites.empty()
        self.taken_spaces = 0
        #self.regenerate_image()
        
class Dialog (InfoBoard):
    """Dialog class. Inherits from InfoBoard.
    It's a grid of different sprites. A confirmation/dialog window. The normal way to use it is 
    with one or two texts, and some buttons, normally to confirm or decline. 
    The grid can have a different ammount of columns and rows, it will adjust the Sprites to them. 
    General class attributes:
        __default_config (:dict:): Contains parameters about the text looks and positioning.
            rows (int): rows of the grid
            cols (int): columns of the grid
    Attributes:
        buttons (:obj: pygame.sprite.OrderedUpdates):   All the buttons that the dialog posseses.
    """   
    __default_config = {'rows'  : 3,
                        'cols'  : 4,
                        'text_color': WHITE
    }

    def __init__(self, id_, user_event_id, element_size, canvas_size, **params):
        """Dialog constructor.
        Args:
            id_ (str):  Identifier of the Sprite.
            user_event_id (int): Identifier of the event that will be sent.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            element_size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            *elements (:tuple: UI_Element, int):    Subelements to be added, separated by commas. Usually TextSprites.
                                                    The tuple follows the schema (UIElement, infoboard spaces taken).
            **params (:dict:):  Dict of keywords and values as parameters to create the self.image attribute.
                                Variety going from fill_color and use_gradient to text_only.
            """
        UtilityBox.join_dicts(params, Dialog.__default_config)
        super().__init__(id_, user_event_id, (0, 0), element_size, canvas_size, **params)
        self.elements = pygame.sprite.OrderedUpdates()  #Elements that can collide with the mouse and do actions
        Dialog.generate(self)

    @staticmethod
    def generate(self):
        """Clear the previous texts from the dialog (The ones created in super classes), and set the position
        to the middle of the screen."""
        self.clear()    #To delete the text fromn the button
        position = tuple(x//2 - y//2 for x, y in zip(self.resolution, self.rect.size))
        self.set_position(position)
        try:
            if self.params['text'] and self.params['text'] != '':
                self.add_text_element(self.id+'_text', self.params['text'], self.params['cols'], color=self.params['text_color'])
        except KeyError:
            pass

    def set_active(self, active):
        """Sets the active state in the dialog, and in the contained buttons.
        Args:
            active (boolean):   True if active, False otherwise."""
        super().set_active(active)
        for element in self.elements:
            element.set_active(active)

    def trigger_all_elements(self):
        """Trigger all the elements with variable information (With input=True, that can be modified by the user).
        Ignores buttons and such. Actually, right now only sends TextBoxes."""
        for element in self.elements:
            if element.has_input:
                element.send_event()

    def draw(self, surface):
        """Draws the dialog over the input surface, drawing an overlay in the active
        button for visual recognition.
        Args:
            surface (:obj: pygame.Surface): The surface to draw this dialog onto."""
        if self.visible:
            super().draw(surface)           #Draws self.image
            for element in self.elements:   #Draws elements onto self.imgge
                element.draw(surface, offset=self.rect.topleft)
                if element.active and element.overlay:
                    element.draw_overlay(surface, offset=self.rect.topleft)
    
    def set_canvas_size(self, resolution):
        super().set_canvas_size(resolution)
        for element in self.elements:
            element.set_canvas_size(self.rect.size)

    def add_button(self, spaces, text, command, scale=1, **button_params):
        """Adds a button to the dialog, that follows the input parameters.
        After creating it and adding it to self.buttons, it is blitted onto the dialog image.
        Args:
            spaces (int):   Spaces occupied by the button. Row spaces//2 is recommended.
            text (str): Text of the button.
            command (str):  Command triggered by the button.
            scale (float):  Scale of the button compared with the spaces taken by it.
            **button_params (:dict:):   Dict of keywords and values as parameters to create the self.image of the button.
                                        Variety going from fill_color and use_gradient to text_only."""
        self.add_ui_element(spaces, text, command, scale=scale, constructor=ButtonAction, **button_params)

    def add_input_box(self, spaces, text, command, scale=1, **textbox_params):
        """Adds a textbox to the dialog, that follows the input parameters.
        After creating it and adding it to self.buttons, it is blitted onto the dialog image.
        Args:
            spaces (int):   Spaces occupied by the button. Row spaces//2 is recommended.
            text (str): Text of the button.
            command (str):  Command triggered by the button.
            scale (float):  Scale of the button compared with the spaces taken by it.
            **textbox_params (:dict:):  Dict of keywords and values as parameters to create the self.image of the button.
                                        Variety going from fill_color and use_gradient to text_only."""
        self.add_ui_element(spaces, text, command, scale=scale, constructor=TextBox, **textbox_params)

    def add_ui_element(self, spaces, text, command, scale=1, constructor=None, centering='center', *elements, **params):
        """Adds an ui_element to the dialog, that follows the input parameters.
        After creating it and adding it to self.buttons, it is blitted onto the dialog image.
        Args:
            spaces (int):   Spaces occupied by the button. Row spaces//2 is recommended.
            text (str): Text of the button.
            command (str):  Command triggered by the button.
            scale (float):  Scale of the button compared with the spaces taken by it.
            constructor (method -> __init__, default=None): Class of the uielement that we want added. Not tested with all the possible options.
            **params (:dict:):  Dict of keywords and values as parameters to create the self.image of the button.
                                Variety going from fill_color and use_gradient to text_only."""
        spaces = self.parse_element_spaces(spaces)
        size = self.get_element_size(spaces, scale)
        position = self.get_element_position(spaces, size)
        if constructor:
            try:
                element = constructor(self.id+"_element", command, self.event_id, position, size, self.rect.size, text=text, **params)
            except:
                try:
                    element = constructor(self.id+"_element", self.event_id, position, size, self.rect.size, text=text, **params)
                except:
                    element = constructor(self.id+"_element", self.event_id, position, self.rect.size, text=text, **params)
        else:
            element = UIElement.factory(self.id+"_element", command, self.event_id, position, size, self.rect.size, text=text, *elements, **params) 
        self.adjust_position(size, position, element, centering=centering)
        self.elements.add(element)
        self.taken_spaces += spaces
    
    def adjust_position(self, size, position, element, centering='center'):
        position_x = position[0]
        position_x += (size[0]//2-element.rect.width//2) if 'center' in centering\
        else (size[0] - element.rect.width) if 'right' in centering else 0
        element.set_position((position_x, position[1]))

    def add_sprite_to_elements(self, spaces, sprite, centering='center', scale=1):
        """Testing this to add animated chars"""
        spaces = self.parse_element_spaces(spaces)
        size = self.get_element_size(spaces, scale)
        position = self.get_element_position(spaces, size)
        sprite.set_size(size)
        self.adjust_position(size, position, sprite, centering=centering)
        self.elements.add(sprite)
        self.taken_spaces += spaces

    def get_collisions(self, mouse_sprite, first_only=False):
        collisions = super().get_collisions(mouse_sprite, list_sprites=self.elements)
        collisions.extend(super().get_collisions(mouse_sprite))
        if first_only and collisions:
            return collisions[0]
        return collisions
    
    def full_clear(self):
        """Deletes all the sprites of the infoboard. Useful when deleting the texts."""
        super().clear()
        self.elements.empty()

class SelectableTable(Dialog):
    def __init__(self, id_, user_event_id, command, row_size, canvas_size, keys, *data, **params):
        """Dialog constructor.
        Args:
            id_ (str):  Identifier of the Sprite.
            user_event_id (int): Identifier of the event that will be sent.
            position (:tuple: int,int): Position of the Sprite in the screen. In pixels.
            element_size (:tuple: int,int):     Size of the Sprite in the screen. In pixels.
            canvas_size (:tuple: int,int):  Size of the display. In pixels.
            *elements (:tuple: UI_Element, int):    Subelements to be added, separated by commas. Usually TextSprites.
                                                    The tuple follows the schema (UIElement, infoboard spaces taken).
            **params (:dict:):  Dict of keywords and values as parameters to create the self.image attribute.
                                Variety going from fill_color and use_gradient to text_only.
            """
        params['cols'] = 1
        params['rows'] = len(data)+1
        super().__init__(id_, user_event_id, (row_size[0], row_size[1]*(len(data)+1)), canvas_size, **params)
        SelectableTable.generate(self, row_size, command, keys, *data)
    
    @staticmethod
    def generate(self, row_size, command, keys, *rows): #TODO ROWS FOLLOWIN A SCHEMA (text, value)
        font = None
        scale = 0.95
        try:
            font = self.params['text_font']
        except KeyError:
            pass
        new_keys, new_rows = self.parse_data(keys, *tuple(row[0] for row in rows))  #Only the first part of the rows
        self.add_button(1, self.build_row(new_keys), command, scale=scale, only_text=True, text_font=font)
        new_rows = [(x, y[1]) for x, y in zip(new_rows, rows)]  #Resstructuring it again
        #print(self.build_row(new_keys))
        #print("LEN "+str(len(self.build_row(new_keys))))
        for row in new_rows:
            #print(self.build_row(row))
            #print("LEN "+str(len(self.build_row(row))))
            #print(row[1])
            #print(self.build_row(row[0]))
            self.add_ui_element(1, self.build_row(row[0]), command, scale=scale, default_values=(row[1],), only_text=True, shows_value=False, text_font=font)
            #print(type(self.elements.sprites()[-1]))
        self.elements.sprites()[0].set_enabled(False) #We dont want the keys to be clickable

    def build_row(self, row):
        """Returns the entire row sring"""
        row_string = '| '
        for string in row:
            row_string+=string+' | '
        return row_string

    def parse_data(self, keys, *rows):
        """Parse all the elements of all rows to match the longest string in each column"""
        new_keys, new_rows = [], []
        for i in range(0, len(keys)):
            #Get the longest text in the column i
            longest = len(keys[i])
            for row in rows:
                if len(row[i]) > longest:
                    longest = len(row[i])
            #Parse the rest of texts:
            new_keys.append(self.parse_text(keys[i], longest))
            for j in range (0, len(rows)):
                try:
                    new_rows[j].append(self.parse_text(rows[j][i], longest))
                except IndexError:
                    new_rows.append([self.parse_text(rows[j][i], longest)])
        return new_keys, new_rows

    def parse_text(self, text, new_length):
        """Parse a text to match a new length, padding it with spaces"""
        start = (new_length-len(text))//2
        end = (new_length-len(text))//2 if (new_length-len(text))%2 == 0 else math.ceil((new_length-len(text))/2)
        return (start*' ')+text+(end*' ')

class TextBox(UIElement):
    CURSOR_CHAR = 'I'
    def __init__(self, id_, command, user_event_id, position, element_size, canvas_size, initial_text='', placeholder='', char_limit=0, **params):
        params['overlay'] = False
        super().__init__(id_, command, user_event_id, position, element_size, canvas_size, **params)
        self.text = initial_text
        self.has_input  = True
        self.cursor_pos = len(self.text)
        self.char_limit = char_limit #0 is unlimited
        TextBox.generate(self)

    @staticmethod
    def generate(self):
        self.update_text()

    def hitbox_action(self, command, value):
        """Executes the associated action of the element. To be called when a click or key-press happens."""
        if ('mouse' in command and ('click' in command or 'button' in command)):
            x_mouse = value[0]-self.rect.x
            text_sprite = self.sprites.sprites()[0]
            cursor_position = None
            if x_mouse-text_sprite.rect.x < 0:                              #Before the entire text
                cursor_position = 0
            elif (text_sprite.rect.x+text_sprite.rect.width)-x_mouse < 0:   #After the entire text
                cursor_position = len(self.text)
            else:
                cursor_position = int(((x_mouse-text_sprite.rect.x)/text_sprite.rect.width)*len(self.text))
                if cursor_position < self.cursor_pos:                       #The +1 is due to the cursor char in the middle of everything
                    cursor_position += 1
            self.change_cursor_position(cursor_position)
        elif 'dec' in command or 'left' in command:       
            self.change_cursor_position(self.cursor_pos-1)
        elif 'inc' in command or 'right' in command:    
            self.change_cursor_position(self.cursor_pos+1)
        else:
            value = str(value).lower()
            if 'backspace' in value:
                self.delete_char()
            elif 'space' in value:
                self.add_char(' ')
            elif 'enter' in value:
                self.send_event()
            elif 'del' in value:
                self.clear_text()
            else:
                if len(value) == 1:
                    self.add_char(str(value))

    def change_cursor_position(self, position):
        self.cursor_pos = int(position)
        self.cursor_pos = len(self.text) if self.cursor_pos>len(self.text)\
        else 0 if self.cursor_pos < 0 else self.cursor_pos
        self.update_text()

    def add_char(self, char):
        if self.char_limit == 0 or len(self.text) < self.char_limit:
            self.text = self.text[:self.cursor_pos]+char+self.text[self.cursor_pos:]
            self.cursor_pos = self.cursor_pos+1 
            self.update_text()

    def delete_char(self):
        if len(self.text) > 0:
            self.text = self.text[:self.cursor_pos-1]+self.text[self.cursor_pos:]
            self.cursor_pos = self.cursor_pos-1 
            self.update_text()

    def clear_text(self):
        self.text = ''
        self.update_text()

    def update_text(self):
        self.sprites.empty()    #Deleting the text inside
        text = self.text[:self.cursor_pos]+TextBox.CURSOR_CHAR+self.text[self.cursor_pos:] if self.active else self.text
        self.add_text_sprite('text', text, text_size=tuple(0.95*x for x in self.rect.size))
        self.regenerate_image()

    def set_active(self, state):
        super().set_active(state)

    def send_event(self):
        """Post the event associated with this element, along with the current value and the command.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()"""
        my_event = pygame.event.Event(self.get_event_id(), command=self.get_action(), value=self.text)
        pygame.event.post(my_event)

class ScrollingText(UIElement):
    #Half transparent background with text on it.
    def __init__(self, id_, user_event_id, canvas_size, size=None, transparency=128, **params):
        if not size:
            super().__init__(id_, None, user_event_id, (0, 0), canvas_size, canvas_size, **params)
        else:
            super().__init__(id_, None, user_event_id, (0, 0), size, canvas_size, **params)
        self.transparency = transparency
        self.image = self.image.convert()
        self.image.set_alpha(transparency)
        self.changed = True

    def has_changed(self):  #Kinda like an once checkable flag
        changed = self.changed
        self.changed = False
        return changed

    @synchronized
    def add_msg(self, text, msg_size=(0.85, 0.10), **params):
        print(msg_size)
        self.changed = True
        self.add_text_sprite('screen_msg_'+str(len(self.sprites.sprites())), text,\
                            text_size=tuple(x*y for x,y in zip(self.rect.size, msg_size)), **params)
        text_sprite = self.sprites.sprites()[-1]
        text_sprite.set_position((text_sprite.rect.x, self.resolution[1]))
        for sprite in self.sprites:
            sprite.set_position((sprite.rect.x, sprite.rect.y-text_sprite.rect.height))
        #self.regenerate_image()

    @synchronized
    def clear_msgs(self):
        self.changed = True
        self.sprites.empty()

    def regenerate_image(self):
        super().regenerate_image()
        self.image = self.image.convert()
        self.image.set_alpha(self.transparency)
    