import pygame, gradients, random, math
from polygons import *
from resizer import Resizer
from pygame_test import PygameSuite
from colors import *
from exceptions import InvalidUIElementException, BadUIElementInitException, InvalidCommandValueException, TooManyElementsException
from utility_box import UtilityBox

__all__ = ["TextSprite", "UIElement", "ButtonAction", "ButtonValue", "Slider", "InfoBoard", "Dialog"]

MIN_ANIMATION_VALUE     = 0.00
MAX_ANIMATION_VALUE     = 1.00
ANIMATION_STEP          = 0.03      #Like 1/30, so in 60 fps it does a complete loop
MAX_TRANSPARENCY        = 255

class TextSprite(pygame.sprite.Sprite):
    '''Class TextSprite. Inherits from pygame.sprite, and the main surface is a text, from pygame.font.render.
    Attributes:
        image: Surface that contains the text
        rect: pygame.Rect containing the position and size of the text sprite.
    '''
    __default_config = {'font': None,
                        'max_font_size' : 200,
                        'font_size'     : 0,
                        'color'         : WHITE,
                        'position'      : (0, 0)
    }
    #def __init__(self, font, rect_size, max_font_allowed, text, text_color, position=(0,0), source_rect=None, alignment=0):
    def __init__(self, _id, text, rect, **params):
        super().__init__()
        self.id     = _id
        self.text   = text
        self.params = TextSprite.__default_config.copy()
        self.params.update(params)
        self.generate(text, rect)  
    
    def draw(self, surface, offset=(0, 0)):
        if offset != (0, 0):    surface.blit(self.image, tuple([x+y for x,y in zip(offset, self.rect.topleft)]))
        else:                   surface.blit(self.image, self.rect)

    def set_text(self, text):   #Longer string, different size must me used
        if len(text) is not len(self.text):
            self.generate(text)
        else:
            self.image  = pygame.font.Font(self.font, self.size).render(text, True, self.color)
            self.rect   = pygame.Rect(self.rect.topleft, self.image.get_size())
        self.text       = text

    def set_position(self, source_rect, alignment, offset=(0, 0)):
        if isinstance(source_rect, tuple):  source_rect = pygame.Rect((0, 0), source_rect)
        elif not isinstance(source_rect, pygame.Rect):  raise BadUIElementInitException("Source rect of text sprite must be a tuple or a rect")
        x_pos               = int(source_rect.width*0.02) if alignment is 1 \
            else            source_rect.width-self.image.get_width() if alignment is 2 \
            else            (source_rect.width//2)-(self.image.get_width()//2)
        y_pos               = (source_rect.height//2)-(self.image.get_height()//2)
        self.rect.topleft   = [x+y for x,y in zip(offset, (x_pos, y_pos))]

    def generate(self, text, rect=None):
        if rect is not None and isinstance(rect, pygame.Rect):              self.rect = rect
        elif rect is not None and isinstance(rect, (list, tuple)):          self.rect = pygame.Rect(self.params["position"], rect)
        elif rect is not None:                                              raise BadUIElementInitException("Can't create text sprite, wrong rect")
        self.params['font_size']    = Resizer.max_font_size(text, self.rect.size, self.params['max_font_size'], self.params['font'])
        self.image                  = pygame.font.Font(self.params['font'], self.params['font_size']).render(text, True, self.params['color'])
            
#Graphical element, automatic creation of a menu's elements
class UIElement(pygame.sprite.Sprite):
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
                        'gradient_type': 0,
                        'overlay_color': WHITE
    }
    
    @staticmethod
    def close_button(id_, user_event_id, window_rect, **params):
        params['text'] = "X"
        size     = (window_rect.width*0.20, window_rect.height*0.10)
        position = (window_rect.width-size[0], 0)      
        return ButtonAction(id_, user_event_id, position, size, window_rect.size, **params)

    @staticmethod
    def factory(id_, user_event_id, position, size, canvas_size, default_values, *elements, **params):
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
        if any(x < 1 for x in size):    size = tuple(x*y for x,y in zip(size, canvas_size))
        if any(y < 1 for y in position):position = tuple(x*y for x,y in zip(position, canvas_size))
        if len(elements) > 0:
            if isinstance(elements[0], ButtonAction):
                return Dialog(id_, user_event_id, position, size, canvas_size, *elements, **params)
            elif isinstance(elements[0], TextSprite, pygame.sprite.Sprite):
                return InfoBoard(id_, user_event_id, position, size, canvas_size, *elements, **params)
            else:    raise BadUIElementInitException("Can't create an object with those *elements of type "+str(type(elements[0])))
        if isinstance(default_values, (list, tuple)):
            return ButtonValue(id_, user_event_id, position, size, canvas_size, tuple(default_values), **params)
        elif isinstance(default_values, (int, float)):
            return Slider(id_, user_event_id, position, size, canvas_size, float(default_values), **params)
        elif default_values is None:
            return ButtonAction(id_, user_event_id, position, size, canvas_size, **params)    
        else:
            raise BadUIElementInitException("Can't create an object with those default_values of type "+str(type(default_values)))

    def __init__(self, command, user_event_id, position, size, canvas_size, **params):
        '''Constructor of the UiElement class.'''
        super().__init__() 
        #Basic parameters on top of those inherited from Sprite
        self.__action       = command
        self.__event_id     = user_event_id
        self.pieces       = pygame.sprite.OrderedUpdates()
        self.text         = None
        #Parameters to regenerate object
        self.params         = UIElement.__default_config.copy()
        self.params.update(params)
        self.params["position"]     = position
        self.params["size"]         = size
        #Rect and images
        self.rect           = pygame.Rect(position, size) 
        self.rect_original  = self.rect.copy()
        self.real_rect      = (tuple([x/y for x,y in zip(position, canvas_size)]), tuple([x/y for x,y in zip(size, canvas_size)]))      #Made for regeneration purposes and such, have the percentage of the screen that it occupies
        self.image          = None                                      #Will be assigned a good object in the next line
        self.image_original = None
        self.mask           = None                                      #TODO to use in the future
        #Animation and showing
        self.animation_value= 0
        self.animation_step = ANIMATION_STEP
        self.overlay        = None
        self.visible        = True
        #Final method to create the complete object
        self.generate()                                               #Generate the first sprite and the self.image attribute

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
    def get_canvas_size(self):
        return tuple([x//y for x,y in zip(self.rect.size, self.real_rect[1])])

    def set_visible(self, visible):
        self.visible = visible

    def add_text(self, text, font, canvas_rect, text_rect, max_font_size, text_color, alignment): 
        '''Generates and adds sprite-based text object following the input parameters.
        Args:
            text:           String object, is the text itself.
            text_color:     Color of the text.
            text_alignment: Decides which type of centering the text follows. 0-center, 1-left, 2-right.
            font:           Type of font that the text will have. Default value of pygame: None.
            font_size:      Size of the font (height in pixels).
        Returns:
            Nothing
        Old code of method:
            #surface.blit(text_surf, (x_pos, y_pos))
            #return text_surf, pygame.Rect(x_pos, y_pos, text_surf.get_size())
        '''
        text = TextSprite(self.get_id()+"_text", text, text_rect, font=font, max_font_size=max_font_size, text_color=text_color)
        text.set_position(canvas_rect, alignment)
        self.pieces.add(text)  

    def draw(self, surface, offset=(0, 0)):
        if self.visible:
            if offset != (0, 0):    surface.blit(self.image, tuple([x+y for x,y in zip(offset, self.rect.topleft)]))
            else:                   surface.blit(self.image, self.rect)

    def draw_text(self, text, font, canvas_rect, text_rect, max_font_size, text_color, alignment):
        text = TextSprite(self.get_id()+"_text", text, text_rect, font=font, max_font_size=max_font_size, text_color=text_color)
        text.set_position(canvas_rect, alignment)
        self.image.blit(text.image, text.rect)
    
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
        if len(self.pieces.sprites())<1:        raise InvalidUIElementException("Creating the image of UIElement returned None")
        #surf                                    = pygame.Surface(self.rect.size) #Doesnt handle well transparencies
        #surf = surf.convert_alpha()
        surf = self.pieces.sprites()[0].image
        for sprite in self.pieces.sprites()[1:]:       surf.blit(sprite.image, sprite.rect.topleft)
        return surf

    def get_rect_if_canvas_size(self, canvas_size):
        return pygame.Rect(tuple([x*y for x,y in zip(self.real_rect[0], canvas_size)]),\
         tuple([x*y for x,y in zip(self.real_rect[1], canvas_size)]))

    def generate(self, rect=None, generate_image=True):
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
        if rect is not None:    self.rect, self.params["position"], self.params["size"] = rect, rect.topleft, rect.size
        self.pieces.empty()
        self.overlay            = pygame.Surface(self.rect.size) #TODO Not sure if this is the best place, just doing it here
        self.overlay.fill(self.params['overlay_color']) 
        self.pieces.add(Rectangle((0, 0), self.params['size'], self.params['texture'], self.params['color'],\
                                self.params['border'], self.params['border_width'], self.params['border_color'],\
                                self.params['gradient'], self.params['start_gradient'], self.params['end_gradient'], self.params['gradient_type']))
        if generate_image:    
            self.image          = self.generate_image()  
            self.save_state()

    def save_state(self):
        self.image_original  =   self.image.copy()
        self.rect_original   =   self.rect.copy()        

    def load_state(self):
        self.image  =   self.image_original.copy()
        self.rect   =   self.rect_original.copy()
    
    def hitbox_action(self, command, value=None):
        if self.active:     self.send_event()

    def send_event(self):
        '''Post the event associated with this element, along with the current value.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()'''
        my_event = pygame.event.Event(self.get_event_id(), command=self.get_action(), value=self.get_value())
        pygame.event.post(my_event)

    def animate(self):
        self.animation_value += self.animation_step
        if not MIN_ANIMATION_VALUE <= self.animation_value <= MAX_ANIMATION_VALUE:
            self.animation_step = -self.animation_step
            self.animation_value = MIN_ANIMATION_VALUE if self.animation_value < MIN_ANIMATION_VALUE else MAX_ANIMATION_VALUE

    def update(self):
        '''Update method, will process and change image attributes to simulate animation when drawing
        Args, Returns:
            None, Nothing
        '''
        self.animate()
        self.overlay.set_alpha(int(MAX_TRANSPARENCY*self.animation_value))
        self.image = self.image_original.copy()
        self.image.blit(self.overlay, (0,0))

    def set_event(self, event_id):
        self.__event_id = event_id

class ButtonAction(UIElement):
    __default_config = {'text': 'default',
                        'font': None,
                        'max_font_size': 50,
                        'font_size': 0,
                        'text_centering': 0,
                        'text_color': WHITE
    }
    def __init__(self, id_, user_event_id, element_position, element_size, canvas_size, **params):
        super().__init__(id_, user_event_id, element_position, element_size, canvas_size, **params)    
        self.active = True
    
    def set_active(self, active):
        if active and not self.active:      #Deactivating button
            self.image.blit(pygame.Surface(self.rect.size).fill(TRANSPARENT_GRAY), (0, 0))
            self.active     = False
        elif not active and self.active:    #Activating button
            self.load_state()
            self.active     = True
  
    def generate(self, rect=None, generate_image=True):
        super().generate(rect=rect, generate_image=False) 
        UtilityBox.check_missing_keys_in_dict(self.params, ButtonAction.__default_config)     #Totally needed after the update of params in super.init()
        self.params['font_size'] = Resizer.max_font_size(self.params['text'], self.rect.size, self.params['max_font_size'], self.params['font'])
        self.add_text(self.params['text'], self.params['font'], self.rect, [x//2 for x in self.rect.size], self.params['max_font_size'], self.params['text_color'], 0)
        if generate_image:    
            self.image = self.generate_image() 
            self.save_state()
    
    def send_event(self):
        '''Post the event associated with this element, along with the current value.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()'''
        my_event = pygame.event.Event(self.get_event_id(), command=self.get_action(), value=None)
        pygame.event.post(my_event)

class ButtonValue (ButtonAction):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'shows_value': True}
    def __init__(self, id_, user_event_id, element_position, element_size, canvas_size, set_of_values, **params):
        self.values             = set_of_values
        self.current_index      = 0
        super().__init__(id_, user_event_id, element_position, element_size, canvas_size, **params)    

    def generate(self, rect=None, generate_image=True):
        super().generate(rect=rect, generate_image=True)
        UtilityBox.check_missing_keys_in_dict(self.params, ButtonValue.__default_config)     #Totally needed after the update of params in super.init()
        if self.params['shows_value']:  self.draw_text(str(self.get_value()), self.params['font'], self.rect,\
                        [x//3 for x in self.rect.size], self.params['max_font_size'], self.params['text_color'], 2)  
        
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
            self.load_state()
            if self.params['shows_value']:  self.draw_text(str(self.get_value()), self.params['font'], self.rect,\
                        [x//3 for x in self.rect.size], self.params['max_font_size'], self.params['text_color'], 2)  

    def inc_index(self):
        '''Increment the index in a circular fassion (If over the len, goes back to the start, 0).'''
        self.current_index = self.current_index+1 if self.current_index < len(self.values)-1 else 0
        
    def dec_index(self):
        '''Decrements the index in a circular fassion (If undex 0, goes back to the max index).'''
        self.current_index = self.current_index-1 if self.current_index > 0 else len(self.values)-1

    def send_event(self):
        '''Post the event associated with this element, along with the current value.
        Posts it in the pygame.event queue. Can be retrieved with pygame.event.get()'''
        my_event = pygame.event.Event(self.get_event_id(), command=self.get_action(), value=self.get_value())
        pygame.event.post(my_event)

class Slider (UIElement):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'text': 'default',
                        'font': None,
                        'max_font_size': 50,
                        'font_size': 0,
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

    def __init__(self, id_, user_event_id, element_position, element_size, canvas_size, default_value, **params):
        self.value          =   default_value
        self.slider         =   None                #Due to the high access rate to this sprite, it will be on its own
        super().__init__(id_, user_event_id, element_position, element_size, canvas_size, **params) 

    def generate(self, rect=None, generate_image=True):
        super().generate(rect=rect, generate_image=False)
        UtilityBox.check_missing_keys_in_dict(self.params, Slider.__default_config)     #Totally needed after the update of params in super.init()
        self.params['font_size'] = Resizer.max_font_size(self.params['text'], self.rect.size, self.params['max_font_size'], self.params['font'])//2
        self.add_text(self.params['text'], self.params['font'], self.rect, [x//2 for x in self.rect.size], self.params['max_font_size'], self.params['text_color'], 1)    
        self.slider =   self.generate_slider(self.params['slider_color'], self.params['slider_gradient'], self.params['slider_start_color'],\
                                            self.params['slider_end_color'], self.params['slider_border'], self.params['slider_border_color'],\
                                            self.params['slider_border_size'], self.params['slider_type'])
        if generate_image:    
            self.image = self.generate_image() 
            self.save_state()   #TODO THIS SHIT KEEPS EXISTING IN THE BAR; EVEN AFTER CHANGING VALUE
            #self.image.blit(self.slider.image, self.slider.rect)

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
        
        slider.rect.x = (self.value*self.rect.width)-slider.rect.width//2     #To adjust the offset error due to transforming the surface.
        return slider

    def set_slider_position(self, position): 
        slider_position = int(self.rect.width*position) if (0 <= position <= 1) else int(position)                                      #Converting the slider position to pixels.
        slider_position = 0 if slider_position < 0 else self.rect.width if slider_position > self.rect.width else slider_position       #Checking if it's out of bounds 
        self.slider.rect.x = slider_position-(self.slider.rect.width//2)                                                                #To compensate the graphical offset of managing center/top-left

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
        self.load_state()
        self.send_event()

    def load_state(self): #TODO The fuck the draw text here?? 
        self.image  =   self.image_original.copy()
        self.rect   =   self.rect_original.copy()
        #Since the original image only contains the background text and color, we need to blit the slider and value again
        self.image.blit(self.slider.image, self.slider.rect)    #Blitting the new slider position                                                   #Sending the event with the new value to be captured somewhere else
        if self.params['shows_value']:  self.draw_text(str(self.get_value()), self.params['font'], self.rect,\
                [x//3 for x in self.rect.size], self.params['max_font_size'], self.params['text_color'], 2)   

    def update(self):
        '''Update method, will process and change image attributes to simulate animation when drawing
        Args, Returns:
            None, Nothing
        '''
        color = UtilityBox.random_rgb_color()
        self.draw_slider_overlay(color)

    def draw_slider_overlay(self, color):  #This gets calculated in each frame, this is not necessary
        topleft         = (int(self.value*self.rect.width)-self.rect.height//6, 0)
        center          = (int(self.value*self.rect.width), self.rect.height//2)
        overlay_rect    = pygame.Rect(topleft, (self.rect.height//3, self.rect.height))
        if self.params['slider_type'] is 0:     pygame.draw.circle(self.image, color, center, self.rect.height//2)
        elif self.params['slider_type'] is 1:   pygame.draw.ellipse(self.image, color, overlay_rect)
        else:                                   pygame.draw.rect(self.image, color, overlay_rect)

class InfoBoard (UIElement):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'rows'  : 6,
                        'cols'  : 3 
    }
    def __init__(self, id_, user_event_id, element_position, element_size, canvas_size, *elements, **params):
        super().__init__(id_, user_event_id, element_position, element_size, canvas_size, **params)    
        self.sprites        = pygame.sprite.Group()
        UtilityBox.check_missing_keys_in_dict(self.params, InfoBoard.__default_config)     #Totally needed after the update of params in super.init()
        self.spaces         = self.params['rows']*self.params['cols']
        self.taken_spaces   = 0
        self.add_and_adjust_sprites(*elements)
 
    def draw(self, surface):
        if self.visible:
            super().draw(surface)
            for sprite in self.sprites: sprite.draw(surface, offset=self.rect.topleft)

    def update(self):
        pass
    
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
            self.sprites.add(element[0])
            self.taken_spaces   += spaces 
            if self.taken_spaces > self.spaces: raise TooManyElementsException("Too many elements in infoboard") 

class Dialog (UIElement):
    #The default config of a subclass contains only those parameters that the superclass does not mention
    __default_config = {'text'          : 'default',
                        'font'          : None,
                        'max_font_size' : 50,
                        'font_size'     : 0,
                        'text_color'    : WHITE,
                        'auto_center'   : True,
                        'rows'          : 1,
                        'cols'          : 1
    }

    def __init__(self, id_, user_event_id, element_position, element_size, canvas_size, *buttons, **params):
        self.buttons            = pygame.sprite.Group()
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
            pos[1]  += size[1]


if __name__ == "__main__":
    timeout = 20
    testsuite = PygameSuite(fps=144)
    #Create elements DEPRECATED
    sli = UIElement.factory(pygame.USEREVENT+1, (10,10), (400, 100), (0.80, 0.10), (0.2))
    but = UIElement.factory(pygame.USEREVENT+2, (10, 210), (400, 100), (0.80, 0.10), (30, 40))
    sli2 = UIElement.factory(pygame.USEREVENT+3, (10, 410), (400, 100), (0.80, 0.10), (0.2), text="Slider")
    but2 = UIElement.factory(pygame.USEREVENT+4, (10, 610), (400, 100), (0.80, 0.10), ((30, 40)), text="Button")
    sli3 = UIElement.factory(pygame.USEREVENT+5, (510, 10), (400, 100), (0.80, 0.10), (0.2), text="SuperSlider", slider_type=0, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but3 = UIElement.factory(pygame.USEREVENT+6, (510, 210), (400, 100), (0.80, 0.10), ((30, 40)), text="SuperButton", start_gradient = GREEN, end_gradient=BLACK)
    sli4 = UIElement.factory(pygame.USEREVENT+7, (510, 410), (400, 100), (0.80, 0.10), (0.2), text="LongTextIsLongSoLongThatIsLongestEver", slider_type=2, start_gradient = RED, end_gradient=BLACK, slider_start_color = RED, slider_end_color = WHITE)
    but4 = UIElement.factory(pygame.USEREVENT+8, (510, 610), (400, 100), (0.80, 0.10), ((30, 40)), text="LongTextIsLongSoLongThatIsLongestEver", start_gradient = GREEN, end_gradient=BLACK)
    testsuite.add_elements(sli, but, sli2, but2, sli3, but3, sli4, but4)
    testsuite.loop(seconds = timeout)